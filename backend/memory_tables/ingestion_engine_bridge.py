#!/usr/bin/env python3
"""
Ingestion Engine Bridge
Ensures ingestion pipelines consume Memory Tables data
Replaces ad-hoc metadata with structured table queries
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class IngestionEngineBridge:
    """
    Bridges Memory Tables to the ingestion engine
    Ensures all ingestion jobs read from/write to tables
    """
    
    def __init__(self, registry=None):
        self.registry = registry
        self._active_jobs = {}
    
    async def create_ingestion_job(
        self, 
        file_path: Path, 
        table_name: str,
        job_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Create an ingestion job that populates a Memory Table
        Returns job metadata for tracking
        """
        try:
            if not self.registry:
                from backend.memory_tables.registry import table_registry
                self.registry = table_registry
            
            # Generate job ID
            job_id = f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(file_path).stem}"
            
            # Create job metadata
            job = {
                'job_id': job_id,
                'file_path': str(file_path),
                'table_name': table_name,
                'job_type': job_type,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'stages': {
                    'extraction': 'pending',
                    'validation': 'pending',
                    'population': 'pending',
                    'sync': 'pending'
                }
            }
            
            self._active_jobs[job_id] = job
            
            logger.info(f"📋 Created ingestion job: {job_id}")
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create ingestion job: {e}")
            return {'error': str(e)}
    
    async def execute_ingestion_job(self, job_id: str) -> bool:
        """
        Execute an ingestion job
        Processes file → extracts data → populates table
        """
        if job_id not in self._active_jobs:
            logger.error(f"Job not found: {job_id}")
            return False
        
        job = self._active_jobs[job_id]
        
        try:
            job['status'] = 'running'
            
            # Stage 1: Extract data
            logger.info(f"📄 Extracting: {job['file_path']}")
            job['stages']['extraction'] = 'running'
            
            from backend.memory_tables.schema_agent import SchemaInferenceAgent
            from backend.memory_tables.content_pipeline import content_pipeline
            
            agent = SchemaInferenceAgent(registry=self.registry)
            file_path = Path(job['file_path'])
            
            # Analyze file
            analysis = await content_pipeline.analyze(file_path)
            job['stages']['extraction'] = 'complete'
            job['analysis'] = analysis
            
            # Stage 2: Validate schema
            logger.info(f"🔍 Validating schema for {job['table_name']}")
            job['stages']['validation'] = 'running'
            
            schema = self.registry.get_schema(job['table_name'])
            if not schema:
                raise Exception(f"Schema not found: {job['table_name']}")
            
            job['stages']['validation'] = 'complete'
            
            # Stage 3: Populate table
            logger.info(f"💾 Populating {job['table_name']}")
            job['stages']['population'] = 'running'
            
            # Extract row data
            row_data = await agent.extract_row_data(file_path, job['table_name'])
            row_data['ingestion_pipeline_id'] = job_id
            
            # Insert
            inserted = self.registry.insert_row(job['table_name'], row_data)
            
            if inserted:
                job['row_id'] = str(inserted.id)
                job['stages']['population'] = 'complete'
                logger.info(f"✅ Populated row: {inserted.id}")
            else:
                raise Exception("Failed to insert row")
            
            # Stage 4: Sync to learning
            logger.info(f"📚 Syncing to learning systems")
            job['stages']['sync'] = 'running'
            
            from backend.memory_tables.learning_integration import learning_bridge
            
            sync_success = await learning_bridge.sync_to_ingestion(
                job['table_name'],
                job['row_id']
            )
            
            if sync_success:
                job['stages']['sync'] = 'complete'
            else:
                job['stages']['sync'] = 'failed'
            
            # Mark job complete
            job['status'] = 'complete'
            job['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"✅ Ingestion job complete: {job_id}")
            
            return True
            
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = str(e)
            logger.error(f"❌ Ingestion job failed: {job_id} - {e}")
            return False
    
    async def query_table_for_ingestion(
        self, 
        table_name: str, 
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query a table to get data for ingestion/learning
        Replaces ad-hoc metadata lookups
        """
        try:
            rows = self.registry.query_rows(table_name, filters=filters, limit=1000)
            
            # Convert to serializable format
            data = []
            for row in rows:
                row_dict = {
                    k: str(v) for k, v in row.__dict__.items()
                    if not k.startswith('_')
                }
                data.append(row_dict)
            
            logger.info(f"📊 Queried {len(data)} rows from {table_name}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to query table: {e}")
            return []
    
    async def update_ingestion_metadata(
        self, 
        table_name: str, 
        row_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update ingestion metadata for a table row
        """
        try:
            import uuid
            
            success = self.registry.update_row(
                table_name,
                uuid.UUID(row_id),
                metadata
            )
            
            if success:
                logger.info(f"✅ Updated metadata for {table_name}/{row_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an ingestion job"""
        return self._active_jobs.get(job_id)
    
    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """List all active ingestion jobs"""
        return list(self._active_jobs.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        jobs = list(self._active_jobs.values())
        
        return {
            'total_jobs': len(jobs),
            'pending': len([j for j in jobs if j['status'] == 'pending']),
            'running': len([j for j in jobs if j['status'] == 'running']),
            'complete': len([j for j in jobs if j['status'] == 'complete']),
            'failed': len([j for j in jobs if j['status'] == 'failed'])
        }


# Global instance
ingestion_bridge = IngestionEngineBridge()
