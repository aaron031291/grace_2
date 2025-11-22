"""
Ingestion Quality Pipeline - Complete Integration
"""
import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

from .deterministic_chunker import DeterministicChunker
from .fingerprinting_service import fingerprinting_service
from .pii_scrubber_middleware import pii_scrubber_middleware
from .ingestion_metrics_emitter import ingestion_metrics_emitter

logger = logging.getLogger(__name__)

class IngestionQualityPipeline:
    """Complete ingestion quality pipeline"""
    
    def __init__(self, config: Dict = None):
        self.chunker = DeterministicChunker(config)
        self.pipeline_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_processing_time": 0.0
        }
    
    async def process_content(self, content: str, source_id: str, 
                            metadata: Dict = None) -> Dict[str, Any]:
        """Process content through complete quality pipeline"""
        start_time = datetime.utcnow()
        
        try:
            # Stage 1: Deterministic Chunking
            chunks = await self.chunker.chunk_text(content, source_id)
            logger.info(f"Chunked {source_id}: {len(chunks)} chunks")
            
            # Stage 2: Fingerprinting & Deduplication
            unique_chunks, dedup_stats = await fingerprinting_service.check_duplicates(chunks)
            logger.info(f"Deduplicated {source_id}: {len(chunks)} -> {len(unique_chunks)} chunks")
            
            # Stage 3: PII Scrubbing
            scrubbed_chunks, pii_stats = await pii_scrubber_middleware.scrub_content(unique_chunks)
            logger.info(f"PII scrubbed {source_id}: {pii_stats['total_redactions']} redactions")
            
            # Stage 4: Metrics Emission
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            metrics = await ingestion_metrics_emitter.emit_ingestion_metrics(
                scrubbed_chunks, dedup_stats, pii_stats, processing_time
            )
            
            # Update pipeline stats
            self.pipeline_stats["total_runs"] += 1
            self.pipeline_stats["successful_runs"] += 1
            self._update_avg_processing_time(processing_time)
            
            return {
                "status": "success",
                "source_id": source_id,
                "original_chunks": len(chunks),
                "final_chunks": len(scrubbed_chunks),
                "deduplication_stats": dedup_stats,
                "pii_stats": pii_stats,
                "metrics": metrics,
                "processing_time": processing_time,
                "chunks": scrubbed_chunks
            }
            
        except Exception as e:
            self.pipeline_stats["total_runs"] += 1
            self.pipeline_stats["failed_runs"] += 1
            logger.error(f"Pipeline failed for {source_id}: {e}")
            
            return {
                "status": "failed",
                "source_id": source_id,
                "error": str(e),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
    
    def _update_avg_processing_time(self, processing_time: float):
        """Update average processing time"""
        total_runs = self.pipeline_stats["successful_runs"]
        current_avg = self.pipeline_stats["avg_processing_time"]
        self.pipeline_stats["avg_processing_time"] = (
            (current_avg * (total_runs - 1) + processing_time) / total_runs
        )
    
    def get_pipeline_stats(self) -> Dict:
        """Get pipeline statistics"""
        return {
            **self.pipeline_stats,
            "success_rate": self.pipeline_stats["successful_runs"] / max(1, self.pipeline_stats["total_runs"]),
            "chunker_stats": self.chunker.stats,
            "fingerprinting_stats": fingerprinting_service.get_stats(),
            "pii_stats": pii_scrubber_middleware.get_stats()
        }

# Global instance
ingestion_quality_pipeline = IngestionQualityPipeline()
