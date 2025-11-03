"""
Simplified Grace E2E Test - Tests core functionality
Run this to verify Grace is operational
"""

import sys
import asyncio
from datetime import datetime
from pathlib import Path
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("GRACE SIMPLIFIED E2E TEST")
print("=" * 80)
print(f"Start Time: {datetime.now()}")
print("=" * 80)
print()

test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def test(name):
    """Decorator for tests"""
    def decorator(func):
        async def wrapper():
            try:
                print(f"[TEST] {name}...", end=" ")
                await func()
                print("✓ PASSED")
                test_results["passed"] += 1
            except Exception as e:
                print(f"✗ FAILED: {e}")
                test_results["failed"] += 1
                test_results["errors"].append((name, str(e)))
        return wrapper
    return decorator

@test("1. Metrics Service Import")
async def test_metrics_import():
    from backend.metrics_service import get_metrics_collector, publish_metric
    collector = get_metrics_collector()
    assert collector is not None

@test("2. Cognition Engine Import")
async def test_cognition_import():
    from backend.cognition_metrics import get_metrics_engine
    engine = get_metrics_engine()
    assert engine is not None
    assert len(engine.domains) > 0

@test("3. Metric Publishing")
async def test_publish_metric():
    from backend.metrics_service import publish_metric
    await publish_metric("test", "test_metric", 0.95)

@test("4. Metric Publishers Import")
async def test_publishers():
    from backend.metric_publishers import (
        CoreMetrics, OrchestratorMetrics, KnowledgeMetrics,
        HunterMetrics, MLMetrics, TemporalMetrics,
        ParliamentMetrics, FederationMetrics, SpeechMetrics
    )
    assert all([CoreMetrics, OrchestratorMetrics, KnowledgeMetrics])

@test("5. Publish Core Metrics")
async def test_core_metrics():
    from backend.metric_publishers import CoreMetrics
    await CoreMetrics.publish_uptime(0.99)
    await CoreMetrics.publish_governance_score(0.92)

@test("6. Publish Transcendence Metrics")
async def test_transcendence_metrics():
    from backend.metric_publishers import OrchestratorMetrics
    await OrchestratorMetrics.publish_task_completed(True, 0.92)
    await OrchestratorMetrics.publish_plan_created(0.88)

@test("7. Publish Knowledge Metrics")
async def test_knowledge_metrics():
    from backend.metric_publishers import KnowledgeMetrics
    await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
    await KnowledgeMetrics.publish_search_performed(0.93, 8)

@test("8. Publish Security Metrics")
async def test_security_metrics():
    from backend.metric_publishers import HunterMetrics
    await HunterMetrics.publish_scan_completed(2, 0.96, 0.015)
    await HunterMetrics.publish_threat_quarantined(auto_fixed=True)

@test("9. Publish ML Metrics")
async def test_ml_metrics():
    from backend.metric_publishers import MLMetrics
    await MLMetrics.publish_training_completed(0.94, 1800)
    await MLMetrics.publish_deployment_completed(True, 0.028)

@test("10. Publish Temporal Metrics")
async def test_temporal_metrics():
    from backend.metric_publishers import TemporalMetrics
    await TemporalMetrics.publish_prediction_made(0.87)
    await TemporalMetrics.publish_causal_graph_updated(0.82)

@test("11. Publish Parliament Metrics")
async def test_parliament_metrics():
    from backend.metric_publishers import ParliamentMetrics
    await ParliamentMetrics.publish_vote_completed(0.95)
    await ParliamentMetrics.publish_recommendation_adopted(True)

@test("12. Publish Federation Metrics")
async def test_federation_metrics():
    from backend.metric_publishers import FederationMetrics
    await FederationMetrics.publish_connector_health("test", 0.98)
    await FederationMetrics.publish_api_call(True, "test")

@test("13. Publish Speech Metrics")
async def test_speech_metrics():
    from backend.metric_publishers import SpeechMetrics
    await SpeechMetrics.publish_recognition(0.91)
    await SpeechMetrics.publish_voice_command(True, 0.5)

@test("14. Check Metrics Collected")
async def test_metrics_collected():
    from backend.metrics_service import get_metrics_collector
    collector = get_metrics_collector()
    assert len(collector.metrics) > 0, "No metrics collected"

@test("15. Check Domain Status")
async def test_domain_status():
    from backend.metrics_service import get_metrics_collector
    collector = get_metrics_collector()
    status = collector.get_all_domains_status()
    assert len(status) > 0, "No domain status available"

@test("16. Check Cognition Status")
async def test_cognition_status():
    from backend.cognition_metrics import get_metrics_engine
    engine = get_metrics_engine()
    status = engine.get_status()
    assert "overall_health" in status
    assert "domains" in status
    assert "saas_ready" in status

@test("17. Check Readiness Report")
async def test_readiness_report():
    from backend.cognition_metrics import get_metrics_engine
    engine = get_metrics_engine()
    report = engine.get_readiness_report()
    assert "ready" in report
    assert "benchmarks" in report
    assert "next_steps" in report

@test("18. Check Benchmark Scheduler")
async def test_benchmark_scheduler():
    from backend.benchmark_scheduler import get_benchmark_scheduler
    scheduler = get_benchmark_scheduler()
    assert scheduler is not None

@test("19. Readiness Report Generator")
async def test_report_generator():
    from backend.readiness_report import get_report_generator
    generator = get_report_generator()
    report = generator.generate_markdown_report()
    assert len(report) > 100, "Report too short"

@test("20. CLI Commands Import")
async def test_cli_import():
    from backend.cli.commands.cognition_command import (
        cognition_status, cognition_readiness
    )
    assert callable(cognition_status)
    assert callable(cognition_readiness)

async def run_all_tests():
    """Run all tests"""
    tests = [
        test_metrics_import,
        test_cognition_import,
        test_publish_metric,
        test_publishers,
        test_core_metrics,
        test_transcendence_metrics,
        test_knowledge_metrics,
        test_security_metrics,
        test_ml_metrics,
        test_temporal_metrics,
        test_parliament_metrics,
        test_federation_metrics,
        test_speech_metrics,
        test_metrics_collected,
        test_domain_status,
        test_cognition_status,
        test_readiness_report,
        test_benchmark_scheduler,
        test_report_generator,
        test_cli_import
    ]
    
    for test_func in tests:
        await test_func()
    
    # Final Report
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']} ✓")
    print(f"Failed: {test_results['failed']} ✗")
    
    if test_results['failed'] > 0:
        print("\nFailed Tests:")
        for name, error in test_results['errors']:
            print(f"  ✗ {name}: {error}")
    
    print("=" * 80)
    
    if test_results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! Cognition Dashboard is operational.")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    
    print("=" * 80)
    print(f"End Time: {datetime.now()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
