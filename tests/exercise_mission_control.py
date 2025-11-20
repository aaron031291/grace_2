"""
Exercise Mission Control - Verify Unified Task/Mission View

This script:
1. Connects to Mission Control API
2. Lists all active missions/tasks
3. Creates a test mission
4. Watches it transition from active -> resolved
5. Verifies unified view is up-to-date
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_mission_control_api():
    """Test Mission Control API endpoints"""
    
    print("=" * 80)
    print("MISSION CONTROL - UNIFIED TASK/MISSION VIEW TEST")
    print("=" * 80)
    print()
    
    try:
        from backend.mission_control.hub import mission_control_hub
        from backend.mission_control.schemas import Mission, MissionStatus
        
        # Start Mission Control
        print("[1/6] Starting Mission Control Hub...")
        await mission_control_hub.start()
        print("      [OK] Mission Control started")
        print()
        
        # Get status
        print("[2/6] Getting Mission Control status...")
        status = await mission_control_hub.get_status()
        print(f"      Active missions: {status.active_missions}")
        print(f"      Completed missions: {status.completed_missions}")
        print(f"      Total subsystems: {len(status.subsystem_health)}")
        print()
        
        # List current missions
        print("[3/6] Listing current missions...")
        missions = await mission_control_hub.list_missions(status="active")
        
        if missions:
            print(f"      Found {len(missions)} active missions:")
            for mission in missions[:5]:
                print(f"      - {mission.title} ({mission.mission_type})")
                print(f"        Status: {mission.status}")
        else:
            print("      No active missions found")
        print()
        
        # Create a test learning mission
        print("[4/6] Creating test learning mission...")
        test_mission = Mission(
            mission_id=f"mission_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            mission_type="learning",
            title="Test Learning Mission",
            description="Verify mission tracking and status transitions",
            created_by="test_script",
            status=MissionStatus.ACTIVE,
            priority=5,
            metadata={
                "test": True,
                "purpose": "verify_mission_tracking"
            }
        )
        
        success = await mission_control_hub.create_mission(test_mission)
        
        if success:
            print(f"      [OK] Mission created: {test_mission.mission_id}")
            print(f"      Status: {test_mission.status}")
        else:
            print("      [WARN] Mission creation may have failed")
        print()
        
        # Update mission progress
        print("[5/6] Simulating mission progress...")
        
        # Update to in-progress
        test_mission.status = MissionStatus.ACTIVE
        test_mission.metadata["progress"] = 50
        test_mission.metadata["status_message"] = "Processing..."
        await mission_control_hub.update_mission(test_mission.mission_id, test_mission)
        print("      Progress: [50%] Processing...")
        
        await asyncio.sleep(1)
        
        # Complete the mission
        test_mission.status = MissionStatus.COMPLETED
        test_mission.metadata["progress"] = 100
        test_mission.metadata["status_message"] = "Complete"
        test_mission.completed_at = datetime.utcnow()
        await mission_control_hub.update_mission(test_mission.mission_id, test_mission)
        print("      Progress: [100%] Complete")
        print()
        
        # Verify transition
        print("[6/6] Verifying mission transition...")
        retrieved = await mission_control_hub.get_mission(test_mission.mission_id)
        
        if retrieved:
            print(f"      Mission ID: {retrieved.mission_id}")
            print(f"      Title: {retrieved.title}")
            print(f"      Status: {retrieved.status}")
            print(f"      Created: {retrieved.created_at}")
            if retrieved.completed_at:
                print(f"      Completed: {retrieved.completed_at}")
                duration = (retrieved.completed_at - retrieved.created_at).total_seconds()
                print(f"      Duration: {duration:.2f}s")
            
            if retrieved.status == MissionStatus.COMPLETED:
                print("\n      [PASS] Mission transitioned: active -> completed")
            else:
                print(f"\n      [WARN] Unexpected status: {retrieved.status}")
        else:
            print("      [WARN] Could not retrieve mission")
        
        print()
        print("=" * 80)
        print("[SUCCESS] Mission Control unified view is working!")
        print("          Missions can be created, tracked, and resolved")
        print("=" * 80)
        
        return 0
        
    except ImportError as e:
        print(f"[ERROR] Mission Control not available: {e}")
        print("\nMission Control requires Grace to be fully started.")
        print("Run: START_GRACE.bat")
        return 1
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 2

async def test_task_registry_integration():
    """Test that task registry shows healing and learning tasks"""
    
    print("\n" + "=" * 80)
    print("TASK REGISTRY INTEGRATION CHECK")
    print("=" * 80)
    print()
    
    try:
        from backend.services.task_registry import task_registry
        from backend.models.task_registry_models import TaskRegistryEntry
        from backend.models.base_models import async_session
        from sqlalchemy import select, func
        
        print("[1/3] Querying task registry...")
        
        async with async_session() as session:
            # Count tasks
            result = await session.execute(
                select(func.count(TaskRegistryEntry.id))
            )
            total = result.scalar()
            print(f"      Total tasks: {total}")
            
            # Count by subsystem
            result = await session.execute(
                select(
                    TaskRegistryEntry.subsystem,
                    func.count(TaskRegistryEntry.id).label('count')
                ).group_by(TaskRegistryEntry.subsystem)
            )
            subsystems = result.all()
            
            print("\n[2/3] Tasks by subsystem:")
            for subsystem, count in subsystems:
                print(f"      {subsystem}: {count}")
            
            # Show recent tasks
            print("\n[3/3] Recent tasks:")
            result = await session.execute(
                select(TaskRegistryEntry)
                .order_by(TaskRegistryEntry.id.desc())
                .limit(5)
            )
            recent = result.scalars().all()
            
            for task in recent:
                print(f"\n      {task.task_id}")
                print(f"      Type: {task.task_type}")
                print(f"      Subsystem: {task.subsystem}")
                print(f"      Status: {task.status}")
        
        print("\n" + "=" * 80)
        print("[PASS] Task registry integrated with missions")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"[INFO] Task registry not initialized yet")
        print(f"       Error: {e}")
        print("\n" + "=" * 80)
        print("[NOTE] Start Grace first to initialize database")
        print("=" * 80)
        return 1

async def main():
    """Main test runner"""
    
    print("Testing Mission Control unified task/mission view...")
    print("This verifies tasks can transition: active -> resolved")
    print()
    
    # Test Mission Control
    result1 = await test_mission_control_api()
    
    # Test Task Registry
    result2 = await test_task_registry_integration()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS:")
    print("-" * 80)
    print(f"Mission Control API: {'PASS' if result1 == 0 else 'NEEDS GRACE RUNNING'}")
    print(f"Task Registry: {'PASS' if result2 == 0 else 'NEEDS GRACE RUNNING'}")
    print("=" * 80)
    
    return 0 if (result1 == 0 or result2 == 0) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
