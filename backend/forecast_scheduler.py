"""
Forecast Scheduler - Periodically generates metric forecasts
Proactively predicts incidents before they occur
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List
from .temporal_forecasting import temporal_forecaster, ForecastRequest
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class ForecastScheduler:
    """Runs forecasting on a schedule to predict future incidents"""
    
    def __init__(self, interval_minutes: int = 15):
        self.interval_minutes = interval_minutes
        self.running = False
        self._task = None
        self.forecast_count = 0
        
        # Key metrics to forecast
        self.key_metrics = [
            "api.latency_p95",
            "api.error_rate",
            "executor.queue_depth",
            "autonomy.plan_success_rate",
            "infra.cpu_utilization",
            "infra.memory_utilization"
        ]
    
    async def start(self):
        """Start the forecast scheduler"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._forecast_loop())
        logger.info(f"[FORECAST-SCHED]  Started (running every {self.interval_minutes}min)")
        print(f"[FORECAST-SCHED]  Forecasting scheduler started ({self.interval_minutes}min intervals)")
    
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[FORECAST-SCHED] Stopped")
    
    async def _forecast_loop(self):
        """Main forecasting loop"""
        while self.running:
            try:
                await asyncio.sleep(self.interval_minutes * 60)
                
                if not self.running:
                    break
                
                logger.info("[FORECAST-SCHED]  Running forecast cycle...")
                print(f"[FORECAST-SCHED]  Generating {len(self.key_metrics)}-metric forecast...")
                
                # Generate forecasts
                request = ForecastRequest(
                    metric_ids=self.key_metrics,
                    horizon_minutes=60,
                    include_trust_signals=True,
                    include_learning_signals=True
                )
                
                forecasts = await temporal_forecaster.forecast(request)
                
                # Analyze forecasts for predicted incidents
                predicted_incidents = []
                for forecast in forecasts:
                    # Check if forecast predicts critical values
                    max_predicted = max(forecast.predicted_values) if forecast.predicted_values else 0
                    
                    # Get thresholds from catalog (simplified check)
                    critical_threshold = self._get_critical_threshold(forecast.metric_id)
                    
                    if max_predicted > critical_threshold:
                        predicted_incidents.append({
                            "metric_id": forecast.metric_id,
                            "predicted_max": max_predicted,
                            "threshold": critical_threshold,
                            "confidence": forecast.confidence,
                            "minutes_until": self._predict_breach_time(forecast)
                        })
                
                if predicted_incidents:
                    logger.warning(
                        f"[FORECAST-SCHED]  Predicted {len(predicted_incidents)} future incidents"
                    )
                    print(
                        f"[FORECAST-SCHED]  PREDICTION: {len(predicted_incidents)} incidents "
                        f"likely in next 60min"
                    )
                    
                    # Publish prediction event
                    await trigger_mesh.publish(TriggerEvent(
                        event_type="forecast.incident_predicted",
                        source="forecast_scheduler",
                        actor="temporal_forecaster",
                        resource="predictive_analytics",
                        payload={
                            "predictions": predicted_incidents,
                            "forecast_count": len(forecasts),
                            "horizon_minutes": 60
                        },
                        timestamp=datetime.now(timezone.utc)
                    ))
                else:
                    logger.info("[FORECAST-SCHED]  No incidents predicted")
                    print("[FORECAST-SCHED]  System stable - no incidents predicted")
                
                self.forecast_count += 1
                
                # Log to immutable log
                await immutable_log.append(
                    actor="forecast_scheduler",
                    action="forecast_cycle_complete",
                    resource="forecasting",
                    subsystem="predictive_analytics",
                    payload={
                        "forecasts_generated": len(forecasts),
                        "incidents_predicted": len(predicted_incidents),
                        "cycle_number": self.forecast_count
                    },
                    result="success"
                )
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[FORECAST-SCHED] Error in forecast cycle: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    def _get_critical_threshold(self, metric_id: str) -> float:
        """Get critical threshold for metric (simplified)"""
        thresholds = {
            "api.latency_p95": 500.0,
            "api.error_rate": 0.03,
            "executor.queue_depth": 75.0,
            "autonomy.plan_success_rate": 75.0,
            "infra.cpu_utilization": 85.0,
            "infra.memory_utilization": 90.0
        }
        return thresholds.get(metric_id, 100.0)
    
    def _predict_breach_time(self, forecast) -> int:
        """Predict when metric will breach threshold (minutes from now)"""
        # Simplified: find first value exceeding threshold
        critical = self._get_critical_threshold(forecast.metric_id)
        
        for i, value in enumerate(forecast.predicted_values):
            if value > critical:
                return (i + 1) * 5  # 5-minute intervals
        
        return 60  # Default to end of horizon


# Global singleton
forecast_scheduler = ForecastScheduler(interval_minutes=15)
