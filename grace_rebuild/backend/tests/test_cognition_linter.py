"""Tests for GraceCognitionLinter - Contradiction Detection"""

import pytest
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cognition.GraceCognitionLinter import GraceCognitionLinter
from cognition.models import ViolationSeverity
from cognition.GraceLoopOutput import GraceLoopOutput, OutputType

class TestGraceCognitionLinter:
    """Test GraceCognitionLinter functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.linter = GraceCognitionLinter()
    
    def test_no_violations(self):
        """Test clean output passes linting"""
        output = GraceLoopOutput(
            loop_id="clean_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="valid_decision",
            confidence=0.9,
            constitutional_compliance=True
        )
        
        report = self.linter.lint(output)
        
        assert report.passed is True
        assert len(report.violations) == 0
        assert report.severity == ViolationSeverity.INFO
    
    def test_direct_conflict_detection(self):
        """Test detection of contradictory statements"""
        output = GraceLoopOutput(
            loop_id="conflict_loop",
            component="reflection",
            output_type=OutputType.REASONING,
            result={
                "statement1": "This is true and valid",
                "statement2": "This is false and invalid"
            },
            confidence=0.8
        )
        
        report = self.linter.lint(output)
        
        assert report.passed is False
        assert len(report.violations) > 0
        assert any(v.violation_type == 'direct_conflict' for v in report.violations)
    
    def test_policy_drift_detection(self):
        """Test policy violation detection"""
        output = GraceLoopOutput(
            loop_id="policy_loop",
            component="hunter",
            output_type=OutputType.DECISION,
            result="action",
            confidence=0.9
        )
        output.add_policy_tag('safety_policy', 'violation', 'Unsafe action detected')
        
        report = self.linter.lint(output)
        
        assert report.passed is False
        assert any(v.violation_type == 'policy_drift' for v in report.violations)
        assert report.severity == ViolationSeverity.ERROR
    
    def test_temporal_inconsistency(self):
        """Test future timestamp detection"""
        output = GraceLoopOutput(
            loop_id="temporal_loop",
            component="causal",
            output_type=OutputType.PREDICTION,
            result="prediction",
            confidence=0.85
        )
        
        # Add future citation
        future_time = datetime.utcnow() + timedelta(days=1)
        output.add_citation('future_source', 0.9, 'future excerpt')
        output.citations[0].timestamp = future_time
        
        report = self.linter.lint(output)
        
        assert any(v.violation_type == 'temporal_inconsistency' for v in report.violations)
    
    def test_expired_output(self):
        """Test expired output detection"""
        output = GraceLoopOutput(
            loop_id="expired_loop",
            component="meta",
            output_type=OutputType.OBSERVATION,
            result="old_observation",
            confidence=0.7,
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        report = self.linter.lint(output)
        
        assert any(v.violation_type == 'temporal_inconsistency' for v in report.violations)
    
    def test_memory_conflict_detection(self):
        """Test conflict with recent memory"""
        # Add a previous output to cache
        previous = GraceLoopOutput(
            loop_id="previous_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="yes",
            confidence=0.9
        )
        self.linter._update_memory_cache(previous)
        
        # New contradicting output
        current = GraceLoopOutput(
            loop_id="current_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="no",
            confidence=0.85
        )
        
        report = self.linter.lint(current, context={'recent_memory': self.linter.recent_memory_cache})
        
        assert any(v.violation_type == 'memory_conflict' for v in report.violations)
    
    def test_constitutional_alignment(self):
        """Test constitutional compliance checking"""
        output = GraceLoopOutput(
            loop_id="unconstitutional_loop",
            component="hunter",
            output_type=OutputType.ACTION,
            result="critical_action",
            confidence=0.9,
            requires_approval=True,
            constitutional_compliance=False
        )
        
        report = self.linter.lint(output)
        
        assert any(v.violation_type == 'constitutional_misalignment' for v in report.violations)
        assert report.severity == ViolationSeverity.CRITICAL
    
    def test_knowledge_artifact_validation(self):
        """Test citation validation against knowledge"""
        # Add knowledge artifact
        self.linter.add_knowledge_artifact('trusted_source', {'trust_score': 0.7})
        
        output = GraceLoopOutput(
            loop_id="citation_loop",
            component="reflection",
            output_type=OutputType.REASONING,
            result="conclusion",
            confidence=0.8
        )
        output.add_citation('trusted_source', confidence=0.95)
        
        report = self.linter.lint(output)
        
        assert any(v.violation_type == 'knowledge_conflict' for v in report.violations)
    
    def test_auto_remediation(self):
        """Test automatic fix generation"""
        output = GraceLoopOutput(
            loop_id="fixable_loop",
            component="temporal",
            output_type=OutputType.OBSERVATION,
            result="observation",
            confidence=0.8
        )
        
        # Add future timestamp (auto-fixable)
        future_time = datetime.utcnow() + timedelta(days=1)
        output.add_citation('source', 0.9)
        output.citations[0].timestamp = future_time
        
        report = self.linter.lint(output)
        
        assert len(report.suggested_fixes) > 0
        assert any(p.safe_to_auto_apply for p in report.suggested_fixes)
        
        # Test auto-remediation
        result = self.linter.auto_remediate(report)
        if result:
            assert result['remediated'] is True
            assert len(result['patches_applied']) > 0
    
    def test_severity_computation(self):
        """Test severity level computation"""
        # Critical violation
        critical_output = GraceLoopOutput(
            loop_id="critical_loop",
            component="hunter",
            output_type=OutputType.ACTION,
            result="action",
            requires_approval=True,
            constitutional_compliance=False
        )
        
        critical_report = self.linter.lint(critical_output)
        assert critical_report.severity == ViolationSeverity.CRITICAL
        
        # Warning violation
        warning_output = GraceLoopOutput(
            loop_id="warning_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="decision",
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        warning_report = self.linter.lint(warning_output)
        # Should have at least info level
        assert warning_report.severity in [ViolationSeverity.INFO, ViolationSeverity.WARNING]
    
    def test_causal_dependency_checking(self):
        """Test causal dependency validation"""
        # Set up dependencies
        self.linter.set_causal_dependencies({
            'meta': ['reflection', 'hunter']
        })
        
        # Output missing required dependency
        output = GraceLoopOutput(
            loop_id="causal_loop",
            component="meta",
            output_type=OutputType.DECISION,
            result="decision",
            context={'causal_chain': ['reflection']}  # Missing 'hunter'
        )
        
        report = self.linter.lint(output)
        
        assert any(v.violation_type == 'causal_mismatch' for v in report.violations)
    
    def test_summary_generation(self):
        """Test report summary generation"""
        output = GraceLoopOutput(
            loop_id="summary_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="action",
            requires_approval=True,
            constitutional_compliance=False
        )
        output.add_policy_tag('policy1', 'violation')
        
        report = self.linter.lint(output)
        
        assert report.summary is not None
        assert 'violation' in report.summary.lower()
        assert len(report.violations) > 0
    
    def test_cache_management(self):
        """Test memory cache size limits"""
        # Fill cache beyond max size
        for i in range(150):
            output = GraceLoopOutput(
                loop_id=f"cache_loop_{i}",
                component="reflection",
                output_type=OutputType.OBSERVATION,
                result=f"observation_{i}",
                constitutional_compliance=True
            )
            report = self.linter.lint(output)
        
        # Cache should be limited
        assert len(self.linter.recent_memory_cache) <= self.linter.max_cache_size
    
    def test_fix_generation_for_conflicts(self):
        """Test fix suggestions for different violation types"""
        output = GraceLoopOutput(
            loop_id="fix_test_loop",
            component="reflection",
            output_type=OutputType.REASONING,
            result={"statement": "This should and should not happen"},
            confidence=0.8
        )
        
        report = self.linter.lint(output)
        
        if report.violations:
            assert len(report.suggested_fixes) > 0
            for fix in report.suggested_fixes:
                assert fix.action in ['remove', 'replace', 'merge', 'escalate']
                assert fix.confidence >= 0.0 and fix.confidence <= 1.0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
