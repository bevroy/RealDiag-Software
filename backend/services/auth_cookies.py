"""
HttpOnly Cookie Authentication Implementation
Secure JWT storage using HttpOnly cookies instead of localStorage
"""

from fastapi import Response, Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import secrets
import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CookieAuthManager:
    """Manage authentication using secure HttpOnly cookies"""
    
    def __init__(
        self,
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30,
        cookie_secure: bool = True,
        cookie_samesite: str = "strict",
        cookie_domain: Optional[str] = None
    ):
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.cookie_secure = cookie_secure  # True in production (HTTPS)
        self.cookie_samesite = cookie_samesite  # 'strict', 'lax', or 'none'
        self.cookie_domain = cookie_domain
        
        # Cookie names
        self.ACCESS_TOKEN_COOKIE = "access_token"
        self.REFRESH_TOKEN_COOKIE = "refresh_token"
        self.CSRF_TOKEN_COOKIE = "csrf_token"
    
    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        csrf_token: Optional[str] = None
    ):
        """
        Set authentication cookies on response
        
        Args:
            response: FastAPI Response object
            access_token: JWT access token
            refresh_token: JWT refresh token
            csrf_token: CSRF protection token (optional)
        """
        # Access token (short-lived)
        response.set_cookie(
            key=self.ACCESS_TOKEN_COOKIE,
            value=access_token,
            max_age=self.access_token_expire_minutes * 60,
            httponly=True,  # Not accessible via JavaScript
            secure=self.cookie_secure,  # HTTPS only in production
            samesite=self.cookie_samesite,  # CSRF protection
            domain=self.cookie_domain,
            path="/"
        )
        
        # Refresh token (long-lived)
        response.set_cookie(
            key=self.REFRESH_TOKEN_COOKIE,
            value=refresh_token,
            max_age=self.refresh_token_expire_days * 24 * 60 * 60,
            httponly=True,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            domain=self.cookie_domain,
            path="/api/auth/refresh"  # Only sent to refresh endpoint
        )
        
        # CSRF token (if using double-submit cookie pattern)
        if csrf_token:
            response.set_cookie(
                key=self.CSRF_TOKEN_COOKIE,
                value=csrf_token,
                max_age=self.access_token_expire_minutes * 60,
                httponly=False,  # Accessible to JS for CSRF header
                secure=self.cookie_secure,
                samesite=self.cookie_samesite,
                domain=self.cookie_domain,
                path="/"
            )
        
        logger.info("✅ Auth cookies set successfully")
    
    def get_access_token(self, request: Request) -> Optional[str]:
        """Extract access token from cookie"""
        return request.cookies.get(self.ACCESS_TOKEN_COOKIE)
    
    def get_refresh_token(self, request: Request) -> Optional[str]:
        """Extract refresh token from cookie"""
        return request.cookies.get(self.REFRESH_TOKEN_COOKIE)
    
    def get_csrf_token(self, request: Request) -> Optional[str]:
        """Extract CSRF token from cookie"""
        return request.cookies.get(self.CSRF_TOKEN_COOKIE)
    
    def clear_auth_cookies(self, response: Response):
        """Clear all authentication cookies (logout)"""
        response.delete_cookie(
            key=self.ACCESS_TOKEN_COOKIE,
            path="/",
            domain=self.cookie_domain
        )
        response.delete_cookie(
            key=self.REFRESH_TOKEN_COOKIE,
            path="/api/auth/refresh",
            domain=self.cookie_domain
        )
        response.delete_cookie(
            key=self.CSRF_TOKEN_COOKIE,
            path="/",
            domain=self.cookie_domain
        )
        logger.info("✅ Auth cookies cleared")
    
    def generate_csrf_token(self) -> str:
        """Generate secure CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, request: Request, token_from_header: str) -> bool:
        """
        Verify CSRF token using double-submit cookie pattern
        
        Args:
            request: FastAPI Request object
            token_from_header: CSRF token from X-CSRF-Token header
            
        Returns:
            True if tokens match, False otherwise
        """
        token_from_cookie = self.get_csrf_token(request)
        
        if not token_from_cookie or not token_from_header:
            return False
        
        return secrets.compare_digest(token_from_cookie, token_from_header)
    
    def create_refresh_token_hash(self, refresh_token: str) -> str:
        """
        Create hash of refresh token for database storage
        Never store raw tokens in database
        """
        return hashlib.sha256(refresh_token.encode()).hexdigest()


# Global instance
cookie_auth = CookieAuthManager()


# Dependency for extracting tokens from cookies
async def get_token_from_cookie(request: Request) -> str:
    """
    FastAPI dependency to extract and validate access token from cookie
    
    Usage:
        @app.get("/protected")
        async def protected_route(token: str = Depends(get_token_from_cookie)):
            # token is automatically extracted and validated
            pass
    """
    token = cookie_auth.get_access_token(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no access token cookie",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token


async def verify_csrf_protection(request: Request) -> bool:
    """
    FastAPI dependency for CSRF protection
    
    Usage:
        @app.post("/api/action")
        async def action(verified: bool = Depends(verify_csrf_protection)):
            # CSRF token automatically verified
            pass
    """
    # Skip CSRF for safe methods
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return True
    
    # Get CSRF token from header
    csrf_header = request.headers.get("X-CSRF-Token")
    
    if not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing in request header"
        )
    
    # Verify token
    if not cookie_auth.verify_csrf_token(request, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    return True


# Migration helper for existing endpoints
def create_cookie_response(
    data: Dict[str, Any],
    access_token: str,
    refresh_token: str,
    status_code: int = 200
) -> JSONResponse:
    """
    Create JSON response with auth cookies set
    
    Use this to replace existing responses that return tokens in body:
    
    OLD:
        return {"access_token": token, "user": user_data}
    
    NEW:
        return create_cookie_response(
            data={"user": user_data},
            access_token=token,
            refresh_token=refresh_token
        )
    
    Args:
        data: Response body data (without tokens)
        access_token: JWT access token
        refresh_token: JWT refresh token
        status_code: HTTP status code
        
    Returns:
        JSONResponse with cookies set
    """
    # Generate CSRF token
    csrf_token = cookie_auth.generate_csrf_token()
    
    # Add CSRF token to response body for client to use in headers
    data["csrf_token"] = csrf_token
    
    # Create response
    response = JSONResponse(content=data, status_code=status_code)
    
    # Set cookies
    cookie_auth.set_auth_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token,
        csrf_token=csrf_token
    )
    
    return response


# Example usage in existing auth endpoints:
"""
# OLD LOGIN ENDPOINT (returns token in body - INSECURE)
@router.post("/login")
async def login(credentials: LoginCredentials):
    user = authenticate_user(credentials)
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,  # ❌ Stored in localStorage (XSS vulnerable)
        "token_type": "bearer",
        "user": user.dict()
    }

# NEW LOGIN ENDPOINT (returns token in HttpOnly cookie - SECURE)
@router.post("/login")
async def login(credentials: LoginCredentials):
    user = authenticate_user(credentials)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # ✅ Tokens stored in HttpOnly cookies (XSS protected)
    return create_cookie_response(
        data={
            "message": "Login successful",
            "user": user.dict()
        },
        access_token=access_token,
        refresh_token=refresh_token
    )

# LOGOUT ENDPOINT
@router.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logged out successfully"})
    cookie_auth.clear_auth_cookies(response)
    return response

# REFRESH TOKEN ENDPOINT
@router.post("/auth/refresh")
async def refresh_token(request: Request):
    refresh_token = cookie_auth.get_refresh_token(request)
    
    if not refresh_token:
        raise HTTPException(401, "No refresh token")
    
    # Verify refresh token and create new access token
    user_id = verify_refresh_token(refresh_token)
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)  # Token rotation
    
    return create_cookie_response(
        data={"message": "Token refreshed"},
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

# PROTECTED ENDPOINT
@router.get("/profile")
async def get_profile(token: str = Depends(get_token_from_cookie)):
    # Token automatically extracted from cookie
    user = get_current_user(token)
    return {"user": user.dict()}
"""
