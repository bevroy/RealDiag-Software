"""
Who may have a RealDiag account, and what a session needs (invite-only access).

Settings are read on every call, so they can be changed per environment:
- ALLOW_SELF_REGISTRATION (default off): POST /users/register is refused and
  accounts are created only by an admin (invite link or temporary password).
- INVITE_EXPIRATION_HOURS (default 72): how long an account-setup link works.
- REQUIRE_MFA (default on): every session needs two-factor authentication.
  A signed-in account without MFA gets a session limited to MFA_SETUP_PATHS
  until it enrolls; other sessions must carry the "mfa" claim, which is set
  only after a TOTP or backup code is verified.

Who may hold an account: an email at an approved domain (APPROVED_EMAIL_DOMAINS)
or an individual email an admin put on the allowlist (allowed_emails table;
an in-memory set when no database is configured).
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

APPROVED_EMAIL_DOMAINS = {"realdiag.com", "elionyxhealth.com"}
_memory_allowlist: Dict[str, Dict[str, Any]] = {}

NOT_ALLOWED_DETAIL = ("This email is not approved for RealDiag. Accounts are limited to approved email domains "
                      "and to emails an administrator has added to the allowlist.")
INVITE_ONLY_DETAIL = ("RealDiag accounts are by invitation only. Ask your RealDiag administrator for an invite.")


def _flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def self_registration_allowed() -> bool:
    return _flag("ALLOW_SELF_REGISTRATION", False)


def mfa_required() -> bool:
    return _flag("REQUIRE_MFA", True)


# What a signed-in account that has not enrolled in MFA yet may call.
MFA_SETUP_PATHS = frozenset({"/mfa/enroll", "/mfa/verify", "/mfa/status", "/users/me", "/users/logout"})
MFA_SETUP_DETAIL = "Two-factor authentication must be set up before using RealDiag."
MFA_SIGN_IN_AGAIN_DETAIL = "Sign in again with two-factor authentication."


def invite_expiration_hours() -> int:
    return int(os.getenv("INVITE_EXPIRATION_HOURS", "72"))


def normalize_email(email: Optional[str]) -> str:
    return (email or "").strip().lower()


def email_domain_approved(email: Optional[str]) -> bool:
    parts = normalize_email(email).rsplit("@", 1)
    return len(parts) == 2 and parts[1] in APPROVED_EMAIL_DOMAINS


def _db():
    from backend.services import database
    return database if database.DATABASE_AVAILABLE and database.AllowedEmail is not None else None


def email_allowlisted(email: Optional[str]) -> bool:
    address = normalize_email(email)
    if not address:
        return False
    db = _db()
    if db:
        with db.get_db_session() as session:
            return session.query(db.AllowedEmail).filter_by(email=address).first() is not None
    return address in _memory_allowlist


def email_allowed(email: Optional[str]) -> bool:
    """An approved domain, or an individual email on the admin allowlist."""
    return email_domain_approved(email) or email_allowlisted(email)


def list_allowlist() -> List[Dict[str, Any]]:
    db = _db()
    if db:
        with db.get_db_session() as session:
            rows = session.query(db.AllowedEmail).order_by(db.AllowedEmail.email).all()
            return [{"email": r.email, "note": r.note, "added_by": r.added_by,
                     "added_at": r.added_at.isoformat() if r.added_at else None} for r in rows]
    return [dict(v) for _, v in sorted(_memory_allowlist.items())]


def add_to_allowlist(email: str, note: Optional[str], added_by: str) -> Dict[str, Any]:
    address = normalize_email(email)
    if "@" not in address or address.startswith("@") or address.endswith("@"):
        raise ValueError("A full email address is required.")
    entry = {"email": address, "note": note, "added_by": added_by, "added_at": datetime.utcnow().isoformat()}
    db = _db()
    if db:
        with db.get_db_session() as session:
            row = session.query(db.AllowedEmail).filter_by(email=address).first()
            if row is None:
                session.add(db.AllowedEmail(email=address, note=note, added_by=added_by))
            else:
                row.note = note
        return entry
    _memory_allowlist[address] = entry
    return entry


def remove_from_allowlist(email: str) -> bool:
    address = normalize_email(email)
    db = _db()
    if db:
        with db.get_db_session() as session:
            row = session.query(db.AllowedEmail).filter_by(email=address).first()
            if row is None:
                return False
            session.delete(row)
            return True
    return _memory_allowlist.pop(address, None) is not None
