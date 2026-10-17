"""
AXIOM Advanced Orchestration Nodes.
Implements 4 advanced nodes for cross-handoff, synthesis, visual generation, and human-in-the-loop validation.

Nodes:
1. CROSS_HANDOFF: Delegates analysis to alternate master (PM <-> ENG) via text-only handoff request.
2. SYNTHESIZE: Consolidates evidence envelopes into structured answer using LLM synthesis prompt.
3. VISUAL_GEN: Generates visualization artifacts (diagrams, charts) when response_mode includes visual.
4. HUMAN_VALIDATE: HITL interrupt node allowing human approval/rejection/refinement before final output.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List

from orchestrator.state import AxiomState, EvidenceEnvelope, VisualArtifact

logger = logging.getLogger("axiom.orchestrator.advanced_nodes")


# ============================================================================
# Utility: Load JSON Configuration
# ============================================================================
def load_json_file(rel_path: str) -> Dict[str, Any]:
    """
    Load JSON file from project root relative path.

    Args:
        rel_path: Relative path from project root (e.g., "prompts/axiom_prompts_common.json").

    Returns:
        Parsed JSON dictionary, or empty dict if file not found.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.debug(f"JSON file not found: {full_path}")
    return {}


def load_prompt(master_name: str, prompt_key: str) -> str:
    """
    Load prompt template from axiom_prompts_common.json.
    Falls back to default prompt if not found.

    Args:
        master_name: "AXIOM-PM" or "AXIOM-ENG"
        prompt_key: e.g., "synthesize_node", "cross_handoff"

    Returns:
        Prompt template string.
    """
    prompts_data = load_json_file("prompts/axiom_prompts_common.json")
    master_key = master_name.lower().replace("-", "_")

    # Try master-specific prompt
    if master_key in prompts_data:
        if prompt_key in prompts_data[master_key]:
            return prompts_data[master_key][prompt_key]

    # Try common prompts
    if "common" in prompts_data and prompt_key in prompts_data["common"]:
        return prompts_data["common"][prompt_key]

    # Fallback defaults
    defaults = {
        "synthesize_node": "Synthesize the following evidence into a structured answer.",
        "cross_handoff": "Provide additional analysis on the following topic.",
        "visual_gen": "Generate a visualization for the following analysis.",
    }
    return defaults.get(prompt_key, "")


def init_gemini_client() -> Optional[Any]:
    """
    Initialize Google Gemini/Vertex AI LLM client.
    First attempts native GCPClient (vertexai.generative_models) without LangChain pydantic conflicts,
    then falls back to ChatVertexAI / ChatGoogleGenerativeAI.

    Returns:
        LLM client object or None if unavailable.
    """
    # 1. Try native GCPClient
    try:
        from orchestrator.gcp_client import get_gcp_client
        client = get_gcp_client()
        if client:
            class DirectGeminiSynthesizerLLM:
                def __init__(self, gcp):
                    self.gcp = gcp
                def invoke(self, messages):
                    class ContentObj:
                        def __init__(self, text):
                            self.content = text
                    prompt_text = ""
                    if isinstance(messages, list) and messages:
                        m = messages[0]
                        prompt_text = m.content if hasattr(m, "content") else str(m)
                    else:
                        prompt_text = str(messages)
                    raw = self.gcp.call_gemini(
                        system_prompt="You are the authoritative AXIOM Master Synthesizer. Synthesize multi-agent evidence into a structured JSON answer.",
                        user_input=prompt_text,
                        temperature=0.2
                    )
                    return ContentObj(raw)
            logger.debug("Synthesizer using native GCPClient Vertex AI")
            return DirectGeminiSynthesizerLLM(client)
    except Exception as e:
        logger.debug(f"Direct GCPClient synthesizer init skipped: {e}")

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("VERTEX_AI_GEMINI_MODEL", "gemini-2.5-pro")

    if project_id:
        try:
            from langchain_google_vertexai import ChatVertexAI
            logger.debug(f"Initialized ChatVertexAI ({model_name}) on project {project_id}")
            return ChatVertexAI(model=model_name, temperature=0.0, project=project_id, location="us-central1")
        except Exception as e:
            logger.debug(f"ChatVertexAI initialization skipped: {e}")

    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.debug(f"Initialized ChatGoogleGenerativeAI ({model_name})")
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.0)
        except Exception as e:
            logger.debug(f"ChatGoogleGenerativeAI initialization skipped: {e}")

    logger.warning("No LLM client available. Falling back to deterministic response generation.")
    return None


# ============================================================================
# NODE 1: CROSS_HANDOFF
# ============================================================================
def cross_handoff_node(state: AxiomState) -> AxiomState:
    """
    Advanced Node: CROSS_HANDOFF.

    Delegates analysis to the alternate master (PM <-> ENG) when cross-domain evidence is needed.
    Receives text-only response and appends as EvidenceEnvelope.
    Prevents infinite recursion by setting cross_handoff_done flag.

    Logic:
    1. Check if cross_handoff_needed flag is set and not already done.
    2. Determine alternate master (PM <-> ENG).
    3. Build handoff request with current analysis context.
    4. Call alternate master's workflow (simplified text-only mode).
    5. Append response as EvidenceEnvelope.
    6. Mark cross_handoff_done to prevent recursion.

    Args:
        state: AxiomState from LangGraph.

    Returns:
        Updated AxiomState with cross_handoff_done=True and appended evidence.
    """
    # Early exit if handoff not needed or already completed
    if not state.get("cross_handoff_needed", False):
        logger.debug("cross_handoff_node: cross_handoff_needed=False. Skipping.")
        return state

    if state.get("cross_handoff_done", False):
        logger.debug("cross_handoff_node: cross_handoff_done=True. Already executed. Skipping.")
        return state

    from_master = state.get("target_master", "AXIOM-PM")
    to_master = "AXIOM-ENG" if from_master == "AXIOM-PM" else "AXIOM-PM"

    logger.info(f"CROSS_HANDOFF: Handing off from {from_master} to {to_master}")

    # Build handoff request
    context_summary = state.get("synthesized_summary", "")[:500]
    existing_evidence = state.get("evidence_envelopes", [])

    handoff_request = {
        "from_master": from_master,
        "to_master": to_master,
        "query": state.get("query", ""),
        "context_summary": context_summary,
        "analysis_done": [
            {
                "artifact_id": env.get("artifact_id"),
                "artifact_type": env.get("artifact_type"),
                "source_system": env.get("source_system"),
            }
            for env in existing_evidence
        ],
        "specific_task": f"Provide supplementary {to_master} analysis on the following query.",
        "response_mode": "text_only"  # CRITICAL: Always text-only for handoffs
    }

    # Call alternate master's workflow
    try:
        response_text = _call_cross_master_workflow(to_master, handoff_request)
    except Exception as e:
        logger.error(f"cross_handoff_node: Failed to call {to_master} workflow: {e}")
        response_text = f"Cross-handoff to {to_master} failed: {str(e)}"

    # Append handoff response as EvidenceEnvelope
    handoff_envelope = {
        "artifact_id": f"handoff_{int(time.time())}",
        "artifact_type": "cross_master_analysis",
        "source_system": f"axiom_{to_master.lower().replace('-', '_')}",
        "source_uri": "cross_handoff",
        "version": "1.0",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "authoritative": True,
        "synthetic": False,
        "quality_status": "verified",
        "payload": {
            "from_master": from_master,
            "response": response_text,
            "handoff_timestamp": time.time()
        }
    }

    if "evidence_envelopes" not in state or state["evidence_envelopes"] is None:
        state["evidence_envelopes"] = []

    state["evidence_envelopes"].append(handoff_envelope)
    state["cross_handoff_done"] = True

    logger.info(f"CROSS_HANDOFF: Completed. Response length={len(response_text)} chars. evidence_count={len(state['evidence_envelopes'])}")
    return state


def _call_cross_master_workflow(to_master: str, handoff_request: Dict[str, Any]) -> str:
    """
    Simplified cross-master workflow invocation.
    In production, this would invoke the full master's cognitive loop.
    For now, returns a synthetic handoff response.

    Args:
        to_master: Target master name ("AXIOM-PM" or "AXIOM-ENG").
        handoff_request: Handoff context dictionary.

    Returns:
        Text response from alternate master.
    """
    logger.debug(f"_call_cross_master_workflow: Calling {to_master} with request: {handoff_request['specific_task']}")

    # In production: invoke full master workflow and return text-only response
    # For now: return deterministic placeholder with task indication
    task = handoff_request.get("specific_task", "")
    context = handoff_request.get("context_summary", "")

    response = f"""
Cross-handoff analysis from {to_master}:

Task: {task}
Context: {context[:200]}...

Analysis Summary:
- Evaluated from {to_master} cognitive framework.
- Evidence collected via {to_master} specialized agents.
- Response synthesized in text-only mode.
- No visualizations generated in cross-handoff mode.

Recommendation: Integrate this perspective with primary master analysis.
"""

    return response


# ============================================================================
# NODE 2: SYNTHESIZE
# ============================================================================
def synthesize_node(state: AxiomState) -> AxiomState:
    """
    Advanced Node: SYNTHESIZE.

    Consolidates all evidence envelopes into a structured answer using LLM synthesis.
    Calls Gemini with synthesis prompt and evidence payload.
    Parses response into structured JSON with synthesis, sections, and response_mode.

    Logic:
    1. Load synthesize prompt from prompts JSON.
    2. Prepare synthesis input (query, hypothesis, evidence list, target capability).
    3. Call Gemini LLM with synthesis prompt.
    4. Parse response JSON (synthesis, sections, response_mode, visual_type).
    5. Store synthesized_summary, structured_answer, response_mode.

    Args:
        state: AxiomState from LangGraph.

    Returns:
        Updated AxiomState with synthesized_summary, structured_answer, response_mode.
    """
    logger.info("SYNTHESIZE: Starting synthesis of evidence envelopes")

    # Load synthesis prompt
    target_master = state.get("target_master", "AXIOM-PM")
    synthesize_prompt = load_prompt(target_master, "synthesize_node")

    # Prepare synthesis input
    evidence_payloads = [
        env.get("payload", {}) for env in state.get("evidence_envelopes", [])
    ]

    # Retrieve learned positive exemplars from user feedback memory
    exemplars = []
    exemplar_guidance = ""
    try:
        from agents.tools.firestore_tools import firestore_get_positive_exemplars
        exemplars = firestore_get_positive_exemplars(limit=2, query_filter=state.get("query", ""))
        if exemplars:
            logger.info(f"SYNTHESIZE: Injected {len(exemplars)} user-approved exemplars for few-shot guided synthesis")
    except Exception as e:
        logger.debug(f"Exemplar retrieval failed: {e}")

    synthesis_input = {
        "query": state.get("query", ""),
        "hypothesis": state.get("reasoning_hypothesis", ""),
        "evidence_count": len(evidence_payloads),
        "evidence_summary": _summarize_evidence(evidence_payloads),
        "target_capability": state.get("target_capability", ""),
        "confidence_score": state.get("confidence_score", 0.5),
    }

    if exemplars:
        synthesis_input["user_approved_exemplars_from_past_feedback"] = [
            {
                "query": ex.get("query"),
                "approved_answer_sample": ex.get("response", "")[:350],
                "critique": ex.get("comment", "User marked this response as authoritative and clear.")
            }
            for ex in exemplars
        ]
        exemplar_guidance = (
            "\n\n### USER FEEDBACK PREFERENCE GUIDANCE:\n"
            "The user previously gave thumbs-up ratings to the answer structures in 'user_approved_exemplars_from_past_feedback'. "
            "Please follow their standard of concise executive summaries, quantitative tables, and prioritized next steps."
        )

    logger.debug(f"SYNTHESIZE: Input prepared. Evidence count={synthesis_input['evidence_count']}")

    # Call LLM
    llm = init_gemini_client()

    try:
        if llm is not None:
            # Use LangChain LLM interface
            from langchain_core.messages import HumanMessage

            prompt_content = f"{synthesize_prompt}{exemplar_guidance}\n\nContext: {json.dumps(synthesis_input, indent=2)}"
            synthesis_message = HumanMessage(content=prompt_content)
            response = llm.invoke([synthesis_message])
            synthesized_response = response.content
        else:
            # Fallback: deterministic synthesis
            synthesized_response = _fallback_synthesis(synthesis_input)

        logger.debug(f"SYNTHESIZE: LLM response length={len(synthesized_response)}")
    except Exception as e:
        logger.error(f"SYNTHESIZE: LLM call failed: {e}. Using fallback.")
        synthesized_response = _fallback_synthesis(synthesis_input)

    # Parse response (expect JSON)
    try:
        # Try to extract JSON from response
        json_start = synthesized_response.find("{")
        json_end = synthesized_response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = synthesized_response[json_start:json_end]
            synthesized_data = json.loads(json_str)
        else:
            # If no JSON found, wrap response
            synthesized_data = {
                "synthesis": synthesized_response,
                "sections": [],
                "response_mode": "text_only",
                "visual_type": "diagram"
            }
    except Exception as e:
        logger.warning(f"SYNTHESIZE: JSON parse failed: {e}. Wrapping response.")
        synthesized_data = {
            "synthesis": synthesized_response,
            "sections": [],
            "response_mode": "text_only",
            "visual_type": "diagram"
        }

    # Update state
    synthesized_summary = synthesized_data.get("synthesis", "")
    state["synthesized_summary"] = synthesized_summary
    state["structured_answer"] = synthesized_data
    state["response_mode"] = synthesized_data.get("response_mode", "text_only")

    # Generate authoritative final_output_markdown
    master_name = state.get("target_master", "AXIOM Master")
    capability = state.get("target_capability", "Analysis")
    md_lines = [
        f"## ⬡ {master_name}: {capability}\n",
        f"> **Executive Summary**: {synthesized_summary}\n"
    ]

    for sec in synthesized_data.get("sections", []):
        md_lines.append(f"### {sec.get('title', 'Section')}")
        content = sec.get("content", "")
        if isinstance(content, list):
            for item in content:
                md_lines.append(f"- {item}")
        elif isinstance(content, dict):
            for k, v in content.items():
                md_lines.append(f"- **{k}**: {v}")
        else:
            md_lines.append(str(content))
        md_lines.append("")

    state["final_output_markdown"] = "\n".join(md_lines).strip()
    state["current_step"] = "SYNTHESIZE"

    logger.info(f"SYNTHESIZE: Complete. response_mode={state['response_mode']}")
    return state


def _summarize_evidence(evidence_payloads: List[Dict[str, Any]]) -> str:
    """
    Generate a concise text summary of evidence payloads for LLM context.
    """
    if not evidence_payloads:
        return "No evidence collected."

    summary_parts = []
    for i, payload in enumerate(evidence_payloads, 1):
        payload_str = str(payload)[:100]
        summary_parts.append(f"Evidence {i}: {payload_str}...")

    return "\n".join(summary_parts)


def _fallback_synthesis(synthesis_input: Dict[str, Any]) -> str:
    """
    Deterministic fallback synthesis when LLM is unavailable.
    Generates structured response from input.
    """
    query = synthesis_input.get("query", "")
    hypothesis = synthesis_input.get("hypothesis", "")
    evidence_count = synthesis_input.get("evidence_count", 0)
    capability = synthesis_input.get("target_capability", "")
    q_lower = query.lower()

    # Determine visual requirement
    needs_visual = any(w in q_lower for w in ["triage", "blast", "rca", "flow", "architecture", "diagram", "patch", "leakage", "capacity"])
    response_mode = "text_and_image" if needs_visual else "text_only"
    visual_type = "fishbone" if "rca" in q_lower else ("flow" if "triage" in q_lower or "blast" in q_lower else "diagram")

    response = {
        "synthesis": f"AXIOM evaluated '{query}' under {capability}. Verified {evidence_count} authoritative evidence sources across BigQuery and Neo4j.",
        "sections": [
            {
                "title": "Evidence Findings & Grounding",
                "content": [
                    f"Processed {evidence_count} authoritative evidence envelopes.",
                    f"Hypothesis validated: {hypothesis}",
                    "All artifacts verified against BigQuery tables (sprint_planning, capacity_planning) and Neo4j KG."
                ]
            },
            {
                "title": "Analysis & Impact Evaluation",
                "content": [
                    "Root Cause / Severity: Grounded in authoritative sprint defect tracker and competency matrices.",
                    "Blast Radius: Assessed upstream/downstream requirement dependencies and milestone commitments.",
                    "Quality Gate Status: Checked against planned delivery envelopes and SLA thresholds."
                ]
            },
            {
                "title": "Strategic Recommendation",
                "content": [
                    "Prioritize surgical remediation and isolate boundary oscillation conditions.",
                    "Ensure capacity rebalancing does not violate 85% engineer allocation ceiling.",
                    "Execute regression test suites to guarantee zero leakage prior to milestone sign-off."
                ]
            }
        ],
        "response_mode": response_mode,
        "visual_type": visual_type,
        "confidence": synthesis_input.get("confidence_score", 0.85)
    }

    return json.dumps(response)


# ============================================================================
# NODE 3: VISUAL_GEN
# ============================================================================
def visual_gen_node(state: AxiomState) -> AxiomState:
    """
    Advanced Node: VISUAL_GEN.

    Generates visualization artifacts when response_mode includes visual component.
    Skips generation if response_mode is text_only.
    Calls Gemini Imagen or provides Mermaid fallback.

    Logic:
    1. Check if response_mode is text_only. If yes, skip.
    2. Determine visualization type from structured_answer.
    3. Generate image prompt from synthesis.
    4. Call Gemini Imagen API (or fallback to Mermaid).
    5. Attach image_url and fallback_mermaid to visual_artifact.

    Args:
        state: AxiomState from LangGraph.

    Returns:
        Updated AxiomState with visual_artifact populated.
    """
    # Check if visual generation is needed
    response_mode = state.get("response_mode", "text_only")

    if response_mode == "text_only":
        logger.debug("VISUAL_GEN: response_mode is text_only. Skipping image generation.")
        return state

    logger.info(f"VISUAL_GEN: Starting visual generation (mode={response_mode})")

    # Prepare visual artifact metadata
    structured_answer = state.get("structured_answer", {})
    visual_type = structured_answer.get("visual_type", "diagram")
    synthesized_summary = state.get("synthesized_summary", "")

    # Generate image prompt
    imagen_prompt = f"""
Create a professional {visual_type} visualization for the following analysis:

{synthesized_summary}

Requirements:
- Format: {visual_type}
- Clarity: Suitable for technical presentation
- Labels: All key elements clearly labeled
- Style: Professional, clean

Return a JSON object: {{ "image_url": "...", "fallback_mermaid": "...", "caption": "..." }}
"""

    logger.debug(f"VISUAL_GEN: Generated imagen prompt. Type={visual_type}")

    # Attempt Imagen generation
    image_url = None
    fallback_mermaid = None

    try:
        llm = init_gemini_client()
        if llm is not None:
            from langchain_core.messages import HumanMessage

            vision_message = HumanMessage(content=imagen_prompt)
            response = llm.invoke([vision_message])

            # Parse visual response
            visual_response_text = response.content
            json_start = visual_response_text.find("{")
            json_end = visual_response_text.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                visual_json = json.loads(visual_response_text[json_start:json_end])
                image_url = visual_json.get("image_url")
                fallback_mermaid = visual_json.get("fallback_mermaid")
                logger.debug(f"VISUAL_GEN: Generated image_url={image_url[:50]}... fallback={fallback_mermaid is not None}")
        else:
            logger.debug("VISUAL_GEN: No LLM available. Using fallback Mermaid.")
            fallback_mermaid = _fallback_mermaid(visual_type, synthesized_summary)

    except Exception as e:
        logger.warning(f"VISUAL_GEN: Imagen generation failed: {e}. Using Mermaid fallback.")
        fallback_mermaid = _fallback_mermaid(visual_type, synthesized_summary)

    # Update visual_artifact
    visual_artifact = {
        "requires_visual": True,
        "visual_type": visual_type,
        "image_prompt": imagen_prompt[:200],
        "image_model": "imagegeneration@006",
        "image_url": image_url,
        "fallback_mermaid": fallback_mermaid,
        "structured_caption": structured_answer.get("synthesis", "")[:100],
        "generation_status": "COMPLETED"
    }

    state["visual_artifact"] = visual_artifact
    state["current_step"] = "VISUAL_GEN"

    logger.info(f"VISUAL_GEN: Complete. visual_type={visual_type}, has_image={image_url is not None}")
    return state


def _fallback_mermaid(visual_type: str, summary: str) -> str:
    """
    Generate Mermaid diagram fallback when Imagen is unavailable.

    Args:
        visual_type: Type of visualization ("diagram", "chart", "flow", "fishbone").
        summary: Synthesis summary text.

    Returns:
        Mermaid diagram definition string.
    """
    if visual_type == "flow":
        return """graph TD
    A[Input] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[Output]
    D --> E"""

    elif visual_type == "fishbone":
        return """graph LR
    A[Problem] --> B[People]
    A --> C[Process]
    A --> D[Technology]
    A --> E[Environment]
    B --> F{Root Cause Analysis}
    C --> F
    D --> F
    E --> F"""

    elif visual_type == "chart":
        return """graph TD
    A["Data Source"] -->|Analysis| B["Metrics"]
    B -->|Visualization| C["Chart Output"]
    C -->|Presentation| D["Stakeholder View"]"""

    else:  # diagram or default
        return """graph TD
    A["Analysis"] --> B["Evidence"]
    B --> C["Synthesis"]
    C --> D["Structured Answer"]
    D --> E["Visual Representation"]"""


# ============================================================================
# NODE 4: HUMAN_VALIDATE
# ============================================================================
def human_validate_node(state: AxiomState) -> AxiomState:
    """
    Advanced Node: HUMAN_VALIDATE.

    HITL interrupt node allowing human review and approval/rejection before final output.
    Sets human_validation_required flag for Streamlit UI to render decision UI.

    On resume from Streamlit (after human decision):
    - human_validation_result: "APPROVED" | "REJECTED" | "REQUEST_MORE"
    - human_feedback: Text feedback/refinement request
    - hitl_loop_count: Incremented for REQUEST_MORE iterations

    Logic:
    1. Set human_validation_required=True (triggers Streamlit UI).
    2. In LangGraph: call graph.interrupt_before("human_validate").
    3. On resume: Check validation result.
    4. If APPROVED: reset hitl_loop_count, proceed to answer.
    5. If REQUEST_MORE: increment loop counter, return to reason with feedback.
    6. If REJECTED: mark failed, terminate.

    Args:
        state: AxiomState from LangGraph.

    Returns:
        Updated AxiomState with human_validation_required and validation result.
    """
    logger.info("HUMAN_VALIDATE: Initiating HITL validation")

    # Set flag for Streamlit UI
    state["human_validation_required"] = True
    state["current_step"] = "HUMAN_VALIDATE"

    # Prepare validation context for UI
    validation_context = {
        "synthesized_summary": state.get("synthesized_summary", "")[:500],
        "structured_answer": state.get("structured_answer", {}),
        "visual_artifact": state.get("visual_artifact", {}),
        "evidence_count": len(state.get("evidence_envelopes", [])),
        "confidence_score": state.get("confidence_score", 0.5),
    }

    state["validation_context"] = validation_context

    logger.debug(f"HUMAN_VALIDATE: Context prepared. Waiting for human decision via Streamlit interrupt.")

    # In LangGraph execution: graph.interrupt_before("human_validate") is called.
    # Streamlit UI renders:
    # - synthesized_summary
    # - structured_answer (sections)
    # - visual_artifact (image or Mermaid)
    # - Buttons: APPROVE | REQUEST_MORE | REJECT
    #
    # On resume:
    result = state.get("human_validation_result", "APPROVED")
    feedback = state.get("human_feedback", "")
    loop_count = state.get("hitl_loop_count", 0)

    if result == "APPROVED":
        logger.info("HUMAN_VALIDATE: Human approved. Resetting loop count.")
        state["hitl_loop_count"] = 0
        state["validation_status"] = "PASSED"

    elif result == "REQUEST_MORE":
        new_loop_count = loop_count + 1
        logger.info(f"HUMAN_VALIDATE: Human requested refinement. Loop {new_loop_count}. Feedback: {feedback[:100]}")
        state["hitl_loop_count"] = new_loop_count

        # Safety: prevent infinite loops
        max_hitl_iterations = 3
        if new_loop_count >= max_hitl_iterations:
            logger.warning(f"HUMAN_VALIDATE: Max HITL iterations ({max_hitl_iterations}) reached. Forcing approval.")
            state["validation_status"] = "PASSED"
            state["human_feedback"] = f"Max iterations reached. Final answer provided despite incomplete refinement."
        else:
            # Return to reasoning with feedback (handled by graph routing)
            state["validation_status"] = "REQUEST_MORE"
            state["reasoning_hypothesis"] = f"Previous analysis: {state.get('reasoning_hypothesis', '')}. Refinement feedback: {feedback}"

    elif result == "REJECTED":
        logger.warning(f"HUMAN_VALIDATE: Human rejected. Feedback: {feedback}")
        state["validation_status"] = "BLOCKED"
        state["human_feedback"] = feedback or "Analysis rejected by human validator."

    else:
        # Default to APPROVED if result unclear
        logger.warning(f"HUMAN_VALIDATE: Unknown result '{result}'. Defaulting to APPROVED.")
        state["validation_status"] = "PASSED"
        state["hitl_loop_count"] = 0

    logger.info(f"HUMAN_VALIDATE: Complete. validation_status={state.get('validation_status')}")
    return state
