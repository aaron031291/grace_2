"""
Create Crypto Key Storage Tables
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.crypto_models import CryptoKeyStore, ComponentCryptoIdentity
from backend.models.base_models import Base, engine


async def create_tables():
    """Create crypto storage tables"""
    
    print("Creating crypto key storage tables...")
    
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Tables created:")
    print("   - crypto_key_store (encrypted private keys)")
    print("   - component_crypto_identities (public key registry)")
    print("\nCrypto storage ready!")


if __name__ == "__main__":
    asyncio.run(create_tables())
