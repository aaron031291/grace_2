"""
Self-Healing CLI - Command-line interface for self-healing system
Usage:
    python -m backend.self_healing_cli status
    python -m backend.self_healing_cli simulate-failure <component>
    python -m backend.self_healing_cli manual-restart <component>
"""

import sys
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from .self_healing import health_monitor, system_state
from .governance_models import HealthCheck, HealingAction
from .models import async_session


async def show_status():
    """Show component health status"""
    print("\n" + "="*60)
    print("GRACE Self-Healing System Status")
    print("="*60)
    
    # Show system mode
    print(f"\n🔧 System Mode: {system_state.mode.upper()}")
    if system_state.reason:
        print(f"   Reason: {system_state.reason}")
    print(f"   Last Changed: {system_state.last_changed.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Show recent health checks
    print("\n📊 Component Health (Last 5 minutes):")
    print("-" * 60)
    
    async with async_session() as session:
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        
        result = await session.execute(
            select(HealthCheck)
            .where(HealthCheck.created_at >= five_min_ago)
            .order_by(HealthCheck.created_at.desc())
            .limit(20)
        )
        checks = result.scalars().all()
        
        if not checks:
            print("   No health checks in last 5 minutes")
        else:
            # Group by component
            components = {}
            for check in checks:
                if check.component not in components:
                    components[check.component] = check
            
            for component, check in components.items():
                status_icon = "✓" if check.status == "ok" else "✗"
                status_color = check.status.upper()
                latency = f"{check.latency_ms}ms" if check.latency_ms else "N/A"
                
                print(f"   {status_icon} {component:20s} [{status_color:8s}] {latency:8s}")
                if check.error:
                    print(f"      Error: {check.error}")
    
    # Show recent healing actions
    print("\n⚕️  Recent Healing Actions (Last 24 hours):")
    print("-" * 60)
    
    async with async_session() as session:
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        
        result = await session.execute(
            select(HealingAction)
            .where(HealingAction.created_at >= one_day_ago)
            .order_by(HealingAction.created_at.desc())
            .limit(10)
        )
        actions = result.scalars().all()
        
        if not actions:
            print("   No healing actions in last 24 hours")
        else:
            for action in actions:
                result_icon = "✓" if action.result == "success" else "✗"
                timestamp = action.created_at.strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"   {result_icon} [{timestamp}] {action.component}")
                print(f"      Action: {action.action}")
                print(f"      Result: {action.result}")
                print(f"      Detail: {action.detail}")
                print()
    
    # Show consecutive failures
    print("⚠️  Consecutive Failures:")
    print("-" * 60)
    
    if not health_monitor.consecutive_failures:
        print("   None")
    else:
        for component, count in health_monitor.consecutive_failures.items():
            if count > 0:
                print(f"   {component}: {count} consecutive failures")
    
    print("\n" + "="*60 + "\n")


async def simulate_failure(component: str):
    """Simulate a component failure"""
    print(f"\n🧪 Simulating failure for: {component}")
    
    valid_components = ["reflection_service", "database", "task_executor", "trigger_mesh"]
    
    if component not in valid_components:
        print(f"❌ Invalid component. Valid options: {', '.join(valid_components)}")
        return
    
    # Log simulated failure
    async with async_session() as session:
        check = HealthCheck(
            component=component,
            status="critical",
            latency_ms=0,
            error=f"Simulated failure via CLI at {datetime.utcnow()}"
        )
        session.add(check)
        await session.commit()
    
    print(f"✓ Logged simulated failure for {component}")
    
    # Increment consecutive failures
    health_monitor.consecutive_failures[component] = health_monitor.consecutive_failures.get(component, 0) + 1
    
    print(f"✓ Consecutive failures: {health_monitor.consecutive_failures[component]}")
    
    # Check if healing threshold reached
    if health_monitor.consecutive_failures[component] >= 2:
        print(f"\n⚕️  Healing threshold reached! Triggering self-healing...")
        
        result = await health_monitor._attempt_healing(component, "Simulated failure")
        
        async with async_session() as session:
            action = HealingAction(
                component=component,
                action=result["action"],
                result=result["result"],
                detail=f"Triggered by CLI simulation: {result['detail']}"
            )
            session.add(action)
            await session.commit()
        
        print(f"✓ Healing action: {result['action']}")
        print(f"✓ Result: {result['result']}")
        print(f"✓ Detail: {result['detail']}")
        
        if result["result"] == "success":
            health_monitor.consecutive_failures[component] = 0
            print(f"✓ Consecutive failures reset")
    else:
        print(f"\nℹ️  Not yet at healing threshold (need 2 consecutive failures)")
        print(f"   Run this command again to trigger healing")
    
    print()


async def manual_restart(component: str):
    """Manually restart a component"""
    print(f"\n🔧 Manually restarting: {component}")
    
    valid_components = ["reflection_service", "database", "task_executor", "trigger_mesh"]
    
    if component not in valid_components:
        print(f"❌ Invalid component. Valid options: {', '.join(valid_components)}")
        return
    
    # Use health monitor's manual restart (includes governance)
    result = await health_monitor.manual_restart(component, "cli_admin")
    
    print(f"\n📋 Restart Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get("status") == "blocked":
        print(f"   ⛔ Blocked by governance policy: {result.get('policy', 'unknown')}")
    elif result.get("status") == "pending_approval":
        print(f"   ⏳ Requires approval before restart")
    elif result.get("status") == "success":
        print(f"   ✓ {result.get('detail', 'Component restarted successfully')}")
    elif result.get("status") == "failed":
        print(f"   ✗ Restart failed: {result.get('detail', 'unknown error')}")
    
    print()


async def run_health_check():
    """Run immediate health check on all components"""
    print("\n🏥 Running health check on all components...")
    
    await health_monitor.check_all_components()
    
    print("✓ Health check complete\n")
    
    # Show results
    await show_status()


def print_usage():
    """Print CLI usage information"""
    print("""
GRACE Self-Healing CLI
======================

Usage:
    python -m backend.self_healing_cli <command> [args]

Commands:
    status                          Show component health status
    simulate-failure <component>    Trigger a test failure
    manual-restart <component>      Force restart a component
    check                          Run immediate health check

Components:
    - reflection_service
    - database
    - task_executor
    - trigger_mesh

Examples:
    python -m backend.self_healing_cli status
    python -m backend.self_healing_cli simulate-failure reflection_service
    python -m backend.self_healing_cli manual-restart task_executor
    python -m backend.self_healing_cli check
    """)


async def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "status":
            await show_status()
        
        elif command == "simulate-failure":
            if len(sys.argv) < 3:
                print("❌ Error: Missing component argument")
                print("Usage: python -m backend.self_healing_cli simulate-failure <component>")
                return
            component = sys.argv[2]
            await simulate_failure(component)
        
        elif command == "manual-restart":
            if len(sys.argv) < 3:
                print("❌ Error: Missing component argument")
                print("Usage: python -m backend.self_healing_cli manual-restart <component>")
                return
            component = sys.argv[2]
            await manual_restart(component)
        
        elif command == "check":
            await run_health_check()
        
        elif command in ["help", "-h", "--help"]:
            print_usage()
        
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
