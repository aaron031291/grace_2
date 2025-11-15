"""
Check Port Manager Status
View all allocated ports with metadata
"""

import sys
sys.path.insert(0, 'c:/Users/aaron/grace_2')

from backend.core.port_manager import port_manager
from backend.core.port_watchdog import port_watchdog
from datetime import datetime

print("\n" + "="*70)
print("GRACE PORT MANAGER STATUS")
print("="*70)

stats = port_manager.get_stats()

print(f"\nPort Range: {stats['port_range']}")
print(f"Total Ports Available: {stats['total_ports']}")
print(f"Allocated: {stats['allocated_ports']}")
print(f"Available: {stats['available_ports']}")

if stats['allocated_ports'] > 0:
    print("\n" + "="*70)
    print("ALLOCATED PORTS")
    print("="*70)
    
    for alloc in stats['allocations']:
        print(f"\nPort {alloc['port']}: {alloc['service_name']}")
        print(f"  Started by: {alloc['started_by']}")
        print(f"  Purpose: {alloc['purpose']}")
        print(f"  PID: {alloc['pid'] or 'Not registered'}")
        print(f"  Status: {alloc['health_status']}")
        print(f"  Allocated: {alloc['allocated_at']}")
        print(f"  Requests: {alloc['request_count']}")
        print(f"  Errors: {alloc['error_count']}")
else:
    print("\nNo ports currently allocated")

# Watchdog status
print("\n" + "="*70)
print("WATCHDOG STATUS")
print("="*70)

watchdog_status = port_watchdog.get_status()

print(f"\nRunning: {watchdog_status['running']}")
print(f"Check Interval: {watchdog_status['check_interval']}s")
print(f"Checks Performed: {watchdog_status['checks_performed']}")
print(f"Issues Detected: {watchdog_status['issues_detected']}")
print(f"Stale Cleaned: {watchdog_status['stale_cleaned']}")
print(f"Monitored Ports: {watchdog_status['monitored_ports']}")

print("\n" + "="*70)
print("COMMANDS")
print("="*70)
print("\nManually trigger health check:")
print("  python -c \"from backend.core.port_manager import port_manager; print(port_manager.health_check_all())\"")
print("\nView logs:")
print("  type logs\\port_manager\\allocations_*.jsonl")
print("\nView registry:")
print("  type databases\\port_registry\\port_registry.json")
print("\n" + "="*70)
