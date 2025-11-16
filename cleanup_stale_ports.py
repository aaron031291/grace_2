#!/usr/bin/env python3
"""
Cleanup Stale Ports
Removes all dead/stale port allocations from registry
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.port_manager import port_manager

def cleanup_stale_ports():
    """Clean up all stale port allocations"""
    print("=" * 60)
    print("GRACE - Port Cleanup Utility")
    print("=" * 60)
    print()
    
    allocations = port_manager.get_all_allocations()
    
    print(f"Found {len(allocations)} port allocations")
    print()
    
    stale_ports = []
    active_ports = []
    
    for alloc in allocations:
        port = alloc['port']
        status = alloc['health_status']
        service = alloc['service_name']
        
        if status in ['dead', 'not_listening', 'unreachable', 'unknown']:
            stale_ports.append(port)
            print(f"  [STALE] Port {port}: {service} ({status})")
        else:
            active_ports.append(port)
            print(f"  [OK]    Port {port}: {service} ({status})")
    
    print()
    print(f"Active: {len(active_ports)}")
    print(f"Stale:  {len(stale_ports)}")
    print()
    
    if stale_ports:
        response = input(f"Clean up {len(stale_ports)} stale ports? (y/n): ")
        
        if response.lower() == 'y':
            for port in stale_ports:
                port_manager.release_port(port)
                print(f"  Cleaned: {port}")
            
            print()
            print(f"[OK] Cleaned up {len(stale_ports)} ports")
        else:
            print("[SKIP] No cleanup performed")
    else:
        print("[OK] No stale ports found")
    
    print()
    remaining = len(port_manager.get_all_allocations())
    print(f"Remaining allocations: {remaining}")
    print()

if __name__ == "__main__":
    cleanup_stale_ports()
