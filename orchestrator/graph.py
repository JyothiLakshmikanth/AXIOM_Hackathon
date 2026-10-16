"""
AXIOM 9-Node End-to-End Master StateGraph Orchestration.
Implements full 9-node LangGraph architecture with intelligent PLAN node, cross-handoff,
conditional visual generation, and human-in-loop validation checkpoint.

Nodes: REASON → PLAN → EXECUTE → OBSERVE → EVALUATE → CROSS_HANDOFF → SYNTHESIZE → VISUAL_GEN → HUMAN_VALIDATE
Supports both formal LangGraph compiled graph and native AxiomCognitiveRunner.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from orchestrator.state import AxiomState
from orchestrator.router import router_node
from orchestrator.master_nodes import (
    reason_node,
    memory_retrieval_node,
    plan_node,
    execute_agent_node,
    observe_evidence_node,
    evaluate_node
)
from orchestrator.advanced_nodes import (
    cross_handoff_node,
    synthesize_node,
    visual_gen_node,
    human_validate_node
)
from orchestrator.edge_routing import (
    route_after_intent_router,
    route_after_memory,
    route_after_evaluate,
    route_after_synthesize,
    route_after_visual_gen,
    route_after_hitl
)

# For AxiomCognitiveRunner (native 9-node runner)
# These are now unified nodes, not pm_/eng_ prefixed
from orchestrator.master_nodes import (
    reason_node as unified_reason_node,
    memory_retrieval_node as unified_memory_node,
    plan_node as unified_plan_node,
    execute_agent_node as unified_execute_node,
    observe_evidence_node as unified_observe_node,
    evaluate_node as unified_evaluate_node
)

logger = logging.getLogger("axiom.orchestrator.graph")


def build_axiom_langgraph():
    """
    Constructs the 9-node unified LangGraph StateGraph for AXIOM orchestration.

    Both PM.ai and ENG.ai use the SAME 9-node loop. Master-specific behavior is
    parameterized via state["target_master"] and loaded from registries.

    Architecture:
    START → ROUTER → [REASON → MEMORY → PLAN → EXECUTE → OBSERVE → EVALUATE]
      ↓ (loop if insufficient, max 5 iterations)
      → CROSS_HANDOFF (optional) → SYNTHESIZE → VISUAL_GEN (conditional)
      → HUMAN_VALIDATE (HITL) → END
    """
    try:
        from langgraph.graph import StateGraph, END

        builder = StateGraph(AxiomState)

        # ============================================================================
        # UNIFIED 9-NODE ARCHITECTURE (BOTH MASTERS SHARE THE SAME NODES)
        # Master-specific behavior via state["target_master"] parameter
        # ============================================================================

        # 1. TOP-LEVEL ROUTER NODE
        builder.add_node("router", router_node)
        builder.set_entry_point("router")
        builder.add_conditional_edges("router", route_after_intent_router)

        # 2-7. SHARED COGNITIVE LOOP (Both PM.ai and ENG.ai use same nodes)
        builder.add_node("reason", reason_node)
        builder.add_node("memory", memory_retrieval_node)
        builder.add_node("plan", plan_node)
        builder.add_node("execute", execute_agent_node)
        builder.add_node("observe", observe_evidence_node)
        builder.add_node("evaluate", evaluate_node)

        # 8-10. ADVANCED NODES (Shared)
        builder.add_node("cross_handoff", cross_handoff_node)
        builder.add_node("synthesize", synthesize_node)
        builder.add_node("visual_gen", visual_gen_node)
        builder.add_node("human_validate", human_validate_node)

        # ============================================================================
        # EDGES: UNIFIED FLOW FOR BOTH MASTERS
        # ============================================================================

        # REASON → MEMORY
        builder.add_edge("reason", "memory")

        # MEMORY: Hit → EVALUATE, Miss → PLAN
        builder.add_conditional_edges("memory", route_after_memory)

        # PLAN → EXECUTE → OBSERVE → EVALUATE (Core loop)
        builder.add_edge("plan", "execute")
        builder.add_edge("execute", "observe")
        builder.add_edge("observe", "evaluate")

        # EVALUATE: Loop back to PLAN if insufficient (max 5), else continue
        builder.add_conditional_edges("evaluate", route_after_evaluate)

        # CROSS_HANDOFF → SYNTHESIZE
        builder.add_edge("cross_handoff", "synthesize")

        # SYNTHESIZE → VISUAL_GEN (conditional based on response_mode)
        builder.add_conditional_edges("synthesize", route_after_synthesize)

        # VISUAL_GEN → HUMAN_VALIDATE
        builder.add_edge("visual_gen", "human_validate")

        # HUMAN_VALIDATE → END or loop (APPROVED/REJECTED/REQUEST_MORE)
        builder.add_conditional_edges("human_validate", route_after_hitl)

        logger.info("AXIOM 9-node unified LangGraph compiled. Both PM.ai and ENG.ai share nodes.")
        return builder.compile()

    except ImportError:
        logger.debug("langgraph not installed; using native AxiomCognitiveRunner instead.")
        return None


class AxiomCognitiveRunner:
    """
    High-performance native 9-node Cognitive Runner without LangGraph dependency.
    Executes the exact 9-node state transitions: REASON → PLAN → EXECUTE → OBSERVE → EVALUATE
    → CROSS_HANDOFF → SYNTHESIZE → VISUAL_GEN → HUMAN_VALIDATE

    Zero-dependency, immediate execution for standalone AXIOM deployments.
    """

    def run(self, query: str, session_id: str = "demo_session", user_id: str = "demo_user") -> AxiomState:
        """
        Execute full 9-node AXIOM orchestration without LangGraph.

        Returns: Final state with response ready for Streamlit/output layer.
        """
        state: AxiomState = {
            "query": query,
            "session_id": session_id,
            "user_id": user_id,
            "evidence_envelopes": [],
            "evaluation_iteration_count": 0,
            "hitl_loop_count": 0,
            "guardrail_messages": [],
            "material_gaps": []
        }

        logger.info(f"AxiomCognitiveRunner.run(query={query[:50]}..., session={session_id})")

        # ============================================================================
        # STEP 1: TOP-LEVEL ROUTER NODE
        # ============================================================================
        state = router_node(state)
        if state.get("clarification", {}).get("clarification_needed", False):
            logger.info("Router: Clarification needed. Ending gracefully.")
            return state

        master = state.get("target_master", "AXIOM-PM")
        logger.info(f"Router: Routing to {master}")

        # ============================================================================
        # STEP 2: UNIFIED MASTER COGNITIVE LOOP (9-NODE ARCHITECTURE)
        # Both PM.ai and ENG.ai use the same nodes, parameterized by target_master
        # ============================================================================
        state = self._run_unified_master_loop(state)

        logger.info(f"AxiomCognitiveRunner: Execution complete. Response mode: {state.get('response_mode', 'text_only')}")
        return state

    def _run_unified_master_loop(self, state: AxiomState) -> AxiomState:
        """
        Execute unified 9-node cognitive loop for both PM.ai and ENG.ai.
        Master-specific behavior is parameterized via state["target_master"].

        Nodes used:
        1. REASON (master-specific via target_master parameter)
        2. MEMORY (shared cache lookup)
        3. PLAN (intelligent agent selection via LLM)
        4. EXECUTE (agent delegation)
        5. OBSERVE (evidence ingestion)
        6. EVALUATE (sufficiency check)
        7. CROSS_HANDOFF (optional master-to-master)
        8. SYNTHESIZE (LLM synthesis)
        9. VISUAL_GEN (conditional image generation)
        10. HUMAN_VALIDATE (HITL checkpoint)
        """
        master = state.get("target_master", "AXIOM-PM")
        logger.info(f"=== {master} UNIFIED COGNITIVE LOOP START ===")

        # EVIDENCE COLLECTION LOOP (REASON → PLAN → EXECUTE → OBSERVE → EVALUATE)
        while True:
            # NODE 1: REASON (classifies intent, sets required_evidence_dimensions based on master)
            state = reason_node(state)
            state["current_step"] = "REASON"
            logger.info(f"{master}: REASON complete. Required evidence: {state.get('required_evidence_dimensions', [])}")

            # NODE 2: MEMORY RETRIEVAL (checks Firestore cache)
            state = memory_retrieval_node(state)
            if state.get("memory_hit"):
                logger.info(f"{master}: MEMORY cache hit. Skipping agent call.")
                state = evaluate_node(state)
            else:
                # NODE 3: PLAN (intelligent LLM-driven agent selection)
                state = plan_node(state)
                state["current_step"] = "PLAN"
                logger.info(f"{master}: PLAN selected agent: {state.get('delegated_agent')}")

                # NODE 4: EXECUTE (call selected specialized agent)
                state = execute_agent_node(state)
                state["current_step"] = "EXECUTE"
                logger.info(f"{master}: EXECUTE complete. Evidence collected: {len(state.get('evidence_envelopes', []))} envelopes")

                # NODE 5: OBSERVE (normalize and cache evidence)
                state = observe_evidence_node(state)
                state["current_step"] = "OBSERVE"

                # NODE 6: EVALUATE (check if evidence is sufficient)
                state = evaluate_node(state)
                state["current_step"] = "EVALUATE"
                logger.info(f"{master}: EVALUATE: sufficiency={state.get('evidence_sufficiency')}, iteration={state.get('evaluation_iteration_count')}")

            # Check loop condition: If insufficient evidence and under 5 iterations, loop back to PLAN
            if (state.get("evidence_sufficiency") != "SUFFICIENT" and
                state.get("evaluation_iteration_count", 0) < 5):
                logger.info(f"{master}: Evidence INSUFFICIENT. Gaps: {state.get('material_gaps', [])}. Looping back to PLAN (iteration {state.get('evaluation_iteration_count')})")
                continue
            break

        logger.info(f"{master}: Evidence collection complete. Sufficiency: {state.get('evidence_sufficiency')}")

        # NODE 7: CROSS_HANDOFF (Conditional: only if this master needs other master's expertise)
        if state.get("cross_handoff_needed"):
            state = cross_handoff_node(state)
            state["current_step"] = "CROSS_HANDOFF"
            logger.info(f"{master}: CROSS_HANDOFF completed. Response received from {state.get('target_master')}")

        # NODE 8: SYNTHESIZE (LLM consolidates all evidence into structured answer + determines response_mode)
        state = synthesize_node(state)
        state["current_step"] = "SYNTHESIZE"
        logger.info(f"{master}: SYNTHESIZE complete. Response mode: {state.get('response_mode')}")

        # NODE 9 (Conditional): VISUAL_GEN (Generate images if response_mode requires it)
        if state.get("response_mode") in ("text_and_image", "image_only"):
            state = visual_gen_node(state)
            state["current_step"] = "VISUAL_GEN"
            logger.info(f"{master}: VISUAL_GEN complete. Image generated.")
        else:
            logger.info(f"{master}: Skipping VISUAL_GEN (response_mode: {state.get('response_mode')})")

        # NODE 10: HUMAN_VALIDATE (HITL Checkpoint - interrupt for human review)
        state = human_validate_node(state)
        state["current_step"] = "HUMAN_VALIDATE"
        logger.info(f"{master}: HUMAN_VALIDATE checkpoint. Awaiting human decision...")

        # Handle HITL feedback (approve/reject/request more)
        result = state.get("human_validation_result", "APPROVED")
        if result == "REJECTED":
            logger.info(f"{master}: Human REJECTED response. Looping back to REASON with feedback.")
            return self._run_unified_master_loop(state)
        elif result == "REQUEST_MORE" and state.get("hitl_loop_count", 0) < 2:
            logger.info(f"{master}: Human REQUEST_MORE. Looping back to PLAN for another agent call.")
            state["hitl_loop_count"] = state.get("hitl_loop_count", 0) + 1
            return self._run_unified_master_loop(state)

        logger.info(f"=== {master} UNIFIED COGNITIVE LOOP END (result: {result}) ===")
        return state


# Export runner
axiom_runner = AxiomCognitiveRunner()


def run_axiom_orchestration(query: str, session_id: str = "default-session", user_id: str = "default-user") -> Dict[str, Any]:
    """Top-level convenience runner for AXIOM orchestration."""
    return axiom_runner.run(query=query, session_id=session_id, user_id=user_id)

