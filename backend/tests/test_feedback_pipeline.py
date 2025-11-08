"""Tests for Feedback Pipeline - Governance and Integration"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime

from cognition import (
    GraceLoopOutput,
    OutputType,
    governance_prime_directive,
    feedback_integrator,
    GovernanceDecision
)

class TestGovernancePrimeDirective:
    """Test constitutional validation gate"""
    
    @pytest.mark.asyncio
    async def test_approve_compliant_output(self):
        """Should approve output with full compliance"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_001",
            component="test_component",
            output_type=OutputType.REASONING,
            result="This is a safe, compliant output",
            confidence=0.95,
            constitutional_compliance=True
        )
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        assert verdict.is_approved()
        assert verdict.decision in [GovernanceDecision.GO, GovernanceDecision.DEGRADE]
        assert verdict.compliance_score >= 0.0
        assert verdict.safe_to_store
    
    @pytest.mark.asyncio
    async def test_block_non_compliant_output(self):
        """Should block output flagged as non-compliant"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_002",
            component="test_component",
            output_type=OutputType.ACTION,
            result="rm -rf /",
            confidence=0.9,
            constitutional_compliance=False  # Pre-flagged
        )
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        assert verdict.decision == GovernanceDecision.BLOCK
        assert not verdict.is_approved()
        assert 'blocked' in verdict.tags
        assert 'constitutional_violation' in verdict.tags
    
    @pytest.mark.asyncio
    async def test_escalate_low_confidence(self):
        """Should escalate output with low confidence"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_003",
            component="test_component",
            output_type=OutputType.DECISION,
            result="Complex decision with uncertainty",
            confidence=0.4,  # Low confidence
            constitutional_compliance=True
        )
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        assert verdict.decision == GovernanceDecision.ESCALATE
        assert verdict.needs_escalation()
        assert 'requires_human_review' in verdict.tags
    
    @pytest.mark.asyncio
    async def test_degrade_with_errors(self):
        """Should degrade trust for output with errors"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_004",
            component="test_component",
            output_type=OutputType.GENERATION,
            result="Generated code with issues",
            confidence=0.8,
            constitutional_compliance=True
        )
        output.add_error("Syntax error detected")
        output.add_warning("Unused variable")
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        # Should still approve but with degraded trust
        assert verdict.is_approved() or verdict.decision == GovernanceDecision.DEGRADE
        if verdict.decision == GovernanceDecision.DEGRADE:
            assert 'degraded_trust' in verdict.tags
    
    @pytest.mark.asyncio
    async def test_detect_sensitive_content(self):
        """Should detect and tag sensitive content"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_005",
            component="test_component",
            output_type=OutputType.ACTION,
            result="Here is the password: secret123",
            confidence=0.9,
            constitutional_compliance=True
        )
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        # Should detect sensitive content
        assert 'restricted_context' in verdict.tags or not verdict.safe_to_store
    
    @pytest.mark.asyncio
    async def test_explain_verdict(self):
        """Should generate human-readable explanation"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_006",
            component="test_component",
            output_type=OutputType.REASONING,
            result="Test output",
            confidence=0.95,
            constitutional_compliance=True
        )
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        explanation = governance_prime_directive.explain(verdict)
        
        assert len(explanation) > 0
        assert "Governance Decision" in explanation
        assert "Compliance Score" in explanation
        assert str(verdict.decision.value) in explanation.upper()


class TestFeedbackIntegrator:
    """Test feedback integration pipeline"""
    
    @pytest.mark.asyncio
    async def test_integrate_approved_output(self):
        """Should integrate approved output into memory"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_101",
            component="test_component",
            output_type=OutputType.REASONING,
            result="Valid reasoning output",
            confidence=0.95,
            constitutional_compliance=True
        )
        output.add_citation("source_1", 0.9, "Supporting evidence")
        
        memory_ref = await feedback_integrator.integrate(output)
        
        # Should return memory reference
        assert memory_ref is not None
        assert memory_ref.startswith("mem_")
    
    @pytest.mark.asyncio
    async def test_block_non_compliant_output(self):
        """Should not integrate blocked output"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_102",
            component="test_component",
            output_type=OutputType.ACTION,
            result="Destructive action",
            confidence=0.9,
            constitutional_compliance=False
        )
        
        memory_ref = await feedback_integrator.integrate(output)
        
        # Should not store blocked output
        assert memory_ref is None
    
    @pytest.mark.asyncio
    async def test_compute_trust_score(self):
        """Should compute accurate trust scores"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_103",
            component="test_component",
            output_type=OutputType.REASONING,
            result="Test output",
            confidence=0.8,
            quality_score=0.9,
            constitutional_compliance=True
        )
        output.add_citation("source_1", 0.95)
        output.add_citation("source_2", 0.85)
        
        # Get verdict first
        verdict = await governance_prime_directive.validate_against_constitution(output)
        
        # Compute trust score
        trust_score = await feedback_integrator._compute_trust_score(output, verdict)
        
        assert 0.0 <= trust_score <= 1.0
        assert trust_score > 0.5  # Should be reasonably high
    
    @pytest.mark.asyncio
    async def test_trust_degradation(self):
        """Should degrade trust for outputs with errors"""
        
        output = GraceLoopOutput(
            loop_id="test_loop_104",
            component="test_component",
            output_type=OutputType.GENERATION,
            result="Output with issues",
            confidence=0.8,
            constitutional_compliance=True
        )
        output.add_error("Error 1")
        output.add_error("Error 2")
        output.add_warning("Warning 1")
        
        verdict = await governance_prime_directive.validate_against_constitution(output)
        trust_score = await feedback_integrator._compute_trust_score(output, verdict)
        
        # Trust should be degraded due to errors
        assert trust_score < 0.8  # Lower than base confidence
    
    @pytest.mark.asyncio
    async def test_evidence_quality_boost(self):
        """Should boost trust for high-quality evidence"""
        
        output_with_evidence = GraceLoopOutput(
            loop_id="test_loop_105a",
            component="test_component",
            output_type=OutputType.DECISION,
            result="Well-evidenced decision",
            confidence=0.7,
            constitutional_compliance=True
        )
        output_with_evidence.add_citation("high_quality_source", 0.95)
        output_with_evidence.add_citation("verified_source", 0.9)
        
        output_without_evidence = GraceLoopOutput(
            loop_id="test_loop_105b",
            component="test_component",
            output_type=OutputType.DECISION,
            result="Poorly evidenced decision",
            confidence=0.7,
            constitutional_compliance=True
        )
        
        verdict_with = await governance_prime_directive.validate_against_constitution(output_with_evidence)
        verdict_without = await governance_prime_directive.validate_against_constitution(output_without_evidence)
        
        trust_with = await feedback_integrator._compute_trust_score(output_with_evidence, verdict_with)
        trust_without = await feedback_integrator._compute_trust_score(output_without_evidence, verdict_without)
        
        # Evidence should boost trust
        assert trust_with > trust_without
    
    @pytest.mark.asyncio
    async def test_feedback_acknowledgment(self):
        """Should handle feedback acknowledgment"""
        
        memory_ref = "mem_test_12345678"
        metrics = {
            'storage_time_ms': 150,
            'importance': 0.8
        }
        
        # Should not raise exception
        await feedback_integrator.on_feedback_ack(memory_ref, metrics)


class TestEndToEndPipeline:
    """Test complete feedback pipeline flow"""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test full governance -> trust -> memory -> events flow"""
        
        # Create output
        output = GraceLoopOutput(
            loop_id="e2e_test_001",
            component="reflection",
            output_type=OutputType.REFLECTION,
            result="Reflection on recent patterns",
            confidence=0.85,
            quality_score=0.9,
            constitutional_compliance=True,
            importance=0.7
        )
        output.add_citation("memory_ref_123", 0.9, "Previous observation")
        output.add_citation("knowledge_graph", 0.85, "Causal pattern")
        
        # Integrate
        memory_ref = await feedback_integrator.integrate(output)
        
        # Verify integration
        assert memory_ref is not None
        
        # Verify can get verdict independently
        verdict = await governance_prime_directive.validate_against_constitution(output)
        assert verdict.is_approved()
        assert verdict.compliance_score > 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
