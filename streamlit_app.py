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

# Configure page
st.set_page_config(
    page_title="AXIOM | Multi-Agent Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

import uuid
from orchestrator.graph import run_axiom_orchestration, axiom_runner
from agents.tools.neo4j_tools import _DYNAMIC_KG
from agents.tools.bigquery_tools import (
    bigquery_get_sprint_tasks,
    bigquery_get_team_capacity,
    bigquery_get_competency_matrix,
    bigquery_get_pi_planning,
    bigquery_get_test_run_results,
    bigquery_list_all_defects,
    _load_csv,
)
from agents.resource_agent import _RES_TO_ASSOCIATE_MAP
from agents.risk_board import RiskAnalyzer
from agents.tools.firestore_tools import (
    firestore_save_user_feedback,
    firestore_get_positive_exemplars,
    firestore_get_all_feedback,
    firestore_get_feedback_stats,
    firestore_list_user_sessions,
    firestore_get_session_turns,
    firestore_save_session_turn,
    firestore_save_session_metadata
)
from streamlit_components.hitl_renderer import render_hitl_checkpoint, format_structured_answer

# Custom CSS for dark modern aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0a0d14;
        color: #f8fafc;
    }
    .metric-card {
        background: rgba(18, 25, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .hitl-container {
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        background: rgba(15, 23, 42, 0.6);
        margin-top: 15px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

def safe_dataframe(df, use_container_width=True):
    """Safely render dataframes with fallback if pyarrow has ABI/version constraints."""
    try:
        st.dataframe(df, use_container_width=use_container_width)
    except Exception:
        try:
            st.table(df)
        except Exception:
            st.write(df)

# User Profile & Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = "JyothiLakshmikanth"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{st.session_state.user_id}-01"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loaded_session_id" not in st.session_state:
    st.session_state.loaded_session_id = None
if "pending_hitl_state" not in st.session_state:
    st.session_state.pending_hitl_state = None

GITHUB_REPO_URL = "https://github.com/JyothiLakshmikanth/EKey2W"
GITHUB_REPO_NAME = "JyothiLakshmikanth/EKey2W"

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ──────────────────────────────────────────────────────────────────────────────

# Sidebar
with st.sidebar:
    st.title("⬡ AXIOM Orchestrator")
    st.caption("Google Cloud Evidence-Driven Multi-Agent System")
    st.markdown(f"🔗 **Repo:** [{GITHUB_REPO_NAME}]({GITHUB_REPO_URL})")

    # Associate Persona selector directly in sidebar (no login blockage)
    associate_profiles = [
        "JyothiLakshmikanth (Lead System Architect)",
        "bhavya2642-collab (Cloud & Mobile Platform Lead)",
        "manjunathan-j (Embedded Security Lead)",
        "Pavi2604 (Vehicle Software & QA Lead)",
    ]
    current_persona_idx = 0
    for idx, p in enumerate(associate_profiles):
        if st.session_state.user_id in p:
            current_persona_idx = idx
            break

    sel_persona = st.selectbox("👤 Active Persona:", associate_profiles, index=current_persona_idx)
    selected_uid = sel_persona.split(" (")[0]
    if selected_uid != st.session_state.user_id:
        st.session_state.user_id = selected_uid
        st.session_state.session_id = f"session-{selected_uid}-{uuid.uuid4().hex[:6]}"
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Session: `{st.session_state.session_id}`")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ New Session", use_container_width=True, help="Start a new session"):
            new_sid = f"session-{st.session_state.user_id}-{uuid.uuid4().hex[:6]}"
            firestore_save_session_metadata(st.session_state.user_id, new_sid, "New Conversation")
            st.session_state.session_id = new_sid
            st.session_state.messages = []
            st.session_state.loaded_session_id = new_sid
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear active conversation"):
            st.session_state.messages = []
            st.rerun()

    # Session dropdown
    past_sessions = firestore_list_user_sessions(st.session_state.user_id)
    if past_sessions:
        sids = [s["session_id"] for s in past_sessions]
        if st.session_state.session_id not in sids:
            sids.insert(0, st.session_state.session_id)
        current_idx = sids.index(st.session_state.session_id)
        chosen_sid = st.selectbox("📂 Switch Session:", sids, index=current_idx)
        if chosen_sid != st.session_state.session_id:
            st.session_state.session_id = chosen_sid
            turns = firestore_get_session_turns(chosen_sid)
            st.session_state.messages = []
            for t in turns:
                if t.get("role") == "user" or (t.get("query") and not t.get("content")):
                    st.session_state.messages.append({"role": "user", "content": t.get("query") or t.get("content", "")})
                if t.get("content") or t.get("summary"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": t.get("content") or t.get("summary", ""),
                        "visual": t.get("visual"),
                        "evidences": t.get("evidences", []),
                        "target_master": t.get("target_master", "AXIOM-PM")
                    })
            st.session_state.loaded_session_id = chosen_sid
            st.rerun()

    st.divider()

    st.subheader("Knowledge Foundation")
    st.write(f"**Neo4j KG Nodes:** {len(_DYNAMIC_KG.nodes)}")
    st.write(f"**Neo4j KG Edges:** {len(_DYNAMIC_KG.edges)}")

    direct_edges = sum(1 for e in _DYNAMIC_KG.edges if e.get("category") == "direct")
    semantic_edges = sum(1 for e in _DYNAMIC_KG.edges if e.get("category") == "semantic")
    st.write(f"• Direct Edges: `{direct_edges}`")
    st.write(f"• Semantic Edges: `{semantic_edges}`")

    st.divider()
    st.subheader("BigQuery Data Foundation")
    st.write("• **Dataset**: `axiom_data`")
    st.write("• `sprint_planning` (21 tasks/bugs/epics)")
    st.write("• `capacity_planning` (team allocations)")
    st.write("• `competency_matrix` (64 skills/levels)")
    st.write("• `pi_planning` (PI-1 to PI-4 milestones)")
    st.write("• `test_cases` (Master ISO 29119 store)")

    st.divider()
    st.subheader("9-Node StateGraph")
    st.caption("REASON → PLAN → EXECUTE → OBSERVE → EVALUATE → CROSS_HANDOFF → SYNTHESIZE → VISUAL_GEN → HUMAN_VALIDATE")

import json

# Main Platform Tabs
tab_cockpit, tab_chat, tab_bq, tab_kg, tab_envelopes = st.tabs([
    "🎯 Project Risk Cockpit",
    "🧠 Multi-Agent Orchestrator & HITL",
    "📊 BigQuery Data Hub (axiom_data)",
    "🕸️ Neo4j Knowledge Graph",
    "🛡️ Evidence Vault"
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: Project Risk Cockpit
# ──────────────────────────────────────────────────────────────────────────────
with tab_cockpit:
    st.title("🎯 Project Risk Cockpit")
    st.markdown("### 🚘 Project: **AXIOM E-Key 2W Digital Key Platform**")
    st.caption(f"Authoritative Multi-Agent Risk Intelligence &bull; Target Repository: [{GITHUB_REPO_NAME}]({GITHUB_REPO_URL}) &bull; Active Milestone: Alpha Safety Gate")

    # 1. Fetch live sprint planning, capacity planning, and PI planning data
    raw_capacity = bigquery_get_team_capacity() or []
    all_sprint_tasks = _load_csv("sprint_planning") or []
    raw_pi = bigquery_get_pi_planning() or _load_csv("pi_planning") or []

    # Helper function to resolve assignee
    def get_assignee_display(raw_id):
        if not raw_id or raw_id == "Unassigned":
            return "Unassigned"
        info = _RES_TO_ASSOCIATE_MAP.get(raw_id)
        if info:
            return f"{info['associate']} ({raw_id})"
        return raw_id

    # 2. Execute purely dynamic multi-source project risk analysis (Zero Hardcoding)
    risk_analyzer = RiskAnalyzer(
        jira_df=pd.DataFrame(all_sprint_tasks) if all_sprint_tasks else None,
        capacity_df=pd.DataFrame(raw_capacity) if raw_capacity else None,
        pi_df=pd.DataFrame(raw_pi) if raw_pi else None
    )
    temporal_data = risk_analyzer.analyze_temporal_risks()

    # Top Executive Metric Banner (100% Data-Driven)
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    has_critical_blocker = any(t.get('priority') == 'Critical' for t in temporal_data['today_risks'])
    with r_col1:
        st.metric(
            "Project Overall Health",
            "🔴 High Risk" if has_critical_blocker else "🟠 Medium-High",
            delta=f"{temporal_data['today_metrics']['critical_path_items']} Items In-Flight",
            delta_color="inverse"
        )
    with r_col2:
        st.metric(
            "⏪ Yesterday's Risks",
            f"{temporal_data['yesterday_metrics']['total_resolved']} Resolved",
            delta=f"{temporal_data['yesterday_metrics']['points_delivered']} Pts Delivered",
            delta_color="normal"
        )
    with r_col3:
        st.metric(
            "⚡ Today's Active Risks",
            f"{temporal_data['today_metrics']['active_defects_count']} In-Flight",
            delta=f"{temporal_data['today_metrics']['overloaded_engineers_count']} Bottlenecks",
            delta_color="inverse"
        )
    with r_col4:
        st.metric(
            "⏩ Tomorrow's Risks",
            f"{temporal_data['tomorrow_metrics']['horizon_risks_count']} Horizon",
            delta=temporal_data['tomorrow_metrics']['next_safety_gate'],
            delta_color="inverse"
        )

    st.markdown("---")

    # ──────────────────────────────────────────────────────────────────────────
    # 3 TEMPORAL RISK TABS: YESTERDAY, TODAY, TOMORROW (100% Dynamic)
    # ──────────────────────────────────────────────────────────────────────────
    risk_tab_yesterday, risk_tab_today, risk_tab_tomorrow = st.tabs([
        "⏪ Yesterday's Risks (Resolved & Historical Baseline)",
        "⚡ Today's Risks (Active Sprint 3 Critical Hotspots)",
        "⏩ Tomorrow's Risks (Upcoming Sprints & Horizon Risks)"
    ])

    # ==========================================================================
    # SUB-TAB 1: YESTERDAY'S RISKS (Dynamically derived from historical sprints)
    # ==========================================================================
    with risk_tab_yesterday:
        st.subheader("⏪ Historical Baseline & Yesterday's Mitigated Risks")
        st.caption("Technical blockers, defects, and environmental risks from historical sprints that have been successfully isolated, verified, and closed.")

        y_c1, y_c2, y_c3 = st.columns(3)
        y_c1.metric("Resolved Baseline Risks", f"{temporal_data['yesterday_metrics']['total_resolved']} Items", delta="100% Closed")
        y_c2.metric("Regression Rate", temporal_data['yesterday_metrics']['regression_rate'], delta="Safe")
        y_c3.metric("Delivered Velocity", f"{temporal_data['yesterday_metrics']['points_delivered']} Points ({temporal_data['yesterday_metrics']['hours_logged']}h)", delta="On Track")

        yesterday_rows = [
            {
                "Issue ID": r["id"],
                "Summary": r["title"],
                "Sprint": r["sprint"],
                "Assignee": r["assignee"],
                "Initial Threat": r["threat"],
                "Resolution Applied": r["resolution"],
                "Verification Status": r["status"]
            }
            for r in temporal_data["yesterday_risks"]
        ]
        safe_dataframe(pd.DataFrame(yesterday_rows), use_container_width=True)

        st.markdown("#### 🛡️ Historical Safeguards Established")
        for sg in temporal_data["yesterday_metrics"]["safeguards"]:
            st.markdown(f"- {sg}")

    # ==========================================================================
    # SUB-TAB 2: TODAY'S RISKS (Dynamically derived from active sprint items)
    # ==========================================================================
    with risk_tab_today:
        st.subheader("⚡ Today's Critical Hotspots & Active Delivery Risks (Sprint 3)")
        st.caption("Active delivery threats in current Sprint: Critical safety violations, open bugs, and engineer capacity overallocation (>85% safe ceiling).")

        # Layout: Critical Defect Radar & Resource Overload Watch
        c_left, c_right = st.columns([3, 2])

        with c_left:
            st.markdown("#### 🚨 Critical Defect Radar & Immediate Delivery Blockers")

            today_rows = [
                {
                    "ID": r["id"],
                    "Summary": r["title"],
                    "Type": r["type"],
                    "Priority": r["priority"],
                    "Status": r["status"],
                    "Assignee": r["assignee"],
                    "Sprint": r["sprint"],
                    "Impact": r["impact"],
                    "Mitigation": r["mitigation"]
                }
                for r in temporal_data["today_risks"]
            ]
            today_df = pd.DataFrame(today_rows)
            safe_dataframe(today_df, use_container_width=True)

            # Determine top critical item dynamically
            crit_bugs = [r for r in temporal_data["today_risks"] if r["priority"] == "Critical" and r["type"] in ["Bug", "Defect"]]
            top_crit_id = crit_bugs[0]["id"] if crit_bugs else (temporal_data["today_risks"][0]["id"] if temporal_data["today_risks"] else "TWK-107")

            st.caption("💡 Transfer high-priority defect triage directly into the multi-agent cognitive engine:")
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                if st.button(f"⚡ Dispatch {top_crit_id} Defect Triage & RCA", use_container_width=True):
                    st.session_state.temp_prompt = f"What is the defect triage, root cause, and blast radius for {top_crit_id}?"
                    st.info("Query queued! Switch to '🧠 Multi-Agent Orchestrator & HITL' tab to view execution.")
            with act_col2:
                if st.button("⚖️ Generate SPR-03 Capacity Rebalancing Plan", use_container_width=True):
                    st.session_state.temp_prompt = "Analyze team capacity bottlenecks and recommend rebalancing plan for SPR-03"
                    st.info("Query queued! Switch to '🧠 Multi-Agent Orchestrator & HITL' tab to view execution.")

        with c_right:
            st.markdown("#### 👥 Resource Bottlenecks Today (>85% Cap)")
            res_list = [
                {
                    "Associate": r["associate"],
                    "Role": r["role"],
                    "Domain": r["domain"],
                    "Allocation": f"{r['allocation']}%",
                    "Risk": r["status"]
                }
                for r in temporal_data["today_resource_overloads"]
            ]
            safe_dataframe(pd.DataFrame(res_list), use_container_width=True)

            # Cumulative workload callout (100% dynamically aggregated)
            st.caption("📊 **Cumulative Multi-Role Allocation Across Project**:")
            for name, alloc_summary in temporal_data["today_associate_aggregates"].items():
                st.markdown(f"- **{name}**: `{alloc_summary}`")

            st.markdown("#### 📅 Active Sprint Pulse (SPR-03)")
            st.warning(f"⚠️ **Sprint 3 Health**: {len(temporal_data['today_risks'])} items in-flight; {top_crit_id} threatens Alpha gate delivery unless active mitigations are completed.")

        st.markdown("---")
        st.subheader("🛡️ Immediate Mitigation Directives for Today")
        for m in temporal_data["today_mitigations"]:
            st.markdown(m)

    # ==========================================================================
    # SUB-TAB 3: TOMORROW'S RISKS (Dynamically derived from future sprints & PI)
    # ==========================================================================
    with risk_tab_tomorrow:
        st.subheader("⏩ Tomorrow's Risks: Horizon Vulnerabilities & Upcoming Milestones")
        st.caption("Anticipated architectural debt, emerging security windows, and PI milestone dependencies spanning future sprints and roadmaps.")

        tom_c1, tom_c2, tom_c3 = st.columns(3)
        tom_c1.metric("Emerging Horizon Risks", f"{temporal_data['tomorrow_metrics']['horizon_risks_count']} Tracked", delta="Requires Preemptive Governance")
        tom_c2.metric("Next Critical Safety Gate", temporal_data['tomorrow_metrics']['next_safety_gate'], delta=f"{temporal_data['tomorrow_metrics']['days_remaining']} Days Remaining")
        tom_c3.metric("Upcoming PI Focus", temporal_data['tomorrow_metrics']['upcoming_pi_focus'], delta="Security & QA Gate")

        tomorrow_rows = [
            {
                "Target Milestone": r["milestone"],
                "Work Item": r["id"],
                "Horizon Risk Title": r["title"],
                "Threat Mechanism": r["threat"],
                "Owner": r["owner"],
                "Preemptive Strategy": r["preemptive_strategy"]
            }
            for r in temporal_data["tomorrow_risks"]
        ]
        safe_dataframe(pd.DataFrame(tomorrow_rows), use_container_width=True)

        st.markdown("#### 🗺️ Program Increment Horizon Roadmap (PI-1 to PI-4)")
        safe_dataframe(pd.DataFrame(temporal_data["pi_roadmap"]), use_container_width=True)

    # ──────────────────────────────────────────────────────────────────────────
    # Interactive Sprint Tasks Explorer (TWK-101 to TWK-120)
    # ──────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Comprehensive Sprint Tasks & Delivery Tracker (TWK-101 — TWK-120)")
    st.caption("Full traceability across all 20 sprint backlog work items, assignees, priorities, and components from BigQuery `axiom_data.sprint_planning`.")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        sprint_filter = st.selectbox(
            "Filter by Sprint",
            options=["All Sprints"] + sorted(list(set(t.get("Sprint_ID") for t in all_sprint_tasks if t.get("Sprint_ID"))))
        )
    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All Statuses", "Open", "In Progress", "Done", "To Do"]
        )
    with filter_col3:
        type_filter = st.selectbox(
            "Filter by Work Item Type",
            options=["All Types", "Bug", "Story", "Task", "Risk", "Epic"]
        )

    # Filter tasks
    filtered_tasks = all_sprint_tasks
    if sprint_filter != "All Sprints":
        filtered_tasks = [t for t in filtered_tasks if t.get("Sprint_ID") == sprint_filter]
    if status_filter != "All Statuses":
        filtered_tasks = [t for t in filtered_tasks if t.get("Status") == status_filter]
    if type_filter != "All Types":
        filtered_tasks = [t for t in filtered_tasks if t.get("Type") == type_filter]

    task_table_data = []
    for t in filtered_tasks:
        task_table_data.append({
            "ID": t.get("Id"),
            "Type": t.get("Type"),
            "Summary": t.get("Summary"),
            "Sprint": t.get("Sprint_ID"),
            "Status": t.get("Status"),
            "Priority": t.get("Priority"),
            "Assignee": get_assignee_display(t.get("Owned_By")),
            "Points": t.get("Story_Points"),
            "Component": t.get("Components")
        })

    safe_dataframe(pd.DataFrame(task_table_data), use_container_width=True)

    st.markdown("---")
    st.subheader("🛡️ Executive Risk Mitigation Strategies")
    # Dynamically derived from active bottlenecks and horizon risks
    exec_mitigations = temporal_data["today_mitigations"][:3] + [
        f"**Preemptive Horizon Action for {r['id']} ({r['title']})**: {r['preemptive_strategy']}"
        for r in temporal_data["tomorrow_risks"][:3]
    ]
    for strat in exec_mitigations:
        st.markdown(strat)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: Multi-Agent Orchestrator & HITL
# ──────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.title("AXIOM Multi-Agent Cognitive Platform")
    st.write("Unified 9-Node StateGraph reasoning across AXIOM-PM and AXIOM-ENG masters with interactive Human-in-the-Loop validation.")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_hitl_state" not in st.session_state:
        st.session_state.pending_hitl_state = None

    # Quick prompt chips
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛡️ AXIOM-PM Defect Triage (GH-ISSUE-107)"):
            st.session_state.temp_prompt = "What is the blast radius and defect triage for GH-ISSUE-107?"
    with col2:
        if st.button("⚡ AXIOM-ENG Code RCA (proximity_controller.py)"):
            st.session_state.temp_prompt = "Perform deep code RCA and generate surgical patch for proximity_controller.py"
    with col3:
        if st.button("📊 Sprint 3 Capacity & Rebalancing (SPR-03)"):
            st.session_state.temp_prompt = "Analyze team capacity bottlenecks and recommend rebalancing plan for SPR-03"

    # Display chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("visual") and msg["visual"].get("requires_visual"):
                vis = msg["visual"]
                st.info(f"🎨 **Visual Synthesis ({vis.get('visual_type')}):** {vis.get('structured_caption', '')}")
                if vis.get("fallback_mermaid"):
                    st.code(vis["fallback_mermaid"], language="mermaid")
            if msg.get("evidences"):
                with st.expander(f"📋 Verified Evidence Envelopes ({len(msg['evidences'])})"):
                    for env in msg["evidences"]:
                        st.json(env)

            # Interactive Feedback Mechanism (Thumbs Up / Thumbs Down & Exemplar Learning)
            if msg.get("role") == "assistant" and msg.get("content"):
                fb_id = f"fb_{st.session_state.session_id}_{idx}"
                col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 7.6])
                with col_f1:
                    if st.button("👍 Helpful", key=f"up_{fb_id}", help="Save this response to learned exemplars for future queries"):
                        prior_q = ""
                        for p in reversed(st.session_state.messages[:idx]):
                            if p.get("role") == "user":
                                prior_q = p.get("content", "")
                                break
                        firestore_save_user_feedback(
                            user_id=st.session_state.user_id,
                            session_id=st.session_state.session_id,
                            query=prior_q or "User Query",
                            response=msg.get("content", ""),
                            rating="positive",
                            comment="User approved response format & technical accuracy",
                            master=msg.get("target_master", "AXIOM-PM")
                        )
                        st.session_state[fb_id] = "positive"
                        st.rerun()
                with col_f2:
                    if st.button("👎 Critique", key=f"down_{fb_id}", help="Flag response for refinement"):
                        prior_q = ""
                        for p in reversed(st.session_state.messages[:idx]):
                            if p.get("role") == "user":
                                prior_q = p.get("content", "")
                                break
                        firestore_save_user_feedback(
                            user_id=st.session_state.user_id,
                            session_id=st.session_state.session_id,
                            query=prior_q or "User Query",
                            response=msg.get("content", ""),
                            rating="negative",
                            comment="User flagged response for refinement",
                            master=msg.get("target_master", "AXIOM-PM")
                        )
                        st.session_state[fb_id] = "negative"
                        st.rerun()

                if st.session_state.get(fb_id) == "positive":
                    st.success("⭐ **Benchmark Learned**: Added to memory! Future syntheses will refer to this approved benchmark.")
                elif st.session_state.get(fb_id) == "negative":
                    st.info("📝 **Feedback Recorded**: Critique logged for continuous multi-agent cognitive improvement.")

    # ──────────────────────────────────────────────────────────────────────────
    # Check for Pending HITL Checkpoint
    # ──────────────────────────────────────────────────────────────────────────
    if st.session_state.pending_hitl_state is not None:
        state = st.session_state.pending_hitl_state
        st.markdown('<div class="hitl-container">', unsafe_allow_html=True)
        st.subheader("🔍 Human-in-Loop (HITL) Validation Checkpoint")
        st.caption(f"Master: **{state.get('target_master')}** | Capability: **{state.get('target_capability')}** | Step: **HUMAN_VALIDATE**")

        decision = render_hitl_checkpoint(state)

        if decision is not None:
            result = decision.get("human_validation_result")
            feedback = decision.get("human_feedback", "")

            if result == "APPROVED":
                st.success("✅ **Approved by Human Validator!** Delivering authoritative final response.")
                final_md = state.get("final_output_markdown") or format_structured_answer(state.get("structured_answer", {}))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**[Status: Verified & Approved by Human Reviewer]**\n\n{final_md}",
                    "visual": state.get("visual_artifact"),
                    "evidences": state.get("evidence_envelopes", []),
                    "target_master": state.get("target_master", "AXIOM-PM")
                })
                # Persist to Firestore memory
                try:
                    firestore_save_session_turn(
                        session_id=st.session_state.session_id,
                        turn_data={
                            "role": "assistant",
                            "content": final_md,
                            "target_master": state.get("target_master", "AXIOM-PM"),
                            "visual": state.get("visual_artifact"),
                            "evidences": state.get("evidence_envelopes", [])
                        },
                        user_id=st.session_state.user_id
                    )
                except Exception:
                    pass
                st.session_state.pending_hitl_state = None
                st.rerun()

            elif result == "REQUEST_MORE":
                st.info(f"🔄 **Refinement Requested**: '{feedback}'. Re-executing cognitive loop with human guidance...")
                # Re-run cognitive runner with feedback
                state["human_validation_result"] = "REQUEST_MORE"
                state["human_feedback"] = feedback
                state["hitl_loop_count"] = state.get("hitl_loop_count", 0) + 1
                updated_state = axiom_runner._run_unified_master_loop(state)
                st.session_state.pending_hitl_state = updated_state
                st.rerun()

            elif result == "REJECTED":
                st.warning(f"❌ **Analysis Rejected**: '{feedback}'. Looping back to REASON node with rejection feedback.")
                state["human_validation_result"] = "REJECTED"
                state["human_feedback"] = feedback
                updated_state = axiom_runner._run_unified_master_loop(state)
                st.session_state.pending_hitl_state = updated_state
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input box
    prompt = st.chat_input("Ask AXIOM a question...")
    if hasattr(st.session_state, "temp_prompt") and st.session_state.temp_prompt:
        prompt = st.session_state.temp_prompt
        st.session_state.temp_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            firestore_save_session_turn(
                session_id=st.session_state.session_id,
                turn_data={"role": "user", "query": prompt, "content": prompt},
                user_id=st.session_state.user_id
            )
        except Exception:
            pass

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AXIOM Masters reasoning through 9-node LangGraph cognitive loops..."):
            res = run_axiom_orchestration(
                query=prompt,
                session_id=st.session_state.session_id,
                user_id=st.session_state.user_id
            )

            # Check for clarification needed
            clarification = res.get("clarification", {})
            if clarification.get("clarification_needed"):
                with st.chat_message("assistant"):
                    st.warning(f"**Intent Clarification Needed:** {clarification.get('ambiguity_reason')}")
                    st.write("Please clarify:")
                    for q in clarification.get("clarification_questions", []):
                        st.write(f"- {q}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": res.get("final_output_markdown", "Clarification needed."),
                        "target_master": "AXIOM-ROUTER"
                    })
            else:
                # If human validation is required, pause at checkpoint
                if res.get("human_validation_required", True):
                    st.session_state.pending_hitl_state = res
                    st.rerun()
                else:
                    output_md = res.get("final_output_markdown", "No output generated.")
                    with st.chat_message("assistant"):
                        st.markdown(output_md)
                        visual = res.get("visual_artifact", {})
                        if visual.get("requires_visual"):
                            st.info(f"🎨 **Visual Synthesis ({visual.get('visual_type')}):** {visual.get('structured_caption')}")
                            if visual.get("fallback_mermaid"):
                                st.code(visual["fallback_mermaid"], language="mermaid")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": output_md,
                        "visual": res.get("visual_artifact"),
                        "evidences": res.get("evidence_envelopes", []),
                        "target_master": res.get("target_master", "AXIOM-PM")
                    })

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: BigQuery Data Hub (axiom_data)
# ──────────────────────────────────────────────────────────────────────────────
with tab_bq:
    st.header("📊 BigQuery Structured Project Data (`axiom_data`)")
    st.caption("Live querying of BigQuery tables with local CSV persistence fallback.")

    bq_table = st.selectbox(
        "Select BigQuery Table to Explore:",
        [
            "sprint_planning (Work Items, Bugs, Velocity)",
            "capacity_planning (Team Capacity & Allocation %)",
            "competency_matrix (Skills, Expected vs Current Levels)",
            "pi_planning (PI-1 to PI-4 Roadmaps & Milestones)",
            "test_cases (Master ISO 29119 Test Store)",
            "defects_only (Filtered Open Bugs)"
        ]
    )

    if "sprint_planning" in bq_table:
        st.subheader("Sprint Planning & Work Items (`axiom_data.sprint_planning`)")
        tasks = bigquery_get_sprint_tasks("")
        if tasks:
            df = pd.DataFrame(tasks)
            safe_dataframe(df, use_container_width=True)
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total Items", len(df))
            bugs = df[df["Type"] == "Bug"] if "Type" in df.columns else pd.DataFrame()
            col_m2.metric("Defects / Bugs", len(bugs))
            col_m3.metric("Sprints Tracked", df["Sprint_ID"].nunique() if "Sprint_ID" in df.columns else 0)

    elif "capacity_planning" in bq_table:
        st.subheader("Engineer Capacity & Allocations (`axiom_data.capacity_planning`)")
        cap = bigquery_get_team_capacity()
        if cap:
            df = pd.DataFrame(cap)
            safe_dataframe(df, use_container_width=True)
            over = df[df["Allocation_%"].astype(str).str.replace("%", "").astype(float) > 85]
            if not over.empty:
                st.warning(f"⚠️ {len(over)} engineer allocations exceed the 85% planned capacity limit!")

    elif "competency_matrix" in bq_table:
        st.subheader("Developer Competency Matrix (`axiom_data.competency_matrix`)")
        comp = bigquery_get_competency_matrix()
        if comp:
            df = pd.DataFrame(comp)
            safe_dataframe(df, use_container_width=True)
            st.caption(f"Showing {len(df)} skill competency ratings across associates.")

    elif "pi_planning" in bq_table:
        st.subheader("Program Increment Roadmap (`axiom_data.pi_planning`)")
        pi = bigquery_get_pi_planning()
        if pi:
            df = pd.DataFrame(pi)
            safe_dataframe(df, use_container_width=True)

    elif "test_cases" in bq_table:
        st.subheader("Master Test Case Store (`axiom_data.test_cases`)")
        tc = bigquery_get_test_run_results()
        if tc:
            df = pd.DataFrame(tc)
            safe_dataframe(df, use_container_width=True)

    elif "defects_only" in bq_table:
        st.subheader("Authoritative Defect Queue (`Type = 'Bug'`)")
        defects = bigquery_list_all_defects()
        if defects:
            df = pd.DataFrame(defects)
            safe_dataframe(df, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3: Neo4j Knowledge Graph
# ──────────────────────────────────────────────────────────────────────────────
with tab_kg:
    st.header("🕸️ Neo4j Dynamic Knowledge Graph")
    st.caption("Requirement graph nodes, semantic relationships, and blast radius connections.")

    k_col1, k_col2, k_col3 = st.columns(3)
    k_col1.metric("Graph Nodes", len(_DYNAMIC_KG.nodes))
    k_col2.metric("Total Relationships", len(_DYNAMIC_KG.edges))
    k_col3.metric("Semantic Edges", sum(1 for e in _DYNAMIC_KG.edges if e.get("category") == "semantic"))

    st.subheader("Graph Edges & Blast Radius Connections")
    edge_rows = [
        {"Source": e.get("source"), "Relationship": e.get("relationship"), "Target": e.get("target"), "Category": e.get("category")}
        for e in _DYNAMIC_KG.edges
    ]
    safe_dataframe(pd.DataFrame(edge_rows), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5: Evidence Vault & Learned Response Memory
# ──────────────────────────────────────────────────────────────────────────────
with tab_envelopes:
    st.header("🛡️ Evidence Vault & Grounded Provenance")
    st.caption("Immutable EvidenceEnvelopes collected across LangGraph cognitive execution & learned human feedback benchmarks.")

    # Sub-tabs for Evidence and Learned Memory
    sub_tab_evidence, sub_tab_memory = st.tabs([
        "📋 Verified Evidence Envelopes",
        "⭐ Learned Response Benchmarks & Feedback"
    ])

    with sub_tab_evidence:
        all_evidences = []
        for m in st.session_state.get("messages", []):
            all_evidences.extend(m.get("evidences", []))

        if all_evidences:
            st.write(f"Collected **{len(all_evidences)}** verified evidence envelopes across active session:")
            for idx, env in enumerate(all_evidences, 1):
                with st.expander(f"Artifact {idx}: {env.get('artifact_id')} ({env.get('artifact_type')}) - Source: {env.get('source_system')}"):
                    st.json(env)
        else:
            st.info("No evidence envelopes collected yet in this session. Run a query in Tab 2 to collect grounded evidence.")

    with sub_tab_memory:
        st.subheader("⭐ Human Feedback & Exemplar Learning Memory")
        st.caption(
            "AXIOM continuously aligns with team standards through user ratings. "
            "Responses approved with 👍 are stored as positive exemplars and automatically injected into "
            "the Vertex AI Gemini synthesis prompt to guide format, technical rigor, and actionable recommendations."
        )

        # 1. Feedback KPI Metrics
        fb_stats = firestore_get_feedback_stats()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Feedback", fb_stats["total_feedback"])
        c2.metric("👍 Helpful", fb_stats["positive"])
        c3.metric("👎 Critiques", fb_stats["negative"])
        c4.metric("🧠 Learned Exemplars", fb_stats["learned_exemplars"])
        c5.metric("Satisfaction", f"{fb_stats['satisfaction_pct']}%")

        st.markdown("---")
        st.subheader("📚 Active Learned Benchmarks (Few-Shot Exemplars)")
        exemplars = firestore_get_positive_exemplars(limit=10)
        if exemplars:
            for ex in exemplars:
                with st.expander(f"⭐ Approved Benchmark: {ex.get('query', 'Query')[:60]}..."):
                    st.write(f"**Query**: {ex.get('query')}")
                    st.write(f"**Approved By**: `{ex.get('user_id', 'Unknown')}` | **Session**: `{ex.get('session_id', 'N/A')}`")
                    if ex.get("comment"):
                        st.info(f"💡 **User Note**: {ex.get('comment')}")
                    st.markdown("**Approved Response Content:**")
                    st.markdown(ex.get("response", ""))
        else:
            st.info("No approved exemplars yet. Click 👍 on any assistant response in Tab 2 to teach AXIOM your preferred format!")

        st.markdown("---")
        st.subheader("📝 Complete Human Feedback Audit Trail")
        all_fb = firestore_get_all_feedback()
        if all_fb:
            fb_table = [
                {
                    "Timestamp": f.get("timestamp", "")[:19],
                    "User": f.get("user_id"),
                    "Rating": "👍 Helpful" if f.get("rating") == "positive" else "👎 Needs Improvement",
                    "Master": f.get("master", "AXIOM-PM"),
                    "Query": (f.get("query", "")[:50] + "...") if len(f.get("query", "")) > 50 else f.get("query", ""),
                    "User Note": f.get("comment", "")
                }
                for f in all_fb
            ]
            safe_dataframe(pd.DataFrame(fb_table), use_container_width=True)
        else:
            st.caption("No feedback entries recorded yet.")
