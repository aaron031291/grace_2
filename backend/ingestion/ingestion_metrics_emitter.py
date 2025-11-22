"""
Ingestion Metrics Emitter - Emit to Metrics Bus
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict, Counter
import logging

from backend.metrics_service import metrics_service
from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class IngestionMetricsEmitter:
    """Emit ingestion metrics to metrics bus"""
    
    def __init__(self):
        self.metrics_buffer = []
        self.source_diversity_tracker = defaultdict(int)
        self.chunk_size_histogram = defaultdict(int)
        
    async def emit_ingestion_metrics(self, 
                                   chunks: List[Dict],
                                   dedup_stats: Dict,
                                   pii_stats: Dict,
                                   processing_time: float):
        """Emit comprehensive ingestion metrics"""
        
        # Calculate metrics
        metrics = await self._calculate_metrics(chunks, dedup_stats, pii_stats, processing_time)
        
        # Emit to metrics service
        await self._emit_to_metrics_bus(metrics)
        
        # Log metrics
        await self._log_metrics(metrics)
        
        return metrics
    
    async def _calculate_metrics(self, chunks: List[Dict], dedup_stats: Dict, 
                               pii_stats: Dict, processing_time: float) -> Dict:
        """Calculate all ingestion metrics"""
        
        # Chunk size histogram
        chunk_sizes = [chunk.get("char_count", 0) for chunk in chunks]
        size_histogram = self._build_size_histogram(chunk_sizes)
        
        # Source diversity
        sources = [chunk.get("source_id", "unknown") for chunk in chunks]
        source_diversity = self._calculate_source_diversity(sources)
        
        # Deduplication rate
        original_count = dedup_stats.get("original_count", 0)
        duplicates_removed = dedup_stats.get("duplicates_removed", 0) + dedup_stats.get("similarity_removed", 0)
        dup_rate = duplicates_removed / max(1, original_count)
        
        # PII hit rate
        total_processed = pii_stats.get("total_processed", 0)
        items_with_pii = pii_stats.get("items_with_pii", 0)
        pii_hit_rate = items_with_pii / max(1, total_processed)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "chunk_metrics": {
                "total_chunks": len(chunks),
                "size_histogram": size_histogram,
                "avg_chunk_size": sum(chunk_sizes) / max(1, len(chunk_sizes)),
                "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
                "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0
            },
            "deduplication_metrics": {
                "duplicate_rate": dup_rate,
                "original_count": original_count,
                "duplicates_removed": duplicates_removed,
                "unique_retained": dedup_stats.get("unique_count", 0)
            },
            "pii_metrics": {
                "pii_hit_rate": pii_hit_rate,
                "total_redactions": pii_stats.get("total_redactions", 0),
                "pii_types_found": pii_stats.get("pii_types_found", {})
            },
            "source_diversity": source_diversity,
            "performance_metrics": {
                "processing_time_seconds": processing_time,
                "chunks_per_second": len(chunks) / max(0.001, processing_time),
                "throughput_chars_per_second": sum(chunk_sizes) / max(0.001, processing_time)
            }
        }
    
    def _build_size_histogram(self, chunk_sizes: List[int]) -> Dict[str, int]:
        """Build chunk size histogram with bins"""
        histogram = {
            "0-250": 0,
            "251-500": 0, 
            "501-1000": 0,
            "1001-1500": 0,
            "1501-2000": 0,
            "2000+": 0
        }
        
        for size in chunk_sizes:
            if size <= 250:
                histogram["0-250"] += 1
            elif size <= 500:
                histogram["251-500"] += 1
            elif size <= 1000:
                histogram["501-1000"] += 1
            elif size <= 1500:
                histogram["1001-1500"] += 1
            elif size <= 2000:
                histogram["1501-2000"] += 1
            else:
                histogram["2000+"] += 1
        
        return histogram
    
    def _calculate_source_diversity(self, sources: List[str]) -> Dict:
        """Calculate source diversity metrics"""
        source_counts = Counter(sources)
        unique_sources = len(source_counts)
        total_chunks = len(sources)
        
        # Shannon diversity index
        shannon_diversity = 0.0
        if total_chunks > 0:
            for count in source_counts.values():
                p = count / total_chunks
                if p > 0:
                    shannon_diversity -= p * (p ** 0.5)  # Simplified Shannon
        
        return {
            "unique_sources": unique_sources,
            "total_chunks": total_chunks,
            "diversity_index": shannon_diversity,
            "avg_chunks_per_source": total_chunks / max(1, unique_sources),
            "source_distribution": dict(source_counts.most_common(10))
        }
    
    async def _emit_to_metrics_bus(self, metrics: Dict):
        """Emit metrics to metrics service"""
        try:
            # Emit individual metrics
            await metrics_service.capture_metrics("ingestion.chunks.total", metrics["chunk_metrics"]["total_chunks"])
            await metrics_service.capture_metrics("ingestion.chunks.avg_size", metrics["chunk_metrics"]["avg_chunk_size"])
            await metrics_service.capture_metrics("ingestion.dedup.rate", metrics["deduplication_metrics"]["duplicate_rate"])
            await metrics_service.capture_metrics("ingestion.pii.hit_rate", metrics["pii_metrics"]["pii_hit_rate"])
            await metrics_service.capture_metrics("ingestion.sources.diversity", metrics["source_diversity"]["diversity_index"])
            await metrics_service.capture_metrics("ingestion.performance.chunks_per_sec", metrics["performance_metrics"]["chunks_per_second"])
            
            # Emit histogram as structured metric
            for bin_name, count in metrics["chunk_metrics"]["size_histogram"].items():
                await metrics_service.capture_metrics(f"ingestion.chunks.size_hist.{bin_name}", count)
            
        except Exception as e:
            logger.error(f"Failed to emit metrics to bus: {e}")
    
    async def _log_metrics(self, metrics: Dict):
        """Log metrics for audit trail"""
        await immutable_log.append(
            actor="ingestion_metrics_emitter",
            action="metrics_emitted",
            resource="ingestion_pipeline",
            outcome="success",
            payload={
                "metrics_summary": {
                    "total_chunks": metrics["chunk_metrics"]["total_chunks"],
                    "duplicate_rate": metrics["deduplication_metrics"]["duplicate_rate"],
                    "pii_hit_rate": metrics["pii_metrics"]["pii_hit_rate"],
                    "source_diversity": metrics["source_diversity"]["diversity_index"],
                    "processing_time": metrics["performance_metrics"]["processing_time_seconds"]
                }
            }
        )

# Global instance
ingestion_metrics_emitter = IngestionMetricsEmitter()
