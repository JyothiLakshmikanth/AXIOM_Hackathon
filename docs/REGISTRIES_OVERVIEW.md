# AXIOM Registries Overview

**Status:** ✅ All registries created and configured  
**Location:** `registries/` directory  
**Purpose:** Define agents, capabilities, and skills available to PM.ai and ENG.ai masters

---

## 📋 Registry Architecture

```
Three-Layer Registry System:

┌─────────────────────────────────────────────────────────┐
│ CAPABILITIES (What masters CAN DO)                      │
│ capability_matrix.json                                  │
│ ├─ PM.ai Capabilities (12 total)                       │
│ └─ ENG.ai Capabilities (10 total)                       │
└────────────────┬────────────────────────────────────────┘
                 │ depends on
┌────────────────▼────────────────────────────────────────┐
│ SKILLS (HOW they do it)                                 │
│ skill_registry.json                                     │
│ ├─ PM.ai Skills (5 total)                              │
│ └─ ENG.ai Skills (5 total)                              │
└────────────────┬────────────────────────────────────────┘
                 │ enables
┌────────────────▼────────────────────────────────────────┐
│ AGENTS (WHO gathers evidence)                           │
│ agent_registry.json                                     │
│ └─ 5 Specialized Agents                                │
│    ├─ requirement_agent (Neo4j)                        │
│    ├─ test_agent (BigQuery)                            │
│    ├─ defect_agent (BigQuery/GitHub)                   │
│    ├─ resource_agent (BigQuery/Qdrant)                 │
│    └─ codefix_agent (Git AST)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 1️⃣ AGENT REGISTRY (agent_registry.json)

**5 Specialized LangChain ReAct Agents**

### requirement_agent
```json
{
  "name": "Requirement Traceability Specialist Agent",
  "primary_store": "Neo4j Knowledge Graph",
  "capabilities": [
    "Requirement entity lookup",
    "Upstream/downstream trace traversal",
    "Acceptance criteria extraction",
    "Cross-component ripple impact scoring",
    "Specification ambiguity detection"
  ],
  "tools": [
    "neo4j_query_requirement_by_id",
    "neo4j_get_traceability_graph",
    "neo4j_find_dependent_components",
    "qdrant_semantic_search_requirements"
  ],
  "evidence_types": [
    "requirement_record",
    "traceability_edges",
    "acceptance_criteria",
    "ripple_subgraph"
  ]
}
```

### test_agent
```json
{
  "name": "Test & Verification Specialist Agent",
  "primary_store": "BigQuery & Cloud Storage",
  "capabilities": [
    "Test execution history analysis",
    "Test coverage gap computation",
    "Targeted regression test generation",
    "Boundary and oscillation test suite synthesis",
    "Requirement-to-test matrix mapping"
  ],
  "tools": [
    "bigquery_get_test_run_results",
    "bigquery_get_coverage_summary",
    "neo4j_get_tests_for_requirement",
    "generate_pytest_boundary_suite"
  ],
  "evidence_types": [
    "test_run_failure_log",
    "branch_coverage_report",
    "requirement_test_matrix",
    "synthesized_test_case"
  ]
}
```

### defect_agent
```json
{
  "name": "Defect & Issue Intelligence Specialist Agent",
  "primary_store": "BigQuery & GitHub Tracker",
  "capabilities": [
    "GitHub issue retrieval and deduplication",
    "Defect severity & urgency scoring",
    "Leakage direction categorization",
    "Historical bug pattern matching",
    "Sprint defect density assessment"
  ],
  "tools": [
    "bigquery_get_defect_by_issue_id",
    "bigquery_list_open_defects_by_sprint",
    "github_fetch_issue_metadata",
    "firestore_check_cached_defect_evidence"
  ],
  "evidence_types": [
    "github_issue_record",
    "defect_leakage_assessment",
    "component_defect_density",
    "severity_urgency_matrix"
  ]
}
```

### resource_agent
```json
{
  "name": "Resource & Capacity Intelligence Specialist Agent",
  "primary_store": "Qdrant Vector DB & BigQuery",
  "capabilities": [
    "Team velocity and volatility tracking",
    "Engineer capacity and allocation modeling",
    "Holiday and time-off schedule incorporation",
    "Skill affinity to task matching",
    "Sprint replanning load rebalancing"
  ],
  "tools": [
    "bigquery_get_team_velocity_history",
    "bigquery_get_sprint_allocations",
    "qdrant_search_team_skills_and_manifest",
    "compute_rebalanced_sprint_capacity"
  ],
  "evidence_types": [
    "sprint_velocity_record",
    "engineer_capacity_envelope",
    "reallocation_plan",
    "team_burn_rate"
  ]
}
```

### codefix_agent
```json
{
  "name": "Code Analysis & Surgical Fix Specialist Agent",
  "primary_store": "Cloud Storage & Synthetic Git",
  "capabilities": [
    "Deterministic root cause AST inspection",
    "Git commit diff and regression isolation",
    "Surgical patch generation (hysteresis/boundary handling)",
    "Syntax validation and lint check verification",
    "GitHub PR proposal creation"
  ],
  "tools": [
    "git_get_commit_diff",
    "git_inspect_source_file",
    "ast_analyze_code_structure",
    "generate_surgical_patch",
    "validate_patch_syntax"
  ],
  "evidence_types": [
    "git_commit_diff",
    "source_ast_inspection",
    "proposed_surgical_patch",
    "syntax_validation_receipt"
  ]
}
```

---

## 2️⃣ SKILL REGISTRY (skill_registry.json)

**10 Cognitive Skills (5 PM.ai + 5 ENG.ai)**

### PM.ai Skills

#### velocity_analysis_skill
```json
{
  "skill_name": "Velocity Analysis Skill",
  "competence": "Computes sprint completion rates, volatility metrics, commitment-vs-delivered ratios",
  "required_evidence": [
    "sprint_velocity_record",
    "story_point_burn_rate",
    "historical_sprint_aggregates"
  ],
  "evaluation_criteria": [
    "Minimum 3 historical sprints analyzed for rolling average",
    "Volatility standard deviation computed",
    "Variance between committed and completed story points"
  ],
  "visual_trigger": "burndown_and_velocity_trend"
}
```

#### defect_correlation_skill
```json
{
  "skill_name": "Defect Correlation Skill",
  "competence": "Correlates reported defects with system requirements, impacted test cases, and delivery milestones",
  "required_evidence": [
    "github_issue_record",
    "requirement_traceability_link",
    "test_run_failure_log",
    "component_defect_density"
  ],
  "evaluation_criteria": [
    "Defect severity and reproduction state verified",
    "At least one requirement node linked",
    "Probable leakage direction classified"
  ],
  "visual_trigger": "defect_leakage_flow"
}
```

#### test_coverage_analysis_skill
```json
{
  "skill_name": "Test Coverage Analysis Skill",
  "competence": "Measures requirement-to-test traceability gaps, edge-case omissions, branch coverage deficits",
  "required_evidence": [
    "test_coverage_report",
    "requirement_test_matrix",
    "missing_test_cases"
  ],
  "visual_trigger": "coverage_heat_map"
}
```

#### resource_capacity_skill
```json
{
  "skill_name": "Resource Capacity Skill",
  "competence": "Models team utilization, capacity planning, and reallocation strategies",
  "visual_trigger": "resource_workload_heatmap"
}
```

#### dependency_risk_skill
```json
{
  "skill_name": "Dependency Risk Skill",
  "competence": "Analyzes cross-project dependencies and blast radius impact",
  "visual_trigger": "dependency_matrix"
}
```

### ENG.ai Skills

#### root_cause_discovery_skill
```json
{
  "skill_name": "Root Cause Discovery Skill",
  "competence": "Pinpoints code-level root cause via AST syntax, git diffs, regression points",
  "required_evidence": [
    "git_commit_diff",
    "source_ast_inspection",
    "failing_test_stacktrace",
    "code_traceability_edge"
  ],
  "evaluation_criteria": [
    "Regression-introducing commit identified with hash",
    "Exact file, function, and line-level boundary isolated",
    "Deterministic reproduction validated"
  ],
  "visual_trigger": "causal_flow_ast_diff"
}
```

#### architecture_validation_skill
```json
{
  "skill_name": "Architecture Validation Skill",
  "competence": "Validates system design against patterns, coupling, abstraction principles"
}
```

#### code_quality_skill
```json
{
  "skill_name": "Code Quality Skill",
  "competence": "Analyzes complexity, maintainability, and technical debt"
}
```

#### performance_optimization_skill
```json
{
  "skill_name": "Performance Optimization Skill",
  "competence": "Profiles bottlenecks, scalability constraints, optimization opportunities"
}
```

#### security_assessment_skill
```json
{
  "skill_name": "Security Assessment Skill",
  "competence": "Identifies vulnerabilities, threat models, security validation"
}
```

---

## 3️⃣ CAPABILITY MATRIX (capability_matrix.json)

**PM.ai Capabilities (12 total)**

| Capability | Category | Required Skills | Candidate Agents | Visual Format |
|-----------|----------|-----------------|------------------|---------------|
| preliminary_rca | project_governance | defect_correlation, dependency_risk | defect, requirement | dependency_blast_radius |
| defect_triage | defect_management | defect_correlation, dependency_risk | defect, requirement, test | risk_priority_matrix |
| project_health | project_governance | velocity_analysis, defect_correlation, test_coverage, resource_capacity | resource, defect, test | project_health_dashboard |
| sprint_replanning | sprint_operations | velocity_analysis, resource_capacity, sprint_timeline | resource, requirement | burn_down_replan_trajectory |
| sprint_timeline_analysis | sprint_operations | sprint_timeline, velocity_analysis | resource, requirement | gantt_milestone_variance |
| requirement_impact | requirement_management | dependency_risk, test_coverage | requirement, test | traceability_impact_tree |
| test_readiness | quality_assurance | test_coverage_analysis, defect_correlation | test, defect, requirement | coverage_heat_map |
| cross_project_dependency | portfolio_management | dependency_risk, velocity_analysis | requirement, resource | portfolio_dependency_matrix |
| decision_brief | executive_governance | defect_correlation, velocity_analysis | defect, resource | decision_comparison_matrix |
| assignment_recommendation | team_operations | resource_capacity, defect_correlation | resource, requirement | skill_workload_fit_matrix |
| defect_hotspot_analysis | defect_analytics | defect_correlation, velocity_analysis | defect, test | defect_density_heat_map |
| prevention_intelligence | quality_management | defect_correlation, test_coverage | defect, test, requirement | leakage_prevention_flow |

**ENG.ai Capabilities (10 total)**

| Capability | Category | Required Skills | Candidate Agents | Visual Format |
|-----------|----------|-----------------|------------------|---------------|
| root_cause_analysis | technical_rca | root_cause_discovery, code_quality | codefix, test, requirement | causal_flow_ast_diff |
| architecture_review | design_validation | architecture_validation, code_quality | requirement, test | architecture_pattern_diagram |
| code_quality | code_analysis | code_quality, root_cause_discovery | codefix, test | complexity_maintainability_matrix |
| test_coverage_analysis | quality_assurance | test_coverage_analysis, code_quality | test, codefix, requirement | branch_coverage_heat_map |
| performance_analysis | optimization | performance_optimization, code_quality | codefix, test | performance_bottleneck_flame_graph |
| security_assessment | security | security_assessment, code_quality | codefix, requirement, test | threat_model_attack_tree |
| design_validation | design_review | architecture_validation, code_quality | requirement, test | design_pattern_adherence |
| correction_design | implementation | root_cause_discovery, code_quality | codefix | surgical_patch_diff |
| itpa_test_prioritization | test_strategy | test_coverage_analysis, performance_optimization | test, codefix | test_priority_matrix |
| code_ripple_analysis | impact_analysis | code_quality, root_cause_discovery | codefix, requirement, test | code_dependency_graph |

---

## 🔄 How Registries Work Together

### Flow: User Query → Master Selection → Capability → Agents

```
User Query: "What's the delivery risk of this defect?"
    ↓
Router → AXIOM-PM (delivery-focused)
    ↓
REASON Node → Selects capability from PM capabilities
    └─ Match: "defect_triage"
    ↓
PLAN Node → Query capability_matrix.json
    {
      "capability_id": "defect_triage",
      "required_skills": ["defect_correlation_skill", "dependency_risk_skill"],
      "candidate_agents": ["defect_agent", "requirement_agent", "test_agent"]
    }
    ↓
PLAN Node → Query skill_registry.json
    {
      "defect_correlation_skill": {
        "evaluation_criteria": [...],
        "candidate_agents": ["defect_agent", "requirement_agent", "test_agent"]
      }
    }
    ↓
PLAN Node (LLM decision) → "Which agent best fills this evidence gap?"
    └─ Decision: Call defect_agent
    ↓
EXECUTE Node → Query agent_registry.json
    {
      "agent_id": "defect_agent",
      "tools": ["bigquery_get_defect_by_issue_id", ...],
      "evidence_types": ["github_issue_record", "severity_urgency_matrix"]
    }
    ↓
EXECUTE Node → Call defect_agent with specific tools
    ├─ Tool: bigquery_get_defect_by_issue_id
    ├─ Tool: bigquery_list_open_defects_by_sprint
    └─ Tool: github_fetch_issue_metadata
    ↓
OBSERVE Node → Receive evidence (severity_urgency_matrix)
    ↓
EVALUATE Node → Check sufficiency
    "Do we have enough evidence for defect_triage capability?"
    Required skills: [defect_correlation ✓, dependency_risk ✓]
    Collected evidence: [github_issue ✓, severity ✓, urgency ✓]
    Sufficiency: SUFFICIENT
    ↓
SYNTHESIZE → Generate answer with visual_affinity = high
    Visual format: risk_priority_matrix
```

---

## 🎯 Registry Lookup in Code

### From planner_node.py
```python
from registries.agent_registry import AGENT_REGISTRY
from registries.capability_matrix import CAPABILITY_MATRIX
from registries.skill_registry import SKILL_REGISTRY

# Get capability definition
capability = CAPABILITY_MATRIX["defect_triage"]
required_skills = capability["required_skills"]  # [defect_correlation_skill, ...]
candidate_agents = capability["candidate_agents"]  # [defect_agent, requirement_agent, ...]

# Get skill details
skill = SKILL_REGISTRY["defect_correlation_skill"]
evaluation_criteria = skill["evaluation_criteria"]
candidate_agents_for_skill = skill["candidate_agents"]

# Get agent details
agent = AGENT_REGISTRY["defect_agent"]
tools = agent["tools"]
evidence_types = agent["supported_evidence_types"]

# LLM Decision: "Which agent best fills the gap?"
# → "Call defect_agent because it provides [severity_urgency_matrix]"
```

---

## 📊 Registry Statistics

### Agent Count
- **Total Agents:** 5
- **PM.ai Capable Agents:** 5 (all)
- **ENG.ai Capable Agents:** 5 (all)
- **Shared Agents:** 2 (defect_agent, requirement_agent, test_agent used by both)

### Capability Count
- **PM.ai Capabilities:** 12
- **ENG.ai Capabilities:** 10
- **Total Capabilities:** 22

### Skill Count
- **PM.ai Skills:** 5
- **ENG.ai Skills:** 5
- **Total Skills:** 10
- **Shared Skills:** 1 (defect_correlation_skill used by both masters)

### Data Store Connectivity
| Data Store | Agents | Purpose |
|-----------|--------|---------|
| Neo4j Knowledge Graph | requirement_agent | Traceability, graph queries |
| BigQuery | defect_agent, test_agent, resource_agent | Facts, metrics, history |
| GitHub | defect_agent | Issue tracking, metadata |
| Qdrant Vector DB | requirement_agent, resource_agent | Semantic search, skills |
| Firestore | All agents | Caching, session state |
| Cloud Storage | codefix_agent | Source code, diffs |
| Git | codefix_agent | Commits, history, AST |

---

## ✨ Key Features

✅ **Three-layer design** - Separates concerns (agents, skills, capabilities)  
✅ **Master-aware** - Each capability owned by specific master (PM or ENG)  
✅ **Skill-driven** - Capabilities mapped to required competencies  
✅ **Agent-backed** - Skills enabled by specific agents  
✅ **Dynamic selection** - LLM chooses best agent per evidence gap  
✅ **Visual affinity** - Each capability suggests visualization type  
✅ **Evaluation criteria** - Clear thresholds for skill sufficiency  
✅ **Cross-referenced** - All layers linked for intelligent routing  

---

## 🔍 Using Registries in Workflow

### PLAN Node (planner_node.py)
```python
def plan_node(state):
    # 1. Get master's capabilities
    master = state["target_master"]
    capabilities = get_master_capabilities(master)
    
    # 2. Load capability matrix
    required_skills = CAPABILITY_MATRIX[state["resolved_intent"]]["required_skills"]
    
    # 3. Load skills
    for skill in required_skills:
        skill_def = SKILL_REGISTRY[skill]
        evaluation = check_skill_sufficiency(state["evidence_envelopes"], skill_def)
    
    # 4. Identify evidence gaps
    missing_evidence = identify_gaps(required_skills, state["evidence_envelopes"])
    
    # 5. Select agent
    agent_choice = AGENT_REGISTRY[best_agent_for_gap(missing_evidence)]
    
    # 6. Return decision
    return {
        "agent_id": agent_choice["agent_id"],
        "tools": agent_choice["tools"],
        "evidence_types": agent_choice["supported_evidence_types"]
    }
```

---

## 📁 File Structure

```
registries/
├── agent_registry.json          (5 agents × 10 fields)
├── capability_matrix.json       (22 capabilities × 8 fields)
├── skill_registry.json          (10 skills × 7 fields)
└── README.md                    (This file)
```

---

**Status:** ✅ Complete and operational  
**Last Updated:** 2026-10-16  
**Version:** 1.0.0
