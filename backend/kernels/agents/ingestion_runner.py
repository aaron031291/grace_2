"""
Ingestion Runner Agent
Executes ingestion pipelines: chunk → transform → embed
"""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class IngestionRunner:
    """
    Handles file ingestion into Memory Fusion.
    Chunks content, generates embeddings, triggers ML jobs.
    """
    
    def __init__(self, agent_id: str, task_data: Dict, registry=None, kernel=None):
        self.agent_id = agent_id
        self.task_data = task_data
        self.registry = registry
        self.kernel = kernel
        
        self.file_path = task_data.get('path')
        self.metadata = task_data.get('metadata', {})
        
    async def execute(self) -> Dict[str, Any]:
        """
        Ingestion pipeline:
        1. Validate file and check trust
        2. Chunk content
        3. Generate embeddings
        4. Update Memory Fusion
        5. Trigger ML/alert jobs
        6. Update trust metrics
        """
        try:
            logger.info(f"Ingestion Runner {self.agent_id} processing: {self.file_path}")
            
            # Step 1: Validate and trust check
            validation = await self._validate_file()
            if not validation['valid']:
                return {
                    'status': 'skipped',
                    'reason': validation['reason']
                }
            
            # Step 2: Chunk content
            chunks = await self._chunk_content()
            
            # Step 3: Generate embeddings
            embeddings = await self._generate_embeddings(chunks)
            
            # Step 4: Update Memory Fusion
            await self._update_memory_fusion(chunks, embeddings)
            
            # Step 5: Trigger downstream jobs
            await self._trigger_downstream_jobs()
            
            # Step 6: Update trust metrics
            await self._update_trust_metrics(success=True)
            
            # Update ingestion status
            await self._update_ingestion_status('completed')
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'file_path': self.file_path,
                'chunks_processed': len(chunks),
                'embeddings_generated': len(embeddings)
            }
            
        except Exception as e:
            logger.error(f"Ingestion Runner {self.agent_id} failed: {e}")
            await self._update_trust_metrics(success=False)
            await self._update_ingestion_status('failed', str(e))
            
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _validate_file(self) -> Dict:
        """Validate file exists and check trust status"""
        file_path = Path(self.file_path)
        
        if not file_path.exists():
            return {'valid': False, 'reason': 'file_not_found'}
        
        # Check file size (skip if too large for non-streaming ingestion)
        file_size = file_path.stat().st_size
        if file_size > 500 * 1024 * 1024:  # 500 MB
            logger.warning(f"Large file {file_size} bytes, consider streaming ingestion")
        
        # Check trusted sources if it's external
        source_url = self.metadata.get('source_url')
        if source_url and self.kernel.trust_validator:
            trust_check = self.kernel.trust_validator.is_source_trusted(source_url)
            if not trust_check['trusted']:
                return {'valid': False, 'reason': 'untrusted_source'}
        
        return {'valid': True}
    
    async def _chunk_content(self) -> list:
        """Chunk file content for processing"""
        file_path = Path(self.file_path)
        ext = file_path.suffix.lower()
        
        # Text-based files
        if ext in ['.txt', '.md', '.py', '.js', '.json']:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                return self._chunk_text(content)
            except Exception as e:
                logger.error(f"Failed to chunk text file: {e}")
                return []
        
        # For other types, return metadata chunk
        return [{
            'chunk_id': 0,
            'content': f"File: {file_path.name}",
            'metadata': self.metadata
        }]
    
    def _chunk_text(self, content: str, chunk_size: int = 1000) -> list:
        """Chunk text content"""
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunks.append({
                'chunk_id': len(chunks),
                'content': ' '.join(chunk_words),
                'start_offset': i,
                'end_offset': min(i + chunk_size, len(words))
            })
        
        return chunks
    
    async def _generate_embeddings(self, chunks: list) -> list:
        """Generate embeddings for chunks (placeholder)"""
        # In production, call embedding service
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        embeddings = []
        for chunk in chunks:
            # Placeholder: would call actual embedding API
            embeddings.append({
                'chunk_id': chunk['chunk_id'],
                'embedding': [0.0] * 384,  # Placeholder vector
                'model': 'placeholder'
            })
        
        return embeddings
    
    async def _update_memory_fusion(self, chunks: list, embeddings: list):
        """Update Memory Fusion with chunks and embeddings"""
        if not self.registry:
            return
        
        try:
            # Insert chunks into memory_chunks table (if exists)
            for chunk, embedding in zip(chunks, embeddings):
                self.registry.insert_row('memory_chunks', {
                    'file_path': self.file_path,
                    'chunk_id': chunk['chunk_id'],
                    'content': chunk['content'],
                    'embedding': embedding['embedding'],
                    'metadata': {
                        **self.metadata,
                        **chunk.get('metadata', {})
                    },
                    'created_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Inserted {len(chunks)} chunks into Memory Fusion")
            
        except Exception as e:
            logger.error(f"Failed to update Memory Fusion: {e}")
    
    async def _trigger_downstream_jobs(self):
        """Trigger ML jobs, alerts, verification"""
        # Placeholder for triggering:
        # - ML model training/inference
        # - Alert generation
        # - Verification tasks
        logger.info("Triggering downstream jobs (placeholder)")
    
    async def _update_trust_metrics(self, success: bool):
        """Update trust metrics for the source"""
        source_id = self.metadata.get('source_id')
        if source_id and self.kernel.trust_validator:
            try:
                self.kernel.trust_validator.update_quality_metrics(
                    source_id=source_id,
                    success=success,
                    freshness_score=0.9 if success else 0.0
                )
            except Exception as e:
                logger.warning(f"Could not update trust metrics: {e}")
    
    async def _update_ingestion_status(self, status: str, error: str = None):
        """Update ingestion status in memory_documents"""
        if not self.registry:
            return
        
        try:
            # Find the document record
            docs = self.registry.query_rows(
                'memory_documents',
                filters={'file_path': self.file_path},
                limit=1
            )
            
            if docs:
                doc = docs[0]
                doc_id = doc.id if hasattr(doc, 'id') else doc.get('id')
                
                self.registry.update_row('memory_documents', doc_id, {
                    'ingestion_status': status,
                    'ingestion_error': error,
                    'ingested_at': datetime.utcnow().isoformat() if status == 'completed' else None
                })
        except Exception as e:
            logger.warning(f"Could not update ingestion status: {e}")
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping Ingestion Runner {self.agent_id}")
