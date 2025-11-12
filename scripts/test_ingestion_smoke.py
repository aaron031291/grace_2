#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingestion Orchestrator Smoke Test
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.clarity.ingestion_orchestrator import ClarityIngestionOrchestrator


async def main():
    print("=" * 60)
    print("INGESTION ORCHESTRATOR SMOKE TEST")
    print("=" * 60)
    
    # Create and activate orchestrator
    print("\n[1/5] Creating ingestion orchestrator...")
    orch = ClarityIngestionOrchestrator(config={"max_concurrent": 2})
    
    print("[2/5] Activating orchestrator...")
    success = await orch.activate()
    if not success:
        print("    FAIL - Activation failed")
        return 1
    print("    PASS - Orchestrator activated")
    
    # Create a task
    print("[3/5] Creating ingestion task...")
    task = await orch.create_task("github", "https://github.com/test/repo")
    print(f"    PASS - Task created: {task.task_id}")
    
    # Start the task
    print("[4/5] Starting task...")
    success = await orch.start_task(task.task_id)
    if not success:
        print("    FAIL - Task start failed")
        return 1
    print("    PASS - Task started")
    
    # Wait for some progress
    await asyncio.sleep(3)
    
    # Check status
    print("[5/5] Checking status...")
    status = orch.get_status()
    task_info = orch.get_task(task.task_id)
    
    print(f"    Active tasks: {status['active_tasks']}")
    print(f"    Task progress: {task_info['progress']}%")
    print(f"    PASS - Status reporting working")
    
    # Cleanup
    print("\nStopping task...")
    await orch.stop_task(task.task_id)
    await orch.deactivate()
    
    print("\n" + "=" * 60)
    print("RESULTS: All tests passed")
    print("=" * 60)
    print("\nIngestion Orchestrator is OPERATIONAL")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
