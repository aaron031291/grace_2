"""
Phase 1: Guardian Playbook Unit Tests
Test all Guardian playbooks for:
- Execution without errors
- Metrics reporting
- Dry-run mode support
- Valid metadata
"""

import pytest
import asyncio
from backend.core.guardian_playbooks import (
    GuardianPlaybookRegistry,
    RemediationStatus,
    GuardianPlaybook
)


@pytest.fixture
def registry():
    """Get Guardian playbook registry"""
    return GuardianPlaybookRegistry()


@pytest.fixture
def playbooks(registry):
    """Get all registered playbooks"""
    return registry.playbooks


class TestGuardianPlaybookRegistry:
    """Test the playbook registry itself"""
    
    def test_registry_loads(self, registry):
        """Test that registry initializes"""
        assert registry is not None
        assert hasattr(registry, 'playbooks')
    
    def test_registry_has_playbooks(self, playbooks):
        """Test that playbooks are registered"""
        assert len(playbooks) > 0, "No playbooks registered"
    
    def test_all_playbooks_have_ids(self, playbooks):
        """Test that all playbooks have unique IDs"""
        ids = [pb.playbook_id for pb in playbooks.values()]
        assert len(ids) == len(set(ids)), "Duplicate playbook IDs found"


class TestPlaybookMetadata:
    """Test playbook metadata is valid"""
    
    def test_all_have_names(self, playbooks):
        """Test that all playbooks have names"""
        for playbook_id, playbook in playbooks.items():
            assert playbook.name, f"{playbook_id} missing name"
    
    def test_all_have_descriptions(self, playbooks):
        """Test that all playbooks have descriptions"""
        for playbook_id, playbook in playbooks.items():
            assert playbook.description, f"{playbook_id} missing description"
    
    def test_all_have_trigger_patterns(self, playbooks):
        """Test that all playbooks have trigger patterns"""
        for playbook_id, playbook in playbooks.items():
            assert playbook.trigger_pattern, f"{playbook_id} missing trigger pattern"
    
    def test_all_have_priorities(self, playbooks):
        """Test that all playbooks have valid priorities (1-10)"""
        for playbook_id, playbook in playbooks.items():
            assert 1 <= playbook.priority <= 10, \
                f"{playbook_id} has invalid priority: {playbook.priority}"
    
    def test_all_have_remediation_functions(self, playbooks):
        """Test that all playbooks have remediation functions"""
        for playbook_id, playbook in playbooks.items():
            assert playbook.remediation_function is not None, \
                f"{playbook_id} missing remediation function"


class TestPlaybookExecution:
    """Test playbook execution"""
    
    @pytest.mark.asyncio
    async def test_playbook_port_not_responding(self, playbooks):
        """Test port_not_responding playbook execution"""
        playbook = playbooks.get('port_not_responding')
        if not playbook:
            pytest.skip("port_not_responding playbook not found")
        
        context = {
            'port': 9999,
            'service_name': 'test_service',
            'dry_run': True  # Don't actually restart anything
        }
        
        result = await playbook.execute(context)
        
        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'actions_taken')
        assert isinstance(result.actions_taken, list)
    
    @pytest.mark.asyncio
    async def test_playbook_network_degradation(self, playbooks):
        """Test network_degradation playbook execution"""
        playbook = playbooks.get('network_degradation')
        if not playbook:
            pytest.skip("network_degradation playbook not found")
        
        context = {
            'latency_ms': 500,
            'packet_loss': 0.1,
            'dry_run': True
        }
        
        result = await playbook.execute(context)
        
        assert result is not None
        assert hasattr(result, 'status')
    
    @pytest.mark.asyncio
    async def test_playbook_service_crashed(self, playbooks):
        """Test service_crashed playbook execution"""
        playbook = playbooks.get('service_crashed')
        if not playbook:
            pytest.skip("service_crashed playbook not found")
        
        context = {
            'service_name': 'test_service',
            'pid': 12345,
            'dry_run': True
        }
        
        result = await playbook.execute(context)
        
        assert result is not None
        assert hasattr(result, 'status')
    
    @pytest.mark.asyncio
    async def test_playbook_module_not_found(self, playbooks):
        """Test module_not_found playbook execution"""
        playbook = playbooks.get('module_not_found')
        if not playbook:
            pytest.skip("module_not_found playbook not found")
        
        context = {
            'module_name': 'test_module',
            'import_error': 'No module named test_module',
            'dry_run': True
        }
        
        result = await playbook.execute(context)
        
        assert result is not None
        assert hasattr(result, 'status')
    
    @pytest.mark.asyncio
    async def test_playbook_guardrail_bypassed(self, playbooks):
        """Test guardrail_bypassed playbook execution"""
        playbook = playbooks.get('guardrail_bypassed')
        if not playbook:
            pytest.skip("guardrail_bypassed playbook not found")
        
        context = {
            'action': 'test_action',
            'policy': 'test_policy',
            'dry_run': True
        }
        
        result = await playbook.execute(context)
        
        assert result is not None
        assert hasattr(result, 'status')


class TestPlaybookMetrics:
    """Test playbook metrics tracking"""
    
    @pytest.mark.asyncio
    async def test_execution_count_increments(self, playbooks):
        """Test that execution count increments"""
        playbook = list(playbooks.values())[0]
        
        initial_count = playbook.executions
        
        context = {'dry_run': True}
        await playbook.execute(context)
        
        assert playbook.executions == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_last_executed_timestamp_updates(self, playbooks):
        """Test that last executed timestamp updates"""
        playbook = list(playbooks.values())[0]
        
        initial_timestamp = playbook.last_executed
        
        context = {'dry_run': True}
        await playbook.execute(context)
        
        assert playbook.last_executed != initial_timestamp
        assert playbook.last_executed is not None


class TestPlaybookDryRun:
    """Test dry-run mode for all playbooks"""
    
    @pytest.mark.asyncio
    async def test_all_playbooks_support_dry_run(self, playbooks):
        """Test that all playbooks accept dry_run context"""
        for playbook_id, playbook in playbooks.items():
            context = {'dry_run': True}
            
            try:
                result = await playbook.execute(context)
                assert result is not None, f"{playbook_id} returned None in dry-run"
            except Exception as e:
                pytest.fail(f"{playbook_id} failed in dry-run mode: {e}")


class TestPlaybookResults:
    """Test playbook result structure"""
    
    @pytest.mark.asyncio
    async def test_result_has_required_fields(self, playbooks):
        """Test that results have all required fields"""
        playbook = list(playbooks.values())[0]
        
        context = {'dry_run': True}
        result = await playbook.execute(context)
        
        assert hasattr(result, 'status')
        assert hasattr(result, 'actions_taken')
        assert hasattr(result, 'success')
        assert hasattr(result, 'timestamp')
    
    @pytest.mark.asyncio
    async def test_result_to_dict(self, playbooks):
        """Test that results can be converted to dict"""
        playbook = list(playbooks.values())[0]
        
        context = {'dry_run': True}
        result = await playbook.execute(context)
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'status' in result_dict
        assert 'actions_taken' in result_dict
        assert 'success' in result_dict
        assert 'timestamp' in result_dict


# Summary test to verify count
def test_playbook_count(playbooks):
    """Test that we have the expected number of playbooks"""
    # We have 5 playbooks currently, but the roadmap expects 31
    # This test documents current state
    actual_count = len(playbooks)
    print(f"\nCurrent playbook count: {actual_count}")
    print("Target for Phase 1: 31 playbooks")
    
    assert actual_count >= 5, "Missing core playbooks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
