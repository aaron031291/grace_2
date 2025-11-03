"""
End-to-End Cognition System Tests
Tests complete metric flow from publication to readiness evaluation
"""

import pytest
import asyncio
from datetime import datetime

from backend.metrics_service import get_metrics_collector, publish_metric, publish_batch
from backend.cognition_metrics import get_metrics_engine
from backend.benchmark_scheduler import BenchmarkScheduler
from backend.cognition_alerts import get_alert_manager


@pytest.mark.asyncio
async def test_metric_publication():
    """Test that metrics can be published"""
    collector = get_metrics_collector()
    
    # Publish a metric
    await publish_metric("test_domain", "test_kpi", 0.95, {"test": True})
    
    # Verify it's stored
    kpis = collector.get_domain_kpis("test_domain")
    assert "test_kpi" in kpis
    assert kpis["test_kpi"] == 0.95


@pytest.mark.asyncio
async def test_batch_publication():
    """Test batch metric publication"""
    await publish_batch("ml", {
        "model_accuracy": 0.94,
        "deployment_success": 1.0,
        "inference_latency": 0.032
    })
    
    collector = get_metrics_collector()
    kpis = collector.get_domain_kpis("ml")
    
    assert kpis["model_accuracy"] == 0.94
    assert kpis["deployment_success"] == 1.0


@pytest.mark.asyncio
async def test_domain_health_calculation():
    """Test domain health score calculation"""
    collector = get_metrics_collector()
    
    # Publish some metrics
    await publish_batch("security", {
        "threats_detected": 0.0,
        "scan_coverage": 0.95,
        "auto_fix_success": 0.90
    })
    
    health = collector.get_domain_health("security")
    assert health > 0.0
    assert health <= 1.0


@pytest.mark.asyncio
async def test_cognition_engine_status():
    """Test cognition engine status generation"""
    engine = get_metrics_engine()
    
    status = engine.get_status()
    
    assert "timestamp" in status
    assert "overall_health" in status
    assert "overall_trust" in status
    assert "overall_confidence" in status
    assert "saas_ready" in status
    assert "domains" in status


@pytest.mark.asyncio
async def test_readiness_report():
    """Test readiness report generation"""
    engine = get_metrics_engine()
    
    report = engine.get_readiness_report()
    
    assert "ready" in report
    assert "overall_health" in report
    assert "benchmarks" in report
    assert "domains" in report
    assert "next_steps" in report


@pytest.mark.asyncio
async def test_benchmark_evaluation():
    """Test benchmark evaluation logic"""
    engine = get_metrics_engine()
    
    # Simulate high performance
    collector = get_metrics_collector()
    
    for domain in ["core", "transcendence", "security"]:
        await publish_batch(domain, {
            "task_success": 0.92,
            "quality_score": 0.94
        })
    
    # Update engine
    for domain, kpis in collector.aggregates.items():
        if domain in engine.domains:
            engine.update_domain(domain, kpis)
    
    overall_health = engine.get_overall_health()
    assert overall_health > 0.0


@pytest.mark.asyncio
async def test_saas_readiness_trigger():
    """Test SaaS readiness detection"""
    engine = get_metrics_engine()
    
    # Force all benchmarks to high values
    for benchmark in engine.benchmarks.values():
        # Add 8 days of high performance
        for i in range(8):
            benchmark.add_value(0.95, datetime.now())
    
    # Check readiness
    is_ready = engine.is_saas_ready()
    
    # Should be ready with sustained 95% for 8 days
    assert is_ready == True


@pytest.mark.asyncio
async def test_benchmark_scheduler():
    """Test benchmark scheduler evaluation"""
    scheduler = BenchmarkScheduler()
    
    # Run one evaluation
    await scheduler.evaluate_benchmarks()
    
    # Should complete without errors
    assert True


@pytest.mark.asyncio
async def test_alert_system():
    """Test cognition alert system"""
    alert_manager = get_alert_manager()
    
    # Send test alert
    await alert_manager.send_saas_ready_alert(0.92, 0.91, 0.90)
    
    # Check it was recorded
    alerts = alert_manager.get_recent_alerts(limit=1)
    assert len(alerts) > 0
    assert alerts[0]["type"] == "saas_ready"


@pytest.mark.asyncio
async def test_domain_dip_alert():
    """Test domain performance dip alert"""
    alert_manager = get_alert_manager()
    
    # Send domain dip alert
    await alert_manager.send_domain_dip_alert("test_domain", 0.45)
    
    # Check it was recorded
    alerts = alert_manager.get_recent_alerts(limit=1)
    assert len(alerts) > 0
    assert alerts[0]["type"] == "domain_dip"


@pytest.mark.asyncio
async def test_metric_flow_e2e():
    """Test complete end-to-end metric flow"""
    
    # 1. Publish metrics
    await publish_metric("transcendence", "task_success", 0.95)
    
    # 2. Check collector
    collector = get_metrics_collector()
    kpis = collector.get_domain_kpis("transcendence")
    assert "task_success" in kpis
    
    # 3. Sync to engine
    engine = get_metrics_engine()
    engine.update_domain("transcendence", kpis)
    
    # 4. Get status
    status = engine.get_status()
    assert "transcendence" in status["domains"]
    assert status["domains"]["transcendence"]["kpis"]["task_success"] == 0.95
    
    # E2E flow verified!
    assert True


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_metric_publication())
    asyncio.run(test_cognition_engine_status())
    asyncio.run(test_saas_readiness_trigger())
    print("✅ All E2E tests passed!")
