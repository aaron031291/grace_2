
import os
from cryptography.fernet import Fernet
from pathlib import Path

# 1. Generate Vault Key
key = Fernet.generate_key().decode()
print(f"Generated GRACE_VAULT_KEY: {key}")

# 2. Get OpenAI Key (from SETUP_OPENAI_KEY.md or hardcoded fallback)
OPENAI_KEY = "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"

# 3. Update .env
env_path = Path("c:/Users/aaron/grace_2/.env")
if not env_path.exists():
    print(".env not found, creating from .env.example")
    example_path = Path("c:/Users/aaron/grace_2/.env.example")
    if example_path.exists():
        content = example_path.read_text(encoding='utf-8')
    else:
        content = ""
else:
    content = env_path.read_text(encoding='utf-8')

lines = content.splitlines()
new_lines = []
keys_updated = set()

for line in lines:
    if line.strip().startswith("GRACE_VAULT_KEY="):
        new_lines.append(f"GRACE_VAULT_KEY={key}")
        keys_updated.add("GRACE_VAULT_KEY")
    elif line.strip().startswith("OPENAI_API_KEY="):
        new_lines.append(f"OPENAI_API_KEY={OPENAI_KEY}")
        keys_updated.add("OPENAI_API_KEY")
    elif line.strip().startswith("# GRACE_VAULT_KEY="):
         new_lines.append(f"GRACE_VAULT_KEY={key}")
         keys_updated.add("GRACE_VAULT_KEY")
    else:
        new_lines.append(line)

if "GRACE_VAULT_KEY" not in keys_updated:
    new_lines.append(f"\nGRACE_VAULT_KEY={key}")

if "OPENAI_API_KEY" not in keys_updated:
    new_lines.append(f"OPENAI_API_KEY={OPENAI_KEY}")
    
if "OPENAI_MODEL" not in content:
    new_lines.append("OPENAI_MODEL=gpt-4o")

env_path.write_text("\n".join(new_lines), encoding='utf-8')
print(f"Updated .env with keys")
