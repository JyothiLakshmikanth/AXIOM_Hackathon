# ⬡ AXIOM: Evidence-Driven Multi-Agent Intelligence System

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![Vertex AI](https://img.shields.io/badge/Vertex_AI-Gemini-1a73e8?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![LangGraph](https://img.shields.io/badge/LangGraph-9--Node_Cognitive-FF6F00?logo=python&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Design Skills](https://img.shields.io/badge/Design-Professional_SVG-00CC99)](#design-skills-engine)
[![HITL](https://img.shields.io/badge/HITL-Human--in--Loop-FF9900)](#hitl-checkpoint)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Modern_API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

> **Detect. Decide. Deliver. Visualize.**
>
> A unified, evidence-driven, multi-master cognitive intelligence platform deployed on Google Cloud.
> Combines intelligent agent orchestration, professional visualization, and human-in-the-loop validation
> for safety-critical engineering programs.

---

## 📖 Complete Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [9-Node Unified Cognitive Loop](#9-node-unified-cognitive-loop)
4. [Dual Cognitive Masters](#dual-cognitive-masters)
5. [Design Skills Engine](#design-skills-engine)
6. [HITL (Human-in-the-Loop)](#hitl-human-in-the-loop)
7. [Cross-Master Handoff](#cross-master-handoff)
8. [Master Registries](#master-registries)
9. [Specialized Agents](#specialized-langchain-react-agents)
10. [Knowledge Foundation](#knowledge-foundation)
11. [Complete Repository Structure](#complete-repository-structure)
12. [Installation & Setup](#installation--setup)
13. [Deployment to GCP Cloud Run](#deployment-to-gcp-cloud-run)
14. [Running AXIOM](#running-axiom)
15. [Example Queries](#example-queries)
16. [Safety Guardrails](#safety-guardrails)

---

## System Overview

AXIOM is a **unified, evidence-driven cognitive intelligence system** that bridges the gap between project delivery and technical engineering. Instead of guessing, AXIOM:

1. **Routes intelligently** - LLM-driven semantic classification (not keyword matching)
2. **Gathers evidence** - Delegates to specialized agents for domain-specific queries
3. **Validates sufficiency** - Checks deterministically against skill requirements
4. **Synthesizes intelligently** - LLM combines evidence into coherent findings
5. **Visualizes professionally** - Generates SVG diagrams using semantic design rules
6. **Validates with humans** - HITL checkpoint before final delivery

**Key Innovation:** Single unified 9-node LangGraph framework used by both masters (PM.ai and ENG.ai), reducing code by 50% and eliminating duplication.

---

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                            │
│               (CLI / FastAPI / Streamlit / Cloud Run Endpoint)            │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
        ╔════════════════════════════════════════════════════════╗
        ║           ROUTER NODE (LLM-Driven Intent)              ║
        ║   Loads: "21_intent_detection_classifier" prompt      ║
        ║   Classifies: Domain (PJM/ENG), Boundary, Confidence  ║
        ║   Routes: to AXIOM-PM or AXIOM-ENG                   ║
        ╚════════════════╤═════════════════════════════════════╝
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
    ┌──────────────┐          ┌──────────────┐
    │  AXIOM-PM    │          │  AXIOM-ENG   │
    │  (Delivery)  │          │  (Technical) │
    └──────┬───────┘          └──────┬───────┘
           │                         │
           └──────────────┬──────────┘
                          │
        ╔═════════════════▼══════════════════════════════════════╗
        ║      UNIFIED 9-NODE COGNITIVE LOOP                     ║
        ║  (Both masters use identical implementation)           ║
        ║  Parameterized by state["target_master"]             ║
        ║                                                        ║
        ║  1. REASON          → Set evidence dimensions         ║
        ║  2. MEMORY          → Check Firestore cache          ║
        ║  3. PLAN            → Select best agent              ║
        ║  4. EXECUTE         → Delegate to specialist         ║
        ║  5. OBSERVE         → Normalize evidence             ║
        ║  6. EVALUATE        → Check sufficiency              ║
        ║  7. CROSS_HANDOFF   → PM ↔ ENG communication        ║
        ║  8. SYNTHESIZE      → LLM synthesis                  ║
        ║  9a. VISUAL_GEN     → Design Skills (SVG)            ║
        ║  9b. HUMAN_VALIDATE → HITL Checkpoint               ║
        ╚═════════════════╤══════════════════════════════════════╝
                          │
        ╔═════════════════▼══════════════════════════════════════╗
        ║         KNOWLEDGE FOUNDATION (Polyglot)               ║
        ║                                                        ║
        ║  🟢 Firestore       → Short-term memory & cache      ║
        ║  🔵 BigQuery        → Analytics & vector search      ║
        ║  🟣 Neo4j AuraDB    → Relationship graph             ║
        ║  🟠 Git + Storage   → Code AST analysis              ║
        ╚═════════════════╤══════════════════════════════════════╝
                          │
        ╔═════════════════▼══════════════════════════════════════╗
        ║    SPECIALIZED LANGCHAIN REACT AGENTS                 ║
        ║                                                        ║
        ║  • requirement_agent  (Neo4j)                         ║
        ║  • test_agent         (BigQuery)                      ║
        ║  • defect_agent       (GitHub + BigQuery)             ║
        ║  • resource_agent     (BigQuery + Qdrant)             ║
        ║  • codefix_agent      (Git AST)                       ║
        ╚════════════════════════════════════════════════════════╝
```

---

## 9-Node Unified Cognitive Loop

### Detailed Flow (ASCII)

```
                          ┌──────────────────┐
                          │     START        │
                          └────────┬─────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  1. REASON NODE             │
                    │  ─────────────────────────  │
                    │  • Load master config       │
                    │  • Set required evidence    │
                    │  • Form initial hypothesis │
                    │  • Load PM/ENG capability  │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  2. MEMORY NODE             │
                    │  ─────────────────────────  │
                    │  • Query Firestore cache    │
                    │  • Check session history    │
                    │  • If hit: jump to 6        │
                    └──────────────┬──────────────┘
                                   │
          ┌─────────────────────────▼──────────────────────────┐
          │  3. PLAN NODE (Intelligence Hub)                  │
          │  ─────────────────────────────────────────────    │
          │  • Identify evidence gaps                          │
          │  • Load agent_registry.json                        │
          │  • Load capability_matrix.json                     │
          │  • Call LLM planner: "Which agent fills gap?"    │
          │  • Decision: agent_id, tools, expected_evidence   │
          └─────────────────┬────────────────────────────────┘
                            │
          ┌─────────────────▼────────────────────────────────┐
          │  4. EXECUTE NODE                                │
          │  ─────────────────────────────────────────────  │
          │  • Retrieve agent from agent_registry            │
          │  • Call selected specialized agent              │
          │  • Pass tools from registry                      │
          │  • Collect evidence_envelopes                   │
          └─────────────────┬────────────────────────────────┘
                            │
          ┌─────────────────▼────────────────────────────────┐
          │  5. OBSERVE NODE                                │
          │  ─────────────────────────────────────────────  │
          │  • Normalize to EvidenceEnvelope format         │
          │  • Validate against expected_evidence           │
          │  • Cache to Firestore                           │
          │  • Append to state["evidence_envelopes"]        │
          └─────────────────┬────────────────────────────────┘
                            │
    ┌───────────────────────▼────────────────────────────┐
    │  6. EVALUATE NODE                                 │
    │  ─────────────────────────────────────────────   │
    │  • Check evidence_sufficiency                    │
    │  • Compare collected vs. required dimensions    │
    │  • Evaluate: SUFFICIENT | PARTIAL | MISSING    │
    │  • hitl_loop_count++                            │
    │                                                  │
    │  If INSUFFICIENT and iteration < 5:            │
    │      └─→ LOOP BACK TO PLAN (Step 3)           │
    │                                                  │
    │  Else:                                          │
    │      └─→ PROCEED TO CROSS_HANDOFF (Step 7)    │
    └────────────────────┬───────────────────────────┘
                         │
    ┌────────────────────▼───────────────────────────┐
    │  7. CROSS_HANDOFF NODE (Optional)             │
    │  ─────────────────────────────────────────   │
    │  • Check if cross_domain analysis needed      │
    │  • If needed:                                 │
    │     ├─ Package evidence (text-only)          │
    │     ├─ Call OTHER master                     │
    │     ├─ Prevent recursion (flag check)        │
    │     └─ Append other master's response       │
    │                                              │
    │  • If not needed:                            │
    │     └─ Skip this node                        │
    │                                              │
    │  Set: state["cross_handoff_done"] = True    │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼──────────────────────────────┐
    │  8. SYNTHESIZE NODE                              │
    │  ─────────────────────────────────────────────   │
    │  • Load: "synthesize_node" prompt               │
    │  • LLM synthesizes all evidence                 │
    │  • Generate structured answer (JSON)           │
    │  • Decide response_mode:                        │
    │    ├─ "text_only"       (no images)            │
    │    ├─ "text_and_image"  (text + visual)        │
    │    └─ "image_only"      (visual primary)       │
    │                                                 │
    │  Output: structured_answer, response_mode     │
    └────────────────────┬──────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
         ▼                                ▼
    ┌──────────────────┐   ┌───────────────────────────┐
    │  9a. VISUAL_GEN  │   │  9b. HUMAN_VALIDATE (HITL)│
    │  ──────────────  │   │  ─────────────────────── │
    │  If response_mode│   │  • Display answer        │
    │  = text_only:    │   │  • Display visualization │
    │    └─ Skip       │   │  • Three buttons:        │
    │                  │   │    ├─ ✅ APPROVE        │
    │  Else:           │   │    ├─ ❌ REJECT         │
    │    ├─ Load design│   │    └─ 📝 REQUEST_MORE   │
    │    │  specs     │   │                          │
    │    ├─ Render    │   │  Human Decision:         │
    │    │  SVG/PNG   │   │  • APPROVE → END         │
    │    └─ Return    │   │  • REJECT → REASON (loop)│
    │       image_url │   │  • REQUEST → PLAN (max 2)│
    └────────┬────────┘   └────────┬──────────────┘
             │                     │
             └──────────┬──────────┘
                        │
                    ┌───▼────────────────────────┐
                    │  FINAL OUTPUT               │
                    │  ─────────────────────────  │
                    │  • Structured markdown      │
                    │  • Evidence citations       │
                    │  • Image artifact (if gen)  │
                    │  • Confidence scores        │
                    └───┬────────────────────────┘
                        │
                        ▼
                    ┌──────────────┐
                    │     END      │
                    └──────────────┘
```

---

## Dual Cognitive Masters

### PM.ai (AXIOM-PM) - Project Delivery Intelligence

**Mission:** Correlate project evidence to provide delivery risk visibility, preliminary analysis, and decision support.

**Domain:** Schedule, Resource, Scope, Quality (delivery consequences)

**Capabilities (12 total):**
- preliminary_rca
- defect_triage
- project_health
- sprint_replanning
- sprint_timeline_analysis
- requirement_impact
- test_readiness
- cross_project_dependency
- decision_brief
- assignment_recommendation
- defect_hotspot_analysis
- prevention_intelligence

**Required Skills (5):**
- velocity_analysis_skill
- defect_correlation_skill
- test_coverage_analysis_skill
- resource_capacity_skill
- dependency_risk_skill

**Prohibited (Safety):**
- ❌ MUST NOT assert code root causes
- ❌ MUST NOT generate code patches
- ❌ MUST NOT close defects without QA verification

---

### ENG.ai (AXIOM-ENG) - Engineering Intelligence

**Mission:** Correlate engineering evidence to provide technical RCA, code insights, and design validation.

**Domain:** Code, Architecture, Testing, Performance, Security

**Capabilities (10 total):**
- root_cause_analysis
- architecture_review
- code_quality
- test_coverage_analysis
- performance_analysis
- security_assessment
- design_validation
- correction_design
- itpa_test_prioritization
- code_ripple_analysis

**Required Skills (5):**
- root_cause_discovery_skill
- architecture_validation_skill
- code_quality_skill
- performance_optimization_skill
- security_assessment_skill

**Prohibited (Safety):**
- ❌ MUST NOT alter milestone commitments
- ❌ MUST NOT commit code without human PR review
- ❌ MUST NOT reassign engineers without PM.ai approval

---

## Design Skills Engine

### Purpose

Generate **professional, presentation-ready SVG visualizations** using explicit design rules (NOT text prompts to Gemini). AXIOM owns the visual generation with zero external dependencies.

### Three-Layer System

#### 1. Semantic Color System

```
🔴 CRITICAL (Red #DC3545)
   → Failure, leakage, blocking issues
   Used for: Error states, critical risks, blocking dependencies

🟠 WARNING (Orange #FFC107)
   → Warning, attention, medium risk
   Used for: Warnings, attention-needed items, medium severity

🟢 SUCCESS (Green #28A745)
   → Verified, resolved, successful
   Used for: Success states, resolved items, low risk

🔵 INFO (Blue #17A2B8)
   → Information, process, neutral content
   Used for: Informational items, process flows, neutral data

⚫ DARK (Gray #212529)
   → Structure, text, supporting information
   Used for: Main text, labels, structure, borders
```

#### 2. Typography Hierarchy

```
TITLE      → 32px, bold, dark gray
            Scannable immediately, main heading

HEADING    → 20px, bold, dark gray
            Section headers, subsection titles

LABEL      → 14px, bold, dark gray
            Key items, field names, emphasis

DETAIL     → 12px, normal, dark gray
            Supporting information, descriptive text

CAPTION    → 10px, normal, gray
            Metadata, timestamps, footnotes
```

#### 3. Visualization Types (6 Total)

```
1. FISHBONE (Ishikawa RCA)
   ├─ Layout: Horizontal spine with branching causes
   ├─ Categories: Requirements, Testing, Software, Process
   ├─ Color: Category-specific (Red, Orange, Blue)
   └─ Use: Root cause analysis, problem decomposition

2. FIVE-WHY
   ├─ Layout: Horizontal chain of connected nodes
   ├─ Progression: Problem → Why1 → Why2 → ... → Root Cause
   ├─ Color: Red → Orange → Orange → Green
   └─ Use: Causal chain analysis, why-because investigation

3. TIMELINE
   ├─ Layout: Horizontal roadmap with date markers
   ├─ Status colors: Blue (planned), Orange (new), Red (delayed), Green (complete)
   ├─ Milestones: Visually prominent markers
   └─ Use: Project roadmap, sprint planning, delivery dates

4. LEAKAGE PROPAGATION CHAIN
   ├─ Layout: Horizontal progression (Error → Defect → Failure)
   ├─ Stages: Each has semantic color & icon
   ├─ Optional: Detection gaps, impact points
   └─ Use: Defect leakage analysis, failure propagation

5. PROJECT HEALTH DASHBOARD
   ├─ Layout: Card-based grid (Health summary + sprints + risks + outlook)
   ├─ Risk colors: 🔴 Critical → 🟠 High → 🟡 Medium → 🟢 Low
   ├─ Sprint status: On-track / At-risk / Off-track
   └─ Use: Executive dashboard, 4-pillar assessment, health overview

6. SPRINT IMPACT TIMELINE (Resource Heatmap)
   ├─ Layout: Table/card grid (Associate, Load, Risk, Recommendation)
   ├─ Load level: 🟢 Light → 🟡 Moderate → 🔴 High → ⚫ Overloaded
   ├─ Risk level: 🟢 No risk → 🟡 Moderate → 🔴 High
   └─ Use: Team capacity, workload assessment, sprint planning
```

### Implementation

**File:** `orchestrator/design_skills_engine.py` (452 lines)

**Classes:**
- `ColorPalette` - Semantic color definitions
- `Typography` - Typography styles
- `DesignSpecifications` - Spec builder for all 6 types
- `VisualizationEngine` - Renders SVG from spec + data

**Features:**
- ✅ Deterministic rendering (no LLM guessing)
- ✅ Reusable design specs
- ✅ Professional engineering aesthetic
- ✅ SVG output (vector, scalable)
- ✅ PNG export (raster, universal)

---

## HITL (Human-in-the-Loop)

### Purpose

Ensure every AXIOM response receives human review and approval before delivery. Provides structured feedback loop for iterative refinement.

### Three Decision Buttons

```
                 HUMAN_VALIDATE NODE
                      │
            ┌──────────┼──────────┐
            │          │          │
            ▼          ▼          ▼
        ┌────────┐ ┌────────┐ ┌────────────┐
        │ APPROVE│ │ REJECT │ │REQUEST_MORE│
        └───┬────┘ └───┬────┘ └────┬───────┘
            │          │           │
            ▼          ▼           ▼
         END      RESTART FROM  LOOP TO PLAN
                   REASON         (Max 2x)
                  (with feedback)
```

### Decision Logic

| Button | Action | Result | Max Iterations |
|--------|--------|--------|----------------|
| **APPROVE** ✅ | Accept answer | Deliver response | Final |
| **REJECT** ❌ | Restart with feedback | Reanalyze from REASON node | Unlimited |
| **REQUEST_MORE** 📝 | Ask for specifics | Loop back to PLAN for more evidence | Max 2 additional loops |

### Implementation

**File:** `streamlit_components/hitl_renderer.py` (345 lines)

**Components:**
- `render_hitl_checkpoint()` - Displays answer for human review
- `stream_hitl_integration()` - LangGraph interrupt/resume
- `format_structured_answer()` - JSON → markdown formatting

**UI Elements:**
1. Structured answer (text + JSON sections)
2. Visualization (SVG/PNG image if generated)
3. Confidence metrics (overall, evidence_coverage, data_quality)
4. Three action buttons with optional feedback text

---

## Cross-Master Handoff

### When It Happens

```
┌─────────────────────────────────────────┐
│  EVALUATE NODE (evidence check)         │
├─────────────────────────────────────────┤
│  Decision: Do we need the OTHER master? │
│                                         │
│  If cross_domain analysis needed:       │
│    └─→ CROSS_HANDOFF triggered         │
│                                         │
│  Else:                                  │
│    └─→ Skip directly to SYNTHESIZE     │
└─────────────────────────────────────────┘
```

### Communication Flow

```
PM.ai Analysis (Preliminary)
  │
  ├─ Hypothesis: "Bug likely from missing validation"
  ├─ Evidence: [severity, team_impact, velocity]
  ├─ Gap: Missing code-level root cause
  │
  └─→ CROSS_HANDOFF triggered
      │
      ▼
   ┌──────────────────────────────┐
   │  Send to ENG.ai              │
   ├──────────────────────────────┤
   │  Package:                    │
   │  • Hypothesis (text)         │
   │  • Evidence (text-only)      │
   │  • Question: "Confirm RCA?" │
   │  • Constraint: Text-only     │
   └──────────────────────────────┘
      │
      ▼
   ENG.ai Analysis
   │
   ├─ Code AST analysis
   ├─ Finding: "ValidationHelper.checkBounds() missing null check"
   ├─ Evidence: [commit_hash, exact_line, test_failure]
   │
   └─→ Return to PM.ai (text response)
       │
       ▼
   Back to PM.ai
   ├─ Append ENG response to evidence_envelopes
   ├─ Set: state["cross_handoff_done"] = True
   └─ Continue to SYNTHESIZE
```

### Safety Features

| Feature | Mechanism | Purpose |
|---------|-----------|---------|
| **No Recursion** | `cross_handoff_done` flag | Prevent PM→ENG→PM loops |
| **Text-Only** | No image generation during handoff | Efficiency, no visual overhead |
| **Max Handoff = 1** | Count-based prevention | Single per analysis cycle |
| **Timeout Protection** | 60-second timeout | Prevent hanging |
| **Evidence Integration** | Append to state["evidence_envelopes"] | Combine both perspectives |

---

## Master Registries

### Three-Layer Registry System

```
┌───────────────────────────────────┐
│  CAPABILITIES (What masters do)   │
│  capability_matrix.json           │
│  ├─ PM: 12 capabilities           │
│  └─ ENG: 10 capabilities          │
│  Maps to: skills + agents         │
└────────────┬──────────────────────┘
             │ depends on
┌────────────▼──────────────────────┐
│  SKILLS (How they do it)          │
│  skill_registry.json              │
│  ├─ PM: 5 skills                  │
│  └─ ENG: 5 skills (1 shared)      │
│  Maps to: agents + evidence       │
└────────────┬──────────────────────┘
             │ enabled by
┌────────────▼──────────────────────┐
│  AGENTS (Who does the work)       │
│  agent_registry.json              │
│  └─ 5 specialized agents          │
│  Maps to: tools + evidence types  │
└───────────────────────────────────┘
```

### 1. Agent Registry (agent_registry.json)

```json
5 Specialized Agents:

1. requirement_agent
   • Primary store: Neo4j Knowledge Graph
   • Capabilities: Traceability, impact analysis, ripple effect
   • Tools: requirement_details_tool, impact_analysis_tool
   • Evidence types: requirement_record, traceability_edges, acceptance_criteria

2. test_agent
   • Primary store: BigQuery & Cloud Storage
   • Capabilities: Coverage gap analysis, test generation
   • Tools: test_details_tool, test_generation_tool
   • Evidence types: test_run_failure_log, branch_coverage_report, requirement_test_matrix

3. defect_agent
   • Primary store: GitHub Issues + BigQuery
   • Capabilities: Severity/urgency scoring, leakage analysis
   • Tools: github_fetch_issue, bigquery_defect_scoring
   • Evidence types: github_issue_record, defect_leakage_assessment, severity_urgency_matrix

4. resource_agent
   • Primary store: BigQuery + Qdrant Vector DB
   • Capabilities: Velocity tracking, capacity modeling, skill matching
   • Tools: team_velocity_tool, engineer_capacity_tool
   • Evidence types: sprint_velocity_record, engineer_capacity_envelope, team_burn_rate

5. codefix_agent
   • Primary store: Git + Cloud Storage
   • Capabilities: Root cause isolation, patch generation, syntax validation
   • Tools: ast_inspect_tool, generate_patch_tool
   • Evidence types: git_commit_diff, source_ast_inspection, proposed_surgical_patch
```

### 2. Capability Matrix (capability_matrix.json)

**PM.ai Capabilities (12):**
- preliminary_rca (defect_correlation, dependency_risk)
- defect_triage (defect_correlation, dependency_risk)
- project_health (velocity_analysis, defect_correlation, test_coverage, resource_capacity)
- sprint_replanning (velocity_analysis, resource_capacity)
- sprint_timeline_analysis (velocity_analysis)
- requirement_impact (dependency_risk, test_coverage)
- test_readiness (test_coverage_analysis, defect_correlation)
- cross_project_dependency (dependency_risk, velocity_analysis)
- decision_brief (defect_correlation, velocity_analysis)
- assignment_recommendation (resource_capacity, defect_correlation)
- defect_hotspot_analysis (defect_correlation, velocity_analysis)
- prevention_intelligence (defect_correlation, test_coverage)

**ENG.ai Capabilities (10):**
- root_cause_analysis (root_cause_discovery, code_quality)
- architecture_review (architecture_validation, code_quality)
- code_quality (code_quality, root_cause_discovery)
- test_coverage_analysis (test_coverage_analysis, code_quality)
- performance_analysis (performance_optimization, code_quality)
- security_assessment (security_assessment, code_quality)
- design_validation (architecture_validation, code_quality)
- correction_design (root_cause_discovery, code_quality)
- itpa_test_prioritization (test_coverage_analysis, performance_optimization)
- code_ripple_analysis (code_quality, root_cause_discovery)

### 3. Skill Registry (skill_registry.json)

**PM.ai Skills (5):**
- velocity_analysis_skill
- defect_correlation_skill (SHARED with ENG)
- test_coverage_analysis_skill
- resource_capacity_skill
- dependency_risk_skill

**ENG.ai Skills (5):**
- root_cause_discovery_skill
- architecture_validation_skill
- code_quality_skill
- performance_optimization_skill
- security_assessment_skill

---

## Specialized LangChain ReAct Agents

### Agent Overview

| Agent | Primary Store | Capabilities | Tools | Evidence Types |
|-------|---------------|--------------|-------|-----------------|
| **requirement_agent** | Neo4j | Traceability analysis, impact mapping, ripple effect analysis | requirement_details_tool, impact_analysis_tool, trace_upstream, trace_downstream | requirement_record, traceability_edges, acceptance_criteria, variant_divergence |
| **test_agent** | BigQuery + Cloud Storage | Coverage gap analysis, test generation, test failure analysis | test_details_tool, test_generation_tool, coverage_report_tool | test_run_failure_log, branch_coverage_report, requirement_test_matrix, test_gap_analysis |
| **defect_agent** | GitHub + BigQuery | Severity/urgency scoring, defect leakage analysis, hotspot detection | github_fetch_issue, bigquery_defect_scoring, leakage_analysis_tool | github_issue_record, defect_leakage_assessment, severity_urgency_matrix, hotspot_correlation |
| **resource_agent** | BigQuery + Qdrant | Velocity tracking, capacity modeling, skill matching, burn rate analysis | team_velocity_tool, engineer_capacity_tool, skill_match_tool | sprint_velocity_record, engineer_capacity_envelope, team_burn_rate, skill_availability |
| **codefix_agent** | Git + Cloud Storage | Root cause isolation, patch generation, syntax validation, ripple analysis | ast_inspect_tool, generate_patch_tool, syntax_validator_tool | git_commit_diff, source_ast_inspection, proposed_surgical_patch, syntax_validation_report |

### Agent Communication Pattern (ReAct Loop)

```
AGENT RECEIVES QUERY
  │
  ├─ Thought: What tools do I need?
  │
  ├─ Action: SELECT TOOL(S)
  │   └─ Tool input from evidence + context
  │
  ├─ Observation: TOOL RESULT
  │   └─ Parse structured data from store
  │
  ├─ Thought: Is this sufficient?
  │   ├─ If yes → Proceed to final answer
  │   └─ If no → Loop back to Action
  │
  └─ Final Answer: EVIDENCE ENVELOPE
      ├─ Structured findings
      ├─ Confidence score
      ├─ Data sources
      └─ Timestamps
```

---

## Knowledge Foundation

### How AXIOM Uses Both (The Winning Architecture)

> ### 💡 The Pitch to the Judges:
> *"AXIOM utilizes a polyglot persistence model on Google Cloud. We use **Firestore** for low-latency operational state and chat history. We use **Neo4j** for deep, multi-hop graph reasoning and variant divergence. And we use **BigQuery** as our unified analytical data lake, natively storing both our relational traceability matrices and our high-dimensional vector embeddings, allowing our specialized agents to execute complex SQL-based semantic searches without the overhead of managing a third-party vector database."*

To score maximum points for **Technical Merit & GenAI Implementation**, AXIOM distributes data across Google Cloud and Neo4j according to operational characteristics—using the right tool for the right job:

```mermaid
graph TD
  subgraph Brain["AXIOM Cognitive Brain Persistence Model"]
    FS["🟢 Firestore<br/><b>The Brain's Short-Term Memory</b><br/>• LangGraph State Checkpoints<br/>• Conversation Session History<br/>• User Preferences & Filters<br/>• Runtime Evidence Cache"]
    BQ["🔵 BigQuery<br/><b>The Brain's Long-Term Analytical Memory</b><br/>• 768-dim text-embedding-004 Vector Embeddings<br/>• Historical Defects & 8D RCA Records<br/>• Sprint Velocity & Burndown Metrics<br/>• Native SQL VECTOR_SEARCH (IVF + Cosine)"]
    NEO["🟣 Neo4j AuraDB<br/><b>The Brain's Relationship Map</b><br/>• Multi-Hop Graph Traversal (1..3 hops)<br/>• Variant Divergence (Base vs. Premium)<br/>• Semantic Topic Affinity Clusters<br/>• Requirement Cypher Vector Index"]
  end
```

### Data Distribution Breakdown

| Storage Foundation | Brain Analogy | Role & Data Managed | Key Capabilities |
|---|---|---|---|
| **🟢 Google Cloud Firestore** | **The Brain's Short-Term Memory** | Data that changes constantly and needs low-latency operational read/write access.<br>• **LangGraph State**: Checkpoints so the orchestrator preserves context across turns.<br>• **Chat History**: Conversation turns between the user and AXIOM.<br>• **User Preferences**: Dynamic session filters (e.g., *"Show me only Premium variant risks"*).<br>• **Runtime Cache**: Low-latency cache of verified `EvidenceEnvelope` artifacts. | Immediate sub-10ms document reads/writes; automatic state persistence across server restarts. |
| **🔵 Google BigQuery** (`axiom_qa.test_cases_embeddings`) | **The Brain's Long-Term Analytical Memory** | Massive, analytical knowledge base that the AI analyzes, correlates, and searches.<br>• **Vector Embeddings**: 768-dimensional `text-embedding-004` vectors for test cases (*replacing 3rd-party vector DBs with zero GCS overhead*).<br>• **Historical Defect & QA Data**: Past bug logs, RCA records, sprint velocities, and commit histories.<br>• **Native SQL Vector Search**: `VECTOR_SEARCH` with Cosine distance & IVF index. | Scalable petabyte analytics; native SQL semantic search without 3rd-party vector DB maintenance. |
| **🟣 Neo4j AuraDB** | **The Brain's Relationship Map** | Deep, multi-hop graph traversals that relational SQL cannot efficiently navigate.<br>• **Variant Divergence**: How REQ-L5-001 (Base BLE) diverges from REQ-L5-002 (Premium UWB) via `VARIANT_DIVERGENCE_OF`.<br>• **Semantic Affinity**: Which requirements share underlying topics via `SEMANTIC_AFFINITY`.<br>• **Complex Impact Analysis**: Multi-hop traversal across `PARENT_OF` / `CHILD_OF` hierarchy, `CONSTRAINS` safety boundaries, `MITIGATES_RISK_OF` security links, and `ALLOCATED_TO` BusinessComponents.<br>• **Requirement Vector Search**: Embedded Cypher vector indexes (`requirement_embeddings`). | Multi-hop graph pattern matching (`1..3 hops`); transitive blast radius calculation. |

### Knowledge Graph Metrics (Live Neo4j AuraDB Instance):
- **103 Total Nodes**:
  - `Requirement`: System & stakeholder requirement nodes with rich specification text and verification criteria
  - `TestCase`: Verification test cases linked directly to requirements
  - `BusinessComponent`: Allocated subsystem modules (Vehicle Controller, Mobile App, Cloud Key Service, Security Module, System)
  - `Variant`: Target vehicle variants (`VAR-BASE`, `VAR-PREM`, `VAR-FLEET`, `VAR-GLOB`)
  - `OEM`: Customization targets (e.g., `All OEMs`, `OEM-A`, `OEM-B`)
  - `ArtifactType`: Stakeholder, Software, and System requirement categorizations
  - `VerificationLevel`: Acceptance, Integration, and System verification stages
- **266 Total Relationships**:
  - **Structural Traceability**: `PARENT_OF`, `CHILD_OF`, `ALLOCATED_TO`, `TARGETS_VARIANT`, `CONSTRAINS`
  - **Safety & Risk Mitigation**: `MITIGATES_RISK_OF`
  - **Semantic Reasoning & Divergence**: `VARIANT_DIVERGENCE_OF`, `CO_ALLOCATED_WITH`, `SEMANTIC_AFFINITY`
- *Dynamic in-memory graph (`_DYNAMIC_KG`) mirrors these exact entities for local testing when offline.*

---

### Polyglot Data Architecture Deep Dive

AXIOM uses a **polyglot persistence strategy** - each data type stored in the optimal system for that domain:

#### 🟢 Firestore (Short-term Memory & Cache)

**Purpose:** LangGraph state checkpoints, conversation history, runtime evidence cache

**Data:**
- LangGraph checkpoint store (state snapshots between nodes)
- Session history (user conversations)
- Evidence cache (prevent redundant queries)
- User preferences & conversation context
- HITL decision history

**Access Pattern:**
```
MEMORY node queries Firestore:
  └─→ Cache hit? Return cached evidence (skip to EVALUATE)
  └─→ Cache miss? Proceed to PLAN
```

#### 🔵 BigQuery (Analytics & Vector Search)

**Purpose:** Structured data, vector search, historical analysis

**Datasets:**
- `axiom_data` - Defects, tests, velocity, coverage reports
- `axiom_cache` - Pre-computed vectors, embeddings
- `axiom_logs` - Query execution logs, performance metrics

**Features:**
- 768-dimensional text-embedding-004 vectors
- Native SQL VECTOR_SEARCH operator
- Streaming inserts for real-time data
- Scheduled queries for daily analytics
- Hybrid search (keyword + vector)

**Queries:**
```
BQ Agent queries:
  • SELECT * FROM axiom_data.defects WHERE issue_id = ?
  • SELECT * FROM axiom_cache.embeddings 
    WHERE VECTOR_SEARCH(embedding, @query_vector, top_k=10)
  • SELECT sprint_velocity FROM axiom_data.sprints WHERE date >= @start
```

#### 🟣 Neo4j AuraDB (Relationship Graph)

**Purpose:** Traceability, architecture, multi-hop relationships

**Node Types:**
- `Requirement` (L1, L2, L3, L4, L5)
- `TestCase` (unit, integration, system)
- `Defect` (confirmed, open, closed)
- `Engineer` (name, skills, velocity)
- `Sprint` (dates, capacity, status)
- `Module` (code, architecture)

**Relationships:**
- `REQUIRES` → REQ-1 requires REQ-2
- `VERIFIED_BY` → REQ verified by TEST
- `FOUND_BY` → DEFECT found by TEST
- `ASSIGNED_TO` → DEFECT assigned to ENGINEER
- `PART_OF` → MODULE part of SYSTEM
- `TRACES_TO` → VARIANT traces to BASELINE

**Queries:**
```
NEO4J Queries (Cypher):
  • MATCH (r:Requirement)-[:REQUIRES]->(:Requirement) RETURN ...
  • MATCH (t:TestCase)-[:VERIFIES]->(r:Requirement) RETURN ...
  • MATCH (d:Defect)-[*]->(r:Requirement) RETURN length(path) AS hops
  • MATCH (m:Module)-[:PART_OF*]->(s:System) RETURN m, s
```

#### 🟠 Git + Cloud Storage (Code Analysis)

**Purpose:** Source code AST, diffs, commit history

**Storage:**
- Git repositories (GitHub, internal)
- Cloud Storage buckets (AST JSON, diff files, patches)
- Code-to-commit mappings

**Data:**
- Full source code trees
- Abstract syntax trees (AST JSON)
- Commit diffs (line-by-line changes)
- Patch files (proposed fixes)
- Syntax validation results

**Analysis:**
```
CodeFix Agent queries:
  • git show COMMIT_HASH:path/to/file.py
  • ast.parse(source_code) → AST tree
  • Traverse AST for ValidationHelper.checkBounds()
  • Generate diff: old_code vs. new_code
  • Validate: compile(new_code) works
```

---

## Complete Repository Structure

```
AXIOM_Hackathon-main/
│
├── orchestrator/                          # 🧠 Core LangGraph & Nodes
│   ├── graph.py                           # Unified 9-node LangGraph (288 lines)
│   ├── state.py                           # Extended AxiomState (124 lines)
│   ├── master_nodes.py                    # Unified PM/ENG nodes (411 lines) [NEW]
│   ├── router.py                          # LLM-driven semantic router (185 lines)
│   ├── planner_node.py                    # Agent selection intelligence (411 lines)
│   ├── edge_routing.py                    # Conditional routing logic (225 lines)
│   ├── advanced_nodes.py                  # Cross-handoff, synthesis, visual gen (639 lines) [NEW]
│   ├── evidence_cache.py                  # Evidence envelope management (401 lines)
│   ├── prompt_loader.py                   # Dynamic JSON prompt loading (296 lines)
│   ├── gcp_client.py                      # GCP Gemini/BigQuery/Firestore (380 lines)
│   └── design_skills_engine.py            # SVG visualization rendering (452 lines) [NEW]
│
├── agents/                                # 🤖 Specialized ReAct Agents
│   ├── requirement_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                       # Neo4j queries (traceability)
│   │   ├── tools.py                       # requirement_details_tool, etc.
│   │   └── prompts.py                     # ReAct system prompts
│   ├── test_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                       # BigQuery queries (coverage)
│   │   ├── tools.py                       # test_details_tool, etc.
│   │   └── prompts.py
│   ├── defect_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                       # GitHub + BigQuery queries
│   │   ├── tools.py                       # defect scoring tools
│   │   └── prompts.py
│   ├── resource_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                       # Capacity & velocity queries
│   │   ├── tools.py
│   │   └── prompts.py
│   └── codefix_agent/
│       ├── __init__.py
│       ├── agent.py                       # Git AST analysis
│       ├── tools.py                       # Patch generation tools
│       └── prompts.py
│
├── registries/                            # 📋 Master Registries
│   ├── agent_registry.json                # 5 agents + tools
│   ├── capability_matrix.json             # 22 capabilities (12 PM + 10 ENG)
│   └── skill_registry.json                # 10 skills (5 PM + 5 ENG + 1 shared)
│
├── prompts/                               # 📝 LLM Prompts (Config-Driven)
│   ├── axiom_pm_master_v3.json            # PM system prompt + 13 stages
│   ├── axiom_eng_master_v3.json           # ENG system prompt + 13 stages
│   └── axiom_prompts_common.json          # Shared sections + classifiers
│
├── streamlit_components/                  # 🎨 UI Components
│   ├── hitl_renderer.py                   # HITL checkpoint UI (345 lines) [NEW]
│   ├── dashboard.py                       # Main dashboard
│   └── styles.css                         # Styling
│
├── deployment/                            # 🚀 GCP Cloud Run Package [NEW]
│   ├── Dockerfile.new                     # Multi-stage Cloud Run build
│   ├── deploy.sh                          # Automated deployment (~500 lines)
│   ├── main.py                            # FastAPI entry point (400+ lines)
│   ├── requirements.txt                   # Python dependencies
│   ├── cloudbuild.yaml                    # Cloud Build CI/CD
│   └── .dockerignore                      # Docker optimization
│
├── docs/                                  # 📚 Documentation
│   ├── AXIOM_COMPLETE.md                  # Architecture summary (440 lines)
│   ├── DESIGN_SKILLS_INTEGRATION.md       # Design engine guide (347 lines) [NEW]
│   ├── REGISTRIES_OVERVIEW.md             # Registry documentation (799 lines) [NEW]
│   ├── DEPLOYMENT_GUIDE.md                # Full deployment walkthrough
│   ├── QUICK_START_DEPLOYMENT.md          # 15-minute quickstart [NEW]
│   └── images/
│       ├── agent_pjm_core_components.png
│       └── react_loop_pjmai.png
│
├── tests/                                 # 🧪 Test Suite
│   ├── test_graph.py
│   ├── test_agents.py
│   ├── test_design_engine.py              # [NEW]
│   └── test_integrations.py
│
├── data/                                  # 📊 Sample Data & Configs
│   ├── sample_queries.json
│   └── sample_evidence.json
│
├── logging/                               # 📋 Logging Configuration
│   ├── logger.py
│   └── handlers.py
│
├── README_COMPLETE.md                     # THIS FILE [NEW - UNIFIED]
├── README.md                              # Original README (backup)
├── requirements.txt                       # Main dependencies
├── setup.py                               # Package setup
└── .gitignore                             # Git ignore patterns
```

**New/Updated Files in this version:**
- ✅ `orchestrator/master_nodes.py` - Unified implementation
- ✅ `orchestrator/advanced_nodes.py` - Cross-handoff, synthesis, visual gen
- ✅ `orchestrator/design_skills_engine.py` - Professional SVG rendering
- ✅ `streamlit_components/hitl_renderer.py` - HITL UI
- ✅ `deployment/` - Complete GCP Cloud Run package
- ✅ `docs/DESIGN_SKILLS_INTEGRATION.md` - Integration guide
- ✅ `docs/REGISTRIES_OVERVIEW.md` - Registry documentation
- ✅ `docs/QUICK_START_DEPLOYMENT.md` - Quick start guide

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Google Cloud Platform account with project
- gcloud CLI installed
- Docker installed (for Cloud Run deployment)
- Git

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/AXIOM_Hackathon-main.git
cd AXIOM_Hackathon-main

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
gcloud auth application-default login

# 5. Configure environment variables
cp .env.example .env
# Edit .env with your GCP project ID, etc.

# 6. Initialize data stores (Firestore, BigQuery, Neo4j)
python scripts/init_datastores.py

# 7. Verify setup
python -c "from orchestrator.gcp_client import GCPClient; print('✅ Setup complete')"
```

### Environment Variables

```bash
# .env file
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
FIRESTORE_DATABASE=axiom-db
BIGQUERY_DATASET=axiom_data
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
GEMINI_MODEL=gemini-2.0-flash
ENVIRONMENT=development
DEBUG=true
```

---

## Deployment to GCP Cloud Run

### Quick Start (5 Minutes)

```bash
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Make deploy script executable
chmod +x deploy.sh

# 3. Deploy to production
./deploy.sh prod us-central1

# That's it! Service is running.
```

### What the Deploy Script Does

```
./deploy.sh [environment] [region]
     │
     ├─→ ✅ Check prerequisites (gcloud, docker, auth)
     ├─→ ✅ Validate GCP configuration
     ├─→ ✅ Create IAM service account with minimal roles
     ├─→ ✅ Setup Firestore (if not exists)
     ├─→ ✅ Setup BigQuery datasets
     ├─→ ✅ Build multi-stage Docker image
     ├─→ ✅ Push image to Google Container Registry
     ├─→ ✅ Deploy to Cloud Run
     ├─→ ✅ Verify health endpoint
     └─→ ✅ Generate deployment summary
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GCP PROJECT                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CLOUD RUN (axiom-orchestrator-prod)                 │   │
│  │ ├─ Memory: 2Gi                                      │   │
│  │ ├─ CPU: 2                                           │   │
│  │ ├─ Timeout: 3600s                                  │   │
│  │ ├─ Max instances: 10                               │   │
│  │ └─ Service account: axiom-orchestrator@proj.iam... │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              │                                              │
│    ┌─────────┼─────────┬──────────────┬─────────────────┐  │
│    │         │         │              │                 │  │
│    ▼         ▼         ▼              ▼                 ▼  │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │Gemi- │ │Firestor│ │BigQuery│ │Neo4j     │ │Cloud     │  │
│  │ni    │ │e       │ │        │ │AuraDB    │ │Storage   │  │
│  │API   │ │(state) │ │(data)  │ │(graph)   │ │(code)    │  │
│  └──────┘ └────────┘ └────────┘ └──────────┘ └──────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Modes

| Mode | Command | Use Case |
|------|---------|----------|
| **Production** | `./deploy.sh prod us-central1` | Live users |
| **Staging** | `./deploy.sh staging us-west1` | Testing before production |
| **Development** | `docker build -f Dockerfile.new -t axiom .` | Local testing |

### Verify Deployment

```bash
# Get service URL
gcloud run services describe axiom-orchestrator-prod \
  --region us-central1 --format="value(status.url)"

# Test health endpoint
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://axiom-orchestrator-prod-xxxxx.run.app/health

# View logs
gcloud run logs read axiom-orchestrator-prod --region us-central1 --limit 50

# Monitor metrics (set up Cloud Monitoring dashboard)
gcloud monitoring dashboards create --config-from-file=monitoring.yaml
```

---

## Running AXIOM

### 1. Interactive CLI

```bash
# Direct query
python main.py "What's the delivery risk of GH-ISSUE-107?"

# Output:
# ┌──────────────────────────────┐
# │ AXIOM Response               │
# │                              │
# │ Delivery Risk: HIGH          │
# │ Confidence: 92%              │
# │ Evidence: [3 defects found]  │
# │ Recommendation: Replan       │
# └──────────────────────────────┘
```

### 2. FastAPI + OpenAPI Docs

```bash
# Start server
python -m uvicorn deployment.main:app --reload --host 0.0.0.0 --port 8080

# Visit http://localhost:8080/docs for interactive API explorer

# Example POST request:
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Root cause of proximity_controller bug?",
    "context": {
      "issue_id": "GH-ISSUE-107",
      "master": "auto"
    }
  }'
```

### 3. Streamlit Dashboard

```bash
# Start dashboard
streamlit run streamlit_app.py

# Visit http://localhost:8501

# Features:
# ├─ Query input form
# ├─ Real-time streaming response
# ├─ Visualization rendering
# ├─ HITL checkpoint buttons
# └─ Conversation history
```

### 4. Cloud Run (Production)

```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Query deployed service
curl -H "Authorization: Bearer $TOKEN" \
  -X POST https://axiom-orchestrator-prod-xxxxx.run.app/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "4-pillar health assessment for project PJM-2024",
    "master": "pm"
  }'

# Response:
# {
#   "response_id": "resp-12345",
#   "structured_answer": {
#     "delivery_risk": "MEDIUM",
#     "confidence": 0.94,
#     "evidence_count": 7,
#     "summary": "...",
#     "findings": [...]
#   },
#   "visualization_url": "https://storage.googleapis.com/...",
#   "timestamp": "2026-10-16T14:32:00Z"
# }
```

---

## Example Queries

### PM.ai Query Examples

```
Query 1: Defect Triage
Input:  "What's the blast radius of GH-ISSUE-107?"

Routing: PM.ai (defect_triage capability)
Evidence: [defect_correlation, dependency_risk]
Flow:    REASON → MEMORY → PLAN → defect_agent → SYNTHESIZE → VISUAL_GEN
Visual:  leakage_propagation_chain diagram (Error → Defect → Failure)

Output:
  ├─ Severity: CRITICAL
  ├─ Affected Teams: Backend, QA, Release
  ├─ Sprint Impact: -18 velocity points
  ├─ Mitigation: Revert + 2-day fix + retest
  └─ Diagram: [SVG showing leakage stages]

---

Query 2: Project Health
Input:  "4-pillar health dashboard for Sprint 24?"

Routing: PM.ai (project_health capability)
Evidence: [velocity, defects, test coverage, resources]
Flow:    REASON → MEMORY → PLAN → resource_agent + test_agent → SYNTHESIZE → VISUAL_GEN
Visual:  project_health_dashboard (risk cards + sprint status)

Output:
  ├─ Delivery Risk: HIGH (🔴)
  ├─ Quality Risk: MEDIUM (🟡)
  ├─ Velocity: -22% vs. baseline
  ├─ Test Coverage: 67% (below 80% target)
  ├─ Team Capacity: 18% overloaded
  └─ Diagram: [SVG showing 4-pillar metrics]

---

Query 3: Sprint Replanning
Input:  "Sprint 4 is -18pts, replan for Q4"

Routing: PM.ai (sprint_replanning capability)
Evidence: [velocity_analysis, resource_capacity]
Flow:    REASON → MEMORY → PLAN → resource_agent → SYNTHESIZE → VISUAL_GEN
Visual:  sprint_impact_timeline (capacity heatmap)

Output:
  ├─ Rebalanced scope: 42pts → 35pts
  ├─ Recommended action: Move 7pts to Sprint 5
  ├─ Teams affected: Backend (3pts), QA (2pts), Release (2pts)
  ├─ New velocity estimate: 35pts (80% confidence)
  └─ Diagram: [SVG showing team load across 4 sprints]
```

### ENG.ai Query Examples

```
Query 1: Code Root Cause
Input:  "Deep RCA for proximity_controller.py bug?"

Routing: ENG.ai (root_cause_analysis capability)
Evidence: [code_quality, root_cause_discovery]
Flow:    REASON → MEMORY → PLAN → codefix_agent → SYNTHESIZE → VISUAL_GEN
Visual:  fishbone diagram (RCA categories)

Output:
  ├─ Root Cause: ValidationHelper.checkBounds() missing null check
  ├─ Affected Code: Line 143-145 of proximity_controller.py
  ├─ Git Commit: abc1234def (introduced in PR #8765)
  ├─ Detection Gap: No unit test for null input
  ├─ Patch: [Surgical fix proposed]
  └─ Diagram: [SVG fishbone with 4 RCA categories]

---

Query 2: Test Coverage Gaps
Input:  "Coverage gaps for REQ-L5-001 (validation)?"

Routing: ENG.ai (test_coverage_analysis capability)
Evidence: [test_coverage_analysis, code_quality]
Flow:    REASON → MEMORY → PLAN → test_agent → SYNTHESIZE → VISUAL_GEN
Visual:  coverage report (test matrix)

Output:
  ├─ Current Coverage: 73%
  ├─ Missing: Null input validation (edge case)
  ├─ Missing: Unicode character handling (integration)
  ├─ Missing: Performance under load (system)
  ├─ Recommended Tests: [3 test cases]
  └─ Diagram: [SVG showing requirement-to-test traceability]

---

Query 3: Architecture Review
Input:  "Design validation for new caching layer?"

Routing: ENG.ai (architecture_review capability)
Evidence: [architecture_validation, code_quality]
Flow:    REASON → MEMORY → PLAN → requirement_agent + codefix_agent → SYNTHESIZE
Visual:  none (text-only architecture assessment)

Output:
  ├─ Design Review: APPROVED with recommendations
  ├─ Concern 1: Cache invalidation strategy unclear
  ├─ Concern 2: Memory overhead not estimated
  ├─ Recommendation: Add TTL + LRU eviction policy
  └─ Design Pattern: Aligned with CQRS (✅)
```

---

## Safety Guardrails

AXIOM implements multiple layers of safety to prevent harmful outputs and ensure correctness:

### 1. Evidence Grounding

```
┌──────────────────────────────────┐
│  SYNTHESIZE NODE                  │
├──────────────────────────────────┤
│                                  │
│  Before generating response:     │
│  ├─ Check evidence_envelopes     │
│  ├─ Validate data quality        │
│  ├─ Verify confidence thresholds │
│  └─ Require citations to sources │
│                                  │
│  If insufficient:                │
│  └─→ Loop back to PLAN (max 5x)  │
│                                  │
└──────────────────────────────────┘

Safety Rule: NEVER synthesize without verified evidence.
```

### 2. Read-Only Agent Access

All agents have **query-only** permissions (no writes):

| Agent | Allowed Operations | Blocked Operations |
|-------|--------------------|--------------------|
| requirement_agent | SELECT, TRAVERSE | CREATE, UPDATE, DELETE |
| test_agent | SELECT, ANALYZE | WRITE, MODIFY |
| defect_agent | SELECT, FETCH | CREATE ISSUE, CLOSE |
| resource_agent | SELECT, QUERY | ASSIGN, MODIFY HOURS |
| codefix_agent | AST ANALYZE, PARSE | COMMIT, PUSH |

### 3. Deterministic Validation

Code patches must pass validation before presentation:

```python
# CodeFix Agent before returning patch
proposed_patch = generate_surgical_patch(root_cause)

# VALIDATION GATE
ast.parse(original_code)        # ✅ Parse original
patched_code = apply_patch(proposed_patch)
try:
    ast.parse(patched_code)     # ✅ Parse patched
    compile(patched_code, '<string>', 'exec')  # ✅ Compile works
except SyntaxError:
    return {"status": "REJECTED", "reason": "Syntax error in patch"}
```

### 4. Human Approval (HITL)

Every response pauses at HUMAN_VALIDATE node:

```
SYNTHESIZE
  │ (structured answer + visualization)
  ▼
HUMAN_VALIDATE
  ├─ Display answer
  ├─ Display visualization
  └─ Require approval before delivery
      ├─ ✅ APPROVE → End (deliver)
      ├─ ❌ REJECT → Restart from REASON
      └─ 📝 REQUEST_MORE → Loop to PLAN (max 2x)
```

### 5. Recursion Prevention

Cross-master handoff has built-in prevention:

```
PM.ai Analysis
  │
  ├─ Check: cross_handoff_done == False?
  ├─ If True: Skip handoff (already did one)
  └─ If False: Allow ONE handoff to ENG.ai
      │
      └─→ ENG.ai Analysis
          ├─ Set: cross_handoff_done = True
          └─ Return to PM.ai (NO further handoffs)
```

### 6. Loop Limits

| Loop | Limit | Reason |
|------|-------|--------|
| PLAN iteration (evidence gathering) | Max 5 | Prevent infinite loops |
| HITL feedback (REQUEST_MORE) | Max 2 | Prevent analysis paralysis |
| Cross-handoff | Max 1 | Prevent ping-pong |
| Total query time | 3600s timeout | Prevent hung processes |

### 7. Input Validation

All user inputs validated at system boundary:

```python
# FastAPI endpoint
@app.post("/query")
def query(request: QueryRequest):
    # Validate query length
    if len(request.query) > 5000:
        raise ValueError("Query too long")
    
    # Validate master selection
    if request.master not in ["pm", "eng", "auto"]:
        raise ValueError("Invalid master")
    
    # Sanitize for LLM input
    safe_query = sanitize_for_llm(request.query)
    
    return axiom_runner.run(safe_query, request.master)
```

---

## System Statistics

| Metric | Value |
|--------|-------|
| **Architecture** | 9-node unified LangGraph |
| **Code Duplication** | 0% (single framework) |
| **Masters** | 2 (AXIOM-PM, AXIOM-ENG) |
| **Specialized Agents** | 5 (requirement, test, defect, resource, codefix) |
| **PM Capabilities** | 12 |
| **ENG Capabilities** | 10 |
| **Total Capabilities** | 22 |
| **PM Skills** | 5 |
| **ENG Skills** | 5 |
| **Shared Skills** | 1 (defect_correlation) |
| **Total Skills** | 11 |
| **Visualization Types** | 6 (fishbone, 5-why, timeline, leakage, health, heatmap) |
| **Semantic Colors** | 6 (Red, Orange, Green, Blue, Gray, White) |
| **Typography Levels** | 4 (Title, Heading, Label, Detail) |
| **Data Stores** | 4 (Firestore, BigQuery, Neo4j, Git) |
| **Safety Layers** | 7 (evidence grounding, read-only, validation, HITL, recursion prevention, loop limits, input validation) |
| **Max Query Time** | 3600 seconds |
| **LLM Model** | Gemini 2.0 Flash |
| **Embedding Dimension** | 768 |
| **Vector Store** | BigQuery VECTOR_SEARCH |
| **Cloud Platform** | Google Cloud Run |
| **Container Memory** | 2Gi |
| **Container CPU** | 2 |
| **Max Instances** | 10 |
| **Min Instances** | 1 |

---

## Troubleshooting

### Deployment Issues

**Problem:** `gcloud command not found`
```
Solution: Install Google Cloud SDK from https://cloud.google.com/sdk/install
```

**Problem:** `Docker build failed`
```
Solution: Ensure Docker is running and has sufficient disk space
         docker system prune  # Free up space
         ./deploy.sh prod us-central1  # Retry
```

**Problem:** `Health check failed`
```
Solution: Check Cloud Run logs:
         gcloud run logs read axiom-orchestrator-prod --limit 50
         Service may still be warming up (wait 30-60 seconds)
```

### Runtime Issues

**Problem:** `Evidence cache miss in MEMORY node`
```
Solution: First time running, cache miss is expected
         Subsequent runs will hit cache for identical queries
```

**Problem:** `Cross-handoff timeout`
```
Solution: One master is not responding
         Check Cloud Logs for error details
         Increase timeout: edit orchestrator/advanced_nodes.py
```

**Problem:** `Visualization generation failed`
```
Solution: Check response_mode (text_only doesn't need visual)
         Verify design specs in design_skills_engine.py
         Check SVG for syntax errors
```

---

## Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| **Cache Hit (MEMORY)** | <100ms | Firestore lookup |
| **Single Agent Call** | 500-2000ms | Depends on tool |
| **Evidence Synthesis (LLM)** | 1-3s | Gemini response |
| **Visualization Generation** | 200-500ms | SVG rendering |
| **Full Query (cache miss)** | 5-10s | Typical flow |
| **Full Query (with handoff)** | 10-15s | PM→ENG communication |
| **HITL Timeout** | 3600s | Before auto-reject |

---

## Development Guide

### Adding a New Visualization Type

1. **Add DesignSpec** to `orchestrator/design_skills_engine.py`:
```python
@staticmethod
def your_viz_type() -> DesignSpec:
    return DesignSpec(
        viz_type="your_viz_type",
        title="Your Visualization",
        # ... define width, height, colors, rules, icons
    )
```

2. **Register in VisualizationEngine**:
```python
def render(self, viz_type: str, ...):
    elif viz_type == "your_viz_type":
        return self._render_your_viz_type(design, data, output_format)
```

3. **Implement renderer**:
```python
def _render_your_viz_type(self, design: DesignSpec, data: Dict, output_format: str) -> str:
    # Generate SVG
    svg_lines = [...]
    return "\n".join(svg_lines)
```

4. **Test**:
```python
# tests/test_design_engine.py
def test_your_viz_type():
    engine = VisualizationEngine()
    svg = engine.render("your_viz_type", {"title": "Test"})
    assert "your_viz_type" in svg
```

### Adding a New Agent

1. **Create agent directory**: `agents/your_agent/`
2. **Define ReAct loop**: `agent.py` with tools and prompt
3. **Register in agent_registry.json**:
```json
{
  "agent_id": "your_agent",
  "tools": [...],
  "evidence_types": [...]
}
```
4. **Map to capability**: Update `capability_matrix.json`
5. **Test**: `pytest tests/test_agents.py::test_your_agent`

---

## Contributing

AXIOM welcomes contributions! Please follow these guidelines:

1. **Code Style**: Follow PEP 8
2. **Testing**: 80%+ coverage required
3. **Documentation**: Update docstrings and README
4. **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)
5. **PRs**: Include tests + documentation

```bash
# Set up development
git clone ...
pip install -e .[dev]
pytest  # Run tests
black .  # Format code
```

---

## License

Apache 2.0 License - See LICENSE file

---

## Support & Documentation

- **Architecture**: [AXIOM_COMPLETE.md](docs/AXIOM_COMPLETE.md)
- **Design Skills**: [DESIGN_SKILLS_INTEGRATION.md](docs/DESIGN_SKILLS_INTEGRATION.md)
- **Registries**: [REGISTRIES_OVERVIEW.md](docs/REGISTRIES_OVERVIEW.md)
- **Quick Start**: [QUICK_START_DEPLOYMENT.md](docs/QUICK_START_DEPLOYMENT.md)
- **Full Deployment**: [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

## Changelog

### Current Release
- ✅ 9-node unified LangGraph
- ✅ Design Skills Engine (SVG visualizations)
- ✅ HITL Checkpoint with Streamlit UI
- ✅ Cross-Master Handoff (PM ↔ ENG)
- ✅ GCP Cloud Run deployment
- ✅ Config-driven prompts (v3 JSON)
- ✅ LLM-driven semantic router
- ✅ Evidence grounding with loop limits

### Roadmap
- 🔄 PNG export (raster images)
- 🔄 Real-time streaming responses
- 🔄 Advanced caching strategies (Redis)
- 🔄 Multi-language support
- 🔄 Mobile app integration
- 🔄 Analytics dashboard

---

**Made with ⬡ by the AXIOM team**
