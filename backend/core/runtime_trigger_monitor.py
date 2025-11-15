"""
Runtime Trigger Monitor
Continuously runs all triggers and routes issues to self-healing/coding agent

Integrates:
- 10 advanced triggers
- Self-healing playbook execution
- Coding agent task submission
- Immutable logging
- Operator dashboard metrics
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RuntimeTriggerMonitor:
    """
    Runs all triggers in continuous loop
    Routes detected issues to repair systems
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 30  # Check every 30 seconds
        self.issue_counts: Dict[str, int] = {}
        self.last_check: Dict[str, datetime] = {}
        self.metrics: Dict[str, Any] = {
            'total_checks': 0,
            'issues_detected': 0,
            'actions_executed': 0,
            'last_run': None
        }
    
    async def start(self):
        """Start runtime trigger monitoring"""
        
        if self.running:
            return
        
        self.running = True
        logger.info("[RUNTIME-TRIGGERS] Starting continuous trigger monitoring")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[RUNTIME-TRIGGERS] Stopped")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        
        while self.running:
            try:
                await self._run_all_triggers()
                await asyncio.sleep(self.check_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[RUNTIME-TRIGGERS] Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Back off on error
    
    async def _run_all_triggers(self):
        """Run all triggers and route issues"""
        
        self.metrics['total_checks'] += 1
        self.metrics['last_run'] = datetime.utcnow()
        
        # Import all triggers
        try:
            from ..triggers import (
                health_signal_trigger,
                latency_queue_trigger,
                config_drift_trigger,
                dependency_regression_trigger,
                model_integrity_trigger,
                resource_pressure_trigger,
                pre_boot_code_diff_trigger,
                live_error_feed_trigger,
                telemetry_drift_trigger,
                predictive_failure_trigger
            )
            
            # Run all triggers in parallel
            trigger_tasks = [
                health_signal_trigger.check(),
                latency_queue_trigger.check(),
                config_drift_trigger.check(),
                dependency_regression_trigger.check(),
                model_integrity_trigger.check(),
                resource_pressure_trigger.check(),
                pre_boot_code_diff_trigger.check(),
                live_error_feed_trigger.check(),
                telemetry_drift_trigger.check(),
                predictive_failure_trigger.check()
            ]
            
            results = await asyncio.gather(*trigger_tasks, return_exceptions=True)
            
            # Process results
            for trigger_result in results:
                if trigger_result and not isinstance(trigger_result, Exception):
                    await self._handle_trigger_result(trigger_result)
        
        except Exception as e:
            logger.error(f"[RUNTIME-TRIGGERS] Failed to run triggers: {e}")
    
    async def _handle_trigger_result(self, result: Dict):
        """Route trigger result to appropriate repair system"""
        
        trigger_name = result.get('trigger')
        target = result.get('target')
        action = result.get('action')
        issues = result.get('issues', [])
        
        if not issues:
            return
        
        self.metrics['issues_detected'] += len(issues)
        
        # Track issue counts
        self.issue_counts[trigger_name] = self.issue_counts.get(trigger_name, 0) + len(issues)
        self.last_check[trigger_name] = datetime.utcnow()
        
        logger.info(f"[RUNTIME-TRIGGERS] {trigger_name} detected {len(issues)} issues → {target}")
        
        # Route to repair system
        if target == 'self_healing':
            await self._route_to_self_healing(action, issues)
        elif target == 'coding_agent':
            await self._route_to_coding_agent(action, issues)
        
        self.metrics['actions_executed'] += 1
    
    async def _route_to_self_healing(self, action: str, issues: List[Dict]):
        """Route to self-healing system"""
        
        try:
            from .control_plane import control_plane
            
            for issue in issues:
                await control_plane._execute_self_healing_actions([issue])
                logger.info(f"[RUNTIME-TRIGGERS] Executed self-healing action: {action}")
        
        except Exception as e:
            logger.error(f"[RUNTIME-TRIGGERS] Self-healing routing failed: {e}")
    
    async def _route_to_coding_agent(self, action: str, issues: List[Dict]):
        """Route to coding agent"""
        
        try:
            from ..agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
            
            for issue in issues[:5]:  # Top 5 issues
                # Create task description based on issue type
                task_desc = self._create_task_description(issue)
                
                # Submit task
                task = CodingTask(
                    task_id=f"runtime_{int(datetime.utcnow().timestamp())}_{issue['type']}",
                    task_type=CodingTaskType.FIX_BUG,
                    description=task_desc,
                    requirements=issue,
                    execution_mode=ExecutionMode.AUTO,
                    priority=8,  # High priority for runtime issues
                    created_at=datetime.utcnow()
                )
                
                await elite_coding_agent.submit_task(task)
                logger.info(f"[RUNTIME-TRIGGERS] Submitted coding task: {task_desc[:60]}")
        
        except Exception as e:
            logger.error(f"[RUNTIME-TRIGGERS] Coding agent routing failed: {e}")
    
    def _create_task_description(self, issue: Dict) -> str:
        """Create task description from issue"""
        
        issue_type = issue.get('type')
        
        if issue_type == 'schema_drift':
            endpoint = issue.get('endpoint')
            missing = issue.get('missing_fields', [])
            return f"Fix schema drift in {endpoint}: missing fields {missing}"
        
        elif issue_type == 'predicted_failure':
            file_path = issue.get('file')
            risk = issue.get('risk_score', 0)
            return f"Proactive code review for {file_path} (risk: {risk:.0%})"
        
        elif issue_type == 'repeated_error':
            error_sig = issue.get('error_signature')
            return f"Fix repeated error: {error_sig}"
        
        elif issue_type == 'version_change':
            pkg = issue.get('package')
            return f"Review dependency change: {pkg}"
        
        else:
            return f"Fix {issue_type}: {issue}"
    
    def get_metrics(self) -> Dict:
        """Get monitoring metrics for dashboard"""
        
        return {
            **self.metrics,
            'running': self.running,
            'check_interval': self.check_interval,
            'issue_counts': self.issue_counts,
            'triggers_monitored': 10
        }


# Global instance
runtime_trigger_monitor = RuntimeTriggerMonitor()
