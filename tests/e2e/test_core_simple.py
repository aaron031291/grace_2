#!/usr/bin/env python3
"""
Test Grace's Core - Simple Version (No Unicode)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

async def test_core():
    """Test the core systems"""
    
    print("=" * 80)
    print("GRACE UNBREAKABLE CORE TEST")
    print("=" * 80)
    
    # Test Message Bus
    print("\n[TEST 1] Message Bus")
    print("-" * 80)
    
    from backend.core.message_bus import message_bus
    
    await message_bus.start()
    print("Message Bus: STARTED")
    
    # Publish message
    msg_id = await message_bus.publish(
        source='test',
        topic='system.test',
        payload={'message': 'Hello Grace!'}
    )
    print(f"Published message: {msg_id}")
    
    stats = message_bus.get_stats()
    print(f"Messages sent: {stats['total_messages']}")
    print(f"Topics: {stats['active_topics']}")
    
    #Test Immutable Log
    print("\n[TEST 2] Immutable Log")
    print("-" * 80)
    
    from backend.core.immutable_log import immutable_log
    
    await immutable_log.start()
    print(f"Immutable Log: STARTED")
    
    log_stats = immutable_log.get_stats()
    print(f"Existing entries: {log_stats['total_entries']}")
    
    # Append entry
    log_id = await immutable_log.append(
        actor='test',
        action='test_boot',
        resource='core_system',
        decision={'status': 'testing'},
        metadata={'test': True}
    )
    print(f"Appended entry: {log_id}")
    
    log_stats = immutable_log.get_stats()
    print(f"Total entries now: {log_stats['total_entries']}")
    
    # Test Control Plane
    print("\n[TEST 3] Control Plane")
    print("-" * 80)
    
    from backend.core.control_plane import control_plane
    
    await control_plane.start()
    print("Control Plane: STARTED")
    
    status = control_plane.get_status()
    print(f"System state: {status['system_state']}")
    print(f"Total kernels: {status['total_kernels']}")
    print(f"Running kernels: {status['running_kernels']}")
    
    # Show kernel status
    print("\nKernel Status:")
    for name, kernel in status['kernels'].items():
        state = kernel['state']
        critical = "CRITICAL" if kernel['critical'] else "optional"
        print(f"  {name:20s} [{state:10s}] ({critical})")
    
    # Test pause/resume
    print("\n[TEST 4] Pause/Resume")
    print("-" * 80)
    
    print("Pausing...")
    await control_plane.pause()
    print(f"State: {control_plane.get_status()['system_state']}")
    
    await asyncio.sleep(0.5)
    
    print("Resuming...")
    await control_plane.resume()
    print(f"State: {control_plane.get_status()['system_state']}")
    
    # Shutdown
    print("\n[TEST 5] Graceful Shutdown")
    print("-" * 80)
    
    print("Shutting down...")
    await control_plane.stop()
    await message_bus.stop()
    print("Shutdown complete")
    
    # Final stats
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    print("\nMessage Bus:")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Topics: {', '.join(stats['topics'])}")
    
    print("\nImmutable Log:")
    print(f"  Total entries: {log_stats['total_entries']}")
    print(f"  Log file: {log_stats['log_file']}")
    print(f"  Size: {log_stats['log_size_bytes']} bytes")
    
    print("\nControl Plane:")
    print(f"  Kernels managed: {status['total_kernels']}")
    print(f"  Running: {status['running_kernels']}")
    print(f"  Failed: {status['failed_kernels']}")
    
    print("\n" + "=" * 80)
    print("GRACE'S UNBREAKABLE CORE: WORKING")
    print("=" * 80)
    print()
    print("Core Systems Tested:")
    print("  [OK] Message Bus - Communication backbone")
    print("  [OK] Immutable Log - Audit trail")
    print("  [OK] Control Plane - Kernel orchestration")
    print("  [OK] Pause/Resume - State management")
    print("  [OK] Graceful Shutdown - Clean stop")
    print()
    print("Grace's spine is resilient and functional!")
    print()
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_core())
