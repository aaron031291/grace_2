"""
Show Evidence From Unified Task Registry

This script queries the unified task registry to show:
1. Self-healing incidents registered as tasks
2. Learning activities registered as tasks
3. Combined view of all autonomous activities
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

async def query_task_registry():
    """Query the unified task registry for all tasks"""
    try:
        from backend.models.task_registry_models import TaskRegistryEntry
        from backend.models.base_models import async_session
        from sqlalchemy import select, func
        
        print("=" * 80)
        print("UNIFIED TASK REGISTRY - EVIDENCE REPORT")
        print("=" * 80)
        print()
        
        async with async_session() as session:
            # 1. Count total tasks
            print("[1/5] Querying task registry database...")
            result = await session.execute(
                select(func.count(TaskRegistryEntry.id))
            )
            total_tasks = result.scalar()
            print(f"      Total tasks registered: {total_tasks}")
            print()
            
            # 2. Break down by subsystem
            print("[2/5] Tasks by subsystem:")
            print("-" * 80)
            
            result = await session.execute(
                select(
                    TaskRegistryEntry.subsystem,
                    func.count(TaskRegistryEntry.id).label('count')
                ).group_by(TaskRegistryEntry.subsystem)
            )
            subsystems = result.all()
            
            for subsystem, count in subsystems:
                print(f"  {subsystem}: {count} tasks")
            print()
            
            # 3. Self-healing tasks
            print("[3/5] Self-Healing Incidents:")
            print("-" * 80)
            
            result = await session.execute(
                select(TaskRegistryEntry)
                .where(TaskRegistryEntry.subsystem == 'self_healing')
                .order_by(TaskRegistryEntry.id.desc())
                .limit(5)
            )
            healing_tasks = result.scalars().all()
            
            if healing_tasks:
                for task in healing_tasks:
                    print(f"\n  Task ID: {task.task_id}")
                    print(f"  Title: {task.title}")
                    print(f"  Status: {task.status}")
                    if task.started_at:
                        print(f"  Started: {task.started_at}")
                    if task.completed_at:
                        print(f"  Completed: {task.completed_at}")
                        if task.duration_seconds:
                            print(f"  Duration: {task.duration_seconds:.3f}s")
            else:
                print("  No self-healing tasks found in registry yet")
            print()
            
            # 4. Learning tasks with progress
            print("[4/5] Current Learning Activities:")
            print("-" * 80)
            
            # Get active learning tasks
            result = await session.execute(
                select(TaskRegistryEntry)
                .where(
                    TaskRegistryEntry.subsystem == 'learning',
                    TaskRegistryEntry.status == 'active'
                )
                .order_by(TaskRegistryEntry.started_at.desc())
            )
            active_learning = result.scalars().all()
            
            if active_learning:
                print(f"\n  🎓 Currently Learning ({len(active_learning)} active):")
                for task in active_learning:
                    print(f"\n  → {task.title}")
                    print(f"    Type: {task.task_type}")
                    
                    # Extract progress from metadata
                    if task.task_metadata:
                        progress = task.task_metadata.get('progress_percent', 0)
                        status_msg = task.task_metadata.get('status_message', 'In progress')
                        print(f"    Progress: [{progress:.1f}%] {status_msg}")
                    
                    if task.started_at:
                        elapsed = (datetime.utcnow() - task.started_at.replace(tzinfo=None)).total_seconds()
                        print(f"    Running for: {elapsed:.1f}s")
            else:
                print("  No active learning tasks at the moment")
            
            # Show recent completed learning
            result = await session.execute(
                select(TaskRegistryEntry)
                .where(
                    TaskRegistryEntry.subsystem == 'learning',
                    TaskRegistryEntry.status == 'completed'
                )
                .order_by(TaskRegistryEntry.completed_at.desc())
                .limit(3)
            )
            completed_learning = result.scalars().all()
            
            if completed_learning:
                print(f"\n  ✅ Recently Completed:")
                for task in completed_learning:
                    print(f"  → {task.title} ({task.task_type})")
                    if task.duration_seconds:
                        print(f"    Duration: {task.duration_seconds:.1f}s")
            print()
            
            # 5. Summary statistics
            print("[5/5] SUMMARY:")
            print("-" * 80)
            
            # Count by status
            result = await session.execute(
                select(
                    TaskRegistryEntry.status,
                    func.count(TaskRegistryEntry.id).label('count')
                ).group_by(TaskRegistryEntry.status)
            )
            status_counts = result.all()
            
            print("\nTasks by status:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
            
            # Count completed tasks
            result = await session.execute(
                select(func.count(TaskRegistryEntry.id))
                .where(TaskRegistryEntry.status == 'completed')
            )
            completed_count = result.scalar()
            
            # Average duration
            result = await session.execute(
                select(func.avg(TaskRegistryEntry.duration_seconds))
                .where(TaskRegistryEntry.duration_seconds.isnot(None))
            )
            avg_duration = result.scalar()
            
            print(f"\nCompleted tasks: {completed_count}")
            if avg_duration:
                print(f"Average duration: {avg_duration:.3f} seconds")
            
            print()
            print("=" * 80)
            
            # Verdict
            if total_tasks > 0:
                healing_count = sum(count for sub, count in subsystems if sub == 'self_healing')
                learning_count = sum(count for sub, count in subsystems if sub == 'learning')
                
                evidence = []
                if healing_count > 0:
                    evidence.append(f"{healing_count} self-healing incidents")
                if learning_count > 0:
                    evidence.append(f"{learning_count} learning activities")
                
                print("[PASS] UNIFIED TASK REGISTRY IS TRACKING!")
                print(f"       Evidence: {', '.join(evidence) if evidence else f'{total_tasks} total tasks'}")
                print("=" * 80)
                return 0
            else:
                print("[INFO] Task registry exists but no tasks registered yet")
                print("       Run: python tests/trigger_real_healing.py to create tasks")
                print("=" * 80)
                return 1
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        print("[NOTE] Task registry database may not be initialized yet")
        print("       This is normal if Grace hasn't been started")
        print("=" * 80)
        return 2

def main():
    return asyncio.run(query_task_registry())

if __name__ == "__main__":
    sys.exit(main())
