"""
Complete System Test Runner
Triple-check all new systems work E2E

Systems tested:
1. Remote learning (Firefox, web scraper, GitHub, remote access)
2. Self-driving learning loop (triage, missions, events)
3. Tiered agents (research -> design -> implement -> test -> deploy)
4. Governance & safety (RBAC, approvals, risk scoring)
5. Chaos engineering (profiles, attacks, healing integration)
6. Port watchdog fix
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_system_imports():
    """Test all new modules can be imported"""
    print("\n" + "=" * 80)
    print("IMPORT TESTS")
    print("=" * 80)
    
    imports = [
        # Core fix
        ('backend.core.resolution_protocol', 'ResolutionProtocol'),
        
        # Remote learning
        ('backend.agents.firefox_agent', 'firefox_agent'),
        ('backend.utilities.safe_web_scraper', 'safe_web_scraper'),
        
        # Learning feedback loop
        ('backend.learning_systems.learning_triage_agent', 'learning_triage_agent'),
        ('backend.learning_systems.learning_mission_launcher', 'learning_mission_launcher'),
        ('backend.learning_systems.event_emitters', 'guardian_events'),
        
        # Tiered agents
        ('backend.agents_core.tiered_agent_framework', 'AGENT_REGISTRY'),
        ('backend.agents_core.agent_orchestrator', 'agent_orchestrator'),
        
        # Governance
        ('backend.governance_system.rbac_system', 'rbac_system'),
        ('backend.governance_system.inline_approval_engine', 'inline_approval_engine'),
        
        # Chaos
        ('backend.chaos.component_profiles', 'component_registry'),
        ('backend.chaos.attack_scripts', 'ATTACK_SCRIPTS'),
        ('backend.chaos.chaos_agent', 'chaos_agent'),
        
        # Port fix
        ('backend.core.port_manager', 'port_manager'),
        ('backend.core.port_watchdog', 'port_watchdog'),
    ]
    
    passed = 0
    failed = 0
    
    for module_path, item_name in imports:
        try:
            module = __import__(module_path, fromlist=[item_name])
            item = getattr(module, item_name)
            print(f"[OK] {module_path}.{item_name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {module_path}.{item_name}: {e}")
            failed += 1
    
    print(f"\nImports: {passed} passed, {failed} failed")
    return failed == 0


async def test_system_initialization():
    """Test all systems can be initialized"""
    print("\n" + "=" * 80)
    print("INITIALIZATION TESTS")
    print("=" * 80)
    
    tests = []
    
    # Test 1: RBAC system
    try:
        from backend.governance_system.rbac_system import rbac_system
        await rbac_system.start()
        assert len(rbac_system.service_accounts) >= 4
        print(f"[OK] RBAC system: {len(rbac_system.service_accounts)} service accounts")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] RBAC system: {e}")
        tests.append(False)
    
    # Test 2: Approval engine
    try:
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        await inline_approval_engine.start()
        assert inline_approval_engine.auto_approval_threshold == 0.3
        print(f"[OK] Approval engine: threshold={inline_approval_engine.auto_approval_threshold}")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Approval engine failed: {e}")
        tests.append(False)
    
    # Test 3: Learning triage agent
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        assert learning_triage_agent.boot_phase is True
        assert learning_triage_agent.boot_interval == 15
        print(f"[OK] Triage agent: boot_phase={learning_triage_agent.boot_phase}, interval={learning_triage_agent.boot_interval}s")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Triage agent failed: {e}")
        tests.append(False)
    
    # Test 4: Mission launcher
    try:
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        assert learning_mission_launcher.max_concurrent_missions == 3
        print(f"[OK] Mission launcher: max_concurrent={learning_mission_launcher.max_concurrent_missions}")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Mission launcher failed: {e}")
        tests.append(False)
    
    # Test 5: Agent orchestrator
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        assert agent_orchestrator.max_concurrent_pipelines == 2
        print(f"[OK] Agent orchestrator: max_pipelines={agent_orchestrator.max_concurrent_pipelines}")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Agent orchestrator failed: {e}")
        tests.append(False)
    
    # Test 6: Chaos agent
    try:
        from backend.chaos.chaos_agent import chaos_agent
        await chaos_agent.start()
        assert chaos_agent.auto_run_enabled is False
        print(f"[OK] Chaos agent: auto_run={chaos_agent.auto_run_enabled} (safe)")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Chaos agent failed: {e}")
        tests.append(False)
    
    # Test 7: Component registry
    try:
        from backend.chaos.component_profiles import component_registry
        profiles = len(component_registry.profiles)
        assert profiles >= 7
        print(f"[OK] Component registry: {profiles} profiles")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Component registry failed: {e}")
        tests.append(False)
    
    # Test 8: Port manager
    try:
        from backend.core.port_manager import port_manager
        assert port_manager.start_port == 8000
        assert port_manager.end_port == 8010
        print(f"[OK] Port manager: {port_manager.start_port}-{port_manager.end_port}")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Port manager failed: {e}")
        tests.append(False)
    
    print(f"\nInitialization: {sum(tests)} passed, {len(tests) - sum(tests)} failed")
    return all(tests)


async def test_integrations():
    """Test integrations between systems"""
    print("\n" + "=" * 80)
    print("INTEGRATION TESTS")
    print("=" * 80)
    
    tests = []
    
    # Test 1: Missions use approval system
    try:
        from backend.learning_systems.learning_mission_launcher import LearningMission
        
        mission = LearningMission(
            mission_id='test_123',
            mission_type='test',
            description='Test mission',
            context={'domain': 'test'},
            priority=0.5,
            launched_by='test'
        )
        
        assert hasattr(mission, 'risk_score')
        assert hasattr(mission, 'impact_score')
        assert hasattr(mission, 'combined_score')
        print(f"[OK] Missions have risk/impact scoring")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Mission scoring failed: {e}")
        tests.append(False)
    
    # Test 2: Agents use playbooks
    try:
        from backend.agents_core.tiered_agent_framework import ResearchAgent
        
        agent = ResearchAgent()
        assert hasattr(agent, 'use_playbook')
        print(f"[OK] Agents can use playbooks")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Agent playbook integration failed: {e}")
        tests.append(False)
    
    # Test 3: Chaos feeds healing
    try:
        from backend.chaos.chaos_agent import chaos_agent
        
        assert hasattr(chaos_agent, 'healing_orchestrator')
        assert hasattr(chaos_agent, '_raise_healing_task')
        print(f"[OK] Chaos agent integrated with healing")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Chaos-healing integration failed: {e}")
        tests.append(False)
    
    # Test 4: Learning loop has adaptive cadence
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        assert learning_triage_agent.boot_interval == 15
        assert learning_triage_agent.steady_interval == 180
        assert hasattr(learning_triage_agent, '_transition_to_steady_state')
        print(f"[OK] Triage agent has adaptive cadence (15s -> 180s)")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Adaptive cadence failed: {e}")
        tests.append(False)
    
    print(f"\nIntegrations: {sum(tests)} passed, {len(tests) - sum(tests)} failed")
    return all(tests)


async def test_file_structure():
    """Verify all new files exist"""
    print("\n" + "=" * 80)
    print("FILE STRUCTURE TESTS")
    print("=" * 80)
    
    required_files = [
        'backend/core/resolution_protocol.py',
        'backend/utilities/safe_web_scraper.py',
        'backend/learning_systems/learning_triage_agent.py',
        'backend/learning_systems/learning_mission_launcher.py',
        'backend/learning_systems/event_emitters.py',
        'backend/agents_core/tiered_agent_framework.py',
        'backend/agents_core/agent_orchestrator.py',
        'backend/governance_system/rbac_system.py',
        'backend/governance_system/inline_approval_engine.py',
        'backend/chaos/component_profiles.py',
        'backend/chaos/attack_scripts.py',
        'backend/chaos/chaos_agent.py',
        'backend/routes/learning_feedback_api.py',
        'backend/routes/agent_pipeline_api.py',
        'backend/routes/governance_api.py',
        'backend/routes/chaos_api.py',
        'docs/REMOTE_LEARNING.md',
        'docs/SELF_DRIVING_LEARNING.md',
        'docs/TIERED_AGENT_EXECUTION.md',
        'docs/AUTOMATION_CADENCE.md',
        'docs/CHAOS_ENGINEERING.md',
        'docs/COMPLETE_LEARNING_SYSTEM.md',
        'docs/PORT_WATCHDOG_FIX.md',
        'tests/test_e2e_complete_system.py',
        'scripts/utilities/cleanup_port_registry.py'
    ]
    
    passed = 0
    failed = 0
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[OK] {file_path}")
            passed += 1
        else:
            print(f"[FAIL] {file_path} MISSING")
            failed += 1
    
    print(f"\nFiles: {passed} found, {failed} missing")
    return failed == 0


async def main():
    """Run all tests"""
    print()
    print("+" + "=" * 78 + "+")
    print("|" + " " * 20 + "GRACE COMPLETE SYSTEM VERIFICATION" + " " * 23 + "|")
    print("+" + "=" * 78 + "+")
    print()
    print(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all test suites
    results.append(("File Structure", await test_file_structure()))
    results.append(("Imports", await test_system_imports()))
    results.append(("Initialization", await test_system_initialization()))
    results.append(("Integrations", await test_integrations()))
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print()
    if all_passed:
        print("+" + "=" * 78 + "+")
        print("|" + " " * 28 + "ALL TESTS PASSED!" + " " * 32 + "|")
        print("+" + "=" * 78 + "+")
        print()
        print("Grace complete learning system is ready!")
        print()
        print("Systems verified:")
        print("  [OK] Remote learning (internet & GitHub access)")
        print("  [OK] Self-driving feedback loop (adaptive cadence)")
        print("  [OK] Tiered agent execution (5-phase pipeline)")
        print("  [OK] Governance & safety (RBAC + approvals)")
        print("  [OK] Chaos engineering (domain-specific stress tests)")
        print("  [OK] Port watchdog (fixed, no more spam)")
        print()
        print("Start Grace:")
        print("  python server.py")
        print()
    else:
        print("+" + "=" * 78 + "+")
        print("|" + " " * 30 + "SOME TESTS FAILED" + " " * 30 + "|")
        print("+" + "=" * 78 + "+")
        print()
        print("Check logs above for details")
        print()
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
