"""
Human-in-Loop Validation Checkpoint UI Component.

Renders the HUMAN_VALIDATE node checkpoint in Streamlit, allowing humans to
approve, reject, or request additional analysis before the final response is
delivered to the user.

Key responsibilities:
- Display structured answer sections in readable format
- Show generated visualizations (image or fallback Mermaid)
- Provide evidence collection transparency
- Capture human validation decisions (APPROVED, REJECTED, REQUEST_MORE)
- Return structured feedback for graph resumption
"""

from typing import Dict, List, Any
import streamlit as st
from orchestrator.state import AxiomState


def render_hitl_checkpoint(state: AxiomState) -> Dict[str, Any]:
    """
    Main function called from Streamlit app to render HUMAN_VALIDATE checkpoint.

    Displays the system's analysis results (structured answer + visual) and
    captures human approval/rejection/request for more analysis.

    Args:
        state: AxiomState dict containing analysis results, visuals, and evidence.

    Returns:
        Dict with keys:
        - "human_validation_result": str ("APPROVED", "REJECTED", "REQUEST_MORE")
        - "human_feedback": str (optional rejection/request details)

    Example:
        result = render_hitl_checkpoint(state)
        if result["human_validation_result"] == "APPROVED":
            proceed_with_final_output()
    """
    st.header("🔍 Human-in-Loop Validation Checkpoint")
    st.write(
        "Please review the system's analysis below before final delivery. "
        "Your feedback helps improve future responses."
    )

    st.divider()

    # Display structured answer
    structured_answer = state.get("structured_answer", {})
    if structured_answer:
        st.subheader("📊 Analysis Results")

        sections = structured_answer.get("sections", [])
        if sections:
            for section in sections:
                _render_section(section)
        else:
            # Fallback if no structured sections
            summary = structured_answer.get("summary", "")
            if summary:
                st.markdown(summary)

    st.divider()

    # Display visual artifact if present
    visual_artifact = state.get("visual_artifact", {})
    if visual_artifact.get("requires_visual"):
        st.subheader("🎨 Generated Visualization")

        if visual_artifact.get("image_url"):
            caption = visual_artifact.get("structured_caption", "Generated visualization")
            st.image(visual_artifact["image_url"], caption=caption, use_container_width=True)
        elif visual_artifact.get("fallback_mermaid"):
            st.info(
                f"Visual Type: **{visual_artifact.get('visual_type', 'diagram')}**"
            )
            st.code(visual_artifact["fallback_mermaid"], language="mermaid")

    st.divider()

    # Display evidence transparency
    evidence_envelopes = state.get("evidence_envelopes", [])
    if evidence_envelopes:
        _display_evidence_summary(evidence_envelopes)
        st.divider()

    # Human validation decision buttons
    st.subheader("✅ Your Decision")

    col1, col2, col3 = st.columns(3)

    # Approval path
    with col1:
        if st.button("✅ Approve", key="approve_btn", use_container_width=True):
            st.session_state.hitl_decision = {
                "human_validation_result": "APPROVED",
                "human_feedback": ""
            }
            st.success("Analysis approved! Proceeding with final response...")
            return {
                "human_validation_result": "APPROVED",
                "human_feedback": ""
            }

    # Rejection path
    with col2:
        if st.button("❌ Reject", key="reject_btn", use_container_width=True):
            st.session_state.show_reject_form = True

    # Request more path
    with col3:
        if st.button("📝 Request More", key="request_btn", use_container_width=True):
            st.session_state.show_request_form = True

    # Rejection form
    if st.session_state.get("show_reject_form"):
        st.warning("Please provide feedback on why this analysis needs rejection.")
        with st.form("rejection_form", clear_on_submit=True):
            feedback = st.text_area(
                "Rejection feedback:",
                placeholder="Explain what was incorrect or missing in the analysis...",
                height=100,
                key="reject_feedback"
            )
            submitted = st.form_submit_button("Submit Rejection", type="secondary")
            if submitted:
                if feedback.strip():
                    st.session_state.hitl_decision = {
                        "human_validation_result": "REJECTED",
                        "human_feedback": feedback.strip()
                    }
                    st.error("Analysis rejected. Routing feedback for re-analysis...")
                    st.session_state.show_reject_form = False
                    return {
                        "human_validation_result": "REJECTED",
                        "human_feedback": feedback.strip()
                    }
                else:
                    st.error("Please provide feedback before submitting rejection.")

    # Request more form
    if st.session_state.get("show_request_form"):
        st.info("Request additional analysis or clarification.")
        with st.form("request_form", clear_on_submit=True):
            request = st.text_area(
                "What additional analysis is needed?",
                placeholder="Specify what additional information, analysis depth, or clarification you need...",
                height=100,
                key="request_feedback"
            )
            submitted = st.form_submit_button("Submit Request", type="primary")
            if submitted:
                if request.strip():
                    st.session_state.hitl_decision = {
                        "human_validation_result": "REQUEST_MORE",
                        "human_feedback": request.strip()
                    }
                    st.info("Request received. Re-analyzing with your feedback...")
                    st.session_state.show_request_form = False
                    return {
                        "human_validation_result": "REQUEST_MORE",
                        "human_feedback": request.strip()
                    }
                else:
                    st.error("Please specify what additional analysis is needed.")

    # Return any decision made
    if "hitl_decision" in st.session_state:
        return st.session_state.hitl_decision

    # No decision yet
    return None


def _render_section(section: Dict[str, Any]) -> None:
    """
    Render a single section from structured answer.

    Handles different content types: text, lists, tables, and dicts.

    Args:
        section: Dict with "title" and "content" keys.
                 content can be str, list, or dict.
    """
    title = section.get("title", "Section")
    content = section.get("content")

    st.subheader(f"**{title}**")

    if isinstance(content, str):
        st.markdown(content)
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                # List of dicts as bullet points
                st.markdown(f"- **{item.get('label', 'Item')}**: {item.get('value', '')}")
            else:
                # Simple list items
                st.markdown(f"- {item}")
    elif isinstance(content, dict):
        # Key-value pairs as bullet list
        for key, value in content.items():
            st.markdown(f"- **{key}**: {value}")
    else:
        st.write(content)


def format_structured_answer(structured_answer: Dict[str, Any]) -> str:
    """
    Convert structured JSON answer into readable markdown format.

    Handles different section types (text, list, table) and formats them
    appropriately for markdown rendering.

    Args:
        structured_answer: Dict with "sections" list containing title and content.

    Returns:
        Markdown-formatted string representation of the answer.

    Example:
        md = format_structured_answer(state["structured_answer"])
        st.markdown(md)
    """
    markdown = ""
    sections = structured_answer.get("sections", [])

    for section in sections:
        title = section.get("title", "Section")
        content = section.get("content")

        markdown += f"## {title}\n\n"

        if isinstance(content, str):
            markdown += f"{content}\n\n"
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    markdown += f"- **{item.get('label', 'Item')}**: {item.get('value', '')}\n"
                else:
                    markdown += f"- {item}\n"
            markdown += "\n"
        elif isinstance(content, dict):
            for key, value in content.items():
                markdown += f"- **{key}**: {value}\n"
            markdown += "\n"
        else:
            markdown += f"{str(content)}\n\n"

    return markdown


def _display_evidence_summary(evidence_envelopes: List[Dict[str, Any]]) -> None:
    """
    Display what evidence was collected for transparency.

    Shows evidence sources and types to help human understand what data
    informed the analysis.

    Args:
        evidence_envelopes: List of EvidenceEnvelope dicts with metadata.
    """
    with st.expander(f"📋 Evidence Collected ({len(evidence_envelopes)} sources)"):
        for i, env in enumerate(evidence_envelopes, 1):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption(f"**Source {i}**")
                st.write(env.get("source_system", "Unknown"))

            with col2:
                st.caption("**Type**")
                st.write(env.get("artifact_type", "Unknown"))

            with col3:
                st.caption("**Quality**")
                quality = env.get("quality_status", "unknown")
                if quality == "verified":
                    st.success(quality)
                elif quality == "partial":
                    st.warning(quality)
                else:
                    st.info(quality)

            st.divider()


def stream_hitl_integration(graph: Any, state: AxiomState) -> AxiomState:
    """
    Integration function with LangGraph interrupt/resume for HITL.

    This function assumes the graph has been configured to interrupt at
    the "human_validate" node. It renders the HITL checkpoint UI and
    resumes graph execution with the human's decision.

    Args:
        graph: LangGraph compiled graph with interrupt capability.
        state: Current AxiomState at the HUMAN_VALIDATE node.

    Returns:
        Final AxiomState after graph resumption with human decision.

    Note:
        Before calling this function, the graph should be configured with:
        graph.interrupt_before(["human_validate"])

    Example:
        # In streamlit_app.py
        if state.get("current_node") == "human_validate":
            final_state = stream_hitl_integration(graph, state)
            display_final_response(final_state)
    """
    # Render HITL checkpoint and capture human decision
    hitl_result = render_hitl_checkpoint(state)

    if hitl_result is None:
        # No decision made yet - checkpoint will be re-rendered on next interaction
        return state

    # Augment state with human validation results
    augmented_state = dict(state)
    augmented_state["human_validation_result"] = hitl_result["human_validation_result"]
    augmented_state["human_feedback"] = hitl_result["human_feedback"]
    augmented_state["human_validation_required"] = True
    augmented_state["human_validated_at"] = _get_timestamp()

    # Resume graph execution with human decision
    try:
        final_state = graph.invoke(augmented_state)
        return final_state
    except Exception as e:
        st.error(f"Error resuming graph execution: {str(e)}")
        return augmented_state


def _get_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO format timestamp string.
    """
    from datetime import datetime
    return datetime.utcnow().isoformat()
