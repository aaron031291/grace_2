"""
Agent Orchestrator
Coordinates tiered agent execution pipeline with Guardian oversight

Pipeline: research → design → implement → test → deploy
- Guardian can pause/override at any phase
- Artifacts flow between phases
- All results feed learning loop
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from .tiered_agent_framework import (
    AgentPhase,
    AgentStatus,
    AgentResult,
    AgentArtifact,
    AGENT_REGISTRY
)

logger = logging.getLogger(__name__)


class PipelineStatus:
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentPipeline:
    """Represents a full agent execution pipeline"""
    
    def __init__(
        self,
        pipeline_id: str,
        task: str,
        context: Dict[str, Any],
        phases: Optional[List[AgentPhase]] = None
    ):
        self.pipeline_id = pipeline_id
        self.task = task
        self.context = context
        self.phases = phases or [
            AgentPhase.RESEARCH,
            AgentPhase.DESIGN,
            AgentPhase.IMPLEMENT,
            AgentPhase.TEST,
            AgentPhase.DEPLOY
        ]
        
        self.status = PipelineStatus.PENDING
        self.current_phase: Optional[AgentPhase] = None
        self.phase_results: Dict[AgentPhase, AgentResult] = {}
        self.all_artifacts: List[AgentArtifact] = []
        
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        
        # Guardian control
        self.guardian_paused = False
        self.guardian_override: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'pipeline_id': self.pipeline_id,
            'task': self.task,
            'status': self.status,
            'current_phase': self.current_phase.value if self.current_phase else None,
            'phases': [p.value for p in self.phases],
            'phase_results': {
                p.value: r.to_dict() for p, r in self.phase_results.items()
            },
            'artifacts_count': len(self.all_artifacts),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
            'guardian_paused': self.guardian_paused
        }


class AgentOrchestrator:
    """
    Orchestrates tiered agent execution
    
    Features:
    - Pipeline coordination (research → design → implement → test → deploy)
    - Guardian oversight (pause/override capability)
    - Artifact collection and flow
    - Learning loop integration
    - Event publishing
    """
    
    def __init__(self):
        self.running = False
        self.pipelines: Dict[str, AgentPipeline] = {}
        self.active_pipelines: List[str] = []
        
        # Configuration
        self.max_concurrent_pipelines = 2
        self.auto_recover_on_failure = True
        
        # Statistics
        self.stats = {
            'pipelines_started': 0,
            'pipelines_completed': 0,
            'pipelines_failed': 0,
            'total_artifacts': 0
        }
        
        # Dependencies
        self.message_bus = None
        self.guardian = None
        self.immutable_log = None
        self.learning_loop = None
    
    async def start(self):
        """Start the agent orchestrator"""
        if self.running:
            return
        
        logger.info("[AGENT-ORCHESTRATOR] Starting agent orchestrator...")
        
        # Initialize dependencies
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
            
            # Subscribe to Guardian control events
            await self.message_bus.subscribe('guardian.pause_pipeline', self._handle_guardian_pause)
            await self.message_bus.subscribe('guardian.resume_pipeline', self._handle_guardian_resume)
            await self.message_bus.subscribe('guardian.override_pipeline', self._handle_guardian_override)
        except ImportError:
            logger.warning("[AGENT-ORCHESTRATOR] Message bus not available")
        
        try:
            from backend.core.guardian import guardian
            self.guardian = guardian
        except ImportError:
            logger.warning("[AGENT-ORCHESTRATOR] Guardian not available")
        
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[AGENT-ORCHESTRATOR] Immutable log not available")
        
        self.running = True
        
        logger.info("[AGENT-ORCHESTRATOR] ✅ Started")
        logger.info(f"[AGENT-ORCHESTRATOR] Max concurrent pipelines: {self.max_concurrent_pipelines}")
    
    async def stop(self):
        """Stop the agent orchestrator"""
        self.running = False
        logger.info("[AGENT-ORCHESTRATOR] Stopped")
    
    async def execute_pipeline(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        phases: Optional[List[AgentPhase]] = None
    ) -> str:
        """
        Execute a full agent pipeline
        
        Args:
            task: Task description
            context: Initial context
            phases: Optional custom phase list
            
        Returns:
            Pipeline ID
        """
        pipeline_id = f"pipeline_{uuid4().hex[:8]}"
        
        pipeline = AgentPipeline(
            pipeline_id=pipeline_id,
            task=task,
            context=context or {},
            phases=phases
        )
        
        self.pipelines[pipeline_id] = pipeline
        self.stats['pipelines_started'] += 1
        
        logger.info(f"[AGENT-ORCHESTRATOR] 🚀 Pipeline started: {pipeline_id}")
        logger.info(f"[AGENT-ORCHESTRATOR]   Task: {task}")
        logger.info(f"[AGENT-ORCHESTRATOR]   Phases: {[p.value for p in pipeline.phases]}")
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='agent_pipeline',
                subcategory='started',
                data=pipeline.to_dict(),
                actor='agent_orchestrator',
                action='start_pipeline',
                resource=pipeline_id
            )
        
        # Publish event
        if self.message_bus:
            await self.message_bus.publish('pipeline.started', pipeline.to_dict())
        
        # Execute pipeline asynchronously
        asyncio.create_task(self._execute_pipeline_async(pipeline))
        
        return pipeline_id
    
    async def _execute_pipeline_async(self, pipeline: AgentPipeline):
        """Execute pipeline phases sequentially"""
        
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.utcnow()
        
        try:
            for phase in pipeline.phases:
                pipeline.current_phase = phase
                
                logger.info(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Starting phase: {phase.value}")
                
                # Check if Guardian paused pipeline
                if pipeline.guardian_paused:
                    logger.warning(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Paused by Guardian")
                    pipeline.status = PipelineStatus.PAUSED
                    
                    # Wait for resume
                    while pipeline.guardian_paused:
                        await asyncio.sleep(1)
                    
                    logger.info(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Resumed by Guardian")
                    pipeline.status = PipelineStatus.RUNNING
                
                # Check for Guardian override
                if pipeline.guardian_override:
                    logger.info(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Guardian override active")
                    phase_context = {
                        **pipeline.context,
                        'guardian_override': pipeline.guardian_override
                    }
                else:
                    phase_context = self._build_phase_context(pipeline, phase)
                
                # Create agent for this phase
                agent_class = AGENT_REGISTRY.get(phase)
                if not agent_class:
                    raise Exception(f"No agent registered for phase: {phase.value}")
                
                agent = agent_class()
                
                # Execute agent
                result = await agent.execute(phase_context)
                
                # Store result
                pipeline.phase_results[phase] = result
                pipeline.all_artifacts.extend(result.artifacts)
                self.stats['total_artifacts'] += len(result.artifacts)
                
                # Check if phase failed
                if result.status == AgentStatus.FAILED:
                    if self.auto_recover_on_failure:
                        logger.warning(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Phase {phase.value} failed, attempting recovery...")
                        
                        # Try recovery playbook
                        recovered = await self._attempt_recovery(pipeline, phase, result)
                        
                        if not recovered:
                            raise Exception(f"Phase {phase.value} failed and recovery unsuccessful")
                    else:
                        raise Exception(f"Phase {phase.value} failed: {result.error}")
                
                logger.info(f"[AGENT-ORCHESTRATOR] [{pipeline.pipeline_id}] Phase {phase.value} completed")
                
                # Feed artifacts to learning loop
                await self._feed_artifacts_to_learning_loop(pipeline, result)
            
            # Pipeline completed successfully
            pipeline.status = PipelineStatus.COMPLETED
            pipeline.completed_at = datetime.utcnow()
            self.stats['pipelines_completed'] += 1
            
            logger.info(f"[AGENT-ORCHESTRATOR] ✅ Pipeline completed: {pipeline.pipeline_id}")
            logger.info(f"[AGENT-ORCHESTRATOR]   Artifacts: {len(pipeline.all_artifacts)}")
            logger.info(f"[AGENT-ORCHESTRATOR]   Duration: {(pipeline.completed_at - pipeline.started_at).total_seconds():.1f}s")
            
            # Publish completion
            if self.message_bus:
                await self.message_bus.publish('pipeline.completed', pipeline.to_dict())
        
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            pipeline.error = str(e)
            pipeline.completed_at = datetime.utcnow()
            self.stats['pipelines_failed'] += 1
            
            logger.error(f"[AGENT-ORCHESTRATOR] ❌ Pipeline failed: {pipeline.pipeline_id} - {e}")
            
            # Publish failure
            if self.message_bus:
                await self.message_bus.publish('pipeline.failed', pipeline.to_dict())
            
            # Emit to learning loop
            try:
                from backend.learning_systems.event_emitters import agent_events
                await agent_events.emit_task_failed(
                    agent='agent_orchestrator',
                    task=pipeline.task,
                    error=str(e)
                )
            except ImportError:
                pass
        
        finally:
            # Log completion
            if self.immutable_log:
                await self.immutable_log.append_entry(
                    category='agent_pipeline',
                    subcategory='completed' if pipeline.status == PipelineStatus.COMPLETED else 'failed',
                    data=pipeline.to_dict(),
                    actor='agent_orchestrator',
                    action='complete_pipeline',
                    resource=pipeline.pipeline_id
                )
    
    def _build_phase_context(self, pipeline: AgentPipeline, phase: AgentPhase) -> Dict[str, Any]:
        """Build context for phase execution with artifacts from previous phases"""
        
        context = {
            **pipeline.context,
            'pipeline_id': pipeline.pipeline_id,
            'task': pipeline.task
        }
        
        # Add artifacts from previous phases
        for prev_phase in AgentPhase:
            if prev_phase.value >= phase.value:
                break
            
            if prev_phase in pipeline.phase_results:
                result = pipeline.phase_results[prev_phase]
                context[f'{prev_phase.value}_artifacts'] = [a.to_dict() for a in result.artifacts]
        
        return context
    
    async def _attempt_recovery(
        self,
        pipeline: AgentPipeline,
        failed_phase: AgentPhase,
        result: AgentResult
    ) -> bool:
        """Attempt to recover from phase failure"""
        
        logger.info(f"[AGENT-ORCHESTRATOR] Attempting recovery for phase: {failed_phase.value}")
        
        # Use recovery playbook
        try:
            from backend.core.guardian_playbooks import guardian_playbook_registry
            
            recovery_playbook = guardian_playbook_registry.get_playbook('phase_failure_recovery')
            
            if recovery_playbook:
                recovery_result = await recovery_playbook.execute({
                    'pipeline_id': pipeline.pipeline_id,
                    'failed_phase': failed_phase.value,
                    'error': result.error
                })
                
                if recovery_result.get('success', False):
                    logger.info(f"[AGENT-ORCHESTRATOR] Recovery successful for: {failed_phase.value}")
                    return True
        
        except Exception as e:
            logger.error(f"[AGENT-ORCHESTRATOR] Recovery attempt failed: {e}")
        
        return False
    
    async def _feed_artifacts_to_learning_loop(
        self,
        pipeline: AgentPipeline,
        result: AgentResult
    ):
        """Feed phase artifacts to learning loop for continuous improvement"""
        
        if not result.artifacts:
            return
        
        try:
            from backend.learning_systems.event_emitters import agent_events
            
            # Emit artifact creation events
            for artifact in result.artifacts:
                await agent_events.emit(
                    'agent.artifact.created',
                    {
                        'pipeline_id': pipeline.pipeline_id,
                        'phase': result.phase.value,
                        'artifact_type': artifact.artifact_type,
                        'artifact_id': artifact.artifact_id,
                        'playbooks_used': result.playbooks_used
                    },
                    severity='low'
                )
            
            logger.info(f"[AGENT-ORCHESTRATOR] Fed {len(result.artifacts)} artifacts to learning loop")
        
        except Exception as e:
            logger.warning(f"[AGENT-ORCHESTRATOR] Failed to feed artifacts to learning loop: {e}")
    
    async def _handle_guardian_pause(self, event: Dict[str, Any]):
        """Handle Guardian pause command"""
        pipeline_id = event.get('pipeline_id')
        
        if pipeline_id in self.pipelines:
            pipeline = self.pipelines[pipeline_id]
            pipeline.guardian_paused = True
            
            logger.warning(f"[AGENT-ORCHESTRATOR] Guardian paused pipeline: {pipeline_id}")
            
            # Publish event
            if self.message_bus:
                await self.message_bus.publish('pipeline.paused', {
                    'pipeline_id': pipeline_id,
                    'reason': 'guardian_pause'
                })
    
    async def _handle_guardian_resume(self, event: Dict[str, Any]):
        """Handle Guardian resume command"""
        pipeline_id = event.get('pipeline_id')
        
        if pipeline_id in self.pipelines:
            pipeline = self.pipelines[pipeline_id]
            pipeline.guardian_paused = False
            
            logger.info(f"[AGENT-ORCHESTRATOR] Guardian resumed pipeline: {pipeline_id}")
            
            # Publish event
            if self.message_bus:
                await self.message_bus.publish('pipeline.resumed', {
                    'pipeline_id': pipeline_id
                })
    
    async def _handle_guardian_override(self, event: Dict[str, Any]):
        """Handle Guardian override command"""
        pipeline_id = event.get('pipeline_id')
        override_data = event.get('override', {})
        
        if pipeline_id in self.pipelines:
            pipeline = self.pipelines[pipeline_id]
            pipeline.guardian_override = override_data
            
            logger.info(f"[AGENT-ORCHESTRATOR] Guardian override applied to pipeline: {pipeline_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            'running': self.running,
            'total_pipelines': len(self.pipelines),
            'active_pipelines': len([p for p in self.pipelines.values() if p.status == PipelineStatus.RUNNING])
        }
    
    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline details"""
        if pipeline_id in self.pipelines:
            return self.pipelines[pipeline_id].to_dict()
        return None
    
    def get_pipelines(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pipelines, optionally filtered by status"""
        pipelines = []
        
        for pipeline in self.pipelines.values():
            if status and pipeline.status != status:
                continue
            
            pipelines.append(pipeline.to_dict())
        
        # Sort by started time (newest first)
        pipelines.sort(
            key=lambda p: p.get('started_at', ''),
            reverse=True
        )
        
        return pipelines


# Global instance
agent_orchestrator = AgentOrchestrator()
