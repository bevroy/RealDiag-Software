"""
SMART on FHIR Session Store
============================

Server-side storage for SMART on FHIR OAuth sessions. The whole point of
this module: the real FHIR access token (and refresh token, if issued)
never leaves the server. The browser only ever holds an opaque, random,
HttpOnly session_id cookie that points at a row here - never the token
itself.

Uses the same SQLAlchemy Base/engine/session machinery as database.py so
this table is created automatically by init_database() and shares the
existing connection pool.
"""

import base64
import logging
import os
import secrets as _secrets
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .database import Base, DATABASE_AVAILABLE, get_db_session

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- tokens at rest
#
# FHIR access and refresh tokens are stored encrypted (Fernet: AES-128-CBC +
# HMAC-SHA256). The key is SMART_TOKEN_ENCRYPTION_KEY (a Fernet key) when set;
# otherwise it is derived with HKDF-SHA256 from JWT_SECRET_KEY, which the app
# already requires, so no extra configuration is needed. Rotating the key ends
# active SMART sessions (they last at most 30 minutes). Stored values carry
# the prefix "enc:v1:"; a value without it (saved before encryption) is read
# as-is until its session expires.

TOKEN_KEY_ENV = "SMART_TOKEN_ENCRYPTION_KEY"
_ENCRYPTED_PREFIX = "enc:v1:"


@lru_cache(maxsize=1)
def _token_cipher() -> Fernet:
    configured = os.getenv(TOKEN_KEY_ENV, "").strip()
    if configured:
        return Fernet(configured.encode())
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if not secret:
        raise RuntimeError(f"Set {TOKEN_KEY_ENV} or JWT_SECRET_KEY to store SMART session tokens")
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"realdiag-smart-session-tokens").derive(secret.encode())
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_token(token: Optional[str]) -> Optional[str]:
    if token is None:
        return None
    return _ENCRYPTED_PREFIX + _token_cipher().encrypt(token.encode()).decode()


def decrypt_token(stored: Optional[str]) -> Optional[str]:
    """Plain token from a stored value. Raises InvalidToken if it cannot be decrypted."""
    if stored is None or not stored.startswith(_ENCRYPTED_PREFIX):
        return stored  # saved before encryption; expires with its session
    return _token_cipher().decrypt(stored[len(_ENCRYPTED_PREFIX):].encode()).decode()


if DATABASE_AVAILABLE and Base is not None:
    from sqlalchemy import Column, Integer, String, Text, DateTime

    class SmartSession(Base):
        """A single SMART on FHIR OAuth session.

        Created once, at the end of the /smart/callback exchange, and
        looked up (never mutated) by every subsequent /smart/* call that
        needs to talk to the EHR's FHIR server on the clinician's behalf.
        """
        __tablename__ = "smart_sessions"

        id = Column(Integer, primary_key=True, index=True)
        session_id = Column(String(255), unique=True, nullable=False, index=True)
        ehr_vendor = Column(String(50), nullable=False)
        iss = Column(String(500), nullable=False)
        patient_id = Column(String(255), nullable=True)
        fhir_access_token = Column(Text, nullable=False)
        fhir_refresh_token = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        expires_at = Column(DateTime, nullable=False)

        def to_dict(self) -> Dict[str, Any]:
            """Deliberately excludes fhir_access_token/fhir_refresh_token -
            those never leave the server, even in an internal debug dump."""
            return {
                "session_id": self.session_id,
                "ehr_vendor": self.ehr_vendor,
                "patient_id": self.patient_id,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            }
else:
    SmartSession = None


def create_smart_session(
    ehr_vendor: str,
    iss: str,
    patient_id: Optional[str],
    fhir_access_token: str,
    fhir_refresh_token: Optional[str],
    expires_at: datetime,
) -> Optional[str]:
    """Persist a new SMART session server-side and return its opaque id.

    Returns None if no database is configured - callers must treat that as
    a hard failure (there is nowhere safe to hold the token) rather than
    falling back to handing the token to the browser.
    """
    if not DATABASE_AVAILABLE or SmartSession is None:
        return None

    session_id = _secrets.token_urlsafe(32)
    with get_db_session() as db:
        db.add(SmartSession(
            session_id=session_id,
            ehr_vendor=ehr_vendor,
            iss=iss,
            patient_id=patient_id,
            fhir_access_token=encrypt_token(fhir_access_token),
            fhir_refresh_token=encrypt_token(fhir_refresh_token),
            expires_at=expires_at,
        ))
    return session_id


def get_smart_session(session_id: str):
    """Look up an active SMART session by its opaque id. Does not check
    expiry - callers should compare .expires_at themselves.

    The returned (detached) row carries the decrypted tokens. A session whose
    tokens cannot be decrypted (e.g. the key changed) is treated as missing.
    """
    if not DATABASE_AVAILABLE or SmartSession is None or not session_id:
        return None
    with get_db_session() as db:
        row = db.query(SmartSession).filter_by(session_id=session_id).first()
        if row is None: return None
        # Detach the row before this session commits/closes below, so
        # callers can safely read its attributes afterward without a
        # DetachedInstanceError.
        db.expunge(row)
    try:
        row.fhir_access_token = decrypt_token(row.fhir_access_token)
        row.fhir_refresh_token = decrypt_token(row.fhir_refresh_token)
    except InvalidToken:
        logger.warning("SMART session tokens could not be decrypted (key changed?); treating session as expired")
        return None
    return row
        
        
def delete_smart_session(session_id: str) -> None:
    """Remove a SMART session, e.g. once it's expired."""
    if not DATABASE_AVAILABLE or SmartSession is None or not session_id:
        return
    with get_db_session() as db:
        db.query(SmartSession).filter_by(session_id=session_id).delete()
