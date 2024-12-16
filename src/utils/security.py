import hashlib
import secrets
from base64 import b64encode
from typing import Optional, Tuple
from cryptography.fernet import Fernet

class Security:
    """Security utilities for the agent."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
    def generate_nonce(self, length: int = 32) -> str:
        """Generate a secure random nonce."""
        return b64encode(secrets.token_bytes(length)).decode('utf-8')
        
    def hash_data(self, data: str) -> str:
        """Create a secure hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()
        
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.fernet.encrypt(data.encode()).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted data."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
        
    def generate_api_key(self) -> Tuple[str, str]:
        """Generate an API key and its hash."""
        api_key = secrets.token_urlsafe(32)
        api_key_hash = self.hash_data(api_key)
        return api_key, api_key_hash
        
    def verify_api_key(self, api_key: str, api_key_hash: str) -> bool:
        """Verify an API key against its hash."""
        return self.hash_data(api_key) == api_key_hash