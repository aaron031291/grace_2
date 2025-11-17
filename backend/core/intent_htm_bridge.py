"""
Intent-HTM Bridge - Complete Layer 3 ↔ Layer 2 Integration

Features:
- Bidirectional ID sharing between intents and HTM tasks
- Context propagation from brain to execution
- Completion event flow back to learning loop
- Real-time status synchronization

Architecture:
    Layer 3 (Agentic Brain)
         ↓ Intent submission
    Intent API
         ↓ Task creation with intent_id
    HTM (Layer 2)
         ↓ Execution updates
    Intent API
         ↓ Outcome feedback
    Learning Loop (Layer 3)
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from backend.core.intent_api import IntentAPI, Intent, IntentStatus, IntentOutcome, IntentRecord
from backend.core.message_bus import message_bus, MessagePriority
from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from sqlalchemy import select, update


class IntentHTMBridge:
    """
    Bridges intent API and HTM for complete integration
    
    Responsibilities:
    - Convert intents to HTM tasks with linked IDs
    - Propagate context from intent to task payload
    - Subscribe to HTM completion events
    - Update intent status based on task progress
    - Feed outcomes to learning loop
    """
    
    def __init__(self):
        self.intent_api = IntentAPI()
        self.active_mappings: Dict[str, str] = {}  # intent_id -> task_id
        self.task_to_intent: Dict[str, str] = {}  # task_id -> intent_id
        self.running = False
        self._task = None
    
    async def start(self):
        """Start the bridge and subscribe to events"""
        if self.running:
            return
        
        await self.intent_api.initialize()
        
        # Subscribe to intent events
        message_bus.subscribe("agentic.intent.created", self._handle_intent_created)
        
        # Subscribe to HTM events
        message_bus.subscribe("htm.task.completed", self._handle_task_completed)
        message_bus.subscribe("htm.task.failed", self._handle_task_failed)
        message_bus.subscribe("htm.task.timeout", self._handle_task_timeout)
        message_bus.subscribe("htm.task.update", self._handle_task_update)
        
        self.running = True
        self._task = asyncio.create_task(self._sync_loop())
        
        print("[INTENT-HTM BRIDGE] Started - Layer 3 ↔ Layer 2 connected")
        
        # Publish bridge ready event
        await message_bus.publish(
            source="intent_htm_bridge",
            topic="bridge.ready",
            payload={
                "layer3": "agentic_brain",
                "layer2": "htm",
                "features": [
                    "id_sharing",
                    "context_propagation",
                    "bidirectional_events",
                    "learning_feedback"
                ]
            },
            priority=MessagePriority.LOW
        )
    
    async def stop(self):
        """Stop the bridge"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[INTENT-HTM BRIDGE] Stopped")
    
    async def submit_intent_as_task(
        self,
        intent: Intent,
        task_handler: str
    ) -> str:
        """
        Submit intent and create HTM task with linked IDs
        
        Args:
            intent: Intent from agentic brain
            task_handler: HTM handler to execute task
            
        Returns:
            task_id created in HTM
        """
        # Submit intent to intent API
        intent_id = await self.intent_api.submit_intent(intent)
        
        # Create HTM task with intent linkage
        task_id = f"task_{intent.domain}_{datetime.now(timezone.utc).timestamp()}"
        
        # Store bidirectional mapping
        self.active_mappings[intent_id] = task_id
        self.task_to_intent[task_id] = intent_id
        
        # Calculate payload size
        from backend.core.htm_size_tracker import PayloadSizeCalculator
        payload_dict = {
            **intent.context,
            "goal": intent.goal,
            "expected_outcome": intent.expected_outcome,
            "confidence": intent.confidence,
            "risk_level": intent.risk_level,
            "created_by": intent.created_by,
            "origin": "intent"  # Tag origin
        }
        data_size_bytes = PayloadSizeCalculator.for_json(payload_dict)
        
        # Route task
        from backend.core.htm_advanced_routing import htm_router
        routing_decision = await htm_router.route_task(
            task_id=task_id,
            task_type=intent.domain,
            priority=intent.priority.value,
            payload=payload_dict,
            created_by=intent.created_by,
            data_size_bytes=data_size_bytes
        )
        
        # Create HTM task with intent context + routing metadata
        async with async_session() as session:
            htm_task = HTMTask(
                task_id=task_id,
                task_type=intent.domain,
                domain=intent.domain,
                priority=intent.priority.value,
                intent_id=intent_id,  # Link to intent
                payload=payload_dict,
                data_size_bytes=data_size_bytes,  # Add size
                sla_ms=intent.sla_ms,
                sla_deadline=datetime.now(timezone.utc).timestamp() + (intent.sla_ms / 1000),
                created_by=intent.created_by
            )
            session.add(htm_task)
            await session.commit()
        
        # Update intent with task ID
        async with async_session() as session:
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(
                    htm_task_id=task_id,
                    status="executing"
                )
            )
            await session.commit()
        
        # Publish task creation event
        await message_bus.publish(
            source="intent_htm_bridge",
            topic="htm.task.created",
            payload={
                "task_id": task_id,
                "intent_id": intent_id,
                "task_type": intent.domain,
                "handler": task_handler,
                "goal": intent.goal,
                "sla_ms": intent.sla_ms,
                "context_keys": list(intent.context.keys())
            },
            priority=MessagePriority.NORMAL
        )
        
        log_event(
            action="intent_to_task",
            actor="intent_htm_bridge",
            resource=task_id,
            outcome="created",
            payload={
                "intent_id": intent_id,
                "task_id": task_id,
                "domain": intent.domain,
                "goal": intent.goal
            }
        )
        
        print(f"[INTENT-HTM BRIDGE] Intent {intent_id} → Task {task_id}")
        
        return task_id
    
    async def _handle_intent_created(self, event: Dict[str, Any]):
        """Handle intent creation - could auto-convert to task"""
        # This is called when intent is created
        # Orchestrator decides when to convert to task
        pass
    
    async def _handle_task_update(self, event: Dict[str, Any]):
        """Handle task progress updates"""
        task_id = event.get("task_id")
        if not task_id or task_id not in self.task_to_intent:
            return
        
        intent_id = self.task_to_intent[task_id]
        status = event.get("status")
        
        # Map HTM status to intent status
        if status == "running":
            intent_status = "executing"
        elif status == "completed":
            intent_status = "completed"
        elif status in ["failed", "timeout"]:
            intent_status = "failed"
        else:
            return
        
        # Update intent status
        async with async_session() as session:
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(status=intent_status)
            )
            await session.commit()
    
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Handle task completion - feed outcome to intent and learning loop"""
        task_id = event.get("task_id")
        if not task_id or task_id not in self.task_to_intent:
            return
        
        intent_id = self.task_to_intent[task_id]
        
        # Load task details
        async with async_session() as session:
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.task_id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return
            
            # Create intent outcome
            outcome = IntentOutcome(
                intent_id=intent_id,
                status=IntentStatus.COMPLETED,
                result=task.result or {},
                execution_time_ms=task.total_time_ms or 0,
                success=task.success or False,
                metrics={
                    "queue_time_ms": task.queue_time_ms,
                    "execution_time_ms": task.execution_time_ms,
                    "attempt_number": task.attempt_number,
                    "sla_met": task.sla_met,
                    "sla_buffer_ms": task.sla_buffer_ms
                }
            )
            
            # Update intent record
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(
                    status="completed",
                    success=task.success,
                    sla_met=task.sla_met,
                    actual_execution_ms=task.total_time_ms,
                    completed_at=datetime.now(timezone.utc),
                    result=task.result
                )
            )
            await session.commit()
        
        # Feed to learning loop
        await self._feed_to_learning_loop(intent_id, outcome)
        
        # Publish completion event for agentic brain
        await message_bus.publish(
            source="intent_htm_bridge",
            topic="agentic.intent.completed",
            payload={
                "intent_id": intent_id,
                "task_id": task_id,
                "success": outcome.success,
                "execution_time_ms": outcome.execution_time_ms,
                "sla_met": task.sla_met,
                "result": outcome.result,
                "metrics": outcome.metrics
            },
            priority=MessagePriority.HIGH
        )
        
        log_event(
            action="task_to_intent_completion",
            actor="intent_htm_bridge",
            resource=intent_id,
            outcome="completed",
            payload={
                "task_id": task_id,
                "success": outcome.success,
                "execution_time_ms": outcome.execution_time_ms
            }
        )
        
        print(f"[INTENT-HTM BRIDGE] Task {task_id} → Intent {intent_id} completed")
        
        # Cleanup mapping
        if intent_id in self.active_mappings:
            del self.active_mappings[intent_id]
        if task_id in self.task_to_intent:
            del self.task_to_intent[task_id]
    
    async def _handle_task_failed(self, event: Dict[str, Any]):
        """Handle task failure"""
        task_id = event.get("task_id")
        if not task_id or task_id not in self.task_to_intent:
            return
        
        intent_id = self.task_to_intent[task_id]
        error_message = event.get("error_message", "Unknown error")
        
        # Update intent as failed
        async with async_session() as session:
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(
                    status="failed",
                    success=False,
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await session.commit()
        
        # Notify agentic brain
        await message_bus.publish(
            source="intent_htm_bridge",
            topic="agentic.intent.failed",
            payload={
                "intent_id": intent_id,
                "task_id": task_id,
                "error": error_message
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"[INTENT-HTM BRIDGE] Task {task_id} → Intent {intent_id} failed: {error_message}")
        
        # Cleanup
        if intent_id in self.active_mappings:
            del self.active_mappings[intent_id]
        if task_id in self.task_to_intent:
            del self.task_to_intent[task_id]
    
    async def _handle_task_timeout(self, event: Dict[str, Any]):
        """Handle task timeout"""
        task_id = event.get("task_id")
        if not task_id or task_id not in self.task_to_intent:
            return
        
        intent_id = self.task_to_intent[task_id]
        
        # Update intent as timeout
        async with async_session() as session:
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(
                    status="timeout",
                    success=False,
                    sla_met=False,
                    completed_at=datetime.now(timezone.utc)
                )
            )
            await session.commit()
        
        # Notify agentic brain
        await message_bus.publish(
            source="intent_htm_bridge",
            topic="agentic.intent.timeout",
            payload={
                "intent_id": intent_id,
                "task_id": task_id
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"[INTENT-HTM BRIDGE] Task {task_id} → Intent {intent_id} timeout")
        
        # Cleanup
        if intent_id in self.active_mappings:
            del self.active_mappings[intent_id]
        if task_id in self.task_to_intent:
            del self.task_to_intent[task_id]
    
    async def _feed_to_learning_loop(self, intent_id: str, outcome: IntentOutcome):
        """Feed intent outcome to learning loop for continuous improvement"""
        try:
            from backend.learning_systems.learning_loop import learning_loop
            
            # Get intent details
            async with async_session() as session:
                result = await session.execute(
                    select(IntentRecord)
                    .where(IntentRecord.intent_id == intent_id)
                )
                intent_record = result.scalar_one_or_none()
                
                if not intent_record:
                    return
                
                # Record outcome in learning loop
                await learning_loop.record_outcome(
                    action_type=f"intent_{intent_record.domain}",
                    success=outcome.success,
                    error_pattern=intent_record.goal,
                    playbook_id=f"intent_pipeline_{intent_record.domain}",
                    confidence_score=intent_record.confidence,
                    execution_time=outcome.execution_time_ms / 1000,  # Convert to seconds
                    context={
                        "intent_id": intent_id,
                        "goal": intent_record.goal,
                        "domain": intent_record.domain,
                        "sla_met": intent_record.sla_met,
                        "metrics": outcome.metrics
                    }
                )
                
                # Mark as learned from
                await session.execute(
                    update(IntentRecord)
                    .where(IntentRecord.intent_id == intent_id)
                    .values(learned_from=True)
                )
                await session.commit()
                
                print(f"[INTENT-HTM BRIDGE] Fed intent {intent_id} to learning loop")
                
        except Exception as e:
            print(f"[INTENT-HTM BRIDGE] Failed to feed to learning loop: {e}")
    
    async def _sync_loop(self):
        """Periodic sync between intent and task status"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Sync every 30s
                
                # Check for orphaned tasks (task completed but intent not updated)
                async with async_session() as session:
                    for intent_id, task_id in list(self.active_mappings.items()):
                        result = await session.execute(
                            select(HTMTask)
                            .where(HTMTask.task_id == task_id)
                        )
                        task = result.scalar_one_or_none()
                        
                        if task and task.status in ['completed', 'failed', 'timeout']:
                            # Trigger completion handler
                            await message_bus.publish(
                                source="intent_htm_bridge",
                                topic=f"htm.task.{task.status}",
                                payload={"task_id": task_id},
                                priority=MessagePriority.NORMAL
                            )
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[INTENT-HTM BRIDGE] Sync error: {e}")
    
    async def get_bridge_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        return {
            "active_mappings": len(self.active_mappings),
            "mappings": {
                "intent_to_task": dict(list(self.active_mappings.items())[:10]),
                "task_to_intent": dict(list(self.task_to_intent.items())[:10])
            },
            "running": self.running
        }


# Global instance
intent_htm_bridge = IntentHTMBridge()
