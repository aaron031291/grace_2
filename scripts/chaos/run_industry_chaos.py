"""
Industry-Grade Chaos Testing
Google DiRT + Netflix FIT + Jepsen Combined

Full diagnostics, artifact collection, evidence-backed validation
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from backend.chaos.industry_chaos_runner import industry_chaos_runner
    
    print()
    print("=" * 80)
    print("INDUSTRY-GRADE CHAOS TESTING SUITE")
    print("Google DiRT + Netflix FIT + Jepsen")
    print("=" * 80)
    print()
    print("Test Approaches:")
    print("  1. DiRT (Google)     - Infrastructure resilience, kernel kills")
    print("  2. FIT (Netflix)     - Load + chaos, dependency failures")
    print("  3. Jepsen            - Consistency, partitions, clock skew")
    print("  4. ALL               - Full suite (recommended)")
    print()
    
    choice = input("Select test approach (1-4): ").strip()
    
    category_map = {
        '1': ['dirt_infrastructure'],
        '2': ['fit_load'],
        '3': ['jepsen_consistency'],
        '4': None  # All categories
    }
    
    categories = category_map.get(choice)
    
    if categories:
        print(f"\nRunning: {', '.join(categories)}")
    else:
        print("\nRunning: ALL test approaches")
    
    print()
    print("=" * 80)
    print()
    
    # Run the suite
    report = await industry_chaos_runner.run_full_suite(categories=categories)
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Evidence & Artifacts:")
    print()
    
    for artifact_type, path in report.get('artifacts', {}).items():
        print(f"  {artifact_type}:")
        print(f"    {path}")
        print()
    
    print("Review these artifacts for evidence-backed validation!")
    print()
    
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
