"""
Metrics Integration Module
Safe wrappers for integrating metrics into existing code without breaking functionality
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def safe_metric_publish(func):
    """
    Decorator to safely publish metrics without breaking main functionality
    
    Usage:
        @safe_metric_publish
        async def my_function():
            result = await do_work()
            await publish_metric("domain", "metric", 1.0)
            return result
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}", exc_info=True)
            raise
    return wrapper


async def safe_publish_metric(domain: str, kpi: str, value: float, metadata: Optional[Dict[str, Any]] = None):
    """
    Safely publish a metric - failures won't break the calling code
    
    Args:
        domain: Domain name (e.g., "transcendence", "ml")
        kpi: KPI name (e.g., "task_success", "model_accuracy")
        value: Metric value
        metadata: Optional metadata
    """
    try:
        from backend.metrics_service import publish_metric
        await publish_metric(domain, kpi, value, metadata)
    except ImportError as e:
        logger.warning(f"Metrics service not available: {e}")
    except Exception as e:
        logger.error(f"Failed to publish metric {domain}.{kpi}: {e}")
        # Don't re-raise - metric failures shouldn't break main functionality


def fire_and_forget_metric(domain: str, kpi: str, value: float, metadata: Optional[Dict[str, Any]] = None):
    """
    Fire-and-forget metric publishing for sync contexts
    
    Usage in sync code:
        fire_and_forget_metric("transcendence", "task_success", 1.0)
    """
    try:
        asyncio.create_task(safe_publish_metric(domain, kpi, value, metadata))
    except RuntimeError:
        # No event loop - try to create one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(safe_publish_metric(domain, kpi, value, metadata))
            else:
                loop.run_until_complete(safe_publish_metric(domain, kpi, value, metadata))
        except Exception as e:
            logger.warning(f"Could not publish metric in sync context: {e}")


class MetricsIntegration:
    """
    Easy-to-use metrics integration class
    
    Usage:
        metrics = MetricsIntegration("transcendence")
        await metrics.track_success(True)
        await metrics.track_quality(0.95)
    """
    
    def __init__(self, domain: str):
        self.domain = domain
    
    async def track(self, kpi: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Track a metric"""
        await safe_publish_metric(self.domain, kpi, value, metadata)
    
    async def track_success(self, success: bool, metadata: Optional[Dict[str, Any]] = None):
        """Track success/failure"""
        await self.track("task_success", 1.0 if success else 0.0, metadata)
    
    async def track_quality(self, score: float, metadata: Optional[Dict[str, Any]] = None):
        """Track quality score (0.0 to 1.0)"""
        await self.track("quality_score", max(0.0, min(1.0, score)), metadata)
    
    async def track_count(self, kpi: str, count: int, metadata: Optional[Dict[str, Any]] = None):
        """Track a count"""
        await self.track(kpi, float(count), metadata)
    
    async def track_duration(self, kpi: str, seconds: float, metadata: Optional[Dict[str, Any]] = None):
        """Track duration in seconds"""
        await self.track(kpi, seconds, metadata)


# Domain-specific integrations

class TranscendenceMetrics(MetricsIntegration):
    """Metrics for Transcendence domain"""
    
    def __init__(self):
        super().__init__("transcendence")
    
    async def track_task_completed(self, success: bool, quality: float = 0.85):
        """Track task completion"""
        await self.track_success(success)
        if success:
            await self.track_quality(quality)
    
    async def track_plan_created(self, quality: float = 0.85):
        """Track plan creation"""
        await self.track("planning_accuracy", quality)


class SecurityMetrics(MetricsIntegration):
    """Metrics for Security domain"""
    
    def __init__(self):
        super().__init__("security")
    
    async def track_scan(self, threats_found: int, coverage: float, duration: float):
        """Track security scan"""
        await self.track_count("threats_detected", threats_found)
        await self.track("scan_coverage", coverage)
        await self.track_duration("response_time", duration)


class KnowledgeMetrics(MetricsIntegration):
    """Metrics for Knowledge domain"""
    
    def __init__(self):
        super().__init__("knowledge")
    
    async def track_ingestion(self, trust_score: float, source_count: int = 1):
        """Track knowledge ingestion"""
        await self.track("trust_score", trust_score)
        await self.track_count("ingestion_rate", source_count)


class MLMetrics(MetricsIntegration):
    """Metrics for ML domain"""
    
    def __init__(self):
        super().__init__("ml")
    
    async def track_training(self, accuracy: float, duration: float):
        """Track model training"""
        await self.track("model_accuracy", accuracy)
        await self.track_duration("training_time", duration)
    
    async def track_deployment(self, success: bool, latency: float = 0.032):
        """Track model deployment"""
        await self.track_success(success, {"type": "deployment"})
        await self.track("inference_latency", latency)


# Global instances for easy import
transcendence_metrics = TranscendenceMetrics()
security_metrics = SecurityMetrics()
knowledge_metrics = KnowledgeMetrics()
ml_metrics = MLMetrics()


# Example integration patterns

async def example_task_execution():
    """Example: Integrating metrics into task execution"""
    
    # At the start of a task
    metrics = MetricsIntegration("transcendence")
    
    try:
        # Your existing code
        result = await execute_task()
        
        # Track success
        await metrics.track_success(result.get('success', False))
        
        if result.get('success'):
            # Track quality if successful
            await metrics.track_quality(result.get('quality_score', 0.85))
        
        return result
    
    except Exception as e:
        # Track failure
        await metrics.track_success(False, {"error": str(e)})
        raise


async def example_security_scan():
    """Example: Integrating metrics into security scanning"""
    
    import time
    metrics = SecurityMetrics()
    
    start = time.time()
    try:
        # Your existing scan code
        threats = await perform_scan()
        duration = time.time() - start
        
        # Track scan metrics
        await metrics.track_scan(
            threats_found=len(threats),
            coverage=calculate_coverage(),
            duration=duration
        )
        
        return threats
    
    except Exception as e:
        # Still track what we can
        duration = time.time() - start
        await metrics.track_duration("scan_failed_after", duration)
        raise


# Convenience functions for quick integration

async def track_transcendence_task(success: bool, quality: float = 0.85):
    """Quick helper for transcendence tasks"""
    await transcendence_metrics.track_task_completed(success, quality)


async def track_security_scan(threats: int, coverage: float, duration: float):
    """Quick helper for security scans"""
    await security_metrics.track_scan(threats, coverage, duration)


async def track_knowledge_ingestion(trust: float, count: int = 1):
    """Quick helper for knowledge ingestion"""
    await knowledge_metrics.track_ingestion(trust, count)


async def track_ml_training(accuracy: float, duration: float):
    """Quick helper for ML training"""
    await ml_metrics.track_training(accuracy, duration)
