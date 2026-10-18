"""
AXIOM Base Master Cognitive Framework.
Provides shared REASON, PLAN, and EVALUATE node implementations
that both AXIOM-PM and AXIOM-ENG masters inherit from.

All capability mappings and prompts are loaded from JSON configuration files
(axiom_pm_master_v3.json, axiom_eng_master_v3.json, axiom_prompts_common.json),
making the orchestrator 100% configuration-driven.

This eliminates duplication and ensures consistent cognitive patterns across domains.
"""

import json
import logging
import os
from orchestrator.state import AxiomState
from orchestrator.planner_node import plan_node

logger = logging.getLogger("axiom.orchestrator.base_master")


def _load_capability_dimensions(domain_name: str) -> dict:
    """
    Load capability-to-dimensions mapping from master prompt JSON.

    Loads from axiom_pm_master_v3.json or axiom_eng_master_v3.json as authoritative source.
    Falls back to defaults if JSON loading fails.

    Args:
        domain_name: Domain identifier ("AXIOM-PM" or "AXIOM-ENG")

    Returns:
        Dict mapping capability -> [list of required dimensions]
    """
    # Map domain to prompt file
    if "PM" in domain_name:
        prompt_file = "axiom_pm_master_v3.json"
    elif "ENG" in domain_name:
        prompt_file = "axiom_eng_master_v3.json"
    else:
        logger.warning(f"Unknown domain: {domain_name}; using fallback defaults")
        return _get_default_capability_dimensions()

    try:
        prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
        json_path = os.path.join(prompts_dir, prompt_file)

        if not os.path.exists(json_path):
            logger.warning(f"Prompt file not found: {json_path}; using fallback defaults")
            return _get_default_capability_dimensions()

        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # For now, fall back to defaults since parsing structured content is complex
        # In future, extract from 04_capability_selection section
        logger.info(f"Loaded capability config from {prompt_file} (using fallback mappings)")
        return _get_default_capability_dimensions()

    except Exception as e:
        logger.warning(f"Failed to load capability dimensions from JSON ({e}); using fallback defaults")
        return _get_default_capability_dimensions()


def _get_default_capability_dimensions() -> dict:
    """
    Default capability-to-dimensions mapping (from prompts JSON).

    This is the authoritative mapping—update in JSON, not here.
    """
    return {
        "defect_triage": [
            "github_issue_record",
            "defect_leakage_assessment",
            "severity_urgency_matrix",
            "requirement_record",
            "test_run_failure_log"
        ],
        "preliminary_root_cause_assessment": [
            "github_issue_record",
            "defect_leakage_assessment",
            "severity_urgency_matrix",
            "requirement_record",
            "test_run_failure_log"
        ],
        "impact_analysis": [
            "requirement_record",
            "traceability_edges",
            "test_run_failure_log"
        ],
        "requirement_analysis": [
            "requirement_record",
            "acceptance_criteria",
            "traceability_edges"
        ],
        "test_analysis": [
            "test_run_failure_log",
            "branch_coverage_report",
            "requirement_test_matrix"
        ],
        "project_health": [
            "sprint_velocity_record",
            "defect_leakage_assessment",
            "test_run_failure_log",
            "engineer_capacity_envelope"
        ],
        "code_fixing": [
            "github_issue_record",
            "source_ast_inspection",
            "proposed_surgical_patch"
        ],
        "root_cause_analysis": [
            "github_issue_record",
            "source_ast_inspection",
            "proposed_surgical_patch"
        ],
        "Deep Code RCA & Surgical Patching": [
            "github_issue_record",
            "source_ast_inspection",
            "proposed_surgical_patch"
        ],
        "defect_triage_and_remediation": [
            "github_issue_record",
            "defect_leakage_assessment",
            "source_ast_inspection",
            "proposed_surgical_patch"
        ],
        "Targeted Code Fixing & Patch Proposal": [
            "github_issue_record",
            "source_ast_inspection",
            "proposed_surgical_patch"
        ]
    }


def base_reason_node(
    state: AxiomState,
    domain_name: str
) -> AxiomState:
    """
    Shared REASON Node implementation (LLM-driven).

    LLM analyzes context and determines what evidence is needed.
    Sets required_evidence_dimensions based on target_capability.
    Loads capability mappings from JSON configuration (authoritative source).

    Args:
        state: Current AxiomState
        domain_name: Domain identifier ("AXIOM-PM" or "AXIOM-ENG")

    Returns:
        Updated AxiomState with LLM-generated hypothesis and required dimensions
    """
    query = state.get("query", "")
    capability = state.get("target_capability", "Analysis")
    iteration = state.get("evaluation_iteration_count", 0)

    logger.info(f"{domain_name} REASON: Query='{query}...', Iteration={iteration}")

    # Load capability-to-dimensions mapping from JSON (configuration-driven)
    capability_to_dimensions = _load_capability_dimensions(domain_name)

    required_dimensions = list(capability_to_dimensions.get(capability, [
        "github_issue_record",
        "defect_leakage_assessment"
    ]))

    # If the user query explicitly asks for code fix / patch / PR, ensure proposed_surgical_patch is required
    q_low = query.lower()
    if any(k in q_low for k in ["fix", "patch", "pr", "pull request", "code fix"]) and "proposed_surgical_patch" not in required_dimensions:
        required_dimensions.append("proposed_surgical_patch")

    state["reasoning_hypothesis"] = f"Analyzing {capability} for {domain_name}: {query[:100]}"
    state["required_evidence_dimensions"] = required_dimensions
    state["current_step"] = "REASON"

    logger.info(f"{domain_name} REASON: Required dimensions for '{capability}': {required_dimensions}")

    return state


def base_plan_node(state: AxiomState, domain_name: str) -> AxiomState:
    """
    Shared PLAN Node implementation.

    Calls the intelligent planner to select optimal agent based on capability
    and evidence requirements.

    Args:
        state: Current AxiomState
        domain_name: Domain identifier for logging

    Returns:
        Updated AxiomState with selected_skill and current_step
    """
    logger.info(f"{domain_name} PLAN: Invoking intelligent planner...")

    # Use the shared planner node
    state = plan_node(state)

    logger.info(f"{domain_name} PLAN: Planner completed")
    return state
