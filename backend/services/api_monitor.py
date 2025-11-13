"""
API Monitor
Wraps external API calls to detect rate limits and trigger mitigation
"""

import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import time


class APIRateLimitMonitor:
    """
    Monitors API calls and handles rate limiting
    Integrates with self-healing for automatic backoff
    """
    
    def __init__(self):
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.backoff_until: Dict[str, datetime] = {}
    
    async def call_with_monitoring(
        self,
        api_name: str,
        api_call: Callable,
        *args,
        **kwargs
    ):
        """
        Wrap an API call with rate limit monitoring
        
        Args:
            api_name: Name of the API (e.g., "OpenAI", "Stripe")
            api_call: Async function to call
            *args, **kwargs: Arguments to pass to the call
            
        Returns:
            Result of the API call
            
        Raises:
            Exception if call fails after retries
        """
        # Check if we're in backoff period
        if api_name in self.backoff_until:
            wait_until = self.backoff_until[api_name]
            if datetime.now() < wait_until:
                wait_seconds = (wait_until - datetime.now()).total_seconds()
                print(f"[APIMonitor] {api_name} in backoff, waiting {wait_seconds:.1f}s")
                await asyncio.sleep(wait_seconds)
        
        # Make the call
        try:
            start_time = time.time()
            result = await api_call(*args, **kwargs)
            duration = time.time() - start_time
            
            # Success - clear any backoff
            if api_name in self.backoff_until:
                del self.backoff_until[api_name]
            
            print(f"[APIMonitor] {api_name} call succeeded ({duration:.2f}s)")
            return result
            
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if '429' in error_str or 'rate' in error_str.lower() or 'quota' in error_str.lower():
                await self._handle_rate_limit(api_name, e, kwargs.get('retry_count', 0))
                raise
            else:
                # Other error - just raise
                raise
    
    async def _handle_rate_limit(self, api_name: str, error: Exception, retry_count: int = 0):
        """
        Handle rate limit exceeded error
        """
        print(f"[APIMonitor] Rate limit exceeded for {api_name}")
        
        # Extract retry-after from error if available
        retry_after = 60  # Default 1 minute
        
        # Calculate backoff
        backoff_seconds = retry_after * (2 ** retry_count)  # Exponential
        backoff_until = datetime.now() + timedelta(seconds=backoff_seconds)
        self.backoff_until[api_name] = backoff_until
        
        print(f"[APIMonitor] Backing off for {backoff_seconds}s")
        
        # Log monitoring event
        try:
            from backend.monitoring_models import MonitoringEvent
            from backend.models import async_session
            
            async with async_session() as session:
                event = MonitoringEvent(
                    event_type="api.rate_limit_exceeded",
                    severity="medium",
                    source=api_name,
                    component="External API Client",
                    title="API Rate Limit Exceeded",
                    description=f"{api_name} rate limit exceeded",
                    error_details=str(error),
                    status="resolving",
                    playbook_applied="api_backoff"
                )
                session.add(event)
                await session.commit()
                
                incident_id = event.id
                print(f"[APIMonitor] Monitoring event created: {incident_id}")
        except Exception as e:
            print(f"[APIMonitor] Failed to log event: {e}")
            incident_id = None
        
        # Publish to Clarity event bus
        try:
            from backend.clarity import get_event_bus, Event
            bus = get_event_bus()
            await bus.publish(Event(
                event_type="api.rate_limit_exceeded",
                source="api_monitor",
                payload={
                    "incident_id": incident_id,
                    "api_name": api_name,
                    "retry_count": retry_count,
                    "backoff_seconds": backoff_seconds,
                    "retry_at": backoff_until.isoformat()
                }
            ))
            print(f"[APIMonitor] Published api.rate_limit_exceeded event")
        except Exception as e:
            print(f"[APIMonitor] Failed to publish event: {e}")
        
        return incident_id
    
    def get_status(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limit status"""
        if api_name:
            return {
                "api_name": api_name,
                "in_backoff": api_name in self.backoff_until,
                "backoff_until": self.backoff_until.get(api_name, datetime.now()).isoformat() if api_name in self.backoff_until else None
            }
        else:
            return {
                "apis_in_backoff": len(self.backoff_until),
                "backoff_apis": list(self.backoff_until.keys())
            }


# Global instance
api_monitor = APIRateLimitMonitor()


# Example usage helper
async def call_openai_with_monitoring(prompt: str):
    """
    Example: Call OpenAI API with automatic rate limit handling
    """
    async def make_call():
        # TODO: Replace with actual OpenAI call
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI()
        # response = await client.chat.completions.create(...)
        # return response
        
        # Simulate for now
        await asyncio.sleep(0.1)
        return {"result": "success"}
    
    return await api_monitor.call_with_monitoring("OpenAI", make_call)
