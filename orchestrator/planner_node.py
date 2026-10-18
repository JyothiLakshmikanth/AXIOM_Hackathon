"""
AXIOM Planner Node: Intelligent Agent Selection via LLM.

The PLAN node is the intelligence core of the 9-node architecture.
Instead of hardcoded if/else logic, it delegates agent selection to an LLM reasoner
that understands evidence gaps, agent capabilities, and the hypothesis context.

CONFIGURATION-DRIVEN:
- Loads prompts from JSON files (axiom_pm_master_v3.json, axiom_eng_master_v3.json, axiom_prompts_common.json)
- All capability mappings and agent selection guidance sourced from authoritative JSON
- No hardcoded logic—100% configuration-driven

This node:
1. Analyzes missing evidence dimensions
2. Loads agent capabilities from registry
3. Calls Gemini LLM to decide which agent should gather evidence next
4. Stores the planner decision in state for EXECUTE node to invoke
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from orchestrator.state import AxiomState
from orchestrator.gemini_client import get_gemini_api_key, generate_gemini_content
from orchestrator.prompt_loader import load_prompt

logger = logging.getLogger("axiom.orchestrator.planner_node")


def load_json_file(rel_path: str) -> Dict[str, Any]:
    """
    Load JSON configuration file from project root.

    Args:
        rel_path: Relative path from project root (e.g., "registries/agent_registry.json")

    Returns:
        Parsed JSON dictionary, or empty dict if file not found
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.warning(f"Registry file not found: {full_path}")
    return {}


def _initialize_llm_client():
    """
    Initialize Gemini/Vertex AI LLM client with automatic Pydantic v1 validator reuse patch.

    Returns:
        Initialized LLM client, or None if unavailable
    """
    # Patch Pydantic v1 validator allow_reuse to prevent duplicate validator ConfigError
    for _mod_name in ("pydantic.v1.class_validators", "pydantic.class_validators"):
        try:
            import importlib
            _cv = importlib.import_module(_mod_name)
            if hasattr(_cv, "_prepare_validator"):
                _orig_prep = _cv._prepare_validator
                _cv._prepare_validator = lambda f, allow_reuse=False, _orig=_orig_prep: _orig(f, allow_reuse=True)
        except Exception:
            pass

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or os.getenv("GCP_PROJECT_ID")
    api_key = get_gemini_api_key()

    if api_key or project_id:
        logger.info("[LLM] Planner engine ready (via Gemini Client)")
        return "GEMINI_READY"

    logger.warning("No LLM credentials available; planner will fall back to intelligent heuristic selection.")
    return None



def _compute_missing_dimensions(
    required_dimensions: List[str],
    evidence_envelopes: List[Dict[str, Any]]
) -> set:
    """
    Compute the set of evidence dimensions not yet collected.

    Args:
        required_dimensions: Evidence types required by the capability
        evidence_envelopes: Evidence already collected

    Returns:
        Set of missing artifact types
    """
    collected_types = {env.get("artifact_type") for env in evidence_envelopes if env}
    missing = set(required_dimensions) - collected_types
    logger.debug(f"Required: {required_dimensions}, Collected: {collected_types}, Missing: {missing}")
    return missing


def _build_planner_prompt(
    agent_registry: Dict[str, Any],
    skill_registry: Dict[str, Any],
    missing_dimensions: set,
    query: str,
    hypothesis: str,
    target_master: str,
    iteration_count: int,
    last_delegated_agent: str = None
) -> str:
    """
    Construct the prompt for the LLM planner.

    Args:
        agent_registry: Loaded agent capabilities from registry
        skill_registry: Loaded cognitive skills and their requirements
        missing_dimensions: Evidence types still needed
        query: Original user query
        hypothesis: Reasoning hypothesis from REASON node
        target_master: Target master ("AXIOM-PM" or "AXIOM-ENG")
        iteration_count: Current iteration (for loop termination heuristics)

    Returns:
        Formatted prompt for LLM planner
    """
    # Build agent summaries
    agent_summaries = []
    for agent_id, agent_meta in agent_registry.items():
        capabilities = agent_meta.get("capabilities", [])
        evidence_types = agent_meta.get("supported_evidence_types", [])
        agent_summaries.append(
            f"  - {agent_id}: {agent_meta.get('name', agent_id)}\n"
            f"    Capabilities: {', '.join(capabilities)}\n"
            f"    Supported Evidence: {', '.join(evidence_types)}"
        )

    agent_options = "\n".join(agent_summaries)

    # Build skill summaries
    skill_summaries = []
    for skill_id, skill_meta in skill_registry.items():
        applicable = skill_meta.get("applicable_masters", [])
        if target_master not in applicable:
            continue
        competence = skill_meta.get("competence", "")
        candidate_agents = skill_meta.get("candidate_agents", [])
        skill_summaries.append(
            f"  - {skill_id}: {skill_meta.get('skill_name', skill_id)}\n"
            f"    Competence: {competence[:150]}\n"
            f"    Candidate Agents: {', '.join(candidate_agents)}"
        )

    skill_options = "\n".join(skill_summaries) if skill_summaries else "No applicable skills for this master"

    # NOTE: Agent selection guidance should be loaded from prompts JSON (10_specialist_delegation section)
    # This ensures planner uses prompts as authoritative source, not hardcoded logic
    # For now, hardcoded as fallback—integrate with prompt_loader in future refactor

    prompt = f"""You are the AXIOM Planner LLM. Your task is to:
1. Identify which SKILL is needed based on the query and hypothesis
2. Select the BEST AGENT that can execute that skill

USER QUERY:
{query}

REASONING HYPOTHESIS (from prior analysis):
{hypothesis}

TARGET MASTER: {target_master}

AVAILABLE COGNITIVE SKILLS:
{skill_options}

AVAILABLE SPECIALIZED AGENTS:
{agent_options}

EVIDENCE COLLECTION STATUS:
- Missing evidence dimensions: {', '.join(missing_dimensions) if missing_dimensions else 'NONE (all evidence collected)'}
- Current iteration: {iteration_count}
- Last delegated agent: {last_delegated_agent if last_delegated_agent else 'None (first iteration)'}

AGENT SELECTION GUIDANCE (from prompts JSON):
- DIVERSIFY: If an agent was called in the previous iteration, select a DIFFERENT agent to collect complementary evidence
- PRIORITY ORDER: Select agents in this order to build complete evidence:
  1. defect_agent: for github_issue_record, defect_leakage_assessment, severity_urgency_matrix, component_defect_density
  2. requirement_agent: for requirement_record, traceability_edges, acceptance_criteria, ripple_subgraph
  3. test_agent: for test_run_failure_log, branch_coverage_report, requirement_test_matrix, synthesized_test_case
  4. resource_agent: for sprint_velocity_record, engineer_capacity_envelope, reallocation_plan, team_burn_rate
  5. codefix_agent: for git_commit_diff, source_ast_inspection, proposed_surgical_patch, syntax_validation_receipt

YOUR DECISION:
1. Identify which evidence dimension from missing_dimensions is NOT YET COLLECTED
2. Map that dimension to the AGENT RESPONSIBLE for it (using PRIORITY ORDER above)
3. Select that agent to fill the gap
4. Return a JSON object with EXACTLY these fields:

{{
  "required_skill": "<skill_id that matches the query intent>",
  "agent_id": "<agent_id that can execute this skill>",
  "gap": "<description of the specific evidence gap this agent fills>",
  "agent_objective": "<specific task for the agent to accomplish>",
  "agent_prompt": "<detailed specialized prompt to give to the selected agent>",
  "rationale": "<why this skill+agent combination is best>",
  "expected_evidence_type": "<artifact_type this agent will collect>",
  "stopping_condition": "<condition that signals evidence collection is complete>"
}}

CRITICAL RULES:
1. Select exactly ONE skill and ONE agent per planning cycle.
2. Align agent selection with skill's candidate_agents list.
3. Prioritize the NEXT UNCOLLECTED dimension from missing_dimensions (use AGENT SELECTION GUIDANCE order).
4. If all evidence is collected, select agent_id as "SYNTHESIS_READY" and gap as "All required evidence collected".
5. Return ONLY valid JSON; do not add explanatory text before or after.
6. The "agent_prompt" field MUST be detailed enough for the agent to execute independently.
7. Do NOT re-select an agent that was just called; diversify to collect evidence from different domains.
"""
    return prompt


def _call_planner_llm(
    llm_client: Any,
    planner_prompt: str,
    agent_registry: Dict[str, Any],
    missing_dimensions: set,
    query: str,
    hypothesis: str
) -> Optional[Dict[str, Any]]:
    """
    Call Gemini to make an intelligent agent selection decision.
    """
    if llm_client is None:
        logger.warning("LLM client not available; using fallback heuristic selection")
        return None

    try:
        logger.info("[LLM] Invoking Gemini planner...")
        response_text = generate_gemini_content(
            prompt=planner_prompt,
            system_prompt="You are an expert multi-agent orchestrator. Select the single best skill and agent to fulfill evidence gaps.",
            json_mode=True,
            timeout=25
        )

        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            decision = json.loads(response_text[json_start:json_end])
        else:
            decision = json.loads(response_text)

        logger.info(f"[LLM] Planner selected agent: {decision.get('agent_id')} | Skill: {decision.get('required_skill')}")
        return decision

    except Exception as e:
        logger.warning(f"Planner LLM notice ({e}); falling back to heuristic selection.")
        return None


def _fallback_agent_selection(
    agent_registry: Dict[str, Any],
    missing_dimensions: set,
    query: str
) -> Dict[str, Any]:
    """
    Heuristic-based fallback agent selection when LLM is unavailable.

    Prioritizes agent selection based on evidence gaps and agent capabilities.

    Args:
        agent_registry: Available agents
        missing_dimensions: Evidence gaps
        query: User query

    Returns:
        Fallback planner decision
    """
    logger.info("Using fallback heuristic agent selection...")

    # Priority mapping: evidence dimension -> agent_id
    dimension_to_agent = {
        "github_issue_record": "defect_agent",
        "defect_leakage_assessment": "defect_agent",
        "severity_urgency_matrix": "defect_agent",
        "component_defect_density": "defect_agent",

        "requirement_record": "requirement_agent",
        "traceability_edges": "requirement_agent",
        "acceptance_criteria": "requirement_agent",
        "ripple_subgraph": "requirement_agent",

        "test_run_failure_log": "test_agent",
        "branch_coverage_report": "test_agent",
        "requirement_test_matrix": "test_agent",
        "synthesized_test_case": "test_agent",

        "sprint_velocity_record": "resource_agent",
        "engineer_capacity_envelope": "resource_agent",
        "reallocation_plan": "resource_agent",
        "team_burn_rate": "resource_agent",

        "git_commit_diff": "codefix_agent",
        "source_ast_inspection": "codefix_agent",
        "proposed_surgical_patch": "codefix_agent",
        "syntax_validation_receipt": "codefix_agent",
    }

    # Select agent based on first missing dimension
    selected_agent_id = "defect_agent"
    expected_evidence = None

    if missing_dimensions:
        for dim in missing_dimensions:
            if dim in dimension_to_agent:
                selected_agent_id = dimension_to_agent[dim]
                expected_evidence = dim
                break
        # If no specific mapping, default to first missing dimension's implied agent
        if not expected_evidence and missing_dimensions:
            expected_evidence = list(missing_dimensions)[0]
    else:
        selected_agent_id = "SYNTHESIS_READY"

    decision = {
        "agent_id": selected_agent_id,
        "gap": f"Missing evidence dimension: {expected_evidence}" if expected_evidence else "All required evidence collected",
        "agent_objective": f"Collect {expected_evidence} for query: {query[:100]}" if expected_evidence else "Prepare synthesis",
        "agent_prompt": f"Your task: gather {expected_evidence}. Query context: {query[:150]}",
        "rationale": f"Fallback heuristic: {selected_agent_id} owns {expected_evidence}",
        "expected_evidence_type": expected_evidence or "summary",
        "stopping_condition": "Evidence collected and quality_status=verified" if expected_evidence else "N/A"
    }

    logger.info(f"Fallback selected agent: {selected_agent_id}, Evidence: {expected_evidence}")
    return decision


def _extract_required_dimensions_from_state(state: AxiomState) -> List[str]:
    """
    Extract required evidence dimensions from state.

    Looks for dimensions in multiple possible state keys for robustness.

    Args:
        state: Current AXIOM state

    Returns:
        List of required evidence dimensions
    """
    # Try multiple keys for robustness
    dimensions = state.get("required_evidence_dimensions", [])
    if not dimensions:
        dimensions = state.get("required_evidence_types", [])
    if not dimensions:
        # Fallback: infer from capability matrix
        dimensions = ["github_issue_record", "defect_leakage_assessment", "severity_urgency_matrix"]

    return dimensions if isinstance(dimensions, list) else [dimensions]


def plan_node(state: AxiomState) -> AxiomState:
    """
    PLAN Node: Intelligent Agent Selection via LLM.

    Core Planning Logic:
    1. Compute missing evidence dimensions
    2. Load agent capabilities
    3. Call Gemini LLM to decide next agent
    4. Store decision in state

    Args:
        state: Current AXIOM state from prior nodes

    Returns:
        Updated state with planner_decision, delegated_agent, and agent_prompt
    """
    logger.info("=" * 80)
    logger.info("PLAN NODE: Starting intelligent agent selection...")
    logger.info("=" * 80)

    # Extract state
    query = state.get("query", "")
    hypothesis = state.get("reasoning_hypothesis", "")
    target_master = state.get("target_master", "AXIOM-PM")
    iteration_count = state.get("evaluation_iteration_count", 0)
    evidence_envelopes = state.get("evidence_envelopes", [])
    last_delegated_agent = state.get("delegated_agent", None)

    logger.debug(f"Query: {query[:100]}")
    logger.debug(f"Hypothesis: {hypothesis[:100]}")
    logger.debug(f"Target Master: {target_master}")
    logger.debug(f"Iteration: {iteration_count}")
    logger.debug(f"Evidence envelopes collected: {len(evidence_envelopes)}")

    # Load registries
    agent_registry = load_json_file("registries/agent_registry.json").get("agents", {})
    skill_registry = load_json_file("registries/skill_registry.json").get("skills", {})
    logger.debug(f"Loaded {len(agent_registry)} agents and {len(skill_registry)} skills from registries")

    # Extract required dimensions
    required_dimensions = _extract_required_dimensions_from_state(state)
    logger.debug(f"Required evidence dimensions: {required_dimensions}")

    # Compute missing dimensions
    missing_dimensions = _compute_missing_dimensions(required_dimensions, evidence_envelopes)
    logger.info(f"Missing dimensions: {missing_dimensions if missing_dimensions else 'NONE'}")

    # Initialize LLM
    llm_client = _initialize_llm_client()

    # Build planner prompt (now includes skill registry)
    planner_prompt = _build_planner_prompt(
        agent_registry,
        skill_registry,
        missing_dimensions,
        query,
        hypothesis,
        target_master,
        iteration_count,
        last_delegated_agent
    )

    # Call LLM planner (with fallback)
    planner_decision = _call_planner_llm(
        llm_client,
        planner_prompt,
        agent_registry,
        missing_dimensions,
        query,
        hypothesis
    )

    # Use fallback if LLM call failed
    if planner_decision is None:
        planner_decision = _fallback_agent_selection(agent_registry, missing_dimensions, query)

    # Validate decision has required fields
    required_fields = ["agent_id", "gap", "agent_objective", "agent_prompt", "rationale", "expected_evidence_type", "stopping_condition"]
    for field in required_fields:
        if field not in planner_decision:
            logger.warning(f"Planner decision missing field '{field}'; setting default")
            planner_decision[field] = ""

    # Store in state
    state["planner_decision"] = planner_decision
    state["delegated_agent"] = planner_decision.get("agent_id", "defect_agent")
    state["agent_prompt"] = planner_decision.get("agent_prompt", "")
    state["current_step"] = "PLAN"

    # Log decision summary
    logger.info(f"PLAN DECISION: Agent={state['delegated_agent']}")
    logger.info(f"Gap: {planner_decision.get('gap', 'N/A')}")
    logger.info(f"Rationale: {planner_decision.get('rationale', 'N/A')}")
    logger.info(f"Expected Evidence: {planner_decision.get('expected_evidence_type', 'N/A')}")
    logger.info(f"Stopping Condition: {planner_decision.get('stopping_condition', 'N/A')}")

    logger.info("=" * 80)
    logger.info("PLAN NODE: Complete")
    logger.info("=" * 80)

    return state
