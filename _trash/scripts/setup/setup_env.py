#!/usr/bin/env python3
"""
Quick environment setup - Generates secure SECRET_KEY
"""

import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)

def setup_env():
    """Setup .env file with secure values"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_example.exists():
        print("✗ .env.example not found")
        return False
    
    # Read example
    content = env_example.read_text()
    
    # Generate secure secret key
    secret_key = generate_secret_key()
    
    # Replace placeholder
    content = content.replace("SECRET_KEY=change-me", f"SECRET_KEY={secret_key}")
    
    # Set default database URL if not set
    if "# DATABASE_URL=sqlite+aiosqlite" in content:
        content = content.replace(
            "# DATABASE_URL=sqlite+aiosqlite:///./grace.db",
            "DATABASE_URL=sqlite+aiosqlite:///./backend/grace.db"
        )
    
    # Write to .env
    env_file.write_text(content)
    
    print("[OK] .env file configured")
    print(f"[OK] SECRET_KEY generated: {secret_key[:10]}...")
    print("[OK] DATABASE_URL set to SQLite")
    print()
    print("Environment ready! Start backend with:")
    print("  uvicorn backend.main:app --reload")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  Grace Environment Setup")
    print("=" * 50)
    print()
    
    if setup_env():
        print()
        print("[OK] Setup complete!")
    else:
        print()
        print("[ERROR] Setup failed")
