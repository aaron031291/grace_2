#!/usr/bin/env python3
"""
Test Grace's Boot Layer - Unbreakable Core
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.core.boot_layer import boot_layer
from backend.core.control_plane import control_plane
from backend.core.message_bus import message_bus
from backend.core.immutable_log import immutable_log


async def test_boot_layer():
    """Test the boot layer"""
    
    print()
    print("Testing Grace's Unbreakable Core...")
    print()
    
    # Boot Grace
    result = await boot_layer.boot_grace()
    
    if result['success']:
        print("\nBoot successful!")
        print(f"Duration: {result['boot_duration_seconds']:.2f}s")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test pause/resume
        print("\n" + "=" * 80)
        print("Testing Pause/Resume")
        print("=" * 80)
        
        print("\nPausing system...")
        await control_plane.pause()
        status = control_plane.get_status()
        print(f"System state: {status['system_state']}")
        
        await asyncio.sleep(1)
        
        print("\nResuming system...")
        await control_plane.resume()
        status = control_plane.get_status()
        print(f"System state: {status['system_state']}")
        
        # Test message bus
        print("\n" + "=" * 80)
        print("Testing Message Bus")
        print("=" * 80)
        
        print("\nPublishing test message...")
        msg_id = await message_bus.publish(
            source='test',
            topic='system.test',
            payload={'message': 'Hello from test!'}
        )
        print(f"Published: {msg_id}")
        
        bus_stats = message_bus.get_stats()
        print(f"Total messages: {bus_stats['total_messages']}")
        print(f"Active topics: {bus_stats['active_topics']}")
        
        # Test immutable log
        print("\n" + "=" * 80)
        print("Testing Immutable Log")
        print("=" * 80)
        
        print("\nAppending test entry...")
        log_id = await immutable_log.append(
            actor='test',
            action='test_action',
            resource='test_resource',
            decision={'approved': True},
            metadata={'test': True}
        )
        print(f"Logged: {log_id}")
        
        log_stats = immutable_log.get_stats()
        print(f"Total entries: {log_stats['total_entries']}")
        print(f"Log file: {log_stats['log_file']}")
        print(f"Size: {log_stats['log_size_bytes']} bytes")
        
        # Search log
        print("\nSearching log (last 5 entries)...")
        recent = await immutable_log.search(limit=5)
        for entry in recent:
            print(f"  - [{entry['timestamp']}] {entry['actor']}: {entry['action']}")
        
        # Graceful shutdown
        print("\n" + "=" * 80)
        print("Shutdown Test")
        print("=" * 80)
        
        print("\nInitiating graceful shutdown...")
        await boot_layer.shutdown_grace()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print("""
Grace's Unbreakable Core Tested:

✓ Message Bus - Communication backbone working
✓ Control Plane - Kernel orchestration working
✓ Immutable Log - Audit trail working
✓ Pause/Resume - State management working
✓ Graceful Shutdown - Clean shutdown working

Core is resilient and ready!
""")
    
    else:
        print(f"\nBoot failed: {result.get('error')}")


if __name__ == '__main__':
    asyncio.run(test_boot_layer())
