from cryptography.fernet import Fernet
from django.conf import settings
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class KeyManagement:
    """Secure key management system for file encryption keys."""
    
    def __init__(self):
        # Use Django's SECRET_KEY to derive a master key
        self.master_key = self._derive_master_key(settings.SECRET_KEY.encode())
        self.fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
    
    def _derive_master_key(self, secret):
        """Derive a master key using PBKDF2."""
        salt = b'secure_file_share'  # In production, this should be stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(secret)
    
    def encrypt_key(self, key):
        """Encrypt a file encryption key using the master key."""
        return self.fernet.encrypt(key)
    
    def decrypt_key(self, encrypted_key):
        """Decrypt a file encryption key using the master key."""
        return self.fernet.decrypt(encrypted_key)
    
    def generate_file_key(self):
        """Generate a new encryption key for a file."""
        return os.urandom(32)
    
    def generate_iv(self):
        """Generate a new initialization vector."""
        return os.urandom(16)


# Global instance
key_manager = KeyManagement() 