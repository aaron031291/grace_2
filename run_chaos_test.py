"""
Chaos Test Runner
Runs complete diagnostic chaos test from beginning to end

Run: python run_chaos_test.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))


async def run_complete_chaos_test():
    """
    Complete chaos test with full diagnostics
    FROM BEGINNING TO END
    """
    
    print("\n" + "=" * 80)
    print("GRACE CHAOS ENGINEERING - COMPLETE DIAGNOSTIC TEST")
    print("=" * 80)
    print()
    
    # Step 1: Boot Grace Layer 1
    print("STEP 1: Booting Grace Layer 1")
    print("-" * 80)
    
    from backend.core import message_bus, immutable_log
    from backend.core.control_plane import control_plane
    
    try:
        # Start core
        await message_bus.start()
        print("[OK] Message Bus started")
        
        await immutable_log.start()
        print("[OK] Immutable Log started")
        
        # Start control plane (boots all kernels)
        await control_plane.start()
        print("[OK] Control plane started")
        
        status = control_plane.get_status()
        print(f"[OK] Kernels: {status['running_kernels']}/{status['total_kernels']} running")
        print()
    
    except Exception as e:
        print(f"[ERROR] Boot failed: {e}")
        return
    
    # Step 2: Start monitoring systems
    print("STEP 2: Starting Monitoring Systems")
    print("-" * 80)
    
    try:
        from backend.core.runtime_trigger_monitor import runtime_trigger_monitor
        await runtime_trigger_monitor.start()
        print("[OK] Runtime trigger monitor started")
        
        from backend.core.error_recognition_system import error_recognition_system
        await error_recognition_system.start()
        print(f"[OK] Error recognition started ({len(error_recognition_system.knowledge_base)} known signatures)")
        
        from backend.core.refactor_task_system import refactor_task_system
        await refactor_task_system.start()
        print(f"[OK] Refactor system started ({len(refactor_task_system.patterns)} patterns)")
        
        print()
    
    except Exception as e:
        print(f"[ERROR] Monitoring startup failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Run Chaos Test Suite
    print("STEP 3: Running Chaos Test Suite")
    print("-" * 80)
    
    from backend.chaos.chaos_suite import concurrent_chaos_runner
    
    report = await concurrent_chaos_runner.start_test_run()
    
    # Step 4: Display Results
    print("\n" + "=" * 80)
    print("TEST COMPLETE - FINAL RESULTS")
    print("=" * 80)
    print()
    print(f"Report File: {report['report_file']}")
    print()
    print("Summary:")
    print(f"  Total Waves: {concurrent_chaos_runner.total_waves_run}")
    print(f"  Scenarios Passed: {concurrent_chaos_runner.total_scenarios_passed}")
    print(f"  Scenarios Failed: {concurrent_chaos_runner.total_scenarios_failed}")
    print(f"  Success Rate: {concurrent_chaos_runner.total_scenarios_passed / max(concurrent_chaos_runner.total_scenarios_passed + concurrent_chaos_runner.total_scenarios_failed, 1) * 100:.1f}%")
    print()
    print(f"  Escalated: {report['summary']['escalated_incidents']}")
    print(f"  Diagnostic Dumps: {report['summary']['diagnostic_dumps']}")
    print()
    
    # Step 5: Show System State
    print("STEP 5: Final System State")
    print("-" * 80)
    
    final_status = control_plane.get_status()
    print(f"Control Plane: {final_status['system_state']}")
    print(f"Kernels: {final_status['running_kernels']}/{final_status['total_kernels']} running")
    print(f"Failed: {final_status['failed_kernels']}")
    print()
    
    # Error recognition stats
    er_stats = error_recognition_system.get_statistics()
    print("Error Recognition:")
    print(f"  Known Signatures: {er_stats['known_signatures']}")
    print(f"  Auto-Apply Enabled: {er_stats['auto_apply_enabled']}")
    print(f"  High Confidence: {er_stats['high_confidence_fixes']}")
    print()
    
    # Refactor stats
    refactor_stats = refactor_task_system.get_metrics()
    print("Refactor System:")
    print(f"  Active Tasks: {refactor_stats['active_tasks']}")
    print(f"  Completed: {refactor_stats['refactors_completed']}")
    print(f"  Patterns Learned: {refactor_stats['patterns_learned']}")
    print()
    
    print("=" * 80)
    print("[SUCCESS] CHAOS TEST COMPLETE")
    print("=" * 80)
    print()
    print("All diagnostics saved to logs/chaos/")
    print(f"Full report: {report['report_file']}")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(run_complete_chaos_test())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
