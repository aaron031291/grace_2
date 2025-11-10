"""
Temporal forecasting models for proactive intelligence.

This module provides a faade for the Temporal Fusion Transformer (TFT)
that Grace will use to predict multi-metric incident risk ahead of time.

The implementation intentionally ships as a scaffold:
- Concrete training/evaluation hooks will be wired to the metrics snapshot
  store once live telemetry is flowing.
- Model weights can be persisted via Grace's memory/provenance systems.
- Predictions are routed through the proactive intelligence engine to
  trigger early playbook recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from datetime import datetime, timezone
import json
from pathlib import Path
from .immutable_log import immutable_log
from .grace_training_storage import training_storage

logger = logging.getLogger(__name__)


@dataclass
class ForecastRequest:
    """Input payload describing the prediction horizon and feature set."""

    metric_ids: List[str]
    horizon_minutes: int = 60
    include_trust_signals: bool = True
    include_learning_signals: bool = True
    metadata: Optional[Dict[str, str]] = None


@dataclass
class ForecastResult:
    """Structured output returned by the TFT forecaster."""

    metric_id: str
    predicted_values: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    confidence: float
    feature_importance: Dict[str, float]


class TemporalFusionForecaster:
    """
    Temporal Fusion Transformer faade.

    Responsibilities:
    - Train/update the TFT model on metrics snapshots.
    - Generate multi-horizon forecasts per metric.
    - Emit confidence scores and feature attributions for governance review.
    """

    def __init__(self) -> None:
        self._model = None  # Placeholder for actual TFT implementation
        self._model_dir = Path("ml_artifacts") / "temporal_forecaster"
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._last_training_snapshot = {}
        self._training_history: List[Dict] = []
        logger.info("[TEMPORAL-FC] Temporal Fusion Forecaster initialized")

    async def load_or_initialize(self) -> None:
        """
        Load existing weights from Grace's memory workspace or initialize
        a fresh model if none are available.
        """

        model_path = self._model_dir / "tft_model.json"
        
        if model_path.exists():
            try:
                with open(model_path, 'r') as f:
                    self._model = json.load(f)
                logger.info("[TEMPORAL-FC]  Loaded existing TFT model")
                print("[TEMPORAL-FC]  Loaded trained forecasting model")
            except Exception as e:
                logger.warning(f"[TEMPORAL-FC] Failed to load model: {e}, initializing fresh")
                self._model = self._initialize_fresh_model()
        else:
            self._model = self._initialize_fresh_model()
            logger.info("[TEMPORAL-FC]  Initialized fresh TFT model")
            print("[TEMPORAL-FC]  Initialized new forecasting model")
    
    def _initialize_fresh_model(self) -> Dict:
        """Initialize a fresh model structure"""
        return {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metric_baselines": {},
            "seasonal_patterns": {},
            "trend_coefficients": {},
            "trained": False
        }

    async def train(self, training_data: Dict[str, List[float]]) -> None:
        """
        Train or fine-tune the model.

        Args:
            training_data: mapping of metric_id -> ordered list of values.
        """

        if self._model is None:
            await self.load_or_initialize()

        logger.info(f"[TEMPORAL-FC] Training on {len(training_data)} metrics...")
        print(f"[TEMPORAL-FC]  Training on {len(training_data)} metric series")
        
        # Update model with training data baselines
        for metric_id, values in training_data.items():
            if len(values) > 0:
                self._model["metric_baselines"][metric_id] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values)
                }
        
        self._model["trained"] = True
        self._model["last_trained"] = datetime.now(timezone.utc).isoformat()
        
        # Save model
        model_path = self._model_dir / "tft_model.json"
        with open(model_path, 'w') as f:
            json.dump(self._model, f, indent=2)
        
        # Record training snapshot
        self._last_training_snapshot = {
            "metric_count": len(training_data),
            "total_samples": sum(len(v) for v in training_data.values()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._training_history.append(self._last_training_snapshot)
        
        logger.info(f"[TEMPORAL-FC]  Training complete: {len(training_data)} metrics")
        print(f"[TEMPORAL-FC]  Model trained on {sum(len(v) for v in training_data.values())} data points")
        
        # Log to immutable log
        await immutable_log.append(
            actor="temporal_forecaster",
            action="model_trained",
            resource="tft_model",
            subsystem="forecasting",
            payload=self._last_training_snapshot,
            result="success"
        )
        
        # Save training record to storage
        await training_storage.save_knowledge(
            category="code_patterns",
            item_id=f"tft_training_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            content={
                "model_version": self._model.get("version"),
                "metrics_trained": list(training_data.keys()),
                "snapshot": self._last_training_snapshot,
                "baselines": self._model.get("metric_baselines", {})
            },
            source="temporal_forecaster",
            tags=["ml_training", "forecasting", "tft"]
        )

    async def forecast(self, request: ForecastRequest) -> List[ForecastResult]:
        """
        Produce forecasts for the requested metrics.

        Returns:
            List of ForecastResult entries ordered to match the request.
        """

        if self._model is None:
            await self.load_or_initialize()

        logger.info(
            f"[TEMPORAL-FC] Forecasting {len(request.metric_ids)} metrics, "
            f"horizon={request.horizon_minutes}min"
        )
        
        results: List[ForecastResult] = []
        horizon_steps = request.horizon_minutes // 5 or 1  # 5-min resolution
        
        for metric_id in request.metric_ids:
            # Get baseline if available
            baseline = self._model.get("metric_baselines", {}).get(metric_id, {})
            base_value = baseline.get("mean", 0.0)
            
            # Simple prediction: baseline + small variance
            # In production, this would use actual TFT predictions
            predicted = [base_value * (1.0 + 0.05 * (i / horizon_steps)) for i in range(horizon_steps)]
            lower = [p * 0.9 for p in predicted]
            upper = [p * 1.1 for p in predicted]
            
            # Calculate feature importance
            importance = {
                "seasonality": 0.2,
                "recent_trend": 0.3,
                "trust_signals": 0.3 if request.include_trust_signals else 0.0,
                "learning_signals": 0.2 if request.include_learning_signals else 0.0,
            }
            
            confidence = 0.75 if baseline else 0.5

            results.append(
                ForecastResult(
                    metric_id=metric_id,
                    predicted_values=predicted,
                    lower_bound=lower,
                    upper_bound=upper,
                    confidence=confidence,
                    feature_importance=importance,
                )
            )
        
        logger.info(f"[TEMPORAL-FC] Generated {len(results)} forecasts")
        print(f"[TEMPORAL-FC]  Predicted {len(results)} metrics over {request.horizon_minutes}min")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get forecaster statistics"""
        return {
            "model_loaded": self._model is not None,
            "model_trained": self._model.get("trained", False) if self._model else False,
            "metrics_learned": len(self._model.get("metric_baselines", {})) if self._model else 0,
            "training_sessions": len(self._training_history),
            "last_training": self._last_training_snapshot
        }


# Global singleton
temporal_forecaster = TemporalFusionForecaster()


__all__ = [
    "ForecastRequest",
    "ForecastResult",
    "TemporalFusionForecaster",
    "temporal_forecaster",
]
