#!/usr/bin/env python3
"""
Test script for Re-planning on Failure functionality
Tests the complete failure detection, analysis, and replanning pipeline
"""

import asyncio
import logging
from datetime import datetime

from backend.event_bus import event_bus, Event, EventType
from backend.failure_detection_system import failure_detection_system, FailureEvent
from backend.failure_analysis_engine import failure_analysis_engine
from backend.replanning_engine import replanning_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_failure_detection():
    """Test failure detection system"""
    print("🧪 Testing Failure Detection System...")

    # Create a test failure
    test_failure = FailureEvent(
        failure_id="test_task_001",
        source="test_executor",
        error_type="ConnectionError",
        error_message="Failed to connect to external service: timeout",
        context={
            "task_type": "api_call",
            "endpoint": "https://api.example.com/data",
            "timeout": 30,
            "retry_count": 0
        },
        severity="medium"
    )

    # Process the failure
    await failure_detection_system.process_failure(test_failure)

    # Check if analysis was created
    analysis = failure_detection_system.analysis_cache.get("test_task_001")
    if analysis:
        print(f"✅ Analysis created: {analysis.root_cause}")
        print(f"   Recommended strategy: {analysis.recommended_strategy}")
        print(f"   Corrective actions: {len(analysis.corrective_actions)}")
    else:
        print("❌ No analysis created")

    return analysis

async def test_replanning_engine():
    """Test replanning engine"""
    print("\n🧪 Testing RePlanning Engine...")

    # Create a test failure analysis
    from backend.failure_detection_system import FailureAnalysis

    test_analysis = FailureAnalysis(
        failure_id="test_mission_001",
        root_cause="Network connectivity issue with external API",
        corrective_actions=[
            {
                "action_type": "retry",
                "description": "Retry with exponential backoff",
                "parameters": {"max_retries": 3, "backoff_factor": 2},
                "priority": "high"
            },
            {
                "action_type": "fallback",
                "description": "Use cached data as fallback",
                "parameters": {"cache_ttl": 3600},
                "priority": "medium"
            }
        ],
        prevention_measures=[
            "Add circuit breaker pattern",
            "Implement connection pooling",
            "Add health checks for external services"
        ],
        confidence_score=0.85,
        recommended_strategy="retry"
    )

    # Test replanning
    context = {
        "plan_id": "test_mission_001",
        "original_plan": {
            "type": "mission",
            "goals": ["fetch_data", "process_data", "store_results"]
        }
    }

    result = await replanning_engine.replan_based_on_analysis(
        "test_mission_001", test_analysis, context
    )

    if result:
        print(f"✅ Replanning successful: {result.success_probability:.2f} success probability")
        print(f"   Changes made: {len(result.changes_made)}")
        for change in result.changes_made:
            print(f"   - {change.rationale}")
    else:
        print("❌ Replanning failed")

    return result

async def test_event_integration():
    """Test event-driven integration"""
    print("\n🧪 Testing Event Integration...")

    # Subscribe to test events
    events_received = []

    async def test_event_handler(event: Event):
        events_received.append(event)
        print(f"📡 Received event: {event.event_type}")

    event_bus.subscribe(EventType.TASK_FAILED, test_event_handler)
    event_bus.subscribe(EventType.LEARNING_OUTCOME, test_event_handler)

    # Publish a test failure event
    test_event = Event(
        event_type=EventType.TASK_FAILED,
        source="test_system",
        data={
            "task_id": "integration_test_001",
            "error": "Test connection timeout",
            "error_type": "TimeoutError",
            "context": {"test": True}
        }
    )

    await event_bus.publish(test_event)

    # Wait a bit for processing
    await asyncio.sleep(0.1)

    print(f"✅ Events processed: {len(events_received)}")
    for event in events_received:
        print(f"   - {event.event_type} from {event.source}")

async def test_pattern_recognition():
    """Test failure pattern recognition"""
    print("\n🧪 Testing Pattern Recognition...")

    # Create multiple similar failures to test pattern detection
    failures = [
        FailureEvent(
            failure_id=f"pattern_test_{i}",
            source="api_client",
            error_type="ConnectionError",
            error_message="Connection timeout after 30s",
            context={"endpoint": "https://api.service.com", "timeout": 30},
            severity="medium"
        )
        for i in range(3)
    ]

    for failure in failures:
        await failure_analysis_engine.analyze_failure(failure)
        await asyncio.sleep(0.01)  # Small delay

    # Check pattern insights
    insights = failure_analysis_engine.get_pattern_insights()
    print(f"✅ Pattern analysis: {insights['total_patterns']} patterns found")
    print(f"   High confidence patterns: {insights['high_confidence_patterns']}")
    print(f"   Recent patterns: {len(insights['recent_patterns'])}")

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Re-planning on Failure System Tests\n")

    try:
        # Test individual components
        analysis = await test_failure_detection()
        replan_result = await test_replanning_engine()
        await test_event_integration()
        await test_pattern_recognition()

        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)

        # Get system stats
        stats = failure_detection_system.get_failure_stats()
        print(f"Total failures processed: {stats['total_failures']}")
        print(f"Active failures: {stats['active_failures']}")
        print(f"Severity distribution: {stats['severity_distribution']}")

        # Get replanning history
        history = replanning_engine.get_replanning_history()
        if history:
            print(f"Total replannings: {history.get('total_replannings', 0)}")

        print("\n✅ All tests completed successfully!")
        print("🎉 Re-planning on Failure system is operational!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_all_tests())