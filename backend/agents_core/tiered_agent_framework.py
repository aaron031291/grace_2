"""
Tiered Agent Execution Framework
Specialized agents working in pipeline: research → design → implement → test → deploy

Each agent:
- Publishes results to event bus (Guardian can pause/override)
- Uses playbooks as first-class tools
- Collects artifacts
- Feeds learning loop
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import json

logger = logging.getLogger(__name__)


class AgentPhase(str, Enum):
    """Agent execution phases"""
    RESEARCH = "research"
    DESIGN = "design"
    IMPLEMENT = "implement"
    TEST = "test"
    DEPLOY = "deploy"


class AgentStatus(str, Enum):
    """Agent status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentArtifact:
    """Artifact produced by an agent"""
    
    artifact_id: str
    artifact_type: str  # 'research_doc', 'design_spec', 'code', 'test_results', 'deployment_manifest'
    phase: AgentPhase
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'artifact_id': self.artifact_id,
            'artifact_type': self.artifact_type,
            'phase': self.phase.value,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AgentResult:
    """Result from agent execution"""
    
    agent_id: str
    phase: AgentPhase
    status: AgentStatus
    artifacts: List[AgentArtifact] = field(default_factory=list)
    playbooks_used: List[str] = field(default_factory=list)
    playbook_results: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'phase': self.phase.value,
            'status': self.status.value,
            'artifacts': [a.to_dict() for a in self.artifacts],
            'playbooks_used': self.playbooks_used,
            'playbook_results': self.playbook_results,
            'execution_time': self.execution_time,
            'error': self.error,
            'metadata': self.metadata
        }


class BaseAgent:
    """Base class for all tiered agents"""
    
    def __init__(
        self,
        agent_id: str,
        phase: AgentPhase,
        description: str
    ):
        self.agent_id = agent_id
        self.phase = phase
        self.description = description
        self.status = AgentStatus.PENDING
        self.artifacts: List[AgentArtifact] = []
        self.playbooks_used: List[str] = []
        self.playbook_results: Dict[str, Any] = {}
        
        # Dependencies
        self.message_bus = None
        self.guardian = None
        self.playbook_registry = None
        self.immutable_log = None
    
    async def initialize(self):
        """Initialize dependencies"""
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
        except ImportError:
            logger.warning(f"[{self.agent_id}] Message bus not available")
        
        try:
            from backend.core.guardian import guardian
            self.guardian = guardian
        except ImportError:
            logger.warning(f"[{self.agent_id}] Guardian not available")
        
        try:
            from backend.core.guardian_playbooks import guardian_playbook_registry
            self.playbook_registry = guardian_playbook_registry
        except ImportError:
            logger.warning(f"[{self.agent_id}] Playbook registry not available")
        
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning(f"[{self.agent_id}] Immutable log not available")
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent phase
        
        Args:
            context: Execution context with previous phase results
            
        Returns:
            Agent result with artifacts
        """
        await self.initialize()
        
        start_time = datetime.utcnow()
        self.status = AgentStatus.RUNNING
        
        # Publish start event
        await self._publish_event('agent.phase.started', {
            'agent_id': self.agent_id,
            'phase': self.phase.value,
            'context': context
        })
        
        # Log start
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='agent_execution',
                subcategory='phase_started',
                data={'agent_id': self.agent_id, 'phase': self.phase.value},
                actor=self.agent_id,
                action='start_phase',
                resource=self.phase.value
            )
        
        try:
            # Check Guardian approval
            if not await self._check_guardian_approval(context):
                raise Exception("Guardian denied execution")
            
            # Execute phase-specific logic
            await self._execute_phase(context)
            
            self.status = AgentStatus.COMPLETED
            
            # Publish completion
            await self._publish_event('agent.phase.completed', {
                'agent_id': self.agent_id,
                'phase': self.phase.value,
                'artifacts': len(self.artifacts)
            })
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            error_msg = str(e)
            
            logger.error(f"[{self.agent_id}] Phase {self.phase.value} failed: {e}", exc_info=True)
            
            # Publish failure
            await self._publish_event('agent.phase.failed', {
                'agent_id': self.agent_id,
                'phase': self.phase.value,
                'error': error_msg
            })
            
            # Emit to learning loop
            await self._emit_learning_event('agent.task.failed', {
                'agent': self.agent_id,
                'phase': self.phase.value,
                'task': self.description,
                'error': error_msg
            }, severity='high')
            
            return AgentResult(
                agent_id=self.agent_id,
                phase=self.phase,
                status=self.status,
                error=error_msg
            )
        
        finally:
            # Log completion
            if self.immutable_log:
                await self.immutable_log.append_entry(
                    category='agent_execution',
                    subcategory='phase_completed',
                    data={
                        'agent_id': self.agent_id,
                        'phase': self.phase.value,
                        'status': self.status.value,
                        'artifacts': len(self.artifacts)
                    },
                    actor=self.agent_id,
                    action='complete_phase',
                    resource=self.phase.value
                )
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AgentResult(
            agent_id=self.agent_id,
            phase=self.phase,
            status=self.status,
            artifacts=self.artifacts,
            playbooks_used=self.playbooks_used,
            playbook_results=self.playbook_results,
            execution_time=execution_time
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute phase-specific logic (override in subclass)"""
        raise NotImplementedError("Subclass must implement _execute_phase")
    
    async def _check_guardian_approval(self, context: Dict[str, Any]) -> bool:
        """Check if Guardian approves execution"""
        if not self.guardian:
            return True  # No guardian = automatic approval
        
        # Guardian check (simplified)
        logger.info(f"[{self.agent_id}] Requesting Guardian approval for {self.phase.value}")
        
        # In production, would call guardian.check_can_execute()
        return True
    
    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to message bus"""
        if not self.message_bus:
            return
        
        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            **data
        }
        
        await self.message_bus.publish(event_type, event)
    
    async def _emit_learning_event(self, event_type: str, data: Dict[str, Any], severity: str = 'medium'):
        """Emit event to learning loop"""
        try:
            from backend.learning_systems.event_emitters import emit_learning_event
            await emit_learning_event(event_type, data, severity)
        except ImportError:
            pass
    
    async def use_playbook(
        self,
        playbook_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use a playbook as a tool
        
        Args:
            playbook_id: Playbook identifier
            context: Context for playbook execution
            
        Returns:
            Playbook result with success/failure + artifacts
        """
        if not self.playbook_registry:
            logger.warning(f"[{self.agent_id}] Playbook registry not available")
            return {'success': False, 'error': 'Playbook registry not available'}
        
        logger.info(f"[{self.agent_id}] Using playbook: {playbook_id}")
        
        # Get playbook
        playbook = self.playbook_registry.get_playbook(playbook_id)
        
        if not playbook:
            return {'success': False, 'error': f'Playbook not found: {playbook_id}'}
        
        # Execute playbook
        try:
            result = await playbook.execute(context)
            
            self.playbooks_used.append(playbook_id)
            self.playbook_results[playbook_id] = result
            
            # Emit playbook result to learning loop
            await self._emit_learning_event('playbook.executed', {
                'playbook_id': playbook_id,
                'agent': self.agent_id,
                'phase': self.phase.value,
                'success': result.get('success', False),
                'artifacts': result.get('artifacts', [])
            }, severity='low')
            
            logger.info(f"[{self.agent_id}] Playbook {playbook_id} completed: {result.get('success', False)}")
            
            return result
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{self.agent_id}] Playbook {playbook_id} failed: {e}")
            
            # Emit failure to learning loop
            await self._emit_learning_event('playbook.failed', {
                'playbook_id': playbook_id,
                'agent': self.agent_id,
                'phase': self.phase.value,
                'error': error_msg
            }, severity='medium')
            
            return {'success': False, 'error': error_msg}
    
    def add_artifact(
        self,
        artifact_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add artifact produced by this agent"""
        artifact = AgentArtifact(
            artifact_id=f"{self.agent_id}_{uuid4().hex[:8]}",
            artifact_type=artifact_type,
            phase=self.phase,
            content=content,
            metadata=metadata or {}
        )
        
        self.artifacts.append(artifact)
        
        logger.info(f"[{self.agent_id}] Artifact created: {artifact_type}")


class ResearchAgent(BaseAgent):
    """Research phase agent - gathers information and context"""
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent",
            phase=AgentPhase.RESEARCH,
            description="Research and gather context for task"
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute research phase"""
        logger.info("[RESEARCH] Starting research phase...")
        
        task = context.get('task', 'Unknown task')
        
        # Use playbook for research
        research_playbook = await self.use_playbook(
            'research_and_gather',
            {'task': task, 'sources': ['web', 'github', 'rag']}
        )
        
        if research_playbook.get('success'):
            # Extract research findings
            findings = research_playbook.get('findings', [])
            
            self.add_artifact(
                artifact_type='research_doc',
                content={
                    'task': task,
                    'findings': findings,
                    'sources': research_playbook.get('sources', [])
                },
                metadata={'playbook': 'research_and_gather'}
            )
        
        logger.info("[RESEARCH] Research phase completed")


class DesignAgent(BaseAgent):
    """Design phase agent - creates architecture and specifications"""
    
    def __init__(self):
        super().__init__(
            agent_id="design_agent",
            phase=AgentPhase.DESIGN,
            description="Design architecture and create specifications"
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute design phase"""
        logger.info("[DESIGN] Starting design phase...")
        
        # Get research from previous phase
        research = context.get('research_artifacts', [])
        
        # Use playbook for design
        design_playbook = await self.use_playbook(
            'create_design_spec',
            {'research': research, 'requirements': context.get('requirements', [])}
        )
        
        if design_playbook.get('success'):
            design_spec = design_playbook.get('design_spec', {})
            
            self.add_artifact(
                artifact_type='design_spec',
                content=design_spec,
                metadata={'playbook': 'create_design_spec'}
            )
        
        logger.info("[DESIGN] Design phase completed")


class ImplementAgent(BaseAgent):
    """Implementation phase agent - writes code"""
    
    def __init__(self):
        super().__init__(
            agent_id="implement_agent",
            phase=AgentPhase.IMPLEMENT,
            description="Implement code based on design"
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute implementation phase"""
        logger.info("[IMPLEMENT] Starting implementation phase...")
        
        # Get design from previous phase
        design = context.get('design_artifacts', [])
        
        # Use playbook for implementation
        impl_playbook = await self.use_playbook(
            'implement_code',
            {'design': design, 'language': context.get('language', 'python')}
        )
        
        if impl_playbook.get('success'):
            code = impl_playbook.get('code', '')
            files = impl_playbook.get('files', [])
            
            self.add_artifact(
                artifact_type='code',
                content={'code': code, 'files': files},
                metadata={'playbook': 'implement_code'}
            )
        
        logger.info("[IMPLEMENT] Implementation phase completed")


class TestAgent(BaseAgent):
    """Test phase agent - runs tests and validation"""
    
    def __init__(self):
        super().__init__(
            agent_id="test_agent",
            phase=AgentPhase.TEST,
            description="Test and validate implementation"
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute test phase"""
        logger.info("[TEST] Starting test phase...")
        
        # Get implementation from previous phase
        implementation = context.get('implementation_artifacts', [])
        
        # Use playbook for testing
        test_playbook = await self.use_playbook(
            'run_tests',
            {'implementation': implementation, 'test_types': ['unit', 'integration']}
        )
        
        if test_playbook.get('success'):
            test_results = test_playbook.get('test_results', {})
            
            self.add_artifact(
                artifact_type='test_results',
                content=test_results,
                metadata={'playbook': 'run_tests'}
            )
            
            # If tests failed, emit to learning loop
            if not test_results.get('all_passed', False):
                await self._emit_learning_event('agent.tests.failed', {
                    'agent': self.agent_id,
                    'failed_count': test_results.get('failed', 0),
                    'total_count': test_results.get('total', 0)
                }, severity='medium')
        
        logger.info("[TEST] Test phase completed")


class DeployAgent(BaseAgent):
    """Deploy phase agent - deploys to target environment"""
    
    def __init__(self):
        super().__init__(
            agent_id="deploy_agent",
            phase=AgentPhase.DEPLOY,
            description="Deploy to target environment"
        )
    
    async def _execute_phase(self, context: Dict[str, Any]):
        """Execute deploy phase"""
        logger.info("[DEPLOY] Starting deploy phase...")
        
        # Get test results from previous phase
        test_results = context.get('test_artifacts', [])
        
        # Check if tests passed
        all_passed = all(
            t.get('content', {}).get('all_passed', False)
            for t in test_results
        )
        
        if not all_passed:
            raise Exception("Cannot deploy: tests failed")
        
        # Use playbook for deployment
        deploy_playbook = await self.use_playbook(
            'deploy_to_environment',
            {'environment': context.get('environment', 'staging'), 'test_results': test_results}
        )
        
        if deploy_playbook.get('success'):
            deployment = deploy_playbook.get('deployment', {})
            
            self.add_artifact(
                artifact_type='deployment_manifest',
                content=deployment,
                metadata={'playbook': 'deploy_to_environment'}
            )
        
        logger.info("[DEPLOY] Deploy phase completed")


# Agent registry
AGENT_REGISTRY = {
    AgentPhase.RESEARCH: ResearchAgent,
    AgentPhase.DESIGN: DesignAgent,
    AgentPhase.IMPLEMENT: ImplementAgent,
    AgentPhase.TEST: TestAgent,
    AgentPhase.DEPLOY: DeployAgent
}
