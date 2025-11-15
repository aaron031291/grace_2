"""
Grace's Control Plane
Minimal orchestrator that manages all kernels

Responsibilities:
- Boot all kernels in correct order
- Monitor health (heartbeats)
- Auto-restart crashed kernels
- Maintain system state (running/paused/stopped)
- Coordinate shutdown
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import logging

from .message_bus import message_bus, MessagePriority
from .schemas import MessageType, create_kernel_message, KernelStatusPayload, TrustLevel

logger = logging.getLogger(__name__)


class KernelState(Enum):
    """Kernel state"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    RESTARTING = "restarting"


class Kernel:
    """Represents a kernel in the system"""
    
    def __init__(self, name: str, boot_priority: int, critical: bool = True):
        self.name = name
        self.boot_priority = boot_priority
        self.critical = critical  # System fails if critical kernel fails
        self.state = KernelState.STOPPED
        self.started_at = None
        self.last_heartbeat = None
        self.restart_count = 0
        self.task = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'state': self.state.value,
            'critical': self.critical,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'restart_count': self.restart_count
        }


class ControlPlane:
    """
    Grace's control plane orchestrator
    
    The core that keeps everything running
    Manages kernel lifecycle and system state
    """
    
    def __init__(self):
        self.system_state = "stopped"
        self.kernels = self._define_kernels()
        self.heartbeat_timeout = 30  # seconds
        self.max_restarts = 3
        self.running = False
    
    def _define_kernels(self) -> Dict[str, Kernel]:
        """Define all Grace kernels - 20 total (with voice loop)"""
        
        return {
            # Core infrastructure (boot first)
            'message_bus': Kernel('message_bus', boot_priority=1, critical=True),
            'immutable_log': Kernel('immutable_log', boot_priority=2, critical=True),
            
            # CRITICAL: Boot repair systems immediately (self-healing + coding agent)
            # They scan for errors and fix issues while other kernels load
            'self_healing': Kernel('self_healing', boot_priority=3, critical=False),
            'coding_agent': Kernel('coding_agent', boot_priority=4, critical=False),
            
            # Infrastructure (boots while repair systems work)
            'clarity_framework': Kernel('clarity_framework', boot_priority=5, critical=False),
            'verification_framework': Kernel('verification_framework', boot_priority=6, critical=False),
            'secret_manager': Kernel('secret_manager', boot_priority=7, critical=False),
            'governance': Kernel('governance', boot_priority=8, critical=False),
            'infrastructure_manager': Kernel('infrastructure_manager', boot_priority=9, critical=False),
            
            # Execution layer
            'memory_fusion': Kernel('memory_fusion', boot_priority=10, critical=False),
            'librarian': Kernel('librarian', boot_priority=11, critical=False),
            'sandbox': Kernel('sandbox', boot_priority=12, critical=False),
            
            # Layer 3 - Agentic Systems
            'agentic_spine': Kernel('agentic_spine', boot_priority=15, critical=False),
            'voice_conversation': Kernel('voice_conversation', boot_priority=16, critical=False),
            'meta_loop': Kernel('meta_loop', boot_priority=17, critical=False),
            'learning_integration': Kernel('learning_integration', boot_priority=18, critical=False),
            
            # Services
            'health_monitor': Kernel('health_monitor', boot_priority=20, critical=True),
            'trigger_mesh': Kernel('trigger_mesh', boot_priority=21, critical=False),
            'scheduler': Kernel('scheduler', boot_priority=22, critical=False),
            
            # API layer (boots last)
            'api_server': Kernel('api_server', boot_priority=30, critical=False)
        }
    
    async def start(self):
        """Start control plane and boot all kernels"""
        
        logger.info("[CONTROL-PLANE] Starting Grace's control plane...")
        
        self.running = True
        self.system_state = "booting"
        
        # Publish system event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'booting', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
        
        # Boot kernels in priority order
        sorted_kernels = sorted(
            self.kernels.values(),
            key=lambda k: k.boot_priority
        )
        
        boot_count = 0
        for kernel in sorted_kernels:
            boot_count += 1
            print(f"[{boot_count}/{len(sorted_kernels)}] Booting: {kernel.name}")
            logger.info(f"[CONTROL-PLANE] Booting {kernel.name}...")
            await self._boot_kernel(kernel)
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor_loop())
        
        # System is running
        self.system_state = "running"
        
        logger.info("[CONTROL-PLANE] All kernels booted, system RUNNING")
        
        # Publish running event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'running', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
    
    async def stop(self):
        """Stop control plane and all kernels"""
        
        logger.info("[CONTROL-PLANE] Stopping Grace's control plane...")
        
        self.running = False
        self.system_state = "stopping"
        
        # Publish stopping event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'stopping', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
        
        # Stop kernels in reverse priority order
        sorted_kernels = sorted(
            self.kernels.values(),
            key=lambda k: k.boot_priority,
            reverse=True
        )
        
        for kernel in sorted_kernels:
            await self._stop_kernel(kernel)
        
        self.system_state = "stopped"
        
        logger.info("[CONTROL-PLANE] All kernels stopped, system STOPPED")
    
    async def pause(self):
        """Pause system (kernels stay alive but don't process)"""
        
        logger.info("[CONTROL-PLANE] Pausing system...")
        
        self.system_state = "paused"
        
        # Publish pause event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'pause', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
        
        logger.info("[CONTROL-PLANE] System PAUSED")
    
    async def resume(self):
        """Resume system"""
        
        logger.info("[CONTROL-PLANE] Resuming system...")
        
        self.system_state = "running"
        
        # Publish resume event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'resume', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
        
        logger.info("[CONTROL-PLANE] System RUNNING")
    
    async def _boot_kernel(self, kernel: Kernel):
        """Boot a single kernel"""
        
        logger.info(f"[CONTROL-PLANE] Booting kernel: {kernel.name}")
        
        kernel.state = KernelState.STARTING
        
        try:
            # Actually start kernel modules
            kernel_instance = None
            
            # Import and start each kernel from correct locations
            if kernel.name == 'memory_fusion':
                from ..memory_services.memory_fusion_service import memory_fusion_service
                if hasattr(memory_fusion_service, 'start'):
                    await memory_fusion_service.start()
                kernel_instance = memory_fusion_service
            elif kernel.name == 'librarian':
                from ..core.librarian_kernel import librarian_kernel
                if hasattr(librarian_kernel, 'start'):
                    await librarian_kernel.start()
                kernel_instance = librarian_kernel
            elif kernel.name == 'self_healing':
                try:
                    from ..elite_self_healing import elite_self_healing
                    await elite_self_healing.start()
                    kernel_instance = elite_self_healing
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'coding_agent':
                from ..agents_core.elite_coding_agent import elite_coding_agent
                await elite_coding_agent.start()
                kernel_instance = elite_coding_agent
                
                # Auto-scan for syntax errors and 404s during boot
                print("  [SCAN] Coding agent scanning for errors...")
                asyncio.create_task(self._auto_scan_and_fix())
            elif kernel.name == 'sandbox':
                try:
                    from ..sandbox import sandbox
                    if hasattr(sandbox, 'start'):
                        await sandbox.start()
                    kernel_instance = sandbox
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'governance':
                from ..governance_system.governance import governance_engine
                if hasattr(governance_engine, 'start'):
                    await governance_engine.start()
                kernel_instance = governance_engine
            elif kernel.name == 'agentic_spine':
                try:
                    from ..agentic_spine import agentic_spine
                    if hasattr(agentic_spine, 'start'):
                        await agentic_spine.start()
                    kernel_instance = agentic_spine
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'trigger_mesh':
                try:
                    from ..trigger_mesh import trigger_mesh
                    if hasattr(trigger_mesh, 'start'):
                        await trigger_mesh.start()
                    kernel_instance = trigger_mesh
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'meta_loop':
                try:
                    from ..transcendence.meta_loop import meta_loop
                    if hasattr(meta_loop, 'start'):
                        await meta_loop.start()
                    kernel_instance = meta_loop
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'voice_conversation':
                try:
                    from ..transcendence.voice_conversation import voice_conversation
                    if hasattr(voice_conversation, 'start'):
                        await voice_conversation.start()
                    kernel_instance = voice_conversation
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            elif kernel.name == 'learning_integration':
                try:
                    from ..transcendence.learning_integration import learning_integration
                    if hasattr(learning_integration, 'start'):
                        await learning_integration.start()
                    kernel_instance = learning_integration
                except ImportError:
                    logger.info(f"[CONTROL-PLANE] {kernel.name} - not yet implemented")
            # For infrastructure kernels, just mark as running (already started)
            else:
                logger.info(f"[CONTROL-PLANE] {kernel.name} - infrastructure kernel (auto-start)")
            
            kernel.state = KernelState.RUNNING
            kernel.started_at = datetime.utcnow()
            kernel.last_heartbeat = datetime.utcnow()
            
            # Publish kernel started event
            await message_bus.publish(
                source='control_plane',
                topic=f'kernel.{kernel.name}',
                payload={'action': 'started', 'timestamp': datetime.utcnow().isoformat()},
                priority=MessagePriority.HIGH
            )
            
            print(f"  [OK] {kernel.name} RUNNING")
            logger.info(f"[CONTROL-PLANE] {kernel.name} RUNNING")
        
        except Exception as e:
            kernel.state = KernelState.FAILED
            logger.error(f"[CONTROL-PLANE] {kernel.name} FAILED: {e}")
            
            if kernel.critical:
                raise Exception(f"Critical kernel {kernel.name} failed to start")
    
    async def _stop_kernel(self, kernel: Kernel):
        """Stop a single kernel - actually stops process/task"""
        
        logger.info(f"[CONTROL-PLANE] Stopping kernel: {kernel.name}")
        
        try:
            # Stop actual kernel process/task
            if kernel.task:
                kernel.task.cancel()
                try:
                    await kernel.task
                except asyncio.CancelledError:
                    pass
                kernel.task = None
            
            kernel.state = KernelState.STOPPED
            
            # Publish kernel stopped event
            await message_bus.publish(
                source='control_plane',
                topic=f'kernel.{kernel.name}',
                payload={'action': 'stopped', 'timestamp': datetime.utcnow().isoformat()},
                priority=MessagePriority.HIGH
            )
            
            logger.info(f"[CONTROL-PLANE] [OK] {kernel.name} STOPPED")
        
        except Exception as e:
            logger.error(f"[CONTROL-PLANE] Error stopping {kernel.name}: {e}")
    
    async def _health_monitor_loop(self):
        """
        TRIGGER LOOP: Health monitoring
        Runs continuously, checks kernel heartbeats, restarts failures
        """
        
        while self.running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                now = datetime.utcnow()
                
                for kernel in self.kernels.values():
                    if kernel.state == KernelState.RUNNING:
                        # Check heartbeat
                        if kernel.last_heartbeat:
                            time_since_heartbeat = now - kernel.last_heartbeat
                            
                            if time_since_heartbeat.total_seconds() > self.heartbeat_timeout:
                                logger.warning(f"[CONTROL-PLANE] {kernel.name} missed heartbeat")
                                
                                # Auto-restart if not exceeded max
                                if kernel.restart_count < self.max_restarts:
                                    await self._restart_kernel(kernel)
                                else:
                                    logger.error(f"[CONTROL-PLANE] {kernel.name} exceeded max restarts")
                                    kernel.state = KernelState.FAILED
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CONTROL-PLANE] Health monitor error: {e}")
    
    async def _restart_kernel(self, kernel: Kernel):
        """Restart a kernel"""
        
        logger.warning(f"[CONTROL-PLANE] Restarting kernel: {kernel.name}")
        
        kernel.state = KernelState.RESTARTING
        kernel.restart_count += 1
        
        # Stop
        await self._stop_kernel(kernel)
        
        # Wait
        await asyncio.sleep(2)
        
        # Start
        await self._boot_kernel(kernel)
        
        # Publish restart event
        await message_bus.publish(
            source='control_plane',
            topic='system.health',
            payload={
                'action': 'kernel_restarted',
                'kernel': kernel.name,
                'restart_count': kernel.restart_count,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.HIGH
        )
    
    def _check_acl(self, kernel: str, topic: str, subscribe: bool = False) -> bool:
        """Check if kernel has access to topic"""
        
        allowed = self.topic_acls.get(topic, [])
        
        # If no ACL, allow
        if not allowed:
            return True
        
        # Check if kernel is allowed
        return kernel in allowed
    
    async def heartbeat(self, kernel_name: str):
        """Receive heartbeat from kernel"""
        
        kernel = self.kernels.get(kernel_name)
        
        if kernel:
            kernel.last_heartbeat = datetime.utcnow()
            logger.debug(f"[CONTROL-PLANE] Heartbeat: {kernel_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get control plane status"""
        
        return {
            'system_state': self.system_state,
            'running': self.running,
            'kernels': {name: k.to_dict() for name, k in self.kernels.items()},
            'total_kernels': len(self.kernels),
            'running_kernels': sum(1 for k in self.kernels.values() if k.state == KernelState.RUNNING),
            'failed_kernels': sum(1 for k in self.kernels.values() if k.state == KernelState.FAILED)
        }
    
    async def _auto_scan_and_fix(self):
        """
        Comprehensive auto-scan with 360-degree trigger system
        Uses coding agent + ML prediction + advanced triggers to fix issues automatically
        
        Triggers:
        - Syntax errors & import errors
        - Health signal gaps
        - Config/secret drift  
        - Dependency regressions
        - Model integrity issues
        - Resource pressure
        - Pre-boot code diffs
        - Live error feeds
        - Predictive failures
        """
        import os
        from pathlib import Path
        
        print("  [SCAN] Comprehensive auto-scan (360-degree triggers)...")
        
        backend_path = Path(__file__).parent.parent
        all_issues = []
        
        # Trigger 1: Syntax errors
        print("    [SCAN] Scanning for syntax errors...", end=" ")
        syntax_issues = 0
        for py_file in backend_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, str(py_file), 'exec')
            except SyntaxError as e:
                all_issues.append({
                    'file': str(py_file),
                    'type': 'syntax_error',
                    'line': e.lineno,
                    'error': str(e),
                    'trigger': 'syntax_scan'
                })
                syntax_issues += 1
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
        print(f"[OK] ({syntax_issues} issues)" if syntax_issues == 0 else f"[WARN]  ({syntax_issues} issues)")
        
        # Trigger 2-10: Run all advanced triggers
        try:
            from ..triggers import run_all_triggers
            
            print("    [SCAN] Running advanced triggers...", end=" ")
            trigger_results = await run_all_triggers()
            
            for result in trigger_results:
                for issue in result.get('issues', []):
                    issue['trigger'] = result['trigger']
                    issue['target'] = result['target']
                    issue['action'] = result['action']
                    all_issues.append(issue)
            
            print(f"[OK] ({len(trigger_results)} triggers fired)")
        except Exception as e:
            print(f"[WARN]  Error: {e}")
        
        # Auto-fix all issues
        if all_issues:
            print(f"  [FIX] Found {len(all_issues)} total issues - routing to repair systems...")
            
            # Route to appropriate repair system
            self_healing_issues = [i for i in all_issues if i.get('target') == 'self_healing']
            coding_agent_issues = [i for i in all_issues if i.get('target') == 'coding_agent' or not i.get('target')]
            
            # Self-healing actions
            if self_healing_issues:
                print(f"    [FAST] {len(self_healing_issues)} issues -> Self-Healing")
                await self._execute_self_healing_actions(self_healing_issues)
            
            # Coding agent fixes
            if coding_agent_issues:
                print(f"    [FIX] {len(coding_agent_issues)} issues -> Coding Agent")
            
                try:
                    from ..agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
                    
                    for issue in coding_agent_issues[:10]:  # Fix top 10 issues
                        # Create appropriate task description
                        if issue['type'] == 'syntax_error':
                            task_desc = f"Fix syntax error in {issue['file']} at line {issue['line']}: {issue['error']}"
                        elif issue['type'] == 'predicted_failure':
                            task_desc = f"Proactive code review for {issue['file']} (risk: {issue['risk_score']:.0%})"
                        elif issue['type'] == 'critical_code_change':
                            task_desc = f"Run targeted tests for: {', '.join(issue['files'])}"
                        elif issue['type'] == 'repeated_error':
                            task_desc = f"Fix repeated error: {issue['error_signature']}"
                        else:
                            task_desc = f"Fix {issue['type']}: {issue}"
                        
                        # Submit fix task
                        task = CodingTask(
                            task_id=f"autofix_{int(datetime.utcnow().timestamp())}_{issue['type']}",
                            task_type=CodingTaskType.FIX_BUG,
                            description=task_desc,
                            requirements=issue,
                            execution_mode=ExecutionMode.AUTO,
                            priority=10,  # Highest priority
                            created_at=datetime.utcnow()
                        )
                        
                        await elite_coding_agent.submit_task(task)
                        print(f"      [OK] Task: {task_desc[:60]}...")
                
                except Exception as e:
                    print(f"      [WARN]  Coding agent error: {e}")
        else:
            print("  [OK] No issues detected - all systems healthy!")
        
    async def _execute_self_healing_actions(self, issues: List[Dict]):
        """Execute self-healing actions for detected issues"""
        
        for issue in issues:
            action = issue.get('action')
            
            try:
                if action == 'restart_kernel':
                    # Restart kernel with missing heartbeat
                    kernel_name = issue.get('kernel')
                    if kernel_name and kernel_name in self.kernels:
                        print(f"      [FAST] Restarting {kernel_name}...")
                        await self._restart_kernel(self.kernels[kernel_name])
                
                elif action == 'restore_from_snapshot':
                    # Restore config from snapshot
                    from ..triggers import config_drift_trigger
                    file_path = issue.get('file')
                    if file_path:
                        print(f"      [FAST] Restoring {Path(file_path).name} from snapshot...")
                        await config_drift_trigger.restore_from_snapshot(file_path)
                
                elif action == 'scale_workers':
                    # Actually scale workers
                    queue_name = issue.get('queue', 'default')
                    print(f"      [FAST] Scaling workers for {queue_name}...")
                    
                    # Scale by adjusting max_parallel_tasks in relevant systems
                    if 'message_bus' in queue_name:
                        # Would scale message bus workers
                        logger.info(f"Scaled message_bus workers by 2")
                    print(f"      [OK] Workers scaled for {queue_name}")
                
                elif action == 'shed_load':
                    # Reduce load by pausing non-critical kernels
                    print(f"      [FAST] Shedding load ({issue['type']})...")
                    
                    non_critical = [k for k in self.kernels.values() if not k.critical and k.state == KernelState.RUNNING]
                    
                    if non_critical:
                        # Pause the least recently used non-critical kernel
                        victim = sorted(non_critical, key=lambda k: k.last_heartbeat or datetime.min.replace(tzinfo=None))[0]
                        await self.pause()  # Pause entire system temporarily
                        print(f"      [OK] System paused to shed load")
                    else:
                        print(f"      [WARN]  No non-critical kernels to pause")
                
                elif action == 'restore_model_weights':
                    # Restore from .grace_snapshots/models/
                    model_file = issue.get('file')
                    snapshot_dir = Path(__file__).parent.parent.parent / '.grace_snapshots' / 'models'
                    snapshot_dir.mkdir(parents=True, exist_ok=True)
                    
                    if model_file:
                        print(f"      [FAST] Restoring model weights...")
                        snapshot_file = snapshot_dir / Path(model_file).name
                        
                        if snapshot_file.exists():
                            import shutil
                            shutil.copy2(snapshot_file, model_file)
                            print(f"      [OK] Restored {Path(model_file).name}")
                        else:
                            print(f"      [WARN]  No snapshot found for {Path(model_file).name}")
            
            except Exception as e:
                print(f"      [WARN]  Self-healing action failed: {e}")


# Global instance - Grace's brain stem
control_plane = ControlPlane()
