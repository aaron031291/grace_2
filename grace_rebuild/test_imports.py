"""Quick import test to verify core components load"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing core imports...")

try:
    print("1. Importing metrics_service...", end=" ")
    from backend.metrics_service import get_metrics_collector, publish_metric
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("2. Importing cognition_metrics...", end=" ")
    from backend.cognition_metrics import get_metrics_engine
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("3. Testing metrics collector...", end=" ")
    collector = get_metrics_collector()
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("4. Testing cognition engine...", end=" ")
    engine = get_metrics_engine()
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("5. Testing metric publish...", end=" ")
    import asyncio
    asyncio.run(publish_metric("test", "test_kpi", 0.95))
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("6. Testing status generation...", end=" ")
    status = engine.get_status()
    assert "domains" in status
    assert "overall_health" in status
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

print("\n✅ All imports working!")
print("\nNext: Start backend with START_GRACE.bat")
