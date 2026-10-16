# AXIOM System Architecture Design

## 1. System Overview

```
Streamlit Frontend
      │  user query
      ▼
 [TOP-LEVEL ROUTER]   ── LangGraph node, JSON prompt-driven
      │  intent classified → PM.ai or ENG.ai
      ├──────────────────────┐
      ▼                      ▼
 [PM.ai MASTER]        [ENG.ai MASTER]
  LangGraph + ReAct      LangGraph + ReAct
  8-node cognitive loop  8-node cognitive loop
      │                      │
  calls 3 agents         calls 3 agents
  (defect, resource,     (codefix, test,
   requirement, test)     requirement, defect)
      │                      │
      └──── cross-handoff ───┘  (text_only, bidirectional)
      │
      ▼
  Response to Streamlit
  text_only | text_and_image | image_only
```

---

## 2. Five Specialized Agents

| Agent | Master(s) | Tools | Domain |
|---|---|---|---|
| `defect_agent` | PM.ai, ENG.ai | BigQuery, Firestore | Issue triage, severity scoring |
| `resource_agent` | PM.ai | BigQuery, Qdrant | Capacity, velocity, rebalancing |
| `requirement_agent` | PM.ai, ENG.ai | Neo4j graph, vector | Requirement details, impact blast radius |
| `test_agent` | PM.ai, ENG.ai | BigQuery, test store | Test coverage, results, gap analysis |
| `codefix_agent` | ENG.ai | Git, AST, patch tools | Code RCA, surgical patch, regression diff |

---

## 3. Recommended LangGraph Node Sequence

### Your proposed: `reason → observe → decide → execute → verify → validate → synthesize`

### Issues with this ordering:
- `observe` **before** `decide/execute` is backwards — you observe the **output** of an execution, not before it
- `verify` and `validate` overlap; one should be **automatic** (AI), one **human** (HITL)
- Missing: **Planner node** (decides which agent + creates the specialized prompt)
- Missing: **Cross-master handoff node**
- Missing: **Evidence evaluation / loop-back** decision
- Missing: **Visual generation** node

---

## 4. Recommended 9-Node LangGraph Architecture

```
START
  │
  ▼
┌──────────────────┐
│  1. REASON       │  Classify intent within master's capability map.
│                  │  Form hypothesis. Define required evidence dimensions.
│                  │  Load JSON stage prompt → system_prompt state.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. PLAN         │  Planner LLM call with evidence inventory.
│                  │  Decides: which agent? what specialized prompt?
│                  │  what is the exact evidence gap?
│                  │  Outputs: planner_decision { agent_id, agent_prompt, gap }
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. EXECUTE      │  Call selected specialized agent with its prompt.
│                  │  Agent runs LangChain ReAct loop internally.
│                  │  Returns EvidenceEnvelopes.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. OBSERVE      │  Ingest evidence from agent output.
│                  │  Cache to Firestore. Normalize EvidenceEnvelopes.
│                  │  Map evidence to required dimensions.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐   evidence      ┌──────────────┐
│  5. EVALUATE     │──insufficient──▶│  loop → PLAN │ (max 5 iterations)
│                  │                  └──────────────┘
│                  │──sufficient─────▶ continue
└────────┬─────────┘
         │
         ▼ (conditional)
┌──────────────────┐
│  6. CROSS_HANDOFF│  Only if master needs other master's domain evidence.
│                  │  Sends: full analysis + task description (text_only).
│  (OPTIONAL NODE) │  Receives: text_only response, appends to evidence.
│                  │  Rule: handoff is always text_only, non-recursive.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  7. SYNTHESIZE   │  LLM call: synthesize all evidence into structured answer.
│                  │  Uses synthesize_node prompt from JSON.
│                  │  Determines response_mode: text_only | text_and_image | image_only
│                  │  Produces structured JSON envelope.
└────────┬─────────┘
         │
         ▼ (conditional on response_mode)
┌──────────────────┐
│  8. VISUAL_GEN   │  Only if response_mode = text_and_image or image_only.
│                  │  Calls Imagen / Mermaid generator.
│                  │  Attaches image_url or fallback_mermaid to state.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  9. HUMAN_VALIDATE│  HITL checkpoint. Presents structured answer to human.
│  (HITL node)     │  Human can: APPROVE → END, REJECT → loop to REASON,
│                  │            REQUEST_MORE → loop to PLAN.
│                  │  Interrupt point in LangGraph (graph.interrupt_before).
└────────┬─────────┘
         │
         ▼
       [END]  →  Response to Streamlit
```

---

## 5. Node Summary Table

| # | Node | Type | Loops back to | Prompt source |
|---|---|---|---|---|
| 1 | **REASON** | LLM (intent classify + hypothesis) | — | `reason_node` from JSON |
| 2 | **PLAN** | LLM (planner decides agent + prompt) | — | `execute_action_node` from JSON |
| 3 | **EXECUTE** | Agent call | — | Agent-specific prompt (created by PLAN) |
| 4 | **OBSERVE** | Deterministic (ingest + normalize) | — | — |
| 5 | **EVALUATE** | Deterministic (sufficiency check) | → PLAN (if insufficient) | `23_analyze_outputs_system` |
| 6 | **CROSS_HANDOFF** | Async master call (conditional) | — | other master's prompt |
| 7 | **SYNTHESIZE** | LLM (full synthesis) | — | `synthesize_node` from JSON |
| 8 | **VISUAL_GEN** | Tool call (conditional) | — | Imagen prompt from skill |
| 9 | **HUMAN_VALIDATE** | HITL interrupt | → REASON or PLAN | — |

> **Your nodes `verify` + `validate`** → mapped to **EVALUATE** (auto-verify, deterministic) + **HUMAN_VALIDATE** (HITL). Keeping them separate is correct — just rename them this way.

---

## 6. Cross-Master Handoff Design

```
PM.ai MASTER                              ENG.ai MASTER
    │                                          │
    │  handoff_request {                       │
    │    from_master: "PM.ai",                 │
    │    to_master: "ENG.ai",                  │
    │    context_summary: str,     ──────────▶ │  runs its own
    │    analysis_done: dict,                  │  REASON→PLAN→EXECUTE→
    │    specific_task: str,                   │  OBSERVE→EVALUATE→
    │    response_mode: "text_only"            │  SYNTHESIZE loop
    │  }                                       │
    │                                          │
    │ ◀─────────────────────────── text_only ──┘
    │  (plain text, no image, no nested JSON)
    │
    appended to evidence_envelopes as
    EvidenceEnvelope(source_system="axiom_eng_master")
```

**Rules:**
- Handoff is always `text_only` — never recursive
- Handoff must include `context_summary` of what PM.ai already found
- Receiving master does NOT handoff back; it just returns text
- Max 1 cross-handoff per query (prevent infinite loops)

---

## 7. Response Modes

| Mode | When | Contains |
|---|---|---|
| `text_only` | Factual queries, cross-master handoffs, clarifications | JSON envelope with `sections[]` |
| `text_and_image` | Risk dashboards, timelines, defect flows, RCA diagrams | JSON + `visuals[]` array with image URLs |
| `image_only` | Explicit visualization requests | `visuals[]` only, minimal text caption |

**Decision rule in SYNTHESIZE node:**
```python
if "visualize" in query or "chart" in query or "diagram" in query:
    response_mode = "text_and_image"
elif capability in ["project_health", "root_cause_analysis", "sprint_replanning"]:
    response_mode = "text_and_image"   # default for these capabilities
else:
    response_mode = "text_only"
```

---

## 8. Updated `AxiomState` — Required Fields

```python
class AxiomState(TypedDict, total=False):

    # ── User Input & Session ──────────────────────────────────────────
    query: str
    session_id: str
    user_id: str

    # ── Router ───────────────────────────────────────────────────────
    intent_clarified: bool
    clarification: Dict[str, Any]
    target_master: Optional[str]          # "AXIOM-PM" | "AXIOM-ENG"
    target_capability: Optional[str]
    confidence_score: float
    system_prompt_router: str             # ← NEW: loaded from JSON

    # ── Cognitive Master: REASON node ────────────────────────────────
    resolved_intent: str                  # ← NEW: classified capability intent
    required_evidence_dimensions: List[str]  # ← NEW: what evidence is needed
    reasoning_hypothesis: str
    current_step: str
    system_prompt: str                    # ← stage-specific prompt from JSON

    # ── Cognitive Master: PLAN node ──────────────────────────────────
    planner_decision: Dict[str, Any]      # ← NEW: {agent_id, agent_prompt, gap, rationale}
    selected_skill: Optional[Dict[str, Any]]

    # ── Cognitive Master: EXECUTE node ───────────────────────────────
    delegated_agent: Optional[str]
    agent_task_input: Dict[str, Any]
    agent_prompt: str                     # ← NEW: specialized prompt created by PLAN

    # ── Cognitive Master: OBSERVE node ───────────────────────────────
    evidence_envelopes: List[Dict[str, Any]]
    memory_hit: bool

    # ── Cognitive Master: EVALUATE node ─────────────────────────────
    evaluation_passed: bool
    evaluation_iteration_count: int
    evaluation_checklist_results: Dict[str, bool]
    evidence_sufficiency: str             # ← NEW: "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT"
    material_gaps: List[str]              # ← NEW: unfilled evidence gaps

    # ── Cross-Master Handoff ─────────────────────────────────────────
    cross_handoff_needed: bool            # ← NEW
    cross_handoff_request: Dict[str, Any] # ← NEW: {to_master, context_summary, task}
    cross_handoff_response: str           # ← NEW: text_only response from other master
    cross_handoff_done: bool              # ← NEW: prevent recursive handoff

    # ── Guardrails & Validation ───────────────────────────────────────
    validation_status: str                # "PASSED" | "BLOCKED" | "GUARDRAIL_VIOLATION"
    guardrail_messages: List[str]

    # ── SYNTHESIZE node ───────────────────────────────────────────────
    response_mode: str                    # ← NEW: "text_only" | "text_and_image" | "image_only"
    synthesized_summary: str
    structured_answer: Dict[str, Any]

    # ── VISUAL_GEN node ───────────────────────────────────────────────
    visual_artifact: Dict[str, Any]

    # ── HUMAN_VALIDATE (HITL) ────────────────────────────────────────
    human_validation_required: bool       # ← NEW
    human_validation_result: str          # ← NEW: "APPROVED" | "REJECTED" | "REQUEST_MORE"
    human_feedback: str                   # ← NEW: human's text feedback
    hitl_loop_count: int                  # ← NEW: prevent infinite HITL loops

    # ── Final Output ──────────────────────────────────────────────────
    final_output_markdown: str
```

---

## 9. PLAN Node Design (The Planner)

This is the most important new node. It must:

1. Read `required_evidence_dimensions` from REASON node
2. Read `evidence_envelopes` already collected
3. Identify **the single most critical gap**
4. Select the **one specialist agent** that fills it
5. Create a **specialized, scoped prompt** for that agent
6. Write `planner_decision` into state

```python
# planner_decision schema
{
    "agent_id": "defect_agent",
    "gap": "Missing authoritative severity classification for GH-ISSUE-107",
    "agent_objective": "Retrieve severity, urgency, and leakage direction for GH-ISSUE-107",
    "agent_prompt": "You are the Defect Intelligence Agent. Your task: ...",
    "rationale": "defect_agent owns BigQuery issue records; no other agent can fill this gap",
    "expected_evidence_type": "github_issue_record",
    "stopping_condition": "severity and urgency fields present with quality_status=verified"
}
```

---

## 10. LangGraph Edge / Conditional Logic

```python
# After EVALUATE
def route_after_evaluate(state):
    if state["evaluation_passed"]:
        if state.get("cross_handoff_needed") and not state.get("cross_handoff_done"):
            return "cross_handoff"
        return "synthesize"
    if state["evaluation_iteration_count"] >= 5:
        return "synthesize"          # hit max iterations, synthesize conditionally
    return "plan"                    # loop back for another agent call

# After SYNTHESIZE
def route_after_synthesize(state):
    if state["response_mode"] in ("text_and_image", "image_only"):
        return "visual_gen"
    return "human_validate"

# After VISUAL_GEN
def route_after_visual(state):
    return "human_validate"

# After HUMAN_VALIDATE (HITL interrupt)
def route_after_hitl(state):
    result = state.get("human_validation_result", "APPROVED")
    if result == "APPROVED":
        return END
    if result == "REJECTED":
        return "reason"              # restart from reason with feedback
    if result == "REQUEST_MORE":
        if state.get("hitl_loop_count", 0) >= 2:
            return END               # safety cap
        return "plan"               # one more agent call
```

---

## 11. Streamlit Integration Points

```
User types query
    │
    ▼
streamlit_app.py
    │  calls run_axiom_orchestration(query, session_id, user_id)
    │
    ▼
graph.py → AxiomCognitiveRunner.run()
    │
    │  At HUMAN_VALIDATE node → interrupt
    │  streamlit renders structured_answer for human review
    │  human clicks APPROVE / REJECT / REQUEST_MORE
    │  sends human_validation_result back via graph.resume()
    │
    ▼
final_output_markdown rendered in streamlit
visual_artifact image_url embedded as st.image()
```

---

## 12. Implementation Priority Order

1. **Update `AxiomState`** — add all new fields (Section 8 above)
2. **Implement PLAN node** — the planner LLM call (Section 9)
3. **Add CROSS_HANDOFF node** — with text_only response rule
4. **Add HUMAN_VALIDATE node** — using `graph.interrupt_before("human_validate")`
5. **Update LangGraph edges** — conditional routing (Section 10)
6. **Update Streamlit** — render HITL checkpoint, handle approve/reject
7. **Wire response_mode** — into SYNTHESIZE and VISUAL_GEN nodes
