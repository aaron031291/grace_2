"""
Start Monitoring Safeguards
Initializes ACL and resource pressure monitors during boot

Called by orchestrator to ensure safeguards are active
"""

import logging

logger = logging.getLogger(__name__)


async def start_all_monitors():
    """
    Start all monitoring safeguards
    
    Includes:
    - ACL violation monitor (catches S02_acl_spam)
    - Resource pressure monitor (catches S03_cpu_spike)
    """
    
    logger.info("[MONITORS] Starting monitoring safeguards...")
    
    # Start ACL violation monitor
    try:
        from backend.monitoring.acl_violation_monitor import acl_violation_monitor
        await acl_violation_monitor.start()
        logger.info("✅ ACL violation monitor started")
    except Exception as e:
        logger.error(f"[MONITORS] ACL monitor failed to start: {e}")
    
    # Start resource pressure monitor
    try:
        from backend.monitoring.resource_pressure_monitor import resource_pressure_monitor
        await resource_pressure_monitor.start()
        logger.info("✅ Resource pressure monitor started")
    except Exception as e:
        logger.error(f"[MONITORS] Resource monitor failed to start: {e}")
    
    logger.info("[MONITORS] All monitoring safeguards active")


async def stop_all_monitors():
    """Stop all monitoring safeguards"""
    
    logger.info("[MONITORS] Stopping monitoring safeguards...")
    
    try:
        from backend.monitoring.acl_violation_monitor import acl_violation_monitor
        await acl_violation_monitor.stop()
    except Exception as e:
        logger.debug(f"ACL monitor stop error: {e}")
    
    try:
        from backend.monitoring.resource_pressure_monitor import resource_pressure_monitor
        await resource_pressure_monitor.stop()
    except Exception as e:
        logger.debug(f"Resource monitor stop error: {e}")
    
    logger.info("[MONITORS] Monitoring safeguards stopped")
