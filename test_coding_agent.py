"""Test if coding agent is running and processing tasks"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from backend.core import control_plane
    from backend.agents_core.elite_coding_agent import elite_coding_agent
    
    print("[1/3] Booting control plane...")
    await control_plane.start()
    
    print()
    print("[2/3] Checking coding agent status...")
    print(f"  Running: {elite_coding_agent.running}")
    print(f"  Task Queue: {len(elite_coding_agent.task_queue)} tasks")
    print(f"  Active Tasks: {len(elite_coding_agent.active_tasks)} tasks")
    print()
    
    if elite_coding_agent.task_queue:
        print("[3/3] Tasks in queue:")
        for i, task in enumerate(elite_coding_agent.task_queue[:5]):
            print(f"  {i+1}. {task.task_id}")
            print(f"     Type: {task.task_type.value}")
            print(f"     Desc: {task.description[:60]}...")
            print(f"     Priority: {task.priority}")
    
    # Wait to see if tasks get processed
    print()
    print("[WAIT] Waiting 10s to see if tasks get processed...")
    await asyncio.sleep(10)
    
    print(f"  Task Queue After Wait: {len(elite_coding_agent.task_queue)} tasks")
    print(f"  Completed Tasks: {len(elite_coding_agent.completed_tasks)} tasks")
    
    if elite_coding_agent.completed_tasks:
        print()
        print("[SUCCESS] Coding agent IS processing tasks!")
        for task in elite_coding_agent.completed_tasks[:3]:
            print(f"  - {task.task_id}: {task.status}")
    else:
        print()
        print("[ISSUE] Coding agent not processing tasks")
        print(f"  Running flag: {elite_coding_agent.running}")
        print(f"  Has task loop: {hasattr(elite_coding_agent, '_task_processing_loop')}")


if __name__ == '__main__':
    asyncio.run(main())
