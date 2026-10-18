# AXIOM 9-Node Architecture — Flow Diagrams

## 1. Complete 9-Node StateGraph Flow (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AXIOM UNIFIED ORCHESTRATOR                          │
│                  Single LangGraph for PM.ai & ENG.ai                        │
└─────────────────────────────────────────────────────────────────────────────┘

                                    START
                                      │
                                      ▼
                          ┌───────────────────┐
                          │   ROUTER NODE     │
                          │ (Intent Detection)│
                          └───────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │ target_master = PM.ai or ENG.ai    │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                    ╔═════════════════════════════════╗
                    ║  COGNITIVE REASONING LOOP       ║
                    ║  (Max 5 iterations)             ║
                    ║  Iteration 1/5 ... 5/5          ║
                    ╚═════════════════════════════════╝
                                      │
                                      ▼
                          ┌───────────────────┐
                    ┌────→│  REASON NODE      │
                    │     │ (LLM Analysis)    │
                    │     └───────────────────┘
                    │                │
                    │                ▼
                    │     ┌───────────────────┐
                    │     │ MEMORY RETRIEVAL  │
                    │     │ (Check Firestore) │
                    │     └───────────────────┘
                    │                │
                    │         ┌──────┴──────┐
                    │         │ HIT?        │
                    │      Yes│    │No
                    │         ▼    │
                    │    (EVALUATE) ▼
                    │             ┌───────────────────┐
                    │             │  PLAN NODE        │
                    │             │ (Skill+Agent SEL) │
                    │             │ Load Registries   │
                    │             │ LLM decides:      │
                    │             │ • Skill needed    │
                    │             │ • Agent to call   │
                    │             │ • Agent prompt    │
                    │             └───────────────────┘
                    │                     │
                    │                     ▼
                    │             ┌───────────────────┐
                    │             │ EXECUTE NODE      │
                    │             │ (Universal Invok) │
                    │             │                   │
                    │             │ agent_map = {     │
                    │             │  "defect_agent"   │
                    │             │  "requirement_ag" │
                    │             │  "test_agent"     │
                    │             │  "codefix_agent"  │
                    │             │  ...              │
                    │             │ }                 │
                    │             │                   │
                    │             │ Call agent with   │
                    │             │ planner's prompt  │
                    │             └───────────────────┘
                    │                     │
                    │                     ▼
                    │             ┌───────────────────┐
                    │             │ OBSERVE NODE      │
                    │             │ (Evidence Ingest) │
                    │             │ Cache to Firestore│
                    │             └───────────────────┘
                    │                     │
                    │                     ▼
                    │             ┌───────────────────┐
                    │             │ EVALUATE NODE     │
                    │             │ (Sufficiency?)    │
                    │             └───────────────────┘
                    │                     │
                    │         ┌───────────┴────────────┐
                    │         │ Sufficient?            │
                    │      No │            │ Yes
                    │         │            │
                    └─────────┘            ▼
                              ┌───────────────────┐
                              │CROSS_HANDOFF NODE │
                              │ (Optional HO)     │
                              └───────────────────┘
                                        │
                                        ▼
                              ┌───────────────────┐
                              │ SYNTHESIZE NODE   │
                              │ (Consolidate Ev)  │
                              │ Exec Response     │
                              └───────────────────┘
                                        │
                                        ▼
                              ┌───────────────────┐
                              │ VISUAL_GEN NODE   │
                              │ (Conditional)     │
                              │ Create diagrams   │
                              └───────────────────┘
                                        │
                                        ▼
                              ╔═════════════════════╗
                              ║ HUMAN_VALIDATE NODE ║
                              ║ (HITL Checkpoint)   ║
                              ╚═════════════════════╝
                                        │
                    ┌───────────────────┼───────────────────┐
                    │ Action?           │                   │
              APPROVED│          REQUEST_MORE     REJECTED
                    │                   │                   │
                    ▼                   ▼                   ▼
              ┌──────────┐         ┌──────────┐       ┌──────────┐
              │Deliver   │         │Re-execute│       │Loop back │
              │Response  │         │with      │       │to REASON │
              │(Final)   │         │feedback  │       │w/ reject │
              └──────────┘         └──────────┘       └──────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                                        ▼
                                      END
```

---

## 2. Core Reasoning Loop (Detailed)

```
╔════════════════════════════════════════════════════════════════╗
║            REASON → PLAN → EXECUTE → OBSERVE → EVALUATE       ║
║                                                                ║
║  This 5-step loop runs up to 5 times until evidence sufficient║
╚════════════════════════════════════════════════════════════════╝

ITERATION 1:
  ┌──────────┐
  │ REASON   │─────────────────────────────────────────────────┐
  └──────────┘                                                 │
      ▲      Query: "Analyze GH-ISSUE-107"                     │
      │      State: {evidence_envelopes: []}                   │
      │                                                         │
      └──────────────────────────────────────────────────┐     │
                                                         │     │
                                            ┌────────────┘     │
                                            │                  │
                                       ┌────┴─────┐            │
                                       │ PLAN NODE│            │
                                       └────┬─────┘            │
                                            │                  │
                Load: {                     │                  │
                  skill_registry,           │                  │
                  agent_registry            │                  │
                }                           │                  │
                                            │                  │
                LLM Decides:                │                  │
                  required_skill:           │                  │
                    "defect_correlation"    │                  │
                  agent_id:                 │                  │
                    "defect_agent"          │                  │
                  agent_prompt:             │                  │
                    "Triage GH-ISSUE-107..." │                  │
                                            │                  │
                                       ┌────┴──────┐            │
                                       │ EXECUTE   │            │
                                       └────┬──────┘            │
                                            │                  │
                    agent_map.get(          │                  │
                      "defect_agent"        │                  │
                    ).execute_react_loop(   │                  │
                      {"prompt": ...}       │                  │
                    )                       │                  │
                                            │                  │
                                       ┌────┴─────┐             │
                                       │ OBSERVE   │             │
                                       └────┬─────┘             │
                                            │                  │
                    Evidence collected:     │                  │
                    • github_issue_record   │                  │
                    • severity_urgency      │                  │
                                            │                  │
                                       ┌────┴────────┐          │
                                       │ EVALUATE    │          │
                                       └────┬────────┘          │
                                            │                  │
                    Evidence_count: 2       │                  │
                    Sufficient? No          │                  │
                    → Loop back to REASON   │                  │
                                            │                  │
                            ┌───────────────┘                  │
                            │                                  │
                            ▼                                  │
ITERATION 2:           ┌──────────┐                           │
                       │ REASON   │◄──────────────────────────┘
                       └──────────┘
                            │
                      Evidence: 2/5 collected
                      Query: "Need requirement impact"
                            │
                            ▼
                       ┌────────────┐
                       │ PLAN NODE  │
                       └────┬───────┘
                            │
                LLM Decides:
                  skill: "dependency_risk"
                  agent: "requirement_agent"
                            │
                            ▼
                       ┌──────────┐
                       │ EXECUTE  │
                       └────┬─────┘
                            │
                  Call requirement_agent
                            │
                            ▼
                       ┌────────────┐
                       │ OBSERVE    │
                       └────┬───────┘
                            │
                  Evidence: 4/5 collected
                            │
                            ▼
                       ┌────────────┐
                       │ EVALUATE   │
                       └────┬───────┘
                            │
                   Sufficient? YES
                   → Exit loop
                            │
                            ▼
                    ┌──────────────┐
                    │ CROSS_HANDOFF│
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ SYNTHESIZE   │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ VISUAL_GEN   │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │HUMAN_VALIDATE│
                    └──────────────┘
                            │
                       [APPROVED]
                            │
                            ▼
                          END
```

---

## 3. Execute Node — Dynamic Agent Invocation (NO Hardcoding)

```
┌─────────────────────────────────────────────────────────────────┐
│              EXECUTE_AGENT_NODE — Universal Pattern             │
│                     (Same for PM.ai & ENG.ai)                   │
└─────────────────────────────────────────────────────────────────┘

INPUT: planner_decision (from PLAN node)
  {
    "agent_id": "requirement_agent",
    "agent_prompt": "Query: GH-ISSUE-107... Find impacted requirements...",
    "required_skill": "dependency_risk",
    "gap": "Missing requirement impact analysis"
  }

EXECUTION:

Step 1: Extract planner decision
  agent_id = planner_decision["agent_id"]
  agent_prompt = planner_decision["agent_prompt"]
  required_skill = planner_decision["required_skill"]

Step 2: Dynamic agent lookup (NO if/else hardcoding!)
  agent_map = {
    "defect_agent": defect_agent,
    "requirement_agent": requirement_agent,
    "test_agent": test_agent,
    "codefix_agent": codefix_agent,
    "resource_agent": resource_agent
  }
  
  agent = agent_map.get(agent_id)

Step 3: Handle special cases
  if agent_id == "SYNTHESIS_READY":
    return state  # No agent call needed

Step 4: Execute agent
  try:
    result = agent.execute_react_loop({
      "query": state.query,
      "prompt": agent_prompt,  ◄─ From planner, NOT hardcoded
      "context": agent_prompt
    })
  except Exception as e:
    state["agent_execution_error"] = str(e)

Step 5: Store evidence
  state["observed_new_evidences"] = result["evidences"]
  state["agent_task_input"] = {
    "executed_agent": agent_id,
    "skill": required_skill,
    "summary": result.get("summary")
  }

OUTPUT: Updated state with evidence collected
```

---

## 4. Skill + Agent Selection (Planner Intelligence)

```
┌──────────────────────────────────────────────────────────────┐
│              PLAN_NODE — Intelligent Selection               │
│              (Skill Registry + Agent Registry)               │
└──────────────────────────────────────────────────────────────┘

LOAD REGISTRIES:

skill_registry.json:
  {
    "velocity_analysis_skill": {
      "skill_name": "Velocity Analysis",
      "applicable_masters": ["PM.ai"],
      "competence": "Compute velocity trends...",
      "candidate_agents": ["resource_agent", "defect_agent"]
    },
    "defect_correlation_skill": {
      "skill_name": "Defect Correlation",
      "applicable_masters": ["PM.ai", "ENG.ai"],
      "competence": "Correlates defects with requirements...",
      "candidate_agents": ["defect_agent", "requirement_agent"]
    },
    ...
  }

agent_registry.json:
  {
    "requirement_agent": {
      "name": "Requirement Traceability Specialist",
      "capabilities": ["Lookup requirement metadata", ...],
      "supported_evidence_types": ["requirement_record", ...]
    },
    "defect_agent": {
      "name": "Defect & Issue Intelligence Specialist",
      "capabilities": ["Retrieve GitHub issue metadata", ...],
      "supported_evidence_types": ["github_issue_record", ...]
    },
    ...
  }

LLM PLANNER PROMPT:

  "You are the AXIOM Planner LLM.
  
  USER QUERY: {query}
  TARGET MASTER: {target_master}
  
  AVAILABLE SKILLS (for {target_master}):
  {skill_options filtered by applicable_masters}
  
  AVAILABLE AGENTS:
  {agent_options}
  
  YOUR TASK:
  1. Identify which SKILL is needed based on the query
  2. Select the BEST AGENT from that skill's candidate_agents
  
  Return JSON:
  {
    "required_skill": "defect_correlation_skill",
    "agent_id": "defect_agent",
    "agent_prompt": "Detailed prompt...",
    "gap": "Missing evidence...",
    ...
  }"

LLM DECISION:
  required_skill: "defect_correlation_skill"
  candidate_agents: ["defect_agent", "requirement_agent"]
  → Select: "defect_agent" (best match)
  
  agent_prompt: "Triage GH-ISSUE-107, classify severity/urgency, identify leakage direction..."

RESULT: Planner decision with intelligent agent selection!
```

---

## 5. Master Selection Flow (PM.ai vs ENG.ai)

```
┌────────────────────────────────────────────────────────┐
│         ROUTER NODE — Master Intent Detection         │
└────────────────────────────────────────────────────────┘

QUERY: "Analyze GH-ISSUE-107 defect and impact"

ROUTER LOGIC (Pattern-based):
  
  if "defect" in query OR "bug" in query OR "issue" in query:
    → target_master = "AXIOM-PM"
    → reason: defect triage is PM responsibility
  
  if "patch" in query OR "code fix" in query:
    → target_master = "AXIOM-ENG"
    → reason: code fixing is ENG responsibility
  
  if "test" in query:
    → target_master = "AXIOM-PM" (default)
    → reason: test management is PM responsibility
  
  Default: "AXIOM-PM"

RESULT:
  state["target_master"] = "AXIOM-PM"
  
  ┌─────────────────────────────────────────┐
  │ All subsequent nodes use this setting:  │
  │ • Skill registry filtered by master     │
  │ • Agent selection considers master role │
  │ • Evidence types match master domain    │
  └─────────────────────────────────────────┘
```

---

## 6. Key Differences: AXIOM vs agent_pjm.py

```
┌─────────────────────────────────────────────────────────┐
│         FEATURE COMPARISON: AXIOM vs agent_pjm.py      │
└─────────────────────────────────────────────────────────┘

❌ BEFORE (Hardcoded):
  ├─ PM_CAPABILITY_EVIDENCE_DIMS static mapping
  ├─ if master == "PM": ... elif master == "ENG": ...
  ├─ if agent_id == "defect": ... elif agent_id == "req": ...
  ├─ Hardcoded "GH-ISSUE-107", "proximity_controller.py"
  └─ ~100+ lines per master

✅ AFTER (LLM-Driven):
  ├─ Planner loads skill_registry dynamically
  ├─ LLM decides skill + agent (no if/else)
  ├─ agent_map universal lookup (5 lines)
  ├─ agent_prompt from planner (0 hardcoding)
  └─ ~40 lines, same for all masters

RESULT: Single codebase, max intelligence, zero duplication!
```

---

## 7. Evidence Collection Flow

```
┌─────────────────────────────────────────────────────────┐
│         EVIDENCE ACCUMULATION ACROSS ITERATIONS        │
└─────────────────────────────────────────────────────────┘

Iteration 1:
  state["evidence_envelopes"] = []
  
  EXECUTE: defect_agent
  → Collects: [
      {"artifact_id": "GH-ISSUE-107", "artifact_type": "github_issue_record", ...},
      {"artifact_id": "severity_S1", "artifact_type": "severity_urgency_matrix", ...}
    ]
  
  state["evidence_envelopes"] = 2 evidences

Iteration 2:
  EVALUATE: Is 2 sufficient? No (need requirement impact)
  
  EXECUTE: requirement_agent
  → Collects: [
      {"artifact_id": "REQ-L2-001", "artifact_type": "requirement_record", ...},
      {"artifact_id": "ripple_123", "artifact_type": "ripple_subgraph", ...}
    ]
  
  state["evidence_envelopes"] = 4 evidences

Iteration 3:
  EVALUATE: Is 4 sufficient? YES
  → Exit loop
  → Go to SYNTHESIZE
  
  SYNTHESIZE:
    Consolidates 4 evidences into:
    • Summary: "GH-ISSUE-107 is S1 critical..."
    • Sources: [GitHub issue, Requirement KG, ...]
    • Confidence: 0.92
    • Gaps: ["Test coverage analysis"]

  VISUAL_GEN:
    Creates diagram: "Defect Impact Blast Radius"

  HUMAN_VALIDATE:
    APPROVED → Deliver final response
```

---

## Summary

**AXIOM's 9-node architecture:**
- ✅ **Unified codebase** for PM.ai & ENG.ai (no duplication)
- ✅ **LLM-driven planning** (skill + agent selection via planner)
- ✅ **Dynamic execution** (universal agent_map, no hardcoding)
- ✅ **Evidence accumulation** (max 5 iterations, then synthesis)
- ✅ **Human-in-loop** (HITL checkpoint before final delivery)
- ✅ **Parity with agent_pjm.py** (same pattern, better integration)
