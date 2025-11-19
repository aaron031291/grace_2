
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("="*60)
print("VERIFYING CORE EXPORTS")
print("="*60)

def verify_import(name, module_path, class_name):
    print(f"Checking {name}...")
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  [OK] Successfully imported {class_name} from {module_path}")
        return True
    except ImportError as e:
        print(f"  [FAIL] ImportError: {e}")
        return False
    except AttributeError as e:
        print(f"  [FAIL] AttributeError: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

success = True

# 1. GraceAutonomous
if not verify_import("GraceAutonomous", "backend.grace_agent", "GraceAutonomous"):
    success = False

# 2. MemoryAsset
if not verify_import("MemoryAsset", "backend.memory.memory_catalog", "MemoryAsset"):
    success = False

# 3. PersistentMemory
if not verify_import("PersistentMemory", "backend.memory_services.memory", "PersistentMemory"):
    success = False

print("-" * 60)
if success:
    print("ALL CORE EXPORTS VERIFIED")
    sys.exit(0)
else:
    print("SOME EXPORTS FAILED")
    sys.exit(1)
