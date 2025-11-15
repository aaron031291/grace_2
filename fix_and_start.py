"""
Fix common issues and start Grace
"""

import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("GRACE - AUTO-FIX AND START")
print("="*70)

# Fix 1: Check Python version
print("\n[Fix 1] Checking Python version...")
if sys.version_info < (3, 11):
    print(f"⚠️ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    print("   Recommended: Python 3.11+")
else:
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")

# Fix 2: Create required directories
print("\n[Fix 2] Creating required directories...")
dirs_to_create = [
    "logs/remote_sessions",
    "databases/remote_access",
    "databases/learning_curriculum",
    "sandbox/learning_projects"
]

for dir_path in dirs_to_create:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    
print(f"✅ Created {len(dirs_to_create)} directories")

# Fix 3: Test imports
print("\n[Fix 3] Testing critical imports...")
errors = []

try:
    from backend.main import app
    print("✅ Main app imports OK")
except Exception as e:
    print(f"❌ Main app failed: {e}")
    errors.append(("Main app", str(e)))

try:
    from backend.remote_access.zero_trust_gate import zero_trust_gate
    print("✅ Remote access imports OK")
except Exception as e:
    print(f"❌ Remote access failed: {e}")
    errors.append(("Remote access", str(e)))

try:
    from backend.learning_systems.autonomous_curriculum import autonomous_curriculum
    print("✅ Learning system imports OK")
except Exception as e:
    print(f"❌ Learning system failed: {e}")
    errors.append(("Learning system", str(e)))

# Fix 4: Check if port 8000 is available
print("\n[Fix 4] Checking port 8000...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('localhost', 8000))
    sock.close()
    print("✅ Port 8000 available")
except OSError:
    print("⚠️ Port 8000 in use - will try to use it anyway")

# Summary
print("\n" + "="*70)
if errors:
    print(f"❌ {len(errors)} ERROR(S) FOUND")
    print("="*70)
    for name, error in errors:
        print(f"\n{name}:")
        print(f"  {error}")
    print("\nFix these errors before starting Grace")
    input("\nPress Enter to exit...")
    sys.exit(1)
else:
    print("✅ ALL CHECKS PASSED - READY TO START")
    print("="*70)
    
    # Start server
    print("\nStarting Grace...")
    import subprocess
    subprocess.run([sys.executable, "serve_fixed.py"])
