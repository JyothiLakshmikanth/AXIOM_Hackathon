"""
AXIOM Evidence Checking Node — Master-Level Cache Lookup.
Before calling agents, check if evidence already exists in Firestore.
Avoids redundant agent calls and improves performance.
"""

import logging
from typing import Dict, Any, Optional
from orchestrator.state import AxiomState
from agents.tools.firestore_tools import firestore_get_cached_evidence

logger = logging.getLogger("axiom.orchestrator.evidence_check")


def evidence_check_node(state: AxiomState) -> AxiomState:
    """
    Cognitive Node: EVIDENCE CHECK.

    Checks if required evidence already exists in Firestore cache
    scoped to user + session. If found, skips agent calls.

    This node runs AFTER REASON (we know what evidence is needed)
    and BEFORE PLAN (before deciding which agent to call).

    Args:
        state: Current AxiomState

    Returns:
        Updated AxiomState with cached evidence if found
    """
    master_id = state.get("target_master", "AXIOM-PM")
    user_id = state.get("user_id", "default-user")
    session_id = state.get("session_id", "default-session")
    query = state.get("query", "")

    logger.info(
        f"{master_id} EVIDENCE_CHECK: Checking cache for user={user_id}, session={session_id}"
    )

    # Initialize evidence list if needed
    if "evidence_envelopes" not in state:
        state["evidence_envelopes"] = []

    # Try to extract artifact IDs from query (heuristic)
    artifact_ids = _extract_artifact_ids_from_query(query)

    if not artifact_ids:
        logger.debug(f"{master_id} EVIDENCE_CHECK: No artifact IDs found in query")
        state["evidence_cache_hit"] = False
        return state

    # Check Firestore cache for each artifact ID
    found_evidence = []
    for artifact_id in artifact_ids:
        cached = firestore_get_cached_evidence(
            artifact_id,
            user_id=user_id,
            session_id=session_id
        )

        if cached:
            logger.info(
                f"{master_id} EVIDENCE_CHECK: Cache HIT for {artifact_id} "
                f"(quality={cached.get('quality_status')})"
            )
            found_evidence.append(cached)
        else:
            logger.debug(f"{master_id} EVIDENCE_CHECK: Cache MISS for {artifact_id}")

    # If we found verified evidence, reuse it
    if found_evidence:
        logger.info(f"{master_id} EVIDENCE_CHECK: Found {len(found_evidence)} cached evidences")
        state["evidence_envelopes"].extend(found_evidence)
        state["evidence_cache_hit"] = True
        return state

    state["evidence_cache_hit"] = False
    return state


def _extract_artifact_ids_from_query(query: str) -> list:
    """
    Extract artifact IDs from query text.

    Looks for patterns like:
    - GH-ISSUE-107
    - REQ-L2-001
    - TWK-107
    - TC-ENR-001

    Args:
        query: User query string

    Returns:
        List of artifact IDs found
    """
    import re

    # Match common artifact ID patterns
    patterns = [
        r'GH-ISSUE-\d+',      # GitHub issues: GH-ISSUE-107
        r'TWK-\d+',           # Jira issues: TWK-107
        r'REQ-[A-Z0-9-]+',    # Requirements: REQ-L2-001
        r'TC-[A-Z0-9-]+',     # Test cases: TC-ENR-001
        r'SPR-\d+',           # Sprints: SPR-03
    ]

    artifact_ids = []
    for pattern in patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        artifact_ids.extend(matches)

    return list(set(artifact_ids))  # Remove duplicates
