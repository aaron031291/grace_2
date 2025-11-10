"""Tests for Constitutional AI Framework

Tests constitutional principles, compliance checking, violations,
and clarification workflows.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from backend.models import async_session, engine, Base
from backend.constitutional_models import (
    ConstitutionalPrinciple, ConstitutionalViolation,
    ClarificationRequest, ConstitutionalCompliance
)
from backend.constitutional_engine import constitutional_engine
from backend.constitutional_verifier import constitutional_verifier
from backend.clarifier import clarifier
from backend.seed_constitution import seed_constitutional_principles

@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Setup test database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed constitution
    await seed_constitutional_principles()
    
    yield
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

class TestConstitutionalPrinciples:
    """Test constitutional principles"""
    
    @pytest.mark.asyncio
    async def test_principles_seeded(self):
        """Test that principles are properly seeded"""
        async with async_session() as session:
            result = await session.execute(select(ConstitutionalPrinciple))
            principles = result.scalars().all()
            
            assert len(principles) == 30  # 5 foundational + 10 operational + 15 safety
            
            # Check foundational principles
            foundational = [p for p in principles if p.principle_level == "foundational"]
            assert len(foundational) == 5
            
            # Check all foundational are immutable
            for p in foundational:
                assert p.immutable == True
            
            # Check specific principles exist
            names = [p.principle_name for p in principles]
            assert "beneficence" in names
            assert "transparency_honesty" in names
            assert "accountability" in names
            assert "no_destructive_commands" in names
            assert "no_sensitive_data_exposure" in names
    
    @pytest.mark.asyncio
    async def test_principle_categories(self):
        """Test principle categorization"""
        async with async_session() as session:
            result = await session.execute(
                select(ConstitutionalPrinciple).where(
                    ConstitutionalPrinciple.category == "security"
                )
            )
            security_principles = result.scalars().all()
            
            assert len(security_principles) > 0
            
            # All security principles should be active
            for p in security_principles:
                assert p.active == True

class TestConstitutionalCompliance:
    """Test constitutional compliance checking"""
    
    @pytest.mark.asyncio
    async def test_compliant_action(self):
        """Test checking a compliant action"""
        result = await constitutional_engine.check_constitutional_compliance(
            action_id="test_action_1",
            actor="test_user",
            action_type="read_file",
            resource="/test/file.txt",
            context={"audit_enabled": True},
            confidence=0.95
        )
        
        assert result['compliant'] == True
        assert result['compliance_score'] >= 0.9
        assert len(result['violations']) == 0
    
    @pytest.mark.asyncio
    async def test_destructive_action_blocked(self):
        """Test that destructive actions are blocked"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="code_execution",
            resource="terminal",
            payload={"command": "rm -rf /"},
            confidence=1.0,
            context={}
        )
        
        assert result['allowed'] == False
        assert len(result['violations']) > 0
        
        # Check that no_destructive_commands principle was violated
        violation_principles = [v.get('principle') for v in result['violations']]
        assert "no_destructive_commands" in violation_principles
    
    @pytest.mark.asyncio
    async def test_sensitive_data_exposure_blocked(self):
        """Test that sensitive data exposure is blocked"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="code_generation",
            resource="api_client.py",
            payload={"code": "api_key = 'sk_live_1234567890'"},
            confidence=1.0,
            context={}
        )
        
        assert result['allowed'] == False
        
        # Check violation
        violation_principles = [v.get('principle') for v in result['violations']]
        assert "no_sensitive_data_exposure" in violation_principles
    
    @pytest.mark.asyncio
    async def test_low_confidence_triggers_warning(self):
        """Test that low confidence triggers clarification warning"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="code_generation",
            resource="test.py",
            payload={"code": "def test(): pass"},
            confidence=0.5,  # Low confidence
            context={}
        )
        
        assert result['constitutional_check']['needs_clarification'] == True
        
        # In strict mode, low confidence should block
        assert result['allowed'] == False
    
    @pytest.mark.asyncio
    async def test_self_modification_requires_approval(self):
        """Test that self-modification requires approval"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="file_write",
            resource="constitutional_engine.py",
            payload={"content": "# modified code"},
            confidence=1.0,
            context={"self_modification_approved": False}
        )
        
        assert result['allowed'] == False
        
        violation_principles = [v.get('principle') for v in result['violations']]
        assert "no_self_modification_without_approval" in violation_principles

class TestClarification:
    """Test clarification system"""
    
    @pytest.mark.asyncio
    async def test_detect_ambiguous_pronoun(self):
        """Test detection of ambiguous pronouns"""
        uncertainty = clarifier.detect_uncertainty(
            user_input="Delete it",
            context={"recent_entities": ["file1.txt", "file2.txt", "folder1"]}
        )
        
        assert uncertainty is not None
        assert uncertainty['type'] == "ambiguous_pronoun"
        assert len(uncertainty['options']) > 0
    
    @pytest.mark.asyncio
    async def test_detect_missing_parameter(self):
        """Test detection of missing parameters"""
        uncertainty = clarifier.detect_uncertainty(
            user_input="Fix the bug",
            context={}
        )
        
        assert uncertainty is not None
        assert uncertainty['type'] == "missing_parameter"
    
    @pytest.mark.asyncio
    async def test_detect_vague_requirement(self):
        """Test detection of vague requirements"""
        uncertainty = clarifier.detect_uncertainty(
            user_input="Make it better",
            context={}
        )
        
        assert uncertainty is not None
        assert uncertainty['type'] == "vague_requirement"
    
    @pytest.mark.asyncio
    async def test_clarification_request_flow(self):
        """Test full clarification request/response flow"""
        # Request clarification
        clarification = await constitutional_engine.request_clarification(
            user="test_user",
            original_input="Delete file",
            uncertainty_type="missing_parameter",
            confidence=0.6,
            question="Which file should I delete?",
            options=["file1.txt", "file2.txt"],
            context="Multiple files found",
            timeout_minutes=60
        )
        
        assert clarification['request_id'] is not None
        assert clarification['question'] == "Which file should I delete?"
        
        # Answer clarification
        answer = await constitutional_engine.answer_clarification(
            request_id=clarification['request_id'],
            user_response="file1.txt",
            selected_option="file1.txt"
        )
        
        assert answer['status'] == "answered"
        assert answer['user_response'] == "file1.txt"
    
    @pytest.mark.asyncio
    async def test_pending_clarifications(self):
        """Test getting pending clarifications"""
        # Create a clarification request
        await constitutional_engine.request_clarification(
            user="test_user_2",
            original_input="Improve performance",
            uncertainty_type="vague_requirement",
            confidence=0.65,
            question="What aspect of performance?",
            timeout_minutes=60
        )
        
        # Get pending
        pending = await clarifier.get_pending_clarifications("test_user_2")
        
        assert len(pending) > 0
        assert pending[0]['status'] == "pending" or 'status' not in pending[0]

class TestViolationLogging:
    """Test violation logging"""
    
    @pytest.mark.asyncio
    async def test_log_violation(self):
        """Test logging a constitutional violation"""
        violation = await constitutional_engine.log_violation(
            principle_name="beneficence",
            actor="test_user",
            action="destructive_command",
            resource="/etc/passwd",
            violation_type="attempt",
            detected_by="hunter",
            severity="critical",
            details="Attempted to delete system file",
            blocked=True
        )
        
        assert violation['violation_id'] is not None
        assert violation['principle'] == "beneficence"
        assert violation['blocked'] == True
    
    @pytest.mark.asyncio
    async def test_violation_count(self):
        """Test counting violations"""
        async with async_session() as session:
            result = await session.execute(select(ConstitutionalViolation))
            violations = result.scalars().all()
            
            assert len(violations) > 0

class TestComplianceReporting:
    """Test compliance reporting"""
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self):
        """Test generating compliance report"""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await constitutional_verifier.generate_compliance_report(
            start_date=start_date,
            end_date=end_date
        )
        
        assert 'metrics' in report
        assert 'violations_by_severity' in report
        assert 'violations_by_principle' in report
        assert report['metrics']['total_actions'] >= 0

class TestIntegration:
    """Test integration with other systems"""
    
    @pytest.mark.asyncio
    async def test_governance_integration(self):
        """Test constitutional checks integrate with governance"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="code_execution",
            resource="shell",
            payload={"command": "ls -la"},
            confidence=1.0,
            context={}
        )
        
        # Should have governance decision
        assert result['governance_decision'] is not None
    
    @pytest.mark.asyncio
    async def test_hunter_integration(self):
        """Test constitutional checks integrate with hunter"""
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="network_access",
            resource="external_api",
            payload={"url": "http://malicious.com"},
            confidence=1.0,
            context={}
        )
        
        # Should have hunter alerts field
        assert 'hunter_alerts' in result

def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "-s"])

if __name__ == "__main__":
    run_tests()
