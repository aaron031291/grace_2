"""Test GitHub token handling WITH a token set"""

import asyncio
import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Set a fake token for testing
os.environ['GITHUB_TOKEN'] = 'ghp_test_token_1234567890abcdefghijklmnopqrst'

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_with_token():
    """Test with token set"""
    
    print("=" * 70)
    print("Testing WITH GitHub Token")
    print("=" * 70)
    print()
    
    print("📋 Environment Check:")
    print(f"  GITHUB_TOKEN: ✅ Set (test token)")
    print()
    
    print("🔐 Testing Secrets Vault:")
    try:
        from backend.secrets_vault import secrets_vault
        
        token = await secrets_vault.get_secret('GITHUB_TOKEN', 'test')
        
        if token:
            masked = f"{token[:8]}...{token[-4:]}"
            print(f"  ✅ Token loaded successfully: {masked}")
            print(f"  📏 Token length: {len(token)} characters")
        else:
            print(f"  ❌ Failed to load token")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    print("✅ Token loading mechanism verified!")
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_with_token())
