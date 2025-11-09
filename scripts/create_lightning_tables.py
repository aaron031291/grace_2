"""Create Lightning and Fusion Memory tables"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.base_models import Base, engine
from backend.lightning_fusion_models import (
    CryptoIdentity,
    FusionMemoryFragment,
    LightningMemoryCache,
    ComponentCryptoRegistration,
    DiagnosticTrace,
    VerificationAuditLog
)


async def create_tables():
    """Create all Lightning and Fusion memory tables"""
    
    print("Creating Lightning and Fusion Memory tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Tables created:")
    print("  - crypto_identities")
    print("  - fusion_memory_fragments")
    print("  - lightning_memory_cache")
    print("  - component_crypto_registry")
    print("  - diagnostic_traces")
    print("  - verification_audit_log")


if __name__ == "__main__":
    asyncio.run(create_tables())
