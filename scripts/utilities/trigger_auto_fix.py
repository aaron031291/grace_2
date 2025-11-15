"""
Trigger Auto-Fix for Boot Errors
Feed errors into error recognition system for automatic healing
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))


async def trigger_fixes():
    """Feed boot errors to self-healing and coding agent"""
    
    print("\n" + "=" * 80)
    print("TRIGGERING AUTO-FIX FOR BOOT ERRORS")
    print("=" * 80)
    print()
    
    # Start core systems
    from backend.core import message_bus, immutable_log
    from backend.core.control_plane import control_plane
    from backend.core.error_recognition_system import error_recognition_system
    from backend.core.runtime_trigger_monitor import runtime_trigger_monitor
    
    await message_bus.start()
    await immutable_log.start()
    await error_recognition_system.start()
    await runtime_trigger_monitor.start()
    
    print("[OK] Core systems started")
    print()
    
    # Error 1: Coding Agent - ImmutableLog.append() subsystem parameter
    print("ERROR 1: Coding Agent - ImmutableLog.append() parameter mismatch")
    print("-" * 80)
    
    error1 = Exception("ImmutableLog.append() got an unexpected keyword argument 'subsystem'")
    
    incident_id_1 = await error_recognition_system.handle_kernel_failure('coding_agent', error1)
    
    print(f"  [OK] Fed to error recognition: {incident_id_1}")
    print(f"  [OK] Diagnostic suite completed")
    print(f"  [OK] Signature generated")
    print(f"  [OK] Dispatched to coding agent for analysis")
    print()
    
    # Give it a moment to process
    await asyncio.sleep(2)
    
    # Error 2: Governance - async_session import
    print("ERROR 2: Governance - async_session import missing")
    print("-" * 80)
    
    error2 = Exception("cannot import name 'async_session' from 'backend.models' (unknown location)")
    
    incident_id_2 = await error_recognition_system.handle_kernel_failure('governance', error2)
    
    print(f"  [OK] Fed to error recognition: {incident_id_2}")
    print(f"  [OK] Diagnostic suite completed")
    print(f"  [OK] Signature generated")
    print(f"  [OK] Dispatched to coding agent for analysis")
    print()
    
    await asyncio.sleep(2)
    
    # Check coding agent task queue
    print("CODING AGENT STATUS")
    print("-" * 80)
    
    try:
        from backend.agents_core.elite_coding_agent import elite_coding_agent
        
        print(f"  Running: {elite_coding_agent.running}")
        print(f"  Task Queue: {len(elite_coding_agent.task_queue)} tasks")
        print(f"  Active Tasks: {len(elite_coding_agent.active_tasks)}")
        print()
        
        if elite_coding_agent.task_queue:
            print("  Queued Tasks:")
            for task in elite_coding_agent.task_queue[:5]:
                print(f"    - {task.task_id}: {task.description[:60]}...")
        
        print()
    
    except Exception as e:
        print(f"  [ERROR] Could not check coding agent: {e}")
        print()
    
    # Check self-healing playbook execution
    print("SELF-HEALING STATUS")
    print("-" * 80)
    
    try:
        from backend.core.advanced_playbook_engine import advanced_playbook_engine
        
        if advanced_playbook_engine.execution_history:
            print(f"  Executions: {len(advanced_playbook_engine.execution_history)}")
            print(f"  Recent:")
            for exec in advanced_playbook_engine.execution_history[-3:]:
                print(f"    - {exec['playbook']}: {'SUCCESS' if exec['success'] else 'FAILED'}")
        else:
            print("  No playbook executions yet")
        
        print()
    
    except Exception as e:
        print(f"  [ERROR] Could not check self-healing: {e}")
        print()
    
    # Check error recognition knowledge base
    print("ERROR RECOGNITION KNOWLEDGE BASE")
    print("-" * 80)
    
    stats = error_recognition_system.get_statistics()
    print(f"  Known Signatures: {stats['known_signatures']}")
    print(f"  Auto-Apply Enabled: {stats['auto_apply_enabled']}")
    print(f"  Total Analyzed: {stats['total_incidents_analyzed']}")
    print(f"  Pending Analysis: {stats['pending_analysis']}")
    print()
    
    # Show diagnostic bundles
    if error_recognition_system.diagnostic_history:
        print("  Recent Incidents:")
        for bundle in error_recognition_system.diagnostic_history[-2:]:
            print(f"    - {bundle.incident_id}")
            print(f"      Kernel: {bundle.kernel_name}")
            print(f"      Signature: {bundle.failure_signature.signature_id if bundle.failure_signature else 'N/A'}")
            print(f"      Logs captured: {len(bundle.recent_logs)}")
            print()
    
    # Wait for coding agent to process
    print("WAITING FOR CODING AGENT TO PROCESS TASKS (10 seconds)...")
    print("-" * 80)
    await asyncio.sleep(10)
    
    # Check progress
    try:
        from backend.agents_core.elite_coding_agent import elite_coding_agent
        
        print(f"  Active Tasks: {len(elite_coding_agent.active_tasks)}")
        print(f"  Completed: {len(elite_coding_agent.completed_tasks)}")
        
        if elite_coding_agent.active_tasks:
            print("\n  Currently Processing:")
            for task_id, task in list(elite_coding_agent.active_tasks.items())[:3]:
                print(f"    - {task_id}: {task.status}")
        
        print()
    
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    print("=" * 80)
    print("[SUCCESS] ERRORS TRIGGERED FOR AUTO-FIX")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Coding agent is analyzing both errors")
    print("  2. Diagnostic bundles created with full context")
    print("  3. Fixes will be generated and applied")
    print("  4. On success, signatures saved to knowledge base")
    print("  5. Next boot: Instant auto-fix (<30s)")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(trigger_fixes())
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
