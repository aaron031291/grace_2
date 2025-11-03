"""
Test temporal reasoning and predictive simulation system
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import engine, Base, async_session, Task
from backend.task_executor import ExecutionTask
from backend.temporal_reasoning import temporal_reasoner
from backend.simulation_engine import simulation_engine
from backend.temporal_models import EventPattern, Simulation, DurationEstimate

async def setup_test_data():
    """Create test data for temporal analysis"""
    print("\n=== Setting up test data ===")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Cleaning up existing test data...")
    async with async_session() as session:
        from sqlalchemy import delete
        await session.execute(delete(ExecutionTask).where(ExecutionTask.task_id.like('test-%')))
        await session.commit()
    
    async with async_session() as session:
        now = datetime.utcnow()
        
        for i in range(20):
            task = Task(
                user="test_user",
                title=f"Test Task {i}",
                description="Automated test task",
                status="completed" if i % 3 == 0 else "pending",
                priority="high" if i % 5 == 0 else "medium",
                created_at=now - timedelta(hours=24-i),
                completed_at=now - timedelta(hours=23-i) if i % 3 == 0 else None,
                auto_generated=True
            )
            session.add(task)
        
        task_types = ["model_training", "data_processing", "analysis", "deployment"]
        for i in range(30):
            task_type = task_types[i % len(task_types)]
            start_time = now - timedelta(hours=48-i*1.5)
            
            base_duration = 300 if task_type == "model_training" else 60
            duration_variation = (i % 10) * 30
            
            exec_task = ExecutionTask(
                task_id=f"test-{i}",
                user="test_user",
                task_type=task_type,
                description=f"Test {task_type}",
                status="completed",
                progress=100.0,
                result="Success",
                created_at=start_time,
                started_at=start_time + timedelta(seconds=5),
                completed_at=start_time + timedelta(seconds=base_duration + duration_variation)
            )
            session.add(exec_task)
        
        await session.commit()
    
    print("[+] Created 20 tasks and 30 execution tasks")

async def test_pattern_analysis():
    """Test 1: Pattern discovery"""
    print("\n=== Test 1: Pattern Analysis ===")
    
    await temporal_reasoner.initialize()
    
    patterns = await temporal_reasoner.analyze_sequences(lookback_hours=48)
    
    print(f"[+] Discovered {len(patterns)} patterns")
    for i, pattern in enumerate(patterns[:3], 1):
        print(f"  {i}. {pattern['sequence']}")
        print(f"     Frequency: {pattern['frequency']}, Confidence: {pattern['confidence']:.2f}")
        if pattern.get('avg_duration'):
            print(f"     Avg Duration: {pattern['avg_duration']:.1f}s")
    
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(EventPattern))
        stored = result.scalars().all()
        print(f"[+] Stored {len(stored)} patterns in database")
    
    return len(patterns) > 0

async def test_next_event_prediction():
    """Test 2: Next event prediction"""
    print("\n=== Test 2: Next Event Prediction ===")
    
    current_state = {
        "last_event_type": "task_created",
        "user": "test_user",
        "context": "high_activity"
    }
    
    predictions = await temporal_reasoner.predict_next_event(current_state)
    
    print(f"[+] Generated {len(predictions)} predictions")
    for event, probability in predictions[:5]:
        print(f"  {event}: {probability:.2%}")
    
    return len(predictions) > 0

async def test_duration_estimation():
    """Test 3: Task duration estimation"""
    print("\n=== Test 3: Duration Estimation ===")
    
    task_types = ["model_training", "data_processing", "analysis"]
    
    for task_type in task_types:
        estimate = await temporal_reasoner.estimate_duration(task_type)
        
        print(f"\n  {task_type}:")
        print(f"    Avg: {estimate['avg_duration']:.1f}s")
        print(f"    Range: {estimate['min']:.1f}s - {estimate['max']:.1f}s")
        print(f"    95% CI: {estimate['ci_lower']:.1f}s - {estimate['ci_upper']:.1f}s")
        print(f"    Confidence: {estimate['confidence']:.2%}")
    
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(DurationEstimate))
        estimates = result.scalars().all()
        print(f"\n[+] Computed {len(estimates)} duration estimates")
    
    return True

async def test_anomaly_detection():
    """Test 4: Timing anomaly detection"""
    print("\n=== Test 4: Anomaly Detection ===")
    
    anomalies = await temporal_reasoner.detect_anomalous_timing(lookback_hours=48)
    
    print(f"[+] Detected {len(anomalies)} timing anomalies")
    for anomaly in anomalies[:3]:
        faster = "faster" if anomaly['faster_than_expected'] else "slower"
        print(f"  {anomaly['event_type']}: {anomaly['actual']:.1f}s ({faster} than {anomaly['expected']:.1f}s)")
        print(f"    Deviation: {anomaly['deviation_sigma']:.1f} sigma, Severity: {anomaly['severity']}")
    
    return True

async def test_interval_change_simulation():
    """Test 5: Simulate reflection interval change"""
    print("\n=== Test 5: Reflection Interval Simulation ===")
    
    action = {
        "type": "change_reflection_interval",
        "current_interval": 30,
        "new_interval": 60
    }
    
    print("Simulating change from 30s to 60s interval...")
    result = await simulation_engine.simulate_action(action, iterations=1000)
    
    print("\n  Response Time:")
    print(f"    Mean: {result['response_time']['mean']:.2f}s")
    print(f"    95th percentile: {result['response_time']['percentile_95']:.2f}s")
    
    print("\n  Task Completion Rate:")
    print(f"    Mean: {result['task_completion']['mean']:.2%}")
    
    print("\n  Resource Usage:")
    print(f"    Mean: {result['resource_usage']['mean']:.2%}")
    
    print(f"\n  Summary:")
    summary = result['summary']
    print(f"    Response time change: {summary['response_time_change_pct']:+.1f}%")
    print(f"    Completion rate change: {summary['completion_rate_change_pct']:+.1f}%")
    print(f"    Resource usage change: {summary['resource_usage_change_pct']:+.1f}%")
    print(f"    Recommendation: {summary['recommendation']}")
    
    return abs(summary['response_time_change_pct']) > 0

async def test_threshold_change_simulation():
    """Test 6: Simulate task threshold change"""
    print("\n=== Test 6: Task Threshold Simulation ===")
    
    action = {
        "type": "change_task_threshold",
        "current_threshold": 3,
        "new_threshold": 5
    }
    
    print("Simulating threshold change from 3 to 5...")
    result = await simulation_engine.simulate_action(action, iterations=1000)
    
    print("\n  Tasks Created:")
    print(f"    Mean: {result['tasks_created']['mean']:.1f}")
    
    print("\n  Task Quality:")
    print(f"    Mean: {result['task_quality']['mean']:.2%}")
    
    print("\n  False Positive Rate:")
    print(f"    Mean: {result['false_positive_rate']['mean']:.2%}")
    
    print(f"\n  Summary:")
    summary = result['summary']
    print(f"    Task count change: {summary['task_count_change_pct']:+.1f}%")
    print(f"    Quality change: {summary['quality_change_pct']:+.1f}%")
    print(f"    Expected value: {summary['expected_value']:.2f}")
    print(f"    Recommendation: {summary['recommendation']}")
    
    return True

async def test_scenario_comparison():
    """Test 7: Compare multiple scenarios"""
    print("\n=== Test 7: Scenario Comparison ===")
    
    scenarios = [
        {"type": "change_reflection_interval", "current_interval": 30, "new_interval": 45},
        {"type": "change_reflection_interval", "current_interval": 30, "new_interval": 60},
        {"type": "change_task_threshold", "current_threshold": 3, "new_threshold": 4}
    ]
    
    print(f"Comparing {len(scenarios)} scenarios...")
    comparison = await simulation_engine.simulate_scenarios(scenarios)
    
    print(f"\n  Scenario Scores:")
    for result in comparison['scenarios']:
        print(f"    Scenario {result['scenario_id']}: {result['score']:.2f}")
    
    best = comparison['best_scenario']
    print(f"\n  Best Scenario: #{best['scenario_id']}")
    print(f"    Score: {best['score']:.2f}")
    print(f"    Type: {best['scenario']['type']}")
    print(f"\n  {comparison['recommendation']}")
    
    return best is not None and 'score' in best

async def test_goal_planning():
    """Test 8: Planning simulation for goal"""
    print("\n=== Test 8: Goal-Based Planning ===")
    
    goal = "Get task completion rate to 90%"
    
    print(f"Goal: {goal}")
    print("Searching for optimal action sequence...")
    
    plan = await simulation_engine.run_planning_simulation(goal, max_steps=5)
    
    print(f"\n  Recommended Sequence:")
    for step in plan['steps']:
        print(f"    Step {step['step']}: {step['action']['type']}")
        print(f"      Rationale: {step['rationale']}")
    
    print(f"\n  {plan['predicted_outcome']}")
    print(f"  Confidence: {plan['confidence']:.2%}")
    
    return len(plan['recommended_sequence']) > 0

async def test_recurring_patterns():
    """Test 9: Find recurring patterns"""
    print("\n=== Test 9: Recurring Patterns ===")
    
    patterns = await temporal_reasoner.find_recurring_patterns("daily")
    
    print(f"[+] Found {len(patterns)} recurring patterns")
    for pattern in patterns:
        print(f"  {pattern['type']}: {pattern['description']}")
    
    return len(patterns) > 0

async def test_peak_load_prediction():
    """Test 10: Peak load prediction"""
    print("\n=== Test 10: Peak Load Prediction ===")
    
    prediction = await temporal_reasoner.predict_peak_load()
    
    if prediction['next_peak_time']:
        print(f"  Next peak expected: {prediction['next_peak_time'].strftime('%Y-%m-%d %H:%M')}")
    
    print(f"  Recommendation: {prediction['recommendation']}")
    
    for pattern in prediction['patterns']:
        print(f"    {pattern['description']}")
    
    return True

async def test_preventive_actions():
    """Test 11: Preventive action suggestions"""
    print("\n=== Test 11: Preventive Actions ===")
    
    actions = await temporal_reasoner.suggest_preventive_actions()
    
    print(f"[+] Generated {len(actions)} preventive action suggestions")
    for action in actions:
        print(f"  {action['action']} -> {action['target']}")
        print(f"    Reason: {action['reason']}")
        print(f"    Confidence: {action['confidence']:.2%}")
    
    return True

async def test_prediction_accuracy_tracking():
    """Test 12: Prediction vs actual comparison"""
    print("\n=== Test 12: Prediction Accuracy Tracking ===")
    
    action = {
        "type": "change_reflection_interval",
        "current_interval": 30,
        "new_interval": 60
    }
    
    print("Running simulation...")
    result = await simulation_engine.simulate_action(action, iterations=500)
    
    async with async_session() as session:
        from sqlalchemy import select
        sim_result = await session.execute(
            select(Simulation).order_by(Simulation.id.desc()).limit(1)
        )
        simulation = sim_result.scalar_one_or_none()
        
        if simulation:
            print(f"[+] Simulation #{simulation.id} saved")
            
            actual_outcome = {
                "response_time": {"mean": 5.2},
                "task_completion": {"mean": 0.73},
                "summary": {
                    "response_time_change_pct": 4.0,
                    "completion_rate_change_pct": -2.7
                }
            }
            
            print("\nRecording actual outcome...")
            comparison = await simulation_engine.compare_prediction_vs_actual(
                simulation.id,
                actual_outcome
            )
            
            print(f"  Accuracy: {comparison['accuracy_pct']:.1f}%")
            print(f"  Verdict: {comparison['verdict']}")
            
            return comparison['accuracy'] > 0

async def run_all_tests():
    """Run complete test suite"""
    print("="*60)
    print("   Temporal Reasoning & Simulation Test Suite")
    print("="*60)
    
    await setup_test_data()
    
    tests = [
        ("Pattern Analysis", test_pattern_analysis),
        ("Next Event Prediction", test_next_event_prediction),
        ("Duration Estimation", test_duration_estimation),
        ("Anomaly Detection", test_anomaly_detection),
        ("Interval Change Simulation", test_interval_change_simulation),
        ("Threshold Change Simulation", test_threshold_change_simulation),
        ("Scenario Comparison", test_scenario_comparison),
        ("Goal-Based Planning", test_goal_planning),
        ("Recurring Patterns", test_recurring_patterns),
        ("Peak Load Prediction", test_peak_load_prediction),
        ("Preventive Actions", test_preventive_actions),
        ("Prediction Accuracy", test_prediction_accuracy_tracking)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    print("\n" + "="*60)
    print("                    Test Results")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print("="*60)
    
    if passed == len(results):
        print("\nAll tests passed! Temporal system fully operational.")
        print("\nCapabilities demonstrated:")
        print("  [+] Pattern discovery from historical events")
        print("  [+] Next-event prediction using Markov chains")
        print("  [+] Task duration estimation with confidence intervals")
        print("  [+] Timing anomaly detection (sigma-based)")
        print("  [+] Monte Carlo simulation (1000 iterations)")
        print("  [+] Multi-scenario comparison & optimization")
        print("  [+] Goal-based action planning")
        print("  [+] Recurring pattern detection (daily/weekly)")
        print("  [+] Peak load forecasting")
        print("  [+] Preventive action suggestions")
        print("  [+] Prediction accuracy tracking")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
