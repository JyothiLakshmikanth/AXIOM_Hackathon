# Evidence Scoping Fix — User/Session-Based Storage

## ❌ Current Problem in AXIOM

### Global Evidence Cache (Wrong!)

```python
# agents/tools/firestore_tools.py:103

def firestore_cache_evidence(entity_id: str, evidence_envelope: Dict[str, Any]) -> bool:
    """Saves a verified EvidenceEnvelope to Firestore."""
    client = get_firestore_client()
    if client:
        try:
            # ❌ PROBLEM: Global collection, no user/session isolation!
            client.collection("evidence_cache").document(entity_id).set(evidence_envelope)
            return True
```

**Issues:**
- ❌ All users share same evidence cache
- ❌ No user isolation
- ❌ No session isolation
- ❌ Privacy/security risk
- ❌ Evidence from user A visible to user B!

### Example Scenario

```
User A (user_123) queries: "What is GH-ISSUE-107?"
  └─ Evidence cached at: /evidence_cache/GH-ISSUE-107

User B (user_456) queries: "What is GH-ISSUE-107?"
  └─ Gets same cached evidence (from User A!)
     ❌ Cross-user data leakage!
```

---

## ✅ How agent_pjm.py Does It (Correct)

### Session-Based Evidence Tracking

```python
# agents/agent_pjm/agent_pjm.py:1874

class PJMState(TypedDict):
    # Core session fields
    session_id: str                          # ← Session isolation key
    user_id: str                             # ← User isolation key
    
    # Evidence tracking
    evidence_context: EvidenceContext        # ← Per-session
    _evidence_timestamps: Dict[str, str]     # ← Per-session timestamps
    _evidence_dependencies: Dict[str, List[str]]  # ← Per-session deps
    _active_session_id: str                  # ← Session isolation
```

### Evidence Stored Per Session

```python
# agents/agent_pjm/agent_pjm.py:2236

def _merge_evidence_context(
    evidence_context: EvidenceContext,      # From state (session-scoped)
    new_evidence: Dict[str, Any],
) -> EvidenceContext:
    """Merge new evidence into session's evidence context."""
    merged: EvidenceContext = dict(evidence_context)  # Shallow copy (session-scoped)
    # ... merge logic
    return merged
```

**Key Pattern:**
- Evidence stored **in state** (session-scoped)
- Evidence persisted to **Firestore by session_id**
- No global cross-session sharing

---

## 🔧 How to Fix AXIOM

### Step 1: Update Firestore Tools

**Change from:**
```python
def firestore_cache_evidence(entity_id: str, evidence_envelope: Dict[str, Any]) -> bool:
    client.collection("evidence_cache").document(entity_id).set(evidence_envelope)
    #      ↑ Global collection
```

**Change to:**
```python
def firestore_cache_evidence(
    entity_id: str, 
    evidence_envelope: Dict[str, Any],
    user_id: str,           # ← ADD
    session_id: str         # ← ADD
) -> bool:
    """Saves evidence to Firestore scoped by user and session."""
    client = get_firestore_client()
    if client:
        try:
            # ✅ Path: /users/{user_id}/sessions/{session_id}/evidence_cache/{artifact_id}
            doc_path = f"users/{user_id}/sessions/{session_id}/evidence_cache/{entity_id}"
            client.document(doc_path).set(evidence_envelope)
            return True
        except Exception as e:
            logger.warning(f"Error caching evidence: {e}")
    
    # Fallback to local store (session-scoped)
    if user_id not in _LOCAL_FIRESTORE_STORE["evidence_cache"]:
        _LOCAL_FIRESTORE_STORE["evidence_cache"][user_id] = {}
    if session_id not in _LOCAL_FIRESTORE_STORE["evidence_cache"][user_id]:
        _LOCAL_FIRESTORE_STORE["evidence_cache"][user_id][session_id] = {}
    
    _LOCAL_FIRESTORE_STORE["evidence_cache"][user_id][session_id][entity_id] = evidence_envelope
    return True
```

### Step 2: Update Evidence Retrieval

**Change from:**
```python
def firestore_get_cached_evidence(entity_id: str) -> Optional[Dict[str, Any]]:
    client.collection("evidence_cache").document(entity_id).get()
    #      ↑ Global collection, no scoping!
```

**Change to:**
```python
def firestore_get_cached_evidence(
    entity_id: str,
    user_id: str,           # ← ADD
    session_id: str         # ← ADD
) -> Optional[Dict[str, Any]]:
    """Retrieves evidence from Firestore scoped by user and session."""
    client = get_firestore_client()
    if client:
        try:
            # ✅ Path: /users/{user_id}/sessions/{session_id}/evidence_cache/{artifact_id}
            doc_path = f"users/{user_id}/sessions/{session_id}/evidence_cache/{entity_id}"
            doc = client.document(doc_path).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching evidence: {e}")
    
    # Fallback to local store (session-scoped)
    return (
        _LOCAL_FIRESTORE_STORE["evidence_cache"]
        .get(user_id, {})
        .get(session_id, {})
        .get(entity_id)
    )
```

### Step 3: Update OBSERVE Node

**Change from:**
```python
# orchestrator/master_nodes.py:190
def observe_evidence_node(state: AxiomState) -> AxiomState:
    for env in new_evidences:
        state["evidence_envelopes"].append(env)
        if "artifact_id" in env:
            firestore_cache_evidence(env["artifact_id"], env)
            #                        ↑ Missing user_id, session_id!
```

**Change to:**
```python
def observe_evidence_node(state: AxiomState) -> AxiomState:
    master_id = state.get("target_master", "AXIOM-PM")
    user_id = state.get("user_id", "default-user")       # ← Add
    session_id = state.get("session_id", "default-session") # ← Add
    new_evidences = state.pop("observed_new_evidences", [])
    
    if "evidence_envelopes" not in state or not state["evidence_envelopes"]:
        state["evidence_envelopes"] = []
    
    for env in new_evidences:
        state["evidence_envelopes"].append(env)
        if "artifact_id" in env:
            firestore_cache_evidence(
                env["artifact_id"], 
                env,
                user_id,          # ← Pass
                session_id        # ← Pass
            )
    
    logger.info(f"{master_id} OBSERVE: Total evidences={len(state['evidence_envelopes'])}")
    return state
```

### Step 4: Update Defect Agent (if using cached evidence)

**Change from:**
```python
# agents/defect_agent.py:76
cached = firestore_get_cached_evidence(issue_id) if issue_id else None
#        ↑ No user/session scoping!
```

**Change to:**
```python
def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    issue_id = task_input.get("issue_id")
    user_id = task_input.get("user_id", "default-user")     # ← Add
    session_id = task_input.get("session_id", "default-session") # ← Add
    
    # Check cache (now scoped to user+session)
    cached = firestore_get_cached_evidence(issue_id, user_id, session_id) if issue_id else None
    if cached:
        return cached  # Skip BigQuery if found in session cache
    
    # ... rest of agent logic
```

---

## 📊 Firestore Schema (Fixed)

### Before (Wrong - Global)
```
/evidence_cache/
  ├─ GH-ISSUE-107     ← No user/session isolation!
  ├─ REQ-004
  └─ ripple_123
```

### After (Right - User/Session Scoped)
```
/users/{user_id}/sessions/{session_id}/
  └─ evidence_cache/                    ✅ Per user + session
     ├─ GH-ISSUE-107
     ├─ REQ-004
     └─ ripple_123

Example paths:
  /users/user_123/sessions/sess_456/evidence_cache/GH-ISSUE-107
  /users/user_789/sessions/sess_012/evidence_cache/GH-ISSUE-107  ← Different!
```

---

## 🔒 Security & Privacy Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **User Isolation** | ❌ None | ✅ Strict |
| **Session Isolation** | ❌ None | ✅ Strict |
| **Cross-User Leakage** | ❌ Yes | ✅ No |
| **Session Reuse** | ❌ Yes (wrong) | ✅ No |
| **Audit Trail** | ❌ Per artifact | ✅ Per user/session |
| **Data Privacy** | ❌ Shared | ✅ Isolated |

---

## 📋 Complete Fix Checklist

```
☐ Update firestore_cache_evidence() signature
  └─ Add user_id, session_id parameters
  └─ Change path to /users/{user_id}/sessions/{session_id}/evidence_cache/{entity_id}

☐ Update firestore_get_cached_evidence() signature
  └─ Add user_id, session_id parameters
  └─ Change lookup path to use user+session scope

☐ Update observe_evidence_node()
  └─ Extract user_id, session_id from state
  └─ Pass to firestore_cache_evidence()

☐ Update defect_agent.execute_react_loop()
  └─ Extract user_id, session_id from task_input
  └─ Pass to firestore_get_cached_evidence()

☐ Update require_agent.execute_react_loop()
  └─ Same as defect_agent

☐ Update test_agent.execute_react_loop()
  └─ Same as defect_agent

☐ Update local fallback store structure
  └─ Change from: evidence_cache[artifact_id]
  └─ Change to: evidence_cache[user_id][session_id][artifact_id]

☐ Test with multiple users
  └─ User A queries, evidence cached
  └─ User B queries same, should NOT see User A's cache

☐ Update documentation
```

---

## 🧪 Test Case

```python
def test_evidence_isolation():
    """Verify evidence isolation between users/sessions."""
    
    # User A, Session 1
    firestore_cache_evidence(
        "GH-ISSUE-107",
        {"summary": "User A's issue"},
        user_id="user_123",
        session_id="sess_456"
    )
    
    # User B, Session 2 (different user, different session)
    evidence_b = firestore_get_cached_evidence(
        "GH-ISSUE-107",
        user_id="user_789",      # ← Different user!
        session_id="sess_012"    # ← Different session!
    )
    
    assert evidence_b is None, "User B should NOT see User A's cached evidence!"
    
    # User A, Session 1 (same user, same session - should find)
    evidence_a = firestore_get_cached_evidence(
        "GH-ISSUE-107",
        user_id="user_123",
        session_id="sess_456"
    )
    
    assert evidence_a is not None, "User A should find own cached evidence"
    assert evidence_a["summary"] == "User A's issue"
```

---

## Why This Matters

✅ **Matches agent_pjm.py pattern** — Evidence scoped to session
✅ **Prevents data leakage** — Users can't see each other's evidence
✅ **Audit trail** — Track evidence per user + session
✅ **Session isolation** — Same user, different sessions don't mix
✅ **GDPR/Privacy** — Better data isolation

---

## Summary

**Current (AXIOM):** ❌ Global evidence cache
```
/evidence_cache/GH-ISSUE-107  ← All users share!
```

**Fixed (Like agent_pjm.py):** ✅ User + Session scoped
```
/users/{user_id}/sessions/{session_id}/evidence_cache/GH-ISSUE-107
```

This ensures **no cross-user data leakage** and maintains **proper session isolation**! 🔒
