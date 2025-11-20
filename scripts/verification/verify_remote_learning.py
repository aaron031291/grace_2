
import sys
import os
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(os.getcwd())))

from backend.routes.remote_access_api import WHITELISTED_DOMAINS, is_whitelisted
from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
from backend.learning_systems.governed_web_learning import domain_whitelist, learning_job_orchestrator

print("="*60)
print("REMOTE ACCESS & LEARNING LOOP VERIFICATION")
print("="*60)

# 1. Verify Whitelist
print(f"\n[1] Checking Whitelist Configuration:")
print(f"  - Whitelisted Domains in Remote Access: {len(WHITELISTED_DOMAINS)}")
print(f"  - Example Allowed: {WHITELISTED_DOMAINS[:5]}")

# 2. Verify Gate Logic
print(f"\n[2] Verifying Zero-Trust Gate Logic:")
test_commands = [
    "git clone https://github.com/example/repo",
    "curl https://stackoverflow.com/questions/123",
    "wget https://malicious-site.com/script.sh",
    "python script.py" # Local command
]

for cmd in test_commands:
    allowed = is_whitelisted(cmd)
    status = "ALLOWED" if allowed else "BLOCKED"
    print(f"  - Command: '{cmd}' -> {status}")

# 3. Verify Learning Manager Integration
print(f"\n[3] Verifying Learning Whitelist Manager:")
print(f"  - Loaded Domains: {len(learning_whitelist_manager.whitelist.get('domains', {}))}")
next_topic = learning_whitelist_manager.get_next_topic()
print(f"  - Next Learning Topic: {next_topic['domain'] if next_topic else 'None'}")

# 4. Verify Governed Web Learning
print(f"\n[4] Verifying Governed Web Learning:")
print(f"  - Trusted Domains: {len(domain_whitelist.whitelist)}")
url = "https://github.com/grace/docs"
allowed, reason, entry = domain_whitelist.check_domain_access(url)
print(f"  - Access Check '{url}': {'ALLOWED' if allowed else 'DENIED'} ({reason or 'OK'})")

print(f"\n[5] Verification Conclusion:")
if len(WHITELISTED_DOMAINS) > 0 and is_whitelisted("git clone https://github.com"):
    print("  [OK] Remote Access is connected to Whitelist")
else:
    print("  [FAIL] Remote Access Whitelist disconnected")

if learning_whitelist_manager.whitelist:
    print("  [OK] Learning Loop is connected to Curriculum")
else:
    print("  [FAIL] Learning Loop Curriculum missing")

print("="*60)
