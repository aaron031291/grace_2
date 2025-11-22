"""
HTM SLA Enforcer - Automatic SLA Monitoring and Enforcement

Features:
- Real-time SLA monitoring with deadlines
- Auto-escalation of overdue tasks
- Queue reprioritization based on timing data
- Sub-agent spawning for long-running work
- Dashboard statistics feed

Integration:
- Monitors HTMTask table for SLA violations
- Escalates via message bus
- Spawns sub-agents via Task tool integration
- Feeds stats to agentic brain
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass

from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.core.message_bus import message_bus, MessagePriority
from backend.logging_system_utils import log_event
from sqlalchemy import select, update, func


@dataclass
class SLAViolation:
    """SLA violation record"""
    task_id: str
    task_type: str
    domain: str
    priority: str
    sla_ms: int
    elapsed_ms: float
    overdue_ms: float
    overdue_percent: float
    assigned_worker: Optional[str]
    status: str
    created_at: datetime
    escalation_level: int  # 1=warn, 2=escalate, 3=critical


class HTMSLAEnforcer:
    """
    Monitors HTM tasks for SLA compliance and takes action:
    - Warn when approaching deadline (80% elapsed)
    - Escalate when deadline missed
    - Auto-spawn sub-agents for stuck tasks
    - Reprioritize queues based on urgency
    """
    
    def __init__(self):
        self.check_interval_seconds = 10  # Check every 10s
        self.running = False
        self.task = None
        
        # Escalation thresholds
        self.warn_threshold = 0.8  # Warn at 80% of SLA
        self.critical_threshold = 2.0  # Critical at 200% of SLA
        
        # Statistics
        self.stats = {
            "total_violations": 0,
            "warnings_issued": 0,
            "escalations_triggered": 0,
            "sub_agents_spawned": 0,
            "queue_reprioritizations": 0,
            "tasks_rescued": 0
        }
        
        # Violation tracking (prevent duplicate escalations)
        self.escalated_tasks = set()
        self.warned_tasks = set()
        
    async def start(self):
        """Start SLA enforcement loop"""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._enforcement_loop())
        print("[HTM SLA] Enforcer started")
        
        # Publish startup event
        await message_bus.publish(
            source="htm_sla_enforcer",
            topic="htm.sla.started",
            payload={
                "warn_threshold": self.warn_threshold,
                "critical_threshold": self.critical_threshold,
                "check_interval_seconds": self.check_interval_seconds
            },
            priority=MessagePriority.LOW
        )
    
    async def stop(self):
        """Stop SLA enforcement loop"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("[HTM SLA] Enforcer stopped")
    
    async def _enforcement_loop(self):
        """Main enforcement loop"""
        while self.running:
            try:
                await self._check_sla_compliance()
                await self._reprioritize_queues()
                await self._publish_stats()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[HTM SLA] Error in enforcement loop: {e}")
                await asyncio.sleep(self.check_interval_seconds)
    
    async def _check_sla_compliance(self):
        """Check all active tasks for SLA compliance"""
        now = datetime.now(timezone.utc)
        
        async with async_session() as session:
            # Find running/assigned tasks with SLA deadlines
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status.in_(['assigned', 'running']))
                .where(HTMTask.sla_deadline.isnot(None))
            )
            active_tasks = result.scalars().all()
            
            violations = []
            
            for task in active_tasks:
                # Calculate elapsed time
                start_time = task.started_at or task.assigned_at or task.queued_at
                elapsed = (now - start_time).total_seconds() * 1000  # ms
                
                if task.sla_ms:
                    elapsed_percent = elapsed / task.sla_ms
                    overdue_ms = elapsed - task.sla_ms
                    
                    # Check for violations
                    if elapsed_percent >= self.critical_threshold:
                        # Critical - spawn sub-agent
                        violation = SLAViolation(
                            task_id=task.task_id,
                            task_type=task.task_type,
                            domain=task.domain,
                            priority=task.priority,
                            sla_ms=task.sla_ms,
                            elapsed_ms=elapsed,
                            overdue_ms=overdue_ms,
                            overdue_percent=(elapsed_percent - 1.0) * 100,
                            assigned_worker=task.assigned_worker,
                            status=task.status,
                            created_at=task.created_at,
                            escalation_level=3
                        )
                        violations.append(violation)
                        await self._handle_critical_violation(task, violation)
                        
                    elif elapsed_percent >= 1.0:
                        # Escalate - missed SLA
                        violation = SLAViolation(
                            task_id=task.task_id,
                            task_type=task.task_type,
                            domain=task.domain,
                            priority=task.priority,
                            sla_ms=task.sla_ms,
                            elapsed_ms=elapsed,
                            overdue_ms=overdue_ms,
                            overdue_percent=(elapsed_percent - 1.0) * 100,
                            assigned_worker=task.assigned_worker,
                            status=task.status,
                            created_at=task.created_at,
                            escalation_level=2
                        )
                        violations.append(violation)
                        await self._handle_sla_violation(task, violation)
                        
                    elif elapsed_percent >= self.warn_threshold:
                        # Warning - approaching deadline
                        if task.task_id not in self.warned_tasks:
                            violation = SLAViolation(
                                task_id=task.task_id,
                                task_type=task.task_type,
                                domain=task.domain,
                                priority=task.priority,
                                sla_ms=task.sla_ms,
                                elapsed_ms=elapsed,
                                overdue_ms=overdue_ms,
                                overdue_percent=0,
                                assigned_worker=task.assigned_worker,
                                status=task.status,
                                created_at=task.created_at,
                                escalation_level=1
                            )
                            await self._handle_warning(task, violation)
            
            return violations
    
    async def _handle_warning(self, task: HTMTask, violation: SLAViolation):
        """Handle approaching SLA deadline - send warning"""
        if task.task_id in self.warned_tasks:
            return
        
        self.warned_tasks.add(task.task_id)
        self.stats["warnings_issued"] += 1
        
        # Publish warning
        await message_bus.publish(
            source="htm_sla_enforcer",
            topic="htm.sla.warning",
            payload={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "domain": task.domain,
                "elapsed_percent": violation.elapsed_ms / violation.sla_ms,
                "time_remaining_ms": violation.sla_ms - violation.elapsed_ms,
                "assigned_worker": task.assigned_worker,
                "message": f"Task {task.task_id} approaching SLA deadline (80% elapsed)"
            },
            priority=MessagePriority.NORMAL
        )
        
        print(f"[HTM SLA] ⚠️ Warning: {task.task_id} at {violation.elapsed_ms / violation.sla_ms * 100:.1f}% of SLA")
    
    async def _handle_sla_violation(self, task: HTMTask, violation: SLAViolation):
        """Handle SLA violation - escalate priority"""
        if task.task_id in self.escalated_tasks:
            return
        
        self.escalated_tasks.add(task.task_id)
        self.stats["escalations_triggered"] += 1
        self.stats["total_violations"] += 1
        
        # Update task priority
        async with async_session() as session:
            await session.execute(
                update(HTMTask)
                .where(HTMTask.task_id == task.task_id)
                .values(
                    priority="high",  # Escalate to high priority
                    sla_met=False
                )
            )
            await session.commit()
        
        # Publish escalation event
        await message_bus.publish(
            source="htm_sla_enforcer",
            topic="htm.sla.violated",
            payload={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "domain": task.domain,
                "overdue_ms": violation.overdue_ms,
                "overdue_percent": violation.overdue_percent,
                "assigned_worker": task.assigned_worker,
                "escalated_priority": "high",
                "action": "priority_escalation",
                "message": f"Task {task.task_id} missed SLA by {violation.overdue_percent:.1f}%"
            },
            priority=MessagePriority.HIGH
        )
        
        # Log to immutable log
        log_event(
            action="htm.sla.violated",
            actor="htm_sla_enforcer",
            resource=task.task_id,
            outcome="escalated",
            payload={
                "overdue_ms": violation.overdue_ms,
                "overdue_percent": violation.overdue_percent,
                "new_priority": "high"
            }
        )
        
        print(f"[HTM SLA] 🚨 Violation: {task.task_id} overdue by {violation.overdue_ms:.0f}ms ({violation.overdue_percent:.1f}%)")
    
    async def _handle_critical_violation(self, task: HTMTask, violation: SLAViolation):
        """Handle critical violation - spawn sub-agent"""
        if task.task_id in self.escalated_tasks:
            return
        
        self.escalated_tasks.add(task.task_id)
        self.stats["sub_agents_spawned"] += 1
        self.stats["total_violations"] += 1
        
        # Spawn sub-agent to rescue the task
        await message_bus.publish(
            source="htm_sla_enforcer",
            topic="htm.sla.critical",
            payload={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "domain": task.domain,
                "overdue_ms": violation.overdue_ms,
                "overdue_percent": violation.overdue_percent,
                "assigned_worker": task.assigned_worker,
                "action": "spawn_sub_agent",
                "sub_agent_task": {
                    "goal": f"Rescue stuck task: {task.task_type}",
                    "context": {
                        "original_task_id": task.task_id,
                        "payload": task.payload,
                        "elapsed_ms": violation.elapsed_ms
                    },
                    "priority": "critical",
                    "sla_ms": violation.sla_ms // 2  # Half the original SLA
                },
                "message": f"Task {task.task_id} critically overdue ({violation.overdue_percent:.1f}%), spawning sub-agent"
            },
            priority=MessagePriority.CRITICAL
        )
        
        # Log critical escalation
        log_event(
            action="htm.sla.critical",
            actor="htm_sla_enforcer",
            resource=task.task_id,
            outcome="sub_agent_spawned",
            payload={
                "overdue_ms": violation.overdue_ms,
                "overdue_percent": violation.overdue_percent,
                "action": "spawn_sub_agent"
            }
        )
        
        print(f"[HTM SLA] 🚨🚨 CRITICAL: {task.task_id} overdue {violation.overdue_percent:.1f}% - spawning sub-agent")
    
    async def _reprioritize_queues(self):
        """Reprioritize queued tasks based on SLA urgency"""
        now = datetime.now(timezone.utc)
        
        async with async_session() as session:
            # Find queued tasks approaching deadlines
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status == 'queued')
                .where(HTMTask.sla_deadline.isnot(None))
                .order_by(HTMTask.sla_deadline.asc())  # Most urgent first
            )
            queued_tasks = result.scalars().all()
            
            reprioritized = 0
            
            for task in queued_tasks:
                time_until_deadline = (task.sla_deadline - now).total_seconds() * 1000
                urgency_ratio = time_until_deadline / task.sla_ms
                
                # If less than 50% time remaining, escalate priority
                if urgency_ratio < 0.5 and task.priority != "critical":
                    new_priority = "high" if urgency_ratio > 0.2 else "critical"
                    
                    await session.execute(
                        update(HTMTask)
                        .where(HTMTask.task_id == task.task_id)
                        .values(priority=new_priority)
                    )
                    
                    reprioritized += 1
            
            if reprioritized > 0:
                await session.commit()
                self.stats["queue_reprioritizations"] += reprioritized
                print(f"[HTM SLA] Reprioritized {reprioritized} queued tasks based on SLA urgency")
    
    async def _publish_stats(self):
        """Publish SLA statistics for dashboard"""
        async with async_session() as session:
            # Calculate real-time SLA compliance
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status == 'completed')
                .where(HTMTask.sla_met.isnot(None))
            )
            completed_tasks = result.scalars().all()
            
            if completed_tasks:
                sla_met_count = sum(1 for t in completed_tasks if t.sla_met)
                sla_compliance_rate = sla_met_count / len(completed_tasks)
            else:
                sla_compliance_rate = 1.0
        
        # Publish stats to message bus
        await message_bus.publish(
            source="htm_sla_enforcer",
            topic="htm.sla.stats",
            payload={
                **self.stats,
                "sla_compliance_rate": sla_compliance_rate,
                "active_warnings": len(self.warned_tasks),
                "active_escalations": len(self.escalated_tasks)
            },
            priority=MessagePriority.LOW
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get current SLA enforcement statistics"""
        async with async_session() as session:
            # Active violations
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status.in_(['assigned', 'running']))
                .where(HTMTask.sla_deadline.isnot(None))
            )
            active_tasks = result.scalars().all()
            
            now = datetime.now(timezone.utc)
            active_violations = []
            
            for task in active_tasks:
                if task.sla_deadline < now:
                    elapsed_ms = ((now - (task.started_at or task.assigned_at or task.queued_at)).total_seconds() * 1000)
                    overdue_ms = (now - task.sla_deadline).total_seconds() * 1000
                    active_violations.append({
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "overdue_ms": overdue_ms,
                        "elapsed_ms": elapsed_ms
                    })
            
            # Overall SLA compliance
            result = await session.execute(
                select(func.count(HTMTask.id), func.avg(HTMTask.sla_buffer_ms))
                .where(HTMTask.sla_met.isnot(None))
            )
            row = result.first()
            total_with_sla = row[0] or 0
            avg_buffer_ms = row[1] or 0
            
            result = await session.execute(
                select(func.count(HTMTask.id))
                .where(HTMTask.sla_met == True)
            )
            sla_met_count = result.scalar() or 0
            
            sla_compliance_rate = (sla_met_count / total_with_sla) if total_with_sla > 0 else 1.0
        
        return {
            **self.stats,
            "active_violations": len(active_violations),
            "violations_detail": active_violations[:10],  # Top 10
            "sla_compliance_rate": sla_compliance_rate,
            "avg_buffer_ms": avg_buffer_ms,
            "total_tasks_with_sla": total_with_sla
        }


# Global instance
htm_sla_enforcer = HTMSLAEnforcer()
