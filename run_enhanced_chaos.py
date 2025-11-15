"""
Run Enhanced Chaos Test Suite
Maximum stress - multi-fault, cross-layer, deep complexity
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    from backend.chaos.enhanced_chaos_runner import enhanced_chaos_runner
    
    print()
    print("=" * 80)
    print("GRACE ENHANCED CHAOS TEST SUITE")
    print("Maximum Stress - Pushing All Limits")
    print("=" * 80)
    print()
    
    # Choose what to test
    print("Available categories:")
    print("  1. multi_fault     - Simultaneous, cascading, randomized faults")
    print("  2. layer2          - HTM queue floods, worker stalls")
    print("  3. layer3          - Governance storms, retro cascades")
    print("  4. external        - API attacks, model drift")
    print("  5. deep_complexity - Long-running, Byzantine, failover")
    print("  6. ALL             - Run everything")
    print()
    
    choice = input("Select category (1-6): ").strip()
    
    categories_map = {
        '1': ['multi_fault'],
        '2': ['layer2'],
        '3': ['layer3'],
        '4': ['external'],
        '5': ['deep_complexity'],
        '6': None  # All
    }
    
    categories = categories_map.get(choice)
    
    print()
    print("=" * 80)
    print("STARTING CHAOS TEST")
    print("=" * 80)
    print()
    
    # Run test suite
    report = await enhanced_chaos_runner.run_full_suite(categories=categories)
    
    print()
    print("Test complete!")
    
    return report

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
