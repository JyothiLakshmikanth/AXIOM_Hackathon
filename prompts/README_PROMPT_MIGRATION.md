# AXIOM Prompts Migration: .md → JSON Format

## Overview

The AXIOM prompts have been successfully converted from Markdown (`.md`) to JSON format to align with the main PJM.ai project's modular prompt architecture. This enables:

- **Programmatic loading** via JSON parsers
- **Section versioning** (immutable vs. dynamic)
- **Shared orchestration rules** across multiple agents
- **Stage-mapped execution** (reason_node, execute_action_node, etc.)
- **Easier maintenance** and updates

## New Files Structure

### 4 New JSON Files in `prompts/`

```
AXIOM_Hackathon-main/prompts/
├── axiom_pm_master_v3.json         # PM.ai Master Orchestrator
├── axiom_eng_master_v3.json        # ENG.ai Master Orchestrator
├── axiom_router_v3.json            # Intent Router
├── axiom_prompts_common.json       # Shared orchestration sections
└── README_PROMPT_MIGRATION.md      # This file
```

### Removed (Old Markdown Files)

```
❌ pm_master_prompt.md
❌ eng_master_prompt.md
❌ router_prompt.md
```

---

## File Breakdown

### 1. `axiom_prompts_common.json` ⭐ (NEW)

**Shared orchestration rules** referenced by all three masters.

**Sections:**
- `05_orchestration_framework`: 7-step ReAct reasoning loop (RESOLVE, REQUIRE, INVENTORY, ASSESS, GAP, DELEGATE, SYNTHESIZE)
- `13_output_synthesis`: JSON response format and envelope structure
- `14_presentation_format`: Comprehensive format requirement and output rules
- `17_final_principles`: Evidence-driven, human-centric, boundary-aware principles
- `18_communication_policy`: Clear, concise, unambiguous English (15 rules)
- `20_presentation_system`: Execution rules per LangGraph stage
- `22_planner_decision_system`: 10-step ReAct decision framework
- `23_analyze_outputs_system`: Autonomous sufficiency evaluation
- `24_verify_system`: Quality gate and final verification

**Usage:** Load once at startup, reference by section ID in master prompts.

---

### 2. `axiom_pm_master_v3.json`

**Project Delivery Intelligence** — PM.ai Master Orchestrator

**Structure:**
```json
{
  "agent_name": "axiom_pm_master",
  "version": "3.0",
  "label": "AXIOM PM.ai Master v3.0",
  "description": "...",
  "__imports__": {
    "source": "./axiom_prompts_common.json",
    "sections": ["05_orchestration_framework", "13_output_synthesis", ...]
  },
  "__structure__": {
    "framework_sections": {
      "immutable": ["01_identity_and_mission", "05_non_negotiables", "06_guardrails"],
      "dynamic": ["02_capabilities", "03_skills", "04_specialized_agents", "07_operational_protocol"]
    },
    "stage_to_sections": {
      "reason_node": ["01_identity_and_mission", "02_capabilities", "03_skills", "05_non_negotiables"],
      "execute_action_node": ["04_specialized_agents", "06_guardrails", "22_planner_decision_system"],
      ...
    }
  },
  "01_identity_and_mission": {
    "type": "immutable",
    "stage": "reason_node",
    "title": "Core Identity & Architectural Mission",
    "content": [...]
  },
  ...
}
```

**Key Sections:**
1. **01_identity_and_mission** (immutable): PM.ai role, cognitive loop, mission
2. **02_capabilities** (dynamic): 7 capabilities (preliminary_rca, defect_triage, project_health, sprint_replanning, sprint_timeline_analysis, pi_planning, retrospective)
3. **03_skills** (dynamic): 6 competency skills
4. **04_specialized_agents** (dynamic): 4 delegated agents
5. **05_non_negotiables** (immutable): What PM.ai owns / MUST NOT do
6. **06_guardrails** (immutable): Input, safety, output guardrails
7. **07_operational_protocol** (dynamic): 8-step execution flow

---

### 3. `axiom_eng_master_v3.json`

**Engineering Intelligence** — ENG.ai Master Orchestrator

**Structure:** (mirrors PM.ai with ENG-specific content)

**Key Sections:**
1. **01_identity_and_mission**: ENG.ai role, cognitive loop, mission
2. **02_capabilities**: 6 capabilities (root_cause_analysis, eight_d_analysis, five_why_analysis, code_fixing, test_case_generation, increasing_test_coverage)
3. **03_skills**: 6 engineering skills
4. **04_specialized_agents**: 4 delegated agents (codefix_agent, test_agent, requirement_agent, defect_agent)
5. **05_non_negotiables**: What ENG.ai owns / MUST NOT do
6. **06_guardrails**: Input, safety, output guardrails
7. **07_operational_protocol**: 8-step execution flow

---

### 4. `axiom_router_v3.json`

**Top-Level Intent Router** — Classifies queries and routes to correct master

**Structure:**
```json
{
  "agent_name": "axiom_router",
  "version": "3.0",
  "label": "AXIOM Router v3.0",
  "01_router_identity": {
    "type": "immutable",
    "stage": "router_node",
    "title": "Router Identity & Mission",
    "content": [...]
  },
  "02_routing_boundaries": {
    "type": "immutable",
    "content": [
      "ROUTE TO PM.ai WHEN: delivery, schedule, timeline, risk, team impact, resource, capacity, sprint, release",
      "ROUTE TO ENG.ai WHEN: code, architecture, design, performance, security, quality, testing, ITPA, changelog"
    ]
  },
  "03_clarification_protocol": {
    "type": "dynamic",
    "content": [...]
  },
  "04_json_output_schema": {
    "type": "dynamic",
    "content": ["CLEAR INTENT RESPONSE", "CLARIFICATION RESPONSE", "EXAMPLES"]
  }
}
```

**Output Examples:**
- Clear PM intent → `{ "clarification_needed": false, "target_master": "PM.ai", "confidence_score": 0.95, ... }`
- Clear ENG intent → `{ "clarification_needed": false, "target_master": "ENG.ai", "confidence_score": 0.95, ... }`
- Ambiguous intent → `{ "clarification_needed": true, "clarification_questions": [...], ... }`

---

## JSON Schema & Format

### Top-Level Fields

```json
{
  "agent_name": "axiom_pm_master",          // Unique identifier
  "version": "3.0",                         // Semantic versioning
  "label": "AXIOM PM.ai Master v3.0",      // Display name
  "description": "...",                     // One-line summary
  "__imports__": {
    "source": "./axiom_prompts_common.json", // Path to shared sections
    "sections": ["05_orchestration_framework", ...],  // Which sections to import
    "note": "..."
  },
  "__structure__": {
    "framework_sections": {
      "immutable": [...],  // Stable sections (rarely change)
      "dynamic": [...]     // Versioned sections (updatable)
    },
    "stage_to_sections": {
      "reason_node": [...],
      "execute_action_node": [...],
      ...
    }
  },
  "01_identity_and_mission": { ... },  // Section content
  "02_capabilities": { ... },
  ...
}
```

### Section Format

```json
{
  "type": "immutable|dynamic",
  "stage": "reason_node|execute_action_node|observe_node|synthesize_node|verify_answer_node|router_node",
  "title": "Display name",
  "description": "Brief summary (optional)",
  "content": [
    "Line 1 of content",
    "Line 2 of content",
    "",  // Empty string for spacing
    "Bullet • Item 1",
    "Bullet • Item 2"
  ]
}
```

---

## Loading & Execution

### Python Example

```python
import json

# Load shared sections
with open('axiom_prompts_common.json', 'r') as f:
    common = json.load(f)

# Load PM master
with open('axiom_pm_master_v3.json', 'r') as f:
    pm_master = json.load(f)

# Get stage-specific prompt for reason_node
reason_sections = pm_master['__structure__']['stage_to_sections']['reason_node']
# → ['01_identity_and_mission', '02_capabilities', '03_skills', '05_non_negotiables']

# Construct reason_node prompt
prompt_reason = ""
for section_id in reason_sections:
    section = pm_master[section_id]
    prompt_reason += f"## {section['title']}\n"
    prompt_reason += "\n".join(section['content'])
    prompt_reason += "\n\n"

# Load referenced shared sections
for shared_section_id in pm_master['__imports__']['sections']:
    section = common[shared_section_id]
    prompt_reason += f"## {section['title']}\n"
    prompt_reason += "\n".join(section['content'])
    prompt_reason += "\n\n"

print(prompt_reason)
```

### LangGraph Integration

```python
# In orchestrator/graph.py or similar

def load_prompts():
    """Load AXIOM prompts and construct stage-specific payloads."""
    with open('prompts/axiom_pm_master_v3.json', 'r') as f:
        pm_master = json.load(f)
    
    with open('prompts/axiom_prompts_common.json', 'r') as f:
        common = json.load(f)
    
    return {
        'pm_master': pm_master,
        'common': common,
    }

def reason_node(state):
    """Execute reason_node with appropriate sections."""
    prompts = load_prompts()
    pm = prompts['pm_master']
    
    # Get sections for this stage
    stage_sections = pm['__structure__']['stage_to_sections']['reason_node']
    
    # Build prompt
    prompt = ""
    for section_id in stage_sections:
        section = pm[section_id]
        prompt += f"{section['title']}\n{'-' * 40}\n"
        prompt += "\n".join(section['content']) + "\n\n"
    
    # Add shared sections
    for shared_id in pm['__imports__']['sections']:
        section = prompts['common'][shared_id]
        prompt += f"{section['title']}\n{'-' * 40}\n"
        prompt += "\n".join(section['content']) + "\n\n"
    
    # Call LLM with prompt
    response = llm.invoke(prompt)
    return response
```

---

## Versioning & Maintenance

### Version Scheme

- **Major (e.g., 3.0 → 4.0)**: Immutable section changes (identity, non-negotiables, guardrails)
- **Minor (e.g., 3.0 → 3.1)**: Dynamic section additions/updates (capabilities, skills, agents)
- **Patch (e.g., 3.1.0 → 3.1.1)**: Documentation, typo fixes, clarifications

### Update Workflow

1. **Identify changes**: Which sections are affected?
2. **Check stability**: Immutable vs. dynamic?
3. **Version bump**: Major, minor, or patch?
4. **Update `__last_updated__`**: Date of change
5. **Test loading**: Verify JSON syntax and imports
6. **Deploy**: Push new version to agents

### Example Update

**Original:**
```json
{
  "version": "3.0",
  "__last_updated__": "2026-10-16",
  "02_capabilities": {
    "type": "dynamic",
    "content": [...]
  }
}
```

**After adding capability:**
```json
{
  "version": "3.1",
  "__last_updated__": "2026-10-17",
  "02_capabilities": {
    "type": "dynamic",
    "content": [
      "... existing capabilities ...",
      "8. **New Capability** (`new_capability`)",
      "   Description of new capability."
    ]
  }
}
```

---

## Migration Checklist

- [x] Create `axiom_prompts_common.json` with 9 shared sections
- [x] Create `axiom_pm_master_v3.json` with 7 sections
- [x] Create `axiom_eng_master_v3.json` with 7 sections
- [x] Create `axiom_router_v3.json` with 4 sections
- [x] Update import paths to reference `./axiom_prompts_common.json`
- [ ] Update `orchestrator/graph.py` to load JSON prompts
- [ ] Test prompt loading and stage-mapping
- [ ] Update `agents/` to receive JSON-sourced instructions
- [ ] Update deployment documentation
- [ ] Archive or remove old `.md` files

---

## Comparison: .md vs JSON

| Aspect | .md Format | JSON Format |
|--------|-----------|------------|
| **Readability** | Human-friendly markdown | Structured, machine-parseable |
| **Versioning** | Manual version tracking | Built-in version fields |
| **Maintenance** | Edit prose, risk duplication | Edit sections, shared imports |
| **Automation** | Difficult to parse programmatically | Easy JSON loading |
| **Stage Mapping** | Implicit (reader must infer) | Explicit `stage_to_sections` |
| **Section Reuse** | Copy-paste duplicates | Shared `__imports__` |
| **Testing** | Manual review only | JSON schema validation |

---

## Integration with Main PJM.ai Project

The AXIOM JSON prompts **can coexist** with the main project's prompts:

```
data/prompts_template/
├── prompts_common.json          # Main project shared sections
├── agent_pjm/
│   └── prompts_v3.json          # Main PJM agent prompts
├── agent_eng/
│   └── prompts_v3.json          # Main ENG agent prompts

AXIOM_Hackathon-main/prompts/
├── axiom_prompts_common.json    # AXIOM shared sections
├── axiom_pm_master_v3.json      # AXIOM PM.ai prompts
├── axiom_eng_master_v3.json     # AXIOM ENG.ai prompts
└── axiom_router_v3.json         # AXIOM Router prompts
```

**Advantages:**
- AXIOM remains self-contained with own shared sections
- Can reference main project sections if desired (e.g., `"source": "../../data/prompts_template/prompts_common.json"`)
- No conflicts with main project updates
- Easy to sync shared sections when patterns evolve

---

## Next Steps

1. **Update orchestrator/graph.py** to load and use `axiom_*_v3.json` files
2. **Test prompt loading** with Python JSON parser
3. **Verify stage mapping** (each stage gets correct sections)
4. **Deploy** to agents with new JSON-sourced instructions
5. **Monitor** for missing imports or parse errors
6. **Document** prompt loading in AXIOM's README

---

**Questions?** Refer to:
- `axiom_prompts_common.json` for shared orchestration logic
- `axiom_pm_master_v3.json` for PM.ai capabilities and skills
- `axiom_eng_master_v3.json` for ENG.ai capabilities and skills
- `axiom_router_v3.json` for routing logic and intent classification
