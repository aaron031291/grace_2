"""
Cleanup Port Registry
Removes stale port allocations and resets to fresh state

Run this if:
- Port watchdog reports hundreds of dead ports
- Snapshots fail with health check errors
- You want to reset port tracking
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def cleanup_port_registry():
    """Cleanup port registry and reset to fresh state"""
    
    registry_path = Path("databases/port_registry")
    registry_file = registry_path / "port_registry.json"
    
    print()
    print("=" * 80)
    print("PORT REGISTRY CLEANUP")
    print("=" * 80)
    print()
    
    if not registry_file.exists():
        print("✓ No port registry found - already clean")
        return
    
    # Load current state
    try:
        with open(registry_file, 'r') as f:
            data = json.load(f)
        
        allocations = data.get('allocations', {})
        print(f"Current allocations: {len(allocations)}")
        
        # Show port range
        if allocations:
            ports = [int(p) for p in allocations.keys()]
            print(f"Port range: {min(ports)} - {max(ports)}")
            print()
            
            # Show sample allocations
            print("Sample allocations:")
            for i, (port, alloc) in enumerate(list(allocations.items())[:5]):
                print(f"  {port}: {alloc.get('service_name', 'unknown')} ({alloc.get('health_status', 'unknown')})")
            
            if len(allocations) > 5:
                print(f"  ... and {len(allocations) - 5} more")
        
        print()
        print("=" * 80)
        
        # Confirm cleanup
        response = input("Clean up all allocations? (y/N): ").strip().lower()
        
        if response != 'y':
            print("Cancelled")
            return
        
        # Backup
        backup_file = registry_path / f"port_registry_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Backed up to: {backup_file.name}")
        
        # Create clean state
        clean_data = {
            "allocations": {},
            "metadata": {
                "cleaned": datetime.utcnow().isoformat(),
                "reason": "Manual cleanup - reset to fresh state",
                "previous_allocations": len(allocations),
                "backup_file": backup_file.name
            }
        }
        
        with open(registry_file, 'w') as f:
            json.dump(clean_data, f, indent=2)
        
        print(f"✓ Cleaned {len(allocations)} allocations")
        print(f"✓ Port registry reset to fresh state")
        print()
        print("Next boot will start with clean slate.")
        print("Only actively used ports will be monitored.")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    cleanup_port_registry()
