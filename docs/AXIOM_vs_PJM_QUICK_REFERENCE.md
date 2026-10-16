# AXIOM vs PJM.ai: Quick Reference Card

## One-Line Summary
🔵 **AXIOM** = High-level reference architecture (prompts + conceptual design)  
🟢 **PJM.ai** = Production implementation (40+ files, 5000+ lines of code)

---

## Architecture Comparison

### AXIOM (Hackathon Reference)
```
┌─────────────────────────────────────┐
│ Prompts + Conceptual Architecture   │
├─────────────────────────────────────┤
│ ✅ Dual masters (PM.ai + ENG.ai)    │
│ ✅ Intent router                    │
│ ✅ Knowledge graph schema           │
│ ✅ Prompt templates (JSON)          │
│ ❌ No orchestration code            │
│ ❌ No working agents                │
│ ❌ No real UI                       │
│ ❌ No execution                     │
└─────────────────────────────────────┘
```

### PJM.ai (Production)
```
┌─────────────────────────────────────┐
│ Full Implementation Stack           │
├─────────────────────────────────────┤
│ ✅ Master orchestrator (300+ lines) │
│ ✅ 5 working agents (1000+ lines)   │
│ ✅ Session state management         │
│ ✅ Safety & HITL gates              │
│ ✅ Streamlit dashboard (2000+ lines)│
│ ✅ Knowledge graph queries          │
│ ✅ 50+ unit/integration tests       │
│ ✅ Production deployment            │
└─────────────────────────────────────┘
```

---

## Code Footprint

| Component | AXIOM | PJM.ai |
|-----------|-------|--------|
| **Orchestration** | 100 lines (stub) | 1000+ lines |
| **Agents** | 300 lines (5 stubs) | 2000+ lines (full) |
| **UI** | 200 lines (minimal) | 2000+ lines (production) |
| **Knowledge Graph** | 100 lines (connection only) | 500+ lines (8+ queries) |
| **State Management** | 50 lines (types) | 800+ lines (production) |
| **Safety/HITL** | 0 lines (prompts only) | 500+ lines (enforced) |
| **Testing** | 10 tests (syntax) | 50+ tests (comprehensive) |
| **Total** | ~1000 lines | ~8000 lines |

---

## Key Missing Components in AXIOM

### 1️⃣ **Orchestration Engine** (CRITICAL)
```
AXIOM: prompts/axiom_pm_master_v3.json (prompts only)
PJM.ai: agents/agent_pjm/orchestration/master_orchestrator.py (300+ lines)

Gap: No capability matching, agent selection, execution planning logic
```

### 2️⃣ **Agent Implementation** (CRITICAL)
```
AXIOM Agents:
├── defect_agent.py (50 lines - stub)
├── requirement_agent.py (50 lines - stub)
├── test_agent.py (50 lines - stub)
├── resource_agent.py (50 lines - stub)
└── codefix_agent.py (50 lines - stub)

PJM.ai Agents:
├── requirement_agent_builder.py (300+ lines - full)
├── test_agent_builder.py (200+ lines - full)
├── (defect/resource in orchestration)
└── Complete with Neo4j, BigQuery integration

Gap: AXIOM agents are docstring stubs, PJM has real implementations
```

### 3️⃣ **Knowledge Graph Queries** (CRITICAL)
```
AXIOM: neo4j_tools.py
├── Connection: ✅
├── Sample data: ✅
├── Real queries: ❌ (NO Cypher)

PJM.ai: requirement_agent_builder.py
├── Requirement details: ✅
├── Impact radius (1-3 hops): ✅
├── Variant traversal: ✅
├── Component allocation: ✅
└── 8+ production queries

Gap: AXIOM has connection only, no actual graph operations
```

### 4️⃣ **Session State & Persistence** (HIGH)
```
AXIOM: orchestrator/state.py
├── Type definitions: ✅
├── Evidence storage: ❌
├── Chat history: ❌
├── Cleanup: ❌

PJM.ai: agent_pjm/
├── session_store.py (production Firestore)
├── session_updater.py (250+ lines state machine)
├── _chat_history.py (200+ lines rendering)
└── Evidence caching, cleanup automation

Gap: AXIOM only defines types, PJM has full persistence layer
```

### 5️⃣ **Safety & Guardrails** (HIGH)
```
AXIOM: prompts only
├── Non-negotiables: ✅ (text)
├── Guardrails: ✅ (text)
├── Enforcement: ❌ (no code)

PJM.ai: orchestration/
├── policy_gate.py (150+ lines) - enforces boundaries
├── validation_gate.py (150+ lines) - validates outputs
├── hitl_action_handler.py (200+ lines) - JIRA approval workflow
└── _jira_hitl.py (150+ lines) - audit trail

Gap: AXIOM conceptual only, PJM enforces in code
```

### 6️⃣ **Streamlit Dashboard** (HIGH)
```
AXIOM: streamlit_app.py
├── Main UI: ✅ (basic)
├── Chat history: ❌
├── Evidence viewer: ❌
├── Visualization: ❌

PJM.ai: ui/
├── dashboard.py (800+ lines) - full chat + evidence
├── admin_dashboard.py (400+ lines) - debug traces
├── requirement_page.py (500+ lines) - KG explorer
├── langfuse_monitor_page.py (200+ lines) - LLM metrics
├── _renderers.py (1000+ lines) - rich output
└── Rich markdown/JSON/table/image rendering

Gap: AXIOM minimal, PJM is production dashboard
```

---

## Capability Coverage

### AXIOM Capabilities (Prompts Only)
```
PM.ai:
  • preliminary_rca ✅ prompt, ❌ no code
  • defect_triage ✅ prompt, ❌ no code
  • project_health ✅ prompt, ❌ no code
  • sprint_replanning ✅ prompt, ❌ no code
  • sprint_timeline_analysis ✅ prompt, ❌ no code
  • pi_planning ✅ prompt, ❌ no code
  • retrospective ✅ prompt, ❌ no code

ENG.ai:
  • root_cause_analysis ✅ prompt, ❌ no code
  • eight_d_analysis ✅ prompt, ❌ no code
  • five_why_analysis ✅ prompt, ❌ no code
  • code_fixing ✅ prompt, ❌ no code
  • test_case_generation ✅ prompt, ❌ no code
  • increasing_test_coverage ✅ prompt, ❌ no code

Status: 13 capabilities DEFINED but NOT IMPLEMENTED
```

### PJM.ai Capabilities (Fully Implemented)
```
✅ preliminary_rca (pjm_planner + defect_agent)
✅ defect_triage (requirement_agent + impact)
✅ project_health (risk_management + metrics)
✅ sprint_replanning (master_orchestrator + capacity)
✅ requirement_impact (requirement_agent + traversal)
✅ test_readiness (test_agent + coverage)
✅ delivery_risk (risk_management + visualization)
✅ resource_allocation (capacity modeling)
✅ continuous_risk_management (state machine)
✅ itpa_test_prioritization (A+B+C+D scoring)
✅ leakage_analysis (defect flow modeling)

Status: 11+ capabilities FULLY WORKING
```

---

## Execution Model Comparison

### AXIOM
```
Defined but not implemented:
  User Query
    ↓
  (Router) → Route to PM.ai or ENG.ai  [PROMPTS ONLY]
    ↓
  (Master) → Plan execution  [PROMPTS ONLY]
    ↓
  (Agents) → Execute  [STUBS - NO REAL CODE]
    ↓
  (Dashboard) → Display  [MINIMAL UI]
    ↓
  No actual output
```

### PJM.ai
```
Fully implemented:
  User Query
    ↓
  (Intent Classifier) → Analyze intent [CODE: 200+ lines]
    ↓
  (Master Orchestrator) → Build execution plan [CODE: 300+ lines]
    ↓
  (Agent Selector) → Match capabilities [CODE: 150+ lines]
    ↓
  (Specialized Agents) → Execute [CODE: 2000+ lines]
    ↓
  (Session Updater) → Persist evidence [CODE: 250+ lines]
    ↓
  (Dashboard) → Render with chat history [CODE: 2000+ lines]
    ↓
  User sees rich output: text + evidence + visualization
```

---

## What AXIOM Would Need to Reach Production

### Phase 1: Orchestration (2-3 weeks)
```
❌ → ✅ master_orchestrator.py
     ├── Capability matching
     ├── Agent selection logic
     ├── Execution planning
     └── Data dependency tracking
     
❌ → ✅ intent_classifier.py
     └── Intent detection from user query
     
❌ → ✅ LangGraph wiring
     ├── State transitions
     ├── Iteration management
     └── Node execution
```

### Phase 2: Agent Implementations (2-3 weeks)
```
❌ → ✅ Full defect_agent.py (200+ lines)
❌ → ✅ Full requirement_agent.py (300+ lines)
❌ → ✅ Full test_agent.py (200+ lines)
❌ → ✅ Full resource_agent.py (150+ lines)
❌ → ✅ Full codefix_agent.py (200+ lines)

Plus Neo4j, BigQuery integrations
```

### Phase 3: Safety & State (2 weeks)
```
❌ → ✅ policy_gate.py (guardrail enforcement)
❌ → ✅ validation_gate.py (output validation)
❌ → ✅ session_store.py (evidence persistence)
❌ → ✅ hitl_action_handler.py (JIRA workflows)
```

### Phase 4: UI & Visualization (2 weeks)
```
❌ → ✅ Rich Streamlit dashboard (800+ lines)
❌ → ✅ Chat history rendering (200+ lines)
❌ → ✅ Evidence viewer (300+ lines)
❌ → ✅ Visualization system (400+ lines)
```

### Phase 5: Testing & Deployment (1-2 weeks)
```
❌ → ✅ 50+ unit/integration tests
❌ → ✅ Docker image & Cloud Run config
❌ → ✅ Monitoring & alerting
```

**Total effort: 8-11 weeks** for one engineer or 2-3 weeks for a team

---

## Recommendation

### Use AXIOM As:
```
✅ Reference architecture documentation
✅ Prompt framework (already migrated to JSON)
✅ Design blueprint for dual-master systems
✅ Conceptual validation of multi-agent pattern
```

### Use PJM.ai As:
```
✅ Production implementation reference
✅ Source for reusable components (session_store, dashboard, gates)
✅ Testing strategy and patterns
✅ Deployment approach (Streamlit + FastAPI + Cloud Run)
```

### To Make AXIOM Production-Ready:
```
Option A: Port PJM.ai's implementation to AXIOM's architecture
Option B: Treat AXIOM as reference, use PJM.ai for production
Option C: Merge best of both (AXIOM prompts + PJM.ai orchestration)
```

---

## Files to Study

**To understand what's missing in AXIOM:**
1. `agents/agent_pjm/agent_pjm.py` — Real LangGraph state machine
2. `agents/agent_pjm/orchestration/master_orchestrator.py` — Execution planning
3. `agents/agent_pjm/requirement_agent_builder.py` — Real agent implementation

**To see AXIOM's stubs:**
1. `AXIOM_Hackathon-main/agents/defect_agent.py` — Compare with PJM.ai version
2. `AXIOM_Hackathon-main/orchestrator/pm_master.py` — Prompts only, no execution
3. `AXIOM_Hackathon-main/streamlit_app.py` — Minimal vs PJM.ai's 800+ line dashboard

---

**Status**: AXIOM is well-designed but incomplete. PJM.ai is production-ready. 🚀
