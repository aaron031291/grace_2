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
    
    print("\nðŸ”§ ==================== VERIFICATION SYSTEMS ====================")
    
    # 1. Validate configuration first
    print("ðŸ“‹ Validating configuration...")
    if not validate_startup_config():
        print("âš ï¸  Configuration warnings detected, but continuing...")
    
    # 2. Ensure event persistence model is registered
    print("ðŸ’¾ Registering event persistence models...")
    try:
        # Import to ensure models are registered
        import backend.event_persistence
        import backend.action_contract
        import backend.benchmarks
        import backend.progression_tracker
        import backend.self_heal.safe_hold
        print("   âœ“ All verification models registered")
    except Exception as e:
        print(f"   âš ï¸  Model registration warning: {e}")
    
    # 3. Start approval notification system
    print("ðŸ”” Starting approval notifications (SSE/webhooks)...")
    try:
        await approval_notifications.start()
        print("   âœ“ Approval notifications active")
    except Exception as e:
        print(f"   âš ï¸  Approval notifications failed: {e}")
    
    # 4. Start data aggregation (optional, based on config)
    print("ðŸ“Š Starting data aggregation service...")
    try:
        import os
        interval = int(os.getenv("AGGREGATION_INTERVAL_HOURS", "1"))
        await data_aggregation.start(interval_hours=interval)
        print(f"   âœ“ Data aggregation started (every {interval}h)")
    except Exception as e:
        print(f"   âš ï¸  Data aggregation failed: {e}")
    
    # 5. Start immutable log analytics
    print("ðŸ” Starting immutable log analytics...")
    try:
        await immutable_log_analytics.start(interval_minutes=15)
        print("   âœ“ Log analytics started (verifies every 15min)")
    except Exception as e:
        print(f"   âš ï¸  Log analytics failed: {e}")
    
    print("âœ“ Verification systems initialized")
    print("=" * 64)


async def stop_verification_systems():
    """
    Stop all verification systems on shutdown.
    
    Call this from main.py shutdown to ensure clean shutdown.
    """
    
    print("\nðŸ›‘ Shutting down verification systems...")
    
    try:
        await approval_notifications.stop()
        print("   âœ“ Approval notifications stopped")
    except Exception:
        pass
    
    try:
        await data_aggregation.stop()
        print("   âœ“ Data aggregation stopped")
    except Exception:
        pass
    
    try:
        await immutable_log_analytics.stop()
        print("   âœ“ Log analytics stopped")
    except Exception:
        pass
    
    print("âœ“ Verification systems shut down cleanly")

