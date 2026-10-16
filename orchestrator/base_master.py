"""
AXIOM Base Master Cognitive Framework.
Provides shared REASON, PLAN, and EVALUATE node implementations
that both AXIOM-PM and AXIOM-ENG masters inherit from.

This eliminates duplication and ensures consistent cognitive patterns across domains.
"""

import logging
from typing import Dict, Any, List
from orchestrator.state import AxiomState
from orchestrator.planner_node import plan_node
from orchestrator.evidence_cache import evaluate_evidence_sufficiency, extract_material_gaps

logger = logging.getLogger("axiom.orchestrator.base_master")


def base_reason_node(
    state: AxiomState,
    capability_to_evidence_dims: Dict[str, List[str]],
    hypothesis_builder: callable,
    domain_name: str
) -> AxiomState:
    """
    Shared REASON Node implementation.

    Analyzes context, formulates causal hypotheses, and determines required evidence.

    Args:
        state: Current AxiomState
        capability_to_evidence_dims: Dict mapping capability IDs to required evidence dimensions
        hypothesis_builder: Callable that generates domain-specific hypotheses
        domain_name: Domain identifier ("AXIOM-PM" or "AXIOM-ENG")

    Returns:
        Updated AxiomState with reasoning_hypothesis, required_evidence_dimensions, and resolved_intent
    """
    capability_id = state.get("target_capability", "defect_triage")
    query = state.get("query", "")
    iteration = state.get("evaluation_iteration_count", 0)

    logger.info(f"{domain_name} REASON: Capability='{capability_id}', Iteration={iteration}")

    # Determine required evidence dimensions
    required_evidence_dimensions = capability_to_evidence_dims.get(
        capability_id,
        ["github_issue_record", "severity_classification"]
    )
    state["required_evidence_dimensions"] = required_evidence_dimensions

    # Generate domain-specific hypothesis
    hypothesis = hypothesis_builder(query, capability_id)
    state["reasoning_hypothesis"] = hypothesis
    state["resolved_intent"] = capability_id

    state["current_step"] = "REASON"
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


def base_evaluate_node(
    state: AxiomState,
    capability_matrix: Dict[str, Any],
    domain_name: str
) -> AxiomState:
    """
    Shared EVALUATE Node implementation.

    Assesses collected evidence against required dimensions.
    Determines sufficiency and identifies material gaps.

    Args:
        state: Current AxiomState
        capability_matrix: Registry of capability definitions
        domain_name: Domain identifier for logging

    Returns:
        Updated AxiomState with evaluation results and gap analysis
    """
    collected_envelopes = state.get("evidence_envelopes", [])
    required_dims = state.get("required_evidence_dimensions", [])
    iteration = state.get("evaluation_iteration_count", 0)

    logger.info(
        f"{domain_name} EVALUATE: Iteration={iteration}, "
        f"Evidence count={len(collected_envelopes)}, "
        f"Required dimensions={len(required_dims)}"
    )

    # Evaluate evidence sufficiency
    sufficiency = evaluate_evidence_sufficiency(
        collected_envelopes,
        required_dims,
        capability_matrix
    )

    state["evidence_sufficiency"] = sufficiency

    # Extract material gaps
    gaps = extract_material_gaps(required_dims, collected_envelopes)
    state["material_gaps"] = gaps

    # Determine if we should proceed or loop
    evaluation_passed = sufficiency == "SUFFICIENT"
    state["evaluation_passed"] = evaluation_passed
    state["evaluation_iteration_count"] = iteration + 1

    logger.info(
        f"{domain_name} EVALUATE: Sufficiency={sufficiency}, "
        f"Evaluation_passed={evaluation_passed}, "
        f"Missing dimensions={len(gaps.get('missing_dimensions', []))}"
    )

    return state


def shared_evidence_checklist(evidences: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Shared checklist for basic evidence quality assessment.

    Args:
        evidences: List of evidence envelopes

    Returns:
        Dict with keys: authoritative_record_present, provenance_verified, confidence_threshold_met
    """
    if not evidences:
        return {
            "authoritative_record_present": False,
            "provenance_verified": False,
            "confidence_threshold_met": False
        }

    return {
        "authoritative_record_present": len(evidences) > 0,
        "provenance_verified": all(e.get("authoritative", True) for e in evidences),
        "confidence_threshold_met": len(evidences) >= 2
    }
