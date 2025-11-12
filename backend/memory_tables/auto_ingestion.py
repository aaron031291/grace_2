#!/usr/bin/env python3
"""
Auto-Ingestion Service
Watches folders, analyzes files, proposes schemas, and populates tables
Full pipeline: Upload → Extract → Schema → Approve → Insert → Learn
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class AutoIngestionService:
    """
    Monitors folders for new files and automatically ingests them
    through the complete pipeline with governance
    """
    
    def __init__(self, registry=None, schema_agent=None, content_pipeline=None):
        self.registry = registry
        self.schema_agent = schema_agent
        self.content_pipeline = content_pipeline
        self.watch_folders: List[Path] = []
        self.processed_files: Set[str] = set()
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._task = None
    
    async def start(self, folders: List[str] = None):
        """Start watching folders for new files"""
        if folders:
            self.watch_folders = [Path(f) for f in folders]
        else:
            # Default watch folders
            self.watch_folders = [
                Path("training_data"),
                Path("storage/uploads"),
                Path("grace_training")
            ]
        
        # Create folders if they don't exist
        for folder in self.watch_folders:
            folder.mkdir(parents=True, exist_ok=True)
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info(f"🔍 Auto-ingestion started, watching: {[str(f) for f in self.watch_folders]}")
    
    async def stop(self):
        """Stop the auto-ingestion service"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Auto-ingestion stopped")
    
    async def _watch_loop(self):
        """Main loop that checks for new files"""
        while self._running:
            try:
                for folder in self.watch_folders:
                    await self._scan_folder(folder)
                
                # Check every 5 seconds
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                await asyncio.sleep(10)
    
    async def _scan_folder(self, folder: Path):
        """Scan a folder for new files"""
        if not folder.exists():
            return
        
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                file_id = self._get_file_id(file_path)
                
                # Skip if already processed
                if file_id in self.processed_files:
                    continue
                
                # Skip hidden files and system files
                if file_path.name.startswith('.') or file_path.name.startswith('~'):
                    continue
                
                # Skip lock files, temp files
                if file_path.suffix in ['.lock', '.tmp', '.bak']:
                    continue
                
                # Process the file
                await self._process_file(file_path)
                self.processed_files.add(file_id)
    
    def _get_file_id(self, file_path: Path) -> str:
        """Generate unique ID for a file"""
        # Use path + mtime + size as ID
        stat = file_path.stat()
        data = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(data.encode()).hexdigest()
    
    async def _process_file(self, file_path: Path):
        """
        Process a single file through the complete pipeline:
        1. Extract content
        2. Analyze and propose schema
        3. Submit to Unified Logic Hub
        4. If approved, insert to table
        5. Trigger learning
        """
        logger.info(f"📄 Processing new file: {file_path}")
        
        try:
            # Step 1: Analyze file content
            if not self.content_pipeline:
                from backend.memory_tables.content_pipeline import content_pipeline
                self.content_pipeline = content_pipeline
            
            analysis = await self.content_pipeline.analyze(file_path)
            logger.info(f"✅ Analyzed: {analysis['category']}")
            
            # Step 2: Get schema proposal
            if not self.schema_agent:
                from backend.memory_tables.schema_agent import SchemaInferenceAgent
                self.schema_agent = SchemaInferenceAgent(registry=self.registry)
            
            if not self.registry:
                from backend.memory_tables.registry import table_registry
                self.registry = table_registry
            
            existing_tables = self.registry.list_tables()
            proposal = await self.schema_agent.propose_schema(analysis, existing_tables)
            
            logger.info(f"💡 Schema proposal: {proposal['action']} → {proposal.get('table_name')}")
            
            # Step 3: Submit to Unified Logic Hub
            approval_result = await self._submit_for_approval(file_path, analysis, proposal)
            
            if not approval_result.get('approved'):
                # Store in pending approvals
                approval_id = approval_result.get('update_id', str(file_path))
                self.pending_approvals[approval_id] = {
                    'file_path': str(file_path),
                    'analysis': analysis,
                    'proposal': proposal,
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"⏳ Awaiting approval: {approval_id}")
                return
            
            # Step 4: Insert to table
            await self._insert_to_table(file_path, proposal)
            
            # Step 5: Trigger learning
            await self._trigger_learning(file_path, proposal)
            
            logger.info(f"✅ Successfully ingested: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            # Log to insights table as failed ingestion
            await self._log_failed_ingestion(file_path, str(e))
    
    async def _submit_for_approval(
        self, 
        file_path: Path, 
        analysis: Dict[str, Any], 
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit ingestion to Unified Logic Hub for approval"""
        try:
            from backend.unified_logic_hub import unified_logic_hub
            
            # Determine risk level
            action = proposal.get('action')
            risk_level = 'low'
            
            if action == 'create_new':
                risk_level = 'medium'  # New table creation
            elif action == 'extend_existing':
                risk_level = 'medium'  # Schema modification
            
            # Submit update
            result = await unified_logic_hub.submit_update(
                update_type="auto_ingestion",
                component_targets=["memory_tables", "ingestion"],
                content={
                    'file_path': str(file_path),
                    'analysis': analysis,
                    'proposal': proposal,
                    'auto_ingest': True
                },
                risk_level=risk_level,
                created_by="auto_ingestion_service"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to submit for approval: {e}")
            # Auto-approve low risk if Logic Hub unavailable
            if proposal.get('action') == 'use_existing':
                return {'approved': True, 'reason': 'fallback_auto_approve'}
            return {'approved': False, 'reason': str(e)}
    
    async def _insert_to_table(self, file_path: Path, proposal: Dict[str, Any]):
        """Insert file data into appropriate table"""
        table_name = proposal.get('table_name')
        if not table_name:
            return
        
        # Extract row data
        row_data = await self.schema_agent.extract_row_data(file_path, table_name)
        
        # Add auto-ingestion metadata
        row_data['notes'] = f"Auto-ingested on {datetime.now().isoformat()}"
        row_data['ingestion_pipeline_id'] = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Insert
        inserted = self.registry.insert_row(table_name, row_data)
        
        if inserted:
            logger.info(f"✅ Inserted row into {table_name}: {inserted.id}")
        else:
            raise Exception(f"Failed to insert row into {table_name}")
    
    async def _trigger_learning(self, file_path: Path, proposal: Dict[str, Any]):
        """Trigger learning systems after successful ingestion"""
        try:
            # Publish event to clarity
            from backend.clarity_manifest import clarity_manifest
            
            await clarity_manifest.publish_event(
                event_type="file_ingested",
                component_id="auto_ingestion",
                data={
                    'file_path': str(file_path),
                    'table': proposal.get('table_name'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.warning(f"Could not trigger learning: {e}")
    
    async def _log_failed_ingestion(self, file_path: Path, error: str):
        """Log failed ingestion to insights table"""
        try:
            row_data = {
                'file_path': str(file_path),
                'insight_type': 'alert',
                'content': f"Failed to ingest: {error}",
                'generated_by': 'auto_ingestion',
                'confidence': 0.0,
                'created_at': datetime.now(),
                'tags': ['failed_ingestion', 'auto_ingest']
            }
            
            self.registry.insert_row('memory_insights', row_data)
            
        except Exception as e:
            logger.error(f"Could not log failed ingestion: {e}")
    
    async def approve_pending(self, approval_id: str) -> bool:
        """Manually approve a pending ingestion"""
        if approval_id not in self.pending_approvals:
            return False
        
        pending = self.pending_approvals[approval_id]
        file_path = Path(pending['file_path'])
        proposal = pending['proposal']
        
        try:
            await self._insert_to_table(file_path, proposal)
            await self._trigger_learning(file_path, proposal)
            
            # Remove from pending
            del self.pending_approvals[approval_id]
            
            logger.info(f"✅ Manually approved: {approval_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve {approval_id}: {e}")
            return False
    
    async def reject_pending(self, approval_id: str) -> bool:
        """Reject a pending ingestion"""
        if approval_id not in self.pending_approvals:
            return False
        
        pending = self.pending_approvals[approval_id]
        
        # Log rejection
        await self._log_failed_ingestion(
            Path(pending['file_path']),
            "Manually rejected by user"
        )
        
        # Remove from pending
        del self.pending_approvals[approval_id]
        
        logger.info(f"❌ Rejected: {approval_id}")
        return True
    
    def get_pending_approvals(self) -> Dict[str, Dict[str, Any]]:
        """Get all pending approvals"""
        return self.pending_approvals.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return {
            'running': self._running,
            'watch_folders': [str(f) for f in self.watch_folders],
            'processed_files_count': len(self.processed_files),
            'pending_approvals_count': len(self.pending_approvals)
        }


# Global service instance
auto_ingestion_service = AutoIngestionService()
