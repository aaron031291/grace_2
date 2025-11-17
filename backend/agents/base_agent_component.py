"""
Base Agent Component
Defines sub-agents as BaseComponents with clarity contracts
"""
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class BaseAgentComponent(ABC):
    """
    Base class for all sub-agents with clarity contracts.
    
    Each agent has:
    - Manifest entry (clarity registration)
    - Schema (memory_sub_agents table)
    - Trust metrics (computed and tracked)
    - Heartbeat (alive signal)
    - Constraints (resource limits, permissions)
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        mission: str,
        capabilities: List[str],
        constraints: Dict[str, Any] = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.mission = mission
        self.capabilities = capabilities
        self.constraints = constraints or {}
        
        # Runtime state
        self.status = "initializing"
        self.current_job = None
        self.jobs_completed = 0
        self.jobs_failed = 0
        self.trust_score = 0.5  # Start at neutral
        self.created_at = datetime.utcnow()
        self.last_heartbeat = None
        
        # Clarity contracts
        self.manifest = None
        self.schema_entry = None
        
        # Callbacks
        self._on_job_complete: Optional[Callable] = None
        self._on_job_failed: Optional[Callable] = None
    
    async def initialize(self):
        """
        Initialize agent with clarity contracts.
        1. Register in clarity manifest
        2. Create schema entry in memory_sub_agents
        3. Compute initial trust score
        """
        logger.info(f"Initializing {self.agent_name} ({self.agent_id})")
        
        # Step 1: Register in clarity manifest
        await self._register_manifest()
        
        # Step 2: Create schema entry
        await self._create_schema_entry()
        
        # Step 3: Compute initial trust
        await self._compute_initial_trust()
        
        self.status = "idle"
        logger.info(f"✅ {self.agent_name} initialized (trust: {self.trust_score:.2f})")
    
    async def _register_manifest(self):
        """Register agent in clarity manifest"""
        try:
            from backend.unified_logic_hub import unified_logic_hub
            
            self.manifest = {
                'component_id': self.agent_id,
                'component_type': 'sub_agent',
                'name': self.agent_name,
                'capabilities': self.capabilities,
                'mission': self.mission,
                'constraints': self.constraints,
                'registered_at': self.created_at.isoformat(),
                'status': 'active'
            }
            
            # Submit to clarity
            result = await unified_logic_hub.submit_update(
                update_type="agent_registration",
                component_targets=["clarity_manifest", "sub_agents"],
                content=self.manifest,
                risk_level="low",
                created_by="agent_lifecycle_manager"
            )
            
            logger.debug(f"Manifest registered for {self.agent_id}")
        
        except Exception as e:
            logger.warning(f"Manifest registration failed (OK if clarity not running): {e}")
    
    async def _create_schema_entry(self):
        """Create entry in memory_sub_agents table"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        try:
            result = await sub_agents_integration.register_agent(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                mission=self.mission,
                capabilities=self.capabilities,
                constraints=self.constraints
            )
            
            if result:
                self.schema_entry = result
                logger.debug(f"Schema entry created for {self.agent_id}")
            else:
                logger.warning(f"Schema entry creation returned None for {self.agent_id}")
        
        except Exception as e:
            logger.error(f"Failed to create schema entry for {self.agent_id}: {e}")
            # Don't fail initialization - agent can still work without schema entry
            self.schema_entry = None
    
    async def _compute_initial_trust(self):
        """Compute initial trust score based on constraints and capabilities"""
        # Base trust starts at 0.5
        trust = 0.5
        
        # Boost trust if has strict constraints
        if self.constraints.get('read_only'):
            trust += 0.1
        if self.constraints.get('requires_approval'):
            trust += 0.1
        if self.constraints.get('max_file_size_mb'):
            trust += 0.05
        
        # Boost trust for specialized capabilities
        if len(self.capabilities) <= 3:  # Focused agent
            trust += 0.1
        
        # Penalty for orchestrator type (more powerful)
        if self.agent_type == "orchestrator":
            trust -= 0.1
        
        self.trust_score = min(max(trust, 0.0), 1.0)
    
    async def heartbeat(self):
        """Send heartbeat signal"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        self.last_heartbeat = datetime.utcnow()
        await sub_agents_integration.heartbeat(self.agent_id)
    
    async def execute_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a job and track results.
        
        Args:
            job: Job specification with type, data, etc.
        
        Returns:
            Job result with success status and output
        """
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        job_id = job.get('job_id', str(uuid.uuid4()))
        job_type = job.get('job_type')
        
        logger.info(f"🔵 {self.agent_name} starting job {job_id} ({job_type})")
        
        # Update status
        self.status = "busy"
        self.current_job = job_id
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "busy",
            f"{job_type}:{job_id}"
        )
        
        start_time = datetime.utcnow()
        result = None
        success = False
        
        try:
            # Execute the actual job (implemented by subclass)
            result = await self._execute_job_impl(job)
            success = result.get('success', False)
            
            # Track completion
            self.jobs_completed += 1
            
            logger.info(f"✅ {self.agent_name} completed job {job_id}")
            
            # Callback
            if self._on_job_complete:
                await self._on_job_complete(job, result)
        
        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed job {job_id}: {e}")
            self.jobs_failed += 1
            success = False
            result = {'success': False, 'error': str(e)}
            
            # Callback
            if self._on_job_failed:
                await self._on_job_failed(job, e)
        
        finally:
            # Update status
            self.status = "idle"
            self.current_job = None
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log completion
            await sub_agents_integration.log_task_completion(
                self.agent_id,
                success=success
            )
            
            await sub_agents_integration.update_agent_status(
                self.agent_id,
                "idle",
                None
            )
            
            # Update trust score based on performance
            await self._update_trust_score(success)
            
            # Return result
            return {
                'job_id': job_id,
                'success': success,
                'result': result,
                'duration_ms': duration_ms,
                'agent_id': self.agent_id
            }
    
    @abstractmethod
    async def _execute_job_impl(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement actual job execution logic.
        To be overridden by subclasses.
        """
        pass
    
    async def _update_trust_score(self, success: bool):
        """Update trust score based on job outcome"""
        total_jobs = self.jobs_completed + self.jobs_failed
        success_rate = self.jobs_completed / total_jobs if total_jobs > 0 else 0.5
        
        # Trust = 70% success rate + 30% previous trust (exponential moving average)
        new_trust = (0.7 * success_rate) + (0.3 * self.trust_score)
        self.trust_score = min(max(new_trust, 0.0), 1.0)
    
    async def terminate(self):
        """
        Terminate agent gracefully.
        - Update status
        - Deregister from manifest
        - Log termination
        """
        logger.info(f"Terminating {self.agent_name} ({self.agent_id})")
        
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        # Update status
        self.status = "offline"
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "offline",
            "terminated"
        )
        
        # Deregister from manifest
        try:
            from backend.unified_logic_hub import unified_logic_hub
            
            await unified_logic_hub.submit_update(
                update_type="agent_deregistration",
                component_targets=["clarity_manifest", "sub_agents"],
                content={
                    'agent_id': self.agent_id,
                    'terminated_at': datetime.utcnow().isoformat(),
                    'jobs_completed': self.jobs_completed,
                    'jobs_failed': self.jobs_failed,
                    'final_trust_score': self.trust_score
                },
                risk_level="low",
                created_by="agent_lifecycle_manager"
            )
        except Exception as e:
            logger.warning(f"Manifest deregistration failed: {e}")
        
        logger.info(f"✅ {self.agent_name} terminated (completed {self.jobs_completed} jobs, trust: {self.trust_score:.2f})")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'status': self.status,
            'current_job': self.current_job,
            'jobs_completed': self.jobs_completed,
            'jobs_failed': self.jobs_failed,
            'success_rate': self.jobs_completed / (self.jobs_completed + self.jobs_failed) if (self.jobs_completed + self.jobs_failed) > 0 else 0.0,
            'trust_score': self.trust_score,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'uptime_seconds': (datetime.utcnow() - self.created_at).total_seconds()
        }


class SchemaInferenceAgent(BaseAgentComponent):
    """
    Agent specialized in schema inference from files.
    """
    
    def __init__(self, instance_id: str = None):
        agent_id = instance_id or f"schema_inference_{uuid.uuid4().hex[:8]}"
        
        super().__init__(
            agent_id=agent_id,
            agent_name=f"Schema Inference Agent {agent_id[-8:]}",
            agent_type="specialist",
            mission="Analyze files and infer optimal schema structure",
            capabilities=[
                "file_analysis",
                "content_extraction",
                "schema_inference",
                "field_extraction"
            ],
            constraints={
                "read_only": True,
                "max_file_size_mb": 100,
                "requires_approval": True,
                "allowed_formats": ["txt", "pdf", "md", "csv", "json", "yaml", "py", "js", "ts"]
            }
        )
    
    async def _execute_job_impl(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute schema inference job"""
        from pathlib import Path
        from backend.memory_tables.content_pipeline import content_pipeline
        from backend.memory_tables.schema_agent import SchemaInferenceAgent as LLMSchemaAgent
        from backend.memory_tables.registry import table_registry
        
        file_path = job.get('file_path')
        
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Analyze file
        analysis = await content_pipeline.analyze(file_path)
        
        # Infer schema
        schema_agent = LLMSchemaAgent(registry=table_registry)
        existing_tables = table_registry.list_tables()
        proposal = await schema_agent.propose_schema(analysis, existing_tables)
        
        return {
            'success': True,
            'analysis': analysis,
            'proposal': proposal,
            'confidence': proposal.get('confidence', 0.0),
            'recommended_table': proposal.get('table_name')
        }


class IngestionAgent(BaseAgentComponent):
    """
    Agent specialized in data ingestion to memory tables.
    """
    
    def __init__(self, instance_id: str = None):
        agent_id = instance_id or f"ingestion_{uuid.uuid4().hex[:8]}"
        
        super().__init__(
            agent_id=agent_id,
            agent_name=f"Ingestion Agent {agent_id[-8:]}",
            agent_type="worker",
            mission="Ingest analyzed data into appropriate memory tables",
            capabilities=[
                "table_insertion",
                "data_validation",
                "trust_computation",
                "contradiction_check"
            ],
            constraints={
                "requires_governance": True,
                "auto_approve_threshold": 0.90,
                "max_batch_size": 100
            }
        )
    
    async def _execute_job_impl(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ingestion job"""
        from backend.memory_tables.registry import table_registry
        from backend.memory_tables.trust_scoring import trust_scoring_engine
        
        table_name = job.get('table_name')
        row_data = job.get('row_data')
        
        # Insert row (with upsert to handle duplicates)
        result = table_registry.insert_row(table_name, row_data, upsert=True)
        
        if result:
            # Compute trust score
            trust_score = await trust_scoring_engine.compute_trust_score(table_name, result)
            
            # Update trust score
            table_registry.update_row(
                table_name,
                str(result.id),
                {'trust_score': trust_score}
            )
            
            return {
                'success': True,
                'row_id': str(result.id),
                'trust_score': trust_score,
                'table_name': table_name
            }
        else:
            return {
                'success': False,
                'error': 'Failed to insert row'
            }


class CrossDomainLearningAgent(BaseAgentComponent):
    """
    Agent specialized in cross-domain learning across tables.
    """
    
    def __init__(self, instance_id: str = None):
        agent_id = instance_id or f"learning_{uuid.uuid4().hex[:8]}"
        
        super().__init__(
            agent_id=agent_id,
            agent_name=f"Cross-Domain Learning Agent {agent_id[-8:]}",
            agent_type="specialist",
            mission="Perform cross-domain learning across multiple memory tables",
            capabilities=[
                "cross_table_query",
                "pattern_extraction",
                "insight_generation",
                "knowledge_synthesis"
            ],
            constraints={
                "read_only": True,
                "max_tables": 10,
                "max_rows_per_table": 1000
            }
        )
    
    async def _execute_job_impl(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cross-domain learning job"""
        from backend.memory_tables.learning_integration import learning_bridge
        from backend.memory_tables.registry import table_registry
        
        # Ensure registry is initialized
        if not learning_bridge.registry:
            learning_bridge.registry = table_registry
        
        query_spec = job.get('query_spec', {})
        
        # Perform cross-domain query
        results = await learning_bridge.cross_domain_query(query_spec)
        
        # Extract patterns (simplified)
        patterns = {
            'total_rows': results.get('total_rows', 0),
            'tables_queried': len(results.get('results', {})),
            'success': results.get('success', False)
        }
        
        return {
            'success': True,
            'results': results,
            'patterns': patterns
        }
