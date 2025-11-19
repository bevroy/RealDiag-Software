"""
Security Middleware and Utilities
Implements rate limiting, security headers, and input sanitization
"""

import time
import hashlib
import secrets
from typing import Optional, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger("realdiag.security")

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])


class SecurityHeaders:
    """Add security headers to all responses"""
    
    @staticmethod
    def add_headers(response) -> None:
        """Add comprehensive security headers"""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS - Force HTTPS (only in production)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"


async def security_middleware(request: Request, call_next):
    """Middleware to add security headers to all responses"""
    try:
        response = await call_next(request)
        SecurityHeaders.add_headers(response)
        return response
    except Exception as e:
        logger.error(f"Security middleware error: {str(e)}")
        raise


class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize string input by removing dangerous characters"""
        if not value:
            return ""
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim to max length
        value = value[:max_length]
        
        # Remove HTML tags (basic sanitization)
        import re
        value = re.sub(r'<[^>]*>', '', value)
        
        return value.strip()
    
    @staticmethod
    def validate_age(age: Optional[int]) -> Optional[int]:
        """Validate age is in reasonable range"""
        if age is None:
            return None
        
        if not isinstance(age, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age must be an integer"
            )
        
        if age < 0 or age > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age must be between 0 and 120"
            )
        
        return age
    
    @staticmethod
    def validate_symptoms(symptoms: list) -> list:
        """Validate symptom list"""
        if not symptoms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one symptom is required"
            )
        
        if len(symptoms) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 symptoms allowed"
            )
        
        # Sanitize each symptom
        sanitized = []
        for symptom in symptoms:
            if not isinstance(symptom, str):
                continue
            
            clean = InputValidator.sanitize_string(symptom, max_length=200)
            if clean:
                sanitized.append(clean)
        
        if not sanitized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid symptoms provided"
            )
        
        return sanitized


class AuditLogger:
    """Log security-relevant events for audit trail"""
    
    @staticmethod
    def log_authentication(user_id: str, success: bool, ip: str, user_agent: str):
        """Log authentication attempt"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip,
            "user_agent": user_agent
        }
        
        if success:
            logger.info(f"AUTH_SUCCESS: {event}")
        else:
            logger.warning(f"AUTH_FAILURE: {event}")
    
    @staticmethod
    def log_data_access(user_id: str, resource: str, action: str, ip: str):
        """Log data access for HIPAA compliance"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "data_access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip
        }
        logger.info(f"DATA_ACCESS: {event}")
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log general security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if severity == "ERROR":
            logger.error(f"SECURITY_EVENT: {event}")
        elif severity == "WARNING":
            logger.warning(f"SECURITY_EVENT: {event}")
        else:
            logger.info(f"SECURITY_EVENT: {event}")


class TokenManager:
    """Manage JWT tokens with refresh capability"""
    
    def __init__(self):
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
        self.token_blacklist: set = set()
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate a secure refresh token"""
        token = secrets.token_urlsafe(32)
        
        self.refresh_tokens[token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }
        
        return token
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        """Validate refresh token and return user_id if valid"""
        if token not in self.refresh_tokens:
            return None
        
        token_data = self.refresh_tokens[token]
        
        # Check expiration
        if datetime.utcnow() > token_data["expires_at"]:
            del self.refresh_tokens[token]
            return None
        
        return token_data["user_id"]
    
    def revoke_refresh_token(self, token: str):
        """Revoke a refresh token"""
        if token in self.refresh_tokens:
            del self.refresh_tokens[token]
    
    def blacklist_token(self, token: str):
        """Add token to blacklist (for logout)"""
        self.token_blacklist.add(token)
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in self.token_blacklist


class APIKeyManager:
    """Persistent API key management"""
    
    def __init__(self, storage_file: str = "data/api_keys.json"):
        self.storage_file = storage_file
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from file"""
        import os
        import json
        
        if not os.path.exists(self.storage_file):
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            self._save_keys()
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.api_keys = data.get('keys', {})
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            self.api_keys = {}
    
    def _save_keys(self):
        """Save API keys to file"""
        import json
        
        try:
            with open(self.storage_file, 'w') as f:
                json.dump({'keys': self.api_keys}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
    
    def create_key(self, name: str, permissions: list = None) -> str:
        """Create a new API key"""
        api_key = secrets.token_urlsafe(32)
        
        self.api_keys[api_key] = {
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "permissions": permissions or ["read"],
            "last_used": None,
            "usage_count": 0
        }
        
        self._save_keys()
        return api_key
    
    def validate_key(self, api_key: str) -> bool:
        """Validate API key"""
        if api_key not in self.api_keys:
            return False
        
        # Update usage stats
        self.api_keys[api_key]["last_used"] = datetime.utcnow().isoformat()
        self.api_keys[api_key]["usage_count"] += 1
        self._save_keys()
        
        return True
    
    def revoke_key(self, api_key: str):
        """Revoke an API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            self._save_keys()
    
    def list_keys(self) -> Dict[str, Dict[str, Any]]:
        """List all API keys (without showing the actual keys)"""
        return {
            key[:8] + "...": {
                "name": data["name"],
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "usage_count": data["usage_count"]
            }
            for key, data in self.api_keys.items()
        }


# Global instances
token_manager = TokenManager()
api_key_manager = APIKeyManager()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
