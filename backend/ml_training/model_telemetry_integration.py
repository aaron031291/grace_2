"""
Model Telemetry Integration
Feeds ML metrics into HTM anomaly detector and RAG knowledge graph
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ModelTelemetryIntegration:
    """
    Integrates ML/DL metrics into existing monitoring infrastructure
    
    Feeds:
    - HTM Anomaly Detector: Training durations, loss curves, inference latency
    - RAG Knowledge Graph: Model performance patterns, degradation signals
    - Guardian: Critical model failures
    """
    
    def __init__(self):
        self.running = False
        self.metrics_collected = 0
        self.anomalies_detected = 0
        
        # Collection interval
        self.collection_interval = 300  # 5 minutes
    
    async def start(self):
        """Start telemetry collection"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("[MODEL-TELEMETRY] Starting ML metric collection")
        logger.info("[MODEL-TELEMETRY] Feeding into HTM + RAG every 5 minutes")
        
        # Start collection loop
        asyncio.create_task(self._collection_loop())
    
    async def stop(self):
        """Stop telemetry collection"""
        self.running = False
        logger.info("[MODEL-TELEMETRY] Stopped")
    
    async def _collection_loop(self):
        """Main telemetry collection loop"""
        while self.running:
            try:
                await self._collect_and_publish_metrics()
                self.metrics_collected += 1
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[MODEL-TELEMETRY] Collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_and_publish_metrics(self):
        """Collect ML metrics and publish to HTM + RAG"""
        
        # Collect model metrics
        metrics = await self._collect_model_metrics()
        
        if not metrics:
            return
        
        # Feed to HTM for anomaly detection
        await self._feed_to_htm(metrics)
        
        # Feed to RAG for knowledge graph
        await self._feed_to_rag(metrics)
        
        # Check for critical issues
        await self._check_critical_thresholds(metrics)
    
    async def _collect_model_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all active models"""
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "models": [],
            "embedding_service": {},
            "inference_stats": {}
        }
        
        # Get Ollama model stats
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                metrics["models"] = [
                    {
                        "name": m["name"],
                        "size_bytes": m.get("size", 0),
                        "modified_at": m.get("modified_at")
                    }
                    for m in models
                ]
        except Exception as e:
            logger.debug(f"[MODEL-TELEMETRY] Ollama metrics unavailable: {e}")
        
        # Get embedding service metrics
        try:
            from backend.services.embedding_service import embedding_service
            if hasattr(embedding_service, 'get_stats'):
                metrics["embedding_service"] = embedding_service.get_stats()
        except Exception:
            pass
        
        # Get inference metrics from model orchestrator
        try:
            from backend.model_orchestrator import model_orchestrator
            if hasattr(model_orchestrator, 'get_metrics'):
                metrics["inference_stats"] = await model_orchestrator.get_metrics()
        except Exception:
            pass
        
        return metrics
    
    async def _feed_to_htm(self, metrics: Dict[str, Any]):
        """Feed metrics to HTM anomaly detector"""
        
        try:
            from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
            
            # Feed model count
            model_count = len(metrics.get("models", []))
            htm_detector_pool.feed_metric(
                metric_name="ollama_model_count",
                value=float(model_count),
                timestamp=datetime.utcnow()
            )
            
            # Feed embedding throughput if available
            embedding_stats = metrics.get("embedding_service", {})
            if "throughput" in embedding_stats:
                htm_detector_pool.feed_metric(
                    metric_name="embedding_throughput",
                    value=float(embedding_stats["throughput"]),
                    timestamp=datetime.utcnow()
                )
            
            # Feed inference latency if available
            inference_stats = metrics.get("inference_stats", {})
            if "avg_latency_ms" in inference_stats:
                htm_detector_pool.feed_metric(
                    metric_name="model_inference_latency",
                    value=float(inference_stats["avg_latency_ms"]),
                    timestamp=datetime.utcnow()
                )
            
            logger.debug("[MODEL-TELEMETRY] Metrics fed to HTM")
            
        except Exception as e:
            logger.debug(f"[MODEL-TELEMETRY] HTM feed failed: {e}")
    
    async def _feed_to_rag(self, metrics: Dict[str, Any]):
        """Feed metrics to RAG knowledge graph"""
        
        try:
            from backend.ingestion_services.ingestion_service import ingestion_service
            
            # Create telemetry summary
            summary = f"""Model Telemetry Report
Timestamp: {metrics['timestamp']}

Active Models: {len(metrics.get('models', []))}
Embedding Service: {metrics.get('embedding_service', {}).get('status', 'unknown')}
Inference Stats: {metrics.get('inference_stats', {})}

Model Inventory:
"""
            for model in metrics.get("models", [])[:5]:
                summary += f"- {model['name']} ({model['size_bytes']:,} bytes)\n"
            
            # Ingest into knowledge base
            await ingestion_service.ingest(
                content=summary,
                artifact_type="model_telemetry",
                title=f"Model Telemetry {metrics['timestamp'][:10]}",
                actor="model_telemetry_integration",
                source="system_monitoring",
                domain="ml_ops",
                tags=["telemetry", "ml_metrics", "monitoring"],
                metadata=metrics
            )
            
            logger.debug("[MODEL-TELEMETRY] Metrics fed to RAG")
            
        except Exception as e:
            logger.debug(f"[MODEL-TELEMETRY] RAG feed failed: {e}")
    
    async def _check_critical_thresholds(self, metrics: Dict[str, Any]):
        """Check for critical metric thresholds"""
        
        # Check model count (should have at least 10)
        model_count = len(metrics.get("models", []))
        if model_count < 10:
            logger.warning(f"[MODEL-TELEMETRY] Low model count: {model_count} (expected 21)")
            self.anomalies_detected += 1
        
        # Check embedding service health
        embedding_stats = metrics.get("embedding_service", {})
        if embedding_stats.get("status") == "degraded":
            logger.warning("[MODEL-TELEMETRY] Embedding service degraded")
            self.anomalies_detected += 1
        
        # Check inference latency
        inference_stats = metrics.get("inference_stats", {})
        avg_latency = inference_stats.get("avg_latency_ms", 0)
        if avg_latency > 5000:  # 5 seconds
            logger.warning(f"[MODEL-TELEMETRY] High inference latency: {avg_latency}ms")
            self.anomalies_detected += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics"""
        return {
            "running": self.running,
            "metrics_collected": self.metrics_collected,
            "anomalies_detected": self.anomalies_detected,
            "collection_interval_seconds": self.collection_interval
        }


# Global instance
model_telemetry_integration = ModelTelemetryIntegration()
