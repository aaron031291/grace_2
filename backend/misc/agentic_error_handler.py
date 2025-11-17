"""
Agentic Error Handler - Instant Detection & Trigger Mesh Integration

Catches errors immediately on user input and publishes to Trigger Mesh for
autonomous triage, action, and resolution.

Pipeline: Error Detected -> Problem Identified -> Action Planned -> Resolved/Failed
"""

import asyncio
import traceback
from typing import Dict, Any, Callable
from datetime import datetime, timezone
from functools import wraps
from contextlib import asynccontextmanager
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import ImmutableLog


class AgenticErrorHandler:
    """
    Intercepts errors and orchestrates agentic response pipeline.
    
    Features:
    - Instant error detection & publishing
    - Automatic severity classification
    - Trigger Mesh event flow
    - Governance integration
    - Learning from failures
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.error_count = 0
        self.resolved_count = 0
        
    async def capture_user_input_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        user: str,
        command: str,
        start_time: datetime
    ) -> str:
        """
        Capture and process user input error with instant Trigger Mesh publishing.
        
        Returns error_id for tracking through resolution pipeline
        """
        error_id = f"error_{user}_{datetime.utcnow().timestamp()}"
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Extract error details
        error_type = type(error).__name__
        error_msg = str(error)
        stack_trace = traceback.format_exc()
        
        # Classify severity
        severity = self._classify_severity(error, context)
        
        # Build error payload
        payload = {
            "error_id": error_id,
            "user": user,
            "command": command,
            "error_type": error_type,
            "error_message": error_msg,
            "severity": severity,
            "latency_ms": latency_ms,
            "context": self._sanitize_context(context),
            "stack_trace": stack_trace[:1000],  # Truncate
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # INSTANT: Publish to Trigger Mesh (error.detected)
        await trigger_mesh.publish(TriggerEvent(
            event_type="error.detected",
            source="user_input",
            actor=user,
            resource=command,
            payload=payload,
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Log to immutable ledger
        await self.immutable_log.append(
            actor=user,
            action="error_detected",
            resource=command,
            subsystem="user_input",
            payload=payload,
            result="detected"
        )
        
        self.error_count += 1
        
        return error_id
    
    async def capture_governance_block(
        self,
        action: str,
        user: str,
        policy: str,
        reason: str,
        context: Dict[str, Any]
    ):
        """Capture governance policy block and publish for agentic handling"""
        
        block_id = f"block_{user}_{datetime.utcnow().timestamp()}"
        
        payload = {
            "block_id": block_id,
            "action": action,
            "user": user,
            "policy": policy,
            "reason": reason,
            "context": self._sanitize_context(context),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish governance block
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.forbidden",
            source="governance_engine",
            actor=user,
            resource=action,
            payload=payload,
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Log immutably
        await self.immutable_log.append(
            actor="governance",
            action="action_blocked",
            resource=action,
            subsystem="governance",
            payload=payload,
            result="blocked"
        )
    
    async def capture_warning(
        self,
        source: str,
        message: str,
        severity: str,
        context: Dict[str, Any]
    ):
        """Capture warning for agentic awareness"""
        
        warning_id = f"warn_{source}_{datetime.utcnow().timestamp()}"
        
        payload = {
            "warning_id": warning_id,
            "source": source,
            "message": message,
            "severity": severity,
            "context": self._sanitize_context(context),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish warning
        await trigger_mesh.publish(TriggerEvent(
            event_type="warning.raised",
            source=source,
            actor="system",
            resource="warning",
            payload=payload,
            timestamp=datetime.now(timezone.utc)
        ))
    
    def _classify_severity(self, error: Exception, context: Dict) -> str:
        """Classify error severity for prioritization"""
        
        # Critical: Data loss, security, corruption
        if any(x in str(error).lower() for x in ['database', 'corruption', 'security', 'auth']):
            return "critical"
        
        # High: Service disruption, permissions
        if any(x in str(error).lower() for x in ['permission', 'forbidden', 'unavailable']):
            return "high"
        
        # Medium: Validation, logic errors
        if any(x in type(error).__name__.lower() for x in ['value', 'type', 'key']):
            return "medium"
        
        # Low: User mistakes, retryable
        return "low"
    
    def _sanitize_context(self, context: Dict) -> Dict:
        """Remove sensitive data from context before logging"""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'secret', 'key', 'credential'}
        
        for k, v in context.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = str(v)[:200]  # Truncate long values
        
        return sanitized
    
    def intercept_sync(self, func: Callable):
        """Decorator for synchronous functions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get user context
                user = kwargs.get('user', 'system')
                command = func.__name__
                context = {'args': str(args), 'kwargs': str(kwargs)}
                
                # Capture error asynchronously
                asyncio.create_task(
                    self.capture_user_input_error(e, context, user, command, start_time)
                )
                raise
        return wrapper
    
    def intercept_async(self, func: Callable):
        """Decorator for async functions"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Get user context
                user = kwargs.get('user', 'system')
                if isinstance(user, dict):
                    user = user.get('username', 'system')
                
                command = func.__name__
                context = {'args': str(args)[:500], 'kwargs': str(kwargs)[:500]}
                
                # Capture error
                await self.capture_user_input_error(e, context, user, command, start_time)
                raise
        return wrapper
    
    @asynccontextmanager
    async def track_operation(self, operation: str, user: str, context: Dict = None):
        """Context manager for tracking operations with automatic error capture"""
        start_time = datetime.utcnow()
        operation_id = f"op_{operation}_{start_time.timestamp()}"
        
        # Emit operation start
        await trigger_mesh.publish(TriggerEvent(
            event_type="operation.started",
            source="user_input",
            actor=user,
            resource=operation,
            payload={"operation_id": operation_id, "context": context or {}},
            timestamp=datetime.now(timezone.utc)
        ))
        
        try:
            yield operation_id
            
            # Success
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            await trigger_mesh.publish(TriggerEvent(
                event_type="operation.completed",
                source="user_input",
                actor=user,
                resource=operation,
                payload={"operation_id": operation_id, "duration_ms": duration_ms},
                timestamp=datetime.now(timezone.utc)
            ))
            
        except Exception as e:
            # Error
            await self.capture_user_input_error(
                e, context or {}, user, operation, start_time
            )
            raise


# Global handler instance
agentic_error_handler = AgenticErrorHandler()
