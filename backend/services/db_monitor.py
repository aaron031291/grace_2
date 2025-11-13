"""
Database Monitor
Instruments database connections to detect failures and trigger self-healing
"""

import asyncio
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import OperationalError, DBAPIError
from contextlib import asynccontextmanager


class DatabaseMonitor:
    """
    Monitors database connections and publishes events on failure
    Integrates with Clarity event bus
    """
    
    def __init__(self):
        self.connection_failures = 0
        self.last_failure = None
        self.is_connected = True
    
    async def log_connection_failure(
        self,
        error: Exception,
        host: str = "localhost",
        database: str = "grace.db",
        retry_count: int = 0
    ):
        """
        Log a database connection failure and trigger self-healing
        """
        self.connection_failures += 1
        self.last_failure = datetime.now()
        self.is_connected = False
        
        print(f"[DBMonitor] Connection lost to {database} (attempt {retry_count + 1})")
        
        # Create monitoring event
        try:
            from backend.monitoring_models import MonitoringEvent
            from backend.models import async_session
            
            async with async_session() as session:
                event = MonitoringEvent(
                    event_type="db.connection_lost",
                    severity="high",
                    source=f"{database}@{host}",
                    component="PostgreSQL Connector",
                    title="Database Connection Lost",
                    description=f"Lost connection to database {database}",
                    error_details=str(error),
                    status="active",
                    playbook_applied="db_reconnect"
                )
                session.add(event)
                await session.commit()
                
                incident_id = event.id
                print(f"[DBMonitor] Monitoring event created: {incident_id}")
        except Exception as e:
            print(f"[DBMonitor] Failed to log monitoring event: {e}")
            incident_id = None
        
        # Publish to Clarity event bus
        try:
            from backend.clarity import get_event_bus, Event
            bus = get_event_bus()
            await bus.publish(Event(
                event_type="db.connection_lost",
                source="db_monitor",
                payload={
                    "incident_id": incident_id,
                    "database": database,
                    "host": host,
                    "retry_count": retry_count,
                    "error": str(error)[:200]
                }
            ))
            print(f"[DBMonitor] Published db.connection_lost event")
        except Exception as e:
            print(f"[DBMonitor] Failed to publish event: {e}")
        
        return incident_id
    
    async def log_connection_restored(self, incident_id: Optional[int] = None):
        """
        Log when connection is restored
        """
        self.is_connected = True
        print(f"[DBMonitor] Connection restored!")
        
        # Update monitoring event
        if incident_id:
            try:
                from backend.monitoring_models import MonitoringEvent
                from backend.models import async_session
                
                async with async_session() as session:
                    event = await session.get(MonitoringEvent, incident_id)
                    if event:
                        event.status = "resolved"
                        event.resolved_at = datetime.now()
                        if event.detected_at:
                            delta = datetime.now() - event.detected_at
                            event.resolution_time_seconds = delta.total_seconds()
                        event.auto_fixed = True
                        await session.commit()
                        print(f"[DBMonitor] Incident {incident_id} marked resolved")
            except Exception as e:
                print(f"[DBMonitor] Failed to update incident: {e}")
        
        # Publish restoration event
        try:
            from backend.clarity import get_event_bus, Event
            bus = get_event_bus()
            await bus.publish(Event(
                event_type="db.connection_restored",
                source="db_monitor",
                payload={"incident_id": incident_id}
            ))
        except Exception:
            pass
    
    @asynccontextmanager
    async def monitored_connection(self, engine):
        """
        Context manager for monitored database connections
        Automatically detects and reports failures
        """
        retry_count = 0
        max_retries = 3
        incident_id = None
        
        while retry_count < max_retries:
            try:
                async with engine.begin() as conn:
                    # Connection successful
                    if incident_id:
                        await self.log_connection_restored(incident_id)
                        incident_id = None
                    
                    yield conn
                    return
            except (OperationalError, DBAPIError) as e:
                # Connection failed
                incident_id = await self.log_connection_failure(
                    error=e,
                    retry_count=retry_count
                )
                
                retry_count += 1
                if retry_count < max_retries:
                    # Exponential backoff
                    wait_time = 2 ** retry_count
                    print(f"[DBMonitor] Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[DBMonitor] Max retries exceeded - escalating")
                    raise
    
    def get_status(self):
        """Get monitor status"""
        return {
            "is_connected": self.is_connected,
            "total_failures": self.connection_failures,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None
        }


# Global instance
db_monitor = DatabaseMonitor()
