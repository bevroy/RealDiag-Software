"""
Database Encryption Utilities

Provides column-level encryption for PHI/PII fields using Fernet (symmetric encryption).
Based on cryptography library with secure key management.
"""

import os
import base64
from typing import Optional, Any
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging

logger = logging.getLogger(__name__)

class FieldEncryption:
    """
    Handle field-level encryption for database columns.
    Uses Fernet (symmetric encryption) with AES-128.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption with key from environment or parameter.
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, reads from DATABASE_ENCRYPTION_KEY env var.
        """
        key = encryption_key or os.getenv('DATABASE_ENCRYPTION_KEY')
        
        if not key:
            logger.warning("DATABASE_ENCRYPTION_KEY not set - encryption disabled")
            self.enabled = False
            self.cipher = None
        else:
            try:
                # Validate and create Fernet cipher
                self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
                self.enabled = True
                logger.info("Database encryption enabled")
            except Exception as e:
                logger.error(f"Failed to initialize encryption: {e}")
                self.enabled = False
                self.cipher = None
    
    def encrypt(self, plaintext: Any) -> Optional[str]:
        """
        Encrypt a value for database storage.
        
        Args:
            plaintext: Value to encrypt (will be converted to string)
            
        Returns:
            Base64-encoded encrypted value, or None if encryption fails/disabled
        """
        if not self.enabled or not self.cipher:
            return plaintext  # Return unencrypted if disabled
        
        if plaintext is None:
            return None
        
        try:
            # Convert to string and encode
            plaintext_str = str(plaintext)
            plaintext_bytes = plaintext_str.encode('utf-8')
            
            # Encrypt
            encrypted_bytes = self.cipher.encrypt(plaintext_bytes)
            
            # Return as string for database storage
            return encrypted_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, ciphertext: str) -> Optional[str]:
        """
        Decrypt a value from database.
        
        Args:
            ciphertext: Encrypted value from database
            
        Returns:
            Decrypted plaintext, or None if decryption fails
        """
        if not self.enabled or not self.cipher:
            return ciphertext  # Return as-is if encryption disabled
        
        if ciphertext is None:
            return None
        
        try:
            # Convert to bytes
            ciphertext_bytes = ciphertext.encode('utf-8')
            
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(ciphertext_bytes)
            
            # Return as string
            return decrypted_bytes.decode('utf-8')
            
        except InvalidToken:
            logger.error("Decryption failed - invalid token or corrupted data")
            return None
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with fields to encrypt
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        if not self.enabled:
            return data
        
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[field] = self.encrypt(encrypted_data[field])
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted fields
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        if not self.enabled:
            return data
        
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field] is not None:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        
        return decrypted_data


# Global encryption instance
_encryption_instance = None

def get_encryption() -> FieldEncryption:
    """Get global encryption instance (singleton)"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = FieldEncryption()
    return _encryption_instance


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this to generate DATABASE_ENCRYPTION_KEY for .env file.
    
    Returns:
        Base64-encoded Fernet key
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


def derive_key_from_password(password: str, salt: bytes = None) -> str:
    """
    Derive a Fernet key from a password using PBKDF2.
    
    Args:
        password: Master password
        salt: Salt for key derivation (generates random if None)
        
    Returns:
        Base64-encoded Fernet key
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode('utf-8')


# PHI/PII fields that should be encrypted
PHI_FIELDS = [
    'mrn',  # Medical Record Number
    'name',  # Patient name
    'date_of_birth',
    'ssn',
    'address',
    'phone',
    'email',
    'emergency_contact',
    'insurance_id',
    'medications',  # Current medications
    'allergies',
    'medical_history',
    'chief_complaint',
    'symptoms',
    'diagnosis_notes',
    'treatment_plan'
]


def encrypt_phi(data: dict) -> dict:
    """
    Encrypt all PHI fields in a dictionary.
    
    Args:
        data: Dictionary potentially containing PHI
        
    Returns:
        Dictionary with encrypted PHI fields
    """
    encryption = get_encryption()
    return encryption.encrypt_dict(data, PHI_FIELDS)


def decrypt_phi(data: dict) -> dict:
    """
    Decrypt all PHI fields in a dictionary.
    
    Args:
        data: Dictionary with encrypted PHI fields
        
    Returns:
        Dictionary with decrypted PHI fields
    """
    encryption = get_encryption()
    return encryption.decrypt_dict(data, PHI_FIELDS)


if __name__ == '__main__':
    # Generate a new encryption key for setup
    print("Generated Fernet encryption key:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file as:")
    print("DATABASE_ENCRYPTION_KEY=<key_above>")
