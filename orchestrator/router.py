"""
Top-Level Intent Router and Clarification Node for AXIOM.
LLM-DRIVEN SEMANTIC CLASSIFICATION (not keyword matching).

Routes queries to PM.ai or ENG.ai based on master domain boundaries:
  - PM.ai: Macro-level delivery (schedule, resource, risk, preliminary hypothesis)
  - ENG.ai: Micro-level technical (code, architecture, confirmed RCA, testing)
"""

import os
import json
import logging
from typing import Dict, Any
from orchestrator.state import AxiomState
from orchestrator.prompt_loader import load_prompt
from orchestrator.gcp_client import get_gcp_client

logger = logging.getLogger("axiom.orchestrator.router")


def analyze_intent_with_llm(query: str) -> Dict[str, Any]:
    """
    LLM-DRIVEN semantic intent classification.
    Uses the "21_intent_detection_classifier" prompt from axiom_prompts_common.json
    to intelligently route to PM.ai or ENG.ai based on master domain boundaries.

    Returns:
    {
        "domain": "PJM" | "ENG" | "NEEDS_CLARIFICATION",
        "boundary_classification": "macro_delivery" | "micro_technical" | "cross_domain",
        "confidence": "High" | "Medium" | "Low",
        "reasoning": "Why this query maps to [domain] master",
        "target_master": "AXIOM-PM" | "AXIOM-ENG" | None,
        "target_capability": str or None,
        "clarification_questions": List[str] or []
    }
    """
    try:
        # Load the intent detection classifier prompt from axiom_prompts_common.json
        intent_classifier_prompt = load_prompt("AXIOM-PM", "intent_detection_classifier")

        # Prepare LLM input
        llm_input = f"""
{intent_classifier_prompt}

---

USER QUERY:
"{query}"

---

Based on the above classification framework, analyze this user query and return a JSON response with:
- domain: "PJM" | "ENG" | "NEEDS_CLARIFICATION"
- boundary_classification: "macro_delivery" | "micro_technical" | "cross_domain"
- confidence: "High" | "Medium" | "Low"
- reasoning: explanation of why this query maps to the selected domain
- target_capability: (for PJM or ENG) the specific intent from the taxonomy, or null
"""

        # Call Gemini LLM for semantic classification
        gcp = get_gcp_client()
        llm_response = gcp.call_gemini(
            system_prompt="You are an expert intent router for intelligent systems. Classify user queries semantically (not by keyword matching) into project delivery (PJM) or engineering (ENG) domains.",
            user_input=llm_input,
            temperature=0.3  # Low temperature for consistent routing decisions
        )

        # Parse LLM response
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                classification = json.loads(json_match.group())
            else:
                classification = json.loads(llm_response)
        except json.JSONDecodeError:
            logger.warning(f"LLM response not valid JSON. Response: {llm_response}")
            return {
                "clarification_needed": True,
                "domain": "NEEDS_CLARIFICATION",
                "confidence": "Low",
                "ambiguity_reason": "Could not classify intent reliably. Please clarify: Are you asking about (1) delivery/project (PM), (2) technical/code (ENG), or (3) both?",
                "clarification_questions": [
                    "Are you requesting Project Management analysis (schedule, resource, delivery risk)?",
                    "Are you requesting Engineering analysis (code, architecture, RCA, testing)?",
                    "Do you need both perspectives?"
                ],
                "target_master": None,
                "target_capability": None,
                "confidence_score": 0.2
            }

        # Map domain to target_master
        domain_to_master = {
            "PJM": "AXIOM-PM",
            "ENG": "AXIOM-ENG",
            "BOTH": "AXIOM-PM"  # Start with PM if both needed
        }

        target_master = domain_to_master.get(classification.get("domain"), None)
        target_capability = classification.get("target_capability")
        confidence_score = {"High": 0.95, "Medium": 0.70, "Low": 0.4}.get(
            classification.get("confidence", "Low"), 0.4
        )

        # Build response
        response = {
            "clarification_needed": classification.get("domain") == "NEEDS_CLARIFICATION",
            "domain": classification.get("domain"),
            "target_master": target_master,
            "target_capability": target_capability,
            "confidence_score": confidence_score,
            "boundary_classification": classification.get("boundary_classification"),
            "reasoning_summary": classification.get("reasoning"),
            "clarification_questions": classification.get("clarification_questions", [])
        }

        if response["clarification_needed"]:
            response["ambiguity_reason"] = classification.get("reasoning", "Unclear intent")

        return response

    except Exception as e:
        logger.error(f"LLM-driven classification failed: {e}. Falling back to clarification.")
        return {
            "clarification_needed": True,
            "domain": "NEEDS_CLARIFICATION",
            "confidence": "Low",
            "ambiguity_reason": f"Classification error (non-blocking). Please clarify your question.",
            "clarification_questions": [
                "Are you asking about project delivery/schedule (PM) or technical/code analysis (ENG)?",
                "Do you have a specific defect ticket, sprint, or component to focus on?",
                "Would you like delivery impact analysis, technical RCA, or both?"
            ],
            "target_master": None,
            "target_capability": None,
            "confidence_score": 0.3
        }


def router_node(state: AxiomState) -> AxiomState:
    """
    LangGraph Node: Top-level intent router.
    Uses LLM-driven semantic classification to route to PM.ai or ENG.ai.
    Falls back to clarification if intent is ambiguous.
    """
    query = state.get("query", "")
    logger.info(f"ROUTER: Classifying query: {query[:100]}...")

    # LLM-driven semantic classification (not keyword matching)
    decision = analyze_intent_with_llm(query)

    # Populate state
    state["intent_clarified"] = not decision.get("clarification_needed", False)
    state["target_master"] = decision.get("target_master")
    state["target_capability"] = decision.get("target_capability")
    state["confidence_score"] = decision.get("confidence_score", 0.0)
    state["boundary_classification"] = decision.get("boundary_classification")

    logger.info(
        f"ROUTER: Classification complete. Master={state['target_master']}, "
        f"Confidence={state['confidence_score']}, Clarification={'Y' if decision.get('clarification_needed') else 'N'}"
    )

    if decision.get("clarification_needed"):
        state["clarification"] = {
            "clarification_needed": True,
            "ambiguity_reason": decision.get("ambiguity_reason", "Unclear intent"),
            "clarification_questions": decision.get("clarification_questions", [])
        }
        state["final_output_markdown"] = (
            "### Clarification Needed\n\n"
            f"> [!IMPORTANT]\n"
            f"> {decision.get('ambiguity_reason', 'Unclear intent')}\n\n"
            "To provide you with the most accurate analysis, please clarify:\n"
            + "\n".join(f"- {q}" for q in decision.get("clarification_questions", []))
        )
    else:
        state["clarification"] = {"clarification_needed": False}
        logger.info(f"ROUTER: Routed to {state['target_master']} with capability '{state['target_capability']}'")

    return state
