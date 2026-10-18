"""
Axiom Graph State Definitions.
Defines Pydantic models and TypedDict schemas for LangGraph state propagation,
EvidenceEnvelopes, Clarification payloads, and Visual-First artifacts.
"""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceEnvelope(BaseModel):
    """
    Mandatory evidence envelope applied to every artifact in AXIOM.
    Enforces provenance, authority, and verification status.
    """
    artifact_id: str
    artifact_type: str
    source_system: str
    source_uri: str
    version: str = "1.0"
    updated_at: str
    authoritative: bool = True
    synthetic: bool = True
    quality_status: str = "verified"
    payload: Dict[str, Any] = Field(default_factory=dict)


class VisualArtifact(BaseModel):
    """Visual-first artifact generated for user presentation."""
    requires_visual: bool = False
    visual_type: str = "diagram"  # diagram, chart, flow, fishbone, diff
    image_prompt: Optional[str] = None
    image_model: str = "imagegeneration@006"  # Imagen 2 / Imagen 3
    image_url: Optional[str] = None
    fallback_mermaid: Optional[str] = None
    structured_caption: Optional[str] = None


class ClarificationState(BaseModel):
    """State returned when user intent is ambiguous, triggering immediate termination."""
    clarification_needed: bool = False
    ambiguity_reason: Optional[str] = None
    clarification_questions: List[str] = Field(default_factory=list)


class AxiomState(TypedDict, total=False):
    """
    Top-level shared state passed across LangGraph nodes.
    Supports Intent Router, Memory Retrieval, Master Cognitive Loops, and Visual-First response generation.
    """
    # User Input & Session Metadata
    query: str
    session_id: str
    user_id: str

    # Intent Router Outputs
    intent_clarified: bool
    clarification: Dict[str, Any]
    target_master: Optional[str]  # "AXIOM-PM" or "AXIOM-ENG"
    target_capability: Optional[str]
    confidence_score: float
    confidence_level: Optional[str]  # "High" | "Medium" | "Low"
    system_prompt_router: str  # ← loaded from router JSON/prompt at router_node init

    # Cognitive Master State
    current_step: str
    reasoning_hypothesis: str
    memory_hit: bool
    selected_skill: Optional[Dict[str, Any]]
    validation_status: str  # "PASSED", "BLOCKED", "GUARDRAIL_VIOLATION"
    guardrail_messages: List[str]

    # Agent Delegation & Evidence
    delegated_agent: Optional[str]
    executed_agents: List[str]
    agent_executions: List[Dict[str, Any]]
    agent_task_input: Dict[str, Any]
    evidence_envelopes: List[Dict[str, Any]]
    evaluation_passed: bool
    evaluation_iteration_count: int
    evaluation_checklist_results: Dict[str, bool]

    # Synthesis & Visual-First Delivery
    synthesized_summary: str
    visual_artifact: Dict[str, Any]
    structured_answer: Dict[str, Any]
    final_output_markdown: str

    # AXIOM 9-Node Architecture Fields
    planner_decision: Dict[str, Any]  # {agent_id, agent_prompt, gap, rationale, expected_evidence_type, stopping_condition}
    required_evidence_dimensions: List[str]  # what evidence dimensions are needed to answer query
    resolved_intent: str  # classified capability intent from REASON node
    evidence_sufficiency: str  # "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT"
    material_gaps: List[str]  # unfilled evidence gaps that block synthesis
    cross_handoff_needed: bool  # does PM.ai need to handoff to ENG.ai or vice versa
    cross_handoff_request: Dict[str, Any]  # request payload for cross-master handoff
    cross_handoff_response: str  # response from receiving master
    cross_handoff_done: bool  # handoff completion flag
    response_mode: str  # "text_only" | "text_and_image" | "image_only"
    human_validation_required: bool  # does response require human review before delivery
    human_validation_result: str  # "APPROVED" | "REJECTED" | "REQUEST_MORE"
    human_feedback: str  # human reviewer feedback
    hitl_loop_count: int  # count of human-in-the-loop review iterations
    agent_prompt: str  # specialized prompt created by PLAN node for agent execution
