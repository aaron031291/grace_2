"""Simple Cognition System Usage Examples

Demonstrates how to use cognition components in a real workflow.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from cognition.GraceLoopOutput import GraceLoopOutput, OutputType, ConfidenceLevel
from cognition.MemoryScoreModel import MemoryScoreModel
from cognition.GraceCognitionLinter import GraceCognitionLinter
from cognition.GovernancePrimeDirective import GovernancePrimeDirective
from cognition.QuorumEngine import QuorumEngine
from cognition.models import DecisionTask, SpecialistProposal, DecisionStrategy, RiskLevel


async def example_1_simple_output_validation():
    """Example 1: Create output and validate it"""
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Output Validation")
    print("="*60)
    
    # Create a decision output
    output = GraceLoopOutput(
        output_id="example-1",
        loop_id="demo-loop",
        component="reflection",
        output_type=OutputType.DECISION,
        result="Add input validation to user registration endpoint",
        reasoning=[
            "Prevents SQL injection attacks",
            "Validates email format",
            "Enforces password complexity rules"
        ],
        confidence=ConfidenceLevel.HIGH,
        policy_tags=["security", "validation"]
    )
    
    print(f"\n✅ Created output: {output.result}")
    
    # Validate with linter
    linter = GraceCognitionLinter()
    lint_report = await linter.lint(output)
    
    print(f"✅ Lint check: {'PASSED' if lint_report.passed else 'FAILED'}")
    if lint_report.violations:
        for v in lint_report.violations:
            print(f"   [WARN]  {v.severity.value}: {v.description}")
    
    # Validate with governance
    governance = GovernancePrimeDirective()
    verdict = await governance.validate_against_constitution(output)
    
    print(f"✅ Governance: {verdict.decision}")
    print(f"   Compliance score: {verdict.compliance_score:.2f}")
    print(f"   Reason: {verdict.reason}")
    
    return output, verdict


async def example_2_multi_specialist_consensus():
    """Example 2: Get consensus from multiple specialists"""
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Specialist Consensus")
    print("="*60)
    
    # Create a decision task
    task = DecisionTask(
        task_id="task-cache-strategy",
        description="Choose caching strategy for user sessions",
        context={
            "traffic": "high",
            "latency_requirement": "low",
            "data_sensitivity": "medium"
        },
        strategy=DecisionStrategy.SOFTMAX_WEIGHTED,
        risk_level=RiskLevel.MEDIUM
    )
    
    print(f"\n📋 Task: {task.description}")
    
    # Specialist 1: Reflection proposes Redis
    proposal_1 = SpecialistProposal(
        specialist_name="reflection",
        output=GraceLoopOutput(
            output_id="prop-redis",
            loop_id="demo-loop",
            component="reflection",
            output_type=OutputType.PROPOSAL,
            result="Use Redis for session caching with 1-hour TTL",
            reasoning=[
                "Fast in-memory storage",
                "Built-in expiration",
                "Industry standard"
            ],
            confidence=ConfidenceLevel.HIGH
        ),
        trust_score=0.85,
        track_record=0.88,
        recency_weight=0.9
    )
    
    # Specialist 2: Hunter proposes database caching
    proposal_2 = SpecialistProposal(
        specialist_name="hunter",
        output=GraceLoopOutput(
            output_id="prop-db",
            loop_id="demo-loop",
            component="hunter",
            output_type=OutputType.PROPOSAL,
            result="Use database-level caching with materialized views",
            reasoning=[
                "No additional infrastructure",
                "Persistent storage",
                "Easier to manage"
            ],
            confidence=ConfidenceLevel.MEDIUM
        ),
        trust_score=0.75,
        track_record=0.72,
        recency_weight=0.8
    )
    
    # Specialist 3: Meta proposes hybrid
    proposal_3 = SpecialistProposal(
        specialist_name="meta",
        output=GraceLoopOutput(
            output_id="prop-hybrid",
            loop_id="demo-loop",
            component="meta",
            output_type=OutputType.PROPOSAL,
            result="Hybrid: Redis for hot data, database for cold data",
            reasoning=[
                "Best of both worlds",
                "Optimizes cost vs performance",
                "Scalable approach"
            ],
            confidence=ConfidenceLevel.MEDIUM
        ),
        trust_score=0.80,
        track_record=0.78,
        recency_weight=0.85
    )
    
    task.specialist_proposals = [proposal_1, proposal_2, proposal_3]
    
    # Reach consensus
    quorum = QuorumEngine()
    decision = await quorum.reach_consensus(task)
    
    print(f"\n✅ Consensus reached!")
    print(f"   Chosen: {decision.chosen_proposal.result}")
    print(f"   Confidence: {decision.confidence:.2f}")
    print(f"   Rationale: {decision.rationale}")
    print(f"\n   Specialist weights:")
    for specialist, weight in decision.weights.items():
        print(f"      {specialist}: {weight:.3f}")
    
    return decision


def example_3_memory_trust_scoring():
    """Example 3: Calculate trust scores for memories"""
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Memory Trust Scoring")
    print("="*60)
    
    scorer = MemoryScoreModel()
    
    # Scenario 1: High-quality, verified memory
    high_quality = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.95,
        governance_compliant=True,
        usage_success_rate=0.92
    )
    
    print(f"\n✅ High-quality memory:")
    print(f"   Trust score: {high_quality:.3f}")
    print(f"   [OK] Provenance verified")
    print(f"   [OK] 95% consensus agreement")
    print(f"   [OK] Governance compliant")
    print(f"   [OK] 92% usage success rate")
    
    # Scenario 2: Uncertain memory
    uncertain = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.60,
        governance_compliant=True,
        usage_success_rate=0.50
    )
    
    print(f"\n[WARN]  Uncertain memory:")
    print(f"   Trust score: {uncertain:.3f}")
    print(f"   [OK] Provenance verified")
    print(f"   [WARN]  60% consensus agreement")
    print(f"   [OK] Governance compliant")
    print(f"   [WARN]  50% usage success rate")
    
    # Scenario 3: Low-quality memory
    low_quality = scorer.calculate_trust_score(
        provenance_verified=False,
        consensus_agreement=0.40,
        governance_compliant=False,
        usage_success_rate=0.30
    )
    
    print(f"\n❌ Low-quality memory:")
    print(f"   Trust score: {low_quality:.3f}")
    print(f"   [FAIL] Provenance NOT verified")
    print(f"   [FAIL] Only 40% consensus")
    print(f"   [FAIL] Governance violations")
    print(f"   [FAIL] 30% usage success rate")
    
    # Show decay over time
    print(f"\n⏱️  Time decay simulation (half-life: 7 days):")
    print(f"   Fresh:     {high_quality:.3f}")
    
    one_day = scorer.apply_time_decay(high_quality, age_hours=24, half_life_hours=168)
    print(f"   1 day:     {one_day:.3f}")
    
    one_week = scorer.apply_time_decay(high_quality, age_hours=168, half_life_hours=168)
    print(f"   1 week:    {one_week:.3f}")
    
    two_weeks = scorer.apply_time_decay(high_quality, age_hours=336, half_life_hours=168)
    print(f"   2 weeks:   {two_weeks:.3f}")


async def example_4_complete_workflow():
    """Example 4: Complete end-to-end workflow"""
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Workflow")
    print("="*60)
    
    # Step 1: Specialist creates output
    output = GraceLoopOutput(
        output_id="workflow-001",
        loop_id="demo-loop",
        component="reflection",
        output_type=OutputType.DECISION,
        result="Implement API rate limiting: 1000 requests/hour per API key",
        reasoning=[
            "Prevents abuse and DOS attacks",
            "Fair usage across clients",
            "Protects infrastructure costs"
        ],
        confidence=ConfidenceLevel.HIGH,
        policy_tags=["security", "api-design", "rate-limiting"]
    )
    
    print(f"\n1️⃣  Specialist Output")
    print(f"   {output.result}")
    
    # Step 2: Quality check with linter
    linter = GraceCognitionLinter()
    lint_report = await linter.lint(output)
    
    print(f"\n2️⃣  Quality Check")
    print(f"   Status: {'✅ PASSED' if lint_report.passed else '❌ FAILED'}")
    print(f"   Violations: {len(lint_report.violations)}")
    
    # Step 3: Constitutional validation
    governance = GovernancePrimeDirective()
    verdict = await governance.validate_against_constitution(output)
    
    print(f"\n3️⃣  Constitutional Validation")
    print(f"   Decision: {verdict.decision}")
    print(f"   Compliance: {verdict.compliance_score:.2f}")
    
    # Step 4: Calculate trust score
    scorer = MemoryScoreModel()
    trust_score = scorer.calculate_trust_score(
        provenance_verified=True,
        consensus_agreement=0.90,
        governance_compliant=(verdict.decision == "ALLOW"),
        usage_success_rate=0.0  # New memory
    )
    
    print(f"\n4️⃣  Memory Trust Scoring")
    print(f"   Initial trust: {trust_score:.3f}")
    
    # Step 5: Simulate storage and usage
    print(f"\n5️⃣  Memory Lifecycle")
    print(f"   [OK] Stored in LoopMemoryBank")
    print(f"   [OK] Indexed by policy tags: {', '.join(output.policy_tags)}")
    print(f"   [OK] Available for future loops")
    
    print(f"\n✅ Workflow complete! Output processed and stored.")


async def main():
    """Run all examples"""
    
    print("\n🚀 GRACE COGNITION SYSTEM - USAGE EXAMPLES")
    print("="*60)
    
    # Run examples
    await example_1_simple_output_validation()
    await example_2_multi_specialist_consensus()
    example_3_memory_trust_scoring()
    await example_4_complete_workflow()
    
    print("\n" + "="*60)
    print("✅ All examples completed successfully!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
