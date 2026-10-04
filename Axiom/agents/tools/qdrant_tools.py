"""
Qdrant Vector Database Tools for AXIOM.
Handles semantic embeddings retrieval for:
- Project Manifest
- Resource Details
- Team Competencies & Rosters
- PI Planning Documents
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("axiom.tools.qdrant")

# Synthetic Qdrant Document Store
_SYNTHETIC_DOCS = [
    {
        "id": "DOC-MANIFEST-01",
        "collection": "project_manifest",
        "title": "AXIOM Digital Vehicle Key - Passive Access Architecture Manifest",
        "content": "Defines system boundary for Passive Keyless Entry (PKE). Key fob communicates over BLE and UWB. Critical path delivery requires stable distance detection. Single threshold switching without hysteresis causes relay cycling and lock chatter.",
        "tags": ["architecture", "manifest", "pke", "ble", "milestone_alpha"]
    },
    {
        "id": "DOC-TEAM-DEV-ALPHA",
        "collection": "team_details",
        "title": "Engineer Profile: Dev Alpha (Senior Firmware & Embedded Systems)",
        "content": "Specialties: Python, C++, BLE stack, hardware-in-the-loop testing, state machine design. Current allocation: 95% (OVERALLOCATED in Sprint 4). Primary owner of proximity_controller.py.",
        "tags": ["engineer", "firmware", "dev_alpha", "python"]
    },
    {
        "id": "DOC-TEAM-DEV-BETA",
        "collection": "team_details",
        "title": "Engineer Profile: Dev Beta (Quality & Systems Engineer)",
        "content": "Specialties: Pytest, test automation, edge case analysis, hysteresis validation, CI/CD pipelines. Current allocation: 60% (AVAILABLE CAPACITY).",
        "tags": ["engineer", "qa", "dev_beta", "pytest"]
    },
    {
        "id": "DOC-PI-PLAN-Q4",
        "collection": "pi_planning",
        "title": "Program Increment Plan - Quarter 4 (Milestones Alpha & Beta)",
        "content": "PI objective 1: Deliver certified Passive Access Alpha by Oct 15. PI objective 2: Zero S1 defects escaping to field. Risk: Sensor noise near 2.0m requires digital filtering and hysteresis band.",
        "tags": ["pi_planning", "milestone_alpha", "roadmap"]
    }
]


def get_qdrant_client():
    """Returns live QdrantClient if configured."""
    try:
        from qdrant_client import QdrantClient
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        if url:
            return QdrantClient(url=url, api_key=api_key)
    except Exception as e:
        logger.debug(f"Live Qdrant client not initialized ({e}); using synthetic vector store fallback.")
    return None


def qdrant_search_docs(collection: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Performs dense vector / keyword search across documentation embeddings.
    """
    client = get_qdrant_client()
    if client:
        try:
            # Live search using Vertex AI embeddings or fastembed
            pass
        except Exception as e:
            logger.warning(f"Live Qdrant search error: {e}")

    # Synthetic keyword / semantic relevance score
    results = []
    query_terms = set(query.lower().split())
    for doc in _SYNTHETIC_DOCS:
        if collection and doc["collection"] != collection and collection != "all":
            continue
        text = (doc["title"] + " " + doc["content"] + " " + " ".join(doc["tags"])).lower()
        score = sum(1.5 for term in query_terms if term in text)
        if score > 0 or len(query_terms) == 0:
            results.append({
                "doc_id": doc["id"],
                "collection": doc["collection"],
                "title": doc["title"],
                "snippet": doc["content"],
                "similarity_score": min(0.98, 0.65 + (score * 0.08)),
                "tags": doc["tags"]
            })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]


def qdrant_search_team_skills_and_manifest(query: str) -> List[Dict[str, Any]]:
    """Convenience search across team details and project manifest."""
    return qdrant_search_docs(collection="all", query=query, limit=4)
