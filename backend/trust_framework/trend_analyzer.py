"""
Historical Trend Analyzer - PRODUCTION
Analyzes metrics over time to identify trends and predict issues
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

from .metrics_aggregator import metrics_collector

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


@dataclass
class Trend:
    """Trend analysis result"""
    
    metric_name: str
    direction: TrendDirection
    slope: float  # Rate of change
    
    # Statistics
    current_value: float
    baseline_value: float
    change_percent: float
    
    # Predictions
    predicted_value_1h: Optional[float] = None
    predicted_value_24h: Optional[float] = None
    
    # Confidence
    confidence: float = 0.0
    data_points: int = 0
    
    # Alerts
    alert_triggered: bool = False
    alert_reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'metric': self.metric_name,
            'trend': {
                'direction': self.direction.value,
                'slope': self.slope,
                'change_percent': self.change_percent
            },
            'values': {
                'current': self.current_value,
                'baseline': self.baseline_value
            },
            'predictions': {
                '1h': self.predicted_value_1h,
                '24h': self.predicted_value_24h
            },
            'confidence': self.confidence,
            'data_points': self.data_points,
            'alert': {
                'triggered': self.alert_triggered,
                'reason': self.alert_reason
            }
        }


class TrendAnalyzer:
    """
    Analyzes historical metrics for trends
    
    Capabilities:
    - Detect improving/degrading trends
    - Predict future values
    - Identify anomalies
    - Trigger alerts on significant changes
    """
    
    # Thresholds for alerts
    DEGRADATION_THRESHOLD = 0.2  # 20% worse = alert
    IMPROVEMENT_THRESHOLD = 0.2  # 20% better = note
    VOLATILITY_THRESHOLD = 0.3  # 30% stddev/mean = volatile
    
    def __init__(self):
        # Statistics
        self.trends_analyzed = 0
        self.alerts_triggered = 0
        
        logger.info("[TREND-ANALYZER] Initialized")
    
    def analyze_trend(
        self,
        metric_name: str,
        time_window_hours: int = 24,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[Trend]:
        """
        Analyze trend for a metric
        
        Args:
            metric_name: Name of metric
            time_window_hours: How far back to look
            tags: Filter by tags
        
        Returns:
            Trend analysis result
        """
        
        self.trends_analyzed += 1
        
        # Query metrics
        end_time = datetime.utcnow().timestamp()
        start_time = end_time - (time_window_hours * 3600)
        
        points = metrics_collector.query(metric_name, start_time, end_time, tags)
        
        if len(points) < 10:
            logger.debug(f"[TREND-ANALYZER] Insufficient data for {metric_name}")
            return None
        
        # Extract values and timestamps
        values = np.array([p.value for p in points])
        timestamps = np.array([p.timestamp for p in points])
        
        # Calculate baseline (first 20% of data)
        baseline_count = max(3, len(values) // 5)
        baseline_value = float(np.mean(values[:baseline_count]))
        
        # Current value (last 20% of data)
        current_count = max(3, len(values) // 5)
        current_value = float(np.mean(values[-current_count:]))
        
        # Calculate trend
        slope = self._calculate_slope(timestamps, values)
        
        # Determine direction
        change_percent = ((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0.0
        
        # Check volatility
        volatility = float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0.0
        
        if volatility > self.VOLATILITY_THRESHOLD:
            direction = TrendDirection.VOLATILE
        elif abs(change_percent) < 5:  # <5% change = stable
            direction = TrendDirection.STABLE
        elif change_percent < -self.DEGRADATION_THRESHOLD * 100:
            direction = TrendDirection.DEGRADING
        elif change_percent > self.IMPROVEMENT_THRESHOLD * 100:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.STABLE
        
        # Predict future values
        predicted_1h = self._predict_value(timestamps, values, hours_ahead=1)
        predicted_24h = self._predict_value(timestamps, values, hours_ahead=24)
        
        # Confidence based on data quantity and consistency
        confidence = min(1.0, len(values) / 100) * (1.0 - volatility)
        
        # Check if alert needed
        alert_triggered = False
        alert_reason = ""
        
        if direction == TrendDirection.DEGRADING and abs(change_percent) > 20:
            alert_triggered = True
            alert_reason = f"Degrading by {abs(change_percent):.1f}%"
            self.alerts_triggered += 1
        
        elif direction == TrendDirection.VOLATILE:
            alert_triggered = True
            alert_reason = f"High volatility: {volatility:.1%}"
            self.alerts_triggered += 1
        
        trend = Trend(
            metric_name=metric_name,
            direction=direction,
            slope=slope,
            current_value=current_value,
            baseline_value=baseline_value,
            change_percent=change_percent,
            predicted_value_1h=predicted_1h,
            predicted_value_24h=predicted_24h,
            confidence=confidence,
            data_points=len(values),
            alert_triggered=alert_triggered,
            alert_reason=alert_reason
        )
        
        return trend
    
    def _calculate_slope(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate trend slope using linear regression"""
        
        try:
            coeffs = np.polyfit(x, y, 1)
            return float(coeffs[0])
        except:
            return 0.0
    
    def _predict_value(
        self,
        timestamps: np.ndarray,
        values: np.ndarray,
        hours_ahead: int
    ) -> float:
        """Predict value hours_ahead in the future"""
        
        try:
            # Linear extrapolation
            coeffs = np.polyfit(timestamps, values, 1)
            slope, intercept = coeffs
            
            # Predict
            future_time = datetime.utcnow().timestamp() + (hours_ahead * 3600)
            predicted = slope * future_time + intercept
            
            return float(predicted)
        
        except:
            return float(np.mean(values))
    
    def analyze_all_model_trends(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Dict[str, Trend]]:
        """
        Analyze trends for all models
        
        Returns: {model_name: {metric_name: Trend}}
        """
        
        from backend.model_categorization import MODEL_REGISTRY
        
        results = {}
        
        # Metrics to analyze per model
        metrics_to_analyze = [
            'model.perplexity',
            'model.entropy',
            'model.latency_ms',
            'model.health_score'
        ]
        
        for model_name in MODEL_REGISTRY.keys():
            model_trends = {}
            
            for metric in metrics_to_analyze:
                trend = self.analyze_trend(
                    metric,
                    time_window_hours,
                    tags={'model': model_name}
                )
                
                if trend:
                    model_trends[metric] = trend
            
            if model_trends:
                results[model_name] = model_trends
        
        return results
    
    def get_stats(self) -> Dict:
        """Get analyzer statistics"""
        
        return {
            'trends_analyzed': self.trends_analyzed,
            'alerts_triggered': self.alerts_triggered
        }


# Global analyzer
trend_analyzer = TrendAnalyzer()
