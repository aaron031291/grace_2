
import sys
import os
import subprocess
import asyncio
import importlib
import pkgutil
from pathlib import Path

# Add root to path
sys.path.insert(0, os.getcwd())

print("="*60)
print("GRACE HEALTH DIAGNOSTICS")
print("="*60)

def check_imports():
    print("\n[1] IMPORT CHECK (Critical Modules)")
    modules = [
        "backend.main",
        "backend.core.guardian",
        "backend.core.healing_orchestrator",
        "backend.grace_agent",
        "backend.memory.memory_catalog",
        "backend.memory_services.memory"
    ]
    
    failed = []
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"  [OK] {mod}")
        except ImportError as e:
            print(f"  [FAIL] {mod}: {e}")
            failed.append(mod)
        except Exception as e:
            print(f"  [FAIL] {mod}: {e}")
            failed.append(mod)
            
    return len(failed) == 0

def check_pytest_collection():
    print("\n[2] PYTEST COLLECTION (Syntax Check)")
    try:
        # Run pytest --collect-only to check for syntax errors in tests
        result = subprocess.run(
            ["pytest", "--collect-only", "-q"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  [OK] Test collection passed")
            return True
        else:
            print("  [FAIL] Test collection failed")
            print("  " + "\n  ".join(result.stderr.splitlines()[:5]))
            return False
    except Exception as e:
        print(f"  [FAIL] Pytest check failed: {e}")
        return False

def check_network_ports():
    print("\n[3] NETWORK PORTS")
    # Check if port 8000 is responding (if server is running)
    import socket
    
    port = int(os.getenv("GRACE_PORT", "8000"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"  [OK] Port {port} is OPEN (Grace Backend)")
    else:
        print(f"  [WARN] Port {port} is CLOSED (Backend might be down)")
        # This isn't necessarily a failure of the diagnostic script, just a status
    return True

def check_secrets():
    print("\n[4] SECRETS CHECK")
    required = ["OPENAI_API_KEY", "GRACE_VAULT_KEY"]
    
    missing = []
    from dotenv import load_dotenv
    load_dotenv()
    
    for key in required:
        val = os.getenv(key)
        if val and not val.startswith("your-") and not val.startswith("change-me"):
            print(f"  [OK] {key} configured")
        else:
            print(f"  [WARN] {key} missing or default")
            missing.append(key)
            
    return len(missing) == 0

def main():
    imports_ok = check_imports()
    pytest_ok = check_pytest_collection()
    network_ok = check_network_ports()
    secrets_ok = check_secrets()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Pytest:  {'PASS' if pytest_ok else 'FAIL'}")
    print(f"Secrets: {'PASS' if secrets_ok else 'WARN'}")
    print("="*60)
    
    if imports_ok and pytest_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
