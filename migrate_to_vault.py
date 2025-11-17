"""
Migrate secrets from .env to encrypted vault
Run this once to move all API keys to secure storage
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load current .env
load_dotenv()

API_BASE = "http://localhost:8017"
AUTH_TOKEN = "dev-token"  # Replace with your actual token

# Secrets to migrate
SECRETS_TO_MIGRATE = [
    {
        "name": "OPENAI_API_KEY",
        "env_var": "OPENAI_API_KEY",
        "type": "api_key",
        "scope": "learning",
        "domain": "ai",
        "tags": ["learning", "rag", "ai"],
        "description": "OpenAI API key for GPT models and embeddings"
    },
    {
        "name": "GITHUB_TOKEN",
        "env_var": "GITHUB_TOKEN",
        "type": "token",
        "scope": "code_knowledge",
        "domain": "code",
        "tags": ["github", "api", "code"],
        "description": "GitHub personal access token for repository access"
    },
    {
        "name": "GOOGLE_SEARCH_KEY",
        "env_var": "GOOGLE_SEARCH_KEY",
        "type": "api_key",
        "scope": "web_search",
        "domain": "search",
        "tags": ["google", "search", "learning"],
        "description": "Google Custom Search API key"
    },
    {
        "name": "DUCKDUCKGO_APP_KEY",
        "env_var": "DUCKDUCKGO_APP_KEY",
        "type": "api_key",
        "scope": "web_search",
        "domain": "search",
        "tags": ["duckduckgo", "search", "learning"],
        "description": "DuckDuckGo search API key"
    },
    {
        "name": "SLACK_TOKEN",
        "env_var": "SLACK_TOKEN",
        "type": "token",
        "scope": "notifications",
        "domain": "notifications",
        "tags": ["slack", "notifications"],
        "description": "Slack bot token for notifications"
    },
    {
        "name": "SALESFORCE_API_KEY",
        "env_var": "SALESFORCE_API_KEY",
        "type": "api_key",
        "scope": "crm_integration",
        "domain": "crm",
        "tags": ["salesforce", "crm"],
        "description": "Salesforce API key for CRM access"
    },
]


async def migrate_secrets():
    """Migrate secrets from .env to vault"""
    
    print("=" * 60)
    print("  Grace Secrets Vault - Migration Tool")
    print("=" * 60)
    print()
    
    # Check vault key is set
    vault_key = os.getenv("GRACE_VAULT_KEY")
    if not vault_key:
        print("⚠️  WARNING: GRACE_VAULT_KEY not set!")
        print("   Secrets will not persist across restarts.")
        print("   Run SETUP_VAULT.bat to generate a key.")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print("✅ GRACE_VAULT_KEY is set")
        print()
    
    migrated = 0
    skipped = 0
    failed = 0
    
    async with httpx.AsyncClient() as client:
        for secret_config in SECRETS_TO_MIGRATE:
            secret_value = os.getenv(secret_config["env_var"])
            
            if not secret_value:
                print(f"⏭️  Skipping {secret_config['name']} - not found in .env")
                skipped += 1
                continue
            
            # Mask the value for display
            masked_value = secret_value[:8] + "..." + secret_value[-4:] if len(secret_value) > 12 else "***"
            print(f"📤 Migrating {secret_config['name']}: {masked_value}")
            
            try:
                response = await client.post(
                    f"{API_BASE}/api/secrets/store",
                    headers={
                        "Authorization": f"Bearer {AUTH_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "name": secret_config["name"],
                        "value": secret_value,
                        "secret_type": secret_config["type"],
                        "scope": secret_config["scope"],
                        "environment": "production",
                        "service_name": secret_config.get("domain", ""),
                        "description": secret_config.get("description", ""),
                        "tags": secret_config.get("tags", []),
                    },
                    timeout=10.0,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Stored as {result.get('secret_id', 'unknown ID')}")
                    migrated += 1
                else:
                    print(f"   ❌ Failed: {response.status_code} - {response.text}")
                    failed += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                failed += 1
            
            print()
    
    print("=" * 60)
    print(f"\n✅ Migration complete!")
    print(f"   Migrated: {migrated}")
    print(f"   Skipped: {skipped}")
    print(f"   Failed: {failed}")
    print()
    
    if migrated > 0:
        print("🎯 Next steps:")
        print("   1. Verify secrets in Grace Console (🔐 Vault panel)")
        print("   2. Update backend services to use vault")
        print("   3. Remove migrated secrets from .env")
        print("   4. Keep GRACE_VAULT_KEY in .env")
        print()
    
    if failed > 0:
        print("⚠️  Some secrets failed to migrate.")
        print("   Check backend is running on", API_BASE)
        print("   Check AUTH_TOKEN is valid")
        print()


if __name__ == "__main__":
    print()
    print("This script will migrate secrets from .env to the encrypted vault.")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(migrate_secrets())
    else:
        print("Migration cancelled.")
