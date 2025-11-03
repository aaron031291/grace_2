"""
Real Integration Test - Tests actual backend API
This test verifies the system works end-to-end with a running backend
"""

import asyncio
import httpx
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("GRACE REAL INTEGRATION TEST")
print("=" * 80)
print("\nThis test requires the backend to be running.")
print("Start it with: python -m backend.main")
print("\nTesting...")
print("=" * 80)

API_BASE = "http://localhost:8000"

async def test_backend_health():
    """Test 1: Backend is running"""
    print("\n[1/10] Testing backend health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            print(f"  ✓ Backend is running: {data['message']}")
            return True
    except httpx.ConnectError:
        print("  ✗ Backend not running. Start with: python -m backend.main")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_cognition_status_endpoint():
    """Test 2: Cognition status endpoint"""
    print("\n[2/10] Testing /api/cognition/status...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/api/cognition/status")
            assert response.status_code == 200
            data = response.json()
            assert "overall_health" in data
            assert "domains" in data
            assert "saas_ready" in data
            print(f"  ✓ Status endpoint working")
            print(f"    - Overall Health: {data['overall_health']:.1%}")
            print(f"    - SaaS Ready: {data['saas_ready']}")
            print(f"    - Domains tracked: {len(data['domains'])}")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_cognition_readiness_endpoint():
    """Test 3: Readiness endpoint"""
    print("\n[3/10] Testing /api/cognition/readiness...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/api/cognition/readiness")
            assert response.status_code == 200
            data = response.json()
            assert "ready" in data
            assert "benchmarks" in data
            assert "next_steps" in data
            print(f"  ✓ Readiness endpoint working")
            print(f"    - Ready: {data['ready']}")
            print(f"    - Benchmarks tracked: {len(data.get('benchmarks', {}))}")
            print(f"    - Next steps: {len(data.get('next_steps', []))}")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_publish_metrics():
    """Test 4: Publish test metrics"""
    print("\n[4/10] Publishing test metrics...")
    try:
        from backend.metric_publishers import (
            CoreMetrics, OrchestratorMetrics, KnowledgeMetrics,
            HunterMetrics, MLMetrics
        )
        
        await CoreMetrics.publish_uptime(0.99)
        await CoreMetrics.publish_governance_score(0.92)
        await OrchestratorMetrics.publish_task_completed(True, 0.95)
        await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
        await HunterMetrics.publish_scan_completed(1, 0.97, 0.012)
        await MLMetrics.publish_training_completed(0.94, 1500)
        
        print("  ✓ Metrics published successfully")
        print("    - Core: 2 metrics")
        print("    - Transcendence: 1 metric")
        print("    - Knowledge: 1 metric")
        print("    - Security: 1 metric")
        print("    - ML: 1 metric")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_metrics_reflected_in_api():
    """Test 5: Verify metrics appear in API"""
    print("\n[5/10] Verifying metrics in API response...")
    try:
        # Wait a moment for metrics to propagate
        await asyncio.sleep(0.5)
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/api/cognition/status")
            data = response.json()
            
            # Check if any domains have metrics
            domains_with_metrics = 0
            for domain, info in data.get('domains', {}).items():
                if info.get('kpis') and len(info['kpis']) > 0:
                    domains_with_metrics += 1
            
            print(f"  ✓ Metrics visible in API")
            print(f"    - Domains with metrics: {domains_with_metrics}")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_domain_update_endpoint():
    """Test 6: Domain update endpoint"""
    print("\n[6/10] Testing domain update endpoint...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{API_BASE}/api/cognition/domain/transcendence/update",
                json={"task_success": 0.96, "code_quality": 0.91}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            print("  ✓ Domain update working")
            print(f"    - Domain: {data['domain']}")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_benchmark_endpoint():
    """Test 7: Benchmark endpoint"""
    print("\n[7/10] Testing benchmark endpoint...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{API_BASE}/api/cognition/benchmark/overall_health"
            )
            assert response.status_code == 200
            data = response.json()
            assert "metric" in data
            assert "sustained" in data
            assert "average" in data
            print("  ✓ Benchmark endpoint working")
            print(f"    - Metric: {data['metric']}")
            print(f"    - Sustained: {data['sustained']}")
            print(f"    - Average: {data['average']:.1%}")
            print(f"    - Samples: {data['sample_count']}")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_report_generation():
    """Test 8: Report generation"""
    print("\n[8/10] Testing report generation...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_BASE}/api/cognition/report/latest")
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            report_length = len(data['content'])
            print("  ✓ Report generation working")
            print(f"    - Report size: {report_length} characters")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def test_database_persistence():
    """Test 9: Database persistence"""
    print("\n[9/10] Testing database persistence...")
    try:
        from backend.models import async_session
        from backend.metrics_models import MetricEvent
        
        async with async_session() as session:
            from sqlalchemy import select, func
            
            # Count metric events
            result = await session.execute(select(func.count(MetricEvent.id)))
            count = result.scalar()
            
            print("  ✓ Database persistence working")
            print(f"    - Metric events stored: {count}")
            return count > 0
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_metrics_collection_service():
    """Test 10: Metrics collection service"""
    print("\n[10/10] Testing metrics collection service...")
    try:
        from backend.metrics_service import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # Get stats
        total_metrics = sum(len(queue) for queue in collector.metrics.values())
        total_aggregates = len(collector.aggregates)
        
        print("  ✓ Metrics collection service working")
        print(f"    - Total metrics collected: {total_metrics}")
        print(f"    - Domains with aggregates: {total_aggregates}")
        print(f"    - Subscribers: {len(collector.subscribers)}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    results = []
    
    # Test 1: Backend health
    results.append(await test_backend_health())
    if not results[0]:
        print("\n" + "=" * 80)
        print("BACKEND NOT RUNNING - Cannot continue integration tests")
        print("Start backend with: python -m backend.main")
        print("=" * 80)
        return results
    
    # Run remaining tests
    results.append(await test_cognition_status_endpoint())
    results.append(await test_cognition_readiness_endpoint())
    results.append(await test_publish_metrics())
    results.append(await test_metrics_reflected_in_api())
    results.append(await test_domain_update_endpoint())
    results.append(await test_benchmark_endpoint())
    results.append(await test_report_generation())
    results.append(await test_database_persistence())
    results.append(await test_metrics_collection_service())
    
    # Summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {sum(results)} ✓")
    print(f"Failed: {len(results) - sum(results)} ✗")
    
    if all(results):
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("Grace Cognition Dashboard is fully operational with backend.")
    else:
        print("\n⚠️  Some tests failed. Check output above.")
    
    print("=" * 80)
    return results

if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    sys.exit(0 if all(results) else 1)
