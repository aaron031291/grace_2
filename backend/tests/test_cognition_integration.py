"""Integration tests for complete cognition pipeline"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from cognition import (
    GraceLoopOutput, OutputType, ConfidenceLevel,
    GraceCognitionLinter,
    GovernancePrimeDirective,
    FeedbackIntegrator,
    QuorumEngine,
    LoopMemoryBank,
    MemoryScoreModel,
    DecisionTask, SpecialistProposal,
    DecisionStrategy, RiskLevel
)

@pytest.fixture
def sample_output():
    """Create a sample GraceLoopOutput"""
    return GraceLoopOutput(
        output_id="test-001",
        loop_id="loop-001",
        component="reflection",
        output_type=OutputType.INSIGHT,
        result="User authentication should use JWT tokens with 1-hour expiry",
        reasoning=[
            "JWT provides stateless authentication",
            "Short expiry reduces security risk",
            "Industry standard approach"
        ],
        confidence=ConfidenceLevel.HIGH,
        policy_tags=["security", "authentication"]
    )

@pytest.mark.asyncio
async def test_full_pipeline(sample_output):
    """Test complete pipeline: Output → Linter → Governance → Memory"""
    
    # Step 1: Lint the output
    linter = GraceCognitionLinter()
    lint_report = await linter.lint(sample_output)
    
    assert lint_report.output_id == sample_output.output_id
    assert isinstance(lint_report.passed, bool)
    print(f"✅ Linter: {lint_report.summary}")
    
    # Step 2: Constitutional validation
    governance = GovernancePrimeDirective()
    verdict = await governance.validate_against_constitution(sample_output)
    
    assert verdict.decision in ["ALLOW", "DENY", "ESCALATE"]
    assert verdict.compliance_score >= 0.0
    print(f"✅ Governance: {verdict.decision} (score: {verdict.compliance_score:.2f})")
    
    # Step 3: Store in memory (if passed)
    if verdict.decision == "ALLOW":
        scorer = MemoryScoreModel()
        trust_score = scorer.calculate_trust_score(
            provenance_verified=True,
            consensus_agreement=0.9,
            governance_compliant=True,
            usage_success_rate=0.0  # New memory
        )
        
        assert 0.0 <= trust_score <= 1.0
        print(f"✅ Memory scoring: trust={trust_score:.2f}")
    
    print("\n🎉 Full pipeline completed successfully")

@pytest.mark.asyncio
async def test_quorum_consensus():
    """Test QuorumEngine with multiple specialists"""
    
    quorum = QuorumEngine()
    
    # Create decision task
    task = DecisionTask(
        task_id="decision-001",
        description="Choose authentication strategy",
        context={"risk": "medium", "domain": "security"},
        strategy=DecisionStrategy.SOFTMAX_WEIGHTED,
        risk_level=RiskLevel.MEDIUM
    )
    
    # Create specialist proposals
    proposals = [
        SpecialistProposal(
            specialist_name="reflection",
            output=GraceLoopOutput(
                output_id="ref-001",
                loop_id="loop-001",
                component="reflection",
                output_type=OutputType.INSIGHT,
                result="Use JWT with OAuth2",
                confidence=ConfidenceLevel.HIGH
            ),
            trust_score=0.8,
            track_record=0.85,
            recency_weight=0.9
        ),
        SpecialistProposal(
            specialist_name="hunter",
            output=GraceLoopOutput(
                output_id="hunt-001",
                loop_id="loop-001",
                component="hunter",
                output_type=OutputType.INSIGHT,
                result="Use JWT with short expiry",
                confidence=ConfidenceLevel.MEDIUM
            ),
            trust_score=0.7,
            track_record=0.75,
            recency_weight=0.8
        )
    ]
    
    task.specialist_proposals = proposals
    
    # Reach consensus
    decision = await quorum.reach_consensus(task)
    
    assert decision.task_id == task.task_id
    assert decision.chosen_proposal is not None
    assert decision.confidence >= 0.0
    assert len(decision.weights) == 2
    
    print(f"✅ Quorum decision: {decision.rationale}")
    print(f"   Confidence: {decision.confidence:.2f}")
    print(f"   Weights: {decision.weights}")

@pytest.mark.asyncio
async def test_constitutional_compliance():
    """Test constitutional compliance checking"""
    
    governance = GovernancePrimeDirective()
    
    # Test compliant output
    good_output = GraceLoopOutput(
        output_id="good-001",
        loop_id="loop-001",
        component="reflection",
        output_type=OutputType.INSIGHT,
        result="Implement user authentication with proper security",
        policy_tags=["security"]
    )
    
    verdict = await governance.validate_against_constitution(good_output)
    assert verdict.compliance_score >= 0.7
    print(f"✅ Compliant output: {verdict.compliance_score:.2f}")
    
    # Test potentially risky output
    risky_output = GraceLoopOutput(
        output_id="risky-001",
        loop_id="loop-001",
        component="reflection",
        output_type=OutputType.DECISION,
        result="Delete all user data immediately",
        confidence=ConfidenceLevel.LOW,
        policy_tags=["data-deletion", "high-risk"]
    )
    
    risky_verdict = await governance.validate_against_constitution(risky_output)
    # Should still get a verdict, may be flagged for escalation
    assert risky_verdict.decision in ["ALLOW", "DENY", "ESCALATE"]
    print(f"✅ Risky output: {risky_verdict.decision} ({risky_verdict.compliance_score:.2f})")

def test_memory_trust_scoring():
    """Test memory trust score calculation"""
    
    scorer = MemoryScoreModel()
    
    # High trust scenario
    high_trust = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.95,
        governance_compliant=True,
        usage_success_rate=0.9
    )
    
    assert high_trust >= 0.7
    print(f"✅ High trust score: {high_trust:.2f}")
    
    # Low trust scenario
    low_trust = scorer.calculate_trust_score(
        provenance_verified=False,
        consensus_agreement=0.3,
        governance_compliant=False,
        usage_success_rate=0.2
    )
    
    assert low_trust < high_trust
    print(f"✅ Low trust score: {low_trust:.2f}")
    
    # Medium scenario
    medium_trust = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.6,
        governance_compliant=True,
        usage_success_rate=0.5
    )
    
    assert low_trust < medium_trust < high_trust
    print(f"✅ Medium trust score: {medium_trust:.2f}")

def test_time_decay():
    """Test memory decay over time"""
    
    scorer = MemoryScoreModel()
    
    # Fresh memory (0 hours old)
    fresh_score = scorer.apply_time_decay(
        base_trust=0.8,
        age_hours=0,
        half_life_hours=168,
        curve="hyperbolic"
    )
    assert fresh_score == pytest.approx(0.8, abs=0.01)
    
    # One week old (half-life)
    week_old = scorer.apply_time_decay(
        base_trust=0.8,
        age_hours=168,
        half_life_hours=168,
        curve="hyperbolic"
    )
    assert week_old < fresh_score
    
    # Two weeks old
    two_weeks = scorer.apply_time_decay(
        base_trust=0.8,
        age_hours=336,
        half_life_hours=168,
        curve="hyperbolic"
    )
    assert two_weeks < week_old
    
    print(f"✅ Decay: fresh={fresh_score:.2f}, 1w={week_old:.2f}, 2w={two_weeks:.2f}")

@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete end-to-end cognition workflow"""
    
    print("\n" + "="*60)
    print("END-TO-END COGNITION WORKFLOW TEST")
    print("="*60)
    
    # 1. Create output from specialist
    output = GraceLoopOutput(
        output_id="e2e-001",
        loop_id="loop-e2e",
        component="reflection",
        output_type=OutputType.DECISION,
        result="Implement rate limiting: 100 requests/minute per user",
        reasoning=[
            "Prevents API abuse",
            "Standard industry practice",
            "Protects server resources"
        ],
        confidence=ConfidenceLevel.HIGH,
        policy_tags=["security", "api-design"]
    )
    print(f"\n1️⃣  Created output: {output.output_id}")
    
    # 2. Lint for quality
    linter = GraceCognitionLinter()
    lint_report = await linter.lint(output)
    print(f"2️⃣  Linting: {'PASSED' if lint_report.passed else 'FAILED'}")
    
    if not lint_report.passed:
        print(f"   Issues: {len(lint_report.violations)} violations")
    
    # 3. Constitutional validation
    governance = GovernancePrimeDirective()
    verdict = await governance.validate_against_constitution(output)
    print(f"3️⃣  Governance: {verdict.decision} (compliance: {verdict.compliance_score:.2f})")
    
    # 4. Calculate trust score
    scorer = MemoryScoreModel()
    trust = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.95,
        governance_compliant=(verdict.decision == "ALLOW"),
        usage_success_rate=0.0
    )
    print(f"4️⃣  Trust score: {trust:.2f}")
    
    # 5. Apply time decay (simulate 1 day old)
    decayed_trust = scorer.apply_time_decay(
        base_trust=trust,
        age_hours=24,
        half_life_hours=168,
        curve="hyperbolic"
    )
    print(f"5️⃣  After 24h decay: {decayed_trust:.2f}")
    
    print("\n✅ Complete workflow executed successfully!")
    print("="*60)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
