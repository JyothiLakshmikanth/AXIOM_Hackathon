"""
AXIOM Streamlit Application.
Alternative pure-Python dashboard for local interactive exploration and demonstrations.
Run with: streamlit run streamlit_app.py
"""

import os
import sys
import streamlit as st

# Configure page
st.set_page_config(
    page_title="AXIOM | Multi-Agent Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from orchestrator.graph import run_axiom_orchestration
from agents.tools.neo4j_tools import _DYNAMIC_KG

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
    st.subheader("Masters & Specialized Agents")
    st.write("• **PM.ai Master**: Project Management & Governance")
    st.write("• **ENG.ai Master**: Code & Defect Engineering")
    st.write("• **Specialized Agents**: Requirement (Neo4j), Defect, Test, Resource, CodeFix")

# Main Chat Interface
st.title("AXIOM Multi-Agent Intelligence Platform")
st.write("Ask questions about defect triage, 8D RCA, sprint replanning, or requirement blast radius.")

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "visual" in msg and msg["visual"].get("requires_visual"):
            vis = msg["visual"]
            st.info(f"🎨 **Visual-First**: {vis.get('structured_caption', '')}")
            if vis.get("fallback_mermaid"):
                st.code(vis["fallback_mermaid"], language="mermaid")

# Quick prompt chips
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🛡️ PM.ai Defect Triage (GH-ISSUE-107)"):
        st.session_state.temp_prompt = "What is the blast radius and defect triage for GH-ISSUE-107?"
with col2:
    if st.button("⚡ ENG.ai Code RCA (proximity_controller.py)"):
        st.session_state.temp_prompt = "Perform deep code RCA and generate surgical patch for proximity_controller.py"
with col3:
    if st.button("🔍 Neo4j Requirement Impact"):
        st.session_state.temp_prompt = "Base variant fails passive unlock when BLE RSSI drops below threshold"

prompt = st.chat_input("Ask AXIOM a question...")
if hasattr(st.session_state, "temp_prompt") and st.session_state.temp_prompt:
    prompt = st.session_state.temp_prompt
    st.session_state.temp_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AXIOM Masters reasoning through LangGraph cognitive loops..."):
            res = run_axiom_orchestration(query=prompt)
            
            master = res.get("target_master", "Router")
            capability = res.get("target_capability", "General")
            st.caption(f"**Routed Master:** {master} | **Capability:** {capability} | **Confidence:** {res.get('confidence_score', 0):.2f}")
            
            # Clarification check
            clarification = res.get("clarification", {})
            if clarification.get("clarification_needed"):
                st.warning(f"**Intent Clarification Needed:** {clarification.get('ambiguity_reason')}")
                st.write("Please clarify:")
                for q in clarification.get("clarification_questions", []):
                    st.write(f"- {q}")
            
            # Markdown output
            output_md = res.get("final_output_markdown", "No output generated.")
            st.markdown(output_md)
            
            # Visual presentation
            visual = res.get("visual_artifact", {})
            if visual.get("requires_visual"):
                st.info(f"🎨 **Visual Synthesis ({visual.get('visual_type')}):** {visual.get('structured_caption')}")
                if visual.get("fallback_mermaid"):
                    st.code(visual["fallback_mermaid"], language="mermaid")
            
            # Evidences expander
            evidences = res.get("evidence_envelopes", [])
            if evidences:
                with st.expander(f"📋 View Grounded Evidence Envelopes ({len(evidences)})"):
                    for env in evidences:
                        st.json(env)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": output_md,
                "visual": visual
            })
