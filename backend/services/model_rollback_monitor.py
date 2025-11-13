"""
Model Rollback Monitor
Background service that checks for model degradation and triggers rollbacks
Integrates with self-healing
"""

import asyncio
from typing import Dict, Any
from datetime import datetime


class ModelRollbackMonitor:
    """
    Monitors deployed models and triggers automatic rollbacks
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        self.check_interval = check_interval_seconds
        self.running = False
    
    async def start(self):
        """Start monitoring models"""
        self.running = True
        print("[ModelRollbackMonitor] Started")
        asyncio.create_task(self._monitor_loop())
    
    async def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                await self._check_all_models()
            except Exception as e:
                print(f"[ModelRollbackMonitor] Error: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def _check_all_models(self):
        """Check all production/canary models for rollback triggers"""
        from backend.services.model_registry import get_registry, DeploymentStage
        
        registry = get_registry()
        
        # Get models in production or canary
        production_models = registry.list_models(deploy_status=DeploymentStage.PRODUCTION)
        canary_models = registry.list_models(deploy_status=DeploymentStage.CANARY)
        
        models_to_check = production_models + canary_models
        
        for model in models_to_check:
            await self._check_model(model.model_id)
    
    async def _check_model(self, model_id: str):
        """Check if a specific model should be rolled back"""
        from backend.services.model_registry import get_registry
        
        registry = get_registry()
        
        # Check rollback triggers (10 minute window)
        should_rollback, reasons = registry.check_rollback_triggers(model_id, window_minutes=10)
        
        if should_rollback:
            print(f"[ModelRollbackMonitor] ROLLBACK TRIGGERED for {model_id}")
            print(f"[ModelRollbackMonitor] Reasons: {', '.join(reasons)}")
            
            await self._execute_rollback(model_id, reasons)
    
    async def _execute_rollback(self, model_id: str, reasons: List[str]):
        """Execute model rollback"""
        from backend.services.model_registry import get_registry, DeploymentStage
        
        registry = get_registry()
        
        # Update deployment status
        registry.update_deployment_status(model_id, DeploymentStage.ROLLBACK)
        
        # Create monitoring event
        try:
            from backend.monitoring_models import MonitoringEvent
            from backend.models import async_session
            
            async with async_session() as session:
                event = MonitoringEvent(
                    event_type="model.rollback",
                    severity="high",
                    source=model_id,
                    component="Model Registry",
                    title=f"Model {model_id} Rolled Back",
                    description=f"Automatic rollback triggered. Reasons: {'; '.join(reasons)}",
                    status="active",
                    playbook_applied="model_rollback"
                )
                session.add(event)
                await session.commit()
        except Exception as e:
            print(f"[ModelRollbackMonitor] Failed to log event: {e}")
        
        # Publish event
        try:
            from backend.clarity import get_event_bus, Event
            bus = get_event_bus()
            await bus.publish(Event(
                event_type="model.rollback.requested",
                source="model_rollback_monitor",
                payload={
                    "model_id": model_id,
                    "reasons": reasons,
                    "timestamp": datetime.now().isoformat()
                }
            ))
            print(f"[ModelRollbackMonitor] Published rollback event")
        except Exception as e:
            print(f"[ModelRollbackMonitor] Failed to publish event: {e}")
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        print("[ModelRollbackMonitor] Stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status"""
        return {
            "running": self.running,
            "check_interval_seconds": self.check_interval
        }


# Global instance
model_rollback_monitor = ModelRollbackMonitor()
