"""
Firestore Runtime Memory Tools for AXIOM.
Handles user preferences, chat/turn history, runtime evidence caching, and session state.
Supports both live Google Cloud Firestore and robust local synthetic storage.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("axiom.tools.firestore")

# Local runtime in-memory cache to guarantee zero-dependency execution
_LOCAL_FIRESTORE_STORE: Dict[str, Dict[str, Any]] = {
    "sessions": {},
    "turns": {},
    "evidence_cache": {
        "GH-ISSUE-107": {
            "artifact_id": "GH-ISSUE-107",
            "artifact_type": "github_issue",
            "source_system": "github_tracker",
            "source_uri": "https://github.com/axiom-org/axiom-core/issues/107",
            "version": "1.0",
            "updated_at": "2026-10-04T12:00:00Z",
            "authoritative": True,
            "synthetic": True,
            "quality_status": "verified",
            "payload": {
                "title": "Proximity boundary oscillation causes rapid lock/unlock chatter at 2.0m",
                "severity": "S1_CRITICAL",
                "urgency": "U1_IMMEDIATE",
                "linked_requirement": "REQ-004",
                "state": "OPEN",
                "labels": ["defect", "customer-escalation", "passive-entry"]
            }
        },
        "REQ-004": {
            "artifact_id": "REQ-004",
            "artifact_type": "requirement",
            "source_system": "neo4j_kg",
            "source_uri": "neo4j://axiom/requirements/REQ-004",
            "version": "1.2",
            "updated_at": "2026-10-04T10:00:00Z",
            "authoritative": True,
            "synthetic": True,
            "quality_status": "verified",
            "payload": {
                "title": "Passive Keyless Entry Boundary Control",
                "acceptance_criteria": "Vehicle shall unlock when key is within 2.0m and remain unlocked without oscillation.",
                "milestone": "Milestone Alpha",
                "critical_path": True
            }
        }
    },
    "user_preferences": {
        "default_user": {
            "response_style": "visual_first",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        }
    }
}


def get_firestore_client():
    """Returns live Firestore client if credentials available, else None."""
    try:
        from google.cloud import firestore
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GCP_PROJECT"):
            return firestore.Client()
    except Exception as e:
        logger.debug(f"Live Firestore not initialized ({e}); using synthetic fallback.")
    return None


def firestore_get_cached_evidence(entity_id: str) -> Optional[Dict[str, Any]]:
    """
    Checks Firestore runtime memory for previously retrieved and verified evidences.
    Enables memory_retrieval_node to skip redundant specialized agent calls if evidence exists.
    """
    client = get_firestore_client()
    if client:
        try:
            doc = client.collection("evidence_cache").document(entity_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching from live Firestore: {e}")

    # Fallback to local store
    return _LOCAL_FIRESTORE_STORE["evidence_cache"].get(entity_id)


def firestore_cache_evidence(entity_id: str, evidence_envelope: Dict[str, Any]) -> bool:
    """Saves a verified EvidenceEnvelope to Firestore for cross-turn re-use."""
    client = get_firestore_client()
    if client:
        try:
            client.collection("evidence_cache").document(entity_id).set(evidence_envelope)
            return True
        except Exception as e:
            logger.warning(f"Error saving to live Firestore: {e}")

    _LOCAL_FIRESTORE_STORE["evidence_cache"][entity_id] = evidence_envelope
    return True


def firestore_get_session_turns(session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves recent session turns (user queries, master reasoning, responses)."""
    client = get_firestore_client()
    if client:
        try:
            query = client.collection("sessions").document(session_id).collection("turns")
            docs = query.order_by("timestamp", direction="DESCENDING").limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"Error reading session turns: {e}")

    return _LOCAL_FIRESTORE_STORE["turns"].get(session_id, [])[-limit:]


def firestore_save_session_turn(session_id: str, turn_data: Dict[str, Any]) -> bool:
    """Appends a new turn to the session history in Firestore."""
    turn_data["timestamp"] = datetime.utcnow().isoformat()
    client = get_firestore_client()
    if client:
        try:
            client.collection("sessions").document(session_id).collection("turns").add(turn_data)
            return True
        except Exception as e:
            logger.warning(f"Error appending session turn: {e}")

    if session_id not in _LOCAL_FIRESTORE_STORE["turns"]:
        _LOCAL_FIRESTORE_STORE["turns"][session_id] = []
    _LOCAL_FIRESTORE_STORE["turns"][session_id].append(turn_data)
    return True


def firestore_get_user_preferences(user_id: str = "default_user") -> Dict[str, Any]:
    """Retrieves user interface and presentation preferences (e.g. visual_first)."""
    client = get_firestore_client()
    if client:
        try:
            doc = client.collection("user_preferences").document(user_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching user preferences: {e}")

    return _LOCAL_FIRESTORE_STORE["user_preferences"].get(user_id, {
        "response_style": "visual_first",
        "preferred_visual_model": "imagen-2"
    })
