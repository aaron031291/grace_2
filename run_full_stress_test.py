"""
Complete Layer 1 Stress Test
Runs all 11 chaos scenarios with full diagnostics

The errors are TRIGGERED for auto-fix:
- Coding agent FIXES THE APIs (adds missing parameters)
- Does NOT remove data from calls
- Self-healing learns and saves fixes for instant replay
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))


async def run_full_stress_test():
    """Run complete stress test with all scenarios"""
    
    print("\n" + "=" * 80)
    print("LAYER 1 FULL STRESS TEST - ALL 11 SCENARIOS")
    print("=" * 80)
    print()
    print("This test:")
    print("  - Runs 11 concurrent chaos scenarios")
    print("  - Feeds ALL errors to self-healing & coding agent")
    print("  - Coding agent FIXES APIs (adds missing parameters)")
    print("  - Does NOT remove data from calls")
    print("  - Learns fixes for instant auto-fix next time")
    print()
    
    # Boot core
    print("=" * 80)
    print("PHASE 1: BOOT CORE SYSTEMS")
    print("=" * 80)
    
    from backend.core import message_bus, immutable_log
    from backend.core.control_plane import control_plane
    
    await message_bus.start()
    await immutable_log.start()
    await control_plane.start()
    
    status = control_plane.get_status()
    print(f"[OK] Kernels: {status['running_kernels']}/{status['total_kernels']} running")
    print()
    
    # Start monitoring
    print("=" * 80)
    print("PHASE 2: START MONITORING & SELF-HEALING")
    print("=" * 80)
    
    from backend.core.error_recognition_system import error_recognition_system
    from backend.core.runtime_trigger_monitor import runtime_trigger_monitor
    from backend.core.refactor_task_system import refactor_task_system
    from backend.core.snapshot_hygiene import snapshot_hygiene_manager
    
    await error_recognition_system.start()
    await runtime_trigger_monitor.start()
    await refactor_task_system.start()
    await snapshot_hygiene_manager.start()
    
    print(f"[OK] Error recognition: {len(error_recognition_system.knowledge_base)} known signatures")
    print(f"[OK] Runtime triggers: Monitoring")
    print(f"[OK] Refactor system: {len(refactor_task_system.patterns)} patterns")
    print(f"[OK] Snapshot hygiene: Hourly refresh")
    print()
    
    # Trigger current boot errors
    print("=" * 80)
    print("PHASE 3: FEED CURRENT BOOT ERRORS TO AUTO-FIX")
    print("=" * 80)
    print()
    
    # Error 1: immutable_log.append(subsystem=...) parameter missing
    print("[ERROR 1] coding_agent: ImmutableLog.append() missing 'subsystem' parameter")
    error1 = Exception("ImmutableLog.append() got an unexpected keyword argument 'subsystem'")
    
    incident1 = await error_recognition_system.handle_kernel_failure('coding_agent', error1)
    
    print(f"  [TRIGGER] Incident: {incident1}")
    print(f"  [TRIGGER] Signature: coding_agent_str_...")
    print(f"  [ACTION] Coding agent will FIX THE API:")
    print(f"           Add 'subsystem' parameter to immutable_log.append()")
    print(f"           NOT remove subsystem= from calls")
    print()
    
    # Error 2: async_session import missing
    print("[ERROR 2] governance: async_session import missing from backend.models")
    error2 = Exception("cannot import name 'async_session' from 'backend.models'")
    
    incident2 = await error_recognition_system.handle_kernel_failure('governance', error2)
    
    print(f"  [TRIGGER] Incident: {incident2}")
    print(f"  [TRIGGER] Signature: governance_str_...")
    print(f"  [ACTION] Coding agent will FIX THE EXPORT:")
    print(f"           Add async_session to backend/models/__init__.py")
    print(f"           NOT remove import from governance.py")
    print()
    
    # Check coding agent received tasks
    try:
        from backend.agents_core.elite_coding_agent import elite_coding_agent
        
        print("[CODING AGENT TASKS]")
        print(f"  Queue: {len(elite_coding_agent.task_queue)} tasks")
        print(f"  Active: {len(elite_coding_agent.active_tasks)}")
        
        if elite_coding_agent.task_queue:
            print()
            print("  Pending Analysis:")
            for task in elite_coding_agent.task_queue[:2]:
                print(f"    - {task.task_id}")
                print(f"      Type: {task.task_type.value}")
                print(f"      Priority: {task.priority}")
                desc_lines = task.description.split('\n')[:3]
                for line in desc_lines:
                    if line.strip():
                        print(f"      {line.strip()[:70]}...")
                print()
    except Exception as e:
        print(f"  [ERROR] Could not check coding agent: {e}")
    
    print()
    
    # Run chaos scenarios
    print("=" * 80)
    print("PHASE 4: RUN CHAOS SCENARIOS")
    print("=" * 80)
    print()
    
    from backend.chaos.chaos_suite import concurrent_chaos_runner
    
    print("[CHAOS] Starting concurrent multi-fault stress test...")
    print()
    
    report = await concurrent_chaos_runner.start_test_run()
    
    print()
    
    # Final summary
    print("=" * 80)
    print("STRESS TEST COMPLETE - FINAL SUMMARY")
    print("=" * 80)
    print()
    
    print("Boot Errors Triggered for Auto-Fix:")
    print(f"  - Error 1: immutable_log API → Coding agent will add 'subsystem' param")
    print(f"  - Error 2: models export → Coding agent will add async_session export")
    print()
    
    print("Chaos Test Results:")
    print(f"  Waves Run: {concurrent_chaos_runner.total_waves_run}")
    print(f"  Scenarios Passed: {concurrent_chaos_runner.total_scenarios_passed}")
    print(f"  Scenarios Failed: {concurrent_chaos_runner.total_scenarios_failed}")
    print(f"  Success Rate: {concurrent_chaos_runner.total_scenarios_passed / max(concurrent_chaos_runner.total_scenarios_passed + concurrent_chaos_runner.total_scenarios_failed, 1) * 100:.1f}%")
    print()
    
    print("Error Recognition:")
    er_stats = error_recognition_system.get_statistics()
    print(f"  Incidents Analyzed: {er_stats['total_incidents_analyzed']}")
    print(f"  Known Signatures: {er_stats['known_signatures']}")
    print(f"  Auto-Apply Ready: {er_stats['auto_apply_enabled']}")
    print()
    
    print("System State:")
    final_status = control_plane.get_status()
    print(f"  Kernels: {final_status['running_kernels']}/{final_status['total_kernels']} running")
    print(f"  Failed: {final_status['failed_kernels']}")
    print(f"  State: {final_status['system_state']}")
    print()
    
    print("Diagnostics Saved:")
    print(f"  Chaos Report: {report['report_file']}")
    print(f"  Incident Dumps: logs/chaos/<incident_id>/")
    print(f"  Coding Tasks: {len(elite_coding_agent.task_queue)} pending fixes")
    print()
    
    print("=" * 80)
    print("[SUCCESS] FULL STRESS TEST COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Coding agent will process 2 fix tasks")
    print("  2. APIs will be updated to accept the data")
    print("  3. Signatures saved to knowledge base")
    print("  4. Next boot: Instant auto-fix (<30s)")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(run_full_stress_test())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test interrupted")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
