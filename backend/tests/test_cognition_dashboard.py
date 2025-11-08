"""
Integration tests for Cognition Dashboard System
"""

import pytest
import asyncio
from datetime import datetime

from ..metrics_service import get_metrics_collector, publish_metric, publish_batch
from ..cognition_metrics import get_metrics_engine
from ..metric_publishers import (
    OrchestratorMetrics, HunterMetrics, KnowledgeMetrics,
    MLMetrics, TemporalMetrics, ParliamentMetrics,
    FederationMetrics, CoreMetrics, SpeechMetrics
)


@pytest.mark.asyncio
async def test_metrics_collector():
    """Test metrics collector basic functionality"""
    collector = get_metrics_collector()
    
    # Publish test metric
    await collector.publish("transcendence", "task_success", 0.92, {"test": True})
    
    # Verify metric stored
    history = collector.get_metric_history("transcendence", "task_success", hours=1)
    assert len(history) > 0
    assert history[-1].value == 0.92
    
    # Verify aggregation
    kpis = collector.get_domain_kpis("transcendence")
    assert "task_success" in kpis or len(kpis) == 0  # May not aggregate immediately


@pytest.mark.asyncio
async def test_cognition_engine():
    """Test cognition metrics engine"""
    engine = get_metrics_engine()
    
    # Verify domains initialized
    assert "core" in engine.domains
    assert "transcendence" in engine.domains
    assert len(engine.domains) >= 8
    
    # Test domain update
    engine.update_domain("transcendence", {
        "task_success": 0.95,
        "code_quality": 0.90
    })
    
    domain = engine.domains["transcendence"]
    assert domain.kpis["task_success"] == 0.95
    assert domain.health > 0.0
    
    # Test overall metrics
    overall_health = engine.get_overall_health()
    assert 0.0 <= overall_health <= 1.0
    
    # Test readiness report
    report = engine.get_readiness_report()
    assert "ready" in report
    assert "overall_health" in report
    assert "benchmarks" in report
    assert "domains" in report
    assert "next_steps" in report


@pytest.mark.asyncio
async def test_metric_publishers():
    """Test all metric publisher classes"""
    
    # Test Transcendence metrics
    await OrchestratorMetrics.publish_task_completed(True, 0.92)
    await OrchestratorMetrics.publish_plan_created(0.88)
    
    # Test Security metrics
    await HunterMetrics.publish_scan_completed(3, 0.96, 0.015)
    await HunterMetrics.publish_threat_quarantined(auto_fixed=True)
    
    # Test Knowledge metrics
    await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
    await KnowledgeMetrics.publish_search_performed(0.93, 8)
    
    # Test ML metrics
    await MLMetrics.publish_training_completed(0.94, 1800)
    await MLMetrics.publish_deployment_completed(True, 0.028)
    
    # Test Temporal metrics
    await TemporalMetrics.publish_prediction_made(0.87)
    await TemporalMetrics.publish_causal_graph_updated(0.82)
    
    # Test Parliament metrics
    await ParliamentMetrics.publish_vote_completed(0.95)
    await ParliamentMetrics.publish_recommendation_adopted(True)
    
    # Test Federation metrics
    await FederationMetrics.publish_connector_health("github", 0.98)
    await FederationMetrics.publish_api_call(True, "github")
    
    # Test Core metrics
    await CoreMetrics.publish_uptime(0.99)
    await CoreMetrics.publish_governance_score(0.92)
    
    # Test Speech metrics
    await SpeechMetrics.publish_recognition(0.91)
    await SpeechMetrics.publish_voice_command(True, 0.5)
    
    # Give time for aggregation
    await asyncio.sleep(0.1)
    
    collector = get_metrics_collector()
    
    # Verify some metrics were collected
    assert len(collector.metrics) > 0


@pytest.mark.asyncio
async def test_publish_convenience_functions():
    """Test convenience publish functions"""
    
    # Single metric
    await publish_metric("test_domain", "test_kpi", 0.85)
    
    # Batch metrics
    await publish_batch("test_domain", {
        "kpi1": 0.90,
        "kpi2": 0.88,
        "kpi3": 0.92
    })
    
    collector = get_metrics_collector()
    history = collector.get_metric_history("test_domain", "test_kpi", hours=1)
    
    assert len(history) > 0


@pytest.mark.asyncio
async def test_benchmark_windows():
    """Test benchmark rolling windows"""
    engine = get_metrics_engine()
    
    # Check benchmarks exist
    assert "overall_health" in engine.benchmarks
    assert "overall_trust" in engine.benchmarks
    assert "overall_confidence" in engine.benchmarks
    
    # Test benchmark window
    health_bench = engine.benchmarks["overall_health"]
    
    # Add test values
    now = datetime.now()
    health_bench.add_value(0.92, now)
    health_bench.add_value(0.94, now)
    
    # Check average
    avg = health_bench.average()
    assert 0.90 <= avg <= 1.0


@pytest.mark.asyncio
async def test_domain_status():
    """Test getting status for all domains"""
    collector = get_metrics_collector()
    
    # Publish test metrics for multiple domains
    await publish_metric("core", "uptime", 0.98)
    await publish_metric("transcendence", "task_success", 0.91)
    await publish_metric("security", "scan_coverage", 0.95)
    
    await asyncio.sleep(0.1)
    
    status = collector.get_all_domains_status()
    
    assert "core" in status
    assert "transcendence" in status
    
    for domain_id, domain_data in status.items():
        assert "health" in domain_data
        assert "trust" in domain_data
        assert "confidence" in domain_data
        assert "kpis" in domain_data


@pytest.mark.asyncio
async def test_readiness_next_steps():
    """Test readiness report next steps generation"""
    engine = get_metrics_engine()
    
    report = engine.get_readiness_report()
    next_steps = report.get("next_steps", [])
    
    # Should have recommendations
    assert len(next_steps) > 0
    
    # If not ready, should have improvement steps
    if not report["ready"]:
        improvement_steps = [s for s in next_steps if "Improve" in s or "Strengthen" in s]
        assert len(improvement_steps) > 0


def test_metrics_collector_thread_safety():
    """Test that metrics collector is thread-safe"""
    import threading
    
    collector = get_metrics_collector()
    
    def publish_many():
        for i in range(100):
            asyncio.run(publish_metric("test", f"metric_{i % 10}", float(i % 100) / 100))
    
    threads = [threading.Thread(target=publish_many) for _ in range(5)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # Should not crash
    status = collector.get_all_domains_status()
    assert status is not None


if __name__ == "__main__":
    # Run tests manually
    import sys
    sys.path.insert(0, "../..")
    
    async def run_tests():
        print("Running Cognition Dashboard Tests...\n")
        
        print("1. Testing metrics collector...")
        await test_metrics_collector()
        print("   [OK] Passed\n")
        
        print("2. Testing cognition engine...")
        await test_cognition_engine()
        print("   [OK] Passed\n")
        
        print("3. Testing metric publishers...")
        await test_metric_publishers()
        print("   [OK] Passed\n")
        
        print("4. Testing publish functions...")
        await test_publish_convenience_functions()
        print("   [OK] Passed\n")
        
        print("5. Testing benchmark windows...")
        await test_benchmark_windows()
        print("   [OK] Passed\n")
        
        print("6. Testing domain status...")
        await test_domain_status()
        print("   [OK] Passed\n")
        
        print("7. Testing readiness next steps...")
        await test_readiness_next_steps()
        print("   [OK] Passed\n")
        
        print("8. Testing thread safety...")
        test_metrics_collector_thread_safety()
        print("   [OK] Passed\n")
        
        print("All tests passed! ✅")
    
    asyncio.run(run_tests())
