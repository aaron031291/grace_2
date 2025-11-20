"""
Demo: Show Learning Progress in Unified Task Registry

This demonstrates how learning tasks track progress and show
what Grace is currently learning with completion percentages.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.learning_systems.learning_task_integration import learning_task_integration

async def demo_learning_with_progress():
    """Demonstrate learning task with progress tracking"""
    
    print("=" * 80)
    print("DEMO: LEARNING PROGRESS IN UNIFIED TASK REGISTRY")
    print("=" * 80)
    print()
    
    # 1. Register a training job
    print("[1/4] Registering ML training job...")
    task_id = await learning_task_integration.register_training_job(
        model_name="anomaly_detector",
        dataset_size=1000,
        metadata={
            "epochs_planned": 100,
            "batch_size": 32
        }
    )
    
    if task_id:
        print(f"      ✓ Task registered: {task_id}")
    else:
        print("      ✗ Task registry not available (Grace not started)")
        print("      This demo requires Grace to be running")
        return 1
    
    print()
    
    # 2. Simulate training progress
    print("[2/4] Simulating training progress...")
    
    epochs = [10, 25, 50, 75, 100]
    for epoch in epochs:
        progress = (epoch / 100) * 100
        
        await learning_task_integration.update_learning_progress(
            task_id=task_id,
            progress_percent=progress,
            status_message=f"Training epoch {epoch}/100",
            metadata={
                "current_epoch": epoch,
                "current_accuracy": 0.5 + (epoch / 100) * 0.45  # Simulated improvement
            }
        )
        
        print(f"      Progress: [{progress:>5.1f}%] Epoch {epoch}/100")
        await asyncio.sleep(0.5)
    
    print()
    
    # 3. Get current learning activities
    print("[3/4] Querying active learning tasks...")
    active_tasks = await learning_task_integration.get_active_learning_tasks()
    
    if active_tasks:
        print(f"      Found {len(active_tasks)} active learning task(s):")
        for task in active_tasks:
            print(f"\n      → {task['title']}")
            print(f"        Type: {task['type']}")
            print(f"        Progress: {task['progress_percent']:.1f}%")
            print(f"        Status: {task['status_message']}")
    else:
        print("      No active tasks found")
    
    print()
    
    # 4. Complete the task
    print("[4/4] Completing training task...")
    await learning_task_integration.complete_learning_task(
        task_id=task_id,
        success=True,
        result={
            "final_accuracy": 0.95,
            "total_epochs": 100,
            "training_time": 2.5,
            "model_size_mb": 12.3
        }
    )
    print("      ✓ Task completed")
    
    print()
    print("=" * 80)
    print("DEMO COMPLETE")
    print()
    print("Now run: python tests/show_unified_task_evidence.py")
    print("You should see this training job in the completed learning tasks!")
    print("=" * 80)
    
    return 0

async def main():
    """Main demo runner"""
    try:
        return await demo_learning_with_progress()
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
