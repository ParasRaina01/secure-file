import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from django.core.files.base import ContentFile
from .key_management import key_manager


def generate_key():
    """Generate a random 32-byte key for AES-256."""
    return key_manager.generate_file_key()


def generate_iv():
    """Generate a random 16-byte initialization vector."""
    return key_manager.generate_iv()


def pad_data(data):
    """Pad data to be compatible with AES block size."""
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data)
    padded_data += padder.finalize()
    return padded_data


def unpad_data(padded_data):
    """Remove padding from decrypted data."""
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data)
    data += unpadder.finalize()
    return data


def encrypt_file(file_obj):
    """
    Encrypt a file using AES-256-CBC.
    
    Args:
        file_obj: A file-like object to encrypt
        
    Returns:
        tuple: (encrypted_file, encrypted_key, iv)
            - encrypted_file: Django ContentFile with encrypted data
            - encrypted_key: The encrypted key (bytes)
            - iv: The initialization vector (bytes)
    """
    # Generate key and IV
    key = generate_key()
    iv = generate_iv()
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Read and encrypt file data
    file_data = file_obj.read()
    padded_data = pad_data(file_data)
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Create a new file with encrypted data
    encrypted_file = ContentFile(encrypted_data)
    
    # Encrypt the key with the master key
    encrypted_key = key_manager.encrypt_key(key)
    
    return encrypted_file, encrypted_key, iv


def decrypt_file(file_obj, encrypted_key, iv):
    """
    Decrypt a file using AES-256-CBC.
    
    Args:
        file_obj: Django File object containing encrypted data
        encrypted_key: The encrypted key (bytes)
        iv: The initialization vector (bytes)
        
    Returns:
        ContentFile: A new file-like object containing the decrypted data
    """
    # Decrypt the key using the master key
    key = key_manager.decrypt_key(encrypted_key)
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Read and decrypt file data
    encrypted_data = file_obj.read()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    decrypted_data = unpad_data(padded_data)
    
    # Create a new file with decrypted data
    return ContentFile(decrypted_data) 