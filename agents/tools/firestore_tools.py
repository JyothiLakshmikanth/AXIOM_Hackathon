"""
Firestore Runtime Memory & Feedback Learning Tools for AXIOM.
Handles:
1. User identity profiles & multi-session state persistence.
2. Cross-turn chat history memory indexed by (user_id, session_id).
3. Human feedback capture (👍 / 👎) with reason/critique notes.
4. Positive exemplar learning memory (few-shot exemplars fed into synthesis).
5. Runtime verified evidence caching and presentation preferences.
Supports live Google Cloud Firestore with persistent local JSON fallback.
"""

import os
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("axiom.tools.firestore")

# Path to persistent local store (persists across local & container restarts)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_STORE_FILE = os.path.join(_BASE_DIR, "data", "runtime_session_memory.json")

# In-memory store schema
_LOCAL_FIRESTORE_STORE: Dict[str, Any] = {
    "sessions": {},             # session_id -> {session_id, user_id, title, created_at, updated_at, turn_count}
    "user_sessions": {},        # user_id -> list of session_ids
    "turns": {},                # session_id -> list of turn dicts
    "feedback": [],             # list of feedback records
    "positive_exemplars": [
        {
            "exemplar_id": "ex-seed-107",
            "user_id": "JyothiLakshmikanth",
            "session_id": "session-seed-triage",
            "query": "What is the blast radius and defect triage for GH-ISSUE-107?",
            "rating": "positive",
            "comment": "Exceptional structural breakdown with ASIL-B compliance, affected components, and immediate mitigation.",
            "response": """### 🚨 Defect Triage & Impact Analysis: GH-ISSUE-107 / TWK-107
**Defect Title**: Boundary-Zone Unlock Intermittently Fails
- **Severity**: S1_CRITICAL | **Urgency**: U1_IMMEDIATE | **Safety Level**: ISO 26262 ASIL-B
- **Component**: `proximity_controller.py` & `ble_driver.py`
- **Owner**: Pavi2604 (RES-04) | **Target Sprint**: SPR-03

#### 🔍 Root Cause & Blast Radius
1. **Hysteresis Threshold Fluctuation**: At 1.95m - 2.05m boundary zone, RSSI signal bounce triggers oscillating unlock/lock commands.
2. **Safety Impact**: Driver lock-out at vehicle perimeter violates ISO 26262 entry requirements.
3. **Sprint Impact**: Threatens Alpha milestone sign-off unless resolved in Sprint 3.

#### 🛡️ Recommended Action Plan
- Apply 150ms debounce filter in `proximity_controller.py` boundary state machine.
- Rebalance Pavi2604's secondary QA testing items to free 40% focus for this patch.""",
            "timestamp": "2026-10-17T12:00:00Z"
        },
        {
            "exemplar_id": "ex-seed-cap",
            "user_id": "bhavya2642-collab",
            "session_id": "session-seed-capacity",
            "query": "Analyze team capacity bottlenecks and recommend rebalancing plan for SPR-03",
            "rating": "positive",
            "comment": "Clear quantitative table identifying >85% overallocation ceiling with concrete assignee reassignment.",
            "response": """### 📊 Sprint 3 Capacity & Rebalancing Analysis (SPR-03)
**Active Sprint Context**: 6 in-flight sprint items, 4 core engineering domains.

#### ⚠️ Resource Bottlenecks Identified (>85% Safe Ceiling)
- **Pavi2604 (RES-04)**: 100% Vehicle Software + 100% QA Testing = **200% Load** (Severe Bottleneck).
- **JyothiLakshmikanth (RES-05)**: 100% System Architecture + 100% Vehicle Software = **200% Load**.

#### 🎯 Workload Rebalancing Plan
| Associate | Current Role Load | Rebalanced Action | Projected Post-Load |
| :--- | :--- | :--- | :--- |
| **Pavi2604** | Vehicle (100%) + QA (100%) | Retain TWK-107 / TWK-104; offload QA test execution to automation suite | 85% (Safe) |
| **JyothiLakshmikanth** | Arch (100%) + Vehicle (100%) | Focus on TWK-108 latency architecture; delegate TWK-114 review to manjunathan-j | 80% (Safe) |
| **bhavya2642-collab** | Cloud/Mobile (75%) | Absorb companion app integration tests for TWK-108 | 85% (Optimal) |""",
            "timestamp": "2026-10-17T14:00:00Z"
        }
    ],
    "evidence_cache": {
        "GH-ISSUE-107": {
            "artifact_id": "GH-ISSUE-107",
            "artifact_type": "jira_issue_record",
            "source_system": "bigquery_axiom_data",
            "source_uri": "bigquery://axiom-cloud-run.axiom_data.sprint_planning",
            "version": "1.0",
            "updated_at": "2026-10-17T08:30:00Z",
            "authoritative": True,
            "synthetic": False,
            "quality_status": "verified",
            "payload": {
                "Id": "TWK-107",
                "Summary": "Boundary-Zone Unlock Intermittently Fails",
                "title": "Boundary-Zone Unlock Intermittently Fails",
                "Priority": "Critical",
                "Status": "Open",
                "severity": "S1_CRITICAL",
                "urgency": "U1_IMMEDIATE",
                "Sprint_ID": "SPR-03",
                "Owned_By": "RES-04",
                "Team": "Vehicle",
                "linked_requirement": "REQ-004",
                "state": "OPEN",
                "labels": ["defect", "critical", "passive-entry"]
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
        "JyothiLakshmikanth": {
            "response_style": "visual_first",
            "role": "Lead System Architect",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        },
        "bhavya2642-collab": {
            "response_style": "visual_first",
            "role": "Cloud & Mobile Platform Lead",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        },
        "manjunathan-j": {
            "response_style": "structured_code",
            "role": "Embedded Security Lead",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        },
        "Pavi2604": {
            "response_style": "defect_matrix",
            "role": "Vehicle Software & QA Lead",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        },
        "default_user": {
            "response_style": "visual_first",
            "preferred_visual_model": "imagen-2",
            "notify_on_blocker": True
        }
    }
}


def _load_local_store():
    """Loads persistent store from disk if available."""
    if os.path.exists(_STORE_FILE):
        try:
            with open(_STORE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    for k, v in saved.items():
                        if k in _LOCAL_FIRESTORE_STORE:
                            if isinstance(v, dict):
                                _LOCAL_FIRESTORE_STORE[k].update(v)
                            elif isinstance(v, list) and v:
                                # Merge lists preserving uniqueness
                                existing_ids = {
                                    item.get("exemplar_id") or item.get("feedback_id")
                                    for item in _LOCAL_FIRESTORE_STORE[k] if isinstance(item, dict)
                                }
                                for item in v:
                                    item_id = item.get("exemplar_id") or item.get("feedback_id")
                                    if not item_id or item_id not in existing_ids:
                                        _LOCAL_FIRESTORE_STORE[k].append(item)
            logger.debug(f"Loaded persistent store from {_STORE_FILE}")
        except Exception as e:
            logger.warning(f"Could not load persistent store {_STORE_FILE}: {e}")


def _save_local_store():
    """Saves store to disk safely."""
    try:
        os.makedirs(os.path.dirname(_STORE_FILE), exist_ok=True)
        with open(_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(_LOCAL_FIRESTORE_STORE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.debug(f"Could not write persistent store {_STORE_FILE}: {e}")


# Initialize persistent store on load
_load_local_store()


_firestore_client = None
_firestore_attempted = False

def get_firestore_client():
    """Returns live Firestore client if credentials available, else None."""
    global _firestore_client, _firestore_attempted
    if _firestore_attempted:
        return _firestore_client
    _firestore_attempted = True
    try:
        from google.cloud import firestore
        project_id = (
            os.getenv("GOOGLE_CLOUD_PROJECT") or
            os.getenv("GCP_PROJECT_ID") or
            os.getenv("GCP_PROJECT") or
            "axiom-510516"
        )
        client = firestore.Client(project=project_id)
        _firestore_client = client
        return _firestore_client
    except Exception as e:
        logger.debug(f"Live Firestore not initialized ({e}); using persistent fallback.")
        _firestore_client = None
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 1. EVIDENCE CACHE
# ──────────────────────────────────────────────────────────────────────────────

def firestore_get_cached_evidence(entity_id: str) -> Optional[Dict[str, Any]]:
    """Checks Firestore runtime memory for previously retrieved and verified evidences."""
    client = get_firestore_client()
    if client:
        try:
            doc = client.collection("evidence_cache").document(entity_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching from live Firestore: {e}")

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
    _save_local_store()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# 2. SESSION METADATA & USER SESSIONS
# ──────────────────────────────────────────────────────────────────────────────

def firestore_save_session_metadata(user_id: str, session_id: str, title: Optional[str] = None) -> bool:
    """Creates or updates session metadata indexed under user_id."""
    now = datetime.utcnow().isoformat()
    session_info = {
        "session_id": session_id,
        "user_id": user_id,
        "title": title or f"Session {session_id[-6:]}",
        "updated_at": now
    }

    client = get_firestore_client()
    if client:
        try:
            client.collection("users").document(user_id).collection("sessions").document(session_id).set(session_info, merge=True)
            client.collection("sessions").document(session_id).set(session_info, merge=True)
        except Exception as e:
            logger.debug(f"Live Firestore session write: {e}")

    # Local fallback
    if session_id not in _LOCAL_FIRESTORE_STORE["sessions"]:
        session_info["created_at"] = now
        session_info["turn_count"] = 0
        _LOCAL_FIRESTORE_STORE["sessions"][session_id] = session_info
    else:
        _LOCAL_FIRESTORE_STORE["sessions"][session_id]["updated_at"] = now
        if title:
            _LOCAL_FIRESTORE_STORE["sessions"][session_id]["title"] = title

    if user_id not in _LOCAL_FIRESTORE_STORE["user_sessions"]:
        _LOCAL_FIRESTORE_STORE["user_sessions"][user_id] = []
    if session_id not in _LOCAL_FIRESTORE_STORE["user_sessions"][user_id]:
        _LOCAL_FIRESTORE_STORE["user_sessions"][user_id].insert(0, session_id)

    _save_local_store()
    return True


def firestore_list_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    """Lists all active and historical sessions for a given user."""
    client = get_firestore_client()
    if client:
        try:
            query = client.collection("users").document(user_id).collection("sessions").order_by("updated_at", direction="DESCENDING")
            docs = query.limit(20).stream(timeout=3.0)
            results = [doc.to_dict() for doc in docs]
            if results:
                return results
        except Exception as e:
            logger.debug(f"Live Firestore list sessions: {e}")

    session_ids = _LOCAL_FIRESTORE_STORE["user_sessions"].get(user_id, [])
    sessions = []
    for sid in session_ids:
        s = _LOCAL_FIRESTORE_STORE["sessions"].get(sid)
        if s:
            s_copy = dict(s)
            s_copy["turn_count"] = len(_LOCAL_FIRESTORE_STORE["turns"].get(sid, []))
            sessions.append(s_copy)

    # If no sessions yet, return empty list
    return sessions


# ──────────────────────────────────────────────────────────────────────────────
# 3. CHAT HISTORY / SESSION TURNS
# ──────────────────────────────────────────────────────────────────────────────

def firestore_get_session_turns(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves full conversation turns for a session in chronological order."""
    client = get_firestore_client()
    if client:
        try:
            query = client.collection("sessions").document(session_id).collection("turns")
            docs = query.order_by("timestamp", direction="ASCENDING").limit(limit).stream()
            turns = [doc.to_dict() for doc in docs]
            if turns:
                return turns
        except Exception as e:
            logger.debug(f"Live Firestore get session turns: {e}")

    return _LOCAL_FIRESTORE_STORE["turns"].get(session_id, [])[-limit:]


def firestore_save_session_turn(session_id: str, turn_data: Dict[str, Any], user_id: str = "default_user") -> bool:
    """Appends a turn to the session history in Firestore and updates session metadata."""
    if "timestamp" not in turn_data:
        turn_data["timestamp"] = datetime.utcnow().isoformat()
    turn_data["session_id"] = session_id
    turn_data["user_id"] = user_id

    # If title not established and query present, create title
    title = None
    if turn_data.get("query"):
        q = turn_data["query"].strip()
        title = (q[:40] + "...") if len(q) > 40 else q

    firestore_save_session_metadata(user_id=user_id, session_id=session_id, title=title)

    client = get_firestore_client()
    if client:
        try:
            client.collection("sessions").document(session_id).collection("turns").add(turn_data)
        except Exception as e:
            logger.debug(f"Live Firestore save turn: {e}")

    if session_id not in _LOCAL_FIRESTORE_STORE["turns"]:
        _LOCAL_FIRESTORE_STORE["turns"][session_id] = []
    _LOCAL_FIRESTORE_STORE["turns"][session_id].append(turn_data)

    if session_id in _LOCAL_FIRESTORE_STORE["sessions"]:
        _LOCAL_FIRESTORE_STORE["sessions"][session_id]["turn_count"] = len(_LOCAL_FIRESTORE_STORE["turns"][session_id])
        _LOCAL_FIRESTORE_STORE["sessions"][session_id]["updated_at"] = turn_data["timestamp"]

    _save_local_store()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# 4. FEEDBACK MECHANISM & POSITIVE EXEMPLAR LEARNING
# ──────────────────────────────────────────────────────────────────────────────

def firestore_save_user_feedback(
    user_id: str,
    session_id: str,
    query: str,
    response: str,
    rating: str,
    comment: str = "",
    master: str = "AXIOM-PM",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records user feedback (thumbs up / thumbs down) on an assistant response.
    When rating is 'positive', automatically indexes response into positive_exemplars
    for few-shot in-context learning during future syntheses.
    """
    feedback_id = f"fb-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    feedback_record = {
        "feedback_id": feedback_id,
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "response": response,
        "rating": rating,           # "positive" (👍) or "negative" (👎)
        "comment": comment,
        "master": master,
        "timestamp": now,
        "metadata": metadata or {}
    }

    # Save to live Firestore
    client = get_firestore_client()
    if client:
        try:
            client.collection("user_feedback").document(feedback_id).set(feedback_record)
        except Exception as e:
            logger.debug(f"Live Firestore feedback write: {e}")

    # Save to local store
    _LOCAL_FIRESTORE_STORE["feedback"].append(feedback_record)

    # If positive, elevate to positive_exemplars
    if rating == "positive":
        exemplar_record = {
            "exemplar_id": f"ex-{uuid.uuid4().hex[:8]}",
            "feedback_id": feedback_id,
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "response": response,
            "comment": comment or "High-quality response approved by user",
            "master": master,
            "timestamp": now
        }
        if client:
            try:
                client.collection("positive_exemplars").document(exemplar_record["exemplar_id"]).set(exemplar_record)
            except Exception as e:
                logger.debug(f"Live Firestore exemplar write: {e}")

        # Check if already present
        _LOCAL_FIRESTORE_STORE["positive_exemplars"].insert(0, exemplar_record)
        logger.info(f"Learned new positive exemplar {exemplar_record['exemplar_id']} from user {user_id}")

    _save_local_store()
    return feedback_record


def firestore_get_positive_exemplars(limit: int = 3, query_filter: str = "") -> List[Dict[str, Any]]:
    """
    Retrieves approved positive exemplars to inject as few-shot guidance for Gemini synthesis.
    If query_filter is provided, prioritizes exemplars with matching context or keywords.
    """
    client = get_firestore_client()
    if client:
        try:
            docs = client.collection("positive_exemplars").order_by("timestamp", direction="DESCENDING").limit(limit * 2).stream()
            live_exemplars = [d.to_dict() for d in docs]
            if live_exemplars:
                return live_exemplars[:limit]
        except Exception as e:
            logger.debug(f"Live Firestore exemplar read: {e}")

    exemplars = _LOCAL_FIRESTORE_STORE.get("positive_exemplars", [])

    if not query_filter:
        return exemplars[:limit]

    # Simple keyword scoring
    keywords = set(query_filter.lower().split())
    scored = []
    for ex in exemplars:
        ex_text = (ex.get("query", "") + " " + ex.get("comment", "")).lower()
        score = sum(1 for kw in keywords if len(kw) > 3 and kw in ex_text)
        scored.append((score, ex))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [ex for _, ex in scored[:limit]]


def firestore_get_all_feedback(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all feedback records, optionally filtered by user_id."""
    client = get_firestore_client()
    if client:
        try:
            col = client.collection("user_feedback")
            if user_id:
                col = col.where("user_id", "==", user_id)
            docs = col.order_by("timestamp", direction="DESCENDING").limit(50).stream()
            results = [d.to_dict() for d in docs]
            if results:
                return results
        except Exception as e:
            logger.debug(f"Live Firestore feedback list: {e}")

    feedbacks = _LOCAL_FIRESTORE_STORE.get("feedback", [])
    if user_id:
        feedbacks = [f for f in feedbacks if f.get("user_id") == user_id]
    return list(reversed(feedbacks))


def firestore_get_feedback_stats() -> Dict[str, int]:
    """Calculates summary statistics on user feedback."""
    all_fb = _LOCAL_FIRESTORE_STORE.get("feedback", [])
    pos = sum(1 for f in all_fb if f.get("rating") == "positive")
    neg = sum(1 for f in all_fb if f.get("rating") == "negative")
    exemplars_count = len(_LOCAL_FIRESTORE_STORE.get("positive_exemplars", []))
    return {
        "total_feedback": len(all_fb),
        "positive": pos,
        "negative": neg,
        "learned_exemplars": exemplars_count,
        "satisfaction_pct": int((pos / len(all_fb) * 100)) if all_fb else 100
    }


# ──────────────────────────────────────────────────────────────────────────────
# 5. USER PREFERENCES
# ──────────────────────────────────────────────────────────────────────────────

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
