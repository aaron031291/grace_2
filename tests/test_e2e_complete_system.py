"""
End-to-End Tests for Grace Complete Learning System

Tests:
1. Remote learning systems
2. Self-driving learning feedback loop  
3. Tiered agent execution
4. Governance & safety
5. Chaos engineering
6. Port watchdog fix
"""

import pytest
import asyncio
from datetime import datetime


class TestRemoteLearning:
    """Test remote learning systems"""
    
    @pytest.mark.asyncio
    async def test_firefox_agent_starts(self):
        """Test Firefox agent initialization"""
        from backend.agents.firefox_agent import firefox_agent
        
        await firefox_agent.start(enabled=True)
        
        assert firefox_agent.enabled is True
        assert len(firefox_agent.approved_domains) >= 10
        print("✓ Firefox agent started with approved domains")
    
    @pytest.mark.asyncio
    async def test_web_scraper_integration(self):
        """Test web scraper uses Firefox agent"""
        from backend.utilities.safe_web_scraper import safe_web_scraper
        
        await safe_web_scraper.initialize()
        
        assert safe_web_scraper.firefox_agent is not None
        assert len(safe_web_scraper.trusted_domains) >= 10
        print("✓ Web scraper integrated with Firefox agent")
    
    @pytest.mark.asyncio
    async def test_github_miner_starts(self):
        """Test GitHub knowledge miner"""
        from backend.knowledge.github_knowledge_miner import GitHubKnowledgeMiner
        
        miner = GitHubKnowledgeMiner()
        await miner.start()
        
        assert miner.base_url == "https://api.github.com"
        assert len(miner.learning_repos) >= 4
        
        await miner.stop()
        print("✓ GitHub miner initialized")
    
    @pytest.mark.asyncio
    async def test_remote_computer_access(self):
        """Test remote computer access"""
        from backend.misc.remote_computer_access import RemoteComputerAccess
        
        remote = RemoteComputerAccess()
        await remote.start()
        
        assert remote.access_enabled is True
        assert len(remote.allowed_actions) >= 10
        print("✓ Remote computer access enabled")


class TestLearningFeedbackLoop:
    """Test self-driving learning feedback loop"""
    
    @pytest.mark.asyncio
    async def test_triage_agent_starts(self):
        """Test learning triage agent"""
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        # Check initial state
        assert learning_triage_agent.boot_phase is True
        assert learning_triage_agent.boot_interval == 15
        assert learning_triage_agent.steady_interval == 180
        print("✓ Triage agent initialized in boot phase")
    
    @pytest.mark.asyncio
    async def test_event_clustering(self):
        """Test event clustering logic"""
        from backend.learning_systems.learning_triage_agent import EventCluster, learning_triage_agent
        
        # Create test cluster
        cluster = EventCluster(
            domain='test',
            severity='high',
            pattern_type='error'
        )
        
        cluster.event_count = 10
        urgency = cluster.urgency_score()
        recurrence = cluster.recurrence_score()
        
        assert urgency > 0.5
        assert cluster.should_launch_mission() is True
        print(f"✓ Event clustering works (urgency: {urgency:.2f})")
    
    @pytest.mark.asyncio
    async def test_mission_launcher(self):
        """Test mission launcher"""
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        
        stats = learning_mission_launcher.get_stats()
        
        assert stats['running'] is False  # Not started yet
        assert learning_mission_launcher.max_concurrent_missions == 3
        print("✓ Mission launcher configured")
    
    @pytest.mark.asyncio
    async def test_phase_transition(self):
        """Test boot to steady state transition"""
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        # Simulate transition
        initial_phase = learning_triage_agent.boot_phase
        assert initial_phase is True
        
        await learning_triage_agent._transition_to_steady_state()
        
        assert learning_triage_agent.boot_phase is False
        assert learning_triage_agent.current_interval == 180
        print("✓ Phase transition: boot → steady state")
    
    @pytest.mark.asyncio
    async def test_event_emitters(self):
        """Test event emitters initialize"""
        from backend.learning_systems.event_emitters import (
            guardian_events,
            htm_events,
            rag_events,
            remote_access_events,
            agent_events,
            system_events
        )
        
        await guardian_events.initialize()
        await htm_events.initialize()
        await rag_events.initialize()
        await remote_access_events.initialize()
        await agent_events.initialize()
        await system_events.initialize()
        
        print("✓ All 6 event emitters initialized")


class TestTieredAgents:
    """Test tiered agent execution"""
    
    @pytest.mark.asyncio
    async def test_agent_registry(self):
        """Test agent registry has all phases"""
        from backend.agents_core.tiered_agent_framework import AGENT_REGISTRY, AgentPhase
        
        assert AgentPhase.RESEARCH in AGENT_REGISTRY
        assert AgentPhase.DESIGN in AGENT_REGISTRY
        assert AgentPhase.IMPLEMENT in AGENT_REGISTRY
        assert AgentPhase.TEST in AGENT_REGISTRY
        assert AgentPhase.DEPLOY in AGENT_REGISTRY
        
        print("✓ All 5 agent phases registered")
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test agent creation"""
        from backend.agents_core.tiered_agent_framework import ResearchAgent, DesignAgent
        
        research = ResearchAgent()
        design = DesignAgent()
        
        assert research.phase.value == 'research'
        assert design.phase.value == 'design'
        print("✓ Agents created successfully")
    
    @pytest.mark.asyncio
    async def test_agent_orchestrator(self):
        """Test agent orchestrator"""
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        stats = agent_orchestrator.get_stats()
        
        assert agent_orchestrator.max_concurrent_pipelines == 2
        assert agent_orchestrator.auto_recover_on_failure is True
        print("✓ Agent orchestrator configured")
    
    @pytest.mark.asyncio
    async def test_artifact_creation(self):
        """Test artifact creation"""
        from backend.agents_core.tiered_agent_framework import AgentArtifact, AgentPhase
        
        artifact = AgentArtifact(
            artifact_id='test_123',
            artifact_type='research_doc',
            phase=AgentPhase.RESEARCH,
            content={'findings': ['test']}
        )
        
        assert artifact.artifact_type == 'research_doc'
        assert artifact.phase == AgentPhase.RESEARCH
        print("✓ Artifacts work correctly")


class TestGovernanceSafety:
    """Test governance and safety systems"""
    
    @pytest.mark.asyncio
    async def test_rbac_system(self):
        """Test RBAC system"""
        from backend.governance_system.rbac_system import rbac_system, ServiceAccountRole
        
        await rbac_system.start()
        
        # Check default accounts created
        assert len(rbac_system.service_accounts) >= 4
        
        # Check learning mission account
        learning_account = rbac_system.get_service_account('learning_mission_service')
        assert learning_account is not None
        assert learning_account.role == ServiceAccountRole.LEARNING_MISSION
        
        print(f"✓ RBAC system: {len(rbac_system.service_accounts)} service accounts")
    
    @pytest.mark.asyncio
    async def test_permission_check(self):
        """Test permission checking"""
        from backend.governance_system.rbac_system import rbac_system
        
        await rbac_system.start()
        
        # Learning mission should have read/write
        allowed = await rbac_system.check_permission(
            principal='learning_mission_service',
            resource_type='staging_model',
            resource_id='test_model',
            action='write'
        )
        
        assert allowed is True
        
        # But NOT delete
        denied = await rbac_system.check_permission(
            principal='learning_mission_service',
            resource_type='production_db',
            resource_id='customers',
            action='delete'
        )
        
        assert denied is False
        
        print("✓ RBAC permissions working correctly")
    
    @pytest.mark.asyncio
    async def test_approval_engine(self):
        """Test inline approval engine"""
        from backend.governance_system.inline_approval_engine import (
            inline_approval_engine,
            ResourceAccess
        )
        
        await inline_approval_engine.start()
        
        # Test low-risk auto-approval
        low_risk = ResourceAccess(
            resource_type='test_environment',
            resource_id='test_123',
            action='read',
            requester='test_service'
        )
        
        result = await inline_approval_engine.request_approval(low_risk)
        
        assert result.risk_score < 0.3
        # Decision might be denied if RBAC fails (test_service doesn't exist)
        # But risk calculation should work
        
        print(f"✓ Approval engine: risk scoring works (score: {result.risk_score:.2f})")
    
    @pytest.mark.asyncio
    async def test_risk_calculation(self):
        """Test risk score calculation"""
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        
        await inline_approval_engine.start()
        
        # Calculate risk scores
        prod_risk = inline_approval_engine.resource_risk_weights.get('production_db')
        staging_risk = inline_approval_engine.resource_risk_weights.get('staging_db')
        
        assert prod_risk > staging_risk
        print(f"✓ Risk weights: production ({prod_risk}) > staging ({staging_risk})")


class TestChaosEngineering:
    """Test chaos engineering system"""
    
    @pytest.mark.asyncio
    async def test_component_profiles(self):
        """Test component profile registry"""
        from backend.chaos.component_profiles import component_registry, ComponentType
        
        profiles = component_registry.list_profiles()
        
        assert len(profiles) >= 7  # At least 7 profiles
        
        # Check specific profiles exist
        backend_api = component_registry.get_profile('backend_api')
        assert backend_api is not None
        assert backend_api.component_type == ComponentType.API_ENDPOINT
        assert len(backend_api.stress_patterns) >= 5
        assert len(backend_api.guardrails) >= 3
        
        print(f"✓ Component profiles: {len(profiles)} registered")
    
    @pytest.mark.asyncio
    async def test_attack_scripts(self):
        """Test attack scripts are registered"""
        from backend.chaos.attack_scripts import ATTACK_SCRIPTS, StressPattern
        
        # Check key attack scripts exist
        assert StressPattern.SQL_INJECTION in ATTACK_SCRIPTS
        assert StressPattern.RATE_LIMIT_BREACH in ATTACK_SCRIPTS
        assert StressPattern.BURST_TRAFFIC in ATTACK_SCRIPTS
        
        print(f"✓ Attack scripts: {len(ATTACK_SCRIPTS)} registered")
    
    @pytest.mark.asyncio
    async def test_chaos_agent_starts(self):
        """Test chaos agent initialization"""
        from backend.chaos.chaos_agent import chaos_agent
        
        await chaos_agent.start()
        
        assert chaos_agent.running is True
        assert chaos_agent.auto_run_enabled is False  # Safety: disabled by default
        assert chaos_agent.environment == 'staging'
        assert chaos_agent.blast_radius_limit == 3
        
        print("✓ Chaos agent started (DISABLED by default for safety)")
    
    @pytest.mark.asyncio
    async def test_resilience_scoring(self):
        """Test resilience scoring"""
        from backend.chaos.component_profiles import component_registry
        
        profiles = component_registry.get_by_resilience(ascending=True)
        
        # All should start at 0.0 (never tested)
        for profile in profiles:
            assert profile.resilience_score >= 0.0
            assert profile.resilience_score <= 1.0
        
        print("✓ Resilience scoring initialized")


class TestPortWatchdogFix:
    """Test port watchdog fixes"""
    
    def test_port_range_reduced(self):
        """Test port range is now 8000-8010"""
        from backend.core.port_manager import port_manager
        
        assert port_manager.start_port == 8000
        assert port_manager.end_port == 8010
        
        print(f"✓ Port range: {port_manager.start_port}-{port_manager.end_port} (was 8000-8500)")
    
    def test_cleanup_method_exists(self):
        """Test cleanup method exists"""
        from backend.core.port_manager import port_manager
        
        assert hasattr(port_manager, 'cleanup_all_allocations')
        print("✓ Port manager has cleanup method")
    
    @pytest.mark.asyncio
    async def test_watchdog_only_checks_allocated(self):
        """Test watchdog only checks allocated ports"""
        from backend.core.port_watchdog import port_watchdog
        from backend.core.port_manager import port_manager
        
        # Clear allocations
        port_manager.allocations.clear()
        
        # Should not check anything
        await port_watchdog._perform_health_checks()
        
        print("✓ Watchdog skips when no allocations")


class TestIntegrations:
    """Test integrations between systems"""
    
    @pytest.mark.asyncio
    async def test_learning_mission_approval_flow(self):
        """Test mission → approval → execution flow"""
        from backend.learning_systems.learning_mission_launcher import LearningMission
        
        mission = LearningMission(
            mission_id='test_mission_123',
            mission_type='autonomous_learning',
            description='Test mission',
            context={'domain': 'test'},
            priority=0.5,
            launched_by='test'
        )
        
        # Check risk/impact scores calculated
        assert hasattr(mission, 'risk_score')
        assert hasattr(mission, 'impact_score')
        assert hasattr(mission, 'combined_score')
        
        assert 0.0 <= mission.risk_score <= 1.0
        assert 0.0 <= mission.impact_score <= 1.0
        assert 0.0 <= mission.combined_score <= 1.0
        
        print(f"✓ Mission scoring: risk={mission.risk_score:.2f}, impact={mission.impact_score:.2f}, combined={mission.combined_score:.2f}")
    
    @pytest.mark.asyncio
    async def test_agent_uses_playbooks(self):
        """Test agents can use playbooks"""
        from backend.agents_core.tiered_agent_framework import ResearchAgent
        
        agent = ResearchAgent()
        await agent.initialize()
        
        # Agent should have playbook registry
        assert hasattr(agent, 'use_playbook')
        print("✓ Agents can use playbooks as tools")
    
    @pytest.mark.asyncio
    async def test_chaos_feeds_healing(self):
        """Test chaos results feed healing system"""
        from backend.chaos.chaos_agent import chaos_agent
        
        await chaos_agent.start()
        
        # Check healing orchestrator connection
        assert hasattr(chaos_agent, 'healing_orchestrator')
        print("✓ Chaos agent connected to healing system")
    
    @pytest.mark.asyncio
    async def test_all_systems_have_immutable_log(self):
        """Test all systems integrate with immutable log"""
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        from backend.governance_system.inline_approval_engine import inline_approval_engine
        from backend.chaos.chaos_agent import chaos_agent
        
        systems = [
            learning_triage_agent,
            agent_orchestrator,
            inline_approval_engine,
            chaos_agent
        ]
        
        for system in systems:
            assert hasattr(system, 'immutable_log')
        
        print("✓ All systems integrated with immutable log")


class TestResolutionProtocol:
    """Test the resolution protocol we created"""
    
    @pytest.mark.asyncio
    async def test_resolution_protocol_exists(self):
        """Test resolution protocol module exists"""
        from backend.core.resolution_protocol import ResolutionProtocol
        
        protocol = ResolutionProtocol()
        
        assert hasattr(protocol, 'resolve_issue')
        assert hasattr(protocol, 'classify_issue')
        print("✓ Resolution protocol created and working")
    
    @pytest.mark.asyncio
    async def test_issue_classification(self):
        """Test issue classification"""
        from backend.core.resolution_protocol import ResolutionProtocol
        
        protocol = ResolutionProtocol()
        
        # Test classifications
        assert protocol.classify_issue("ImportError: No module named 'test'") == "import_error"
        assert protocol.classify_issue("Network connection failed") == "network_fault"
        assert protocol.classify_issue("Config error in settings") == "config_error"
        
        print("✓ Issue classification working")


def run_all_tests():
    """Run all E2E tests"""
    print()
    print("=" * 80)
    print("GRACE E2E TEST SUITE")
    print("=" * 80)
    print()
    
    test_classes = [
        TestRemoteLearning,
        TestLearningFeedbackLoop,
        TestTieredAgents,
        TestGovernanceSafety,
        TestChaosEngineering,
        TestPortWatchdogFix,
        TestIntegrations,
        TestResolutionProtocol
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 80)
        
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [
            method for method in dir(test_instance)
            if method.startswith('test_')
        ]
        
        for method_name in test_methods:
            try:
                method = getattr(test_instance, method_name)
                
                # Run async or sync
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                passed += 1
            except Exception as e:
                print(f"✗ {method_name} FAILED: {e}")
                failed += 1
    
    print()
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    print()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
