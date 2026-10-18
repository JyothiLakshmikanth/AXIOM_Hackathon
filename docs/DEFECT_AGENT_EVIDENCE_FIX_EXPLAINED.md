# Defect Agent Evidence Fix — Step-by-Step

## 📍 Location: agents/defect_agent.py:49-100

---

## ❌ BEFORE (Current - Wrong)

```python
def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    """Executes autonomous ReAct reasoning loop."""
    
    issue_id = task_input.get("issue_id")
    sprint_id = task_input.get("sprint_id")
    action = task_input.get("action", "triage_issue")
    
    evidences = []
    
    # ... find issue_id logic ...
    
    # ❌ PROBLEM: No user_id or session_id passed!
    # Line 76:
    cached = firestore_get_cached_evidence(issue_id) if issue_id else None
    #        ↑ Only artifact_id, no user/session scope!
    
    if cached:
        defect_record = cached.get("payload", {})
        evidences.append(cached)
    else:
        # Query BigQuery if not cached
        defect_record = bigquery_get_defect_by_issue_id(issue_id) if issue_id else {}
```

**What happens:**
1. User A queries issue "GH-ISSUE-107"
2. Agent calls: `firestore_get_cached_evidence("GH-ISSUE-107")`
3. Firestore looks in: `/evidence_cache/GH-ISSUE-107` ← GLOBAL!
4. Finds User B's cached evidence from yesterday
5. Returns User B's data to User A 😱

---

## ✅ AFTER (Fixed - Correct)

```python
def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    """Executes autonomous ReAct reasoning loop."""
    
    # ✅ ADD: Extract user/session from task_input
    issue_id = task_input.get("issue_id")
    sprint_id = task_input.get("sprint_id")
    action = task_input.get("action", "triage_issue")
    user_id = task_input.get("user_id", "default-user")         # ← ADD
    session_id = task_input.get("session_id", "default-session") # ← ADD
    
    evidences = []
    
    # ... find issue_id logic ...
    
    # ✅ FIXED: Pass user_id and session_id
    # Line 76:
    cached = firestore_get_cached_evidence(
        issue_id,
        user_id,           # ← ADD
        session_id         # ← ADD
    ) if issue_id else None
    #    ↑ Now looks in: /users/{user_id}/sessions/{session_id}/evidence_cache/...
    
    if cached:
        defect_record = cached.get("payload", {})
        evidences.append(cached)
    else:
        # Query BigQuery if not cached
        defect_record = bigquery_get_defect_by_issue_id(issue_id) if issue_id else {}
```

---

## 🔍 Concrete Example

### Current (WRONG) - Global Cache

```
Scenario: Two users query same issue

User A (user_123)
  └─ Queries: GH-ISSUE-107
     └─ Agent calls: firestore_get_cached_evidence("GH-ISSUE-107")
        └─ Looks in: /evidence_cache/GH-ISSUE-107
           └─ Finds evidence (doesn't matter who cached it!)
              └─ Returns to User A

User B (user_789) - LATER
  └─ Queries: GH-ISSUE-107
     └─ Agent calls: firestore_get_cached_evidence("GH-ISSUE-107")
        └─ Looks in: /evidence_cache/GH-ISSUE-107 ← SAME LOCATION!
           └─ Finds evidence from User A!
              └─ ❌ Returns User A's data to User B!  PRIVACY BREACH!
```

### Fixed (CORRECT) - Session-Scoped Cache

```
Scenario: Two users query same issue

User A (user_123), Session sess_456
  └─ Queries: GH-ISSUE-107
     └─ Agent calls: firestore_get_cached_evidence("GH-ISSUE-107", "user_123", "sess_456")
        └─ Looks in: /users/user_123/sessions/sess_456/evidence_cache/GH-ISSUE-107
           └─ Finds evidence (User A's session)
              └─ Returns to User A ✅

User B (user_789), Session sess_012 - LATER
  └─ Queries: GH-ISSUE-107
     └─ Agent calls: firestore_get_cached_evidence("GH-ISSUE-107", "user_789", "sess_012")
        └─ Looks in: /users/user_789/sessions/sess_012/evidence_cache/GH-ISSUE-107
           └─ Finds NOTHING (different user+session)
              └─ Queries BigQuery (fresh data)
                 └─ Returns fresh data to User B ✅
```

---

## 🔄 Full Flow with Task Input

### Where task_input Comes From

```python
# orchestrator/master_nodes.py:execute_agent_node()

def execute_agent_node(state: AxiomState) -> AxiomState:
    """EXECUTE_AGENT_NODE calls defect_agent."""
    
    agent = agent_map.get("defect_agent")
    
    # ✅ Pass state info to agent via task_input
    result = agent.execute_react_loop({
        "query": state.get("query", ""),
        "prompt": agent_prompt,
        
        # ← These come from authenticated user
        "user_id": state.get("user_id"),           # From login
        "session_id": state.get("session_id"),     # From login
        
        # Issue-specific
        "issue_id": "GH-ISSUE-107"
    })
```

### Agent Receives It

```python
# agents/defect_agent.py:49

def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    
    # Extract everything
    issue_id = task_input.get("issue_id")           # "GH-ISSUE-107"
    user_id = task_input.get("user_id")             # "user_123"
    session_id = task_input.get("session_id")       # "sess_456"
    
    # Use for evidence lookup
    cached = firestore_get_cached_evidence(
        issue_id,      # "GH-ISSUE-107"
        user_id,       # "user_123"
        session_id     # "sess_456"
    )
```

---

## 📋 Changes Needed in defect_agent.py

### Line 49-60 (Function Start)

```python
# BEFORE:
def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    """Executes autonomous ReAct reasoning loop."""
    issue_id = task_input.get("issue_id")
    sprint_id = task_input.get("sprint_id")
    action = task_input.get("action", "triage_issue")
    evidences = []

# AFTER:
def execute_react_loop(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
    """Executes autonomous ReAct reasoning loop."""
    issue_id = task_input.get("issue_id")
    sprint_id = task_input.get("sprint_id")
    action = task_input.get("action", "triage_issue")
    user_id = task_input.get("user_id", "default-user")         # ← ADD THIS
    session_id = task_input.get("session_id", "default-session") # ← ADD THIS
    evidences = []
```

### Line 76 (Cached Evidence Lookup)

```python
# BEFORE:
cached = firestore_get_cached_evidence(issue_id) if issue_id else None

# AFTER:
cached = firestore_get_cached_evidence(
    issue_id,
    user_id,
    session_id
) if issue_id else None
```

---

## 🧪 Testing the Fix

### Test Case 1: Same User, Same Session (Should find cache)

```python
def test_same_user_same_session():
    """User should find their own cached evidence."""
    
    # User A caches evidence
    firestore_cache_evidence(
        "GH-ISSUE-107",
        {"summary": "User A's defect info"},
        user_id="user_123",
        session_id="sess_456"
    )
    
    # User A runs agent in same session
    result = defect_agent.execute_react_loop({
        "issue_id": "GH-ISSUE-107",
        "user_id": "user_123",
        "session_id": "sess_456"
    })
    
    # Should find cached evidence
    assert len(result["evidences"]) > 0
    assert result["evidences"][0]["payload"]["summary"] == "User A's defect info"
```

### Test Case 2: Different User, Different Session (Should NOT find cache)

```python
def test_different_user_different_session():
    """Different user should NOT see other user's cached evidence."""
    
    # User A caches evidence
    firestore_cache_evidence(
        "GH-ISSUE-107",
        {"summary": "User A's defect info"},
        user_id="user_123",
        session_id="sess_456"
    )
    
    # User B runs agent in different session
    result = defect_agent.execute_react_loop({
        "issue_id": "GH-ISSUE-107",
        "user_id": "user_789",           # ← DIFFERENT USER
        "session_id": "sess_012"         # ← DIFFERENT SESSION
    })
    
    # Should NOT find User A's cached evidence
    # Should query BigQuery instead
    assert "error" not in result  # BigQuery worked
    # Evidence should be fresh from BigQuery, not User A's cache
```

### Test Case 3: Same User, Different Session (Should NOT find cache)

```python
def test_same_user_different_session():
    """Same user in different session should NOT see own prior session's cache."""
    
    # User A, Session 1: caches evidence
    firestore_cache_evidence(
        "GH-ISSUE-107",
        {"summary": "User A Session 1 defect info"},
        user_id="user_123",
        session_id="sess_456"
    )
    
    # User A, Session 2 (different): runs agent
    result = defect_agent.execute_react_loop({
        "issue_id": "GH-ISSUE-107",
        "user_id": "user_123",           # ← SAME USER
        "session_id": "sess_789"         # ← DIFFERENT SESSION
    })
    
    # Should NOT find Session 1's evidence
    # Should query BigQuery instead
    # Different sessions are isolated even for same user
```

---

## ✅ Summary

**The change:**
1. Extract `user_id` and `session_id` from `task_input`
2. Pass them to `firestore_get_cached_evidence()`
3. That's it!

**Why it matters:**
- ✅ User A's evidence stays with User A
- ✅ User B can't see User A's cache
- ✅ Different sessions isolated
- ✅ Security + Privacy

**One-liner:**
Change line 76 from:
```python
cached = firestore_get_cached_evidence(issue_id) if issue_id else None
```

To:
```python
cached = firestore_get_cached_evidence(issue_id, user_id, session_id) if issue_id else None
```

(After adding the user_id/session_id extractions at the top!)
