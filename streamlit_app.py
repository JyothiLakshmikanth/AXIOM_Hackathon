"""
AXIOM Streamlit Application.
Evidence-Driven Multi-Agent Intelligence Platform with interactive Human-in-the-Loop
(HITL) validation checkpoints and live BigQuery analytics.
Run with: streamlit run streamlit_app.py
"""

import os
import sys
import pandas as pd
import streamlit as st
import json
import uuid
import time

# Configure page - Theme is set in .streamlit/config.toml (Dark mode enforced)
st.set_page_config(
    page_title="AXIOM | Multi-Agent Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from orchestrator.graph import run_axiom_orchestration, axiom_runner
from streamlit_components.auth_panel import render_login_page, render_user_menu
from agents.tools.auth_tools import firestore_log_audit_entry

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION CHECK
# ─────────────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login_page()
    st.stop()

# User is authenticated
user_id = st.session_state.user_id
session_id = st.session_state.session_id
from agents.tools.neo4j_tools import _DYNAMIC_KG
from agents.tools.bigquery_tools import (
    bigquery_get_sprint_tasks,
    bigquery_get_team_capacity,
    bigquery_get_competency_matrix,
    bigquery_get_pi_planning,
    bigquery_get_test_run_results,
    bigquery_list_all_defects,
)
from streamlit_components.hitl_renderer import render_hitl_checkpoint, format_structured_answer
from agents.risk_board.risk_management_page import render_risk_management_page

# Theme configuration is handled by .streamlit/config.toml (Dark mode enforced)

# Sidebar
with st.sidebar:
    st.title("⬡ AXIOM Orchestrator")
    st.caption("Google Cloud Evidence-Driven Multi-Agent System")

    # User menu
    render_user_menu(user_id)

    st.divider()

    # Sidebar controls
    st.markdown("### 🔧 AXIOM Controls")
    show_trace = st.checkbox("Show execution trace", value=False, key="axiom_show_trace")

# Main Platform Tabs
tab_cockpit, tab_chat = st.tabs([
    "🎯 Project Risk Cockpit",
    "🧠 Multi-Agent Orchestrator"
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: Project Risk Cockpit
# ──────────────────────────────────────────────────────────────────────────────
with tab_cockpit:
    render_risk_management_page()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: Multi-Agent Orchestrator & HITL
# ──────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.title("🧠 AXIOM Multi-Agent Orchestrator")
   # st.write("Unified 9-Node StateGraph with intelligent master selection and Human-in-the-Loop validation.")

    # Initialize session state
    if "axiom_messages" not in st.session_state:
        st.session_state.axiom_messages = []
    if "pending_hitl_state" not in st.session_state:
        st.session_state.pending_hitl_state = None

    # Quick prompt buttons
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     if st.button("🛡️ AXIOM-PM Defect Triage"):
    #         st.session_state.temp_prompt = "What is the blast radius and defect triage for GH-ISSUE-107?"
    # with col2:
    #     if st.button("⚡ AXIOM-ENG Code RCA"):
    #         st.session_state.temp_prompt = "Perform deep code RCA for proximity_controller.py"
    # with col3:
    #     if st.button("📊 Sprint Capacity"):
    #         st.session_state.temp_prompt = "Analyze team capacity bottlenecks for SPR-03"

    # ════════════════════════════════════════════════════════════════════════════
    # HITL CHECKPOINT (if pending)
    # ════════════════════════════════════════════════════════════════════════════
    if st.session_state.pending_hitl_state is not None:
        state = st.session_state.pending_hitl_state
        st.subheader("🔍 Human-in-Loop (HITL) Validation Checkpoint")
        st.caption(f"Master: {state.get('target_master')} | Capability: {state.get('target_capability')}")

        decision = render_hitl_checkpoint(state)

        if decision is not None:
            result = decision.get("human_validation_result")
            feedback = decision.get("human_feedback", "")

            if result == "APPROVED":
                st.success("✅ Approved by Human Validator!")
                final_md = state.get("final_output_markdown") or format_structured_answer(state.get("structured_answer", {}))
                st.session_state.axiom_messages.append({
                    "role": "assistant",
                    "content": f"**[Approved by Human Reviewer]**\n\n{final_md}",
                    "visual": state.get("visual_artifact"),
                    "evidences": state.get("evidence_envelopes", []),
                    "meta": {"status": "approved"}
                })
                st.session_state.pending_hitl_state = None
                st.rerun()

            elif result == "REQUEST_MORE":
                st.info(f"🔄 Refinement Requested: '{feedback}'")
                state["human_validation_result"] = "REQUEST_MORE"
                state["human_feedback"] = feedback
                state["hitl_loop_count"] = state.get("hitl_loop_count", 0) + 1
                updated_state = axiom_runner._run_unified_master_loop(state)
                st.session_state.pending_hitl_state = updated_state
                st.rerun()

            elif result == "REJECTED":
                st.warning(f"❌ Analysis Rejected: '{feedback}'")
                state["human_validation_result"] = "REJECTED"
                state["human_feedback"] = feedback
                updated_state = axiom_runner._run_unified_master_loop(state)
                st.session_state.pending_hitl_state = updated_state
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════════
    # USER INPUT BAR (at bottom, after history/HITL)
    # ════════════════════════════════════════════════════════════════════════════
    prompt = st.chat_input("Ask AXIOM a question...", key="axiom_chat_input")

    # Handle temp_prompt from quick buttons
    if hasattr(st.session_state, "temp_prompt") and st.session_state.temp_prompt:
        prompt = st.session_state.temp_prompt
        st.session_state.temp_prompt = None

    if prompt:
        # 1️⃣ APPEND USER MESSAGE TO SESSION STATE
        st.session_state.axiom_messages.append({"role": "user", "content": prompt})

        # 2️⃣ DISPLAY USER MESSAGE
        with st.chat_message("user"):
            st.markdown(prompt)

        # 3️⃣ CALL MASTER ORCHESTRATION
        with st.spinner("AXIOM masters reasoning through 9-node cognitive loop..."):
            t0 = time.time()
            try:
                res = run_axiom_orchestration(
                    query=prompt,
                    session_id=session_id,
                    user_id=user_id
                )
                elapsed = time.time() - t0

                # Log audit
                firestore_log_audit_entry(
                    user_id,
                    session_id,
                    "query_submitted",
                    {
                        "query_length": len(prompt),
                        "master": res.get("target_master"),
                        "confidence": res.get("confidence_score", 0),
                        "elapsed_s": elapsed,
                        "status": "success"
                    }
                )

            except Exception as e:
                res = {"error": str(e)}
                st.error(f"Error: {e}")

        # 4️⃣ RENDER RESPONSE (structured like agent_pjm_page.py)
        if res.get("error"):
            with st.chat_message("assistant"):
                st.error(f"**Error:** {res.get('error')}")
                st.session_state.axiom_messages.append({
                    "role": "assistant",
                    "content": f"Error: {res.get('error')}"
                })
        else:
            # Check for clarification needed
            clarification = res.get("clarification", {})
            if clarification.get("clarification_needed"):
                with st.chat_message("assistant"):
                    st.warning(f"**Intent Clarification Needed:** {clarification.get('ambiguity_reason')}")
                    st.write("Please clarify:")
                    for q in clarification.get("clarification_questions", []):
                        st.write(f"- {q}")

                st.session_state.axiom_messages.append({
                    "role": "assistant",
                    "content": clarification.get("ambiguity_reason")
                })
            else:
                # Check if HITL required
                if res.get("human_validation_required", True):
                    st.session_state.pending_hitl_state = res
                    st.rerun()
                else:
                    # 5️⃣ RENDER FINAL RESPONSE (structured format)
                    output_md = res.get("final_output_markdown", "No output generated.")

                    with st.chat_message("assistant"):
                        st.markdown(output_md)

                        # Show visual artifacts
                        visual = res.get("visual_artifact", {})
                        if visual.get("requires_visual"):
                            st.info(f"🎨 Visual: {visual.get('visual_type')}")
                            if visual.get("fallback_mermaid"):
                                st.code(visual["fallback_mermaid"], language="mermaid")

                        # Show metadata
                        master = res.get("target_master", "AXIOM")
                        confidence = res.get("confidence_score", 0)
                        st.markdown(
                            f"<small style='color:#888;'>Master: **{master}** | Confidence: **{confidence:.0%}**</small>",
                            unsafe_allow_html=True
                        )

                    # Show trace if enabled
                    if show_trace:
                        if res.get("evidence_envelopes"):
                            with st.expander("🔍 Evidence Collected"):
                                for env in res.get("evidence_envelopes", []):
                                    st.json({
                                        "artifact_id": env.get("artifact_id"),
                                        "type": env.get("artifact_type"),
                                        "source": env.get("source_system")
                                    })

                    # 6️⃣ PERSIST TO SESSION STATE
                    st.session_state.axiom_messages.append({
                        "role": "assistant",
                        "content": output_md,
                        "visual": res.get("visual_artifact"),
                        "evidences": res.get("evidence_envelopes", []),
                        "meta": {
                            "master": res.get("target_master"),
                            "confidence": res.get("confidence_score", 0)
                        }
                    })
