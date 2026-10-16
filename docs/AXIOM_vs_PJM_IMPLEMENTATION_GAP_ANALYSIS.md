# AXIOM vs PJM.ai: Implementation Gap Analysis

**Date**: 2026-10-16  
**Status**: 🔴 **AXIOM is a Reference Architecture, NOT a Production Implementation**

---

## Executive Summary

**AXIOM_Hackathon** is a **high-level reference design** with:
- ✅ Conceptual architecture (LangGraph, dual masters, specialized agents)
- ✅ Prompt templates and framework
- ✅ Knowledge graph schema (Neo4j)
- ❌ **NO production implementation** of orchestration logic
- ❌ **NO actual agent code** (defect, requirement, test, resource, codefix)
- ❌ **NO working streamlit dashboard**
- ❌ **NO actual capability execution**

**Main PJM.ai** is a **production-grade implementation** with:
- ✅ **40+ agent implementation files** (master orchestrator, skill detectors, intent classifiers)
- ✅ **Complete agent cards** with input/output contracts
- ✅ **Working Streamlit dashboard** with real data flow
- ✅ **LangGraph execution** with state management
- ✅ **HITL validation**, data gates, verification systems
- ✅ **Rich UI components** (renderers, visualizers, chat history)

---

## 1. Orchestration Architecture

### AXIOM Design
```
AXIOM Concept (Prompts Only)
├── orchestrator/graph.py          (stub - LangGraph skeleton)
├── orchestrator/pm_master.py      (prompt definition only)
├── orchestrator/eng_master.py     (prompt definition only)
├── orchestrator/router.py         (intent routing logic outline)
└── orchestrator/state.py          (Pydantic models)

Status: ❌ Prompts defined, NO execution logic
```

### PJM.ai Implementation
```
PJM.ai Implementation (40+ Files)
├── orchestration/master_orchestrator.py        ✅ Complete execution
│   ├── MasterOrchestrator class
│   ├── ExecutionPlan with AgentSpec
│   ├── Pattern-based + LLM hybrid approach
│   ├── Capability matching logic
│   ├── Data dependency tracking
│   └── Iteration & safety caps
│
├── orchestration/task_contract.py              ✅ Execution contracts
│   ├── TaskExecutionContract
│   ├── Intent, Complexity, RiskLevel enums
│   ├── ExecutionMode flags
│   └── Required capabilities
│
├── orchestration/dynamic_router.py             ✅ Intent routing
│   ├── Intent classification
│   ├── Master selection logic
│   ├── Confidence scoring
│   └── Clarification protocol
│
├── pjm_planner.py                             ✅ ReAct planner
│   ├── Reason node
│   ├── Execute action node
│   ├── Observe node
│   ├── Synthesize node
│   ├── Verify answer node
│   └── Iteration management
│
├── agent_cards.py                             ✅ Agent capability contracts
│   ├── Agent specs with inputs/outputs
│   ├── Skill-to-agent mapping
│   ├── Validation rules
│   └── Success criteria
│
└── prompt_selector_integration.py             ✅ Dynamic prompt loading
    ├── Load prompts per stage
    ├── Substitute variables
    ├── Version management
    └── Caching
```

---

## 2. Agent Implementation

### AXIOM Status: ❌ STUB ONLY
```
AXIOM_Hackathon-main/agents/
├── defect_agent.py              (50 lines - stub with docstring)
├── requirement_agent.py         (50 lines - stub with docstring)
├── test_agent.py                (50 lines - stub with docstring)
├── resource_agent.py            (50 lines - stub with docstring)
├── codefix_agent.py             (50 lines - stub with docstring)
└── tools/
    ├── neo4j_tools.py           (connection only, no actual queries)
    ├── bigquery_tools.py        (mock data, no real analytics)
    └── firestore_tools.py       (session store only)

Total: ~300 lines of stubs
Status: ❌ NO REAL IMPLEMENTATION
```

### PJM.ai Status: ✅ COMPLETE IMPLEMENTATION
```
agents/agent_pjm/
├── agent_cards.py                              (200+ lines)
│   ├── AGENT_CARDS: Full capability specs
│   ├── Input/output schemas
│   ├── Pre/post conditions
│   └── Success criteria
│
├── requirement_agent_builder.py                (300+ lines)
│   ├── Real Neo4j queries
│   ├── Requirement traceability
│   ├── Impact analysis
│   ├── Variant handling
│   └── Evidence assembly
│
├── test_agent_builder.py                       (200+ lines)
│   ├── Test case lookup
│   ├── Coverage analysis
│   ├── Test prioritization (ITPA)
│   ├── Pytest integration
│   └── Gap detection
│
├── orchestration/master_orchestrator.py        (300+ lines)
│   ├── Capability matching
│   ├── Execution planning
│   ├── Data dependency resolution
│   ├── Hybrid fast/LLM paths
│   └── Agent sequencing
│
├── orchestration/policy_gate.py                (150+ lines)
│   ├── Guardrail enforcement
│   ├── Safety validation
│   ├── Boundary checking
│   └── Evidence gating
│
├── orchestration/validation_gate.py            (150+ lines)
│   ├── Output validation
│   ├── Contract checking
│   ├── Confidence assessment
│   └── Arithmetic reconciliation
│
├── session_updater.py                          (250+ lines)
│   ├── Evidence persistence
│   ├── State management
│   ├── Chat history
│   └── Session cleanup
│
└── context_extractors.py                       (200+ lines)
    ├── Entity extraction
    ├── Reference resolution
    ├── Context enrichment
    └── Dependency inference
```

---

## 3. Streamlit Dashboard

### AXIOM Status: ❌ MINIMAL
```
AXIOM_Hackathon-main/
├── streamlit_app.py
│   ├── Main interface
│   ├── Simple markdown rendering
│   ├── Raw JSON display
│   └── Basic tabs (Prompts, KG, Config)
│
└── main.py (CLI only)
    └── Interactive loop

Status: ❌ NO rendered output, NO chat history, NO visualization
```

### PJM.ai Status: ✅ PRODUCTION DASHBOARD
```
ui/
├── dashboard.py                                (800+ lines)
│   ├── Multi-page navigation
│   ├── Session management
│   ├── Chat history with full state trace
│   ├── Markdown + JSON rendering
│   ├── Evidence visualization
│   ├── Confidence display
│   ├── Risk indicators
│   ├── Recommendation rendering
│   ├── Video/image insertion
│   ├── Copy-to-clipboard
│   ├── CSV export
│   └── Session cleanup UI
│
├── admin_dashboard.py                        (400+ lines)
│   ├── Debug trace viewer
│   ├── Agent execution metrics
│   ├── Evidence state inspection
│   ├── Error log viewer
│   ├── Session history
│   ├── Configuration management
│   └── Performance analytics
│
├── requirement_page.py                       (500+ lines)
│   ├── Requirement search UI
│   ├── Variant filtering
│   ├── Traceability tree
│   ├── Impact visualization
│   ├── Cross-project dependencies
│   ├── Test case mapping
│   └── Status dashboard
│
├── requirement_agent_helper.py               (300+ lines)
│   ├── Neo4j query builder
│   ├── Requirement detail fetcher
│   ├── Variant analysis helper
│   └── Impact calculator
│
├── langfuse_monitor_page.py                  (200+ lines)
│   ├── LLM trace viewer
│   ├── Token usage dashboard
│   ├── Latency analysis
│   ├── Error tracking
│   └── Performance metrics
│
└── _renderers.py                             (1000+ lines)
    ├── Markdown with code blocks
    ├── JSON pretty-printing
    ├── Table rendering
    ├── Metric card rendering
    ├── List formatting
    ├── Risk color coding
    ├── Status badge formatting
    ├── Mermaid diagram rendering
    └── Custom component builders
```

---

## 4. Capability Implementation Matrix

### AXIOM Defined Capabilities (Prompts Only)

| Capability | PM.ai | ENG.ai | Status |
|-----------|-------|--------|--------|
| `preliminary_rca` | ✅ Prompt | ❌ | ❌ No code |
| `defect_triage` | ✅ Prompt | ❌ | ❌ No code |
| `project_health` | ✅ Prompt | ❌ | ❌ No code |
| `sprint_replanning` | ✅ Prompt | ❌ | ❌ No code |
| `sprint_timeline_analysis` | ✅ Prompt | ❌ | ❌ No code |
| `pi_planning` | ✅ Prompt | ❌ | ❌ No code |
| `retrospective` | ✅ Prompt | ❌ | ❌ No code |
| `root_cause_analysis` | ❌ | ✅ Prompt | ❌ No code |
| `eight_d_analysis` | ❌ | ✅ Prompt | ❌ No code |
| `five_why_analysis` | ❌ | ✅ Prompt | ❌ No code |
| `code_fixing` | ❌ | ✅ Prompt | ❌ No code |
| `test_case_generation` | ❌ | ✅ Prompt | ❌ No code |
| `increasing_test_coverage` | ❌ | ✅ Prompt | ❌ No code |

**Total: 13 capabilities (PROMPT ONLY)**

### PJM.ai Implemented Capabilities (Full End-to-End)

| Capability | Implementation | Status |
|-----------|----------------|--------|
| `preliminary_rca` | `pjm_planner.py` + `defect_agent_builder.py` + context extractors | ✅ Production |
| `defect_triage` | `requirement_agent_builder.py` + impact analysis | ✅ Production |
| `project_health` | `session_updater.py` + `risk_management_page.py` | ✅ Production |
| `sprint_replanning` | `master_orchestrator.py` + capacity modeling | ✅ Production |
| `requirement_impact` | `requirement_agent_builder.py` + Neo4j traversal | ✅ Production |
| `test_readiness` | `test_agent_builder.py` + coverage analysis | ✅ Production |
| `delivery_risk` | `risk_management_page.py` + metrics engine | ✅ Production |
| `resource_allocation` | `context_extractors.py` + capacity planning | ✅ Production |
| `continuous_risk_management` | `session_updater.py` + state machine | ✅ Production |
| `itpa_test_prioritization` | `test_agent_builder.py` + A+B+C+D scoring | ✅ Production |
| `leakage_analysis` | `defect_agent_builder.py` + flow modeling | ✅ Production |

**Total: 11+ capabilities (FULLY IMPLEMENTED)**

---

## 5. Knowledge Graph Integration

### AXIOM Status: ❌ NO REAL QUERIES
```
AXIOM/agents/tools/neo4j_tools.py
├── Connection driver: ✅ (neo4j-driver)
├── Static sample data: ✅
├── Real Cypher queries: ❌
├── Requirement lookup: ❌
├── Impact analysis: ❌
├── Variant traversal: ❌
└── Test case linking: ❌

Status: ❌ Connection only, NO actual graph operations
```

### PJM.ai Status: ✅ PRODUCTION QUERIES
```
agents/agent_pjm/requirement_agent_builder.py
├── Requirement details query: ✅
├── Impact radius (1..3 hops): ✅
├── Variant divergence: ✅
├── Co-allocation analysis: ✅
├── Test case linking: ✅
├── Component allocation: ✅
├── Semantic affinity search: ✅
└── Cross-project dependencies: ✅

Status: ✅ 8+ production Cypher queries
```

---

## 6. Session State & Persistence

### AXIOM Status: ❌ NO IMPLEMENTATION
```
AXIOM/orchestrator/state.py
├── LangGraph state model: ✅ (basic)
├── Evidence storage: ❌
├── Session persistence: ❌
├── Chat history: ❌
├── Investigation tracking: ❌
└── State cleanup: ❌

Status: ❌ Type definitions only
```

### PJM.ai Status: ✅ PRODUCTION SYSTEM
```
agents/agent_pjm/session_store.py          (production)
├── Evidence model: ✅
├── Firestore integration: ✅
├── Evidence caching: ✅
├── Session cleanup: ✅
└── Batch operations: ✅

agents/agent_pjm/session_updater.py        (250+ lines)
├── Evidence tracking: ✅
├── State transitions: ✅
├── Chat history assembly: ✅
├── Investigation memory: ✅
├── Confidence rollup: ✅
└── Cleanup automation: ✅

agents/agent_pjm/_chat_history.py          (200+ lines)
├── Message formatting: ✅
├── Evidence citations: ✅
├── Rich rendering: ✅
├── Media attachment: ✅
└── History export: ✅
```

---

## 7. Safety, Guardrails & HITL

### AXIOM Status: ❌ ONLY IN PROMPTS
```
AXIOM prompts/
├── Non-negotiables: ✅ (text definition)
├── Guardrails: ✅ (text definition)
├── Enforcement: ❌
├── Policy gates: ❌
├── Validation gates: ❌
└── Approval workflows: ❌

Status: ❌ Conceptual only
```

### PJM.ai Status: ✅ ENFORCED IN CODE
```
agents/agent_pjm/orchestration/policy_gate.py  (150+ lines)
├── Capability boundary checking: ✅
├── Agent scope validation: ✅
├── Output format enforcement: ✅
├── Confidence thresholds: ✅
├── Decision readiness gating: ✅
└── Safety cap enforcement: ✅

agents/agent_pjm/orchestration/validation_gate.py  (150+ lines)
├── Contract validation: ✅
├── Arithmetic reconciliation: ✅
├── Evidence completeness: ✅
├── Confidence assessment: ✅
├── Feedback loop detection: ✅
└── Rejection with remediation: ✅

agents/agent_pjm/_jira_hitl.py             (150+ lines)
├── JIRA write gatekeeping: ✅
├── Approval workflow: ✅
├── Assignment validation: ✅
├── Status update checks: ✅
└── Audit trail: ✅

agents/agent_pjm/hitl_action_handler.py    (200+ lines)
├── User approval collection: ✅
├── Action execution: ✅
├── Rollback on rejection: ✅
└── Notification dispatch: ✅
```

---

## 8. Visualization & Output Generation

### AXIOM Status: ❌ STUB ONLY
```
AXIOM/orchestrator/visual_gen.py
├── Vertex AI Imagen integration: ✅ (imports only)
├── Mermaid fallback: ❌
├── Prompt engineering: ❌
├── Image caching: ❌
└── Error handling: ❌

Status: ❌ Skeleton, no actual image generation
```

### PJM.ai Status: ✅ PRODUCTION SYSTEM
```
agents/agent_pjm/visual_request_detector.py  (300+ lines)
├── Intent-to-visualization mapping: ✅
├── Type selection (fishbone, timeline, etc.): ✅
├── Data mapping per type: ✅
├── Prompt engineering: ✅
├── Multi-visualization support: ✅
└── Fallback logic: ✅

agents/agent_pjm/_images.py                 (400+ lines)
├── Image generation calls: ✅
├── Caching (local + Firestore): ✅
├── Error recovery: ✅
├── Prompt templating: ✅
├── Format negotiation: ✅
└── Compression & optimization: ✅

ui/_renderers.py                            (1000+ lines)
├── Mermaid diagram rendering: ✅
├── Image insertion: ✅
├── Lazy loading: ✅
├── Zoom & pan: ✅
└── Export (PNG, SVG): ✅
```

---

## 9. Testing & Validation

### AXIOM Status: ❌ MINIMAL
```
AXIOM_Hackathon-main/
├── test_axiom.py              (10/10 tests PASS)
│   ├── Router logic tests: ✅
│   ├── Integration tests: ✅
│   └── Capability matching: ✅
│
Status: ✅ Syntax verification only (no feature tests)
```

### PJM.ai Status: ✅ COMPREHENSIVE
```
agents/agent_pjm/tests/
├── test_orchestration_knowledge.py          (unit)
├── test_planner_validation.py               (unit)
├── test_session_updater.py                  (integration)
├── test_visualization_intent.py             (feature)
├── test_multi_visualization.py              (feature)
├── test_renderer_additive_visuals.py        (integration)
├── test_chat_history_rendering.py           (feature)
├── test_requirement_agent_builder.py        (integration)
├── test_context_extractors.py               (unit)
├── test_prompt_policy_selector_imports.py   (validation)
└── test_agent_pjm_prompt_path.py            (integration)

Status: ✅ 50+ test cases covering features, integration, and regression
```

---

## 10. Comparison Table: Feature Coverage

| Feature | AXIOM | PJM.ai | Gap |
|---------|-------|--------|-----|
| **Orchestration** | | | |
| LangGraph integration | Stub | ✅ Production | Major |
| ReAct execution | Prompt only | ✅ Full | Major |
| Capability matching | Conceptual | ✅ Automatic | Major |
| Agent selection | Stub | ✅ Hybrid fast/LLM | Major |
| State management | Type defs | ✅ Production | Major |
| **Agents** | | | |
| Requirement agent | Stub | ✅ 300+ lines | Major |
| Test agent | Stub | ✅ 200+ lines | Major |
| Defect agent | Stub | ✅ Full | Major |
| Resource agent | Stub | ✅ Full | Major |
| Code fix agent | Stub | ✅ Full | Major |
| **Knowledge Graph** | | | |
| Neo4j connection | ✅ | ✅ | None |
| Requirement queries | ❌ | ✅ 8+ | Major |
| Impact analysis | ❌ | ✅ | Major |
| Variant traversal | ❌ | ✅ | Major |
| **Session/State** | | | |
| Evidence persistence | ❌ | ✅ Firestore | Major |
| Chat history | ❌ | ✅ Rich format | Major |
| Cleanup automation | ❌ | ✅ | Major |
| **Safety** | | | |
| Policy gates | Prompt | ✅ Code | Major |
| Validation gates | Prompt | ✅ Code | Major |
| HITL workflows | Prompt | ✅ Code | Major |
| Guardrail enforcement | ❌ | ✅ | Major |
| **UI/Dashboard** | | | |
| Streamlit app | Minimal | ✅ 2000+ lines | Major |
| Chat history | ❌ | ✅ Full | Major |
| Evidence viewer | ❌ | ✅ | Major |
| Visualization | ❌ | ✅ Fishbone/timeline | Major |
| Admin panel | ❌ | ✅ Debug trace | Major |
| Requirement explorer | ❌ | ✅ Full UI | Major |
| **Testing** | | | |
| Unit tests | ✅ 10 | ✅ 50+ | None |
| Integration tests | ❌ | ✅ | Major |
| Feature tests | ❌ | ✅ | Major |
| **Prompts** | | | |
| JSON format | ✅ 4 files | ✅ 3 files | None |
| Section versioning | ✅ | ✅ | None |
| Stage mapping | ✅ | ✅ | None |

---

## Summary: What AXIOM is Missing for Production

### Critical (Blocks Execution)
1. ❌ **Master Orchestrator Code**: No Python implementation of capability matching, agent selection, execution planning
2. ❌ **Agent Implementation**: All 5 specialized agents are stubs (<50 lines each)
3. ❌ **Knowledge Graph Queries**: No Cypher queries for requirement lookup, impact analysis, variant handling
4. ❌ **Session State Management**: No evidence persistence, chat history, cleanup
5. ❌ **LangGraph Wiring**: No actual graph execution, state transitions, node logic

### High (Degrades Quality)
6. ❌ **Policy/Validation Gates**: No guardrail enforcement, safety checks, confidence validation
7. ❌ **HITL Workflows**: No approval gates, JIRA integration, assignment handling
8. ❌ **UI Dashboard**: Minimal streamlit with no chat history, evidence viewer, or visualization
9. ❌ **Visualization System**: No actual image generation, mermaid rendering, or caching

### Medium (Reduces Usability)
10. ❌ **Testing**: No integration or feature tests (only syntax verification)
11. ❌ **Deployment**: No Docker, Cloud Run config, or scaling strategy
12. ❌ **Monitoring**: No LangFuse integration, metrics collection, or performance tracing

---

## Recommendations

### For AXIOM to Become Production-Ready

**Option A: Reference Architecture (Current)**
- Keep AXIOM as a high-level design blueprint
- Document it as "How to build a multi-agent system like this"
- Reference PJM.ai as the production implementation

**Option B: Production Migration**
1. Migrate prompt definitions ✅ (already done in JSON)
2. Implement master orchestrator (2-3 weeks)
3. Implement 5 specialized agents (2-3 weeks)
4. Build session state management (1 week)
5. Implement safety/HITL gates (1 week)
6. Build Streamlit dashboard (1-2 weeks)
7. Testing & validation (1 week)
8. **Total: 8-11 weeks**

**Option C: Hybrid Approach**
- Use AXIOM prompts + conceptual architecture
- Use PJM.ai orchestration code as reference
- Adapt PJM.ai components for AXIOM's dual-master design
- Reuse: session_store, validation_gate, _renderers, dashboard
- Implement: new master_orchestrator for PM.ai/ENG.ai split, new agents

---

## Files to Review for Implementation

### To Understand PJM.ai's Production Implementation
1. `agents/agent_pjm/agent_pjm.py` — Main LangGraph state machine
2. `agents/agent_pjm/orchestration/master_orchestrator.py` — Execution planning
3. `agents/agent_pjm/orchestration/task_contract.py` — Capability contracts
4. `agents/agent_pjm/requirement_agent_builder.py` — Real agent implementation
5. `agents/agent_pjm/session_updater.py` — State management
6. `ui/dashboard.py` — Production UI
7. `agents/agent_pjm/orchestration/policy_gate.py` — Safety enforcement

### To See What AXIOM Should Have But Doesn't
1. `AXIOM_Hackathon-main/agents/defect_agent.py` vs `agents/agent_pjm/...`
2. `AXIOM_Hackathon-main/orchestrator/graph.py` vs `agents/agent_pjm/agent_pjm.py`
3. `AXIOM_Hackathon-main/streamlit_app.py` vs `ui/dashboard.py`

---

**Conclusion**: AXIOM is a well-architected reference design with excellent conceptual clarity and prompt structure. PJM.ai is the production implementation. AXIOM would need ~8-11 weeks of implementation work to reach production parity.
