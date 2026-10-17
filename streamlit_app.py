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

from orchestrator.graph import run_axiom_orchestration, axiom_runner
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

# Sidebar
with st.sidebar:
    st.title("⬡ AXIOM Orchestrator")
    st.caption("Google Cloud Evidence-Driven Multi-Agent System")

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
    st.title("🎯 AXIOM Project Risk Cockpit")
    st.caption("Live Executive Risk Assessment, Resource Bottlenecks, and Critical Defect Radar across AXIOM E-Key 2W.")

    # Load Risk Report Data
    report_path = os.path.join(os.path.dirname(__file__), "agents", "risk_board", "risk_analysis_report.json")
    risk_data = {}
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                risk_data = json.load(f)
        except Exception:
            pass

    summary = risk_data.get("summary", {
        "overall_risk_level": "Medium",
        "critical_defects": 6,
        "resource_bottlenecks": 6,
        "at_risk_sprints": 1
    })

    # Top Metric Banner
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1:
        st.metric("Overall Project Risk", f"🟠 {summary.get('overall_risk_level', 'Medium')}", delta="Amber Alert", delta_color="inverse")
    with r_col2:
        st.metric("Critical / High Defects", f"{summary.get('critical_defects', 6)} Active", delta="Requires RCA", delta_color="inverse")
    with r_col3:
        st.metric("Capacity Bottlenecks", f"{summary.get('resource_bottlenecks', 6)} Overloaded", delta="> 85% Ceiling", delta_color="inverse")
    with r_col4:
        st.metric("At-Risk Sprints", "SPR-03 (Active)", delta="Critical Path Impact", delta_color="inverse")

    st.markdown("---")

    # Layout: Critical Defect Radar & Resource Overload Watch
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.subheader("🚨 Critical Defect Radar & Delivery Impact")
        st.write("Identified high-impact defects threatening upcoming delivery milestones:")

        defects = risk_data.get("critical_defects", [
            {
                "id": "TWK-107",
                "summary": "Boundary-zone unlock intermittently fails",
                "priority": "Critical",
                "status": "Open",
                "assignee": "RES-04",
                "sprint": "SPR-03",
                "impact": "High (ASIL-B Safety Violation)",
                "mitigation": "Edge case testing & hysteresis patch"
            },
            {
                "id": "TWK-108",
                "summary": "Unlock latency exceeds target on low-power phone",
                "priority": "High",
                "status": "Open",
                "assignee": "RES-05",
                "sprint": "SPR-03",
                "impact": "Medium (QoS SLA Breach)",
                "mitigation": "Async polling & BLE buffer optimization"
            },
            {
                "id": "TWK-104",
                "summary": "Passive unlock state desynchronization",
                "priority": "Critical",
                "status": "In Progress",
                "assignee": "RES-04",
                "sprint": "SPR-03",
                "impact": "High (Security Lockout)",
                "mitigation": "State machine mutex enforcement"
            }
        ])

        defect_df = pd.DataFrame(defects)[["id", "summary", "priority", "status", "assignee", "sprint", "impact"]]
        st.dataframe(defect_df, use_container_width=True)

        st.caption("💡 Click below to transfer high-priority defect triage into the cognitive engine:")
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("⚡ Dispatch TWK-107 Defect Triage & RCA"):
                st.session_state.temp_prompt = "What is the defect triage, root cause, and blast radius for TWK-107?"
                st.info("Query queued! Switch to '🧠 Multi-Agent Orchestrator & HITL' tab to view execution.")
        with act_col2:
            if st.button("⚖️ Generate SPR-03 Workload Rebalancing Plan"):
                st.session_state.temp_prompt = "Analyze team capacity bottlenecks and recommend rebalancing plan for SPR-03"
                st.info("Query queued! Switch to '🧠 Multi-Agent Orchestrator & HITL' tab to view execution.")

    with c_right:
        st.subheader("👥 Resource Bottlenecks (>85% Cap)")
        st.write("Engineers exceeding the 85% safe allocation ceiling:")

        constraints = risk_data.get("resource_constraints", {})
        if constraints:
            res_list = []
            for r_id, r_info in constraints.items():
                res_list.append({
                    "Resource": r_id,
                    "Name": r_info.get("name", "Unknown"),
                    "Role": r_info.get("role", "Engineer"),
                    "Allocation": f"{r_info.get('allocation', 0)}%",
                    "Risk": r_info.get("risk_level", "High")
                })
            res_df = pd.DataFrame(res_list)
            st.dataframe(res_df, use_container_width=True)
        else:
            st.success("No resource constraints recorded.")

        st.subheader("📅 Sprint Delivery Health")
        sprint_risks = risk_data.get("sprint_risks", [
            {"sprint_id": "SPR-01", "total_items": 2, "open_items": 0, "risk_level": "Low"},
            {"sprint_id": "SPR-02", "total_items": 1, "open_items": 0, "risk_level": "Low"},
            {"sprint_id": "SPR-03", "total_items": 7, "open_items": 4, "risk_level": "Critical"},
            {"sprint_id": "SPR-04", "total_items": 4, "open_items": 4, "risk_level": "Medium"}
        ])
        s_df = pd.DataFrame(sprint_risks)[["sprint_id", "total_items", "open_items", "risk_level"]]
        st.dataframe(s_df, use_container_width=True)

    st.markdown("---")
    st.subheader("🛡️ Executive Risk Mitigation Strategies")
    mitigations = risk_data.get("mitigation_strategies", [
        "Rebalance SPR-03 tasks away from RES-04 (110% allocation) to prevent delivery slippage.",
        "Prioritize TWK-107 boundary-zone patch to meet ISO 26262 ASIL-B safety criteria.",
        "Initiate cross-training for BLE stack firmware to mitigate single-point dependency on RES-05."
    ])
    for idx, strat in enumerate(mitigations, 1):
        st.markdown(f"**{idx}.** {strat}")

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
    for msg in st.session_state.messages:
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
                    "evidences": state.get("evidence_envelopes", [])
                })
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
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AXIOM Masters reasoning through 9-node LangGraph cognitive loops..."):
            res = run_axiom_orchestration(query=prompt)

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
                        "content": res.get("final_output_markdown", "Clarification needed.")
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
                        "evidences": res.get("evidence_envelopes", [])
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
            st.dataframe(df, use_container_width=True)
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
            st.dataframe(df, use_container_width=True)
            over = df[df["Allocation_%"].astype(str).str.replace("%", "").astype(float) > 85]
            if not over.empty:
                st.warning(f"⚠️ {len(over)} engineer allocations exceed the 85% planned capacity limit!")

    elif "competency_matrix" in bq_table:
        st.subheader("Developer Competency Matrix (`axiom_data.competency_matrix`)")
        comp = bigquery_get_competency_matrix()
        if comp:
            df = pd.DataFrame(comp)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Showing {len(df)} skill competency ratings across associates.")

    elif "pi_planning" in bq_table:
        st.subheader("Program Increment Roadmap (`axiom_data.pi_planning`)")
        pi = bigquery_get_pi_planning()
        if pi:
            df = pd.DataFrame(pi)
            st.dataframe(df, use_container_width=True)

    elif "test_cases" in bq_table:
        st.subheader("Master Test Case Store (`axiom_data.test_cases`)")
        tc = bigquery_get_test_run_results()
        if tc:
            df = pd.DataFrame(tc)
            st.dataframe(df, use_container_width=True)

    elif "defects_only" in bq_table:
        st.subheader("Authoritative Defect Queue (`Type = 'Bug'`)")
        defects = bigquery_list_all_defects()
        if defects:
            df = pd.DataFrame(defects)
            st.dataframe(df, use_container_width=True)

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
    st.dataframe(pd.DataFrame(edge_rows), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4: Evidence Vault
# ──────────────────────────────────────────────────────────────────────────────
with tab_envelopes:
    st.header("🛡️ Evidence Vault & Grounded Provenance")
    st.caption("Immutable EvidenceEnvelopes collected across LangGraph cognitive execution.")

    all_evidences = []
    for m in st.session_state.get("messages", []):
        all_evidences.extend(m.get("evidences", []))

    if all_evidences:
        st.write(f"Collected **{len(all_evidences)}** verified evidence envelopes across active session:")
        for idx, env in enumerate(all_evidences, 1):
            with st.expander(f"Artifact {idx}: {env.get('artifact_id')} ({env.get('artifact_type')}) - Source: {env.get('source_system')}"):
                st.json(env)
    else:
        st.info("No evidence envelopes collected yet in this session. Run a query in Tab 1 to collect grounded evidence.")
