"""Quick import test to verify core components load"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so `import backend.*` works when run from anywhere
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("Testing core imports...")

try:
    print("1. Importing metrics_service...", end=" ")
    from backend.monitoring.metrics_service import get_metrics_collector, publish_metric
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

try:
    print("2. Importing cognition_metrics...", end=" ")
    from backend.misc.cognition_metrics import get_metrics_engine
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

try:
    print("3. Testing metrics collector...", end=" ")
    collector = get_metrics_collector()
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

try:
    print("4. Testing cognition engine...", end=" ")
    engine = get_metrics_engine()
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

try:
    print("5. Testing metric publish...", end=" ")
    import asyncio
    asyncio.run(publish_metric("test", "test_kpi", 0.95))
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

try:
    print("6. Testing status generation...", end=" ")
    status = engine.get_status()
    assert "domains" in status
    assert "overall_health" in status
    print("OK")
except Exception as e:
    print(f"FAIL {e}")
    sys.exit(1)

print("\nAll imports working!")
print("\nNext: Start backend with START_GRACE.bat")
