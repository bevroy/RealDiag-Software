"""
Multi-Factor Authentication (MFA) Service

Implements TOTP (Time-based One-Time Password) for 2FA.
Compatible with Google Authenticator, Authy, and other TOTP apps.
"""

import pyotp
import qrcode
import io
import base64
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MFAService:
    """
    Handle multi-factor authentication using TOTP.
    """
    
    def __init__(self, issuer_name: str = "RealDiag"):
        """
        Initialize MFA service.
        
        Args:
            issuer_name: Name displayed in authenticator apps
        """
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret for a user.
        
        Returns:
            Base32-encoded secret key
        """
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, email: str, secret: str) -> str:
        """
        Generate provisioning URI for QR code.
        
        Args:
            email: User's email (displayed in authenticator app)
            secret: TOTP secret key
            
        Returns:
            otpauth:// URI for QR code
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, email: str, secret: str) -> str:
        """
        Generate QR code image as base64 data URI.
        
        Args:
            email: User's email
            secret: TOTP secret key
            
        Returns:
            Base64-encoded PNG image data URI
        """
        uri = self.get_provisioning_uri(email, secret)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: User's TOTP secret key
            token: 6-digit code from authenticator app
            window: Number of time windows to check (default 1 = ±30 seconds)
            
        Returns:
            True if token is valid, False otherwise
        """
        if not secret or not token:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            # Remove spaces and validate format
            token = token.replace(' ', '').replace('-', '')
            if not token.isdigit() or len(token) != 6:
                return False
            
            # Verify with time window for clock skew tolerance
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """
        Generate backup codes for account recovery.
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes (8 characters each)
        """
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for secure storage.
        
        Args:
            code: Backup code to hash
            
        Returns:
            Hashed code
        """
        import hashlib
        # Remove formatting
        code = code.replace('-', '').replace(' ', '').upper()
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_backup_code(self, code: str, hashed_code: str) -> bool:
        """
        Verify a backup code against its hash.
        
        Args:
            code: Backup code entered by user
            hashed_code: Stored hash
            
        Returns:
            True if code matches, False otherwise
        """
        return self.hash_backup_code(code) == hashed_code
    
    def get_current_token(self, secret: str) -> str:
        """
        Get current TOTP token (for testing/debugging only).
        
        Args:
            secret: TOTP secret key
            
        Returns:
            Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()


# Global MFA service instance
_mfa_service = None

def get_mfa_service() -> MFAService:
    """Get global MFA service instance (singleton)"""
    global _mfa_service
    if _mfa_service is None:
        _mfa_service = MFAService()
    return _mfa_service


# Database models extension for MFA
def add_mfa_to_user(user_data: Dict) -> Dict:
    """
    Add MFA fields to user dictionary.
    
    Args:
        user_data: User data dictionary
        
    Returns:
        Updated user data with MFA fields
    """
    return {
        **user_data,
        'mfa_enabled': user_data.get('mfa_enabled', False),
        'mfa_secret': user_data.get('mfa_secret'),
        'mfa_backup_codes': user_data.get('mfa_backup_codes', []),
        'mfa_enrolled_at': user_data.get('mfa_enrolled_at')
    }


if __name__ == '__main__':
    # Test MFA functionality
    mfa = MFAService()
    
    # Generate secret
    secret = mfa.generate_secret()
    print(f"Secret: {secret}")
    
    # Generate QR code
    qr_uri = mfa.get_provisioning_uri("user@example.com", secret)
    print(f"QR URI: {qr_uri}")
    
    # Get current token
    token = mfa.get_current_token(secret)
    print(f"Current token: {token}")
    
    # Verify token
    is_valid = mfa.verify_token(secret, token)
    print(f"Token valid: {is_valid}")
    
    # Generate backup codes
    backup_codes = mfa.generate_backup_codes(5)
    print(f"Backup codes: {backup_codes}")
