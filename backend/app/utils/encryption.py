import base64
import hashlib
from cryptography.fernet import Fernet

def get_fernet(key: str) -> Fernet:
    """Creates Fernet instance from key, padding/hashing to 32 bytes and base64 encoding."""
    hasher = hashlib.sha256()
    hasher.update(key.encode('utf-8'))
    key_32_bytes = hasher.digest()
    b64_key = base64.urlsafe_b64encode(key_32_bytes)
    return Fernet(b64_key)

def encrypt_data(data: str, key: str) -> str:
    """Encrypts string, returns base64."""
    fernet = get_fernet(key)
    encrypted = fernet.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_data(encrypted: str, key: str) -> str:
    """Decrypts string."""
    fernet = get_fernet(key)
    encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode('utf-8')
