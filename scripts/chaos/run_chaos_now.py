"""
Quick Chaos Test Runner
Runs a single wave of chaos scenarios
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    print("=" * 80)
    print("GRACE CHAOS TEST - SINGLE WAVE")
    print("=" * 80)
    print()
    
    # Boot core
    print("[1/4] Booting core systems...")
    from backend.core import message_bus, immutable_log, control_plane
    
    await message_bus.start()
    await immutable_log.start()
    await control_plane.start()
    
    status = control_plane.get_status()
    print(f"  [OK] {status['running_kernels']}/{status['total_kernels']} kernels running")
    print()
    
    # Start chaos suite
    print("[2/4] Starting chaos suite...")
    from backend.chaos.chaos_suite import concurrent_chaos_runner
    
    print(f"  [OK] Concurrent chaos runner initialized")
    print()
    
    # Run test
    print("[3/4] Running chaos test (escalating waves)...")
    print()
    
    try:
        report = await concurrent_chaos_runner.start_test_run()
        print()
        print("  [OK] Test completed")
        print(f"  Report: {report.get('report_file', 'N/A')}")
    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        report = {}
    
    print()
    
    # Results
    print("[4/4] Results:")
    final_status = control_plane.get_status()
    print(f"  Kernels running: {final_status['running_kernels']}/{final_status['total_kernels']}")
    print(f"  Failed kernels: {final_status['failed_kernels']}")
    print(f"  System state: {final_status['system_state']}")
    print()
    
    # Test stats
    print(f"  Waves run: {concurrent_chaos_runner.total_waves_run}")
    print(f"  Scenarios passed: {concurrent_chaos_runner.total_scenarios_passed}")
    print(f"  Scenarios failed: {concurrent_chaos_runner.total_scenarios_failed}")
    
    if concurrent_chaos_runner.chaos_ledger_file.exists():
        print(f"  Ledger: {concurrent_chaos_runner.chaos_ledger_file}")
    
    print()
    print("=" * 80)
    print("CHAOS TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
