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

import logging
import secrets as _secrets
from datetime import datetime
from typing import Optional, Dict, Any

from .database import Base, DATABASE_AVAILABLE, get_db_session

logger = logging.getLogger(__name__)

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
            fhir_access_token=fhir_access_token,
            fhir_refresh_token=fhir_refresh_token,
            expires_at=expires_at,
        ))
    return session_id


def get_smart_session(session_id: str):
    """Look up an active SMART session by its opaque id. Does not check
    expiry - callers should compare .expires_at themselves."""
    if not DATABASE_AVAILABLE or SmartSession is None or not session_id:
        return None
    with get_db_session() as db:
        return db.query(SmartSession).filter_by(session_id=session_id).first()


def delete_smart_session(session_id: str) -> None:
    """Remove a SMART session, e.g. once it's expired."""
    if not DATABASE_AVAILABLE or SmartSession is None or not session_id:
        return
    with get_db_session() as db:
        db.query(SmartSession).filter_by(session_id=session_id).delete()
