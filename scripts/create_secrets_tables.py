"""Create Secrets Vault Tables"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.secrets_models import SecretVault, SecretAccessLog, ContactRegistry, SecretValidation
from backend.models.base_models import Base, engine


async def create_tables():
    print("Creating secrets vault tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Tables created:")
    print("   - secret_vault (encrypted secrets)")
    print("   - secret_access_log (audit trail)")
    print("   - contact_registry (emails with consent)")
    print("   - secret_validations (test results)")
    print("\nSecrets vault ready!")


if __name__ == "__main__":
    asyncio.run(create_tables())
