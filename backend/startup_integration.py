"""
Startup Integration Module

Centralizes all new service startup to ensure nothing is forgotten.
Wires up: event persistence, async jobs, observability, notifications, 
aggregation, and log analytics.
"""

from .event_persistence import event_persistence, ActionEvent
from .async_jobs import async_job_queue
from .approval_notifications import approval_notifications
from .data_aggregation import data_aggregation
from .immutable_log_analytics import immutable_log_analytics
from .config_validator import validate_startup_config
from .base_models import Base


async def start_verification_systems():
    """
    Start all verification and resilience systems.
    
    Call this from main.py startup to ensure all systems are initialized.
    """
    
    print("\n🔧 ==================== VERIFICATION SYSTEMS ====================")
    
    # 1. Validate configuration first
    print("📋 Validating configuration...")
    if not validate_startup_config():
        print("⚠️  Configuration warnings detected, but continuing...")
    
    # 2. Ensure event persistence model is registered
    print("💾 Registering event persistence models...")
    try:
        # Import to ensure models are registered
        import backend.event_persistence
        import backend.action_contract
        import backend.benchmarks
        import backend.progression_tracker
        import backend.self_heal.safe_hold
        print("   ✓ All verification models registered")
    except Exception as e:
        print(f"   ⚠️  Model registration warning: {e}")
    
    # 3. Start approval notification system
    print("🔔 Starting approval notifications (SSE/webhooks)...")
    try:
        await approval_notifications.start()
        print("   ✓ Approval notifications active")
    except Exception as e:
        print(f"   ⚠️  Approval notifications failed: {e}")
    
    # 4. Start data aggregation (optional, based on config)
    print("📊 Starting data aggregation service...")
    try:
        import os
        interval = int(os.getenv("AGGREGATION_INTERVAL_HOURS", "1"))
        await data_aggregation.start(interval_hours=interval)
        print(f"   ✓ Data aggregation started (every {interval}h)")
    except Exception as e:
        print(f"   ⚠️  Data aggregation failed: {e}")
    
    # 5. Start immutable log analytics
    print("🔍 Starting immutable log analytics...")
    try:
        await immutable_log_analytics.start(interval_minutes=15)
        print("   ✓ Log analytics started (verifies every 15min)")
    except Exception as e:
        print(f"   ⚠️  Log analytics failed: {e}")
    
    print("✓ Verification systems initialized")
    print("=" * 64)


async def stop_verification_systems():
    """
    Stop all verification systems on shutdown.
    
    Call this from main.py shutdown to ensure clean shutdown.
    """
    
    print("\n🛑 Shutting down verification systems...")
    
    try:
        await approval_notifications.stop()
        print("   ✓ Approval notifications stopped")
    except Exception:
        pass
    
    try:
        await data_aggregation.stop()
        print("   ✓ Data aggregation stopped")
    except Exception:
        pass
    
    try:
        await immutable_log_analytics.stop()
        print("   ✓ Log analytics stopped")
    except Exception:
        pass
    
    print("✓ Verification systems shut down cleanly")
