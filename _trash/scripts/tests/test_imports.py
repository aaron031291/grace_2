
import sys
import os
sys.path.append(os.getcwd())

print("Testing imports...")

try:
    from backend.grace import GraceAutonomous
    print("[OK] GraceAutonomous imported successfully")
except ImportError as e:
    print(f"[FAIL] GraceAutonomous failed: {e}")

try:
    from backend.memory import MemoryAsset
    print("[OK] MemoryAsset imported successfully")
except ImportError as e:
    print(f"[FAIL] MemoryAsset failed: {e}")

try:
    from backend.memory import PersistentMemory
    print("[OK] PersistentMemory imported successfully")
except ImportError as e:
    print(f"[FAIL] PersistentMemory failed: {e}")
