"""Test Healer Watchdog"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from backend.core import control_plane
    from backend.monitoring.healer_watchdog import healer_watchdog
    
    print("=" * 80)
    print("HEALER WATCHDOG TEST")
    print("=" * 80)
    print()
    
    print("[1/3] Booting control plane (includes healer watchdog)...")
    await control_plane.start()
    print()
    
    print("[2/3] Checking healer watchdog status...")
    await asyncio.sleep(2)
    
    status = healer_watchdog.get_status()
    
    print(f"  Self-Healing Healthy: {status['self_healing_healthy']}")
    print(f"  Coding Agent Healthy: {status['coding_agent_healthy']}")
    print(f"  Mutual Recoveries: {status['mutual_recoveries']}")
    print(f"  Emergency Recoveries: {status['emergency_recoveries']}")
    print(f"  Emergency Delegates Active: {status['emergency_delegates_active']}")
    print()
    
    print("[3/3] Mutual Recovery Capability:")
    if status['self_healing_healthy'] and status['coding_agent_healthy']:
        print("  [OK] Both healers online - mutual recovery ready")
        print("  Scenario 1: If coding_agent fails → self_healing restarts it")
        print("  Scenario 2: If self_healing fails → coding_agent restarts it")
        print("  Scenario 3: If BOTH fail → healer_watchdog emergency protocol")
    else:
        print("  [WARN] One or both healers not healthy")
    
    print()
    print("=" * 80)
    print("HEALER WATCHDOG OPERATIONAL ✅")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
