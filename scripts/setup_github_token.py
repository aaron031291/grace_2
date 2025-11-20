"""
GitHub Token Setup Helper
Stores GitHub token in secrets vault securely
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def setup_token():
    print()
    print("=" * 80)
    print("   GitHub Token Setup for Grace")
    print("=" * 80)
    print()
    print("This will store your GitHub token in Grace's encrypted secrets vault.")
    print()
    print("Benefits:")
    print("  ✅ 5000 requests/hour (vs 60 unauthenticated)")
    print("  ✅ Full GitHub API access")
    print("  ✅ No rate limits during learning")
    print()
    
    # Get token from user
    print("Step 1: Get your GitHub Personal Access Token")
    print("  1. Go to: https://github.com/settings/tokens/new")
    print("  2. Token name: 'Grace AI - Local Dev'")
    print("  3. Expiration: 90 days (or your preference)")
    print("  4. Scopes: Select 'public_repo' only")
    print("  5. Click 'Generate token'")
    print("  6. Copy the token (starts with 'ghp_')")
    print()
    
    token = input("Paste your GitHub token here (or press Enter to skip): ").strip()
    
    if not token:
        print("\nNo token provided. Exiting.")
        return
    
    # Validate token format
    if not token.startswith('ghp_'):
        print()
        print("⚠️  Warning: Token doesn't start with 'ghp_'")
        print("   Make sure you copied the entire token")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            return
    
    print()
    print("Step 2: Choose storage method")
    print()
    print("Option 1: Secrets Vault (Recommended - encrypted)")
    print("Option 2: .env file (Simple - plaintext)")
    print()
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        # Store in vault
        print()
        print("Storing in encrypted vault...")
        
        try:
            from backend.security.secrets_vault import secrets_vault
            
            await secrets_vault.store_secret(
                secret_key='GITHUB_TOKEN',
                secret_value=token,
                secret_type='token',
                owner='system',
                service='github',
                description='GitHub Personal Access Token for API access',
                rotation_days=90
            )
            
            print("✅ Token stored in vault successfully!")
            print()
            print("The token is encrypted and will be automatically loaded on startup.")
            
        except Exception as e:
            print(f"❌ Failed to store in vault: {e}")
            print()
            print("Fallback: You can manually add to .env file:")
            print(f"  GITHUB_TOKEN={token}")
            return
            
    elif choice == "2":
        # .env file
        print()
        print("To add to .env file:")
        print()
        print("1. Open: c:/Users/aaron/grace_2/.env")
        print("2. Find the line: GITHUB_TOKEN=your_github_token_here")
        print(f"3. Replace with: GITHUB_TOKEN={token}")
        print("4. Save the file")
        print()
        print("⚠️  Remember: .env file is plaintext - vault is more secure")
        
    else:
        print("Invalid choice. Setup cancelled.")
        return
    
    print()
    print("=" * 80)
    print("Setup Complete!")
    print("=" * 80)
    print()
    print("Next step: Restart Grace")
    print("  python server.py")
    print()
    print("You should see:")
    print("  [GITHUB-MINER] ✅ GitHub token loaded successfully")
    print("  [GITHUB-MINER] 📊 Rate Limit: 5000/5000 requests remaining")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(setup_token())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
