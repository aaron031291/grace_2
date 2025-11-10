"""
Complete Integration Test
Verify all Grace systems work together
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.asyncio
async def test_healing_flow():
    """Test complete healing flow"""
    from backend.autonomous_code_healer import code_healer
    from backend.unified_logger import unified_logger
    
    # Start code healer
    await code_healer.start()
    assert code_healer.running is True
    
    # Log a healing attempt
    await unified_logger.log_healing_attempt(
        attempt_id="test_001",
        error_type="test_error",
        error_message="Test error message",
        detected_by="test",
        severity="low",
        confidence=0.9
    )
    
    # Verify it was logged
    from backend.models import async_session
    from backend.healing_models import HealingAttempt
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(HealingAttempt).where(HealingAttempt.attempt_id == "test_001")
        )
        attempt = result.scalar_one_or_none()
        
        assert attempt is not None
        assert attempt.error_type == "test_error"
        assert attempt.hash is not None  # Crypto hash exists


@pytest.mark.asyncio
async def test_ml_learning():
    """Test ML learning integration"""
    from backend.ml_healing import ml_healing
    from backend.unified_logger import unified_logger
    
    await ml_healing.start()
    assert ml_healing.running is True
    
    # Log learning event
    await unified_logger.log_ml_learning(
        learning_type="pattern_update",
        subsystem="ml_healing",
        pattern_name="test_pattern",
        pattern_success_rate=0.85
    )
    
    # Verify logged
    from backend.models import async_session
    from backend.healing_models import MLLearningLog
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(MLLearningLog).where(MLLearningLog.pattern_name == "test_pattern")
        )
        log = result.scalar_one_or_none()
        
        assert log is not None
        assert log.pattern_success_rate == 0.85


@pytest.mark.asyncio
async def test_data_cube():
    """Test data cube logging"""
    from backend.unified_logger import unified_logger
    
    # Log to data cube
    from backend.models import async_session
    
    async with async_session() as session:
        await unified_logger._log_to_data_cube(
            session=session,
            subsystem='test',
            actor='test_actor',
            action='test_action',
            resource='test_resource',
            success=True,
            duration=1.5,
            confidence=0.9,
            severity='low',
            context={'test': True}
        )
        
        await session.commit()
    
    # Verify in data cube
    from backend.healing_models import DataCubeEntry
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(DataCubeEntry).where(DataCubeEntry.dimension_subsystem == 'test')
        )
        entry = result.scalar_one_or_none()
        
        assert entry is not None
        assert entry.metric_success is True
        assert entry.metric_duration == 1.5


@pytest.mark.asyncio
async def test_governance_framework():
    """Test governance framework integration"""
    from backend.governance_framework import governance_framework
    
    # Check action
    result = await governance_framework.check_action(
        actor='test_user',
        action='create_file',
        resource='backend/test.py',
        context={'description': 'test file'},
        confidence=0.9
    )
    
    assert 'approved' in result
    assert 'checks' in result
    assert 'constitutional' in result['checks']
    assert 'guardrails' in result['checks']
    assert 'whitelist' in result['checks']


@pytest.mark.asyncio
async def test_crypto_verification():
    """Test cryptographic chain verification"""
    from backend.healing_analytics import healing_analytics
    
    report = await healing_analytics.get_crypto_verification_report()
    
    assert 'tables' in report
    assert 'overall_integrity' in report
    assert report['overall_integrity'] is True


@pytest.mark.asyncio
async def test_grace_self_analysis():
    """Test Grace's self-analysis capability"""
    from backend.grace_self_analysis import grace_self_analysis
    
    analysis = await grace_self_analysis.analyze_performance(hours=24)
    
    assert 'health_score' in analysis
    assert 'healing_performance' in analysis
    assert 'learning_performance' in analysis
    assert 'improvement_areas' in analysis
    assert 'strengths' in analysis
    assert 'current_goals' in analysis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
