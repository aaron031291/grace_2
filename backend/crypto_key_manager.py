"""
Compatibility wrapper for backend.crypto_key_manager
Re-exports from backend.crypto.crypto_key_manager
"""

from backend.crypto.crypto_key_manager import (
    CryptoKey,
    SignedMessage,
    CryptoKeyManager,
    crypto_key_manager,
)

__all__ = [
    'CryptoKey',
    'SignedMessage',
    'CryptoKeyManager',
    'crypto_key_manager',
]
