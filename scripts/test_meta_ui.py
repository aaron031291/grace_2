"""
Test script to generate sample meta-loop recommendations for UI testing
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.models import async_session
from backend.meta_loop_approval import approval_queue
from backend.meta_loop import MetaAnalysis
from datetime import datetime

async def create_sample_recommendations():
    """Create sample recommendations for testing the UI"""
    
    async with async_session() as session:
        # Create a meta analysis first
        analysis = MetaAnalysis(
            analysis_type="performance_threshold",
            subject="reflection_loop",
            findings="Reflection interval of 300s is too slow, missing real-time insights",
            recommendation="Reduce reflection interval to 120s for better responsiveness",
            confidence=0.85,
            applied=False
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        
        # Submit recommendations
        rec1_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="interval_adjustment",
            target="reflection_loop.check_interval",
            current_value=300,
            proposed_value=120,
            recommendation_text="Reduce reflection interval from 300s to 120s for better real-time insights",
            confidence=0.85,
            risk_level="low",
            payload={
                "component": "Reflection Loop",
                "predicted_impact": 35.5,
                "reasoning": "Current 5-minute interval causes delayed insights. Reducing to 2 minutes will improve real-time pattern detection while maintaining system stability."
            }
        )
        print(f"✅ Created recommendation {rec1_id}: Reflection interval adjustment")
        
        rec2_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="threshold_change",
            target="task_executor.priority_threshold",
            current_value=0.7,
            proposed_value=0.6,
            recommendation_text="Lower priority threshold to process more tasks",
            confidence=0.65,
            risk_level="medium",
            payload={
                "component": "Task Executor",
                "predicted_impact": 22.3,
                "reasoning": "Current threshold of 0.7 is filtering out potentially valuable tasks. Lowering to 0.6 will increase task processing by ~30% with acceptable quality trade-off."
            }
        )
        print(f"✅ Created recommendation {rec2_id}: Priority threshold adjustment")
        
        rec3_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="batch_size_optimization",
            target="knowledge_graph.batch_size",
            current_value=50,
            proposed_value=100,
            recommendation_text="Increase batch size for better throughput",
            confidence=0.90,
            risk_level="low",
            payload={
                "component": "Knowledge Graph",
                "predicted_impact": 45.8,
                "reasoning": "Memory analysis shows we have headroom. Doubling batch size from 50 to 100 will significantly improve ingestion throughput without memory issues."
            }
        )
        print(f"✅ Created recommendation {rec3_id}: Batch size optimization")
        
        rec4_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="timeout_adjustment",
            target="api_client.request_timeout",
            current_value=30,
            proposed_value=15,
            recommendation_text="Reduce API timeout to fail faster",
            confidence=0.55,
            risk_level="high",
            payload={
                "component": "API Client",
                "predicted_impact": 12.5,
                "reasoning": "30-second timeout is too long. Reducing to 15s will improve user experience for failed requests, but may cause false timeouts on slow networks."
            }
        )
        print(f"✅ Created recommendation {rec4_id}: Timeout adjustment (HIGH RISK)")
        
        print("\n🎉 Sample recommendations created! Visit http://localhost:5173 and navigate to Meta-Loop dashboard")
        print("   You should see 4 pending recommendations with different risk levels")

if __name__ == "__main__":
    asyncio.run(create_sample_recommendations())
