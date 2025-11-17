"""
Boot Pipeline
Structured startup sequence with dependency management and verification

Part of Grace's unbreakable core - ensures clean, verifiable boot
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import logging

from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class BootStage(Enum):
    """Boot pipeline stages"""
    PRE_INIT = "pre_init"
    CORE_INIT = "core_init"
    KERNEL_INIT = "kernel_init"
    SERVICE_INIT = "service_init"
    API_INIT = "api_init"
    POST_INIT = "post_init"
    VERIFICATION = "verification"
    READY = "ready"


class BootStep:
    """Single step in boot pipeline"""
    
    def __init__(
        self,
        name: str,
        stage: BootStage,
        execute_fn: Callable,
        dependencies: List[str] = None,
        critical: bool = True,
        verification_fn: Optional[Callable] = None
    ):
        self.name = name
        self.stage = stage
        self.execute_fn = execute_fn
        self.dependencies = dependencies or []
        self.critical = critical
        self.verification_fn = verification_fn
        
        # Execution tracking
        self.started_at = None
        self.completed_at = None
        self.status = 'pending'  # pending, running, success, failed
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'stage': self.stage.value,
            'status': self.status,
            'critical': self.critical,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': (
                (self.completed_at - self.started_at).total_seconds() * 1000
                if self.started_at and self.completed_at else None
            ),
            'error': self.error
        }


class BootPipeline:
    """
    Structured boot pipeline
    
    Ensures:
    - Dependencies resolved before execution
    - Each step verified
    - Complete audit trail
    - Graceful failure handling
    - Progress visibility
    """
    
    def __init__(self):
        self.steps = {}
        self.current_stage = BootStage.PRE_INIT
        self.boot_id = None
        self.boot_start_time = None
        self.boot_end_time = None
    
    def register_step(self, step: BootStep):
        """Register boot step"""
        self.steps[step.name] = step
        logger.debug(f"[BOOT-PIPELINE] Registered step: {step.name}")
    
    async def execute_pipeline(self) -> Dict[str, Any]:
        """
        Execute complete boot pipeline
        
        Returns:
            Boot result with timing and status
        """
        
        self.boot_id = f"boot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.boot_start_time = datetime.utcnow()
        
        logger.info(f"[BOOT-PIPELINE] Starting boot: {self.boot_id}")
        
        result = {
            'boot_id': self.boot_id,
            'started_at': self.boot_start_time.isoformat(),
            'stages_completed': [],
            'steps_executed': [],
            'steps_failed': [],
            'status': 'unknown'
        }
        
        # Log boot start
        await immutable_log.append(
            actor='boot_pipeline',
            action='boot_start',
            resource='grace_system',
            decision={'boot_id': self.boot_id},
            metadata={'timestamp': self.boot_start_time.isoformat()}
        )
        
        # Execute stages in order
        stages = [
            BootStage.PRE_INIT,
            BootStage.CORE_INIT,
            BootStage.KERNEL_INIT,
            BootStage.SERVICE_INIT,
            BootStage.API_INIT,
            BootStage.POST_INIT,
            BootStage.VERIFICATION
        ]
        
        try:
            for stage in stages:
                self.current_stage = stage
                logger.info(f"[BOOT-PIPELINE] Stage: {stage.value}")
                
                # Execute all steps in this stage
                success = await self._execute_stage(stage)
                
                if success:
                    result['stages_completed'].append(stage.value)
                else:
                    # Critical stage failed
                    result['status'] = 'failed'
                    result['failed_stage'] = stage.value
                    break
            
            # If all stages completed
            if len(result['stages_completed']) == len(stages):
                self.current_stage = BootStage.READY
                result['status'] = 'success'
                logger.info("[BOOT-PIPELINE] Boot complete - system READY")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"[BOOT-PIPELINE] Boot failed: {e}")
        
        self.boot_end_time = datetime.utcnow()
        result['completed_at'] = self.boot_end_time.isoformat()
        result['duration_seconds'] = (self.boot_end_time - self.boot_start_time).total_seconds()
        
        # Collect step results
        for step_name, step in self.steps.items():
            step_result = step.to_dict()
            
            if step.status == 'success':
                result['steps_executed'].append(step_result)
            elif step.status == 'failed':
                result['steps_failed'].append(step_result)
        
        # Log boot complete
        await immutable_log.append(
            actor='boot_pipeline',
            action='boot_complete',
            resource='grace_system',
            decision={
                'boot_id': self.boot_id,
                'status': result['status'],
                'duration_seconds': result['duration_seconds']
            },
            metadata=result
        )
        
        return result
    
    async def _execute_stage(self, stage: BootStage) -> bool:
        """Execute all steps in a stage"""
        
        # Get steps for this stage
        stage_steps = [
            step for step in self.steps.values()
            if step.stage == stage
        ]
        
        if not stage_steps:
            return True  # No steps in this stage
        
        # Execute steps (respecting dependencies)
        for step in stage_steps:
            success = await self._execute_step(step)
            
            if not success and step.critical:
                logger.error(f"[BOOT-PIPELINE] Critical step failed: {step.name}")
                return False
        
        return True
    
    async def _execute_step(self, step: BootStep) -> bool:
        """Execute single boot step"""
        
        # Check dependencies
        for dep in step.dependencies:
            dep_step = self.steps.get(dep)
            if not dep_step or dep_step.status != 'success':
                logger.warning(f"[BOOT-PIPELINE] {step.name} waiting for dependency: {dep}")
                return False
        
        # Execute
        step.status = 'running'
        step.started_at = datetime.utcnow()
        
        logger.info(f"[BOOT-PIPELINE] Executing: {step.name}")
        
        try:
            # Call execute function
            step.result = await step.execute_fn()
            
            # Verify if verification function provided
            if step.verification_fn:
                verified = await step.verification_fn(step.result)
                if not verified:
                    raise Exception(f"Verification failed for {step.name}")
            
            step.status = 'success'
            step.completed_at = datetime.utcnow()
            
            duration = (step.completed_at - step.started_at).total_seconds() * 1000
            logger.info(f"[BOOT-PIPELINE] ✓ {step.name} ({duration:.1f}ms)")
            
            return True
        
        except Exception as e:
            step.status = 'failed'
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            
            logger.error(f"[BOOT-PIPELINE] ✗ {step.name}: {e}")
            
            return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current boot progress"""
        
        total_steps = len(self.steps)
        completed_steps = sum(1 for s in self.steps.values() if s.status == 'success')
        failed_steps = sum(1 for s in self.steps.values() if s.status == 'failed')
        
        return {
            'boot_id': self.boot_id,
            'current_stage': self.current_stage.value,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'progress_percent': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'status': 'booting' if self.current_stage != BootStage.READY else 'ready'
        }


# Global instance
boot_pipeline = BootPipeline()
