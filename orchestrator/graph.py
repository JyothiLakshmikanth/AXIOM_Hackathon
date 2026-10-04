"""
AXIOM End-to-End Master StateGraph Orchestration.
Integrates Intent Router, PM.ai Master, ENG.ai Master, and Pure-Python Visual Generation Node.
Supports both formal LangGraph compiled graph and native standalone cognitive runner.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from orchestrator.state import AxiomState
from orchestrator.router import router_node
from orchestrator.visual_gen import visual_generation_node
from orchestrator.pm_master import (
    pm_reason_node,
    pm_memory_retrieval_node,
    pm_plan_select_skill_node,
    pm_validate_node,
    pm_execute_agent_node,
    pm_observe_evidence_node,
    pm_evaluate_node,
    pm_synthesize_node,
    pm_answer_node
)
from orchestrator.eng_master import (
    eng_reason_node,
    eng_memory_retrieval_node,
    eng_plan_select_skill_node,
    eng_validate_node,
    eng_execute_agent_node,
    eng_observe_evidence_node,
    eng_evaluate_node,
    eng_synthesize_node,
    eng_answer_node
)

logger = logging.getLogger("axiom.orchestrator.graph")


def build_axiom_langgraph():
    """
    Constructs the canonical LangGraph StateGraph when langgraph is available.
    """
    try:
        from langgraph.graph import StateGraph, END

        builder = StateGraph(AxiomState)

        # 1. Register Router
        builder.add_node("router", router_node)

        # 2. Register PM.ai Master Nodes
        builder.add_node("pm_reason", pm_reason_node)
        builder.add_node("pm_memory_retrieval", pm_memory_retrieval_node)
        builder.add_node("pm_plan", pm_plan_select_skill_node)
        builder.add_node("pm_validate", pm_validate_node)
        builder.add_node("pm_execute_agent", pm_execute_agent_node)
        builder.add_node("pm_observe", pm_observe_evidence_node)
        builder.add_node("pm_evaluate", pm_evaluate_node)
        builder.add_node("pm_synthesize", pm_synthesize_node)
        builder.add_node("pm_visual_gen", visual_generation_node)
        builder.add_node("pm_answer", pm_answer_node)

        # 3. Register ENG.ai Master Nodes
        builder.add_node("eng_reason", eng_reason_node)
        builder.add_node("eng_memory_retrieval", eng_memory_retrieval_node)
        builder.add_node("eng_plan", eng_plan_select_skill_node)
        builder.add_node("eng_validate", eng_validate_node)
        builder.add_node("eng_execute_agent", eng_execute_agent_node)
        builder.add_node("eng_observe", eng_observe_evidence_node)
        builder.add_node("eng_evaluate", eng_evaluate_node)
        builder.add_node("eng_synthesize", eng_synthesize_node)
        builder.add_node("eng_visual_gen", visual_generation_node)
        builder.add_node("eng_answer", eng_answer_node)

        # Entry Point
        builder.set_entry_point("router")

        # Routing Conditional Edges
        def route_after_intent(state: AxiomState):
            if state.get("clarification", {}).get("clarification_needed", False):
                return END
            master = state.get("target_master", "PM.ai")
            return "pm_reason" if master == "PM.ai" else "eng_reason"

        builder.add_conditional_edges("router", route_after_intent)

        # PM.ai Cognitive Loop Edges
        builder.add_edge("pm_reason", "pm_memory_retrieval")

        def route_after_pm_memory(state: AxiomState):
            # If evidence found in memory, skip specialized agents and go straight to evaluate
            return "pm_evaluate" if state.get("memory_hit", False) else "pm_plan"

        builder.add_conditional_edges("pm_memory_retrieval", route_after_pm_memory)
        builder.add_edge("pm_plan", "pm_validate")
        builder.add_edge("pm_validate", "pm_execute_agent")
        builder.add_edge("pm_execute_agent", "pm_observe")
        builder.add_edge("pm_observe", "pm_evaluate")

        def route_after_pm_evaluate(state: AxiomState):
            # If not enough evidence and under 2 iterations, loop back to REASON
            if not state.get("evaluation_passed", True) and state.get("evaluation_iteration_count", 0) < 2:
                return "pm_reason"
            return "pm_synthesize"

        builder.add_conditional_edges("pm_evaluate", route_after_pm_evaluate)
        builder.add_edge("pm_synthesize", "pm_visual_gen")
        builder.add_edge("pm_visual_gen", "pm_answer")
        builder.add_edge("pm_answer", END)

        # ENG.ai Cognitive Loop Edges
        builder.add_edge("eng_reason", "eng_memory_retrieval")

        def route_after_eng_memory(state: AxiomState):
            return "eng_evaluate" if state.get("memory_hit", False) else "eng_plan"

        builder.add_conditional_edges("eng_memory_retrieval", route_after_eng_memory)
        builder.add_edge("eng_plan", "eng_validate")
        builder.add_edge("eng_validate", "eng_execute_agent")
        builder.add_edge("eng_execute_agent", "eng_observe")
        builder.add_edge("eng_observe", "eng_evaluate")

        def route_after_eng_evaluate(state: AxiomState):
            if not state.get("evaluation_passed", True) and state.get("evaluation_iteration_count", 0) < 2:
                return "eng_reason"
            return "eng_synthesize"

        builder.add_conditional_edges("eng_evaluate", route_after_eng_evaluate)
        builder.add_edge("eng_synthesize", "eng_visual_gen")
        builder.add_edge("eng_visual_gen", "eng_answer")
        builder.add_edge("eng_answer", END)

        return builder.compile()
    except ImportError:
        logger.debug("langgraph package not installed; using native AxiomCognitiveRunner.")
        return None


class AxiomCognitiveRunner:
    """
    High-performance native Cognitive Runner executing the exact StateGraph transitions.
    Guarantees immediate zero-dependency execution.
    """

    def run(self, query: str, session_id: str = "demo_session", user_id: str = "demo_user") -> AxiomState:
        state: AxiomState = {
            "query": query,
            "session_id": session_id,
            "user_id": user_id,
            "evidence_envelopes": [],
            "evaluation_iteration_count": 0,
            "guardrail_messages": []
        }

        # Step 1: Top-level Router Node
        state = router_node(state)
        if state.get("clarification", {}).get("clarification_needed", False):
            logger.info("Router returned clarification_needed=True. Ending run cleanly.")
            return state

        master = state.get("target_master", "PM.ai")

        if master == "PM.ai":
            # PM.ai Master Cognitive Graph
            while True:
                state = pm_reason_node(state)
                state = pm_memory_retrieval_node(state)

                if state.get("memory_hit", False):
                    state = pm_evaluate_node(state)
                else:
                    state = pm_plan_select_skill_node(state)
                    state = pm_validate_node(state)
                    state = pm_execute_agent_node(state)
                    state = pm_observe_evidence_node(state)
                    state = pm_evaluate_node(state)

                # Check loop condition
                if not state.get("evaluation_passed", True) and state.get("evaluation_iteration_count", 0) < 2:
                    logger.info("PM.ai: Evidence insufficient, looping back to REASON...")
                    continue
                break

            state = pm_synthesize_node(state)
            state = visual_generation_node(state)
            state = pm_answer_node(state)

        elif master == "ENG.ai":
            # ENG.ai Master Cognitive Graph
            while True:
                state = eng_reason_node(state)
                state = eng_memory_retrieval_node(state)

                if state.get("memory_hit", False):
                    state = eng_evaluate_node(state)
                else:
                    state = eng_plan_select_skill_node(state)
                    state = eng_validate_node(state)
                    state = eng_execute_agent_node(state)
                    state = eng_observe_evidence_node(state)
                    state = eng_evaluate_node(state)

                if not state.get("evaluation_passed", True) and state.get("evaluation_iteration_count", 0) < 2:
                    logger.info("ENG.ai: Evidence insufficient, looping back to REASON...")
                    continue
                break

            state = eng_synthesize_node(state)
            state = visual_generation_node(state)
            state = eng_answer_node(state)

        return state


# Export runner
axiom_runner = AxiomCognitiveRunner()


def run_axiom_orchestration(query: str, session_id: str = "default-session", user_id: str = "default-user") -> Dict[str, Any]:
    """Top-level convenience runner for AXIOM orchestration."""
    return axiom_runner.run(query=query, session_id=session_id, user_id=user_id)

