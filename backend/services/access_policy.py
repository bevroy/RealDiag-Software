"""
Who may have a RealDiag account, and what a session needs (invite-only access).

Settings are read on every call, so they can be changed per environment:
- ALLOW_SELF_REGISTRATION (default off): POST /users/register is refused and
  accounts are created only by an admin (invite link or temporary password).
- INVITE_EXPIRATION_HOURS (default 72): how long an account-setup link works.
"""
import os

INVITE_ONLY_DETAIL = ("RealDiag accounts are by invitation only. Ask your RealDiag administrator for an invite.")


def _flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def self_registration_allowed() -> bool:
    return _flag("ALLOW_SELF_REGISTRATION", False)


def invite_expiration_hours() -> int:
    return int(os.getenv("INVITE_EXPIRATION_HOURS", "72"))
