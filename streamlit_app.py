"""
AXIOM Streamlit Application.
Evidence-Driven Multi-Agent Intelligence Platform with interactive Human-in-the-Loop
(HITL) validation checkpoints and live BigQuery analytics.
Run with: streamlit run streamlit_app.py
"""

import os
import sys
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
import json
import uuid
import time
import logging
import collections

class StreamlitLogBuffer(logging.Handler):
    """In-memory circular log buffer to display live runtime logs in Streamlit UI."""
    def __init__(self, capacity=300):
        super().__init__()
        self.buffer = collections.deque(maxlen=capacity)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.buffer.append(msg)
        except Exception:
            pass

    def get_logs(self):
        return "\n".join(self.buffer)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    force=True
)
root_logger = logging.getLogger()
if not any(isinstance(h, StreamlitLogBuffer) for h in root_logger.handlers):
    _buf_handler = StreamlitLogBuffer()
    _buf_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"))
    root_logger.addHandler(_buf_handler)
    logging._axiom_buffer_handler = _buf_handler

logger = logging.getLogger("axiom.streamlit")

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

# Patch Pydantic v1 validator allow_reuse for LangChain/Vertex AI compatibility
for _mod_name in ("pydantic.v1.class_validators", "pydantic.class_validators"):
    try:
        import importlib
        _cv = importlib.import_module(_mod_name)
        if hasattr(_cv, "_prepare_validator"):
            _orig_prep = _cv._prepare_validator
            _cv._prepare_validator = lambda f, allow_reuse=False, _orig=_orig_prep: _orig(f, allow_reuse=True)
    except Exception:
        pass

# ════════════════════════════════════════════════════════════════════════════════
# CUSTOM STYLING (Dark Theme & ChatGPT/Copilot Input Dock)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .block-container {
        padding-bottom: 130px !important;
    }

    /* Hide chat input completely when Tab 1 (Project Risk Cockpit) is selected */
    .stApp:has(button[data-baseweb="tab"]:nth-child(1)[aria-selected="true"]) div[data-testid="stChatInput"],
    .stApp:has(button[data-baseweb="tab"]:nth-child(1)[aria-selected="true"]) div[data-testid="stBottom"] {
        display: none !important;
    }

    /* ChatGPT & Copilot Workspace Centered Dock Style */
    div[data-testid="stBottom"] {
        background: transparent !important;
        padding-bottom: 20px !important;
    }
    div[data-testid="stBottom"] > div {
        background: transparent !important;
    }
    div[data-testid="stChatInput"] {
        max-width: 860px !important;
        margin: 0 auto !important;
        padding: 0 !important;
    }
    div[data-testid="stChatInput"] > div {
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 26px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
        padding: 6px 14px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3), 0 12px 35px rgba(0, 0, 0, 0.6) !important;
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 0.96rem !important;
        color: #f8fafc !important;
        line-height: 1.5 !important;
        background: transparent !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #94a3b8 !important;
    }
    div[data-testid="stChatInput"] button {
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        background: #2563eb !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        transition: background 0.15s ease, transform 0.15s ease !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background: #1d4ed8 !important;
        transform: scale(1.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar (User Profile & Controls only)
with st.sidebar:
    render_user_menu(user_id)
    st.divider()
    st.markdown("### 🔧 AXIOM Controls")
    show_trace = st.checkbox("Show execution trace", value=False, key="axiom_show_trace")

    with st.expander("📜 Live Engine & System Logs", expanded=False):
        if hasattr(logging, "_axiom_buffer_handler"):
            logs_text = logging._axiom_buffer_handler.get_logs()
            st.code(logs_text if logs_text else "No logs recorded yet.", language="log")
            if st.button("🔄 Refresh Logs", key="refresh_logs_btn"):
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# CENTERED PAGE HEADER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
    <h1 style="font-size: 2.6rem; font-weight: 700; margin-bottom: 6px; letter-spacing: -0.5px;">
        ⬡ AXIOM Orchestrator
    </h1>
    <p style="font-size: 1.1rem; color: #94a3b8; margin: 0;">
        Google Cloud Evidence-Driven Multi-Agent System
    </p>
</div>
""", unsafe_allow_html=True)

def format_confidence_level(val: Any) -> str:
    """Format confidence score into qualitative level (High, Medium, Low)."""
    if isinstance(val, str):
        v = val.strip().capitalize()
        if v in ("High", "Medium", "Low"):
            return v
        try:
            val = float(val.replace("%", "").strip()) / (100.0 if "%" in val else 1.0)
        except Exception:
            return "Medium"
    if isinstance(val, (int, float)):
        if val >= 0.75:
            return "High"
        elif val >= 0.45:
            return "Medium"
        else:
            return "Low"
    return "Medium"


def render_mermaid_diagram(mermaid_code: str, caption: str = ""):
    """Renders a Mermaid diagram as an interactive graphical SVG visualization."""
    if not mermaid_code:
        return
    clean = mermaid_code.strip()
    if clean.startswith("```mermaid"):
        clean = clean[len("```mermaid"):].strip()
    if clean.startswith("```"):
        clean = clean[3:].strip()
    if clean.endswith("```"):
        clean = clean[:-3].strip()

    lines_count = len(clean.splitlines())
    calc_height = max(320, min(800, lines_count * 45 + 130))

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
      <style>
        body {{
          background-color: transparent;
          color: #f1f5f9;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          margin: 0;
          padding: 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }}
        .mermaid-container {{
          background: #0f172a;
          border: 1px solid #334155;
          border-radius: 10px;
          padding: 24px;
          width: 95%;
          max-width: 980px;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
          overflow-x: auto;
          display: flex;
          justify-content: center;
        }}
      </style>
    </head>
    <body>
      <div class="mermaid-container">
        <pre class="mermaid">
{clean}
        </pre>
      </div>
      <script>
        mermaid.initialize({{
          startOnLoad: true,
          theme: 'dark',
          securityLevel: 'loose',
          themeVariables: {{
            primaryColor: '#2563eb',
            primaryTextColor: '#f8fafc',
            primaryBorderColor: '#60a5fa',
            lineColor: '#93c5fd',
            secondaryColor: '#1e293b',
            tertiaryColor: '#0f172a'
          }}
        }});
      </script>
    </body>
    </html>
    """
    try:
        import streamlit.components.v1 as components
        components.html(html_content, height=calc_height, scrolling=True)
    except Exception:
        st.code(clean, language="mermaid")

    with st.expander("🔍 View Diagram Mermaid Source", expanded=False):
        st.code(clean, language="mermaid")



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
    # Initialize session state
    if "axiom_messages" not in st.session_state:
        st.session_state.axiom_messages = []
    if "pending_hitl_state" not in st.session_state:
        st.session_state.pending_hitl_state = None

    # Render persistent conversation stream
    for msg in st.session_state.axiom_messages:
        with st.chat_message(msg["role"]):
            if msg.get("meta") and msg["meta"].get("master"):
                conf_val = msg["meta"].get("confidence_level") or msg["meta"].get("confidence", 0)
                conf_str = format_confidence_level(conf_val)
                st.caption(f"🎯 **Master:** `{msg['meta']['master']}` | **Confidence:** `{conf_str}`")
            agents_list = msg.get("executed_agents") or ([msg["agent_task_input"]["executed_agent"]] if msg.get("agent_task_input") else [])
            if agents_list:
                agents_str = "  ".join(f"`🤖 {a}`" for a in agents_list)
                st.caption(f"**Specialist Agents Consulted:** {agents_str}")
            if msg.get("agent_executions"):
                with st.expander(f"🧭 Multi-Agent Delegation Journey ({len(msg['agent_executions'])} delegations)", expanded=False):
                    for step in msg["agent_executions"]:
                        ev_types = ", ".join(step.get("evidence_types", [])) or "None"
                        st.markdown(
                            f"**Iteration {step.get('iteration', 1)}: `{step.get('agent_id')}`** | Skill: `{step.get('skill')}`\n\n"
                            f"> *{step.get('summary')}*\n\n"
                            f"📦 **Evidence Fetched ({step.get('evidences_count', 0)}):** `{ev_types}`"
                        )
            st.markdown(msg["content"])
            if msg.get("visual") and msg["visual"].get("requires_visual"):
                vis = msg["visual"]
                st.info(f"🎨 **Visual ({vis.get('visual_type')}):** {vis.get('structured_caption', '')}")
                if vis.get("image_url"):
                    try:
                        st.image(vis["image_url"], caption=vis.get("structured_caption", "Analysis Visual"), width="stretch")
                    except Exception:
                        st.image(vis["image_url"], caption=vis.get("structured_caption", "Analysis Visual"))
                elif vis.get("fallback_mermaid"):
                    render_mermaid_diagram(vis["fallback_mermaid"], caption=vis.get("structured_caption", "Analysis Visual"))
            if msg.get("evidences"):
                with st.expander(f"📋 Verified Evidence ({len(msg['evidences'])})", expanded=False):
                    for env in msg["evidences"]:
                        payload = env.get("payload", {})
                        title = payload.get("Title") or payload.get("Summary") or env.get("artifact_id")
                        st.markdown(f"**[{env.get('artifact_id')}]** `{env.get('artifact_type')}` — *{title}*")
                        if payload.get("URL"):
                            st.markdown(f"🔗 **Repository URL:** [{payload.get('URL')}]({payload.get('URL')})")
                        if payload.get("PR_URL"):
                            st.markdown(f"🔀 **Pull Request:** [#{payload.get('PR_Number')}: {payload.get('PR_URL')}]({payload.get('PR_URL')}) (Branch: `{payload.get('Branch')}`)")
                        if payload.get("Linked_Requirements"):
                            st.markdown(f"📌 **Linked Requirements:** `{', '.join(payload.get('Linked_Requirements'))}`")
                        if payload.get("Linked_Test_Cases"):
                            st.markdown(f"🧪 **Linked Test Cases:** `{', '.join(payload.get('Linked_Test_Cases'))}`")
                        if payload.get("Patch_Diff"):
                            with st.expander("📝 Unified Patch Diff", expanded=False):
                                st.code(payload.get("Patch_Diff"), language="diff")
                        st.json(env)

    # ════════════════════════════════════════════════════════════════════════════
    # HITL CHECKPOINT (if pending)
    # ════════════════════════════════════════════════════════════════════════════
    if st.session_state.pending_hitl_state is not None:
        state = st.session_state.pending_hitl_state
        # st.subheader("🔍 Human-in-Loop (HITL) Validation Checkpoint")
        conf_val = state.get("confidence_level") or state.get("confidence_score", 0)
        conf_str = format_confidence_level(conf_val)
        # st.caption(f"Master: `{state.get('target_master')}` | Capability: `{state.get('target_capability')}` | Confidence: `{conf_str}`")

        agents_list = state.get("executed_agents") or ([state["agent_task_input"]["executed_agent"]] if state.get("agent_task_input") else [])
        # if agents_list:
            # st.info(f"🤖 **Specialist Agents Consulted ({len(agents_list)})**: {'  |  '.join([f'`{a}`' for a in agents_list])}")

        # if state.get("agent_executions"):
        #     with st.expander(f"🧭 Multi-Agent Delegation Journey ({len(state['agent_executions'])} delegations)", expanded=True):
        #         for step in state["agent_executions"]:
        #             ev_types = ", ".join(step.get("evidence_types", [])) or "None"
        #             st.markdown(
        #                 f"**Iteration {step.get('iteration', 1)}: `{step.get('agent_id')}`** — Skill: `{step.get('skill')}`\n\n"
        #                 f"> *{step.get('summary')}*\n\n"
        #                 f"📦 **Evidences Gathered ({step.get('evidences_count', 0)}):** `{ev_types}`"
        #             )
        # elif state.get("agent_task_input"):
        #     ag = state["agent_task_input"]
        #     st.info(f"🤖 **Specialist Agent Executed**: `{ag.get('executed_agent')}` | Skill: `{ag.get('skill')}`\n\n*{ag.get('summary')}*")

        metrics = state.get("llm_metrics", {})
        if metrics.get("model"):
            st.info(
                f"🧠 **Live LLM Telemetry**: `{metrics.get('provider')}` | Model: `{metrics.get('model')}` | "
                f"Latency: `{metrics.get('latency_s')}s` | Status: `{metrics.get('status')}`"
            )

        if state.get("llm_error"):
            st.error(f"⚠️ **Live LLM Error Details**: `{state.get('llm_error')}`")

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
                    "agent_task_input": state.get("agent_task_input"),
                    "executed_agents": state.get("executed_agents", []),
                    "agent_executions": state.get("agent_executions", []),
                    "meta": {
                        "status": "approved",
                        "master": state.get("target_master"),
                        "confidence": state.get("confidence_score", 0),
                        "confidence_level": format_confidence_level(state.get("confidence_level") or state.get("confidence_score", 0))
                    }
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
            print(f"\n{'='*70}\n[AXIOM STREAMLIT] Query Received: '{prompt}'", flush=True)
            t0 = time.time()
            try:
                res = run_axiom_orchestration(
                    query=prompt,
                    session_id=session_id,
                    user_id=user_id
                )
                elapsed = time.time() - t0
                print(f"[AXIOM STREAMLIT] Orchestration Completed in {elapsed:.2f}s | Master: {res.get('target_master')} | Capability: {res.get('target_capability')}\n{'='*70}", flush=True)

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
                            st.info(f"🎨 Visual: {visual.get('visual_type')} | Status: {visual.get('generation_status', 'UNKNOWN')}")

                            # Show generated image if available
                            if visual.get("image_url"):
                                try:
                                    st.image(visual["image_url"], caption=visual.get("structured_caption", "Generated Analysis"), width="stretch")
                                except Exception:
                                    st.image(visual["image_url"], caption=visual.get("structured_caption", "Generated Analysis"))
                            # Show Mermaid visual diagram
                            elif visual.get("fallback_mermaid"):
                                render_mermaid_diagram(visual["fallback_mermaid"], caption=visual.get("structured_caption", "Generated Analysis"))

                        # Show metadata
                        master = res.get("target_master", "AXIOM")
                        conf_val = res.get("confidence_level") or res.get("confidence_score", 0)
                        conf_str = format_confidence_level(conf_val)
                        st.markdown(
                            f"<small style='color:#888;'>Master: **{master}** | Confidence: **{conf_str}**</small>",
                            unsafe_allow_html=True
                        )

                    # Show trace if enabled
                    if show_trace:
                        with st.expander("🔍 Live Orchestration & LLM Telemetry Trace", expanded=True):
                            metrics = res.get("llm_metrics", {})
                            st.markdown(f"**LLM Engine**: `{metrics.get('provider', 'Google Gemini API')}`")
                            st.markdown(f"**Model**: `{metrics.get('model', 'gemini-flash-lite-latest')}`")
                            st.markdown(f"**Synthesis Latency**: `{metrics.get('latency_s', 0)}s`")
                            st.markdown(f"**Reasoning Hypothesis**: *{res.get('reasoning_hypothesis', 'N/A')}*")
                            st.markdown(f"**Evidence Sufficiency**: `{res.get('evidence_sufficiency', 'SUFFICIENT')}`")
                            if res.get("evidence_envelopes"):
                                st.markdown(f"**Verified Evidence Envelopes ({len(res.get('evidence_envelopes', []))}):**")
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
                        "agent_task_input": res.get("agent_task_input"),
                        "executed_agents": res.get("executed_agents", []),
                        "agent_executions": res.get("agent_executions", []),
                        "meta": {
                            "master": res.get("target_master"),
                            "confidence": res.get("confidence_score", 0),
                            "confidence_level": format_confidence_level(res.get("confidence_level") or res.get("confidence_score", 0))
                        }
                    })
