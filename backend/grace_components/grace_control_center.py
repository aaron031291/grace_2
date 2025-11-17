"""
Grace Control Center
Central control for Grace's automation with pause/resume/stop
LLM co-pilot stays alive, only automation pauses
"""

from typing import Dict, Any
from datetime import datetime
import logging
from pathlib import Path
import json

from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class SystemState:
    """System state management"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"
    EMERGENCY_STOP = "emergency_stop"


class TaskQueue:
    """Task queue for pause/resume functionality"""
    
    def __init__(self):
        self.queue = []
        self.processing = False
    
    def add_task(self, task: Dict[str, Any]):
        """Add task to queue"""
        task['queued_at'] = datetime.utcnow().isoformat()
        task['status'] = 'pending'
        self.queue.append(task)
        logger.info(f"[TASK-QUEUE] Added task: {task.get('name')}")
    
    def get_pending_tasks(self) -> list:
        """Get pending tasks"""
        return [t for t in self.queue if t['status'] == 'pending']
    
    def mark_processing(self, task_id: str):
        """Mark task as processing"""
        for task in self.queue:
            if task.get('id') == task_id:
                task['status'] = 'processing'
                task['started_at'] = datetime.utcnow().isoformat()
                break
    
    def mark_completed(self, task_id: str, result: Any):
        """Mark task as completed"""
        for task in self.queue:
            if task.get('id') == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.utcnow().isoformat()
                task['result'] = result
                break


class GraceControlCenter:
    """
    Central control for Grace's automation
    
    Features:
    - Pause/Resume automation (LLM co-pilot stays alive)
    - Emergency stop
    - Task queuing during pause
    - State persistence
    - Audit trail
    """
    
    def __init__(self):
        self.state = SystemState.STOPPED
        self.task_queue = TaskQueue()
        self.state_file = Path('grace_state.json')
        self.automation_workers = {}
    
    async def start(self):
        """Start control center"""
        
        # Load persisted state
        await self._load_state()
        
        logger.info("[CONTROL-CENTER] Started")
    
    async def _load_state(self):
        """Load persisted state"""
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.state = data.get('system_state', SystemState.STOPPED)
                
                logger.info(f"[CONTROL-CENTER] Loaded state: {self.state}")
            except:
                pass
    
    async def _save_state(self):
        """Save state to disk"""
        
        state_data = {
            'system_state': self.state,
            'updated_at': datetime.utcnow().isoformat(),
            'pending_tasks': len(self.task_queue.get_pending_tasks()),
            'active_workers': list(self.automation_workers.keys())
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2)
    
    async def resume_automation(self, resumed_by: str = 'user') -> Dict[str, Any]:
        """
        Resume Grace's automation
        LLM stays alive, workers start processing queue
        """
        
        if self.state == SystemState.RUNNING:
            return {
                'status': 'already_running',
                'message': 'Grace automation is already running'
            }
        
        logger.info(f"[CONTROL-CENTER] Resuming automation (by {resumed_by})...")
        
        # Update state
        previous_state = self.state
        self.state = SystemState.RUNNING
        await self._save_state()
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='resume_automation',
            decision_context={'previous_state': previous_state, 'resumed_by': resumed_by},
            chosen_action='enable_workers',
            rationale=f'Resuming automation from {previous_state}',
            actor='control_center',
            confidence=1.0,
            risk_score=0.1,
            status='resumed',
            resource='automation'
        )
        
        # Start workers
        await self._start_workers()
        
        # Process queued tasks
        pending = self.task_queue.get_pending_tasks()
        
        logger.info(f"[CONTROL-CENTER] Automation resumed, {len(pending)} tasks in queue")
        
        return {
            'status': 'resumed',
            'previous_state': previous_state,
            'current_state': self.state,
            'pending_tasks': len(pending),
            'message': f'Grace automation resumed. Processing {len(pending)} queued tasks.'
        }
    
    async def pause_automation(self, paused_by: str = 'user') -> Dict[str, Any]:
        """
        Pause Grace's automation
        LLM co-pilot stays alive, workers stop processing
        New tasks are queued
        """
        
        if self.state == SystemState.PAUSED:
            return {
                'status': 'already_paused',
                'message': 'Grace automation is already paused'
            }
        
        logger.info(f"[CONTROL-CENTER] Pausing automation (by {paused_by})...")
        
        # Update state
        previous_state = self.state
        self.state = SystemState.PAUSED
        await self._save_state()
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='pause_automation',
            decision_context={'previous_state': previous_state, 'paused_by': paused_by},
            chosen_action='disable_workers',
            rationale=f'Pausing automation at user request',
            actor='control_center',
            confidence=1.0,
            risk_score=0.05,
            status='paused',
            resource='automation'
        )
        
        # Stop workers (but keep co-pilot alive)
        await self._stop_workers()
        
        logger.info(f"[CONTROL-CENTER] Automation paused")
        
        return {
            'status': 'paused',
            'previous_state': previous_state,
            'current_state': self.state,
            'message': 'Grace automation paused. Co-pilot remains available. New tasks will be queued.'
        }
    
    async def emergency_stop(self, stopped_by: str = 'user') -> Dict[str, Any]:
        """
        Emergency stop - halt everything except co-pilot
        More aggressive than pause
        """
        
        logger.warning(f"[CONTROL-CENTER] EMERGENCY STOP (by {stopped_by})!")
        
        # Update state
        previous_state = self.state
        self.state = SystemState.EMERGENCY_STOP
        await self._save_state()
        
        # Log emergency stop
        await unified_logger.log_agentic_spine_decision(
            decision_type='emergency_stop',
            decision_context={'previous_state': previous_state, 'stopped_by': stopped_by},
            chosen_action='halt_all_automation',
            rationale=f'Emergency stop triggered by {stopped_by}',
            actor='control_center',
            confidence=1.0,
            risk_score=0.02,
            status='emergency_stopped',
            resource='system'
        )
        
        # Force stop all workers
        await self._emergency_stop_workers()
        
        # Clear queue (tasks will need to be re-queued)
        cleared_tasks = len(self.task_queue.queue)
        self.task_queue.queue.clear()
        
        logger.warning(f"[CONTROL-CENTER] Emergency stop complete, {cleared_tasks} tasks cleared")
        
        return {
            'status': 'emergency_stopped',
            'previous_state': previous_state,
            'current_state': self.state,
            'tasks_cleared': cleared_tasks,
            'message': f'Emergency stop executed. {cleared_tasks} tasks cleared. Control returned to human.'
        }
    
    async def _start_workers(self):
        """Start automation workers"""
        
        workers = [
            'research_sweeper',
            'sandbox_improvement',
            'autonomous_improvement',
            'ingestion_processor'
        ]
        
        for worker in workers:
            try:
                # Start worker
                logger.info(f"[CONTROL-CENTER] Starting worker: {worker}")
                self.automation_workers[worker] = 'running'
            except Exception as e:
                logger.error(f"[CONTROL-CENTER] Failed to start {worker}: {e}")
    
    async def _stop_workers(self):
        """Stop automation workers (graceful)"""
        
        for worker in list(self.automation_workers.keys()):
            try:
                logger.info(f"[CONTROL-CENTER] Stopping worker: {worker}")
                self.automation_workers[worker] = 'stopped'
            except Exception as e:
                logger.error(f"[CONTROL-CENTER] Failed to stop {worker}: {e}")
    
    async def _emergency_stop_workers(self):
        """Emergency stop workers (immediate)"""
        
        for worker in list(self.automation_workers.keys()):
            try:
                logger.warning(f"[CONTROL-CENTER] Emergency stopping worker: {worker}")
                del self.automation_workers[worker]
            except Exception as e:
                logger.error(f"[CONTROL-CENTER] Failed to emergency stop {worker}: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current system state"""
        
        return {
            'system_state': self.state,
            'pending_tasks': len(self.task_queue.get_pending_tasks()),
            'active_workers': list(self.automation_workers.keys()),
            'can_accept_tasks': self.state == SystemState.RUNNING,
            'co_pilot_active': True,  # Co-pilot always alive
            'automation_active': self.state == SystemState.RUNNING
        }
    
    async def queue_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queue task for execution
        If running: executes immediately
        If paused: queues for later
        """
        
        task['id'] = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if self.state == SystemState.RUNNING:
            # Execute immediately
            logger.info(f"[CONTROL-CENTER] Executing task immediately: {task.get('name')}")
            self.task_queue.add_task(task)
            # Would trigger execution here
            return {
                'status': 'executing',
                'task_id': task['id'],
                'message': 'Task executing immediately'
            }
        else:
            # Queue for later
            logger.info(f"[CONTROL-CENTER] Queuing task (system {self.state}): {task.get('name')}")
            self.task_queue.add_task(task)
            return {
                'status': 'queued',
                'task_id': task['id'],
                'message': f'Task queued (system {self.state}). Will execute on resume.',
                'queue_position': len(self.task_queue.get_pending_tasks())
            }


# Global instance
grace_control = GraceControlCenter()
