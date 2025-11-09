"""Test GitHub token handling and rate limit checking"""

import asyncio
import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_github_token_loading():
    """Test GitHub token loading from different sources"""
    
    print("=" * 70)
    print("Testing GitHub Token Loading & Secrets Vault Integration")
    print("=" * 70)
    print()
    
    # Check environment variables
    print("📋 Environment Check:")
    print(f"  GITHUB_TOKEN: {'✅ Set' if os.getenv('GITHUB_TOKEN') else '❌ Not set'}")
    print(f"  GRACE_VAULT_KEY: {'✅ Set' if os.getenv('GRACE_VAULT_KEY') else '❌ Not set'}")
    print()
    
    # Test secrets vault
    print("🔐 Testing Secrets Vault:")
    try:
        from backend.secrets_vault import secrets_vault
        
        # Try to get GitHub token
        token = await secrets_vault.get_secret('GITHUB_TOKEN', 'test')
        
        if token:
            # Mask token for display
            masked = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
            print(f"  ✅ GitHub token loaded: {masked}")
            print(f"  📏 Token length: {len(token)} characters")
        else:
            print("  ⚠️  No GitHub token found in vault or environment")
            print("  💡 Add GITHUB_TOKEN=<token> to .env file")
    except Exception as e:
        print(f"  ❌ Error loading from vault: {e}")
    print()
    
    # Test GitHub miner initialization
    print("🐙 Testing GitHub Knowledge Miner:")
    try:
        from backend.github_knowledge_miner import GitHubKnowledgeMiner
        
        miner = GitHubKnowledgeMiner()
        await miner.start()
        
        # Check if token was loaded
        if miner.github_token:
            print(f"  ✅ Miner initialized with token")
        else:
            print(f"  ⚠️  Miner initialized WITHOUT token (anonymous mode)")
        
        print()
        print("📊 Rate Limit Status:")
        print("  (See log output above)")
        
        await miner.stop()
        
    except Exception as e:
        print(f"  ❌ Error initializing miner: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)
    print()
    print("📝 Summary:")
    print("  1. If no token: You'll see warnings about rate limits (60/hour)")
    print("  2. With token: You get 5000/hour and authenticated access")
    print("  3. Add GITHUB_TOKEN to .env or secrets vault to enable")
    print()

if __name__ == "__main__":
    # Load .env if present
    try:
        from dotenv import load_dotenv
        if Path(".env").exists():
            load_dotenv()
            print("✅ Loaded .env file\n")
        else:
            print("ℹ️  No .env file found (using environment variables only)\n")
    except ImportError:
        print("ℹ️  python-dotenv not installed (using environment variables only)\n")
    
    asyncio.run(test_github_token_loading())
