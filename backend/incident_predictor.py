"""
Incident Predictor
Analyzes forecasts and triggers early warnings
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .grace_training_storage import training_storage

logger = logging.getLogger(__name__)


class IncidentPredictor:
    """Monitors forecasts and raises early warnings for predicted incidents"""
    
    def __init__(self):
        self.running = False
        self.predictions_made = 0
        self.incidents_prevented = 0
        
    async def start(self):
        """Start incident predictor"""
        if self.running:
            return
        
        # Subscribe to forecast events
        trigger_mesh.subscribe("forecast.incident_predicted", self._handle_prediction)
        trigger_mesh.subscribe("forecast.metric_predicted", self._handle_metric_forecast)
        
        self.running = True
        logger.info("[INCIDENT-PREDICT]  Started")
        print("[INCIDENT-PREDICT]  Predictive incident detection active")
    
    async def stop(self):
        """Stop predictor"""
        self.running = False
        logger.info("[INCIDENT-PREDICT] Stopped")
    
    async def _handle_prediction(self, event: TriggerEvent):
        """Handle predicted incident"""
        try:
            predictions = event.payload.get("predictions", [])
            
            for prediction in predictions:
                metric_id = prediction.get("metric_id")
                predicted_max = prediction.get("predicted_max")
                confidence = prediction.get("confidence", 0.0)
                minutes_until = prediction.get("minutes_until", 60)
                
                logger.warning(
                    f"[INCIDENT-PREDICT]  PREDICTED INCIDENT: {metric_id} will breach "
                    f"in ~{minutes_until}min (confidence={confidence:.0%})"
                )
                print(
                    f"[INCIDENT-PREDICT]  EARLY WARNING: {metric_id} breach predicted "
                    f"in {minutes_until}min (conf: {confidence:.0%})"
                )
                print(f"[INCIDENT-PREDICT]  Predicted value: {predicted_max:.2f}")
                
                self.predictions_made += 1
                
                # Trigger proactive playbook recommendation
                await self._trigger_early_playbook(metric_id, predicted_max, confidence, minutes_until)
                
                # Save prediction to training storage
                await training_storage.save_knowledge(
                    category="code_patterns",
                    item_id=f"prediction_{metric_id}_{datetime.now(timezone.utc).timestamp()}",
                    content={
                        "type": "incident_prediction",
                        "metric_id": metric_id,
                        "predicted_value": predicted_max,
                        "confidence": confidence,
                        "minutes_until_breach": minutes_until,
                        "prediction_time": datetime.now(timezone.utc).isoformat()
                    },
                    source="incident_predictor",
                    tags=["prediction", "incident", metric_id]
                )
        
        except Exception as e:
            logger.error(f"[INCIDENT-PREDICT] Error handling prediction: {e}")
    
    async def _handle_metric_forecast(self, event: TriggerEvent):
        """Handle individual metric forecast"""
        try:
            metric_id = event.payload.get("metric_id")
            predicted_max = event.payload.get("predicted_max")
            current_band = event.payload.get("current_band")
            confidence = event.payload.get("confidence", 0.0)
            
            # If already in warning/critical and forecast shows worsening
            if current_band in ["warning", "critical"] and confidence > 0.6:
                logger.warning(
                    f"[INCIDENT-PREDICT]  {metric_id} trending worse: "
                    f"current={current_band}, forecast={predicted_max:.2f}"
                )
                print(
                    f"[INCIDENT-PREDICT]  TREND ALERT: {metric_id} likely to worsen "
                    f"(current: {current_band})"
                )
        
        except Exception as e:
            logger.error(f"[INCIDENT-PREDICT] Error handling metric forecast: {e}")
    
    async def _trigger_early_playbook(
        self,
        metric_id: str,
        predicted_value: float,
        confidence: float,
        minutes_until: int
    ):
        """Trigger playbook recommendation before incident occurs"""
        
        # Map metrics to playbooks
        playbook_map = {
            "api.latency_p95": "scale-api-shard",
            "api.error_rate": "restart-workers",
            "executor.queue_depth": "scale-workers",
            "infra.cpu_utilization": "shift-load",
            "infra.memory_utilization": "scale-nodes"
        }
        
        playbook_id = playbook_map.get(metric_id)
        
        if playbook_id:
            logger.info(
                f"[INCIDENT-PREDICT]  Recommending early playbook: {playbook_id} "
                f"for predicted {metric_id} breach"
            )
            print(f"[INCIDENT-PREDICT]  PROACTIVE ACTION: Recommending '{playbook_id}'")
            
            # Publish recommendation
            await trigger_mesh.publish(TriggerEvent(
                event_type="metrics.action_recommended",
                source="incident_predictor",
                actor="predictive_analytics",
                resource=metric_id,
                payload={
                    "playbook_id": playbook_id,
                    "metric_id": metric_id,
                    "band": "predicted_critical",
                    "confidence": confidence,
                    "predicted_value": predicted_value,
                    "minutes_until_breach": minutes_until,
                    "proactive": True
                },
                timestamp=datetime.now(timezone.utc)
            ))
            
            # Log to immutable log
            await immutable_log.append(
                actor="incident_predictor",
                action="early_playbook_recommended",
                resource=metric_id,
                subsystem="predictive_analytics",
                payload={
                    "playbook": playbook_id,
                    "metric": metric_id,
                    "predicted_value": predicted_value,
                    "confidence": confidence,
                    "lead_time_minutes": minutes_until
                },
                result="recommended"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get predictor statistics"""
        return {
            "running": self.running,
            "predictions_made": self.predictions_made,
            "incidents_prevented": self.incidents_prevented,
            "prevention_rate": (
                self.incidents_prevented / max(1, self.predictions_made)
            ) * 100 if self.predictions_made > 0 else 0.0
        }


# Global singleton
incident_predictor = IncidentPredictor()
