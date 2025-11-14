"""
Metrics Snapshot Integration
Connects snapshot aggregator to ML training and forecasting
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from .trigger_mesh import trigger_mesh, TriggerEvent
from .automated_ml_training import automated_training
from .temporal_forecasting import temporal_forecaster, ForecastRequest
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class MetricsSnapshotIntegration:
    """Bridges metrics snapshots to ML systems"""
    
    def __init__(self):
        self.running = False
        self.snapshots_processed = 0
        
    async def start(self):
        """Start integration"""
        if self.running:
            return
        
        # Subscribe to snapshot events
        trigger_mesh.subscribe("metrics.snapshot_created", self._handle_snapshot)
        trigger_mesh.subscribe("metrics.action_recommended", self._handle_recommendation)
        
        self.running = True
        logger.info("[SNAPSHOT-INTEGRATION]  Started")
        print("[SNAPSHOT-INTEGRATION]  Metrics  ML pipeline active")
    
    async def stop(self):
        """Stop integration"""
        self.running = False
        logger.info("[SNAPSHOT-INTEGRATION] Stopped")
    
    async def _handle_snapshot(self, event: TriggerEvent):
        """Handle new metrics snapshot"""
        try:
            snapshot_data = event.payload
            metric_id = snapshot_data.get("metric_id")
            
            self.snapshots_processed += 1
            
            # Check if this snapshot indicates anomaly
            latest_band = snapshot_data.get("latest_band")
            
            if latest_band in ["critical", "warning"]:
                logger.info(
                    f"[SNAPSHOT-INTEGRATION]  {metric_id} in {latest_band} band, "
                    "generating forecast..."
                )
                print(f"[SNAPSHOT-INTEGRATION]  {metric_id}  {latest_band}, predicting trend...")
                
                # Trigger forecast for this metric
                await self._generate_targeted_forecast(metric_id, latest_band)
        
        except Exception as e:
            logger.error(f"[SNAPSHOT-INTEGRATION] Error handling snapshot: {e}")
    
    async def _handle_recommendation(self, event: TriggerEvent):
        """Handle playbook recommendation from aggregator"""
        try:
            playbook_id = event.payload.get("playbook_id")
            metric_id = event.payload.get("metric_id")
            confidence = event.payload.get("confidence", 0.0)
            
            logger.info(
                f"[SNAPSHOT-INTEGRATION]  Playbook '{playbook_id}' recommended "
                f"for {metric_id} (confidence={confidence})"
            )
            print(
                f"[SNAPSHOT-INTEGRATION]  Recommended: {playbook_id}  {metric_id} "
                f"(ML confidence: {confidence:.0%})"
            )
            
            # Log to immutable log
            await immutable_log.append(
                actor="snapshot_integration",
                action="playbook_recommended",
                resource=metric_id,
                subsystem="metrics_ml_bridge",
                payload={
                    "playbook": playbook_id,
                    "metric": metric_id,
                    "confidence": confidence
                },
                result="forwarded"
            )
        
        except Exception as e:
            logger.error(f"[SNAPSHOT-INTEGRATION] Error handling recommendation: {e}")
    
    async def _generate_targeted_forecast(self, metric_id: str, band: str):
        """Generate forecast for specific metric showing anomaly"""
        try:
            request = ForecastRequest(
                metric_ids=[metric_id],
                horizon_minutes=30,  # Shorter horizon for immediate threats
                include_trust_signals=True,
                include_learning_signals=True
            )
            
            forecasts = await temporal_forecaster.forecast(request)
            
            if forecasts:
                forecast = forecasts[0]
                max_predicted = max(forecast.predicted_values) if forecast.predicted_values else 0
                
                logger.info(
                    f"[SNAPSHOT-INTEGRATION]  Forecast for {metric_id}: "
                    f"max={max_predicted:.2f}, confidence={forecast.confidence:.2f}"
                )
                
                # Publish forecast event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="forecast.metric_predicted",
                    source="snapshot_integration",
                    actor="temporal_forecaster",
                    resource=metric_id,
                    payload={
                        "metric_id": metric_id,
                        "current_band": band,
                        "predicted_max": max_predicted,
                        "confidence": forecast.confidence,
                        "horizon_minutes": 30,
                        "feature_importance": forecast.feature_importance
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
        
        except Exception as e:
            logger.error(f"[SNAPSHOT-INTEGRATION] Forecast generation failed: {e}")


# Global singleton
snapshot_integration = MetricsSnapshotIntegration()
