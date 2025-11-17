"""Tests for QuorumEngine - Trust-Weighted Consensus"""

import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cognition.QuorumEngine import QuorumEngine
from cognition.models import (
    DecisionTask, SpecialistProposal, DecisionStrategy, RiskLevel
)
from cognition.GraceLoopOutput import GraceLoopOutput, OutputType

class TestQuorumEngine:
    """Test QuorumEngine consensus mechanisms"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.engine = QuorumEngine()
    
    def create_test_proposal(
        self, 
        specialist: str, 
        result: str, 
        confidence: float = 0.8,
        trust: float = 0.85
    ) -> SpecialistProposal:
        """Helper to create test proposal"""
        output = GraceLoopOutput(
            loop_id=f"test_loop_{specialist}",
            component=specialist,
            output_type=OutputType.DECISION,
            result=result,
            confidence=confidence,
            constitutional_compliance=True
        )
        
        return SpecialistProposal(
            specialist_name=specialist,
            output=output,
            trust_score=trust,
            track_record=0.8,
            recency_weight=0.9
        )
    
    def test_majority_vote(self):
        """Test simple majority voting"""
        task = DecisionTask(
            task_id="test_majority",
            description="Test majority vote",
            context={},
            strategy=DecisionStrategy.MAJORITY
        )
        
        # Add proposals
        task.specialist_proposals = [
            self.create_test_proposal('reflection', 'approve', confidence=0.9, trust=0.85),
            self.create_test_proposal('hunter', 'approve', confidence=0.7, trust=0.90),
            self.create_test_proposal('meta', 'reject', confidence=0.6, trust=0.88)
        ]
        
        decision = self.engine.deliberate(task)
        
        assert decision is not None
        assert decision.strategy_used == DecisionStrategy.MAJORITY
        assert decision.chosen_proposal is not None
        assert len(decision.dissent) == 2
        assert decision.confidence > 0
    
    def test_softmax_weighted_vote(self):
        """Test softmax-weighted consensus"""
        task = DecisionTask(
            task_id="test_softmax",
            description="Test softmax voting",
            context={},
            strategy=DecisionStrategy.SOFTMAX_WEIGHTED
        )
        
        task.specialist_proposals = [
            self.create_test_proposal('reflection', 'option_a', confidence=0.95, trust=0.85),
            self.create_test_proposal('hunter', 'option_b', confidence=0.7, trust=0.90),
            self.create_test_proposal('causal', 'option_c', confidence=0.6, trust=0.82)
        ]
        
        decision = self.engine.deliberate(task)
        
        assert decision is not None
        assert decision.strategy_used == DecisionStrategy.SOFTMAX_WEIGHTED
        assert 'probability' in decision.voting_summary
        assert 'score_distribution' in decision.voting_summary
        assert sum(decision.voting_summary['score_distribution'].values()) == pytest.approx(1.0)
    
    def test_min_risk_vote(self):
        """Test minimum risk strategy"""
        task = DecisionTask(
            task_id="test_min_risk",
            description="Test min risk",
            context={},
            strategy=DecisionStrategy.MIN_RISK,
            risk_level=RiskLevel.CRITICAL,
            constraints=['safety_policy', 'data_privacy']
        )
        
        # High confidence proposal
        safe_output = GraceLoopOutput(
            loop_id="safe_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="safe_action",
            confidence=0.95,
            constitutional_compliance=True
        )
        safe_output.add_policy_tag('safety_policy', 'compliant')
        safe_output.add_policy_tag('data_privacy', 'compliant')
        
        # Low confidence proposal
        risky_output = GraceLoopOutput(
            loop_id="risky_loop",
            component="hunter",
            output_type=OutputType.DECISION,
            result="risky_action",
            confidence=0.6,
            constitutional_compliance=True
        )
        
        task.specialist_proposals = [
            SpecialistProposal(
                specialist_name='reflection',
                output=safe_output,
                trust_score=0.85,
                track_record=0.9,
                recency_weight=0.95
            ),
            SpecialistProposal(
                specialist_name='hunter',
                output=risky_output,
                trust_score=0.90,
                track_record=0.85,
                recency_weight=0.9
            )
        ]
        
        decision = self.engine.deliberate(task)
        
        assert decision is not None
        assert decision.strategy_used == DecisionStrategy.MIN_RISK
        assert decision.governance_validated is True
        assert decision.chosen_proposal.component == 'reflection'
    
    def test_unanimous_consensus(self):
        """Test unanimous agreement"""
        task = DecisionTask(
            task_id="test_unanimous",
            description="Test unanimous",
            context={},
            strategy=DecisionStrategy.UNANIMOUS
        )
        
        # All agree
        task.specialist_proposals = [
            self.create_test_proposal('reflection', 'unanimous_choice'),
            self.create_test_proposal('hunter', 'unanimous_choice'),
            self.create_test_proposal('meta', 'unanimous_choice')
        ]
        
        decision = self.engine.deliberate(task)
        
        assert decision is not None
        assert decision.voting_summary['unanimous'] is True
        assert len(decision.dissent) == 0
        assert decision.confidence == 1.0
    
    def test_unanimous_failure_escalation(self):
        """Test escalation when unanimous consensus fails"""
        task = DecisionTask(
            task_id="test_unanimous_fail",
            description="Test unanimous failure",
            context={},
            strategy=DecisionStrategy.UNANIMOUS
        )
        
        # Disagreement
        task.specialist_proposals = [
            self.create_test_proposal('reflection', 'choice_a'),
            self.create_test_proposal('hunter', 'choice_b'),
            self.create_test_proposal('meta', 'choice_c')
        ]
        
        decision = self.engine.deliberate(task)
        
        assert decision is not None
        assert decision.voting_summary['unanimous'] is False
        assert decision.voting_summary['requires_escalation'] is True
        assert decision.chosen_proposal.requires_approval is True
    
    def test_trust_update(self):
        """Test specialist trust updating"""
        initial_trust = self.engine.specialist_trust['reflection']
        
        # Successful outcome
        self.engine.update_specialist_trust('reflection', outcome_success=True)
        after_success = self.engine.specialist_trust['reflection']
        
        # Failed outcome
        self.engine.update_specialist_trust('reflection', outcome_success=False)
        after_failure = self.engine.specialist_trust['reflection']
        
        assert after_success > initial_trust
        assert after_failure < after_success
    
    def test_track_record(self):
        """Test track record calculation"""
        # Build track record
        for i in range(10):
            self.engine.update_specialist_trust('test_specialist', outcome_success=(i % 2 == 0))
        
        track_record = self.engine.get_specialist_track_record('test_specialist')
        
        assert track_record == pytest.approx(0.5)  # 50% success rate
    
    def test_governance_compliance_bonus(self):
        """Test that governance compliance increases proposal score"""
        task = DecisionTask(
            task_id="test_governance",
            description="Test governance bonus",
            context={},
            strategy=DecisionStrategy.SOFTMAX_WEIGHTED
        )
        
        # Compliant proposal
        compliant_output = GraceLoopOutput(
            loop_id="compliant_loop",
            component="reflection",
            output_type=OutputType.DECISION,
            result="compliant_action",
            confidence=0.8,
            constitutional_compliance=True
        )
        compliant_output.add_policy_tag('policy1', 'compliant')
        compliant_output.add_policy_tag('policy2', 'compliant')
        
        # Non-compliant proposal with higher base confidence
        non_compliant_output = GraceLoopOutput(
            loop_id="non_compliant_loop",
            component="hunter",
            output_type=OutputType.DECISION,
            result="non_compliant_action",
            confidence=0.9,
            constitutional_compliance=False
        )
        
        task.specialist_proposals = [
            SpecialistProposal(
                specialist_name='reflection',
                output=compliant_output,
                trust_score=0.85,
                track_record=0.8,
                recency_weight=0.9
            ),
            SpecialistProposal(
                specialist_name='hunter',
                output=non_compliant_output,
                trust_score=0.85,
                track_record=0.8,
                recency_weight=0.9
            )
        ]
        
        decision = self.engine.deliberate(task)
        
        # Compliant proposal should win due to governance bonus
        assert decision.chosen_proposal.constitutional_compliance is True
    
    def test_explain(self):
        """Test decision explanation"""
        task = DecisionTask(
            task_id="test_explain",
            description="Test explanation",
            context={},
            strategy=DecisionStrategy.MAJORITY
        )
        
        task.specialist_proposals = [
            self.create_test_proposal('reflection', 'choice_a'),
            self.create_test_proposal('hunter', 'choice_b')
        ]
        
        decision = self.engine.deliberate(task)
        explanation = self.engine.explain(decision)
        
        assert 'task_id' in explanation
        assert 'strategy' in explanation
        assert 'winner' in explanation
        assert 'weights' in explanation
        assert 'rationale' in explanation
        assert explanation['task_id'] == task.task_id

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
