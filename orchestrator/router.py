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
from orchestrator.gemini_client import generate_gemini_content

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
        # Load the official router prompt from prompts/axiom_router_v3.json
        intent_classifier_prompt = load_prompt("axiom_router", "router_node")

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
        logger.info(f"[LLM] Router: Analyzing intent for query: {query[:60]}...")
        llm_response = generate_gemini_content(
            prompt=llm_input,
            system_prompt="You are an expert intent router for intelligent systems. Classify user queries semantically into project delivery (PJM) or engineering (ENG) domains.",
            json_mode=True,
            timeout=25
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
            "PM": "AXIOM-PM",
            "PROJECT_MANAGEMENT": "AXIOM-PM",
            "ENG": "AXIOM-ENG",
            "ENGINEERING": "AXIOM-ENG",
            "BOTH": "AXIOM-PM"  # Start with PM if both needed
        }

        domain_raw = str(classification.get("domain", "")).strip().upper()
        target_master = domain_to_master.get(domain_raw)
        if not target_master and classification.get("domain") != "NEEDS_CLARIFICATION":
            target_master = "AXIOM-ENG" if "ENG" in domain_raw else "AXIOM-PM"
        target_capability = classification.get("target_capability")
        raw_conf = str(classification.get("confidence", "Low")).strip().capitalize()
        confidence_level = raw_conf if raw_conf in ("High", "Medium", "Low") else "Medium"
        confidence_score = {"High": 0.95, "Medium": 0.70, "Low": 0.4}.get(
            confidence_level, 0.4
        )

        # Build response
        response = {
            "clarification_needed": classification.get("domain") == "NEEDS_CLARIFICATION",
            "domain": classification.get("domain"),
            "target_master": target_master,
            "target_capability": target_capability,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "boundary_classification": classification.get("boundary_classification"),
            "reasoning_summary": classification.get("reasoning"),
            "clarification_questions": classification.get("clarification_questions", [])
        }

        if response["clarification_needed"]:
            response["ambiguity_reason"] = classification.get("reasoning", "Unclear intent")

        return response

    except Exception as e:
        logger.warning(f"LLM-driven classification unavailable ({e}). Using deterministic rule fallback.")
        return _fallback_intent_classification(query)


def _fallback_intent_classification(query: str) -> Dict[str, Any]:
    """Deterministic fallback classification when GCP Vertex LLM is offline or not configured."""
    q = query.lower()

    is_eng = any(w in q for w in ["rca", "code", "patch", "ast", "diff", "regression", "proximity_controller", "controller.py", "unit test", "pytest", "fix", "code fix", "pr", "pull request", "remediate"])
    is_pm = any(w in q for w in ["sprint", "velocity", "capacity", "rebalance", "allocat", "schedule", "milestone", "pi plan", "burn", "bottleneck", "blast radius", "triage"])

    # High-priority: Combined Defect Analysis + Code Fix queries
    if any(w in q for w in ["fix", "code fix", "patch", "remediate", "pull request", "pr"]) and any(w in q for w in ["defect", "issue", "ticket", "twk", "gh-", "triage", "analysis"]):
        return {
            "clarification_needed": False,
            "domain": "ENG",
            "target_master": "AXIOM-ENG",
            "target_capability": "defect_triage_and_remediation",
            "confidence_score": 0.95,
            "boundary_classification": "cross_domain_fix",
            "reasoning": "Query requests defect triage analysis and surgical code fix."
        }

    if is_eng and not is_pm:
        return {
            "clarification_needed": False,
            "domain": "ENG",
            "target_master": "AXIOM-ENG",
            "target_capability": "Deep Code RCA & Surgical Patching",
            "confidence_score": 0.85,
            "boundary_classification": "micro_technical",
            "reasoning": "Query matches engineering domain (code/patch/RCA)."
        }
    elif is_pm or any(w in q for w in ["defect", "issue", "gh-", "twk-", "bug"]):
        return {
            "clarification_needed": False,
            "domain": "PJM",
            "target_master": "AXIOM-PM",
            "target_capability": "Defect Triage & Impact Blast Radius" if any(w in q for w in ["triage", "blast", "issue", "twk", "gh-"]) else "Sprint Replanning & Capacity Balancing",
            "confidence_score": 0.90,
            "boundary_classification": "macro_delivery",
            "reasoning": "Query matches project management domain (triage/capacity/sprint)."
        }
    return {
        "clarification_needed": True,
        "domain": "NEEDS_CLARIFICATION",
        "confidence": "Low",
        "ambiguity_reason": "Could not classify intent reliably. Please clarify your request.",
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
    router_prompt = load_prompt("axiom_router", "router_node")
    state["system_prompt_router"] = router_prompt
    decision = analyze_intent_with_llm(query)

    # Populate state
    state["intent_clarified"] = not decision.get("clarification_needed", False)
    state["target_master"] = decision.get("target_master")
    state["target_capability"] = decision.get("target_capability")
    state["confidence_score"] = decision.get("confidence_score", 0.0)
    state["confidence_level"] = decision.get("confidence_level", "Medium")
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


# Backward compatibility alias
analyze_intent = analyze_intent_with_llm

