"""
Safe Helpers - Defensive wrappers for critical operations

Ensures event bus, logging, and DB operations never crash the main flow.
All helpers are best-effort with graceful degradation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log

# Configure logger
logger = logging.getLogger(__name__)


async def safe_publish(
    event_type: str,
    source: str,
    actor: str,
    resource: str,
    payload: Dict[str, Any],
    timeout: float = 2.0
) -> bool:
    """
    Safely publish event to trigger mesh with timeout.
    Never blocks or crashes main flow.
    
    Returns:
        True if published successfully, False otherwise
    """
    try:
        event = TriggerEvent(
            event_type=event_type,
            source=source,
            actor=actor,
            resource=resource,
            payload=payload,
            timestamp=datetime.now()
        )
        
        await asyncio.wait_for(
            trigger_mesh.publish(event),
            timeout=timeout
        )
        return True
        
    except asyncio.TimeoutError:
        logger.warning(f"Event publish timeout: {event_type}")
        return False
    except Exception as e:
        logger.warning(f"Event publish failed: {event_type} - {e}")
        return False


async def safe_log(
    actor: str,
    action: str,
    resource: str,
    subsystem: str,
    payload: Dict[str, Any],
    result: str,
    timeout: float = 2.0
) -> bool:
    """
    Safely append to immutable log with timeout.
    Never blocks or crashes main flow.
    
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        await asyncio.wait_for(
            immutable_log.append(
                actor=actor,
                action=action,
                resource=resource,
                subsystem=subsystem,
                payload=payload,
                result=result
            ),
            timeout=timeout
        )
        return True
        
    except asyncio.TimeoutError:
        logger.warning(f"Immutable log timeout: {action}")
        return False
    except Exception as e:
        logger.warning(f"Immutable log failed: {action} - {e}")
        return False


async def safe_db_operation(
    operation: callable,
    fallback_value: Any = None,
    operation_name: str = "db_operation"
) -> Any:
    """
    Safely execute database operation with error handling.
    
    Args:
        operation: Async callable to execute
        fallback_value: Value to return on failure
        operation_name: Name for logging
    
    Returns:
        Operation result or fallback_value on failure
    """
    try:
        return await operation()
    except Exception as e:
        logger.error(f"DB operation failed ({operation_name}): {e}")
        return fallback_value


def safe_get(
    dictionary: Dict,
    key: str,
    default: Any = None,
    expected_type: type = None
) -> Any:
    """
    Safely get value from dictionary with type checking.
    
    Args:
        dictionary: Dict to get from
        key: Key to retrieve
        default: Default value if missing or wrong type
        expected_type: Expected type (validates if provided)
    
    Returns:
        Value or default
    """
    value = dictionary.get(key, default)
    
    if expected_type and value is not None:
        if not isinstance(value, expected_type):
            logger.warning(f"Type mismatch for key '{key}': expected {expected_type}, got {type(value)}")
            return default
    
    return value


class SafeTaskContext:
    """
    Context manager for safe task execution with cleanup.
    Ensures resources are released even on errors.
    """
    
    def __init__(self, task_name: str, timeout: Optional[float] = None):
        self.task_name = task_name
        self.timeout = timeout
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = asyncio.get_event_loop().time()
        logger.info(f"Starting task: {self.task_name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = asyncio.get_event_loop().time() - self.start_time
        
        if exc_type:
            logger.error(f"Task failed: {self.task_name} ({duration:.2f}s) - {exc_val}")
        else:
            logger.info(f"Task completed: {self.task_name} ({duration:.2f}s)")
        
        # Return False to propagate exception
        return False


async def with_timeout(
    operation: callable,
    timeout_seconds: float,
    operation_name: str = "operation"
):
    """
    Execute operation with timeout.
    
    Raises:
        TimeoutError if operation exceeds timeout
    """
    try:
        return await asyncio.wait_for(operation(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out: {operation_name} ({timeout_seconds}s)")
        raise TimeoutError(f"{operation_name} exceeded {timeout_seconds}s timeout")
