"""
Benchmark Scheduler
Evaluates 90% benchmarks hourly and emits product.elevation_ready events
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from .cognition_metrics import get_metrics_engine
from .metrics_service import get_metrics_collector
from .trigger_mesh import trigger_mesh

logger = logging.getLogger(__name__)


class BenchmarkScheduler:
    """
    Background scheduler that evaluates benchmarks and triggers SaaS readiness events
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.running = False
        self.interval_seconds = 3600  # 1 hour
        self.last_saas_ready = False
        
    async def start(self):
        """Start the benchmark evaluation scheduler"""
        if self.running:
            logger.warning("Benchmark scheduler already running")
            return
        
        self.running = True
        logger.info(f"Benchmark scheduler started (interval: {self.interval_seconds}s)")
        
        # Run initial evaluation
        await self.evaluate_benchmarks()
        
        # Schedule periodic evaluation
        asyncio.create_task(self._run_loop())
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Benchmark scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await asyncio.sleep(self.interval_seconds)
                await self.evaluate_benchmarks()
            except Exception as e:
                logger.error(f"Benchmark evaluation error: {e}")
    
    async def evaluate_benchmarks(self):
        """Evaluate current benchmarks and emit events if needed"""
        try:
            collector = get_metrics_collector()
            engine = get_metrics_engine()
            
            # Sync latest metrics
            for domain, kpis in collector.aggregates.items():
                if domain in engine.domains:
                    engine.update_domain(domain, kpis)
            
            # Get current status
            overall_health = engine.get_overall_health()
            overall_trust = engine.get_overall_trust()
            overall_confidence = engine.get_overall_confidence()
            saas_ready = engine.is_saas_ready()
            
            # Log benchmark status
            await self._log_benchmark_status(overall_health, overall_trust, overall_confidence, saas_ready)
            
            # Check for state changes
            if saas_ready and not self.last_saas_ready:
                # Just crossed into SaaS ready state!
                await self._emit_elevation_ready_event(overall_health, overall_trust, overall_confidence)
                await self._record_readiness_event("elevation_ready", overall_health, overall_trust, overall_confidence, True)
            
            elif not saas_ready and self.last_saas_ready:
                # Dropped below threshold
                await self._record_readiness_event("threshold_lost", overall_health, overall_trust, overall_confidence, False)
            
            elif saas_ready:
                # Still ready
                await self._record_readiness_event("threshold_sustained", overall_health, overall_trust, overall_confidence, True)
            
            self.last_saas_ready = saas_ready
            
            logger.info(f"Benchmark evaluation: Health={overall_health:.1%}, Trust={overall_trust:.1%}, Confidence={overall_confidence:.1%}, Ready={saas_ready}")
            
        except Exception as e:
            logger.error(f"Benchmark evaluation failed: {e}")
    
    async def _log_benchmark_status(self, health: float, trust: float, confidence: float, ready: bool):
        """Log benchmark history to database"""
        if not self.db_session:
            return
        
        try:
            from .metrics_models import BenchmarkHistory
            
            for metric_name, value in [("overall_health", health), ("overall_trust", trust), ("overall_confidence", confidence)]:
                history = BenchmarkHistory(
                    metric_name=metric_name,
                    value=value,
                    threshold=0.90,
                    sustained=ready,
                    window_days=7,
                    timestamp=datetime.now(),
                    metadata={"saas_ready": ready}
                )
                
                self.db_session.add(history)
            
            await self.db_session.commit()
        except Exception as e:
            logger.warning(f"Failed to log benchmark history: {e}")
    
    async def _emit_elevation_ready_event(self, health: float, trust: float, confidence: float):
        """Emit product.elevation_ready event when 90% sustained"""
        try:
            event_data = {
                "event": "product.elevation_ready",
                "timestamp": datetime.now().isoformat(),
                "overall_health": health,
                "overall_trust": trust,
                "overall_confidence": confidence,
                "message": "Grace has sustained 90%+ performance for 7 days - Ready for SaaS commercialization!",
                "next_steps": [
                    "Implement multi-tenant authentication",
                    "Set up billing infrastructure (Stripe)",
                    "Create deployment automation",
                    "Build support playbooks",
                    "Launch beta program"
                ]
            }
            
            # Emit via trigger mesh
            await trigger_mesh.emit("product.elevation_ready", event_data)
            
            logger.info("🚀 PRODUCT ELEVATION READY EVENT EMITTED!")
            logger.info(f"   Health: {health:.1%}, Trust: {trust:.1%}, Confidence: {confidence:.1%}")
            
        except Exception as e:
            logger.error(f"Failed to emit elevation event: {e}")
    
    async def _record_readiness_event(self, event_type: str, health: float, trust: float, confidence: float, ready: bool):
        """Record SaaS readiness event to database"""
        if not self.db_session:
            return
        
        try:
            from .metrics_models import SaaSReadinessEvent
            
            message = {
                "elevation_ready": "🚀 Ready for SaaS commercialization!",
                "threshold_sustained": "Maintaining 90%+ performance",
                "threshold_lost": "Performance dropped below 90% threshold",
                "threshold_crossed": "Crossed 90% threshold"
            }.get(event_type, "Benchmark event")
            
            event = SaaSReadinessEvent(
                event_type=event_type,
                overall_health=health,
                overall_trust=trust,
                overall_confidence=confidence,
                saas_ready=ready,
                message=message,
                triggered_at=datetime.now(),
                metadata={
                    "health": health,
                    "trust": trust,
                    "confidence": confidence
                },
                notified=event_type == "elevation_ready"
            )
            
            self.db_session.add(event)
            await self.db_session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to record readiness event: {e}")


# Global scheduler instance
_global_scheduler: Optional[BenchmarkScheduler] = None


def get_benchmark_scheduler(db_session: Optional[Session] = None) -> BenchmarkScheduler:
    """Get or create the global benchmark scheduler"""
    global _global_scheduler
    
    if _global_scheduler is None:
        _global_scheduler = BenchmarkScheduler(db_session)
    
    return _global_scheduler


async def start_benchmark_scheduler(db_session: Optional[Session] = None):
    """Start the benchmark evaluation scheduler"""
    scheduler = get_benchmark_scheduler(db_session)
    await scheduler.start()


async def stop_benchmark_scheduler():
    """Stop the benchmark scheduler"""
    global _global_scheduler
    if _global_scheduler:
        await _global_scheduler.stop()
