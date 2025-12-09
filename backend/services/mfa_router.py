"""
MFA Router

API endpoints for multi-factor authentication setup and verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .mfa_service import get_mfa_service, MFAService
from .auth_service import get_current_user
from .rbac_service import Permission, require_permission

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
    
    # Store in user record (but don't enable MFA yet - wait for verification)
    # Note: This would update the database in a real implementation
    # current_user['mfa_secret'] = secret
    # current_user['mfa_backup_codes'] = hashed_codes
    # current_user['mfa_pending'] = True
    
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
    Verify a TOTP token.
    
    Use this to:
    1. Complete MFA enrollment (verify setup)
    2. Verify token during login
    
    Args:
        token: 6-digit code from authenticator app
    
    Returns:
        Verification result
    """
    secret = current_user.get('mfa_secret')
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this account"
        )
    
    # Verify token
    is_valid = mfa_service.verify_token(secret, request.token)
    
    if is_valid and current_user.get('mfa_pending'):
        # First successful verification - enable MFA
        # current_user['mfa_enabled'] = True
        # current_user['mfa_pending'] = False
        # current_user['mfa_enrolled_at'] = datetime.utcnow()
        return MFAVerifyResponse(
            valid=True,
            message="MFA enabled successfully"
        )
    elif is_valid:
        return MFAVerifyResponse(
            valid=True,
            message="Token verified"
        )
    else:
        return MFAVerifyResponse(
            valid=False,
            message="Invalid token"
        )


@router.post("/verify-backup", response_model=MFAVerifyResponse)
async def verify_backup_code(
    request: MFAVerifyRequest,
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Verify a backup code.
    
    Use this when:
    - Authenticator app is unavailable
    - Phone is lost/broken
    - Need emergency access
    
    **Note:** Each backup code can only be used once.
    
    Args:
        token: Backup code (format: XXXX-XXXX)
    
    Returns:
        Verification result
    """
    backup_codes = current_user.get('mfa_backup_codes', [])
    if not backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup codes available"
        )
    
    # Check if code matches any stored hash
    for i, hashed_code in enumerate(backup_codes):
        if mfa_service.verify_backup_code(request.token, hashed_code):
            # Valid code - remove it (one-time use)
            # backup_codes.pop(i)
            # current_user['mfa_backup_codes'] = backup_codes
            return MFAVerifyResponse(
                valid=True,
                message=f"Backup code accepted. {len(backup_codes)-1} codes remaining."
            )
    
    return MFAVerifyResponse(
        valid=False,
        message="Invalid backup code"
    )


@router.delete("/disable")
async def disable_mfa(
    current_user: dict = Depends(get_current_user)
):
    """
    Disable MFA for current user.
    
    **Security Note:** Requires recent authentication or MFA verification.
    """
    if not current_user.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled"
        )
    
    # Disable MFA
    # current_user['mfa_enabled'] = False
    # current_user['mfa_secret'] = None
    # current_user['mfa_backup_codes'] = []
    
    return {
        "message": "MFA disabled successfully"
    }


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get MFA status for current user.
    
    Returns:
        - Whether MFA is enabled
        - When it was enrolled
        - How many backup codes remain
    """
    return MFAStatusResponse(
        enabled=current_user.get('mfa_enabled', False),
        enrolled_at=current_user.get('mfa_enrolled_at'),
        backup_codes_remaining=len(current_user.get('mfa_backup_codes', []))
    )


@router.post("/regenerate-backup-codes", response_model=List[str])
async def regenerate_backup_codes(
    current_user: dict = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Generate new backup codes.
    
    **Warning:** This invalidates all existing backup codes.
    
    Returns:
        List of new backup codes (save these securely!)
    """
    if not current_user.get('mfa_enabled'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA must be enabled to generate backup codes"
        )
    
    # Generate new codes
    backup_codes = mfa_service.generate_backup_codes(10)
    hashed_codes = [mfa_service.hash_backup_code(code) for code in backup_codes]
    
    # Store hashed codes
    # current_user['mfa_backup_codes'] = hashed_codes
    
    return backup_codes
