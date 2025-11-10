"""
Automated ML Training Pipeline
Continuously trains forecasting models on live metrics data
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from pathlib import Path

from .temporal_forecasting import temporal_forecaster
from .causal_playbook_reinforcement import causal_rl_agent
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .grace_training_storage import training_storage

logger = logging.getLogger(__name__)


class AutomatedMLTraining:
    """Automatically trains ML models on collected metrics"""
    
    def __init__(self, training_interval_hours: int = 6):
        self.training_interval_hours = training_interval_hours
        self.running = False
        self._task = None
        self.training_count = 0
        self.last_training = None
    
    async def start(self):
        """Start automated training"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._training_loop())
        logger.info(f"[AUTO-TRAIN]  Started (training every {self.training_interval_hours}h)")
        print(f"[AUTO-TRAIN]  Automated ML training started ({self.training_interval_hours}h intervals)")
    
    async def stop(self):
        """Stop training loop"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[AUTO-TRAIN] Stopped")
    
    async def _training_loop(self):
        """Main training loop"""
        while self.running:
            try:
                # Wait for interval
                await asyncio.sleep(self.training_interval_hours * 3600)
                
                if not self.running:
                    break
                
                logger.info("[AUTO-TRAIN]  Starting automated training cycle...")
                print("[AUTO-TRAIN]  Collecting metrics for ML training...")
                
                # Collect training data from metrics snapshots
                training_data = await self._collect_training_data()
                
                if not training_data or sum(len(v) for v in training_data.values()) < 10:
                    logger.warning("[AUTO-TRAIN] Insufficient data for training, skipping cycle")
                    print("[AUTO-TRAIN]  Skipped: not enough data yet")
                    continue
                
                # Train temporal forecaster
                print(f"[AUTO-TRAIN]  Training forecaster on {len(training_data)} metrics...")
                await temporal_forecaster.train(training_data)
                
                self.training_count += 1
                self.last_training = datetime.now(timezone.utc)
                
                logger.info(
                    f"[AUTO-TRAIN]  Training cycle {self.training_count} complete: "
                    f"{len(training_data)} metrics, "
                    f"{sum(len(v) for v in training_data.values())} data points"
                )
                print(
                    f"[AUTO-TRAIN]  Training complete: cycle #{self.training_count}, "
                    f"{sum(len(v) for v in training_data.values())} samples processed"
                )
                
                # Publish training event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="ml.training_complete",
                    source="automated_training",
                    actor="ml_trainer",
                    resource="temporal_forecaster",
                    payload={
                        "cycle_number": self.training_count,
                        "metrics_trained": len(training_data),
                        "total_samples": sum(len(v) for v in training_data.values()),
                        "training_duration_seconds": 0  # Would track actual duration
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
                
                # Log to immutable log
                await immutable_log.append(
                    actor="automated_training",
                    action="training_cycle_complete",
                    resource="ml_models",
                    subsystem="ml_training",
                    payload={
                        "cycle": self.training_count,
                        "metrics": len(training_data),
                        "samples": sum(len(v) for v in training_data.values())
                    },
                    result="success"
                )
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUTO-TRAIN] Training cycle error: {e}", exc_info=True)
                print(f"[AUTO-TRAIN]  Training failed: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
    
    async def _collect_training_data(self) -> Dict[str, List[float]]:
        """Collect recent metrics data for training"""
        from .models import async_session
        
        from sqlalchemy import select
        
        training_data = {}
        
        try:
            # Get last 24 hours of snapshots
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            
            async with async_session() as session:
                result = await session.execute(
                    select(MetricSnapshot)
                    .where(MetricSnapshot.window_start >= cutoff)
                    .order_by(MetricSnapshot.window_start)
                )
                snapshots = result.scalars().all()
            
            # Group by metric_id
            for snapshot in snapshots:
                metric_id = snapshot.metric_id
                if metric_id not in training_data:
                    training_data[metric_id] = []
                
                # Extract value (use avg from stats)
                if snapshot.stats and 'avg' in snapshot.stats:
                    training_data[metric_id].append(snapshot.stats['avg'])
            
            logger.info(
                f"[AUTO-TRAIN] Collected {len(snapshots)} snapshots across "
                f"{len(training_data)} metrics"
            )
            
        except Exception as e:
            logger.error(f"[AUTO-TRAIN] Error collecting training data: {e}")
        
        return training_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training statistics"""
        return {
            "running": self.running,
            "training_count": self.training_count,
            "last_training": self.last_training.isoformat() if self.last_training else None,
            "interval_hours": self.training_interval_hours,
            "next_training_in_hours": self._hours_until_next_training()
        }
    
    def _hours_until_next_training(self) -> float:
        """Calculate hours until next training"""
        if not self.last_training:
            return 0.0
        
        elapsed = (datetime.now(timezone.utc) - self.last_training).total_seconds() / 3600
        remaining = max(0, self.training_interval_hours - elapsed)
        return round(remaining, 2)


# Global singleton
automated_training = AutomatedMLTraining(training_interval_hours=6)
