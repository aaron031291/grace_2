#!/usr/bin/env python3  
""" >> scripts/setup_vault.py && echo Grace Secrets Vault Setup >> scripts/setup_vault.py && echo Set up required secrets for autonomous learning and research >> scripts/setup_vault.py && echo """  
  
import asyncio  
import os  
import getpass  
from pathlib import Path  
  
async def setup_secrets():  
    print("?? GRACE SECRETS VAULT SETUP")  
    print("=" * 50)  
    print("This will set up secrets needed for Grace's autonomous systems.")  
    print("All secrets are encrypted and stored securely.\n")  
  
    try:  
        from backend.security.secrets_vault import secrets_vault  
        from backend.security.secure_credential_vault import credential_vault  
    except ImportError as e:  
        print(f"? Error importing vault systems: {e}")  
        return  
  
    github_token = getpass.getpass("Enter GitHub token (or press Enter to skip): ").strip()  
    if github_token:  
        try:  
            result = await secrets_vault.store_secret(  
                secret_key="GITHUB_TOKEN",  
                secret_value=github_token,  
                secret_type="token",  
                owner="aaron",  
                service="github",  
                description="GitHub API token for repository mining"  
            )  
            print(f"? GitHub token stored")  
        except Exception as e:  
            print(f"? Failed to store GitHub token: {e}")  
  
    jc_password = getpass.getpass("Enter JournalClub password (or press Enter to skip): ").strip()  
    if jc_password:  
        try:  
            await credential_vault.store_credential(  
                site="journalclub.io",  
                username="aaron@graceai.uk",  
                credential_type="password",  
                credential_value=jc_password,  
                approved_by="aaron"  
            )  
            print("? JournalClub credentials stored")  
        except Exception as e:  
            print(f"? Failed to store JournalClub credentials: {e}")  
  
    print("\n?? SECRETS SETUP COMPLETE")  
    print("Restart Grace backend to load secrets")  
  
if __name__ == "__main__":  
    asyncio.run(setup_secrets()) 
