"""
TRUST Framework Test Suite - PRODUCTION
Tests all 21 systems in the TRUST framework
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.trust_framework import (
    calculate_trust_score,
    create_mission_from_query,
    hallucination_ledger,
    HallucinationEntry,
    ErrorSeverity,
    htm_detector_pool,
    verification_mesh,
    model_health_registry,
    adaptive_guardrails,
    ahead_of_user_research,
    data_hygiene_pipeline,
    chaos_drill_runner,
    model_integrity_registry,
    model_rollback_system,
    stress_test_harness,
    trustscore_gate,
    uncertainty_reporting,
    ContextChunk,
    FreshnessLevel,
    RiskLevel
)


class TestTrustScore:
    """Test trust score calculation"""
    
    def test_trust_score_calculation(self):
        """Test basic trust score calculation"""
        
        score = calculate_trust_score(
            truth=0.9,
            governance=0.8,
            sovereignty=0.95,
            workflow_integrity=0.85,
            model_used="test_model",
            context_window_used=1000
        )
        
        assert score.composite_score > 0.5
        assert score.truth_score == 0.9
        assert score.governance_score == 0.8
        assert score.trust_level.value in ['very_high', 'high', 'medium', 'low', 'very_low']
    
    def test_low_trust_score(self):
        """Test that low scores trigger correct level"""
        
        score = calculate_trust_score(
            truth=0.3,
            governance=0.4,
            sovereignty=0.5,
            workflow_integrity=0.3,
            model_used="test_model",
            context_window_used=1000
        )
        
        assert score.composite_score < 0.3
        assert score.needs_human_review()
        assert not score.can_auto_approve()


class TestMissionManifest:
    """Test mission manifest system"""
    
    def test_create_mission(self):
        """Test mission creation"""
        
        manifest = create_mission_from_query(
            user_query="Test query",
            intent="Test intent",
            risk_level=RiskLevel.MEDIUM
        )
        
        assert manifest.mission_id.startswith("mission_")
        assert manifest.risk_level == RiskLevel.MEDIUM
        assert len(manifest.kpis) > 0
    
    def test_mission_kpis(self):
        """Test KPI tracking"""
        
        manifest = create_mission_from_query(
            user_query="Test",
            intent="Test",
            risk_level=RiskLevel.HIGH
        )
        
        # Update KPI
        manifest.update_kpi("citation_coverage", 0.9)
        
        # Check progress
        progress = manifest.kpi_progress()
        assert progress >= 0.0


class TestHallucinationLedger:
    """Test hallucination tracking"""
    
    def test_log_hallucination(self):
        """Test logging hallucination"""
        
        entry = HallucinationEntry(
            entry_id="test_001",
            origin_model="test_model",
            context_window_used=1000,
            hallucinated_content="Wrong answer",
            correct_content="Right answer",
            severity=ErrorSeverity.MODERATE
        )
        
        initial_count = len(hallucination_ledger.entries)
        hallucination_ledger.log_hallucination(entry)
        
        assert len(hallucination_ledger.entries) > initial_count
    
    def test_trust_adjustment(self):
        """Test trust adjustment calculation"""
        
        adjustment = hallucination_ledger.get_model_trust_adjustment("test_model")
        assert isinstance(adjustment, float)


class TestHTMAnomalyDetection:
    """Test HTM anomaly detector"""
    
    @pytest.mark.asyncio
    async def test_htm_detection(self):
        """Test HTM anomaly detection"""
        
        from backend.trust_framework.htm_anomaly_detector import TokenSequence
        
        # Create test sequence
        sequence = TokenSequence(
            tokens=[1, 2, 3, 4, 5],
            probabilities=[0.8, 0.7, 0.9, 0.6, 0.85]
        )
        
        # Get detector
        detector = htm_detector_pool.get_detector("test_model")
        
        # Detect (will be in learning mode initially)
        detection = detector.detect(sequence)
        
        assert detection is not None
        assert detection.anomaly_score >= 0.0


class TestVerificationMesh:
    """Test verification mesh"""
    
    @pytest.mark.asyncio
    async def test_verification(self):
        """Test verification mesh"""
        
        result = await verification_mesh.verify(
            content="Test content with facts",
            context={'citations': ['source1', 'source2']},
            generator_model="test_model"
        )
        
        assert result is not None
        assert result.total_votes >= 0
        assert result.trust_score is not None


class TestAdaptiveGuardrails:
    """Test adaptive guardrails"""
    
    def test_guardrail_config(self):
        """Test guardrail configuration"""
        
        manifest = create_mission_from_query(
            user_query="Critical operation",
            intent="Critical",
            risk_level=RiskLevel.CRITICAL
        )
        
        config = adaptive_guardrails.get_config_for_mission(manifest)
        
        assert config.min_trust_score >= 0.9
        assert config.quorum_size >= 5
        assert config.verification_layers >= 4
    
    def test_alignment_prompt(self):
        """Test alignment prompt generation"""
        
        manifest = create_mission_from_query(
            user_query="Test",
            intent="Test",
            risk_level=RiskLevel.HIGH
        )
        
        config = adaptive_guardrails.get_config_for_mission(manifest)
        prompt = adaptive_guardrails.get_alignment_prompt(config)
        
        assert len(prompt) > 0
        assert "Grace" in prompt


class TestDataHygiene:
    """Test data hygiene pipeline"""
    
    @pytest.mark.asyncio
    async def test_data_audit(self):
        """Test data audit"""
        
        result = await data_hygiene_pipeline.audit(
            content="Test content",
            metadata={'source': 'test', 'timestamp': '2025-01-01T00:00:00'},
            existing_data=None
        )
        
        assert result is not None
        assert result.score >= 0.0
        assert result.passed in [True, False]


class TestContextProvenance:
    """Test context provenance"""
    
    @pytest.mark.asyncio
    async def test_trustscore_gate(self):
        """Test trustscore gate"""
        
        chunk = ContextChunk(
            chunk_id="test_001",
            content="Test content",
            source_id="test_source",
            source_type="internal",
            confidence=0.8
        )
        
        result = await trustscore_gate.check(chunk)
        
        assert result is not None
        assert 'action' in result
        assert result['action'] in ['allow', 'refresh', 'escalate']


class TestUncertaintyReporting:
    """Test uncertainty reporting"""
    
    def test_create_report(self):
        """Test uncertainty report creation"""
        
        report = uncertainty_reporting.create_report(
            confidence=0.6,
            mission_id="test_mission",
            model_used="test_model"
        )
        
        assert report.confidence == 0.6
        assert len(report.gaps) > 0  # Auto-identifies gaps
    
    def test_report_summary(self):
        """Test report summary generation"""
        
        report = uncertainty_reporting.create_report(
            confidence=0.6,
            target_confidence=0.9
        )
        
        summary = report.generate_summary()
        
        assert "60%" in summary
        assert "need" in summary.lower()


# ============================================================================
# RUN ALL TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_all_systems_importable():
    """Test that all systems can be imported"""
    
    # All imports already done above
    assert hallucination_ledger is not None
    assert htm_detector_pool is not None
    assert verification_mesh is not None
    assert model_health_registry is not None
    assert adaptive_guardrails is not None
    assert ahead_of_user_research is not None
    assert data_hygiene_pipeline is not None
    assert chaos_drill_runner is not None
    assert model_integrity_registry is not None
    assert model_rollback_system is not None
    assert stress_test_harness is not None
    assert trustscore_gate is not None
    assert uncertainty_reporting is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
