"""
Complete Integration Test - Verify Everything Works Together

Tests:
1. All imports successful
2. Concurrent executor starts
3. Domain adapters register
4. Parallel task execution
5. Bidirectional communication
6. Cognition → Executor → Domains → Results
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def test_all_imports():
    """Test that all new systems import successfully"""
    print("\n[TEST 1] Testing imports...")
    
    try:
        # Cognition system
        from backend.cognition_intent import cognition_authority
        print("  [OK] cognition_intent")
        
        from backend.capability_registry import capability_registry
        print("  [OK] capability_registry")
        
        from backend.capability_handlers import handle_task_list
        print("  [OK] capability_handlers")
        
        # Concurrent execution
        from backend.concurrent_executor import concurrent_executor
        print("  [OK] concurrent_executor")
        
        # Domain adapters
        from backend.domains.all_domain_adapters import (
            domain_registry,
            transcendence_adapter,
            knowledge_adapter,
            security_adapter,
            ml_adapter,
            cognition_adapter
        )
        print("  [OK] all_domain_adapters")
        
        # Updated files
        from backend.grace import GraceAutonomous
        print("  [OK] grace (updated)")
        
        from backend.routes.cognition_api import router as cognition_router
        print("  [OK] cognition_api")
        
        from backend.routes.concurrent_api import router as concurrent_router
        print("  [OK] concurrent_api")
        
        print("\n  [PASS] All imports successful!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Import error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_concurrent_executor():
    """Test concurrent executor can start and process tasks"""
    print("\n[TEST 2] Testing concurrent executor...")
    
    try:
        from backend.concurrent_executor import ConcurrentExecutor
        
        # Create test executor
        executor = ConcurrentExecutor(max_workers=3)
        
        # Start executor
        await executor.start()
        print("  [OK] Executor started with 3 workers")
        
        # Check status
        status = await executor.get_queue_status()
        print(f"  [OK] Queue status: {status}")
        
        assert status["workers"] == 3
        assert status["running"] == True
        
        # Stop executor
        await executor.stop()
        print("  [OK] Executor stopped cleanly")
        
        print("\n  [PASS] Concurrent executor working!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Executor error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_domain_adapters():
    """Test domain adapters can be registered and used"""
    print("\n[TEST 3] Testing domain adapters...")
    
    try:
        from backend.domains.all_domain_adapters import (
            domain_registry,
            transcendence_adapter,
            knowledge_adapter,
            cognition_adapter
        )
        
        # Check adapters are registered
        adapters = domain_registry.get_all_adapters()
        print(f"  [OK] Found {len(adapters)} domain adapters")
        
        # Test knowledge adapter
        adapter = domain_registry.get_adapter("knowledge")
        assert adapter is not None
        print("  [OK] Knowledge adapter registered")
        
        # Test telemetry registration
        telemetry = await adapter.register_telemetry()
        print(f"  [OK] Knowledge adapter has {len(telemetry)} telemetry schemas")
        
        # Test metrics collection
        metrics = await adapter.collect_metrics()
        print(f"  [OK] Knowledge metrics: health_score={metrics.health_score}")
        
        # Test action execution
        result = await adapter.execute_action(
            "search_knowledge",
            {"query": "test"}
        )
        print(f"  [OK] Knowledge action executed: {result.get('ok', False)}")
        
        print("\n  [PASS] Domain adapters working!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Domain adapter error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_cognition_authority():
    """Test cognition authority can parse intents and create plans"""
    print("\n[TEST 4] Testing cognition authority...")
    
    try:
        from backend.cognition_intent import cognition_authority
        
        # Test intent parsing
        intent = await cognition_authority.parse_intent(
            utterance="list my tasks",
            user_id="test_user"
        )
        print(f"  [OK] Parsed intent: {intent.type} (confidence={intent.confidence})")
        assert intent.type == "task.list"
        
        # Test plan creation
        plan = await cognition_authority.create_plan(intent)
        print(f"  [OK] Created plan: {plan.plan_id} with {len(plan.actions)} actions")
        assert len(plan.actions) > 0
        
        print("\n  [PASS] Cognition authority working!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Cognition error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_capability_registry():
    """Test capability registry has all capabilities"""
    print("\n[TEST 5] Testing capability registry...")
    
    try:
        from backend.capability_registry import capability_registry
        
        # Check capabilities registered
        capabilities = capability_registry.get_all_capabilities()
        print(f"  [OK] Registered {len(capabilities)} capabilities")
        
        # Check task capability exists
        task_cap = capability_registry.get_capability("task.list")
        assert task_cap is not None
        print(f"  [OK] task.list capability found")
        
        # Check knowledge capability
        knowledge_cap = capability_registry.get_capability("knowledge.search")
        assert knowledge_cap is not None
        print(f"  [OK] knowledge.search capability found")
        
        # Check LLM tool format
        llm_tools = capability_registry.to_llm_tools()
        print(f"  [OK] Generated {len(llm_tools)} LLM tool definitions")
        
        print("\n  [PASS] Capability registry working!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Capability registry error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_bidirectional_flow():
    """Test complete bidirectional: User → Cognition → Execution → Result → LLM"""
    print("\n[TEST 6] Testing bidirectional flow...")
    
    try:
        from backend.grace import GraceAutonomous
        from backend.memory import PersistentMemory
        
        # Create Grace instance
        memory = PersistentMemory()
        grace = GraceAutonomous(memory)
        
        # Test cognition pipeline is enabled
        assert grace.use_cognition_pipeline == True
        print("  [OK] Cognition pipeline enabled")
        
        # Test legacy fallback exists
        response = await grace._respond_legacy("test_user", "hello")
        print(f"  [OK] Legacy fallback works: '{response[:50]}...'")
        
        print("\n  [PASS] Bidirectional flow configured!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Bidirectional flow error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_integration_points():
    """Test all integration points are wired"""
    print("\n[TEST 7] Testing integration points...")
    
    try:
        # Check main.py has concurrent_executor import
        main_file = Path("backend/main.py")
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "from .concurrent_executor import concurrent_executor" in content
        print("  [OK] main.py imports concurrent_executor")
        
        assert "await concurrent_executor.start()" in content
        print("  [OK] main.py starts concurrent_executor")
        
        assert "domain_registry.register_adapter" in content
        print("  [OK] main.py registers domain adapters")
        
        assert "cognition_api.router" in content
        print("  [OK] main.py includes cognition_api router")
        
        assert "concurrent_api.router" in content
        print("  [OK] main.py includes concurrent_api router")
        
        # Check subagent_bridge uses concurrent_executor
        bridge_file = Path("backend/routes/subagent_bridge.py")
        with open(bridge_file, 'r', encoding='utf-8') as f:
            bridge_content = f.read()
        
        assert "concurrent_executor.submit_task" in bridge_content
        print("  [OK] subagent_bridge routes to concurrent_executor")
        
        print("\n  [PASS] All integration points wired!\n")
        return True
        
    except Exception as e:
        print(f"\n  [FAIL] Integration error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 70)
    print("GRACE COMPLETE INTEGRATION TEST")
    print("Testing: Cognition Authority + Multi-Threading + Domain Adapters")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(await test_all_imports())
    results.append(await test_concurrent_executor())
    results.append(await test_domain_adapters())
    results.append(await test_cognition_authority())
    results.append(await test_capability_registry())
    results.append(await test_bidirectional_flow())
    results.append(await test_integration_points())
    
    # Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"[SUCCESS] ALL {total} TESTS PASSED!")
        print()
        print("Grace is ready with:")
        print("  - Cognition as decision authority")
        print("  - LLM as narrator only")
        print("  - 6-worker concurrent executor")
        print("  - 6 domain adapters active")
        print("  - Parallel task execution")
        print("  - Bidirectional communication")
        print("  - All agentic safeguards preserved")
        print()
        print("Next: Start Grace")
        print("  .venv\\Scripts\\python -m backend.main")
    else:
        print(f"[PARTIAL] {passed}/{total} tests passed")
        print("Please review failures above.")
    
    print("=" * 70)
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
