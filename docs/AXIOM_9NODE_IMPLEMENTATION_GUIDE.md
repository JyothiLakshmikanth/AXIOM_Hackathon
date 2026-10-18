# AXIOM 9-Node Architecture Implementation Guide

**Status:** Implementation in progress (Phase 1-3)  
**Target Completion:** Week 1-3  
**Architecture:** LangGraph + LangChain with GCP Gemini integration  
**No Hardcoding Principle:** All intelligence driven by JSON prompts + LLM reasoning

---

## Executive Summary: The 9-Node Design vs Your Proposal

### Your Proposed Sequence (7 nodes):
```
reason → observe → decide → execute → verify → validate → synthesize
```

**Problems:**
1. **Observe before Execute is backwards** — evidence comes AFTER execution, not before
2. **Verify + Validate undefined** — both sound like the same thing
3. **No PLAN node** — how does system decide which agent to call and how to prompt it?
4. **No CROSS_HANDOFF** — no way for PM.ai ↔ ENG.ai handoff
5. **No VISUAL_GEN** — images need conditional, separate generation
6. **No HUMAN_VALIDATE** — no HITL checkpoint for final approval

### Recommended 9-Node Sequence:
```
REASON → PLAN → EXECUTE → OBSERVE → EVALUATE 
    ↓ (loop if insufficient)
    → CROSS_HANDOFF (optional) → SYNTHESIZE → VISUAL_GEN (conditional) → HUMAN_VALIDATE (HITL) → END
```

**Why this works:**
| Step | Purpose | Intelligence |
|------|---------|--------------|
| **REASON** | Classify intent, form hypothesis, define required evidence | LLM: classify capability |
| **PLAN** | Decide which agent fills the biggest gap & create specialized prompt | **LLM (CRITICAL):** Agent selection |
| **EXECUTE** | Call the selected specialized agent | ReAct loop with tools |
| **OBSERVE** | Ingest and normalize evidence from agent | Deterministic: normalize envelopes |
| **EVALUATE** | Check if evidence is sufficient | Deterministic: validate against requirements |
| **CROSS_HANDOFF** | If needed, ask other master | Conditional: text_only response |
| **SYNTHESIZE** | Synthesize all evidence into structured answer | LLM: determine response_mode |
| **VISUAL_GEN** | Generate images if needed | Conditional: Imagen API |
| **HUMAN_VALIDATE** | HITL checkpoint: approve/reject/request more | Human decision → loop or end |

---

## Core Files Being Implemented

### Phase 1: Core Infrastructure

#### 1. **Enhanced AxiomState** (`orchestrator/state.py`)
All 9-node fields added to TypedDict:
```python
class AxiomState(TypedDict, total=False):
    # ... existing fields ...
    
    # REASON node
    required_evidence_dimensions: List[str]
    resolved_intent: str
    reasoning_hypothesis: str
    
    # PLAN node
    planner_decision: Dict[str, Any]  # {agent_id, agent_prompt, gap, rationale}
    agent_prompt: str  # specialized prompt created by PLAN
    
    # EVALUATE node
    evidence_sufficiency: str  # "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT"
    material_gaps: List[str]  # unfilled evidence gaps
    
    # CROSS_HANDOFF node
    cross_handoff_needed: bool
    cross_handoff_request: Dict[str, Any]
    cross_handoff_response: str
    cross_handoff_done: bool
    
    # SYNTHESIZE node
    response_mode: str  # "text_only" | "text_and_image" | "image_only"
    structured_answer: Dict[str, Any]
    
    # VISUAL_GEN node
    visual_artifact: Dict[str, Any]
    
    # HUMAN_VALIDATE node (HITL)
    human_validation_required: bool
    human_validation_result: str  # "APPROVED" | "REJECTED" | "REQUEST_MORE"
    human_feedback: str
    hitl_loop_count: int
```

#### 2. **Prompt Loader** (`orchestrator/prompt_loader.py`) — NEW
Dynamically loads stage-specific prompts from JSON without hardcoding:
```python
def load_prompt(master_id: str, node_name: str) -> str:
    """Load prompt for a specific node from axiom_{master_id}_master_v3.json"""
    
def load_stage_sections(master_id: str, node_name: str) -> List[Dict]:
    """Load relevant sections from JSON for a node"""
    
def merge_sections(sections: List[Dict]) -> str:
    """Concatenate sections into one full prompt"""
```

**Example:**
```python
prompt = load_prompt("AXIOM-PM", "execute_action_node")
# Loads from prompts/axiom_pm_master_v3.json
# Uses stage_to_sections mapping to get [04_specialized_agents, 06_guardrails, 22_planner_decision_system]
# Merges them into one prompt string
```

#### 3. **GCP Client** (`orchestrator/gcp_client.py`) — NEW
Singleton for all GCP services:
```python
class GCPClient:
    def call_gemini(self, system_prompt: str, user_input: str, temp=0.7) -> str:
        """Call Gemini 2.0 Flash via Vertex AI"""
        
    def query_bigquery(self, sql: str) -> List[Dict]:
        """Execute BigQuery query"""
        
    def get_firestore(self, doc_path: str) -> Dict:
        """Fetch Firestore document"""
        
    def set_firestore(self, doc_path: str, data: Dict):
        """Save to Firestore"""

# Global singleton
gcp = get_gcp_client()
```

#### 4. **Evidence Cache** (`orchestrator/evidence_cache.py`) — NEW
Manages EvidenceEnvelope lifecycle:
```python
def normalize_evidence_envelope(raw_data: Dict, artifact_type: str) -> Dict:
    """Convert raw agent output to EvidenceEnvelope format"""
    
def evaluate_evidence_sufficiency(
    collected_envelopes: List[Dict],
    required_dimensions: List[str],
    capability_matrix: Dict
) -> str:
    """Returns: "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT" """
    
def extract_material_gaps(required_dims: List[str], collected: List[Dict]) -> List[str]:
    """Returns list of missing evidence dimensions"""
```

---

### Phase 2: Planner & Intelligence Hub

#### 5. **PLAN Node** (`orchestrator/planner_node.py`) — NEW, MOST CRITICAL
The intelligence hub where the system decides which agent to call:

```python
def plan_node(state: AxiomState) -> AxiomState:
    """
    Intelligent planner: decides which agent to call based on evidence gaps.
    
    NO HARDCODING: All agent selection comes from LLM reasoning.
    """
    
    # Step 1: Identify missing evidence
    required = state["required_evidence_dimensions"]
    collected_types = {env["artifact_type"] for env in state["evidence_envelopes"]}
    missing = set(required) - collected_types
    
    # Step 2: Load agent capabilities from registry
    agent_caps = load_agent_registry()  # {agent_id -> [evidence_types]}
    
    # Step 3: LLM Planner Call (THE INTELLIGENCE)
    planner_prompt = load_prompt(state["target_master"], "execute_action_node")
    planner_input = {
        "missing_evidence": list(missing),
        "agent_capabilities": agent_caps,
        "query": state["query"],
        "hypothesis": state["reasoning_hypothesis"],
        "iteration": state["evaluation_iteration_count"]
    }
    
    planner_response = gcp_client.call_gemini(planner_prompt, json.dumps(planner_input))
    planner_decision = json.loads(planner_response)
    
    # Step 4: Store decision
    state["planner_decision"] = planner_decision
    state["delegated_agent"] = planner_decision["agent_id"]
    state["agent_prompt"] = planner_decision["agent_prompt"]
    
    return state
```

**Planner LLM Response Format:**
```json
{
  "agent_id": "defect_agent",
  "gap": "Missing authoritative severity classification for GH-ISSUE-107",
  "agent_objective": "Retrieve severity, urgency, and leakage direction",
  "agent_prompt": "<detailed specialized prompt for defect_agent>",
  "rationale": "defect_agent owns BigQuery issue records",
  "expected_evidence_type": "github_issue_record",
  "stopping_condition": "severity field present with quality_status=verified"
}
```

#### 6. **Edge Routing** (`orchestrator/edge_routing.py`) — NEW
Conditional routing logic for LangGraph:

```python
def route_after_evaluate(state: AxiomState) -> str:
    """After EVALUATE: loop back, handoff, or proceed to synthesis"""
    if state["evidence_sufficiency"] == "SUFFICIENT":
        if state.get("cross_handoff_needed") and not state.get("cross_handoff_done"):
            return "cross_handoff"
        else:
            return "synthesize"
    elif state["evaluation_iteration_count"] >= 5:
        return "synthesize"  # safety cap
    else:
        return "plan"  # loop back for more evidence

def route_after_synthesize(state: AxiomState) -> str:
    """After SYNTHESIZE: generate visuals or proceed to HITL"""
    if state["response_mode"] in ("text_and_image", "image_only"):
        return "visual_gen"
    else:
        return "human_validate"

def route_after_hitl(state: AxiomState) -> str:
    """After HUMAN_VALIDATE: approve, restart, or request more"""
    result = state.get("human_validation_result", "APPROVED")
    if result == "APPROVED":
        return END
    elif result == "REJECTED":
        return "reason"  # restart with feedback
    elif result == "REQUEST_MORE":
        if state.get("hitl_loop_count", 0) >= 2:
            return END
        else:
            return "plan"  # one more agent call
    else:
        return END
```

---

### Phase 3: Advanced Nodes

#### 7. **CROSS_HANDOFF Node** (`orchestrator/advanced_nodes.py`)
Master-to-master handoff with strict text_only rule:

```python
def cross_handoff_node(state: AxiomState) -> AxiomState:
    """
    Optional: PM.ai asks ENG.ai (or vice versa) for domain-specific analysis.
    Response is ALWAYS text_only; never recursive.
    """
    
    if not state.get("cross_handoff_needed"):
        return state
    
    from_master = state["target_master"]
    to_master = "AXIOM-ENG" if from_master == "AXIOM-PM" else "AXIOM-PM"
    
    # Build handoff request
    handoff_request = {
        "from_master": from_master,
        "to_master": to_master,
        "context_summary": state["synthesized_summary"][:500],
        "analysis_done": state["evidence_envelopes"],
        "specific_task": "...",
        "response_mode": "text_only"  # ALWAYS text_only
    }
    
    # Call other master's workflow
    response_text = call_other_master_workflow(to_master, handoff_request)
    
    # Append as EvidenceEnvelope
    state["evidence_envelopes"].append({
        "artifact_type": "cross_master_analysis",
        "source_system": f"axiom_{to_master.lower()}",
        "payload": {"response": response_text},
        "quality_status": "verified"
    })
    
    state["cross_handoff_done"] = True  # Prevent recursion
    return state
```

#### 8. **SYNTHESIZE Node** (`orchestrator/advanced_nodes.py`)
LLM synthesizes all evidence:

```python
def synthesize_node(state: AxiomState) -> AxiomState:
    """
    Synthesize all evidence into structured answer.
    Determine response_mode: text_only | text_and_image | image_only
    """
    
    synthesis_prompt = load_prompt(state["target_master"], "synthesize_node")
    synthesis_input = {
        "query": state["query"],
        "hypothesis": state["reasoning_hypothesis"],
        "evidence": [env["payload"] for env in state["evidence_envelopes"]],
        "target_capability": state["target_capability"]
    }
    
    response = gcp_client.call_gemini(synthesis_prompt, json.dumps(synthesis_input))
    synthesized_data = json.loads(response)
    
    state["synthesized_summary"] = synthesized_data.get("synthesis", "")
    state["structured_answer"] = synthesized_data
    state["response_mode"] = synthesized_data.get("response_mode", "text_only")
    
    return state
```

#### 9. **VISUAL_GEN Node** (`orchestrator/advanced_nodes.py`)
Conditional image generation:

```python
def visual_gen_node(state: AxiomState) -> AxiomState:
    """
    Only if response_mode = text_and_image or image_only.
    Generate visualization using Gemini Imagen.
    """
    
    if state["response_mode"] == "text_only":
        return state
    
    visual_type = state["structured_answer"].get("visual_type", "diagram")
    
    # Call Gemini Imagen
    imagen_prompt = f"Generate a {visual_type} visualization of: {state['synthesized_summary']}"
    visual_response = gcp_client.call_gemini("You are a visualization designer.", imagen_prompt)
    visual_data = json.loads(visual_response)
    
    state["visual_artifact"] = {
        "visual_type": visual_type,
        "image_url": visual_data.get("image_url"),
        "fallback_mermaid": visual_data.get("fallback_mermaid")
    }
    
    return state
```

#### 10. **HUMAN_VALIDATE Node** (`orchestrator/advanced_nodes.py`)
HITL checkpoint with interrupt/resume:

```python
def human_validate_node(state: AxiomState) -> AxiomState:
    """
    HITL checkpoint: interrupt here.
    Human reviews structured_answer + visual_artifact.
    Human clicks: APPROVE | REJECT | REQUEST_MORE.
    Resume with human's decision.
    """
    
    state["human_validation_required"] = True
    
    # In LangGraph: graph.interrupt_before("human_validate")
    # Streamlit will render UI here
    # On resume: state["human_validation_result"] is set by human
    
    return state
```

---

### Phase 4: LangGraph Wiring

#### 11. **Refactored LangGraph** (`orchestrator/graph.py`)
Wire all 9 nodes with conditional edges:

```python
from langgraph.graph import StateGraph, END
from orchestrator.edge_routing import (
    route_after_evaluate,
    route_after_synthesize,
    route_after_visual_gen,
    route_after_hitl,
    route_after_intent_router,
    route_after_memory
)

builder = StateGraph(AxiomState)

# Router
builder.add_node("router", router_node)

# PM.ai 9-node loop
builder.add_node("pm_reason", pm_reason_node)
builder.add_node("pm_memory", pm_memory_retrieval_node)
builder.add_node("pm_plan", plan_node)  # PLAN: intelligent agent selection
builder.add_node("pm_execute", pm_execute_agent_node)
builder.add_node("pm_observe", pm_observe_evidence_node)
builder.add_node("pm_evaluate", pm_evaluate_node)
builder.add_node("pm_cross_handoff", cross_handoff_node)
builder.add_node("pm_synthesize", synthesize_node)
builder.add_node("pm_visual_gen", visual_gen_node)
builder.add_node("pm_human_validate", human_validate_node)

# ENG.ai 9-node loop (mirror)
builder.add_node("eng_reason", eng_reason_node)
builder.add_node("eng_memory", eng_memory_retrieval_node)
builder.add_node("eng_plan", plan_node)
builder.add_node("eng_execute", eng_execute_agent_node)
builder.add_node("eng_observe", eng_observe_evidence_node)
builder.add_node("eng_evaluate", eng_evaluate_node)
builder.add_node("eng_cross_handoff", cross_handoff_node)
builder.add_node("eng_synthesize", synthesize_node)
builder.add_node("eng_visual_gen", visual_gen_node)
builder.add_node("eng_human_validate", human_validate_node)

# Edges: Router → Master
builder.set_entry_point("router")
builder.add_conditional_edges("router", route_after_intent_router)

# PM.ai Edges
builder.add_edge("pm_reason", "pm_memory")
builder.add_conditional_edges("pm_memory", lambda s: route_after_memory(s, "pm"))
builder.add_edge("pm_plan", "pm_execute")
builder.add_edge("pm_execute", "pm_observe")
builder.add_edge("pm_observe", "pm_evaluate")
builder.add_conditional_edges("pm_evaluate", route_after_evaluate)
builder.add_edge("pm_cross_handoff", "pm_synthesize")
builder.add_edge("pm_synthesize", "pm_visual_gen")
builder.add_conditional_edges("pm_visual_gen", route_after_visual_gen)
builder.add_edge("pm_visual_gen", "pm_human_validate")
builder.add_conditional_edges("pm_human_validate", route_after_hitl)

# ENG.ai Edges (mirror)
# ... (same as PM.ai)

graph = builder.compile()
```

---

### Phase 5: Streamlit HITL UI

#### 12. **HITL Renderer & 3-Stage Pipeline Checkpoint** (`streamlit_components/hitl_renderer.py`) — ENHANCED
Human-in-the-loop checkpoint UI with interactive approval, PR inspection, unified patch diff, and issue ticket comments:

```python
def render_hitl_checkpoint(state: AxiomState) -> Dict[str, Any]:
    """
    Render HUMAN_VALIDATE checkpoint in Streamlit.
    Displays:
    - Structured analysis findings
    - Generated SVG vector diagram (Gemini LLM) or Mermaid.js interactive visualization
    - GitHub Issue Comment confirmation link
    - Live Pull Request badge and branch link
    - Interactive unified patch diff viewer
    Return: {"human_validation_result": "APPROVED" | "REJECTED" | "REQUEST_MORE", "human_feedback": str}
    """
    st.header("🔍 Human-in-Loop Validation Checkpoint")
    
    # 1. Structured Analysis Findings
    sections = state["structured_answer"].get("sections", [])
    for section in sections:
        st.subheader(section["title"])
        st.write(section["content"])
    
    # 2. Pure Gemini LLM SVG Vector Diagram / Mermaid Fallback
    if state["visual_artifact"].get("image_url"):
        st.image(state["visual_artifact"]["image_url"], width="stretch")
    elif state["visual_artifact"].get("fallback_mermaid"):
        render_mermaid_diagram(state["visual_artifact"]["fallback_mermaid"])
    
    # 3. Verified Evidence, Pull Request Badge & Patch Diff
    _display_evidence_summary(state.get("evidence_envelopes", []))
    
    # 4. Action Buttons (Rule #3 Compliance)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve Fix & PR", type="primary"):
            return {"human_validation_result": "APPROVED", "human_feedback": ""}
    with col2:
        if st.button("❌ Reject Proposed Fix"):
            st.session_state.show_reject_form = True
    with col3:
        if st.button("📝 Request Additional Analysis"):
            st.session_state.show_request_form = True
```

---

### Phase 6: Enhanced Master Nodes

#### PM.ai & ENG.ai Enhancements

**REASON node enhancement:**
```python
def pm_reason_node(state: AxiomState) -> AxiomState:
    capability = state["target_capability"]
    
    # Set required evidence dimensions based on capability
    if capability == "defect_triage":
        state["required_evidence_dimensions"] = [
            "github_issue_record",
            "severity_classification",
            "requirement_impact",
            "test_coverage"
        ]
    elif capability == "sprint_replanning":
        state["required_evidence_dimensions"] = [
            "velocity_history",
            "team_capacity",
            "defect_backlog"
        ]
    
    state["resolved_intent"] = capability
    return state
```

**PLAN node refactor:**
```python
def pm_plan_select_skill_node(state: AxiomState) -> AxiomState:
    """
    REFACTORED: Use intelligent planner instead of hardcoded skill selection.
    """
    from orchestrator.planner_node import plan_node
    return plan_node(state)
```

**EVALUATE node enhancement:**
```python
def pm_evaluate_node(state: AxiomState) -> AxiomState:
    from orchestrator.evidence_cache import evaluate_evidence_sufficiency, extract_material_gaps
    
    collected = state["evidence_envelopes"]
    required = state["required_evidence_dimensions"]
    
    state["evidence_sufficiency"] = evaluate_evidence_sufficiency(collected, required, CAPABILITY_MATRIX)
    state["material_gaps"] = extract_material_gaps(required, collected)
    state["evaluation_passed"] = (state["evidence_sufficiency"] == "SUFFICIENT")
    state["evaluation_iteration_count"] = state.get("evaluation_iteration_count", 0) + 1
    
    return state
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Enhance `/orchestrator/state.py` with all 9-node fields
- [ ] Create `/orchestrator/prompt_loader.py`
- [ ] Create `/orchestrator/gcp_client.py`
- [ ] Create `/orchestrator/evidence_cache.py`

### Phase 2: Planner & Intelligence
- [ ] Create `/orchestrator/planner_node.py`
- [ ] Create `/orchestrator/edge_routing.py`

### Phase 3: Advanced Nodes
- [ ] Create `/orchestrator/advanced_nodes.py` (4 functions)

### Phase 4: Master Enhancements
- [ ] Enhance `/orchestrator/pm_master.py` (REASON, PLAN, EVALUATE)
- [ ] Enhance `/orchestrator/eng_master.py` (same)

### Phase 5: LangGraph Wiring
- [ ] Refactor `/orchestrator/graph.py` to wire all 9 nodes

### Phase 6: Streamlit UI
- [ ] Create `/streamlit_components/hitl_renderer.py`
- [ ] Enhance `/streamlit_app.py` to use HITL UI

### Phase 7: GCP Deployment
- [ ] Set environment variables (GOOGLE_CLOUD_PROJECT, credentials)
- [ ] Deploy to Cloud Run / App Engine
- [ ] Test end-to-end with real Gemini calls

---

## No Hardcoding Principle

**All intelligence is prompt-driven:**

| Decision | Source |
|----------|--------|
| Which agent to call | PLAN node LLM (from execute_action_node prompt) |
| What prompt to give agent | PLAN node LLM output (agent_prompt field) |
| Evidence required for capability | capability_matrix.json |
| Evidence sufficiency | Deterministic check (evidence_cache.py) |
| Response mode | SYNTHESIZE node LLM output |
| Visual type | SYNTHESIZE node LLM output |
| HITL decision | Human (Streamlit UI) |

**No if/else agent selection in Python.** All comes from `planner_decision` LLM output.

---

## GCP + Gemini Integration

**Install:**
```bash
pip install google-cloud-vertexai google-cloud-bigquery google-cloud-firestore
```

**Setup:**
```bash
export GOOGLE_CLOUD_PROJECT=axiom-project-123
gcloud auth application-default login
```

**In code:**
```python
from orchestrator.gcp_client import get_gcp_client

gcp = get_gcp_client()
response = gcp.call_gemini("You are AXIOM-PM...", user_input)
```

**Models:**
- **LLM:** `gemini-2.0-flash-001` (fast, cheap)
- **Images:** `imagegeneration@006` (Imagen 2/3)
- **Database:** BigQuery (SQL queries)
- **Cache:** Firestore (document store)

---

## Testing Strategy

1. **Unit tests:** Each node in isolation with mock state
2. **Integration tests:** Full 9-node loop with mock agents
3. **E2E tests:** Real query through Streamlit → GCP → Gemini
4. **Performance:** Monitor iteration counts, token usage, latency

---

## Next Steps

1. **Wait for implementation agents to complete** (Phase 1-3 files)
2. **Apply enhancements to pm_master.py and eng_master.py**
3. **Wire LangGraph with all 9 nodes**
4. **Add Streamlit HITL UI**
5. **Deploy to GCP + test with real queries**

---

**Questions?** Check the `AXIOM_ARchitecture.md` for deep dives or the roadmap agent's output for specific implementation details.
