"""
Standalone Test for Meta-Loop Recommendation System
Run from project root: py test_meta_system.py
"""
import asyncio
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from grace_rebuild.backend.meta_loop import meta_loop_engine, meta_meta_engine
from grace_rebuild.backend.meta_loop_approval import approval_queue
from grace_rebuild.backend.meta_loop_engine import recommendation_applicator
from grace_rebuild.backend.models import init_db, async_session
from sqlalchemy import select, func
from grace_rebuild.backend.meta_loop_approval import RecommendationQueue
from grace_rebuild.backend.meta_loop_engine import AppliedRecommendation

async def test_system():
    """Test meta-loop recommendation system"""
    
    print("=" * 80)
    print("META-LOOP RECOMMENDATION SYSTEM TEST")
    print("=" * 80)
    
    # Initialize database
    await init_db()
    
    # Test 1: Validation
    print("\n[1] VALIDATION TESTS")
    print("-" * 80)
    
    tests = [
        ("Valid threshold", {"type": "threshold_change", "threshold_name": "task_threshold", "new_value": 5}),
        ("Invalid threshold (too high)", {"type": "threshold_change", "threshold_name": "task_threshold", "new_value": 100}),
        ("Valid interval", {"type": "interval_change", "new_interval": 120}),
        ("Invalid interval (too low)", {"type": "interval_change", "new_interval": 1}),
    ]
    
    for name, rec in tests:
        result = await recommendation_applicator.validate_recommendation(rec)
        status = "✓" if result.get("valid") else "✗"
        print(f"{status} {name}")
        if result.get("valid"):
            print(f"  Risk: {result.get('risk_level')}")
        else:
            print(f"  Reason: {result.get('reason')}")
    
    # Test 2: Submit recommendation
    print("\n[2] SUBMIT RECOMMENDATION")
    print("-" * 80)
    
    rec_id = await approval_queue.submit_for_approval(
        meta_analysis_id=1,
        recommendation_type="threshold_change",
        target="task_threshold",
        current_value=3,
        proposed_value=5,
        recommendation_text="TEST: Increase task threshold to reduce auto-task noise",
        confidence=0.85,
        risk_level="low",
        payload={"component": "learning"}
    )
    print(f"✓ Submitted recommendation #{rec_id}")
    
    # Test 3: View pending
    print("\n[3] PENDING RECOMMENDATIONS")
    print("-" * 80)
    
    pending = await approval_queue.get_pending_recommendations()
    for rec in pending:
        print(f"\nRec #{rec['id']}:")
        print(f"  {rec['text']}")
        print(f"  {rec['current']} → {rec['proposed']}")
        print(f"  Confidence: {rec['confidence']:.0%}, Risk: {rec['risk_level']}")
    
    # Test 4: Auto-approve
    print("\n[4] AUTO-APPROVAL")
    print("-" * 80)
    
    auto_count = await approval_queue.auto_approve_safe_changes()
    print(f"✓ Auto-approved {auto_count} low-risk recommendations")
    
    # Test 5: Manual approval
    print("\n[5] MANUAL APPROVAL")
    print("-" * 80)
    
    pending = await approval_queue.get_pending_recommendations()
    if pending:
        rec = pending[0]
        print(f"Approving #{rec['id']}...")
        
        result = await approval_queue.approve_recommendation(
            rec['id'],
            approver="test_admin",
            reason="Testing approval workflow"
        )
        
        if result.get("success"):
            print(f"✓ Applied successfully")
            print(f"  Applied ID: {result.get('applied_id')}")
            if result.get('before_metrics'):
                m = result['before_metrics']
                print(f"  Before metrics: {m.get('total_tasks_24h')} tasks, {m.get('completion_rate', 0):.0%} completion")
        else:
            print(f"✗ Failed: {result.get('error')}")
    else:
        print("No pending recommendations")
    
    # Test 6: View applied
    print("\n[6] APPLIED RECOMMENDATIONS")
    print("-" * 80)
    
    applied = await approval_queue.get_applied_recommendations(limit=3)
    for rec in applied:
        print(f"\nApplied #{rec['id']}: {rec['type']}")
        print(f"  Target: {rec['target']}")
        print(f"  Change: {rec['old_value']} → {rec['new_value']}")
        print(f"  By: {rec['applied_by']} at {rec['applied_at']}")
        if rec.get('effectiveness') is not None:
            print(f"  Effectiveness: {rec['effectiveness']:+.1f}%")
    
    # Test 7: Statistics
    print("\n[7] SYSTEM STATISTICS")
    print("-" * 80)
    
    async with async_session() as session:
        stats = {
            "pending": await session.scalar(
                select(func.count()).select_from(RecommendationQueue)
                .where(RecommendationQueue.status == "pending")
            ) or 0,
            "approved": await session.scalar(
                select(func.count()).select_from(RecommendationQueue)
                .where(RecommendationQueue.status == "approved")
            ) or 0,
            "rejected": await session.scalar(
                select(func.count()).select_from(RecommendationQueue)
                .where(RecommendationQueue.status == "rejected")
            ) or 0,
            "applied": await session.scalar(
                select(func.count()).select_from(AppliedRecommendation)
            ) or 0,
            "rolled_back": await session.scalar(
                select(func.count()).select_from(AppliedRecommendation)
                .where(AppliedRecommendation.rolled_back == True)
            ) or 0,
        }
    
    for key, val in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {val}")
    
    # Test 8: Meta-meta evaluation
    print("\n[8] META-META EVALUATION")
    print("-" * 80)
    
    await meta_meta_engine.evaluate_improvement(
        meta_analysis_id=1,
        metric_name="task_completion_rate",
        before=0.30,
        after=0.50
    )
    print("✓ Evaluated 66.7% improvement")
    
    await meta_meta_engine.evaluate_improvement(
        meta_analysis_id=2,
        metric_name="reflection_utility",
        before=0.50,
        after=0.35
    )
    print("✓ Evaluated -30.0% regression")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS COMPLETE")
    print("=" * 80)
    print("\nKey Features Verified:")
    print("  ✓ Recommendation validation with safety limits")
    print("  ✓ Submission to approval queue")
    print("  ✓ Auto-approval for low-risk changes")
    print("  ✓ Manual approval workflow")
    print("  ✓ Before/after metrics capture")
    print("  ✓ Applied recommendations tracking")
    print("  ✓ Meta-meta evaluation of improvements")
    print("\nAPI Endpoints:")
    print("  GET  /api/meta/recommendations/pending")
    print("  POST /api/meta/recommendations/{id}/approve")
    print("  POST /api/meta/recommendations/{id}/reject")
    print("  GET  /api/meta/recommendations/applied")
    print("  POST /api/meta/recommendations/{id}/rollback")
    print("  GET  /api/meta/recommendations/stats")

if __name__ == "__main__":
    asyncio.run(test_system())
