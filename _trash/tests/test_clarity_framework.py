"""
Test Clarity Framework - Grace's transparent decision-making system
"""

import pytest
import asyncio
from datetime import datetime
from backend.core.clarity_framework import (
    ClarityFramework,
    DecisionType,
    ClarityLevel,
    Decision
)


@pytest.fixture
def clarity():
    """Create a fresh clarity framework instance"""
    return ClarityFramework()


@pytest.mark.asyncio
async def test_clarity_framework_initialization(clarity):
    """Test that clarity framework initializes correctly"""
    assert clarity is not None
    assert clarity.decision_count == 0
    assert len(clarity.decisions) == 0
    assert clarity.running == False


@pytest.mark.asyncio
async def test_clarity_framework_start(clarity):
    """Test that clarity framework can start"""
    await clarity.start()
    assert clarity.running == True


@pytest.mark.asyncio
async def test_record_decision(clarity):
    """Test recording a decision with full transparency"""
    await clarity.start()
    
    decision = await clarity.record_decision(
        decision_type=DecisionType.AUTONOMOUS_ACTION,
        actor="test_agent",
        action="execute_task",
        resource="test_resource",
        rationale="Testing decision recording",
        confidence=0.95,
        risk_score=0.2,
        clarity_level=ClarityLevel.STANDARD,
        alternatives=["alternative_1", "alternative_2"],
        evidence=[{"type": "metric", "value": 0.9}],
        metrics={"success_rate": 0.95},
        kpis={"task_completion": 1.0}
    )
    
    assert decision is not None
    assert decision.actor == "test_agent"
    assert decision.action == "execute_task"
    assert decision.resource == "test_resource"
    assert decision.rationale == "Testing decision recording"
    assert decision.confidence == 0.95
    assert decision.risk_score == 0.2
    assert len(decision.alternatives_considered) == 2
    assert len(decision.evidence) == 1
    assert decision.metrics["success_rate"] == 0.95
    assert decision.kpis["task_completion"] == 1.0
    
    assert clarity.decision_count == 1
    assert len(clarity.decisions) == 1


@pytest.mark.asyncio
async def test_explain_decision(clarity):
    """Test explaining a decision"""
    await clarity.start()
    
    decision = await clarity.record_decision(
        decision_type=DecisionType.RISK_ASSESSMENT,
        actor="guardian",
        action="approve_action",
        resource="system_config",
        rationale="Risk assessment passed all checks",
        confidence=0.88,
        risk_score=0.3,
        alternatives=["reject", "defer"],
        evidence=[{"check": "security_scan", "passed": True}]
    )
    
    explanation = await clarity.explain_decision(decision.decision_id)
    
    assert explanation is not None
    assert explanation["decision_id"] == decision.decision_id
    assert "guardian" in explanation["summary"]
    assert "approve_action" in explanation["summary"]
    assert explanation["rationale"] == "Risk assessment passed all checks"
    assert "88.0%" in explanation["confidence"]
    assert explanation["risk_level"] == "Medium"
    assert len(explanation["reasoning_chain"]) > 0


@pytest.mark.asyncio
async def test_decision_to_dict(clarity):
    """Test converting decision to dictionary"""
    await clarity.start()
    
    decision = await clarity.record_decision(
        decision_type=DecisionType.POLICY_ENFORCEMENT,
        actor="governance",
        action="enforce_policy",
        resource="api_access",
        rationale="Policy violation detected",
        confidence=1.0,
        risk_score=0.1
    )
    
    decision_dict = decision.to_dict()
    
    assert isinstance(decision_dict, dict)
    assert decision_dict["actor"] == "governance"
    assert decision_dict["action"] == "enforce_policy"
    assert decision_dict["resource"] == "api_access"
    assert decision_dict["confidence"] == 1.0
    assert decision_dict["risk_score"] == 0.1


@pytest.mark.asyncio
async def test_generate_clarity_report(clarity):
    """Test generating clarity report"""
    await clarity.start()
    
    for i in range(3):
        await clarity.record_decision(
            decision_type=DecisionType.AUTONOMOUS_ACTION,
            actor=f"agent_{i}",
            action=f"action_{i}",
            resource=f"resource_{i}",
            rationale=f"Rationale {i}",
            confidence=0.8 + (i * 0.05),
            risk_score=0.2 + (i * 0.1)
        )
    
    report = await clarity.generate_clarity_report()
    
    assert report is not None
    assert report["statistics"]["total_decisions"] == 3
    assert len(report["decisions"]) == 3
    assert "avg_confidence" in report["statistics"]
    assert "avg_risk" in report["statistics"]


@pytest.mark.asyncio
async def test_clarity_stats(clarity):
    """Test getting clarity framework statistics"""
    await clarity.start()
    
    await clarity.record_decision(
        decision_type=DecisionType.TRUST_CALCULATION,
        actor="trust_engine",
        action="calculate_trust",
        resource="domain_metrics",
        rationale="Trust calculation based on KPIs",
        confidence=0.92,
        risk_score=0.15
    )
    
    stats = clarity.get_stats()
    
    assert stats["running"] == True
    assert stats["total_decisions"] == 1
    assert stats["recent_decisions"] == 1
    assert stats["avg_confidence"] > 0
    assert stats["avg_risk"] > 0


@pytest.mark.asyncio
async def test_risk_level_classification(clarity):
    """Test risk level text classification"""
    assert clarity._risk_level_text(0.1) == "Low"
    assert clarity._risk_level_text(0.4) == "Medium"
    assert clarity._risk_level_text(0.7) == "High"
    assert clarity._risk_level_text(0.9) == "Critical"


@pytest.mark.asyncio
async def test_multiple_decision_types(clarity):
    """Test recording different types of decisions"""
    await clarity.start()
    
    decision_types = [
        DecisionType.AUTONOMOUS_ACTION,
        DecisionType.HUMAN_APPROVAL_REQUIRED,
        DecisionType.POLICY_ENFORCEMENT,
        DecisionType.RISK_ASSESSMENT,
        DecisionType.TRUST_CALCULATION
    ]
    
    for dt in decision_types:
        decision = await clarity.record_decision(
            decision_type=dt,
            actor="test_system",
            action="test_action",
            resource="test_resource",
            rationale=f"Testing {dt.value}",
            confidence=0.85,
            risk_score=0.25
        )
        assert decision.decision_type == dt
    
    assert clarity.decision_count == len(decision_types)


def test_clarity_framework_import():
    """Test that clarity framework can be imported"""
    from backend.core.clarity_framework import clarity_framework
    assert clarity_framework is not None
    assert isinstance(clarity_framework, ClarityFramework)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
