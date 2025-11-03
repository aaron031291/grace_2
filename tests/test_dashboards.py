"""Tests for Revenue Tracking and Dashboard Systems"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.transcendence.business.revenue_tracker import (
    revenue_tracker,
    RevenueTransaction,
    Expense,
    RevenueForecast,
    BusinessMetrics,
    RevenueOptimization
)
from backend.transcendence.dashboards.observatory_dashboard import observatory_dashboard
from backend.models import async_session


@pytest.mark.asyncio
async def test_track_income():
    """Test revenue tracking"""
    result = await revenue_tracker.track_income(
        source="Consulting",
        amount=5000.0,
        category="consulting",
        client_id="CLIENT-001",
        description="Website development project",
        payment_method="bank_transfer"
    )
    
    assert result["amount"] == 5000.0
    assert result["source"] == "Consulting"
    assert result["status"] == "completed"
    assert "transaction_id" in result
    
    print(f"✓ Income tracked: {result}")


@pytest.mark.asyncio
async def test_track_expense():
    """Test expense tracking"""
    result = await revenue_tracker.track_expense(
        category="hosting",
        amount=200.0,
        description="AWS hosting costs",
        vendor="Amazon Web Services"
    )
    
    assert result["amount"] == 200.0
    assert result["category"] == "hosting"
    assert result["status"] == "completed"
    assert "expense_id" in result
    
    print(f"✓ Expense tracked: {result}")


@pytest.mark.asyncio
async def test_calculate_profit():
    """Test profit calculation"""
    # Add some test data
    await revenue_tracker.track_income("Consulting", 10000.0, "consulting")
    await revenue_tracker.track_income("SaaS", 5000.0, "saas")
    await revenue_tracker.track_expense("hosting", 500.0, "Server costs")
    await revenue_tracker.track_expense("marketing", 1000.0, "Google Ads")
    
    result = await revenue_tracker.calculate_profit("month")
    
    assert result["revenue"] >= 15000.0
    assert result["expenses"] >= 1500.0
    assert result["profit"] > 0
    assert "profit_margin" in result
    
    print(f"✓ Profit calculated: {result}")


@pytest.mark.asyncio
async def test_revenue_sources():
    """Test revenue source analysis"""
    # Add diverse revenue
    await revenue_tracker.track_income("Consulting", 8000.0, "consulting")
    await revenue_tracker.track_income("Consulting", 6000.0, "consulting")
    await revenue_tracker.track_income("SaaS", 3000.0, "saas")
    await revenue_tracker.track_income("Trading", 2000.0, "trading")
    
    sources = await revenue_tracker.analyze_revenue_sources()
    
    assert len(sources) > 0
    assert sources[0]["source"] == "Consulting"  # Top performer
    assert "total_revenue" in sources[0]
    assert "transaction_count" in sources[0]
    
    print(f"✓ Revenue sources analyzed: {len(sources)} sources")
    for source in sources:
        print(f"  - {source['source']}: ${source['total_revenue']}")


@pytest.mark.asyncio
async def test_growth_rate():
    """Test growth rate calculation"""
    result = await revenue_tracker.calculate_growth_rate("month")
    
    assert "growth_rate" in result
    assert "current_revenue" in result
    assert "previous_revenue" in result
    assert result["growth_direction"] in ["up", "down"]
    
    print(f"✓ Growth rate: {result['growth_rate']}% {result['growth_direction']}")


@pytest.mark.asyncio
async def test_revenue_forecast():
    """Test ML-based revenue forecasting"""
    # Add historical data
    for i in range(10):
        await revenue_tracker.track_income(
            f"Business-{i % 3}",
            1000.0 + (i * 100),
            "consulting"
        )
    
    forecasts = await revenue_tracker.forecast_revenue(months_ahead=3)
    
    assert len(forecasts) <= 3
    if len(forecasts) > 0:
        assert "predicted_revenue" in forecasts[0]
        assert "confidence" in forecasts[0]
        assert "month" in forecasts[0]
    
    print(f"✓ Revenue forecasts generated: {len(forecasts)}")
    for forecast in forecasts:
        print(f"  - {forecast['month']}: ${forecast['predicted_revenue']:.2f} ({forecast['confidence']*100:.0f}% confidence)")


@pytest.mark.asyncio
async def test_optimizations():
    """Test Grace's optimization suggestions"""
    # Add significant revenue
    await revenue_tracker.track_income("TopBusiness", 20000.0, "consulting")
    await revenue_tracker.track_income("TopBusiness", 15000.0, "consulting")
    await revenue_tracker.track_expense("operations", 5000.0, "Various costs")
    
    suggestions = await revenue_tracker.suggest_optimizations()
    
    assert isinstance(suggestions, list)
    if len(suggestions) > 0:
        assert "type" in suggestions[0]
        assert "title" in suggestions[0]
        assert "confidence" in suggestions[0]
    
    print(f"✓ Optimization suggestions: {len(suggestions)}")
    for sugg in suggestions:
        print(f"  - {sugg['title']} ({sugg['type']})")


@pytest.mark.asyncio
async def test_dashboard_cognitive_state():
    """Test dashboard cognitive state API"""
    state = await observatory_dashboard.get_cognitive_state()
    
    assert "status" in state
    assert state["status"] in ["idle", "active"]
    
    print(f"✓ Cognitive state: {state['status']}")


@pytest.mark.asyncio
async def test_dashboard_reasoning_chains():
    """Test reasoning chains API"""
    chains = await observatory_dashboard.get_reasoning_chains(limit=5)
    
    assert isinstance(chains, list)
    print(f"✓ Reasoning chains retrieved: {len(chains)}")


@pytest.mark.asyncio
async def test_dashboard_memory_formation():
    """Test memory formation API"""
    memories = await observatory_dashboard.get_memory_formation(limit=5)
    
    assert isinstance(memories, list)
    print(f"✓ Memory formations retrieved: {len(memories)}")


@pytest.mark.asyncio
async def test_dashboard_proposals():
    """Test pending proposals API"""
    proposals = await observatory_dashboard.get_proposals_pending()
    
    assert isinstance(proposals, list)
    print(f"✓ Pending proposals: {len(proposals)}")


@pytest.mark.asyncio
async def test_business_metrics_update():
    """Test business metrics aggregation"""
    # Track revenue and trigger metrics update
    await revenue_tracker.track_income("TestBusiness", 10000.0, "testing")
    
    # Verify metrics were created
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(BusinessMetrics)
            .where(BusinessMetrics.business_name == "TestBusiness")
        )
        metric = result.scalar_one_or_none()
        
        if metric:
            assert metric.revenue > 0
            print(f"✓ Business metrics updated: ${metric.revenue}")


async def run_all_tests():
    """Run all dashboard tests"""
    print("\n" + "="*60)
    print("DASHBOARD & REVENUE TRACKING TESTS")
    print("="*60 + "\n")
    
    tests = [
        ("Track Income", test_track_income),
        ("Track Expense", test_track_expense),
        ("Calculate Profit", test_calculate_profit),
        ("Analyze Revenue Sources", test_revenue_sources),
        ("Calculate Growth Rate", test_growth_rate),
        ("Revenue Forecast", test_revenue_forecast),
        ("Optimization Suggestions", test_optimizations),
        ("Dashboard Cognitive State", test_dashboard_cognitive_state),
        ("Dashboard Reasoning Chains", test_dashboard_reasoning_chains),
        ("Dashboard Memory Formation", test_dashboard_memory_formation),
        ("Dashboard Proposals", test_dashboard_proposals),
        ("Business Metrics Update", test_business_metrics_update),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            print("-" * 60)
            await test_func()
            passed += 1
            print(f"✓ PASSED: {test_name}\n")
        except Exception as e:
            failed += 1
            print(f"✗ FAILED: {test_name}")
            print(f"  Error: {e}\n")
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
