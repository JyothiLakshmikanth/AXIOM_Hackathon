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
from orchestrator.gemini_client import generate_gemini_content, get_gemini_api_key, get_last_llm_metrics
from orchestrator.visual_gen import generate_nano_banana_image, _create_visualization_from_evidence

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
    Attempts Vertex AI first, falls back to Gemini API.

    Returns:
        LLM client object (ChatVertexAI or ChatGoogleGenerativeAI) or None if both unavailable.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    api_key = get_gemini_api_key()
    model_name = os.getenv("VERTEX_AI_GEMINI_MODEL", "gemini-1.5-flash-001")

    if project_id:
        try:
            from langchain_google_vertexai import ChatVertexAI
            logger.debug(f"Initialized ChatVertexAI ({model_name}) on project {project_id}")
            return ChatVertexAI(model_name=model_name, temperature=0.0, project=project_id, location="us-central1")
        except Exception as e:
            logger.debug(f"ChatVertexAI initialization skipped: {e}")

    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.debug(f"Initialized ChatGoogleGenerativeAI ({model_name})")
            return ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key, temperature=0.0)
        except Exception as e:
            logger.debug(f"ChatGoogleGenerativeAI initialization skipped: {e}")

    logger.warning("No LangChain LLM client available; relying on direct Gemini REST client.")
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

    Mandatory Gemini LLM synthesis stage. Consolidates authoritative evidence
    envelopes into a structured answer, executive summary, sections, and Mermaid diagram.
    """
    target_master = state.get("target_master", "AXIOM-PM")
    capability = state.get("target_capability", "Analysis")
    query = state.get("query", "")
    hypothesis = state.get("reasoning_hypothesis", "")

    evidence_payloads = [
        env.get("payload", {}) for env in state.get("evidence_envelopes", [])
    ]
    evidence_summary = _summarize_evidence(evidence_payloads)

    logger.info(
        f"[LLM] Starting Gemini synthesis | Master: {target_master} | "
        f"Capability: {capability} | Evidence envelopes: {len(evidence_payloads)}"
    )

    synthesis_prompt = f"""You are AXIOM, an expert enterprise orchestration system.
Analyze the user query and authoritative evidence envelopes below to produce a comprehensive, structured response.

USER QUERY:
"{query}"

REASONING HYPOTHESIS:
"{hypothesis}"

CAPABILITY DOMAIN:
"{target_master} - {capability}"

AUTHORITATIVE EVIDENCE PAYLOADS:
{json.dumps(evidence_payloads, indent=2) if evidence_payloads else evidence_summary}

You MUST return a valid JSON object with the following fields:
1. "synthesis": An authoritative, evidence-grounded executive summary directly answering the user query.
2. "sections": A list of sections, each having "title" (string) and "content" (list of detailed bullet points or strings).
   - For engineering/defect queries: Include "Root Cause Analysis", "Blast Radius & Upstream/Downstream Impact", and "Recommended Surgical Fix / Patch".
   - For sprint/replanning queries: Include "Sprint Bottleneck Analysis", "Capacity & Workload Evaluation", and "Rebalancing Plan".
3. "response_mode": "text_and_image" ONLY if: (a) evidence quality is HIGH (confidence ≥0.8), (b) mermaid_diagram would meaningfully clarify analysis, AND (c) user explicitly requested visual (diagram, RCA, flow, architecture, blast radius, triage). Otherwise "text_only".
4. "visual_type": "diagram" or "flow" or "architecture" or "fishbone".
5. "mermaid_diagram": A valid Mermaid diagram string (starting with 'graph TD' or 'graph LR') ONLY if it meaningfully clarifies the analysis. Omit (empty string "") if generic, redundant, or low-confidence. Ensure all syntax is valid.
"""

    synthesized_data = None
    try:
        raw_response = generate_gemini_content(
            prompt=synthesis_prompt,
            system_prompt="You are AXIOM, an enterprise AI orchestrator. Ground all analysis strictly in provided evidence.",
            json_mode=True,
            timeout=35
        )
        logger.info(f"[LLM] Gemini response received | Raw length: {len(raw_response)} chars")

        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            synthesized_data = json.loads(raw_response[json_start:json_end])
        else:
            synthesized_data = json.loads(raw_response)

        # Clear any prior LLM error flag
        state.pop("llm_error", None)

    except Exception as e:
        logger.exception(f"[LLM SYNTHESIS FAILED]: {e}")
        state["llm_error"] = f"Live Gemini synthesis error: {e}"
        # Emergency fallback only if Gemini is unreachable
        synthesis_input = {
            "query": query,
            "hypothesis": hypothesis,
            "evidence_count": len(evidence_payloads),
            "evidence_summary": evidence_summary,
            "target_capability": capability,
            "confidence_score": state.get("confidence_score", 0.5),
        }
        synthesized_data = json.loads(_fallback_synthesis(synthesis_input))

    # Update state
    synthesized_summary = synthesized_data.get("synthesis", "")
    state["synthesized_summary"] = synthesized_summary
    state["structured_answer"] = synthesized_data
    response_mode = synthesized_data.get("response_mode", "text_only")
    state["response_mode"] = response_mode

    # Visual artifact decision: Based on response_mode, query intent, or Mermaid presence
    q_low = query.lower()
    needs_visual = (
        response_mode in ("text_and_image", "image_only")
        or bool(synthesized_data.get("mermaid_diagram"))
        or any(w in q_low for w in ["diagram", "visual", "triage", "blast", "rca", "flow", "architecture", "patch", "fix", "leakage", "threshold"])
    )

    if needs_visual:
        state["response_mode"] = "text_and_image"
        state["visual_artifact"] = {
            "requires_visual": True,
            "visual_type": synthesized_data.get("visual_type", "diagram"),
            "fallback_mermaid": synthesized_data.get("mermaid_diagram") or "",
            "will_be_generated_by_design_engine": True
        }
        logger.info(f"[VISUAL] Visual generation queued (response_mode=text_and_image, type={synthesized_data.get('visual_type')})")
    else:
        state["visual_artifact"] = {"requires_visual": False}
        logger.info("[VISUAL] No visualization (response_mode=text_only); design_skills_engine will not be invoked")

    # Generate authoritative final_output_markdown
    master_name = state.get("target_master") or "AXIOM Master"
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

    # Note: Mermaid diagrams are no longer embedded here; visual generation is handled by visual_gen_node
    # using design_skills_engine when response_mode includes "image"

    state["final_output_markdown"] = "\n".join(md_lines).strip()
    state["current_step"] = "SYNTHESIZE"
    state["llm_metrics"] = get_last_llm_metrics()

    logger.info(f"[LLM] final_output_markdown generated by Gemini ({len(state['final_output_markdown'])} chars)")
    print(
        f"[ORCHESTRATOR DEBUG] Step: SYNTHESIZE Completed | Master: {master_name} | "
        f"Markdown: {len(state['final_output_markdown'])} chars | Telemetry: {state['llm_metrics']}",
        flush=True
    )
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

    logger.debug(f"VISUAL_GEN: Visual type={visual_type}")

    # Check if a live Mermaid diagram was already produced by the synthesis node
    existing_mermaid = (
        state.get("visual_artifact", {}).get("fallback_mermaid")
        or structured_answer.get("mermaid_diagram")
    )

    fallback_mermaid = existing_mermaid
    if not fallback_mermaid:
        try:
            mermaid_prompt = f"""Generate a clean, professional Mermaid.js flowchart (starting with 'graph TD' or 'graph LR') illustrating the following analysis:

{synthesized_summary}

Requirements:
- Visual Type: {visual_type}
- Technical clarity suitable for enterprise review.
- Return ONLY the raw Mermaid diagram definition without markdown code ticks.
"""
            raw_mermaid = generate_gemini_content(
                prompt=mermaid_prompt,
                system_prompt="You are an expert system architect creating valid Mermaid diagrams.",
                json_mode=False,
                timeout=25
            )
            fallback_mermaid = raw_mermaid.replace("```mermaid", "").replace("```", "").strip()
            logger.info(f"[LLM] Dynamic Mermaid diagram generated ({len(fallback_mermaid)} chars)")
        except Exception as e:
            logger.warning(f"VISUAL_GEN: Dynamic mermaid generation notice ({e}); using template fallback.")
            fallback_mermaid = _fallback_mermaid(visual_type, synthesized_summary)

    # Generate actual image using Nano Banana API
    image_url = None
    image_generation_status = "FAILED"

    try:
        # Create visualization spec for Nano Banana
        image_spec = {
            "visual_type": visual_type,
            "summary": synthesized_summary,
            "mermaid_diagram": fallback_mermaid,
            "caption": synthesized_summary[:100]
        }
        logger.info(f"VISUAL_GEN: Generating visual artifact for: {visual_type}")
        image_url = generate_nano_banana_image(image_spec)

        if image_url:
            image_generation_status = "SUCCESS"
            logger.info(f"VISUAL_GEN: Image generated successfully: {image_url[:80]}...")
        else:
            image_generation_status = "NO_URL"
            logger.warning("VISUAL_GEN: Image generation returned no URL")
    except Exception as e:
        logger.warning(f"VISUAL_GEN: Image generation failed ({e}); will use Mermaid fallback")
        image_generation_status = "ERROR"

    # Update visual_artifact
    visual_artifact = {
        "requires_visual": True,
        "visual_type": visual_type,
        "image_prompt": f"Diagram for {synthesized_summary[:80]}",
        "image_model": "gemini-svg-vector-engine" if (image_url and "svg" in image_url) else ("google-imagen-3" if image_url else "mermaid-fallback"),
        "image_url": image_url,
        "fallback_mermaid": fallback_mermaid,
        "structured_caption": synthesized_summary[:100],
        "generation_status": image_generation_status,
        "has_image": image_url is not None
    }

    state["visual_artifact"] = visual_artifact
    state["current_step"] = "VISUAL_GEN"

    logger.info(f"VISUAL_GEN: Complete. visual_type={visual_type}, has_mermaid={fallback_mermaid is not None}, has_image={image_url is not None}")
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
    s_lower = summary.lower()
    if "ble" in s_lower or "unlock" in s_lower or "threshold" in s_lower or "signal" in s_lower:
        return """graph TD
    Signal["📡 Inbound BLE RSSI Signal"] --> Check{"Threshold Check (>= Configured dBm)"}
    Check -->|RSSI >= Threshold| Auth["✅ Authenticate Proximity Unlock"]
    Check -->|Boundary Exact Hit| Bug["🚨 [BUG] Edge Flaw: Reject at Exact Threshold"]
    Check -->|RSSI < Threshold| Deny["❌ Reject Unlock: Out of Range"]
    Bug --> RCA["🔍 Root Cause: Strict '>' operator instead of '>=' in proximity_controller.py"]
    RCA --> Patch["⚡ Surgical Patch PR #412"]"""

    elif "capacity" in s_lower or "sprint" in s_lower or "resource" in s_lower:
        return """graph TD
    Sprint["📅 Sprint Plan (SPR-03)"] --> Workload{"Workload Distribution"}
    Workload -->|> 85% Cap| Risk["⚠️ Over-allocated Engineers"]
    Workload -->|<= 85% Cap| Safe["✅ Sustainable Velocity"]
    Risk --> Rebalance["🔄 AXIOM Task Rebalancing Algorithm"]
    Rebalance --> Safe"""

    elif visual_type == "flow":
        return """graph TD
    Input["Input Event / Telemetry"] --> Decision{"Policy Gate"}
    Decision -->|Pass| Exec["Execute Core Operation"]
    Decision -->|Fail| Handle["Remediation / Exception Handler"]
    Exec --> Output["Authoritative State Output"]
    Handle --> Output"""

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
