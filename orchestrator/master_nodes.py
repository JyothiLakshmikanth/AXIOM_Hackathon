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
    base_plan_node
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


AGENT_REGISTRY = load_json_file("registries/agent_registry.json").get("agents", {})




# ============================================================================
# SHARED COGNITIVE NODES (PARAMETERIZED)
# ============================================================================

def reason_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: REASON.
    LLM analyzes context and determines what evidence is needed.
    Fully LLM-driven, no hardcoded rules or static configurations.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with LLM-generated hypothesis
    """
    master_id = state.get("target_master", "AXIOM-PM")
    return base_reason_node(state, master_id)


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
    Invokes the agent selected by the planner with the planner's detailed prompt.
    No hardcoding — all execution instructions come from the planner.

    Args:
        state: Current AxiomState (includes planner_decision with agent_id and agent_prompt)

    Returns:
        Updated AxiomState with observed evidence from agent execution
    """
    master_id = state.get("target_master", "AXIOM-PM")

    # Get planner decision (from PLAN node)
    planner_decision = state.get("planner_decision", {})
    agent_id = planner_decision.get("agent_id") or state.get("delegated_agent", "defect_agent")
    agent_prompt = planner_decision.get("agent_prompt", "")
    required_skill = planner_decision.get("required_skill", "")

    logger.info(f"{master_id} EXECUTE: Invoking agent '{agent_id}' for skill '{required_skill}'")
    logger.debug(f"Agent prompt: {agent_prompt[:100]}...")

    # Handle synthesis-ready (no agent call needed)
    if agent_id == "SYNTHESIS_READY":
        logger.info(f"{master_id} EXECUTE: All evidence collected. Ready for synthesis.")
        state["observed_new_evidences"] = []
        return state

    # Dynamic agent invocation (no hardcoded if/else)
    agent_map = {
        "defect_agent": defect_agent,
        "requirement_agent": requirement_agent,
        "test_agent": test_agent,
        "codefix_agent": codefix_agent,
        "resource_agent": resource_agent
    }

    agent = agent_map.get(agent_id)
    if not agent:
        logger.error(f"Unknown agent: {agent_id}")
        state["observed_new_evidences"] = []
        return state

    try:
        # Build agent input: planner's prompt + extracted linked IDs from prior evidence
        agent_input = {
            "query": state.get("query", ""),
            "prompt": agent_prompt,
            "context": agent_prompt,
            "agent_prompt": agent_prompt,
            "user_id": state.get("user_id", "default-user"),
            "session_id": state.get("session_id", "default-session")
        }

        # Extract linked requirement IDs from defect evidence for requirement_agent
        evidence_envelopes = state.get("evidence_envelopes", [])
        if evidence_envelopes and agent_id == "requirement_agent":
            for env in evidence_envelopes:
                payload = env.get("payload", {})
                if payload.get("Linked_Requirements"):
                    linked_reqs = payload["Linked_Requirements"]
                    if isinstance(linked_reqs, str):
                        agent_input["requirement_ids"] = [r.strip() for r in linked_reqs.split(",")]
                    elif isinstance(linked_reqs, list):
                        agent_input["requirement_ids"] = linked_reqs
                    logger.debug(f"Extracted requirement IDs from defect evidence: {agent_input.get('requirement_ids')}")
                    break

        # Extract linked test case IDs from defect evidence for test_agent
        if evidence_envelopes and agent_id == "test_agent":
            for env in evidence_envelopes:
                payload = env.get("payload", {})
                if payload.get("Linked_Tests"):
                    linked_tests = payload["Linked_Tests"]
                    if isinstance(linked_tests, str):
                        agent_input["test_case_ids"] = [t.strip() for t in linked_tests.split(",")]
                    elif isinstance(linked_tests, list):
                        agent_input["test_case_ids"] = linked_tests
                    logger.debug(f"Extracted test case IDs from defect evidence: {agent_input.get('test_case_ids')}")
                    break

        # Extract defect context and linked artifacts for codefix_agent
        if evidence_envelopes and agent_id == "codefix_agent":
            for env in evidence_envelopes:
                payload = env.get("payload", {})
                if payload.get("Issue_Number") or payload.get("Id") or payload.get("Summary"):
                    agent_input["defect_id"] = str(payload.get("Id") or f"GH-{payload.get('Issue_Number')}")
                    agent_input["defect_summary"] = payload.get("Summary") or payload.get("Title")
                    if payload.get("Linked_Requirements"):
                        reqs = payload["Linked_Requirements"]
                        agent_input["linked_requirements"] = [r.strip() for r in reqs.split(",")] if isinstance(reqs, str) else reqs
                    if payload.get("Linked_Test_Cases") or payload.get("Linked_Tests"):
                        tcs = payload.get("Linked_Test_Cases") or payload.get("Linked_Tests")
                        agent_input["linked_tests"] = [t.strip() for t in tcs.split(",")] if isinstance(tcs, str) else tcs
                    logger.debug(f"Extracted defect context for codefix_agent: {agent_input.get('defect_id')}")
                    break

        # Call agent with planner's prompt + extracted IDs + user/session context
        result = agent.execute_react_loop(agent_input)

        state["observed_new_evidences"] = result.get("evidences", [])
        state["agent_task_input"] = {
            "executed_agent": agent_id,
            "summary": result.get("summary", ""),
            "skill": required_skill
        }
        if "executed_agents" not in state or not isinstance(state["executed_agents"], list):
            state["executed_agents"] = []
        if agent_id not in state["executed_agents"]:
            state["executed_agents"].append(agent_id)

        if "agent_executions" not in state or not isinstance(state["agent_executions"], list):
            state["agent_executions"] = []
        evs = result.get("evidences", [])
        state["agent_executions"].append({
            "agent_id": agent_id,
            "skill": required_skill,
            "summary": result.get("summary", ""),
            "evidences_count": len(evs),
            "evidence_types": [e.get("artifact_type") for e in evs if e and e.get("artifact_type")],
            "iteration": state.get("evaluation_iteration_count", 0) + 1
        })

        logger.info(f"{master_id} EXECUTE: Agent '{agent_id}' returned {len(result.get('evidences', []))} evidences")

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        state["observed_new_evidences"] = []
        state["agent_execution_error"] = str(e)

    return state


def observe_evidence_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: OBSERVE EVIDENCE.
    Ingests and normalizes EvidenceEnvelopes, persisting them to Firestore runtime cache.
    Evidence is scoped by user_id and session_id for privacy/isolation.
    Shared for both PM.ai and ENG.ai.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with accumulated evidence_envelopes
    """
    master_id = state.get("target_master", "AXIOM-PM")
    user_id = state.get("user_id", "default-user")
    session_id = state.get("session_id", "default-session")
    new_evidences = state.pop("observed_new_evidences", [])

    if "evidence_envelopes" not in state or not state["evidence_envelopes"]:
        state["evidence_envelopes"] = []

    for env in new_evidences:
        state["evidence_envelopes"].append(env)
        # Cache to Firestore runtime (user+session scoped)
        if "artifact_id" in env:
            firestore_cache_evidence(
                env["artifact_id"],
                env,
                user_id=user_id,
                session_id=session_id
            )

    logger.info(f"{master_id} OBSERVE: Total observed EvidenceEnvelopes={len(state['evidence_envelopes'])} (user={user_id}, session={session_id})")
    return state


def evaluate_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: EVALUATE.
    Validates collected evidence against required dimensions.
    SUFFICIENT only when all required evidence types are collected OR safety cap reached.

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with evidence-sufficiency validation
    """
    master_id = state.get("target_master", "AXIOM-PM")
    evidences = state.get("evidence_envelopes", [])
    required_dimensions = state.get("required_evidence_dimensions", [])

    # Increment evaluation iteration count
    state["evaluation_iteration_count"] = state.get("evaluation_iteration_count", 0) + 1

    # Compute missing required dimensions with semantic artifact equivalence
    EQUIVALENCE_MAP = {
        "jira_issue_record": {"github_issue_record", "defect_record", "jira_issue_record"},
        "github_issue_record": {"github_issue_record", "defect_record", "jira_issue_record"},
        "requirement_record": {"requirement_record", "requirement_details", "requirement_impact_analysis"},
        "requirement_details": {"requirement_record", "requirement_details", "requirement_impact_analysis"},
        "requirement_impact_analysis": {"requirement_record", "requirement_details", "requirement_impact_analysis"},
    }

    collected_raw_types = {env.get("artifact_type") for env in evidences if env}
    collected_types = set(collected_raw_types)
    for raw in collected_raw_types:
        if raw in EQUIVALENCE_MAP:
            collected_types.update(EQUIVALENCE_MAP[raw])

    missing_required = set(required_dimensions) - collected_types

    # SUFFICIENT only if all required dimensions collected OR safety cap (5 iterations)
    has_all_required = len(missing_required) == 0
    is_safety_cap = state["evaluation_iteration_count"] >= 5

    state["evaluation_passed"] = has_all_required
    state["evidence_sufficiency"] = "SUFFICIENT" if (has_all_required or is_safety_cap) else "INSUFFICIENT"
    state["material_gaps"] = list(missing_required)

    logger.info(f"{master_id} EVALUATE: Required dimensions: {required_dimensions}")
    logger.info(f"{master_id} EVALUATE: Collected types: {collected_types}")
    logger.info(f"{master_id} EVALUATE: Missing: {missing_required}")
    logger.info(f"{master_id} EVALUATE: Iteration {state['evaluation_iteration_count']} | Sufficiency: {state['evidence_sufficiency']}")

    return state
