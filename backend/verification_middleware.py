"""Verification middleware for cryptographically signing critical actions"""

import functools
import uuid
import inspect
from datetime import datetime
from typing import Callable, Any, Dict
from fastapi import Request, HTTPException
from .verification import verification_engine
from .governance import governance_engine
from .hunter_integration import hunter_integration
from .constitutional_verifier import constitutional_verifier

class VerificationMiddleware:
    """Middleware to wrap critical routes with verification envelopes"""
    
    def __init__(self):
        self.engine = verification_engine
    
    async def verify_and_record(
        self,
        actor: str,
        action_type: str,
        resource: str,
        input_data: Dict[str, Any],
        action_func: Callable,
        *args,
        **kwargs
    ) -> tuple:
        """Sign inputs, execute action, sign outputs, verify against governance"""
        
        action_id = f"{action_type}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        signature, input_hash = self.engine.create_envelope(
            action_id=action_id,
            actor=actor,
            action_type=action_type,
            resource=resource,
            input_data=input_data
        )
        
        verified = self.engine.verify_envelope(
            signature, action_id, actor, action_type, resource, input_hash
        )
        
        if not verified:
            await hunter_integration.flag_verification_failure(
                action_id, actor, action_type, "Signature verification failed"
            )
            raise HTTPException(status_code=403, detail="Verification signature invalid")
        
        result = await action_func(*args, **kwargs)
        
        output_data = {"result": str(result)[:500]}
        await self.engine.log_verified_action(
            action_id=action_id,
            actor=actor,
            action_type=action_type,
            resource=resource,
            input_data=input_data,
            output_data=output_data,
            criteria_met=True
        )
        
        return result, action_id

verification_middleware = VerificationMiddleware()

def verify_action(action_type: str, resource_extractor: Callable = None):
    """
    Decorator to wrap routes with verification envelope
    
    Args:
        action_type: Type of action (e.g., 'file_write', 'code_execution')
        resource_extractor: Function to extract resource name from request
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            current_user = "system"
            request_data = {}

            for arg in args:
                if isinstance(arg, Request):
                    request = arg

            if "current_user" in kwargs:
                current_user = kwargs["current_user"]
            elif "req" in kwargs:
                if hasattr(kwargs["req"], "dict"):
                    request_data = kwargs["req"].dict()

            if request:
                try:
                    body = await request.json()
                    if isinstance(body, dict):
                        request_data.update(body)
                except Exception:
                    pass

            resource = "unknown"
            if resource_extractor and request_data:
                try:
                    resource = resource_extractor(request_data) or "unknown"
                except Exception:
                    resource = "unknown"
            elif "file_path" in request_data:
                resource = request_data["file_path"]
            elif "command" in request_data:
                resource = request_data["command"]
            elif "model_name" in request_data:
                resource = request_data["model_name"]

            # Constitutional compliance check
            constitutional_result = await constitutional_verifier.verify_action(
                actor=current_user,
                action_type=action_type,
                resource=resource,
                payload=request_data,
                confidence=request_data.get('confidence', 1.0),
                context=request_data.get('context', {})
            )

            if not constitutional_result.get('allowed', True):
                violations = constitutional_result.get('violations', [])
                violation_msg = ', '.join([v.get('reason', 'Unknown') for v in violations[:3]])
                raise HTTPException(
                    status_code=403,
                    detail=f"Blocked by constitutional verification: {violation_msg}"
                )

            gov_decision = await governance_engine.check(
                actor=current_user,
                action=action_type,
                resource=resource,
                payload=request_data
            )

            if gov_decision.get("decision") == "block":
                raise HTTPException(
                    status_code=403,
                    detail=f"Blocked by governance: {gov_decision.get('policy', 'unknown')}"
                )

            result, action_id = await verification_middleware.verify_and_record(
                actor=current_user,
                action_type=action_type,
                resource=resource,
                input_data=request_data,
                action_func=func,
                *args,
                **kwargs
            )

            if isinstance(result, dict):
                result["_verification_id"] = action_id

            return result

        # Preserve the original signature for FastAPI dependency resolution
        try:
            # Help FastAPI introspection follow the original callable
            wrapper.__wrapped__ = func  # type: ignore[attr-defined]
            wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
            wrapper.__annotations__ = getattr(func, "__annotations__", {})  # type: ignore[attr-defined]
            wrapper.__module__ = getattr(func, "__module__", wrapper.__module__)
            wrapper.__doc__ = getattr(func, "__doc__", wrapper.__doc__)
        except Exception:
            pass
        return wrapper
    return decorator
