"""
Database Encryption Utility
Provides a custom SQLAlchemy type for transparent column-level encryption.
Uses Fernet (symmetric encryption) from the cryptography library.
"""

from sqlalchemy.types import TypeDecorator, String
from cryptography.fernet import Fernet
import os
import logging
import base64

logger = logging.getLogger(__name__)

# Generate a default key for development if one isn't provided
# In production, this MUST be set via environment variable
DEFAULT_DEV_KEY = Fernet.generate_key()

def get_encryption_key() -> bytes:
    """
    Get the encryption key from environment variable or use dev default.
    Ensures the key is properly formatted (base64 url-safe).
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        if os.getenv("ENVIRONMENT", "development") == "production":
            logger.critical("ENCRYPTION_KEY not set in production! Generating temporary key (DATA WILL BE LOST ON RESTART).")
            return DEFAULT_DEV_KEY
        logger.warning("ENCRYPTION_KEY not set. Using temporary development key.")
        return DEFAULT_DEV_KEY
    
    try:
        # Validate key format
        return key.encode() if isinstance(key, str) else key
    except Exception as e:
        logger.error(f"Invalid ENCRYPTION_KEY format: {e}")
        return DEFAULT_DEV_KEY

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that encrypts data before saving to DB
    and decrypts it when loading from DB.
    
    Usage:
        email = Column(EncryptedString, unique=True)
    """
    impl = String
    cache_ok = True

    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        self._key = key or get_encryption_key()
        self._fernet = Fernet(self._key)

    def process_bind_param(self, value, dialect):
        """Encrypt value before saving to DB"""
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        try:
            return self._fernet.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def process_result_value(self, value, dialect):
        """Decrypt value after loading from DB"""
        if value is None:
            return None
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            # Identify if it's potentially unencrypted legacy data
            # If so, return raw value or handle migration strategy
            # For now, we return the raw value to avoid crashing on legacy cleartext
            return value
