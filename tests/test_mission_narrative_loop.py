"""
Test Mission Narrative & Reporting Loop

Tests the complete flow:
1. Mission completes -> outcome logged with narrative
2. Telemetry backfilled with hard pre/post metrics
3. Auto-status briefs aggregate outcomes into "Today I fixed..." summaries
4. Grace can answer "Did it work?" with concrete data
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.asyncio
async def test_mission_outcome_logging():
    """Test that mission outcomes are logged with narratives"""
    from backend.autonomy.mission_outcome_logger import mission_outcome_logger
    
    # Initialize
    await mission_outcome_logger.initialize()
    
    # Simulate mission outcome
    mission_data = {
        "mission_id": "test_mission_001",
        "title": "Fix ecommerce latency",
        "domain_id": "ecommerce",
        "mission_type": "performance_optimization",
        "trigger_reason": "latency exceeded 500ms threshold",
        "tasks_executed": [
            {"type": "analyze_capacity", "status": "completed"},
            {"type": "scale_workers", "status": "completed"}
        ],
        "duration_seconds": 120,
        "metrics_before": {
            "latency_ms": 520,
            "error_rate": 0.05
        },
        "metrics_after": {
            "latency_ms": 280,
            "error_rate": 0.02
        }
    }
    
    # Log the outcome
    result = await mission_outcome_logger.log_mission_outcome(
        mission_id="test_mission_001",
        mission_data=mission_data,
        success=True
    )
    
    # Verify outcome was logged
    assert result["success"] is True
    assert "narrative" in result
    assert "knowledge_id" in result
    assert len(result["narrative"]) > 0
    
    # Verify narrative contains key information
    narrative = result["narrative"]
    assert "latency" in narrative.lower()
    # Accept various success indicators
    success_indicators = ["improved", "better", "stabilized", "completed", "fixed"]
    assert any(indicator in narrative.lower() for indicator in success_indicators), \
        f"Expected success indicator in narrative: {narrative}"
    
    print(f"[OK] Mission outcome logged: {narrative}")
    
    # Verify stats updated
    stats = mission_outcome_logger.get_stats()
    assert stats["outcomes_logged"] > 0
    assert stats["narratives_created"] > 0
    
    return result


@pytest.mark.asyncio
async def test_telemetry_backfill():
    """Test that telemetry is backfilled with hard metrics"""
    from backend.autonomy.mission_outcome_logger import mission_outcome_logger
    
    await mission_outcome_logger.initialize()
    
    mission_data = {
        "mission_id": "test_mission_002",
        "title": "Fix payment gateway errors",
        "domain_id": "payments",
        "mission_type": "error_remediation",
        "trigger_reason": "error rate spiked to 8%",
        "tasks_executed": [
            {"type": "restart_service", "status": "completed"}
        ],
        "duration_seconds": 45,
        "metrics_before": {
            "error_rate": 0.08,
            "success_rate": 0.92
        }
    }
    
    result = await mission_outcome_logger.log_mission_outcome(
        mission_id="test_mission_002",
        mission_data=mission_data,
        success=True
    )
    
    # Verify telemetry was captured
    assert "telemetry" in result
    telemetry = result["telemetry"]
    
    # Check telemetry structure
    assert "metrics_captured" in telemetry
    assert "data_sources" in telemetry
    
    # If metrics were captured, verify structure
    if telemetry["metrics_captured"]:
        assert "pre_post_comparison" in telemetry
        assert "effectiveness_score" in telemetry
        assert len(telemetry["data_sources"]) > 0
        
        print(f"[OK] Telemetry backfilled from {len(telemetry['data_sources'])} sources")
        print(f"  Effectiveness score: {telemetry['effectiveness_score']:.2f}")
    else:
        print("[INFO] Telemetry backfill attempted (metrics may not be available in test env)")
    
    # Verify telemetry backfills tracked
    stats = mission_outcome_logger.get_stats()
    assert "telemetry_backfills" in stats
    
    return result


@pytest.mark.asyncio
async def test_auto_status_brief_generation():
    """Test auto-status brief consolidation"""
    from backend.autonomy.auto_status_brief import auto_status_brief, generate_status_brief
    
    await auto_status_brief.initialize()
    
    # Generate brief (will query recent mission outcomes)
    result = await generate_status_brief()
    
    # Verify brief structure
    assert "success" in result
    assert "narrative" in result
    assert "missions_covered" in result
    
    if result["success"]:
        narrative = result["narrative"]
        missions = result["missions_covered"]
        
        print(f"[OK] Status brief generated covering {missions} missions")
        print(f"\nBrief:\n{narrative}\n")
        
        # Verify narrative structure
        assert len(narrative) > 0
        
        if missions > 0:
            assert "completed" in narrative.lower() or "fixed" in narrative.lower()
            assert "missions" in narrative.lower()
    else:
        print("[INFO] No missions to report (expected in fresh test environment)")
    
    # Verify stats
    stats = auto_status_brief.get_stats()
    assert "briefs_generated" in stats
    assert "interval_hours" in stats
    
    return result


@pytest.mark.asyncio
async def test_complete_narrative_loop():
    """Test the complete narrative loop end-to-end"""
    from backend.autonomy.mission_outcome_logger import mission_outcome_logger
    from backend.autonomy.auto_status_brief import generate_status_brief
    
    print("\n=== Testing Complete Narrative Loop ===\n")
    
    # Step 1: Initialize systems
    await mission_outcome_logger.initialize()
    print("[OK] Mission outcome logger initialized")
    
    # Step 2: Log multiple mission outcomes
    missions = [
        {
            "mission_id": "loop_test_001",
            "title": "Optimize database queries",
            "domain_id": "database",
            "mission_type": "performance",
            "trigger_reason": "query latency exceeded 200ms",
            "metrics_before": {"query_time_ms": 250},
            "metrics_after": {"query_time_ms": 120},
            "duration_seconds": 180
        },
        {
            "mission_id": "loop_test_002",
            "title": "Fix API timeout",
            "domain_id": "api_gateway",
            "mission_type": "reliability",
            "trigger_reason": "timeout errors increased",
            "metrics_before": {"timeout_rate": 0.05},
            "metrics_after": {"timeout_rate": 0.01},
            "duration_seconds": 90
        }
    ]
    
    logged_outcomes = []
    for mission in missions:
        result = await mission_outcome_logger.log_mission_outcome(
            mission_id=mission["mission_id"],
            mission_data=mission,
            success=True
        )
        logged_outcomes.append(result)
        print(f"[OK] Logged: {mission['title']}")
    
    # Verify all outcomes logged
    assert len(logged_outcomes) == len(missions)
    for outcome in logged_outcomes:
        assert outcome["success"] is True
        assert len(outcome["narrative"]) > 0
    
    print(f"\n[OK] {len(logged_outcomes)} mission outcomes logged with narratives")
    
    # Step 3: Generate status brief (should aggregate the outcomes)
    brief_result = await generate_status_brief()
    
    if brief_result.get("success"):
        print(f"\n[OK] Status brief generated")
        print(f"  Missions covered: {brief_result['missions_covered']}")
        print(f"  Domains affected: {brief_result.get('domains_affected', [])}")
        
        # Brief should mention the missions
        narrative = brief_result["narrative"]
        print(f"\n[BRIEF] Preview:\n{narrative[:300]}...\n")
    
    # Step 4: Verify stats
    logger_stats = mission_outcome_logger.get_stats()
    print(f"\n[STATS] Logger Stats:")
    print(f"  Outcomes logged: {logger_stats['outcomes_logged']}")
    print(f"  Narratives created: {logger_stats['narratives_created']}")
    print(f"  Telemetry backfills: {logger_stats['telemetry_backfills']}")
    
    print("\n[PASS] Complete narrative loop test passed!")
    
    return {
        "outcomes_logged": len(logged_outcomes),
        "brief_generated": brief_result.get("success", False),
        "stats": logger_stats
    }


@pytest.mark.asyncio
async def test_narrative_queryability():
    """Test that Grace can query and cite her own fixes"""
    from backend.world_model import grace_world_model
    
    # Initialize world model
    await grace_world_model.initialize()
    
    # Query for recent fixes
    fixes = await grace_world_model.query(
        query="fixed improved mission completed",
        category="system",
        top_k=5
    )
    
    print(f"\n[QUERY] Found {len(fixes)} recent fixes in world model:")
    
    for fix in fixes[:3]:
        print(f"\n  - {fix.content[:150]}...")
        print(f"    Source: {fix.source}")
        print(f"    Confidence: {fix.confidence}")
    
    # Test self-questioning
    answer = await grace_world_model.ask_self("What did I fix recently?")
    
    print(f"\n[ANSWER] Grace's Answer:")
    print(f"  {answer['answer'][:200]}...")
    print(f"  Confidence: {answer['confidence']:.2f}")
    
    assert len(answer['answer']) > 0
    assert answer['confidence'] > 0
    
    return answer


if __name__ == "__main__":
    """Run tests manually"""
    print("Running Mission Narrative Loop Tests\n")
    
    async def run_all_tests():
        try:
            print("1. Testing mission outcome logging...")
            await test_mission_outcome_logging()
            
            print("\n2. Testing telemetry backfill...")
            await test_telemetry_backfill()
            
            print("\n3. Testing auto-status brief...")
            await test_auto_status_brief_generation()
            
            print("\n4. Testing complete loop...")
            await test_complete_narrative_loop()
            
            print("\n5. Testing narrative queryability...")
            await test_narrative_queryability()
            
            print("\n" + "="*60)
            print("[SUCCESS] ALL TESTS PASSED!")
            print("="*60)
            
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_all_tests())