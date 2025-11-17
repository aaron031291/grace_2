"""
Autonomous Pipeline Agent
Monitors workspace, analyzes files, proposes schemas, manages trust, triggers training
Split into staging (analysis) and approval (governance) for safety
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class StagingAgent:
    """
    Staging agent: analyzes files, drafts schema proposals, computes trust scores.
    Does NOT make any changes - only proposes.
    """
    
    def __init__(self):
        self.agent_id = "staging_agent_001"
        self.agent_name = "Schema Inference Staging Agent"
        self.capabilities = [
            "file_analysis",
            "schema_inference",
            "trust_computation",
            "contradiction_detection"
        ]
        self.status = "idle"
        self.current_task = None
        self._running = False
        self._task = None
    
    async def initialize(self):
        """Initialize dependencies"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        # Register self as a sub-agent
        await sub_agents_integration.register_agent(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            agent_type="specialist",
            mission="Analyze files and propose schema changes without executing them",
            capabilities=self.capabilities,
            constraints={
                "read_only": True,
                "requires_approval": True,
                "max_file_size_mb": 100
            }
        )
        
        logger.info(f"✅ {self.agent_name} registered")
    
    async def start(self):
        """Start the staging agent"""
        if self._running:
            return
        
        await self.initialize()
        
        self._running = True
        self._task = asyncio.create_task(self._main_loop())
        logger.info(f"🤖 {self.agent_name} started")
    
    async def stop(self):
        """Stop the staging agent"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"🛑 {self.agent_name} stopped")
    
    async def _main_loop(self):
        """Main task loop"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        while self._running:
            try:
                # Update heartbeat
                await sub_agents_integration.heartbeat(self.agent_id)
                
                # Scan for new files
                await self._scan_workspace()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in {self.agent_name} loop: {e}")
                await asyncio.sleep(60)
    
    async def _scan_workspace(self):
        """Scan workspace for new files to analyze"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        # Update status
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "active",
            "scanning_workspace"
        )
        
        watch_folders = [
            Path("training_data"),
            Path("storage/uploads"),
            Path("grace_training"),
            Path("docs")
        ]
        
        new_files_found = 0
        
        for folder in watch_folders:
            if not folder.exists():
                continue
            
            for file_path in folder.rglob("*"):
                if file_path.is_file() and self._should_process(file_path):
                    # Check if already processed
                    if not await self._is_already_processed(file_path):
                        await self._analyze_file(file_path)
                        new_files_found += 1
        
        # Update status
        if new_files_found > 0:
            await sub_agents_integration.log_task_completion(
                self.agent_id,
                success=True
            )
        
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "idle",
            None
        )
    
    def _should_process(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip hidden files, temp files, system files
        if file_path.name.startswith('.'):
            return False
        if file_path.name.startswith('~'):
            return False
        if file_path.suffix in ['.lock', '.tmp', '.bak', '.swp']:
            return False
        if file_path.stat().st_size > 100 * 1024 * 1024:  # 100MB limit
            return False
        
        return True
    
    async def _is_already_processed(self, file_path: Path) -> bool:
        """Check if file was already processed"""
        # Check if file exists in any memory table
        from backend.memory_tables.registry import table_registry
        
        file_path_str = str(file_path)
        
        # Check documents table
        rows = table_registry.query_rows(
            'memory_documents',
            filters={'file_path': file_path_str},
            limit=1
        )
        
        return len(rows) > 0
    
    async def _analyze_file(self, file_path: Path):
        """Analyze a file and create proposal (STAGING ONLY - does not execute)"""
        from backend.memory_tables.content_pipeline import content_pipeline
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        from backend.memory_tables.registry import table_registry
        
        logger.info(f"📄 Staging analysis: {file_path}")
        
        try:
            # Analyze file content
            analysis = await content_pipeline.analyze(file_path)
            
            # Get schema proposal
            schema_agent = SchemaInferenceAgent(registry=table_registry)
            existing_tables = table_registry.list_tables()
            proposal = await schema_agent.propose_schema(analysis, existing_tables)
            
            # Draft proposal (does not submit to approval agent yet)
            draft = {
                'file_path': str(file_path),
                'analysis': analysis,
                'proposal': proposal,
                'confidence': proposal.get('confidence', 0.0),
                'recommended_table': proposal.get('table_name'),
                'drafted_at': datetime.utcnow().isoformat(),
                'drafted_by': self.agent_id
            }
            
            logger.info(
                f"📋 Draft created: {file_path.name} → {proposal.get('table_name')} "
                f"(confidence: {proposal.get('confidence', 0):.1%})"
            )
            
            # Send to approval agent if confidence is sufficient
            if proposal.get('confidence', 0) >= 0.7:
                # Hand off to approval agent
                await self._hand_off_to_approval(draft)
            else:
                logger.info(f"⏸️  Low confidence ({proposal.get('confidence', 0):.1%}), skipping approval")
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")


class ApprovalAgent:
    """
    Approval agent: receives drafts from staging, submits to Unified Logic,
    handles governance approvals, executes approved changes.
    """
    
    def __init__(self):
        self.agent_id = "approval_agent_001"
        self.agent_name = "Schema Approval & Execution Agent"
        self.capabilities = [
            "governance_submission",
            "approval_management",
            "table_insertion",
            "trust_updates"
        ]
        self.pending_drafts: List[Dict[str, Any]] = []
        self._running = False
        self._task = None
    
    async def initialize(self):
        """Initialize dependencies"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        # Register self as a sub-agent
        await sub_agents_integration.register_agent(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            agent_type="orchestrator",
            mission="Submit proposals to governance and execute approved changes",
            capabilities=self.capabilities,
            constraints={
                "requires_governance": True,
                "auto_approve_threshold": 0.90,
                "max_pending_proposals": 100
            }
        )
        
        logger.info(f"✅ {self.agent_name} registered")
    
    async def start(self):
        """Start the approval agent"""
        if self._running:
            return
        
        await self.initialize()
        
        self._running = True
        self._task = asyncio.create_task(self._main_loop())
        logger.info(f"🤖 {self.agent_name} started")
    
    async def stop(self):
        """Stop the approval agent"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"🛑 {self.agent_name} stopped")
    
    async def _main_loop(self):
        """Main task loop"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        while self._running:
            try:
                # Update heartbeat
                await sub_agents_integration.heartbeat(self.agent_id)
                
                # Process pending drafts
                await self._process_pending_drafts()
                
                # Wait before next cycle
                await asyncio.sleep(15)  # Every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in {self.agent_name} loop: {e}")
                await asyncio.sleep(30)
    
    async def receive_draft(self, draft: Dict[str, Any]):
        """Receive a draft from staging agent"""
        self.pending_drafts.append(draft)
        logger.info(f"📥 Received draft: {draft['file_path']} ({len(self.pending_drafts)} pending)")
    
    async def _process_pending_drafts(self):
        """Process all pending drafts"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        if not self.pending_drafts:
            return
        
        # Update status
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "active",
            f"processing_{len(self.pending_drafts)}_drafts"
        )
        
        # Process each draft
        drafts_to_process = self.pending_drafts.copy()
        self.pending_drafts.clear()
        
        for draft in drafts_to_process:
            try:
                await self._process_draft(draft)
                await sub_agents_integration.log_task_completion(
                    self.agent_id,
                    success=True
                )
            except Exception as e:
                logger.error(f"Failed to process draft {draft['file_path']}: {e}")
                await sub_agents_integration.log_task_completion(
                    self.agent_id,
                    success=False
                )
        
        # Update status
        await sub_agents_integration.update_agent_status(
            self.agent_id,
            "idle",
            None
        )
    
    async def _process_draft(self, draft: Dict[str, Any]):
        """Process a single draft"""
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        confidence = draft['confidence']
        
        # Submit to schema proposal engine
        result = await schema_proposal_engine.propose_schema_from_file(
            Path(draft['file_path']),
            draft['proposal']
        )
        
        if result.get('success'):
            logger.info(f"✅ Proposal submitted: {draft['file_path']}")
            
            # If high confidence and auto-approved, log it
            if confidence >= 0.90:
                logger.info(f"🚀 Auto-approved (high confidence): {draft['file_path']}")
        else:
            logger.warning(f"⚠️  Proposal failed: {draft['file_path']} - {result.get('error')}")


class AutonomousPipelineAgent:
    """
    Main autonomous agent coordinator.
    Manages staging and approval agents.
    """
    
    def __init__(self):
        self.staging_agent = StagingAgent()
        self.approval_agent = ApprovalAgent()
        self._initialized = False
    
    async def initialize(self):
        """Initialize both agents"""
        if self._initialized:
            return
        
        await self.staging_agent.initialize()
        await self.approval_agent.initialize()
        
        self._initialized = True
        logger.info("✅ Autonomous Pipeline Agent initialized")
    
    async def start(self):
        """Start both agents"""
        if not self._initialized:
            await self.initialize()
        
        await self.staging_agent.start()
        await self.approval_agent.start()
        
        logger.info("🤖 Autonomous Pipeline Agent ACTIVE")
    
    async def stop(self):
        """Stop both agents"""
        await self.staging_agent.stop()
        await self.approval_agent.stop()
        
        logger.info("🛑 Autonomous Pipeline Agent STOPPED")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of both agents"""
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        staging_stats = await sub_agents_integration.get_agent_stats(self.staging_agent.agent_id)
        approval_stats = await sub_agents_integration.get_agent_stats(self.approval_agent.agent_id)
        
        return {
            'staging_agent': staging_stats,
            'approval_agent': approval_stats,
            'pending_drafts': len(self.approval_agent.pending_drafts),
            'active': self.staging_agent._running and self.approval_agent._running
        }


# Global instance
autonomous_pipeline_agent = AutonomousPipelineAgent()


# Hook staging to approval
async def _hand_off_to_approval(draft: Dict[str, Any]):
    """Hand off draft from staging to approval agent"""
    await autonomous_pipeline_agent.approval_agent.receive_draft(draft)


# Monkey-patch the staging agent to use the global hand-off
StagingAgent._hand_off_to_approval = staticmethod(_hand_off_to_approval)
