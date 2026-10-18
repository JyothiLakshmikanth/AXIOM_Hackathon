"""
AXIOM Authentication & User Management Tools.
Handles user registration, login, session creation, and audit logging via Firestore.
"""

import os
import json
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("axiom.tools.auth")


def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verify password against stored hash."""
    return stored_hash == _hash_password(provided_password)


def _generate_user_id() -> str:
    """Generate unique user ID."""
    return f"user_{secrets.token_hex(8)}"


def _generate_session_id() -> str:
    """Generate unique session ID."""
    return f"sess_{secrets.token_hex(12)}"


# Local fallback user store (for demo/testing)
_LOCAL_USER_STORE: Dict[str, Dict[str, Any]] = {
    "users": {
        "demo_user": {
            "user_id": "demo_user",
            "email": "demo@axiom.ai",
            "full_name": "Demo User",
            "password_hash": _hash_password("demo123"),
            "role": "user",
            "created_at": "2026-10-01T00:00:00Z",
            "last_login": None,
            "preferences": {
                "response_style": "visual_first",
                "notify_on_blocker": True
            }
        }
    },
    "sessions": {},
    "audit_log": {}
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


# ──────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────

def firestore_create_user(
    email: str,
    full_name: str,
    password: str,
    role: str = "user"
) -> Optional[str]:
    """
    Create a new user account in Firestore.

    Args:
        email: User email address (must be unique)
        full_name: User's full name
        password: Plaintext password (will be hashed)
        role: User role (user, pm, engineer, admin)

    Returns:
        user_id if successful, None otherwise
    """
    client = get_firestore_client()
    user_id = _generate_user_id()

    user_doc = {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "password_hash": _hash_password(password),
        "role": role,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_login": None,
        "preferences": {
            "response_style": "visual_first",
            "notify_on_blocker": True,
            "preferred_visual_model": "imagen-2"
        }
    }

    if client:
        try:
            client.collection("users").document(user_id).set(user_doc)
            logger.info(f"User created in Firestore: {user_id} ({email})")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user in Firestore: {e}")

    # Fallback to local store
    _LOCAL_USER_STORE["users"][user_id] = user_doc
    logger.info(f"User created in local store: {user_id} ({email})")
    return user_id


def firestore_authenticate_user(email: str, password: str) -> Optional[str]:
    """
    Authenticate user by email and password.
    Updates last_login timestamp.

    Args:
        email: User email
        password: Plaintext password

    Returns:
        user_id if credentials valid, None otherwise
    """
    client = get_firestore_client()

    if client:
        try:
            docs = client.collection("users").where("email", "==", email).stream()
            for doc in docs:
                user = doc.to_dict()
                if _verify_password(user.get("password_hash", ""), password):
                    user_id = user["user_id"]
                    # Update last_login
                    client.collection("users").document(user_id).update({
                        "last_login": datetime.utcnow().isoformat() + "Z"
                    })
                    logger.info(f"User authenticated: {user_id} ({email})")
                    return user_id
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")

    # Fallback to local store
    for user_id, user in _LOCAL_USER_STORE["users"].items():
        if user.get("email") == email:
            if _verify_password(user.get("password_hash", ""), password):
                user["last_login"] = datetime.utcnow().isoformat() + "Z"
                logger.info(f"User authenticated (local): {user_id} ({email})")
                return user_id

    logger.warning(f"Authentication failed for email: {email}")
    return None


def firestore_get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user_id."""
    client = get_firestore_client()

    if client:
        try:
            doc = client.collection("users").document(user_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching user: {e}")

    # Fallback to local store
    return _LOCAL_USER_STORE["users"].get(user_id)


# ──────────────────────────────────────────────────────────────────────────────
# SESSION MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────

def firestore_create_session(
    user_id: str,
    ip_address: str = "0.0.0.0",
    user_agent: str = "unknown"
) -> str:
    """
    Create a new session for authenticated user.

    Args:
        user_id: User ID
        ip_address: Client IP address
        user_agent: Browser user agent

    Returns:
        session_id
    """
    client = get_firestore_client()
    session_id = _generate_session_id()

    session_doc = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_activity": datetime.utcnow().isoformat() + "Z",
        "ip_address": ip_address,
        "user_agent": user_agent,
        "turn_count": 0
    }

    if client:
        try:
            client.collection("sessions").document(session_id).set(session_doc)
            logger.info(f"Session created in Firestore: {session_id} (user={user_id})")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session in Firestore: {e}")

    # Fallback to local store
    _LOCAL_USER_STORE["sessions"][session_id] = session_doc
    logger.info(f"Session created in local store: {session_id} (user={user_id})")
    return session_id


def firestore_get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session info by session_id."""
    client = get_firestore_client()

    if client:
        try:
            doc = client.collection("sessions").document(session_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Error fetching session: {e}")

    # Fallback to local store
    return _LOCAL_USER_STORE["sessions"].get(session_id)


def firestore_update_session_activity(session_id: str) -> bool:
    """Update last_activity timestamp for session."""
    client = get_firestore_client()

    if client:
        try:
            client.collection("sessions").document(session_id).update({
                "last_activity": datetime.utcnow().isoformat() + "Z"
            })
            return True
        except Exception as e:
            logger.warning(f"Error updating session activity: {e}")

    # Fallback to local store
    if session_id in _LOCAL_USER_STORE["sessions"]:
        _LOCAL_USER_STORE["sessions"][session_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
        return True

    return False


# ──────────────────────────────────────────────────────────────────────────────
# AUDIT LOGGING
# ──────────────────────────────────────────────────────────────────────────────

def firestore_log_audit_entry(
    user_id: str,
    session_id: str,
    action: str,
    metadata: Dict[str, Any] = None
) -> bool:
    """
    Log action for audit trail.

    Args:
        user_id: User who performed action
        session_id: Associated session
        action: Action type (login, query_submitted, logout, etc.)
        metadata: Additional metadata

    Returns:
        True if logged successfully
    """
    client = get_firestore_client()
    timestamp = datetime.utcnow().isoformat() + "Z"

    audit_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "session_id": session_id,
        "action": action,
        "metadata": metadata or {}
    }

    if client:
        try:
            # Create document with auto ID
            client.collection("audit_log").add(audit_entry)
            logger.info(f"Audit logged: user={user_id}, action={action}")
            return True
        except Exception as e:
            logger.error(f"Error logging audit entry: {e}")

    # Fallback to local store
    audit_key = f"{user_id}_{timestamp}"
    _LOCAL_USER_STORE["audit_log"][audit_key] = audit_entry
    logger.info(f"Audit logged (local): user={user_id}, action={action}")
    return True


def firestore_get_user_audit_log(user_id: str, limit: int = 50) -> list:
    """Get recent audit entries for a user."""
    client = get_firestore_client()

    if client:
        try:
            docs = (
                client.collection("audit_log")
                .where("user_id", "==", user_id)
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"Error fetching audit log: {e}")

    # Fallback to local store
    return [
        v for v in _LOCAL_USER_STORE["audit_log"].values()
        if v.get("user_id") == user_id
    ][-limit:]
