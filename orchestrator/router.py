"""
Top-Level Intent Router and Clarification Node for AXIOM.
Analyzes user queries, determines intent clarity, and routes to either PM.ai or ENG.ai Master,
or immediately terminates the run with targeted clarification questions.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Tuple
from orchestrator.state import AxiomState, ClarificationState

logger = logging.getLogger("axiom.orchestrator.router")

# Ambiguous keywords that lack necessary context
VAGUE_QUERY_PATTERNS = [
    r"^(hi|hello|hey|help|what can you do)\b",
    r"^(fix|check|analyze|investigate|look at)\s*(this|it|the issue|everything|something)?$",
    r"^what is the status\??$",
    r"^tell me about the project\??$"
]

PM_CAPABILITIES = {
    "preliminary_rca": ["preliminary rca", "high-level rca", "blast radius", "triage defect", "leakage direction"],
    "defect_triage": ["triage", "severity", "urgency", "classify defect", "issue 107", "gh-issue-107", "bug triage"],
    "requirement_impact": ["requirement", "req-", "impact analysis", "traceability", "dependent requirement", "unlock", "ble", "uwb", "offline grace", "valet"],
    "project_health": ["project health", "status", "delivery health", "scorecard", "commitments"],
    "sprint_replanning": ["replan", "replanning", "rebalance", "capacity rebalancing", "sprint slip", "sprint 4 replan"],
    "sprint_timeline_analysis": ["timeline", "critical path", "schedule variance", "forecast completion", "gantt"],
    "pi_planning": ["pi planning", "program increment", "quarterly planning", "pi roadmap"],
    "retrospective": ["retrospective", "sprint retro", "lessons learned", "volatility retro"]
}

ENG_CAPABILITIES = {
    "root_cause_analysis": ["deep rca", "code rca", "root cause", "ast inspection", "regression commit", "single threshold"],
    "eight_d_analysis": ["8d", "eight disciplines", "ishikawa", "fishbone", "containment action", "permanent corrective action"],
    "five_why_analysis": ["5 why", "five why", "why analysis", "causal ladder"],
    "code_fixing": ["code fix", "patch", "surgical fix", "hysteresis fix", "generate patch", "pull request", "fix code"],
    "test_case_generation": ["generate test", "test case generation", "pytest", "boundary test", "oscillation test"],
    "increasing_test_coverage": ["increase coverage", "test coverage", "branch coverage", "untested branch"]
}


def analyze_intent(query: str) -> Dict[str, Any]:
    """
    Analyzes user query to extract intent, target master, target capability, and entities.
    Determines if clarification is required before proceeding.
    """
    cleaned_query = query.strip().lower()

    # Check for obvious ambiguous / underspecified queries
    for pattern in VAGUE_QUERY_PATTERNS:
        if re.search(pattern, cleaned_query):
            return {
                "clarification_needed": True,
                "ambiguity_reason": "Query lacks specific entity context (e.g., defect ID, sprint number, or technical goal).",
                "clarification_questions": [
                    "Are you looking for project-level delivery triage (PM.ai) or technical code-level investigation (ENG.ai)?",
                    "Do you have a specific defect ticket (e.g., GH-ISSUE-107) or sprint (e.g., SPRINT-04) you want to analyze?",
                    "Would you like an 8D root-cause investigation, sprint replanning proposal, or test coverage expansion?"
                ],
                "target_master": None,
                "target_capability": None,
                "confidence_score": 0.2
            }

    # Match Engineering capabilities
    for cap, keywords in ENG_CAPABILITIES.items():
        if any(kw in cleaned_query for kw in keywords):
            return {
                "clarification_needed": False,
                "target_master": "ENG.ai",
                "target_capability": cap,
                "confidence_score": 0.95,
                "reasoning_summary": f"Detected technical engineering intent matching capability '{cap}'. Routed to ENG.ai.",
                "clarification_questions": []
            }

    # Match PM capabilities
    for cap, keywords in PM_CAPABILITIES.items():
        if any(kw in cleaned_query for kw in keywords):
            return {
                "clarification_needed": False,
                "target_master": "PM.ai",
                "target_capability": cap,
                "confidence_score": 0.95,
                "reasoning_summary": f"Detected project management / delivery governance intent matching capability '{cap}'. Routed to PM.ai.",
                "clarification_questions": []
            }

    # Default fallback routing if mentions bugs/issues
    if "bug" in cleaned_query or "issue" in cleaned_query:
        return {
            "clarification_needed": False,
            "target_master": "PM.ai",
            "target_capability": "defect_triage",
            "confidence_score": 0.85,
            "reasoning_summary": "Issue mention detected. Defaulting to initial defect triage with PM.ai.",
            "clarification_questions": []
        }

    # If completely unrecognized, request clarification rather than guessing wrong
    return {
        "clarification_needed": True,
        "ambiguity_reason": "Could not determine whether this inquiry pertains to Project Delivery (PM.ai) or Code Engineering (ENG.ai).",
        "clarification_questions": [
            "Are you requesting Project Management governance (e.g., sprint replanning, defect triage, timeline forecasting)?",
            "Are you requesting Engineering analysis (e.g., code-level RCA, 8D problem solving, pytest generation, surgical patch)?",
            "Which component or ticket should we target (e.g., proximity_controller.py or GH-ISSUE-107)?"
        ],
        "target_master": None,
        "target_capability": None,
        "confidence_score": 0.3
    }


def router_node(state: AxiomState) -> AxiomState:
    """
    LangGraph Node: Top-level intent router.
    Evaluates state['query'] and populates routing decision or clarification payload.
    """
    query = state.get("query", "")
    decision = analyze_intent(query)

    state["intent_clarified"] = not decision["clarification_needed"]
    state["target_master"] = decision.get("target_master")
    state["target_capability"] = decision.get("target_capability")
    state["confidence_score"] = decision.get("confidence_score", 0.0)

    if decision["clarification_needed"]:
        state["clarification"] = {
            "clarification_needed": True,
            "ambiguity_reason": decision["ambiguity_reason"],
            "clarification_questions": decision["clarification_questions"]
        }
        state["final_output_markdown"] = (
            "### Clarification Needed\n\n"
            f"> [!IMPORTANT]\n"
            f"> {decision['ambiguity_reason']}\n\n"
            "To provide you with the most accurate analysis, please clarify:\n"
            + "\n".join(f"- {q}" for q in decision["clarification_questions"])
        )
    else:
        state["clarification"] = {"clarification_needed": False}

    return state
