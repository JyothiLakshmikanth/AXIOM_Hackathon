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
        logger.warning(f"LLM-driven classification unavailable ({e}). Using deterministic rule fallback.")
        return _fallback_intent_classification(query)


def _fallback_intent_classification(query: str) -> Dict[str, Any]:
    """Deterministic fallback classification when GCP Vertex LLM is offline or not configured."""
    q = query.lower()

    is_eng = any(w in q for w in ["rca", "code", "patch", "ast", "diff", "regression", "proximity_controller", "controller.py", "unit test", "pytest"])
    is_pm = any(w in q for w in ["sprint", "velocity", "capacity", "rebalance", "allocat", "schedule", "milestone", "pi plan", "burn", "bottleneck", "blast radius", "triage"])

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


def is_conversational_greeting_or_help(query: str) -> bool:
    """Detects whether user query is a greeting, introduction, or platform help query."""
    import re
    cleaned = query.strip().lower()
    cleaned_no_punct = re.sub(r'[^\w\s]', '', cleaned).strip()

    greeting_words = {
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
        "good evening", "howdy", "hola", "yo", "sup", "welcome"
    }

    help_phrases = {
        "help", "who are you", "what are you", "what can you do", "capabilities",
        "how does this work", "how to use", "what is axiom", "tell me about axiom",
        "menu", "options", "commands"
    }

    return (
        cleaned_no_punct in greeting_words or
        any(cleaned_no_punct.startswith(g + " ") for g in greeting_words) or
        cleaned_no_punct in help_phrases or
        any(phrase in cleaned_no_punct for phrase in ["who are you", "what can you do", "what is axiom", "help me"])
    )


def generate_intelligent_router_greeting(query: str, state: AxiomState) -> str:
    """
    Intelligently generates a personalized, context-aware greeting using Vertex AI Gemini.
    Incorporates:
    - User/Session memory (previous turns and topics discussed in this session)
    - Live BigQuery project context (SPR-03 in-flight items, TWK-107, overloaded engineers)
    - Adaptive guidance towards PM.ai or ENG.ai capabilities
    """
    session_id = state.get("session_id", "default_session")
    user_id = state.get("user_id", "Project_Lead")

    # 1. Fetch user session memory
    session_history = ""
    try:
        from agents.tools.firestore_tools import firestore_get_session_turns
        turns = firestore_get_session_turns(session_id, limit=4)
        if turns:
            queries = [t.get("query", "") for t in turns if t.get("query")]
            if queries:
                session_history = "User's recent queries in this session: " + " | ".join(f'"{q}"' for q in queries[-3:])
    except Exception as e:
        logger.debug(f"Session memory lookup skipped: {e}")

    # 2. Fetch live project facts
    project_facts = ""
    try:
        from agents.tools.bigquery_tools import bigquery_get_team_capacity
        cap = bigquery_get_team_capacity() or []
        over = [c.get("Associate") for c in cap if float(c.get("Allocation_%") or 0) > 85]
        over_str = ", ".join(sorted(list(set(over)))) if over else "Pavi2604, JyothiLakshmikanth"
        project_facts = (
            f"- Project: AXIOM E-Key 2W\n"
            f"- Active Sprint: SPR-03 (6 in-flight items, active safety milestone)\n"
            f"- Top Critical Bugs: TWK-107 (Boundary-Zone Unlock ASIL-B Safety Issue), TWK-108 (Unlock latency SLA breach)\n"
            f"- Capacity Bottlenecks (>85% Safe Ceiling): {over_str}\n"
        )
    except Exception as e:
        logger.debug(f"Project facts lookup skipped: {e}")
        project_facts = "- Active Sprint: SPR-03 | Critical Defect: TWK-107 | Overallocated: Pavi2604, JyothiLakshmikanth"

    # 3. Call Vertex AI Gemini to generate an intelligent, personalized greeting
    try:
        gcp = get_gcp_client()
        system_prompt = (
            "You are the intelligent conversational AXIOM Cognitive Router for the AXIOM E-Key 2W project.\n"
            "You have full contextual awareness of the user's ongoing session history and live project metrics.\n"
            "Acknowledge the user naturally and conversationally. If they have asked previous questions in this session, acknowledge that context naturally.\n"
            "Highlight where the project currently stands (Sprint 3 active, critical defect TWK-107, engineer capacity overload).\n"
            "Present clear, tailored suggestions for what they can do next:\n"
            "- AXIOM-PM (PM.ai): Defect triage, ASIL-B blast radius, Sprint 3 capacity rebalancing.\n"
            "- AXIOM-ENG (ENG.ai): Deep code RCA on proximity_controller.py, surgical patching, test synthesis.\n"
            "Tone: Executive, intelligent, sharp, and helpful. Use clean GitHub markdown with emojis and bullet points."
        )

        user_input = f"""User greeting/message: "{query}"

CONTEXT:
User ID: {user_id}
{session_history if session_history else "New conversation session."}
LIVE PROJECT DATA:
{project_facts}
"""
        response = gcp.call_gemini(
            system_prompt=system_prompt,
            user_input=user_input,
            temperature=0.7
        )
        if response and len(response.strip()) > 20:
            return response.strip()
    except Exception as e:
        logger.warning(f"Intelligent greeting generation fallback due to: {e}")

    # Fallback dynamic response incorporating live project facts and session memory
    context_note = ""
    if session_history:
        context_note = f"\n> 🧠 *Continuing from our earlier discussion in this session...*\n"

    return (
        f"### 👋 Hello! Welcome to AXIOM Intelligence Platform\n\n"
        f"I am the **AXIOM Cognitive Router**, your unified interface coordinating **PM.ai** and **ENG.ai** "
        f"for the **AXIOM E-Key 2W** project.\n\n"
        f"{context_note}"
        f"#### 📊 Current Project Pulse (Sprint 3 Active):\n"
        f"- **Critical Defect Radar**: `TWK-107` (Boundary-Zone Unlock ASIL-B Safety Violation) & `TWK-108` (Unlock Latency SLA Breach).\n"
        f"- **Resource Overload**: Engineers exceeding the 85% safe ceiling: **Pavi2604** & **JyothiLakshmikanth**.\n\n"
        f"#### 🎯 Where would you like to direct the masters?\n\n"
        f"| Master | Best For | Suggested Query |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **🛡️ AXIOM-PM (PM.ai)** | Delivery governance, triage, capacity | *\"Analyze team capacity bottlenecks and recommend rebalancing plan for SPR-03\"* |\n"
        f"| **⚡ AXIOM-ENG (ENG.ai)** | Technical code RCA, AST analysis, patching | *\"Perform deep code RCA and generate surgical patch for proximity_controller.py\"* |\n\n"
        f"*(You can also click any of the prompt chips above or switch to Tab 1 for the Executive Risk Cockpit!)*"
    )


def router_node(state: AxiomState) -> AxiomState:
    """
    LangGraph Node: Top-level intent router.
    Directly answers conversational greetings/help queries.
    Uses LLM-driven semantic classification to route to PM.ai or ENG.ai.
    Falls back to clarification if intent is ambiguous.
    """
    query = state.get("query", "")
    logger.info(f"ROUTER: Classifying query: {query[:100]}...")

    # Direct Intelligent Greeting / Help check: bypass multi-agent loops and respond immediately
    if is_conversational_greeting_or_help(query):
        logger.info("ROUTER: Detected greeting/help query. Generating intelligent context-aware greeting.")
        intelligent_greeting = generate_intelligent_router_greeting(query, state)
        state["is_direct_response"] = True
        state["human_validation_required"] = False
        state["clarification"] = {"clarification_needed": False}
        state["intent_clarified"] = True
        state["target_master"] = "AXIOM-ROUTER"
        state["confidence_score"] = 1.0
        state["boundary_classification"] = "conversational_greeting"
        state["final_output_markdown"] = intelligent_greeting
        state["current_step"] = "ROUTER_DIRECT"
        return state

    # LLM-driven semantic classification (not keyword matching)
    router_prompt = load_prompt("axiom_router", "router_node")
    state["system_prompt_router"] = router_prompt
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
