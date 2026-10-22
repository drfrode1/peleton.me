import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, status

from peleton_api.core.config import settings


@dataclass
class EncryptedToken:
    ciphertext: str
    iv: str
    tag: str


def get_encryption_key() -> bytes:
    """Retrieves and validates the 32-byte Base64-encoded encryption key."""
    encoded = settings.strava_token_encryption_key
    if not encoded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Strava token encryption is not configured.",
        )
    try:
        key = base64.b64decode(encoded)
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes.")
        return key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Strava token encryption is not configured correctly: {e!s}",
        ) from e


def encrypt_token(token: str) -> EncryptedToken:
    """Encrypts plaintext token using AES-256-GCM, returning Base64 components."""
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)  # 96-bit nonce
    encrypted = aesgcm.encrypt(iv, token.encode("utf-8"), None)
    ciphertext = encrypted[:-16]
    tag = encrypted[-16:]

    return EncryptedToken(
        ciphertext=base64.b64encode(ciphertext).decode("utf-8"),
        iv=base64.b64encode(iv).decode("utf-8"),
        tag=base64.b64encode(tag).decode("utf-8"),
    )


def decrypt_token(encrypted: EncryptedToken) -> str:
    """Decrypts AES-256-GCM ciphertext using Base64 components."""
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    iv = base64.b64decode(encrypted.iv)
    ciphertext = base64.b64decode(encrypted.ciphertext)
    tag = base64.b64decode(encrypted.tag)

    decrypted_bytes = aesgcm.decrypt(iv, ciphertext + tag, None)
    return decrypted_bytes.decode("utf-8")
