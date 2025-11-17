"""
Guardian Metrics Publisher - Phase 1
Publish Guardian and OSI probe metrics to cognition system
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GuardianMetricsPublisher:
    """
    Publishes Guardian metrics to the cognition metrics system
    """
    
    def __init__(self):
        self.domain = "guardian"
    
    async def publish_playbook_metrics(self):
        """
        Publish metrics for all Guardian playbooks
        """
        try:
            from backend.core.guardian_playbooks import GuardianPlaybookRegistry
            from backend.metrics_service import publish_metric
            
            registry = GuardianPlaybookRegistry()
            playbooks = registry.playbooks
            
            # Aggregate metrics
            total_executions = sum(pb.executions for pb in playbooks.values())
            total_successes = sum(pb.successes for pb in playbooks.values())
            total_failures = sum(pb.failures for pb in playbooks.values())
            
            success_rate = (total_successes / total_executions) if total_executions > 0 else 0
            
            # Publish aggregate metrics
            await publish_metric(self.domain, "total_playbook_executions", float(total_executions))
            await publish_metric(self.domain, "playbook_successes", float(total_successes))
            await publish_metric(self.domain, "playbook_failures", float(total_failures))
            await publish_metric(self.domain, "playbook_success_rate", success_rate)
            await publish_metric(self.domain, "registered_playbooks", float(len(playbooks)))
            
            # Publish per-playbook metrics
            for playbook_id, playbook in playbooks.items():
                pb_success_rate = (playbook.successes / playbook.executions) if playbook.executions > 0 else 0
                
                await publish_metric(
                    self.domain,
                    f"playbook_{playbook_id}_executions",
                    float(playbook.executions),
                    {"playbook_name": playbook.name, "priority": playbook.priority}
                )
                
                await publish_metric(
                    self.domain,
                    f"playbook_{playbook_id}_success_rate",
                    pb_success_rate,
                    {"playbook_name": playbook.name}
                )
            
            logger.info(f"[GUARDIAN-METRICS] Published metrics for {len(playbooks)} playbooks")
            return True
        
        except Exception as e:
            logger.error(f"[GUARDIAN-METRICS] Failed to publish playbook metrics: {e}")
            return False
    
    async def publish_osi_probe_metrics(self):
        """
        Publish OSI layer probe health metrics
        """
        try:
            from backend.guardian.osi_canary_probes import osi_canary_probes
            from backend.metrics_service import publish_metric
            
            # Run probes
            results = await osi_canary_probes.probe_all_layers()
            summary = osi_canary_probes.get_health_summary()
            
            # Publish summary metrics
            await publish_metric(self.domain, "osi_layers_healthy", float(summary['healthy']))
            await publish_metric(self.domain, "osi_layers_degraded", float(summary['degraded']))
            await publish_metric(self.domain, "osi_layers_failed", float(summary['failed']))
            await publish_metric(self.domain, "osi_health_percentage", summary['health_percentage'])
            
            # Publish per-layer metrics
            for layer, result in results.items():
                layer_name = layer.name.lower().replace('_', '-')
                status_value = {
                    'healthy': 1.0,
                    'degraded': 0.5,
                    'failed': 0.0,
                    'unknown': 0.0
                }.get(result.status.value, 0.0)
                
                await publish_metric(
                    self.domain,
                    f"osi_{layer_name}_status",
                    status_value,
                    {"layer_number": layer.value, "latency_ms": result.latency_ms}
                )
                
                await publish_metric(
                    self.domain,
                    f"osi_{layer_name}_latency",
                    result.latency_ms,
                    {"layer_number": layer.value}
                )
            
            logger.info(f"[GUARDIAN-METRICS] Published OSI probe metrics for {len(results)} layers")
            return True
        
        except Exception as e:
            logger.error(f"[GUARDIAN-METRICS] Failed to publish OSI metrics: {e}")
            return False
    
    async def publish_mttr_metrics(self):
        """
        Publish MTTR (Mean Time To Recovery) metrics
        """
        try:
            from backend.metrics_service import publish_metric
            
            # TODO: Calculate real MTTR from incident log
            # For now, use placeholder
            mttr_seconds = 45.0
            mttr_minutes = mttr_seconds / 60
            
            await publish_metric(self.domain, "mttr_seconds", mttr_seconds)
            await publish_metric(self.domain, "mttr_minutes", mttr_minutes)
            
            # Target MTTR is 2 minutes (120 seconds)
            target_mttr = 120.0
            mttr_compliance = 1.0 if mttr_seconds <= target_mttr else 0.0
            
            await publish_metric(self.domain, "mttr_target_compliance", mttr_compliance)
            
            logger.info(f"[GUARDIAN-METRICS] Published MTTR metrics: {mttr_seconds}s")
            return True
        
        except Exception as e:
            logger.error(f"[GUARDIAN-METRICS] Failed to publish MTTR metrics: {e}")
            return False
    
    async def publish_all_metrics(self):
        """
        Publish all Guardian metrics
        """
        results = await asyncio.gather(
            self.publish_playbook_metrics(),
            self.publish_osi_probe_metrics(),
            self.publish_mttr_metrics(),
            return_exceptions=True
        )
        
        success_count = sum(1 for r in results if r is True)
        total = len(results)
        
        logger.info(f"[GUARDIAN-METRICS] Published {success_count}/{total} metric categories")
        
        return success_count == total


# Global instance
guardian_metrics_publisher = GuardianMetricsPublisher()


# Background task to publish metrics periodically
async def start_metrics_publisher(interval_seconds: int = 60):
    """
    Start background task to publish Guardian metrics
    
    Args:
        interval_seconds: How often to publish metrics (default: 60s)
    """
    logger.info(f"[GUARDIAN-METRICS] Starting metrics publisher (interval: {interval_seconds}s)")
    
    while True:
        try:
            await guardian_metrics_publisher.publish_all_metrics()
        except Exception as e:
            logger.error(f"[GUARDIAN-METRICS] Error in publisher loop: {e}")
        
        await asyncio.sleep(interval_seconds)
