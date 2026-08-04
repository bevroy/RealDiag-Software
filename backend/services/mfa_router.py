"""
MFA Router

API endpoints for multi-factor authentication setup and verification.

PATCHED (audit fixes):
- Every endpoint below used to have its state-mutating lines commented out
  (e.g. `# current_user['mfa_enabled'] = True`), so enrollment never
  actually saved a secret, verification never enabled MFA, and backup
  codes could be reused indefinitely because "remove after use" was also
  commented out. All of that now goes through auth_service's
  get_user_mfa_state()/update_user_mfa_state(), which read/write the real
  database row (or in-memory record) instead of the disposable
  `current_user` dict.
- Added POST /mfa/login-verify: previously nothing in the codebase ever
  required a second factor at login even for users who had "enabled" MFA,
  because user_router.login_user() issued a full session cookie right
  after the password check. Login now issues a short-lived mfa_pending
  token instead when MFA is enabled, and this endpoint exchanges a valid
  TOTP/backup code (plus that pending token) for the real session cookie.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .mfa_service import get_mfa_service, MFAService
from .auth_service import (
    get_current_user,
    get_user_mfa_state,
    update_user_mfa_state,
    verify_mfa_pending_token,
    create_access_token,
)
from .auth_cookies import create_cookie_response
import secrets as _secrets

router = APIRouter(prefix="/mfa", tags=["mfa"])


class MFAEnrollResponse(BaseModel):
    """Response for MFA enrollment"""
    secret: str = Field(..., description="TOTP secret key (store securely)")
    qr_code: str = Field(..., description="QR code data URI for authenticator app")
    backup_codes: List[str] = Field(..., description="One-time backup codes")


class MFAVerifyRequest(BaseModel):
    """Request to verify TOTP token"""
    token: str = Field(..., description="6-digit TOTP code", min_length=6, max_length=6)


class MFAVerifyResponse(BaseModel):
    """Response for MFA verification"""
    valid: bool = Field(..., description="Whether token is valid")
    message: str = Field(..., description="Result message")


class MFAStatusResponse(BaseModel):
    """MFA status for current user"""
    enabled: bool = Field(..., description="Whether MFA is enabled")
    enrolled_at: Optional[datetime] = Field(None, description="When MFA was enrolled")
    backup_codes_remaining: int = Field(..., description="Number of unused backup codes")


class MFALoginVerifyRequest(BaseModel):
    """Completes login for a user whose account has MFA enabled."""
    mfa_token: str = Field(..., description="The mfa_pending token returned by /users/login")
    token: Optional[str] = Field(None, description="6-digit TOTP code")
    backup_code: Optional[str] = Field(None, description="Backup code, alternative to token")


@router.post("/enroll", response_model=MFAEnrollResponse)
async def enroll_mfa(
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Enroll in multi-factor authentication.

    Returns:
        - TOTP secret (user must store this securely)
        - QR code for authenticator app (Google Authenticator, Authy, etc.)
        - Backup codes for account recovery

    **Important:** User must verify a token before MFA is fully enabled.
    """
    if current_user.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA already enabled for this account"
        )

    # Generate new secret
    secret = mfa_service.generate_secret()

    # Generate QR code
    email = current_user.get('email', current_user.get('username'))
    qr_code = mfa_service.generate_qr_code(email, secret)

    # Generate backup codes
    backup_codes = mfa_service.generate_backup_codes(10)

    # Hash backup codes for storage
    hashed_codes = [mfa_service.hash_backup_code(code) for code in backup_codes]

    # Persist pending MFA state until first successful verification.
    update_user_mfa_state(
        current_user["user_id"],
        mfa_secret=secret,
        mfa_backup_codes=hashed_codes,
        mfa_pending=True,
    )

    return MFAEnrollResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa_token(
    request: MFAVerifyRequest,
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Verify a TOTP token to complete enrollment.

    Args:
        token: 6-digit code from authenticator app

    Returns:
        Verification result
    """
    mfa_state = get_user_mfa_state(current_user["user_id"])
    secret = mfa_state.get('mfa_secret')
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this account"
        )

    is_valid = mfa_service.verify_token(secret, request.token)

    if is_valid and mfa_state.get('mfa_pending'):
        update_user_mfa_state(
            current_user["user_id"],
            mfa_enabled=True,
            mfa_pending=False,
            mfa_enrolled_at=datetime.utcnow(),
        )
        return MFAVerifyResponse(valid=True, message="MFA enabled successfully")
    if is_valid:
        return MFAVerifyResponse(valid=True, message="Token verified")
    return MFAVerifyResponse(valid=False, message="Invalid token")


@router.post("/verify-backup", response_model=MFAVerifyResponse)
async def verify_backup_code(
    request: MFAVerifyRequest,
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Verify and consume a backup code."""
    mfa_state = get_user_mfa_state(current_user["user_id"])
    backup_codes = mfa_state.get('mfa_backup_codes', [])
    if not backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup codes available"
        )

    for i, hashed_code in enumerate(backup_codes):
        if mfa_service.verify_backup_code(request.token, hashed_code):
            remaining = backup_codes[:i] + backup_codes[i + 1:]
            update_user_mfa_state(current_user["user_id"], mfa_backup_codes=remaining)
            return MFAVerifyResponse(
                valid=True,
                message=f"Backup code accepted. {len(remaining)} codes remaining."
            )

    return MFAVerifyResponse(valid=False, message="Invalid backup code")


@router.delete("/disable")
async def disable_mfa(current_user: dict = Depends(get_current_user)):
    """Disable MFA for current user."""
    if not current_user.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled"
        )

    update_user_mfa_state(
        current_user["user_id"],
        mfa_enabled=False,
        mfa_pending=False,
        mfa_secret=None,
        mfa_backup_codes=[],
    )

    return {"message": "MFA disabled successfully"}


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(current_user: dict = Depends(get_current_user)):
    """Get MFA status for current user."""
    mfa_state = get_user_mfa_state(current_user["user_id"])
    return MFAStatusResponse(
        enabled=mfa_state.get('mfa_enabled', False),
        enrolled_at=mfa_state.get('mfa_enrolled_at'),
        backup_codes_remaining=len(mfa_state.get('mfa_backup_codes', []))
    )


@router.post("/regenerate-backup-codes", response_model=List[str])
async def regenerate_backup_codes(
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Generate and persist a fresh backup-code set."""
    mfa_state = get_user_mfa_state(current_user["user_id"])
    if not mfa_state.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA must be enabled to generate backup codes"
        )

    backup_codes = mfa_service.generate_backup_codes(10)
    hashed_codes = [mfa_service.hash_backup_code(code) for code in backup_codes]
    update_user_mfa_state(current_user["user_id"], mfa_backup_codes=hashed_codes)

    return backup_codes


@router.post("/login-verify")
async def login_verify(
    request: MFALoginVerifyRequest,
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Complete login for an MFA-enabled account.

    Exchanges a valid mfa_pending token plus a TOTP/backup code for the
    normal authenticated cookie session.
    """
    payload = verify_mfa_pending_token(request.mfa_token)
    user_id = payload.get("sub")
    email = payload.get("email")

    mfa_state = get_user_mfa_state(user_id)
    if not mfa_state.get("mfa_enabled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this account")

    verified = False
    if request.token:
        verified = mfa_service.verify_token(mfa_state.get("mfa_secret"), request.token)
    elif request.backup_code:
        backup_codes = mfa_state.get("mfa_backup_codes", [])
        for i, hashed_code in enumerate(backup_codes):
            if mfa_service.verify_backup_code(request.backup_code, hashed_code):
                verified = True
                remaining = backup_codes[:i] + backup_codes[i + 1:]
                update_user_mfa_state(user_id, mfa_backup_codes=remaining)
                break
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token or backup_code is required")

    if not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    access_token = create_access_token(user_id, email)
    refresh_token = _secrets.token_urlsafe(32)

    return create_cookie_response(
        data={"message": "Login successful"},
        access_token=access_token,
        refresh_token=refresh_token,
    )
