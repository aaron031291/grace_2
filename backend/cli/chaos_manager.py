"""
Chaos Loop Manager CLI
Control autonomous chaos testing loop
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


async def main():
    from backend.chaos.autonomous_chaos_loop import autonomous_chaos_loop
    
    print("=" * 80)
    print("AUTONOMOUS CHAOS LOOP - MANAGER")
    print("=" * 80)
    print()
    
    print("Commands:")
    print("  1. Start autonomous loop (background)")
    print("  2. Run manual test now")
    print("  3. View learning summary")
    print("  4. Escalate all scenarios")
    print("  5. Reset learning data")
    print("  6. Exit")
    print()
    
    while True:
        choice = input("Select command: ").strip()
        print()
        
        if choice == '1':
            await autonomous_chaos_loop.start()
            print("[OK] Autonomous loop started")
            print(f"Next run: {autonomous_chaos_loop._get_next_run_time().strftime('%Y-%m-%d %H:%M')}")
            print()
            print("Loop is running in background. Press Ctrl+C to exit manager.")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(60)
                    summary = autonomous_chaos_loop.get_learning_summary()
                    print(f"[STATUS] Runs: {summary['total_lifetime_runs']}, "
                          f"Mastered: {summary['scenarios_mastered']}/{summary['total_scenarios_tested']}, "
                          f"Next: {autonomous_chaos_loop._get_next_run_time().strftime('%H:%M')}")
            except KeyboardInterrupt:
                print("\n[STOP] Stopping loop...")
                await autonomous_chaos_loop.stop()
                break
        
        elif choice == '2':
            print("[MANUAL RUN] Executing chaos test now...")
            await autonomous_chaos_loop._execute_scheduled_run()
            print("[OK] Manual run complete")
            print()
        
        elif choice == '3':
            summary = autonomous_chaos_loop.get_learning_summary()
            
            print("LEARNING SUMMARY")
            print("-" * 80)
            print(f"Total scenarios tested: {summary['total_scenarios_tested']}")
            print(f"Scenarios mastered: {summary['scenarios_mastered']}")
            print(f"Scenarios failing: {summary['scenarios_still_failing']}")
            print(f"Average difficulty: {summary['average_difficulty_level']:.1f}/10")
            print(f"Lifetime runs: {summary['total_lifetime_runs']}")
            print(f"Last run: {summary['last_run'] or 'Never'}")
            print(f"Next run: {summary['next_run']}")
            print()
        
        elif choice == '4':
            print("[ESCALATE] Escalating all scenarios...")
            for learning in autonomous_chaos_loop.scenario_learning.values():
                if learning.difficulty_level < autonomous_chaos_loop.max_difficulty:
                    learning.difficulty_level += 1
            autonomous_chaos_loop.save_learning_data()
            print("[OK] All scenarios escalated")
            print()
        
        elif choice == '5':
            confirm = input("Reset all learning data? (yes/no): ")
            if confirm.lower() == 'yes':
                autonomous_chaos_loop.scenario_learning.clear()
                autonomous_chaos_loop.total_runs_lifetime = 0
                autonomous_chaos_loop.save_learning_data()
                print("[OK] Learning data reset")
            print()
        
        elif choice == '6':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice")
            print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
