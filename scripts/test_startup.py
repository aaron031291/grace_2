"""
Quick startup test - Verify all critical imports work
Run before starting server.py to catch import errors early
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing Grace startup components...")
print()

errors = []
successes = []

# Test 1: Core imports
print("[1/10] Testing core imports...")
try:
    from backend.core.message_bus import message_bus
    from backend.core.immutable_log import immutable_log
    from backend.core.guardian import guardian
    successes.append("Core imports")
    print("  ✅ Core imports")
except Exception as e:
    errors.append(f"Core imports: {e}")
    print(f"  ❌ Core imports: {e}")

# Test 2: Orchestrator imports
print("[2/10] Testing orchestrators...")
try:
    from backend.orchestrators.web_learning_orchestrator import web_learning_orchestrator
    successes.append("Web learning orchestrator")
    print("  ✅ Web learning orchestrator")
except Exception as e:
    errors.append(f"Web learning orchestrator: {e}")
    print(f"  ❌ Web learning orchestrator: {e}")

# Test 3: Knowledge system
print("[3/10] Testing knowledge system...")
try:
    from backend.knowledge.github_knowledge_miner import github_miner
    from backend.knowledge.knowledge_gap_detector import knowledge_gap_detector
    successes.append("Knowledge system")
    print("  ✅ Knowledge system")
except Exception as e:
    errors.append(f"Knowledge system: {e}")
    print(f"  ❌ Knowledge system: {e}")

# Test 4: Optional modules (should have stubs)
print("[4/10] Testing optional modules...")
try:
    from backend.agents.creative_problem_solver import creative_problem_solver
    from backend.agents.competitor_tracker import competitor_tracker
    from backend.agents.future_projects_learner import future_projects_learner
    successes.append("Optional modules")
    print("  ✅ Optional modules (stubs)")
except Exception as e:
    errors.append(f"Optional modules: {e}")
    print(f"  ❌ Optional modules: {e}")

# Test 5: Task registry
print("[5/10] Testing task registry...")
try:
    from backend.services.task_registry import task_registry
    from backend.models.task_registry_models import TaskRegistryEntry
    from backend.utilities.task_reporter import TaskReporter
    successes.append("Task registry")
    print("  ✅ Task registry")
except Exception as e:
    errors.append(f"Task registry: {e}")
    print(f"  ❌ Task registry: {e}")

# Test 6: Healing orchestrator
print("[6/10] Testing healing orchestrator...")
try:
    from backend.core.healing_orchestrator import healing_orchestrator
    successes.append("Healing orchestrator")
    print("  ✅ Healing orchestrator")
except Exception as e:
    errors.append(f"Healing orchestrator: {e}")
    print(f"  ❌ Healing orchestrator: {e}")

# Test 7: Vector store
print("[7/10] Testing vector store...")
try:
    from backend.services.vector_store import VectorStoreBackend
    successes.append("Vector store")
    print("  ✅ Vector store")
except Exception as e:
    errors.append(f"Vector store: {e}")
    print(f"  ❌ Vector store: {e}")

# Test 8: Port management
print("[8/10] Testing port management...")
try:
    from backend.core.port_manager import port_manager
    from backend.core.port_watchdog import port_watchdog
    successes.append("Port management")
    print("  ✅ Port management")
except Exception as e:
    errors.append(f"Port management: {e}")
    print(f"  ❌ Port management: {e}")

# Test 9: Snapshot manager
print("[9/10] Testing snapshot manager...")
try:
    from backend.boot.snapshot_manager import boot_snapshot_manager
    successes.append("Snapshot manager")
    print("  ✅ Snapshot manager")
except Exception as e:
    errors.append(f"Snapshot manager: {e}")
    print(f"  ❌ Snapshot manager: {e}")

# Test 10: API routes
print("[10/10] Testing API routes...")
try:
    from backend.routes.task_registry_api import router as task_registry_router
    from backend.main import app
    successes.append("API routes")
    print("  ✅ API routes")
except Exception as e:
    errors.append(f"API routes: {e}")
    print(f"  ❌ API routes: {e}")

# Summary
print()
print("=" * 80)
print("STARTUP TEST RESULTS")
print("=" * 80)
print()
print(f"✅ Passed: {len(successes)}/10")
print(f"❌ Failed: {len(errors)}/10")
print()

if errors:
    print("ERRORS:")
    for error in errors:
        print(f"  • {error}")
    print()
    print("⚠️  Fix these errors before starting server.py")
    sys.exit(1)
else:
    print("🎉 All tests passed! Ready to start Grace.")
    print()
    print("Run: python server.py")
    print()
    sys.exit(0)
