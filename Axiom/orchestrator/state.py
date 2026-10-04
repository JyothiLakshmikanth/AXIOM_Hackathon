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
    target_master: Optional[str]  # "PM.ai" or "ENG.ai"
    target_capability: Optional[str]
    confidence_score: float

    # Cognitive Master State
    current_step: str
    reasoning_hypothesis: str
    memory_hit: bool
    selected_skill: Optional[Dict[str, Any]]
    validation_status: str  # "PASSED", "BLOCKED", "GUARDRAIL_VIOLATION"
    guardrail_messages: List[str]

    # Agent Delegation & Evidence
    delegated_agent: Optional[str]
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
