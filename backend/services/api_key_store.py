"""
Integration API Key Store
==========================

Persistent storage for third-party integration API keys (the X-API-Key
header auth used by integration_router.py). Previously these lived only in
a plain module-level dict (api_keys_db = {}), so every key was lost on
every backend restart/redeploy.

Only a SHA-256 hash of the key is ever stored - the raw key is generated
and returned to the caller exactly once, at creation time, and is never
persisted or logged. Validation hashes the presented key and looks up the
hash, rather than looking up the raw key directly.

Uses the same SQLAlchemy Base/engine/session machinery as database.py, so
this table is created automatically by init_database() and shares the
existing connection pool (same pattern as smart_session_store.py). Falls
back to an in-memory dict keyed by key_id when DATABASE_AVAILABLE is False,
mirroring auth_service.py's users_db fallback pattern.
"""

import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any, List

from .database import Base, DATABASE_AVAILABLE, get_db_session

if DATABASE_AVAILABLE and Base is not None:
    from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON

    class ApiKey(Base):
        """A single integration API key. The raw key itself is never
        stored - only its SHA-256 hash (for validation lookups) and a
        short, non-secret prefix (for display in list views)."""
        __tablename__ = "api_keys"

        id = Column(Integer, primary_key=True, index=True)
        key_id = Column(String(64), unique=True, nullable=False, index=True)
        key_hash = Column(String(64), unique=True, nullable=False, index=True)
        key_prefix = Column(String(20), nullable=False)
        name = Column(String(255), nullable=False)
        scopes = Column(JSON, nullable=False, default=list)
        user_id = Column(String(255), nullable=False, index=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        expires_at = Column(DateTime, nullable=True)
        revoked = Column(Boolean, default=False)
        revoked_at = Column(DateTime, nullable=True)
else:
    ApiKey = None

# In-memory fallback, keyed by key_id (mirrors auth_service.py's users_db).
_api_keys_db: Dict[str, Dict[str, Any]] = {}


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _public_dict(record: Dict[str, Any]) -> Dict[str, Any]:
    """Metadata safe to return to callers - never includes key_hash."""
    return {
        "key_id": record["key_id"],
        "key_prefix": record["key_prefix"],
        "name": record["name"],
        "scopes": record["scopes"],
        "user_id": record["user_id"],
        "created_at": _iso(record["created_at"]),
        "expires_at": _iso(record["expires_at"]),
        "revoked": record["revoked"],
        "revoked_at": _iso(record["revoked_at"]),
    }


def create_api_key(
    name: str,
    scopes: List[str],
    user_id: str,
    expires_at: Optional[datetime],
) -> Dict[str, Any]:
    """Generate + persist a new API key. Returns the raw key (only ever
    available here, at creation time) plus its public metadata."""
    raw_key = f"rdiag_{secrets.token_urlsafe(32)}"
    key_id = f"key_{secrets.token_urlsafe(12)}"
    record = {
        "key_id": key_id,
        "key_hash": _hash_key(raw_key),
        "key_prefix": raw_key[:14],
        "name": name,
        "scopes": scopes,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "revoked": False,
        "revoked_at": None,
    }

    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            db.add(ApiKey(**record))
    else:
        _api_keys_db[key_id] = record

    return {"raw_key": raw_key, **_public_dict(record)}


def get_api_key_by_raw(raw_key: str) -> Optional[Dict[str, Any]]:
    """Look up a key's metadata by the raw key a caller presented, for
    validation. Hashes the presented key rather than storing/matching it
    directly."""
    key_hash = _hash_key(raw_key)
    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            row = db.query(ApiKey).filter_by(key_hash=key_hash).first()
            if row is None:
                return None
            return _public_dict(row.__dict__)
    for record in _api_keys_db.values():
        if record["key_hash"] == key_hash:
            return _public_dict(record)
    return None


def get_api_key_by_id(key_id: str) -> Optional[Dict[str, Any]]:
    """Look up a key's metadata by its (non-secret) key_id - used for
    ownership checks on revocation, not for authenticating requests."""
    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            row = db.query(ApiKey).filter_by(key_id=key_id).first()
            return _public_dict(row.__dict__) if row else None
    record = _api_keys_db.get(key_id)
    return _public_dict(record) if record else None


def list_api_keys_for_user(user_id: str) -> List[Dict[str, Any]]:
    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            rows = db.query(ApiKey).filter_by(user_id=user_id).all()
            return [_public_dict(r.__dict__) for r in rows]
    return [
        _public_dict(record)
        for record in _api_keys_db.values()
        if record["user_id"] == user_id
    ]


def revoke_api_key(key_id: str) -> bool:
    """Mark a key revoked. Returns False if key_id doesn't exist. Callers
    are responsible for authorizing the request (owner or admin) before
    calling this."""
    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            row = db.query(ApiKey).filter_by(key_id=key_id).first()
            if row is None:
                return False
            row.revoked = True
            row.revoked_at = datetime.utcnow()
            return True
    record = _api_keys_db.get(key_id)
    if record is None:
        return False
    record["revoked"] = True
    record["revoked_at"] = datetime.utcnow()
    return True


def count_active_api_keys() -> int:
    if DATABASE_AVAILABLE and ApiKey is not None:
        with get_db_session() as db:
            return db.query(ApiKey).filter_by(revoked=False).count()
    return len([r for r in _api_keys_db.values() if not r.get("revoked")])
