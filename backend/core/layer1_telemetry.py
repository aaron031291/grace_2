"""
Layer 1 Telemetry Enrichment
Publish structured metrics to observability hub

Metrics:
- Readiness times per kernel
- Restart counts
- Playbook success/failure rates
- Heartbeat gaps
- Resource usage
- Boot performance
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ReadinessMetric:
    """Kernel readiness metric"""
    kernel_name: str
    ready_time_seconds: float
    retry_count: int
    degraded: bool
    timestamp: datetime


@dataclass
class PlaybookMetric:
    """Playbook execution metric"""
    playbook_name: str
    success: bool
    execution_time_seconds: float
    steps_executed: int
    timestamp: datetime


class Layer1Telemetry:
    """
    Layer 1 telemetry publisher
    Sends enriched metrics to observability hub for Layer 2/3 consumption
    """
    
    def __init__(self):
        self.running = False
        self.readiness_metrics: List[ReadinessMetric] = []
        self.playbook_metrics: List[PlaybookMetric] = []
        self.publish_interval = 60  # Publish every minute
    
    async def start(self):
        """Start telemetry publisher"""
        
        if self.running:
            return
        
        self.running = True
        logger.info("[LAYER1-TELEMETRY] Starting telemetry enrichment")
        
        # Start publish loop
        asyncio.create_task(self._publish_loop())
    
    async def stop(self):
        """Stop telemetry"""
        self.running = False
    
    def record_readiness(self, kernel_name: str, ready_time: float, retry_count: int = 0, degraded: bool = False):
        """Record kernel readiness metric"""
        
        metric = ReadinessMetric(
            kernel_name=kernel_name,
            ready_time_seconds=ready_time,
            retry_count=retry_count,
            degraded=degraded,
            timestamp=datetime.utcnow()
        )
        
        self.readiness_metrics.append(metric)
        
        # Keep last 1000
        self.readiness_metrics = self.readiness_metrics[-1000:]
    
    def record_playbook_execution(
        self,
        playbook_name: str,
        success: bool,
        execution_time: float,
        steps_executed: int
    ):
        """Record playbook execution metric"""
        
        metric = PlaybookMetric(
            playbook_name=playbook_name,
            success=success,
            execution_time_seconds=execution_time,
            steps_executed=steps_executed,
            timestamp=datetime.utcnow()
        )
        
        self.playbook_metrics.append(metric)
        
        # Keep last 1000
        self.playbook_metrics = self.playbook_metrics[-1000:]
    
    async def _publish_loop(self):
        """Continuous publish loop"""
        
        while self.running:
            try:
                await self._publish_metrics()
                await asyncio.sleep(self.publish_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[LAYER1-TELEMETRY] Publish error: {e}")
                await asyncio.sleep(120)
    
    async def _publish_metrics(self):
        """Publish enriched metrics to observability hub"""
        
        # Aggregate metrics
        metrics_bundle = self._aggregate_metrics()
        
        # Publish to message bus
        try:
            from .message_bus import message_bus
            
            await message_bus.publish(
                source='layer1_telemetry',
                topic='telemetry.layer1.metrics',
                payload=metrics_bundle
            )
            
            logger.debug("[LAYER1-TELEMETRY] Published metrics bundle")
        
        except Exception as e:
            logger.error(f"[LAYER1-TELEMETRY] Could not publish: {e}")
    
    def _aggregate_metrics(self) -> Dict[str, Any]:
        """Aggregate all Layer 1 metrics"""
        
        # Readiness metrics
        readiness_by_kernel = {}
        for metric in self.readiness_metrics:
            if metric.kernel_name not in readiness_by_kernel:
                readiness_by_kernel[metric.kernel_name] = []
            readiness_by_kernel[metric.kernel_name].append(metric.ready_time_seconds)
        
        readiness_stats = {}
        for kernel, times in readiness_by_kernel.items():
            readiness_stats[kernel] = {
                'count': len(times),
                'avg_ready_time': sum(times) / len(times) if times else 0,
                'min_ready_time': min(times) if times else 0,
                'max_ready_time': max(times) if times else 0
            }
        
        # Playbook metrics
        playbook_stats = {}
        for metric in self.playbook_metrics:
            if metric.playbook_name not in playbook_stats:
                playbook_stats[metric.playbook_name] = {
                    'total': 0,
                    'success': 0,
                    'failure': 0,
                    'avg_execution_time': 0
                }
            
            playbook_stats[metric.playbook_name]['total'] += 1
            if metric.success:
                playbook_stats[metric.playbook_name]['success'] += 1
            else:
                playbook_stats[metric.playbook_name]['failure'] += 1
        
        # Control plane stats
        control_plane_stats = self._get_control_plane_stats()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'layer': 1,
            'readiness': readiness_stats,
            'playbooks': playbook_stats,
            'control_plane': control_plane_stats,
            'total_readiness_events': len(self.readiness_metrics),
            'total_playbook_executions': len(self.playbook_metrics)
        }
    
    def _get_control_plane_stats(self) -> Dict:
        """Get control plane statistics"""
        
        try:
            from .control_plane import control_plane
            
            status = control_plane.get_status()
            
            # Calculate restart counts
            restart_counts = {}
            for name, kernel in control_plane.kernels.items():
                if kernel.restart_count > 0:
                    restart_counts[name] = kernel.restart_count
            
            return {
                'total_kernels': status['total_kernels'],
                'running_kernels': status['running_kernels'],
                'failed_kernels': status['failed_kernels'],
                'restart_counts': restart_counts,
                'system_state': status['system_state']
            }
        
        except Exception:
            return {}


# Global instance
layer1_telemetry = Layer1Telemetry()
