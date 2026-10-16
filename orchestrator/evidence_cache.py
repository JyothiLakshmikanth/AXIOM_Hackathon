"""
AXIOM Evidence Cache — Normalization, caching, and sufficiency evaluation for artifacts.
Enforces EvidenceEnvelope structure, manages Firestore persistence, and evaluates
whether collected evidence satisfies required capability dimensions.
"""

import logging
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime

logger = logging.getLogger("axiom.orchestrator.evidence_cache")


def normalize_evidence_envelope(
    raw_data: Dict[str, Any], artifact_type: str, source_system: str
) -> Dict[str, Any]:
    """
    Normalize arbitrary artifact data into mandatory EvidenceEnvelope structure.

    Enforces all required fields per AXIOM evidence standards:
    - artifact_id, artifact_type, source_system, source_uri (mandatory)
    - version, updated_at (with defaults)
    - authoritative, synthetic, quality_status (with defaults)
    - payload (the actual artifact data)

    Validates that required fields are present and non-empty.
    If optional fields missing, applies sensible defaults.

    Args:
        raw_data: Arbitrary artifact data dictionary
        artifact_type: Classification (e.g., "requirement", "defect", "test_result", "github_issue")
        source_system: Origin system (e.g., "neo4j_kg", "bigquery", "github_tracker")

    Returns:
        Normalized envelope dictionary with all required fields

    Raises:
        ValueError: If artifact_id or source_uri missing from raw_data
    """
    logger.debug(
        f"Normalizing evidence: type={artifact_type}, source={source_system}, "
        f"data_keys={list(raw_data.keys())}"
    )

    # Mandatory fields that must exist
    artifact_id = raw_data.get("artifact_id") or raw_data.get("id")
    source_uri = raw_data.get("source_uri")

    if not artifact_id:
        logger.error("Cannot normalize: artifact_id or id field required")
        raise ValueError("raw_data must contain artifact_id or id field")

    if not source_uri:
        logger.error(f"Cannot normalize: source_uri required for {artifact_id}")
        raise ValueError(f"raw_data must contain source_uri field (for {artifact_id})")

    # Construct envelope with all required fields
    envelope: Dict[str, Any] = {
        "artifact_id": str(artifact_id),
        "artifact_type": artifact_type,
        "source_system": source_system,
        "source_uri": str(source_uri),
        "version": str(raw_data.get("version", "1.0")),
        "updated_at": str(raw_data.get("updated_at", datetime.utcnow().isoformat() + "Z")),
        "authoritative": bool(raw_data.get("authoritative", True)),
        "synthetic": bool(raw_data.get("synthetic", True)),
        "quality_status": str(raw_data.get("quality_status", "verified")),
        "payload": raw_data,
    }

    logger.info(f"Normalized evidence envelope: {artifact_id} (type={artifact_type})")
    return envelope


def cache_to_firestore(
    evidence: Dict[str, Any], session_id: str, gcp_client: Any
) -> None:
    """
    Save normalized evidence envelope to Firestore cache for session persistence.

    Stores at path: sessions/{session_id}/evidence_cache/{artifact_id}
    Enables rapid retrieval of previously collected evidence without re-fetching.

    Args:
        evidence: Normalized evidence envelope (result of normalize_evidence_envelope)
        session_id: Session identifier for isolation
        gcp_client: GCPClient instance from orchestrator.gcp_client.get_gcp_client()

    Raises:
        ValueError: If evidence missing required envelope fields
        RuntimeError: If Firestore write fails
    """
    artifact_id = evidence.get("artifact_id")

    if not artifact_id:
        logger.error("Cannot cache: evidence missing artifact_id")
        raise ValueError("evidence envelope must contain artifact_id")

    if not session_id:
        logger.error("Cannot cache: session_id required")
        raise ValueError("session_id required for caching")

    logger.debug(f"Caching evidence: session={session_id}, artifact={artifact_id}")

    try:
        doc_path = f"sessions/{session_id}/evidence_cache/{artifact_id}"

        gcp_client.set_firestore(doc_path, evidence)

        logger.info(f"Evidence cached in Firestore: {doc_path}")

    except Exception as e:
        logger.error(f"Failed to cache evidence in Firestore: {e}")
        raise RuntimeError(f"Evidence caching failed: {e}") from e


def retrieve_from_cache(
    artifact_id: str, session_id: str, gcp_client: Any
) -> Optional[Dict[str, Any]]:
    """
    Retrieve normalized evidence from Firestore cache by artifact ID.

    Returns None if document not found (cache miss).
    Returns full evidence envelope including payload.

    Args:
        artifact_id: Identifier of artifact to retrieve
        session_id: Session for document path resolution
        gcp_client: GCPClient instance from orchestrator.gcp_client.get_gcp_client()

    Returns:
        Evidence envelope dictionary if found, None if cache miss

    Raises:
        RuntimeError: If Firestore read fails
    """
    if not artifact_id or not session_id:
        logger.error("Cannot retrieve: artifact_id and session_id required")
        return None

    logger.debug(f"Retrieving from cache: session={session_id}, artifact={artifact_id}")

    try:
        doc_path = f"sessions/{session_id}/evidence_cache/{artifact_id}"

        evidence = gcp_client.get_firestore(doc_path)

        if evidence:
            logger.info(f"Cache hit: {artifact_id} from {doc_path}")
            return evidence
        else:
            logger.debug(f"Cache miss: {artifact_id} not found")
            return None

    except Exception as e:
        logger.error(f"Failed to retrieve from Firestore cache: {e}")
        raise RuntimeError(f"Cache retrieval failed: {e}") from e


def evaluate_evidence_sufficiency(
    evidence_envelopes: List[Dict[str, Any]],
    required_dimensions: List[str],
    capability_matrix: Dict[str, Any]
) -> Literal["SUFFICIENT", "INSUFFICIENT", "CRITICAL_GAPS"]:
    """
    Evaluate whether collected evidence is sufficient to answer the query.

    Analyzes:
    - Number of evidence envelopes
    - Coverage of required evidence dimensions
    - Quality and authority of evidence

    Args:
        evidence_envelopes: List of collected EvidenceEnvelope dicts
        required_dimensions: Required evidence dimensions for the capability
        capability_matrix: Capability definitions

    Returns:
        "SUFFICIENT": All required dimensions covered with verified evidence
        "INSUFFICIENT": Some dimensions covered but not authoritative
        "CRITICAL_GAPS": Major dimensions missing
    """
    if not evidence_envelopes:
        logger.warning("No evidence envelopes provided for evaluation")
        return "CRITICAL_GAPS"

    if not required_dimensions:
        # No specific requirements = minimal bar
        logger.info("No specific evidence dimensions required; using baseline threshold")
        return "SUFFICIENT" if len(evidence_envelopes) >= 1 else "INSUFFICIENT"

    # Extract artifact types from collected evidence
    collected_artifacts = set()
    verified_count = 0

    for env in evidence_envelopes:
        artifact_type = env.get("artifact_type", "unknown")
        collected_artifacts.add(artifact_type)

        if env.get("quality_status") == "verified" and env.get("authoritative", False):
            verified_count += 1

    logger.info(
        f"Evidence evaluation: {len(evidence_envelopes)} envelopes, "
        f"{verified_count} verified/authoritative, "
        f"artifact types: {collected_artifacts}"
    )

    # Check dimension coverage
    # Map evidence artifact types to evidence dimensions
    dimension_coverage = _map_artifacts_to_dimensions(collected_artifacts, required_dimensions)

    covered_dims = sum(1 for covered in dimension_coverage.values() if covered)
    total_dims = len(required_dimensions)

    logger.info(f"Dimension coverage: {covered_dims}/{total_dims}")

    # Decision logic
    if covered_dims == total_dims and verified_count >= len(evidence_envelopes) * 0.5:
        # All dimensions covered with at least 50% verified evidence
        return "SUFFICIENT"
    elif covered_dims >= total_dims * 0.7 and verified_count > 0:
        # 70%+ coverage with at least some verified evidence
        return "INSUFFICIENT"
    else:
        # Major gaps
        return "CRITICAL_GAPS"


def extract_material_gaps_simple(
    required_dims: List[str], collected_envelopes: List[Dict[str, Any]]
) -> List[str]:
    """
    Extract list of missing evidence dimensions that block synthesis.

    Compares required dimensions against evidence envelope types.
    Returns only dimensions where no evidence is present.

    Material gaps are those that would materially change the decision or answer,
    vs. gaps that are nice-to-have but not decision-critical.

    Args:
        required_dims: List of required evidence dimensions
        collected_envelopes: List of evidence envelope dictionaries already collected

    Returns:
        List of dimension names with no evidence collected
    """
    if not required_dims:
        logger.debug("No required dimensions, no gaps")
        return []

    logger.debug(f"Extracting gaps: {len(required_dims)} required, {len(collected_envelopes)} collected")

    # Extract artifact types from collected envelopes
    collected_types = set()
    for envelope in collected_envelopes:
        artifact_type = envelope.get("artifact_type")
        if artifact_type:
            collected_types.add(artifact_type)

    logger.debug(f"Collected artifact types for gap analysis: {collected_types}")

    # Identify gaps by checking for each required dimension
    gaps = []

    # Simple gap detection: if dimension name matches artifact type, it's not a gap
    # More sophisticated: use capability matrix mapping
    for dimension in required_dims:
        # Check if dimension itself is in collected types (simple case)
        # Or if any artifact type matches the dimension name (loose matching)
        is_covered = dimension.lower() in [t.lower() for t in collected_types]

        if not is_covered:
            gaps.append(dimension)

    logger.info(f"Material gaps identified: {len(gaps)} dimensions without evidence")
    if gaps:
        logger.debug(f"Gap list: {gaps}")

    return gaps


def extract_material_gaps(
    required_dimensions: List[str],
    evidence_envelopes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract material gaps between required evidence and what was collected.

    Args:
        required_dimensions: Required evidence dimensions
        evidence_envelopes: Collected evidence

    Returns:
        Dict with keys:
        - "missing_dimensions": List of unmet dimensions
        - "gap_descriptions": Dict mapping dimensions to gap reasons
        - "collection_priority": Ordered list of highest-priority gaps
    """
    if not required_dimensions:
        return {
            "missing_dimensions": [],
            "gap_descriptions": {},
            "collection_priority": []
        }

    # Extract artifact types from evidence
    collected_artifacts = set()
    for env in evidence_envelopes:
        artifact_type = env.get("artifact_type", "unknown")
        collected_artifacts.add(artifact_type)

    # Map dimensions to evidence types
    dimension_evidence_map = {
        "github_issue_record": ["github_issue", "github_defect"],
        "severity_classification": ["severity_assessment", "impact_analysis"],
        "requirement_impact": ["requirement_trace", "requirement_mapping", "impact_analysis"],
        "test_coverage": ["test_results", "test_coverage_report"],
        "velocity_history": ["sprint_metrics", "velocity_data"],
        "team_capacity": ["resource_allocation", "team_capacity_report"],
        "defect_backlog": ["defect_inventory", "backlog_analysis"],
    }

    missing = []
    gap_descriptions = {}

    for dimension in required_dimensions:
        expected_types = dimension_evidence_map.get(dimension, [])
        if not expected_types or not any(art in collected_artifacts for art in expected_types):
            missing.append(dimension)
            gap_descriptions[dimension] = (
                f"Missing evidence type: expected one of {expected_types}, "
                f"collected: {list(collected_artifacts)}"
            )

    # Prioritize: highest-impact gaps first
    priority = _prioritize_gaps(missing)

    return {
        "missing_dimensions": missing,
        "gap_descriptions": gap_descriptions,
        "collection_priority": priority
    }


def _map_artifacts_to_dimensions(
    artifact_types: set,
    required_dimensions: List[str]
) -> Dict[str, bool]:
    """
    Map collected artifact types to required evidence dimensions.

    Returns dict indicating which dimensions are covered.
    """
    dimension_evidence_map = {
        "github_issue_record": {"github_issue", "github_defect", "defect_record"},
        "severity_classification": {"severity_assessment", "impact_analysis", "risk_score"},
        "requirement_impact": {"requirement_trace", "requirement_mapping", "impact_analysis"},
        "test_coverage": {"test_results", "test_coverage_report", "test_suite"},
        "velocity_history": {"sprint_metrics", "velocity_data", "historical_velocity"},
        "team_capacity": {"resource_allocation", "team_capacity_report", "capacity_plan"},
        "defect_backlog": {"defect_inventory", "backlog_analysis", "defect_list"},
    }

    coverage = {}
    for dimension in required_dimensions:
        expected = dimension_evidence_map.get(dimension, set())
        coverage[dimension] = bool(artifact_types & expected)

    return coverage


def _prioritize_gaps(missing_dimensions: List[str]) -> List[str]:
    """
    Prioritize gaps by impact and collection ease.

    High priority:
    - Authoritative records (github_issue_record, defect_record)
    - Requirement traceability (requirement_impact)

    Medium priority:
    - Severity/impact classification
    - Team metrics

    Low priority:
    - Historical data (can be inferred)
    """
    high_priority = []
    medium_priority = []
    low_priority = []

    for dim in missing_dimensions:
        if dim in ["github_issue_record", "requirement_impact"]:
            high_priority.append(dim)
        elif dim in ["severity_classification", "team_capacity"]:
            medium_priority.append(dim)
        else:
            low_priority.append(dim)

    return high_priority + medium_priority + low_priority
