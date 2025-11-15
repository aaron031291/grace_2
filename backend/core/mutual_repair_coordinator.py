"""
Mutual Repair Coordinator
Enables coding agent and self-healing to fix each other

Features:
- Cross-component health monitoring
- Mutual repair triggers
- Deadlock detection and breaking
- Safe restart coordination
- State preservation during mutual repair
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MutualRepairCoordinator:
    """
    Coordinates mutual repair between coding agent and self-healing
    Ensures they can fix each other without deadlock
    """
    
    def __init__(self):
        self.running = False
        self.monitoring_interval = 60  # Check every minute
        
        # Health state
        self.coding_agent_healthy = True
        self.self_healing_healthy = True
        self.last_mutual_check: Optional[datetime] = None
        
        # Deadlock detection
        self.coding_agent_stuck_count = 0
        self.self_healing_stuck_count = 0
        self.deadlock_threshold = 3
        
        # Repair coordination
        self.repair_in_progress = False
        self.current_repair_target: Optional[str] = None
    
    async def start(self):
        """Start mutual repair coordinator"""
        
        if self.running:
            return
        
        self.running = True
        logger.info("[MUTUAL-REPAIR] Starting coordinator")
        
        # Start monitoring loop
        asyncio.create_task(self._mutual_monitoring_loop())
    
    async def stop(self):
        """Stop coordinator"""
        self.running = False
    
    async def _mutual_monitoring_loop(self):
        """Continuous mutual health monitoring"""
        
        while self.running:
            try:
                await self._check_mutual_health()
                await asyncio.sleep(self.monitoring_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[MUTUAL-REPAIR] Monitoring error: {e}", exc_info=True)
                await asyncio.sleep(120)
    
    async def _check_mutual_health(self):
        """Check health of both components"""
        
        self.last_mutual_check = datetime.utcnow()
        
        # Check coding agent
        coding_health = await self._check_coding_agent()
        
        # Check self-healing
        healing_health = await self._check_self_healing()
        
        # Detect issues
        if not coding_health['healthy'] and not self.repair_in_progress:
            await self._trigger_self_healing_to_fix_coding_agent(coding_health)
        
        if not healing_health['healthy'] and not self.repair_in_progress:
            await self._trigger_coding_agent_to_fix_self_healing(healing_health)
        
        # Detect deadlock
        if not coding_health['healthy'] and not healing_health['healthy']:
            await self._handle_deadlock()
    
    async def _check_coding_agent(self) -> Dict:
        """Check coding agent health"""
        
        health = {
            'healthy': True,
            'issues': []
        }
        
        try:
            from ..agents_core.elite_coding_agent import elite_coding_agent
            
            # Check if running
            if not elite_coding_agent.running:
                health['healthy'] = False
                health['issues'].append('not_running')
            
            # Check task queue depth
            queue_depth = len(elite_coding_agent.task_queue)
            if queue_depth > 100:
                health['healthy'] = False
                health['issues'].append(f'queue_overload_{queue_depth}')
            
            # Check if stuck (same active task for >5 min)
            if elite_coding_agent.active_tasks:
                # Would check task age here
                pass
            
            # Check resource usage
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                cpu = process.cpu_percent(interval=0.1)
                
                if cpu > 95:
                    self.coding_agent_stuck_count += 1
                    if self.coding_agent_stuck_count >= 3:
                        health['healthy'] = False
                        health['issues'].append('stuck_loop_high_cpu')
                else:
                    self.coding_agent_stuck_count = 0
            except:
                pass
            
            self.coding_agent_healthy = health['healthy']
        
        except Exception as e:
            health['healthy'] = False
            health['issues'].append(f'exception_{str(e)[:50]}')
        
        return health
    
    async def _check_self_healing(self) -> Dict:
        """Check self-healing health"""
        
        health = {
            'healthy': True,
            'issues': []
        }
        
        try:
            # Check playbook engine
            from .advanced_playbook_engine import advanced_playbook_engine
            
            if not advanced_playbook_engine.running:
                health['healthy'] = False
                health['issues'].append('not_running')
            
            # Check recent playbook failure rate
            if advanced_playbook_engine.execution_history:
                recent = advanced_playbook_engine.execution_history[-10:]
                failures = sum(1 for e in recent if not e.get('success'))
                
                if failures > 7:  # 70% failure rate
                    health['healthy'] = False
                    health['issues'].append(f'high_failure_rate_{failures}/10')
            
            # Check if stuck in loop
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                cpu = process.cpu_percent(interval=0.1)
                
                if cpu > 90:
                    self.self_healing_stuck_count += 1
                    if self.self_healing_stuck_count >= 3:
                        health['healthy'] = False
                        health['issues'].append('stuck_loop_high_cpu')
                else:
                    self.self_healing_stuck_count = 0
            except:
                pass
            
            self.self_healing_healthy = health['healthy']
        
        except Exception as e:
            health['healthy'] = False
            health['issues'].append(f'exception_{str(e)[:50]}')
        
        return health
    
    async def _trigger_self_healing_to_fix_coding_agent(self, health: Dict):
        """
        Self-healing fixes coding agent
        Restart, rollback patches, quarantine bad changes
        """
        
        logger.warning(f"[MUTUAL-REPAIR] Self-healing fixing coding agent: {health['issues']}")
        
        self.repair_in_progress = True
        self.current_repair_target = 'coding_agent'
        
        try:
            from .advanced_playbook_engine import advanced_playbook_engine, Severity
            
            # Determine which playbook to run
            if 'stuck_loop_high_cpu' in health['issues']:
                playbook = 'coding_agent_stuck_loop'
            elif 'not_running' in health['issues']:
                playbook = 'coding_agent_crash_recovery'
            else:
                playbook = 'coding_agent_crash_recovery'  # Default
            
            # Execute repair playbook
            result = await advanced_playbook_engine.execute_playbook(
                playbook_name=playbook,
                context={
                    'kernel': 'coding_agent',
                    'health_issues': health['issues'],
                    'repaired_by': 'self_healing'
                },
                severity=Severity.CRITICAL
            )
            
            if result['success']:
                logger.info(f"[MUTUAL-REPAIR] Self-healing successfully repaired coding agent")
            else:
                logger.error(f"[MUTUAL-REPAIR] Self-healing failed to repair coding agent")
        
        except Exception as e:
            logger.error(f"[MUTUAL-REPAIR] Repair failed: {e}")
        
        finally:
            self.repair_in_progress = False
            self.current_repair_target = None
    
    async def _trigger_coding_agent_to_fix_self_healing(self, health: Dict):
        """
        Coding agent fixes self-healing
        Patch playbooks, fix execution logic, refactor loops
        """
        
        logger.warning(f"[MUTUAL-REPAIR] Coding agent fixing self-healing: {health['issues']}")
        
        self.repair_in_progress = True
        self.current_repair_target = 'self_healing'
        
        try:
            from ..agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
            
            # Create repair task
            if 'high_failure_rate' in str(health['issues']):
                description = """
Self-Healing Playbook Failure Rate Too High

Issues: {issues}

Tasks:
1. Analyze recent playbook execution history
2. Identify failing playbooks and root causes
3. Fix playbook logic or add missing error handling
4. Validate all playbooks pass basic execution tests
5. Update playbook documentation

Files to check:
- playbooks/*.yaml
- backend/core/advanced_playbook_engine.py
- backend/services/playbook_engine.py

Acceptance:
- All playbooks parse without errors
- Failure rate < 30%
- Run 5 sample playbooks successfully
""".format(issues=health['issues'])
                
                task_type = CodingTaskType.FIX_BUG
            
            elif 'stuck_loop' in str(health['issues']):
                description = """
Self-Healing Stuck in Infinite Loop

Issues: {issues}

Tasks:
1. Analyze playbook execution engine for infinite loops
2. Add loop detection and breaking logic
3. Add timeout enforcement
4. Refactor complex loops to simpler patterns

Files to check:
- backend/core/advanced_playbook_engine.py
- backend/services/playbook_engine.py

Intent: REDUCE_COMPLEXITY

Acceptance:
- CPU usage < 50% during playbook execution
- All loops have timeout guards
- Add loop iteration counters
""".format(issues=health['issues'])
                
                task_type = CodingTaskType.REFACTOR
            
            else:
                description = f"Fix self-healing kernel issues: {health['issues']}"
                task_type = CodingTaskType.FIX_BUG
            
            task = CodingTask(
                task_id=f"repair_self_healing_{int(datetime.utcnow().timestamp())}",
                task_type=task_type,
                description=description,
                requirements={
                    'health_issues': health['issues'],
                    'repaired_by': 'coding_agent',
                    'mutual_repair': True
                },
                execution_mode=ExecutionMode.AUTO,  # Auto-apply for mutual repair
                priority=10,  # Critical
                created_at=datetime.utcnow()
            )
            
            await elite_coding_agent.submit_task(task)
            
            logger.info(f"[MUTUAL-REPAIR] Coding agent repair task created: {task.task_id}")
        
        except Exception as e:
            logger.error(f"[MUTUAL-REPAIR] Repair failed: {e}")
        
        finally:
            self.repair_in_progress = False
            self.current_repair_target = None
    
    async def _handle_deadlock(self):
        """
        Handle deadlock when both components are unhealthy
        Restart both in coordinated sequence
        """
        
        logger.critical("[MUTUAL-REPAIR] DEADLOCK DETECTED - Both components unhealthy")
        
        self.repair_in_progress = True
        
        try:
            from .control_plane import control_plane
            
            # Strategy: Restart in dependency order with stagger
            
            # Step 1: Force restart self-healing first (simpler component)
            logger.info("[MUTUAL-REPAIR] Step 1: Restarting self-healing")
            
            sh_kernel = control_plane.kernels.get('self_healing')
            if sh_kernel:
                await control_plane._restart_kernel(sh_kernel)
                await asyncio.sleep(5)  # Wait for stabilization
            
            # Step 2: Restart coding agent
            logger.info("[MUTUAL-REPAIR] Step 2: Restarting coding agent")
            
            ca_kernel = control_plane.kernels.get('coding_agent')
            if ca_kernel:
                await control_plane._restart_kernel(ca_kernel)
                await asyncio.sleep(10)  # Wait for task processing to resume
            
            # Step 3: Verify both recovered
            await asyncio.sleep(5)
            
            coding_health = await self._check_coding_agent()
            healing_health = await self._check_self_healing()
            
            if coding_health['healthy'] and healing_health['healthy']:
                logger.info("[MUTUAL-REPAIR] Deadlock resolved - both components healthy")
            else:
                logger.error("[MUTUAL-REPAIR] Deadlock persists - escalating to human")
                await self._escalate_to_human()
        
        except Exception as e:
            logger.error(f"[MUTUAL-REPAIR] Deadlock handling failed: {e}")
        
        finally:
            self.repair_in_progress = False
    
    async def _escalate_to_human(self):
        """Escalate to human when mutual repair fails"""
        
        logger.critical("[MUTUAL-REPAIR] ESCALATING TO HUMAN - Automated repair failed")
        
        try:
            from .message_bus import message_bus
            
            await message_bus.publish(
                source='mutual_repair_coordinator',
                topic='alert.critical',
                payload={
                    'alert_type': 'mutual_repair_failure',
                    'message': 'Both coding agent and self-healing unhealthy - manual intervention required',
                    'coding_agent_healthy': self.coding_agent_healthy,
                    'self_healing_healthy': self.self_healing_healthy,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        
        except Exception as e:
            logger.error(f"[MUTUAL-REPAIR] Could not escalate: {e}")
    
    def get_status(self) -> Dict:
        """Get mutual repair status"""
        
        return {
            'running': self.running,
            'coding_agent_healthy': self.coding_agent_healthy,
            'self_healing_healthy': self.self_healing_healthy,
            'repair_in_progress': self.repair_in_progress,
            'current_repair_target': self.current_repair_target,
            'last_check': self.last_mutual_check.isoformat() if self.last_mutual_check else None,
            'deadlock_risk': not self.coding_agent_healthy and not self.self_healing_healthy
        }


# Global instance
mutual_repair_coordinator = MutualRepairCoordinator()
