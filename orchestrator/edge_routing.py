"""
AXIOM LangGraph Conditional Edge Routing.
Defines routing functions that determine the next node in the LangGraph based on state conditions.
These functions are used by builder.add_conditional_edges() to route between cognitive nodes.

Supports both AXIOM-PM and AXIOM-ENG master cognitive loops with unified routing logic.
"""

import logging
try:
    from langgraph.graph import END
except ImportError:
    END = "__end__"

from orchestrator.state import AxiomState

logger = logging.getLogger("axiom.orchestrator.edge_routing")


def route_after_intent_router(state: AxiomState) -> str:
    """
    Route after the top-level Intent Router node.

    Determines whether to proceed to the unified cognitive loop (both masters use same nodes)
    or terminate immediately if clarification is needed.

    Args:
        state: Current AXIOM state with intent routing results.

    Returns:
        Next node name: "reason" (unified node for both masters), or END.

    Logic:
        - If clarification_needed, return END (user must provide clarification)
        - Otherwise, proceed to shared "reason" node (target_master in state parameterizes behavior)
    """
    clarification = state.get("clarification", {})
    if clarification.get("clarification_needed", False):
        logger.info(
            "Intent Router: Clarification needed. Terminating. Reason: %s",
            clarification.get("ambiguity_reason", "Unknown")
        )
        return END

    master = state.get("target_master", "AXIOM-PM")
    logger.info(f"Intent Router: Routing to {master}. Starting shared cognitive loop at REASON node.")
    return "reason"  # Both masters use the same "reason" node


def route_after_memory(state: AxiomState) -> str:
    """
    Route after Memory Retrieval node.

    Determines whether cached evidence was found and can be used,
    or if a specialized agent call is needed via the PLAN node.

    Args:
        state: Current AXIOM state with memory retrieval results.

    Returns:
        Next node name: "evaluate" (if cache hit) or "plan" (if cache miss).
        Works for both PM.ai and ENG.ai (uses unified nodes).

    Logic:
        - If memory_hit=True, skip agent call and go directly to EVALUATE
        - Otherwise, proceed to PLAN to select and invoke a specialized agent
    """
    if state.get("memory_hit", False):
        logger.info("Memory Retrieval: Cache hit. Skipping agent call, jumping to EVALUATE.")
        return "evaluate"
    else:
        logger.info("Memory Retrieval: Cache miss. Proceeding to PLAN to select agent.")
        return "plan"


def route_after_evaluate(state: AxiomState) -> str:
    """
    Route after EVALUATE node.

    Determines whether sufficient evidence has been collected to proceed to SYNTHESIZE,
    or if additional evidence gathering is needed via PLAN (loop back to REASON first).
    Enforces a safety cap on iteration count to prevent infinite loops.

    Args:
        state: Current AXIOM state with evaluation results.

    Returns:
        Next node name: "synthesize", "cross_handoff", "plan", or master-prefixed variant.

    Logic:
        - If evidence_sufficiency="SUFFICIENT":
            - If cross_handoff_needed and not cross_handoff_done, route to "cross_handoff"
            - Otherwise, route to "synthesize"
        - If evaluation_iteration_count >= 5 (safety cap), route to "synthesize"
        - Otherwise, route back to "plan" to gather more evidence
    """
    evidence_sufficiency = state.get("evidence_sufficiency", "INSUFFICIENT")
    iteration_count = state.get("evaluation_iteration_count", 0)
    cross_handoff_needed = state.get("cross_handoff_needed", False)
    cross_handoff_done = state.get("cross_handoff_done", False)

    if evidence_sufficiency == "SUFFICIENT":
        if cross_handoff_needed and not cross_handoff_done:
            logger.info("Evaluate: Evidence sufficient. Cross-handoff needed. Routing to cross_handoff.")
            return "cross_handoff"
        else:
            logger.info("Evaluate: Evidence sufficient. Routing to synthesize.")
            return "synthesize"

    if iteration_count >= 5:
        logger.warning(
            "Evaluate: Iteration cap reached (count=%d). Routing to synthesize despite insufficient evidence.",
            iteration_count
        )
        return "synthesize"

    logger.info(
        "Evaluate: Evidence insufficient (iteration %d). Looping back to plan.",
        iteration_count
    )
    return "plan"


def route_after_synthesize(state: AxiomState) -> str:
    """
    Route after SYNTHESIZE node.

    Determines whether visual generation is needed based on response_mode.
    Routes to visual generation if images/diagrams are required, otherwise to human validation.

    Args:
        state: Current AXIOM state with synthesized summary.

    Returns:
        Next node name: "visual_gen" or "human_validate".

    Logic:
        - If response_mode in ("text_and_image", "image_only"), route to "visual_gen"
        - Otherwise, route to "human_validate"
    """
    response_mode = state.get("response_mode", "text_only")

    if response_mode in ("text_and_image", "image_only"):
        logger.info(
            "Synthesize: Response mode is '%s'. Routing to visual_gen.",
            response_mode
        )
        return "visual_gen"
    else:
        logger.info(
            "Synthesize: Response mode is '%s'. Routing to human_validate.",
            response_mode
        )
        return "human_validate"


def route_after_visual_gen(state: AxiomState) -> str:
    """
    Route after VISUAL_GEN node.

    Always routes to human validation after visual artifact generation.

    Args:
        state: Current AXIOM state (used for logging only).

    Returns:
        Always returns "human_validate".
    """
    logger.info("Visual Gen: Complete. Routing to human_validate.")
    return "human_validate"


def route_after_hitl(state: AxiomState) -> str:
    """
    Route after HUMAN_VALIDATE (HITL) node.

    Determines next action based on human feedback:
    - APPROVED: End the workflow
    - REJECTED: Return to REASON to restart with feedback appended
    - REQUEST_MORE: Gather additional evidence (loop back to PLAN)
    - Other: End the workflow

    Enforces safety cap on HITL iterations to prevent infinite loops.

    Args:
        state: Current AXIOM state with human validation result.

    Returns:
        Next node name: END, "reason", "plan", or another continuation point.

    Logic:
        - If result="APPROVED", return END
        - If result="REJECTED", return "reason" (restart from scratch)
        - If result="REQUEST_MORE":
            - If hitl_loop_count >= 2 (safety cap), return END
            - Otherwise, return "plan" (one more agent call)
        - Otherwise, return END
    """
    validation_result = state.get("human_validation_result", "APPROVED")
    hitl_loop_count = state.get("hitl_loop_count", 0)

    if validation_result == "APPROVED":
        logger.info("HITL: User approved. Ending workflow.")
        return END

    if validation_result == "REJECTED":
        logger.info("HITL: User rejected. Restarting from REASON with feedback appended.")
        return "reason"

    if validation_result == "REQUEST_MORE":
        if hitl_loop_count >= 2:
            logger.warning(
                "HITL: REQUEST_MORE hit iteration cap (count=%d). Ending workflow.",
                hitl_loop_count
            )
            return END
        else:
            logger.info(
                "HITL: REQUEST_MORE (iteration %d). Looping back to plan.",
                hitl_loop_count
            )
            return "plan"

    logger.warning(
        "HITL: Unknown validation result '%s'. Ending workflow.",
        validation_result
    )
    return END
