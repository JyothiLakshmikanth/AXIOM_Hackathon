"""
AXIOM Shared Master Cognitive Nodes.

Consolidates PM.ai and ENG.ai master node implementations into a single
parameterized set of nodes that work for both masters by checking
state["target_master"] and loading master-specific configurations.

Nodes:
  1. reason_node - Classify intent and determine required evidence dimensions
  2. memory_retrieval_node - Check Firestore cache for verified evidence
  3. plan_node - Intelligent agent selection via LLM planner
  4. execute_agent_node - Delegate to selected specialized agent
  5. observe_evidence_node - Ingest and normalize evidence envelopes
  6. evaluate_node - Check evidence sufficiency and identify gaps

Both AXIOM-PM and AXIOM-ENG use these same nodes; behavior is parameterized
by target_master, capability, and master-specific registries.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from orchestrator.state import AxiomState
from orchestrator.base_master import (
    base_reason_node,
    base_plan_node,
    base_evaluate_node,
    shared_evidence_checklist
)
from agents.tools.firestore_tools import (
    firestore_get_cached_evidence,
    firestore_cache_evidence,
    firestore_save_session_turn
)
from agents.defect_agent import defect_agent
from agents.resource_agent import resource_agent
from agents.requirement_agent import requirement_agent
from agents.test_agent import test_agent
from agents.codefix_agent import codefix_agent

logger = logging.getLogger("axiom.orchestrator.master_nodes")


# ============================================================================
# REGISTRY LOADING (SHARED)
# ============================================================================

def load_json_file(rel_path: str) -> Dict[str, Any]:
    """Load JSON registry file relative to project root."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


SKILL_REGISTRY = load_json_file("registries/skill_registry.json").get("skills", {})
CAPABILITY_MATRIX = load_json_file("registries/capability_matrix.json").get("capabilities", {})
AGENT_REGISTRY = load_json_file("registries/agent_registry.json").get("agents", {})


# ============================================================================
# MASTER CONFIGURATIONS (PM vs ENG)
# ============================================================================

# PM-specific evidence dimension requirements by capability
PM_CAPABILITY_EVIDENCE_DIMS = {
    "defect_triage": [
        "github_issue_record",
        "severity_classification",
        "requirement_impact",
        "test_coverage"
    ],
    "sprint_replanning": [
        "velocity_history",
        "team_capacity",
        "defect_backlog"
    ],
    "resource_allocation": [
        "team_capacity",
        "velocity_history",
        "resource_allocation"
    ],
    "requirement_impact": [
        "requirement_impact",
        "github_issue_record"
    ],
    "project_health": [
        "velocity_history",
        "team_capacity",
        "defect_backlog"
    ]
}

# ENG-specific evidence dimension requirements by capability
ENG_CAPABILITY_EVIDENCE_DIMS = {
    "root_cause_analysis": [
        "github_issue_record",
        "git_commit_history",
        "source_code_analysis",
        "test_coverage"
    ],
    "eight_d_analysis": [
        "problem_definition",
        "containment_action",
        "root_cause_analysis",
        "corrective_action"
    ],
    "five_why_analysis": [
        "initial_symptom",
        "causal_evidence",
        "root_cause_hypothesis"
    ],
    "code_fixing": [
        "root_cause_record",
        "patch_candidate",
        "test_validation"
    ],
    "test_case_generation": [
        "requirement_specification",
        "boundary_conditions",
        "test_framework"
    ]
}


# ============================================================================
# HYPOTHESIS BUILDERS (MASTER-SPECIFIC)
# ============================================================================

def _pm_hypothesis_builder(query: str, capability_id: str) -> str:
    """Build PM-specific hypothesis based on query and capability."""
    query_lower = query.lower()

    if "sprint" in query_lower or "velocity" in query_lower or "replan" in query_lower:
        return (
            "Sprint 4 delivery commitments may slip due to velocity volatility and developer overallocation. "
            "Need historical velocity records and team capacity envelopes."
        )
    elif "107" in query or "defect" in query_lower or "bug" in query_lower:
        return (
            "GH-ISSUE-107 represents an S1 critical blocker threatening Milestone Alpha delivery. "
            "Need authoritative defect record, linked requirement in Neo4j, and severity classification."
        )
    else:
        return f"Project inquiry requires governance assessment under capability '{capability_id}'."


def _eng_hypothesis_builder(query: str, capability_id: str) -> str:
    """Build ENG-specific hypothesis based on query and capability."""
    query_lower = query.lower()

    if "8d" in query_lower:
        return "Customer defect requires formal 8D problem solving methodology from D1 to D8."
    elif "5 why" in query_lower or "why" in query_lower:
        return "Defect manifestation requires recursive 5-Why causal ladder from physical symptom to CI governance."
    elif "patch" in query_lower or "fix" in query_lower:
        return "Need deterministic surgical patch adding hysteresis band to proximity_controller.py."
    else:
        return (
            "Proximity controller exhibits boundary oscillation near 2.0m threshold. "
            "Hypothesis: single conditional threshold without hysteresis deadband or debounce state causes relay cycling."
        )


def get_master_config(master_id: str) -> Dict[str, Any]:
    """
    Retrieve master-specific configuration.

    Args:
        master_id: "AXIOM-PM" or "AXIOM-ENG"

    Returns:
        Dict with capability_evidence_dims and hypothesis_builder
    """
    if master_id == "AXIOM-PM":
        return {
            "capability_evidence_dims": PM_CAPABILITY_EVIDENCE_DIMS,
            "hypothesis_builder": _pm_hypothesis_builder
        }
    elif master_id == "AXIOM-ENG":
        return {
            "capability_evidence_dims": ENG_CAPABILITY_EVIDENCE_DIMS,
            "hypothesis_builder": _eng_hypothesis_builder
        }
    else:
        # Default to PM if unknown
        logger.warning(f"Unknown master_id '{master_id}', defaulting to AXIOM-PM")
        return {
            "capability_evidence_dims": PM_CAPABILITY_EVIDENCE_DIMS,
            "hypothesis_builder": _pm_hypothesis_builder
        }


# ============================================================================
# SHARED COGNITIVE NODES (PARAMETERIZED)
# ============================================================================

def reason_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: REASON.
    Analyzes context, hypothesizes delivery/technical risks, and determines required evidence.
    Shared for both PM.ai and ENG.ai, delegating to base_reason_node with master-specific configs.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with reasoning_hypothesis, required_evidence_dimensions, resolved_intent
    """
    master_id = state.get("target_master", "AXIOM-PM")
    config = get_master_config(master_id)

    return base_reason_node(
        state,
        config["capability_evidence_dims"],
        config["hypothesis_builder"],
        master_id
    )


def memory_retrieval_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: MEMORY_RETRIEVAL.
    Checks Firestore runtime memory for previously verified EvidenceEnvelopes.
    If authoritative evidence exists, skips specialized agent calls and proceeds to EVALUATE.
    Shared for both PM.ai and ENG.ai.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with memory_hit flag and evidence_envelopes if cache hit
    """
    master_id = state.get("target_master", "AXIOM-PM")
    query = state.get("query", "")
    logger.info(f"{master_id} MEMORY_RETRIEVAL: Checking Firestore cache...")

    # Determine target artifact ID based on query context
    target_id: Optional[str] = None

    if master_id == "AXIOM-PM":
        # PM.ai looks for issues and requirements
        if "107" in query:
            target_id = "GH-ISSUE-107"
        elif "004" in query:
            target_id = "REQ-004"
    else:  # AXIOM-ENG
        # ENG.ai looks for patches and technical artifacts
        if "patch" in query.lower() or "fix" in query.lower():
            target_id = "PATCH-proximity_controller.py"

    state["memory_hit"] = False
    if target_id:
        cached_evidence = firestore_get_cached_evidence(target_id)
        if cached_evidence and cached_evidence.get("quality_status") == "verified":
            logger.info(f"{master_id} MEMORY_HIT: Found verified evidence in Firestore for {target_id}.")
            if "evidence_envelopes" not in state or not state["evidence_envelopes"]:
                state["evidence_envelopes"] = []
            state["evidence_envelopes"].append(cached_evidence)
            state["memory_hit"] = True
    else:
        logger.debug(f"{master_id} MEMORY_RETRIEVAL: No cacheable artifact identified in query.")

    return state


def plan_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: PLAN / SELECT SKILL.
    Uses intelligent planner LLM to decide which agent to call.
    Replaces hardcoded skill selection with context-aware agent selection.
    Shared for both PM.ai and ENG.ai.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with selected_skill and current_step
    """
    master_id = state.get("target_master", "AXIOM-PM")
    return base_plan_node(state, master_id)


def execute_agent_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: EXECUTE SPECIALIZED AGENT.
    Delegates domain evidence gathering to the chosen LangChain ReAct agent.
    Master-specific agent delegation based on selected skill.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with agent_task_input and observed_new_evidences
    """
    master_id = state.get("target_master", "AXIOM-PM")
    agent_id = state.get("delegated_agent", "defect_agent")
    query = state.get("query", "")

    logger.info(f"{master_id} EXECUTE: Delegating to LangChain agent '{agent_id}'")

    result = {}

    if master_id == "AXIOM-PM":
        # PM.ai agents
        if agent_id == "defect_agent":
            issue_id = "GH-ISSUE-107" if "107" in query else "GH-ISSUE-107"
            result = defect_agent.execute_react_loop({"action": "triage_issue", "issue_id": issue_id})
        elif agent_id == "resource_agent":
            result = resource_agent.execute_react_loop({"action": "analyze_team_capacity", "sprint_id": "SPRINT-04"})
        elif agent_id == "requirement_agent":
            req_matches = [w.strip(".,;:()") for w in query.split() if w.strip(".,;:()").startswith("REQ-")]
            if req_matches:
                result = requirement_agent.execute_react_loop({"query_type": "impact_analysis", "requirement_ids": req_matches})
            elif any(kw in query.lower() for kw in ["defect", "bug", "fails", "failure", "issue", "unlock", "grace"]):
                result = requirement_agent.execute_react_loop({"query_type": "defect_impact_analysis", "defect_summary": query})
            else:
                result = requirement_agent.execute_react_loop({"query_type": "lookup_by_id", "requirement_id": "REQ-L2-001"})
        elif agent_id == "test_agent":
            result = test_agent.execute_react_loop({"action": "get_test_results", "target_id": "proximity_controller.py"})
        else:
            result = defect_agent.execute_react_loop({"action": "triage_issue", "issue_id": "GH-ISSUE-107"})

    else:  # AXIOM-ENG
        # ENG.ai agents
        if agent_id == "codefix_agent":
            result = codefix_agent.execute_react_loop({"action": "isolate_regression", "file_path": "proximity_controller.py"})
        elif agent_id == "test_agent":
            result = test_agent.execute_react_loop({"action": "generate_boundary_tests", "target_id": "proximity_controller.py"})
        elif agent_id == "requirement_agent":
            req_matches = [w.strip(".,;:()") for w in query.split() if w.strip(".,;:()").startswith("REQ-")]
            if req_matches:
                result = requirement_agent.execute_react_loop({"query_type": "impact_analysis", "requirement_ids": req_matches})
            elif any(kw in query.lower() for kw in ["defect", "bug", "fails", "failure", "issue", "unlock", "grace"]):
                result = requirement_agent.execute_react_loop({"query_type": "defect_impact_analysis", "defect_summary": query})
            else:
                result = requirement_agent.execute_react_loop({"query_type": "lookup_by_id", "requirement_id": "REQ-L2-001"})
        else:
            result = codefix_agent.execute_react_loop({"action": "isolate_regression", "file_path": "proximity_controller.py"})

    state["agent_task_input"] = {"executed_agent": agent_id, "summary": result.get("summary")}
    state["observed_new_evidences"] = result.get("evidences", [])

    return state


def observe_evidence_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: OBSERVE EVIDENCE.
    Ingests and normalizes EvidenceEnvelopes, persisting them into Firestore runtime cache.
    Shared for both PM.ai and ENG.ai.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with accumulated evidence_envelopes
    """
    master_id = state.get("target_master", "AXIOM-PM")
    new_evidences = state.pop("observed_new_evidences", [])

    if "evidence_envelopes" not in state or not state["evidence_envelopes"]:
        state["evidence_envelopes"] = []

    for env in new_evidences:
        state["evidence_envelopes"].append(env)
        # Cache to Firestore runtime
        if "artifact_id" in env:
            firestore_cache_evidence(env["artifact_id"], env)

    logger.info(f"{master_id} OBSERVE: Total observed EvidenceEnvelopes={len(state['evidence_envelopes'])}")
    return state


def evaluate_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: EVALUATE.
    Evaluates collected evidence against capability requirements.
    Checks sufficiency and identifies material gaps.
    Determines whether to iterate back to REASON or proceed to SYNTHESIZE.
    Shared for both PM.ai and ENG.ai, with master-specific checklists.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with evaluation_passed, material_gaps, and evaluation_checklist_results
    """
    master_id = state.get("target_master", "AXIOM-PM")

    # Use base evaluation
    state = base_evaluate_node(state, CAPABILITY_MATRIX, master_id)

    # Add master-specific checklist results
    evidences = state.get("evidence_envelopes", [])

    if master_id == "AXIOM-PM":
        # PM-specific checklist
        state["evaluation_checklist_results"] = shared_evidence_checklist(evidences)
    else:  # AXIOM-ENG
        # ENG-specific technical checklist
        state["evaluation_checklist_results"] = {
            "regression_commit_proven": any(e.get("artifact_type") == "git_commit_diff" for e in evidences),
            "ast_logic_isolated": any(e.get("artifact_type") == "source_ast_inspection" for e in evidences),
            "patch_syntax_verified": any(e.get("artifact_type") == "proposed_surgical_patch" for e in evidences)
        }

    return state
