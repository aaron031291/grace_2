"""
Proactive Intelligence - Predict & Prevent Before Incidents Occur

Shifts GRACE from reactive (responding to incidents) to predictive
(preventing incidents before they happen). Uses time-series analysis,
ML models, and pattern recognition to forecast anomalies, predict
capacity needs, and identify at-risk systems.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics
import math

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class PredictionConfidence(Enum):
    VERY_LOW = 0.0
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


class RiskLevel(Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    LATENCY_SPIKE = "latency_spike"
    ERROR_RATE_INCREASE = "error_rate_increase"
    CAPACITY_SATURATION = "capacity_saturation"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TRAFFIC_ANOMALY = "traffic_anomaly"


@dataclass
class TimeSeriesPoint:
    """Single point in time series"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyForecast:
    """Predicted anomaly before it occurs"""
    forecast_id: str
    node_id: str
    anomaly_type: AnomalyType
    predicted_time: datetime
    confidence: float
    severity: RiskLevel
    contributing_factors: List[str]
    recommended_action: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    prevented: bool = False


@dataclass
class CapacityPrediction:
    """Predicted capacity needs"""
    prediction_id: str
    resource_type: str
    current_capacity: float
    predicted_demand: float
    predicted_time: datetime
    shortfall: float
    confidence: float
    triggering_events: List[str]
    recommended_scaling: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemRiskAssessment:
    """Risk assessment for a system component"""
    assessment_id: str
    node_id: str
    risk_level: RiskLevel
    risk_score: float
    risk_factors: Dict[str, float]
    time_to_failure_estimate: Optional[float]
    recommended_maintenance: List[str]
    assessed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftSignal:
    """Early signal of system drift"""
    signal_id: str
    node_id: str
    metric: str
    baseline: float
    current: float
    drift_percentage: float
    drift_velocity: float
    estimated_critical_time: Optional[datetime]
    detected_at: datetime = field(default_factory=datetime.utcnow)


class TimeSeriesAnalyzer:
    """Analyzes time series data for patterns and predictions"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_point(self, series_id: str, point: TimeSeriesPoint):
        """Add data point to time series"""
        self.time_series[series_id].append(point)
    
    async def forecast_next_value(
        self,
        series_id: str,
        horizon_minutes: int = 30
    ) -> Tuple[float, float]:
        """Forecast future value using exponential smoothing"""
        
        if series_id not in self.time_series or len(self.time_series[series_id]) < 10:
            return 0.0, 0.0
        
        series = list(self.time_series[series_id])
        values = [p.value for p in series]
        
        forecast, confidence = await self._exponential_smoothing(values, horizon_minutes)
        
        return forecast, confidence
    
    async def _exponential_smoothing(
        self,
        values: List[float],
        horizon: int
    ) -> Tuple[float, float]:
        """Simple exponential smoothing forecast"""
        
        if not values:
            return 0.0, 0.0
        
        alpha = 0.3
        
        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        
        recent_variance = statistics.variance(values[-20:]) if len(values) >= 20 else 0.0
        confidence = max(0.0, 1.0 - (recent_variance / (smoothed + 1e-6)))
        
        forecast = smoothed
        
        return forecast, confidence
    
    async def detect_trend(self, series_id: str) -> Tuple[str, float]:
        """Detect trend direction and strength"""
        
        if series_id not in self.time_series or len(self.time_series[series_id]) < 20:
            return "stable", 0.0
        
        series = list(self.time_series[series_id])
        values = [p.value for p in series[-20:]]
        
        first_half = sum(values[:10]) / 10
        second_half = sum(values[10:]) / 10
        
        change = (second_half - first_half) / (first_half + 1e-6)
        
        if abs(change) < 0.05:
            return "stable", abs(change)
        elif change > 0:
            return "increasing", abs(change)
        else:
            return "decreasing", abs(change)
    
    async def calculate_volatility(self, series_id: str) -> float:
        """Calculate recent volatility"""
        
        if series_id not in self.time_series or len(self.time_series[series_id]) < 10:
            return 0.0
        
        series = list(self.time_series[series_id])
        values = [p.value for p in series[-20:]]
        
        if len(values) < 2:
            return 0.0
        
        mean = statistics.mean(values)
        variance = statistics.variance(values)
        
        return math.sqrt(variance) / (mean + 1e-6)
    
    async def detect_seasonality(self, series_id: str, period: int = 24) -> bool:
        """Detect if time series has seasonal pattern"""
        
        if series_id not in self.time_series or len(self.time_series[series_id]) < period * 3:
            return False
        
        series = list(self.time_series[series_id])
        values = [p.value for p in series]
        
        if len(values) < period * 3:
            return False
        
        period_1 = values[-period*3:-period*2]
        period_2 = values[-period*2:-period]
        period_3 = values[-period:]
        
        corr_12 = await self._correlation(period_1, period_2)
        corr_23 = await self._correlation(period_2, period_3)
        
        return (corr_12 > 0.7 and corr_23 > 0.7)
    
    async def _correlation(self, series1: List[float], series2: List[float]) -> float:
        """Calculate correlation between two series"""
        
        if len(series1) != len(series2) or len(series1) < 2:
            return 0.0
        
        mean1 = statistics.mean(series1)
        mean2 = statistics.mean(series2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(series1, series2))
        
        std1 = statistics.stdev(series1)
        std2 = statistics.stdev(series2)
        
        denominator = std1 * std2 * len(series1)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


class AnomalyForecaster:
    """Forecasts anomalies before they occur"""
    
    def __init__(self, ts_analyzer: TimeSeriesAnalyzer):
        self.ts_analyzer = ts_analyzer
        self.anomaly_patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.forecasts: List[AnomalyForecast] = []
        self.thresholds = {
            "latency_p95": 500,
            "error_rate": 0.01,
            "cpu_utilization": 80,
            "memory_utilization": 85,
            "disk_utilization": 90
        }
    
    async def forecast_anomalies(
        self,
        node_id: str,
        metrics: Dict[str, str]
    ) -> List[AnomalyForecast]:
        """Forecast anomalies for a node"""
        
        forecasts = []
        
        for metric_name, series_id in metrics.items():
            forecast_value, confidence = await self.ts_analyzer.forecast_next_value(
                series_id, horizon_minutes=30
            )
            
            trend, trend_strength = await self.ts_analyzer.detect_trend(series_id)
            volatility = await self.ts_analyzer.calculate_volatility(series_id)
            
            if await self._is_anomalous(metric_name, forecast_value, trend, trend_strength, volatility):
                anomaly = await self._create_anomaly_forecast(
                    node_id, metric_name, forecast_value, confidence, trend, trend_strength
                )
                forecasts.append(anomaly)
        
        self.forecasts.extend(forecasts)
        return forecasts
    
    async def _is_anomalous(
        self,
        metric: str,
        forecast: float,
        trend: str,
        trend_strength: float,
        volatility: float
    ) -> bool:
        """Check if forecast indicates anomaly"""
        
        threshold = self.thresholds.get(metric, float('inf'))
        
        if forecast > threshold:
            return True
        
        if trend == "increasing" and trend_strength > 0.15:
            if forecast > threshold * 0.8:
                return True
        
        if volatility > 0.5:
            return True
        
        return False
    
    async def _create_anomaly_forecast(
        self,
        node_id: str,
        metric: str,
        forecast_value: float,
        confidence: float,
        trend: str,
        trend_strength: float
    ) -> AnomalyForecast:
        """Create anomaly forecast"""
        
        anomaly_type = await self._classify_anomaly_type(metric, forecast_value, trend)
        severity = await self._assess_severity(metric, forecast_value, trend_strength)
        factors = [f"{trend} trend ({trend_strength:.1%})", f"forecast: {forecast_value:.2f}"]
        action = await self._recommend_action(anomaly_type, node_id, metric)
        
        forecast = AnomalyForecast(
            forecast_id=f"forecast_{datetime.utcnow().timestamp()}",
            node_id=node_id,
            anomaly_type=anomaly_type,
            predicted_time=datetime.utcnow() + timedelta(minutes=30),
            confidence=confidence,
            severity=severity,
            contributing_factors=factors,
            recommended_action=action
        )
        
        await immutable_log.append(
            actor="proactive_intelligence",
            action="anomaly_forecast",
            resource=forecast.forecast_id,
            subsystem="anomaly_forecaster",
            payload={
                "node_id": node_id,
                "anomaly_type": anomaly_type.value,
                "severity": severity.value,
                "confidence": confidence
            },
            result="forecasted"
        )
        
        return forecast
    
    async def _classify_anomaly_type(self, metric: str, value: float, trend: str) -> AnomalyType:
        """Classify type of anomaly"""
        
        if "latency" in metric:
            return AnomalyType.LATENCY_SPIKE
        elif "error" in metric:
            return AnomalyType.ERROR_RATE_INCREASE
        elif "cpu" in metric or "memory" in metric:
            return AnomalyType.RESOURCE_EXHAUSTION
        elif "capacity" in metric:
            return AnomalyType.CAPACITY_SATURATION
        else:
            return AnomalyType.TRAFFIC_ANOMALY
    
    async def _assess_severity(self, metric: str, value: float, trend_strength: float) -> RiskLevel:
        """Assess severity of predicted anomaly"""
        
        threshold = self.thresholds.get(metric, 100)
        overage = (value - threshold) / threshold if threshold > 0 else 0
        
        combined_score = overage + trend_strength
        
        if combined_score > 0.5:
            return RiskLevel.CRITICAL
        elif combined_score > 0.3:
            return RiskLevel.HIGH
        elif combined_score > 0.15:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    async def _recommend_action(self, anomaly_type: AnomalyType, node_id: str, metric: str) -> str:
        """Recommend preventive action"""
        
        actions = {
            AnomalyType.LATENCY_SPIKE: f"Pre-emptively scale {node_id} capacity",
            AnomalyType.ERROR_RATE_INCREASE: f"Increase health check frequency for {node_id}",
            AnomalyType.CAPACITY_SATURATION: f"Add capacity to {node_id} before saturation",
            AnomalyType.RESOURCE_EXHAUSTION: f"Scale resources for {node_id}",
            AnomalyType.TRAFFIC_ANOMALY: f"Prepare rate limiting for {node_id}"
        }
        
        return actions.get(anomaly_type, f"Monitor {node_id} closely")


class CapacityPredictor:
    """Predicts capacity needs before demand arrives"""
    
    def __init__(self, ts_analyzer: TimeSeriesAnalyzer):
        self.ts_analyzer = ts_analyzer
        self.capacity_models: Dict[str, Dict] = {}
        self.predictions: List[CapacityPrediction] = []
        self.known_events: List[Dict] = []
    
    async def predict_capacity_needs(
        self,
        resource_type: str,
        current_capacity: float,
        demand_series_id: str
    ) -> Optional[CapacityPrediction]:
        """Predict future capacity needs"""
        
        forecast_demand, confidence = await self.ts_analyzer.forecast_next_value(
            demand_series_id, horizon_minutes=60
        )
        
        trend, trend_strength = await self.ts_analyzer.detect_trend(demand_series_id)
        
        has_seasonality = await self.ts_analyzer.detect_seasonality(demand_series_id)
        
        if has_seasonality:
            forecast_demand *= 1.2
        
        if trend == "increasing" and trend_strength > 0.1:
            forecast_demand *= (1 + trend_strength)
        
        known_event_multiplier = await self._check_known_events()
        forecast_demand *= known_event_multiplier
        
        shortfall = forecast_demand - current_capacity
        
        if shortfall > current_capacity * 0.1:
            prediction = CapacityPrediction(
                prediction_id=f"capacity_{datetime.utcnow().timestamp()}",
                resource_type=resource_type,
                current_capacity=current_capacity,
                predicted_demand=forecast_demand,
                predicted_time=datetime.utcnow() + timedelta(minutes=60),
                shortfall=shortfall,
                confidence=confidence,
                triggering_events=await self._get_triggering_events(),
                recommended_scaling=await self._calculate_scaling(current_capacity, forecast_demand)
            )
            
            self.predictions.append(prediction)
            
            await immutable_log.append(
                actor="proactive_intelligence",
                action="capacity_prediction",
                resource=prediction.prediction_id,
                subsystem="capacity_predictor",
                payload={
                    "resource_type": resource_type,
                    "shortfall": shortfall,
                    "confidence": confidence
                },
                result="predicted"
            )
            
            return prediction
        
        return None
    
    async def register_known_event(
        self,
        event_name: str,
        event_time: datetime,
        expected_load_multiplier: float
    ):
        """Register known event that will affect capacity"""
        self.known_events.append({
            "name": event_name,
            "time": event_time,
            "multiplier": expected_load_multiplier
        })
    
    async def _check_known_events(self) -> float:
        """Check if any known events are approaching"""
        
        now = datetime.utcnow()
        upcoming = [
            e for e in self.known_events
            if e["time"] > now and (e["time"] - now) < timedelta(hours=2)
        ]
        
        if upcoming:
            return max(e["multiplier"] for e in upcoming)
        
        return 1.0
    
    async def _get_triggering_events(self) -> List[str]:
        """Get events triggering capacity need"""
        
        now = datetime.utcnow()
        upcoming = [
            e["name"] for e in self.known_events
            if e["time"] > now and (e["time"] - now) < timedelta(hours=2)
        ]
        
        return upcoming
    
    async def _calculate_scaling(
        self,
        current: float,
        needed: float
    ) -> Dict[str, Any]:
        """Calculate recommended scaling parameters"""
        
        scale_factor = needed / current if current > 0 else 2.0
        
        buffer = 1.2
        target_capacity = needed * buffer
        
        return {
            "scale_factor": scale_factor,
            "target_capacity": target_capacity,
            "buffer_percentage": 20,
            "scale_up_by": target_capacity - current
        }


class RiskAssessor:
    """Identifies systems at risk of failure"""
    
    def __init__(self):
        self.risk_models: Dict[str, Dict] = {}
        self.assessments: List[SystemRiskAssessment] = []
    
    async def assess_system_risk(
        self,
        node_id: str,
        health_metrics: Dict[str, float],
        age_days: float,
        incident_history: List[Dict]
    ) -> SystemRiskAssessment:
        """Assess risk of system failure"""
        
        risk_factors = {}
        
        risk_factors["age_risk"] = await self._calculate_age_risk(age_days)
        risk_factors["health_risk"] = await self._calculate_health_risk(health_metrics)
        risk_factors["incident_risk"] = await self._calculate_incident_risk(incident_history)
        risk_factors["dependency_risk"] = await self._calculate_dependency_risk(node_id)
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        risk_level = await self._classify_risk_level(overall_risk)
        
        time_to_failure = await self._estimate_time_to_failure(overall_risk, incident_history)
        
        maintenance = await self._recommend_maintenance(risk_factors, risk_level)
        
        assessment = SystemRiskAssessment(
            assessment_id=f"risk_{datetime.utcnow().timestamp()}",
            node_id=node_id,
            risk_level=risk_level,
            risk_score=overall_risk,
            risk_factors=risk_factors,
            time_to_failure_estimate=time_to_failure,
            recommended_maintenance=maintenance
        )
        
        self.assessments.append(assessment)
        
        await immutable_log.append(
            actor="proactive_intelligence",
            action="risk_assessment",
            resource=assessment.assessment_id,
            subsystem="risk_assessor",
            payload={
                "node_id": node_id,
                "risk_level": risk_level.value,
                "risk_score": overall_risk
            },
            result="assessed"
        )
        
        return assessment
    
    async def _calculate_age_risk(self, age_days: float) -> float:
        """Calculate risk based on system age"""
        
        if age_days < 30:
            return 0.1
        elif age_days < 90:
            return 0.2
        elif age_days < 180:
            return 0.4
        elif age_days < 365:
            return 0.6
        else:
            return 0.8
    
    async def _calculate_health_risk(self, metrics: Dict[str, float]) -> float:
        """Calculate risk based on health metrics"""
        
        unhealthy_count = 0
        total = len(metrics)
        
        for metric, value in metrics.items():
            if "error" in metric and value > 0.01:
                unhealthy_count += 1
            elif "latency" in metric and value > 1000:
                unhealthy_count += 1
            elif "cpu" in metric and value > 80:
                unhealthy_count += 1
        
        return unhealthy_count / total if total > 0 else 0.0
    
    async def _calculate_incident_risk(self, incidents: List[Dict]) -> float:
        """Calculate risk based on incident history"""
        
        recent_incidents = [
            i for i in incidents
            if (datetime.utcnow() - i.get("timestamp", datetime.min)) < timedelta(days=30)
        ]
        
        if len(recent_incidents) >= 5:
            return 0.9
        elif len(recent_incidents) >= 3:
            return 0.6
        elif len(recent_incidents) >= 1:
            return 0.3
        else:
            return 0.1
    
    async def _calculate_dependency_risk(self, node_id: str) -> float:
        """Calculate risk from dependencies"""
        return 0.3
    
    async def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify overall risk level"""
        
        if risk_score > 0.7:
            return RiskLevel.CRITICAL
        elif risk_score > 0.5:
            return RiskLevel.HIGH
        elif risk_score > 0.3:
            return RiskLevel.MODERATE
        elif risk_score > 0.15:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    async def _estimate_time_to_failure(
        self,
        risk_score: float,
        incidents: List[Dict]
    ) -> Optional[float]:
        """Estimate time to failure in hours"""
        
        if risk_score < 0.3:
            return None
        
        if risk_score > 0.7:
            return 24.0
        elif risk_score > 0.5:
            return 72.0
        else:
            return 168.0
    
    async def _recommend_maintenance(
        self,
        risk_factors: Dict[str, float],
        risk_level: RiskLevel
    ) -> List[str]:
        """Recommend maintenance actions"""
        
        recommendations = []
        
        if risk_factors.get("age_risk", 0) > 0.5:
            recommendations.append("Schedule system upgrade/refresh")
        
        if risk_factors.get("health_risk", 0) > 0.4:
            recommendations.append("Investigate health metrics degradation")
        
        if risk_factors.get("incident_risk", 0) > 0.5:
            recommendations.append("Review and address recurring incidents")
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Consider preemptive replacement or failover")
        
        return recommendations


class DriftDetector:
    """Detects early drift before it becomes critical"""
    
    def __init__(self, ts_analyzer: TimeSeriesAnalyzer):
        self.ts_analyzer = ts_analyzer
        self.baselines: Dict[str, float] = {}
        self.drift_signals: List[DriftSignal] = []
    
    async def establish_baseline(self, metric_id: str, baseline_value: float):
        """Establish baseline for metric"""
        self.baselines[metric_id] = baseline_value
    
    async def detect_drift(
        self,
        node_id: str,
        metric_id: str,
        current_value: float
    ) -> Optional[DriftSignal]:
        """Detect drift from baseline"""
        
        if metric_id not in self.baselines:
            await self.establish_baseline(metric_id, current_value)
            return None
        
        baseline = self.baselines[metric_id]
        
        drift_pct = ((current_value - baseline) / baseline * 100) if baseline != 0 else 0
        
        trend, trend_strength = await self.ts_analyzer.detect_trend(metric_id)
        drift_velocity = trend_strength
        
        if abs(drift_pct) > 10:
            critical_time = await self._estimate_critical_time(
                drift_pct, drift_velocity
            )
            
            signal = DriftSignal(
                signal_id=f"drift_{datetime.utcnow().timestamp()}",
                node_id=node_id,
                metric=metric_id,
                baseline=baseline,
                current=current_value,
                drift_percentage=drift_pct,
                drift_velocity=drift_velocity,
                estimated_critical_time=critical_time
            )
            
            self.drift_signals.append(signal)
            
            await immutable_log.append(
                actor="proactive_intelligence",
                action="drift_detected",
                resource=signal.signal_id,
                subsystem="drift_detector",
                payload={
                    "node_id": node_id,
                    "drift_percentage": drift_pct,
                    "drift_velocity": drift_velocity
                },
                result="detected"
            )
            
            return signal
        
        return None
    
    async def _estimate_critical_time(
        self,
        drift_pct: float,
        velocity: float
    ) -> Optional[datetime]:
        """Estimate when drift becomes critical"""
        
        critical_threshold = 50.0
        
        if velocity <= 0:
            return None
        
        remaining_drift = critical_threshold - abs(drift_pct)
        
        if remaining_drift <= 0:
            return datetime.utcnow()
        
        hours_to_critical = remaining_drift / (velocity * 100)
        
        return datetime.utcnow() + timedelta(hours=hours_to_critical)


class ProactiveIntelligence:
    """
    Main proactive intelligence coordinator.
    
    Shifts GRACE from reactive (responding to incidents) to predictive
    (preventing incidents before they occur).
    """
    
    def __init__(self):
        self.ts_analyzer = TimeSeriesAnalyzer(window_size=200)
        self.anomaly_forecaster = AnomalyForecaster(self.ts_analyzer)
        self.capacity_predictor = CapacityPredictor(self.ts_analyzer)
        self.risk_assessor = RiskAssessor()
        self.drift_detector = DriftDetector(self.ts_analyzer)
        self.running = False
        self.prediction_interval_seconds = 180
    
    async def start(self):
        """Start proactive intelligence"""
        
        await trigger_mesh.subscribe("metrics.*", self._handle_metric_event)
        await trigger_mesh.subscribe("health.*", self._handle_health_event)
        
        asyncio.create_task(self._prediction_loop())
        
        self.running = True
        print("✓ Proactive Intelligence started - GRACE now predicts & prevents")
    
    async def stop(self):
        """Stop proactive intelligence"""
        self.running = False
    
    async def _prediction_loop(self):
        """Main prediction loop"""
        
        while self.running:
            try:
                print(f"\n[Proactive Intelligence] Running prediction cycle at {datetime.utcnow().strftime('%H:%M:%S')}")
                
                await self._run_anomaly_forecasting()
                await self._run_capacity_prediction()
                await self._run_risk_assessment()
                
            except Exception as e:
                print(f"✗ Prediction cycle error: {e}")
            
            await asyncio.sleep(self.prediction_interval_seconds)
    
    async def _run_anomaly_forecasting(self):
        """Run anomaly forecasting"""
        
        node_metrics = {
            "api-service": {
                "latency_p95": "api_latency",
                "error_rate": "api_errors",
                "cpu_utilization": "api_cpu"
            }
        }
        
        total_forecasts = 0
        for node_id, metrics in node_metrics.items():
            forecasts = await self.anomaly_forecaster.forecast_anomalies(node_id, metrics)
            
            for forecast in forecasts:
                if forecast.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    await self._issue_preventive_directive(forecast)
                    total_forecasts += 1
        
        if total_forecasts > 0:
            print(f"  -> Issued {total_forecasts} preventive directives")
    
    async def _run_capacity_prediction(self):
        """Run capacity prediction"""
        
        predictions = []
        
        prediction = await self.capacity_predictor.predict_capacity_needs(
            resource_type="api_instances",
            current_capacity=10.0,
            demand_series_id="api_demand"
        )
        
        if prediction:
            predictions.append(prediction)
            await self._issue_capacity_directive(prediction)
        
        if predictions:
            print(f"  -> Predicted {len(predictions)} capacity needs")
    
    async def _run_risk_assessment(self):
        """Run risk assessment"""
        
        systems_to_assess = [
            {"node_id": "legacy-service", "age_days": 400, "incidents": []},
            {"node_id": "database-primary", "age_days": 200, "incidents": []}
        ]
        
        high_risk_count = 0
        for system in systems_to_assess:
            assessment = await self.risk_assessor.assess_system_risk(
                node_id=system["node_id"],
                health_metrics={},
                age_days=system["age_days"],
                incident_history=system["incidents"]
            )
            
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._issue_maintenance_directive(assessment)
                high_risk_count += 1
        
        if high_risk_count > 0:
            print(f"  -> Identified {high_risk_count} high-risk systems")
    
    async def _handle_metric_event(self, event: TriggerEvent):
        """Handle metric events for time series analysis"""
        
        if "value" in event.payload:
            point = TimeSeriesPoint(
                timestamp=event.timestamp,
                value=event.payload["value"],
                metadata=event.payload
            )
            
            series_id = f"{event.resource}_{event.payload.get('metric', 'unknown')}"
            self.ts_analyzer.add_point(series_id, point)
            
            if event.resource:
                drift = await self.drift_detector.detect_drift(
                    node_id=event.resource,
                    metric_id=series_id,
                    current_value=event.payload["value"]
                )
                
                if drift and abs(drift.drift_percentage) > 20:
                    await self._issue_drift_directive(drift)
    
    async def _handle_health_event(self, event: TriggerEvent):
        """Handle health events"""
        pass
    
    async def _issue_preventive_directive(self, forecast: AnomalyForecast):
        """Issue preventive directive based on forecast"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="proactive.preventive_action",
            source="proactive_intelligence",
            actor="proactive_intelligence",
            resource=forecast.node_id,
            payload={
                "forecast_id": forecast.forecast_id,
                "anomaly_type": forecast.anomaly_type.value,
                "severity": forecast.severity.value,
                "action": forecast.recommended_action,
                "confidence": forecast.confidence,
                "time_to_anomaly_minutes": 30
            },
            timestamp=datetime.utcnow()
        ))
        
        print(f"  ⚠️  Preventive action: {forecast.recommended_action}")
    
    async def _issue_capacity_directive(self, prediction: CapacityPrediction):
        """Issue capacity scaling directive"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="proactive.capacity_scaling",
            source="proactive_intelligence",
            actor="proactive_intelligence",
            resource=prediction.resource_type,
            payload={
                "prediction_id": prediction.prediction_id,
                "shortfall": prediction.shortfall,
                "recommended_scaling": prediction.recommended_scaling,
                "confidence": prediction.confidence,
                "time_to_shortage_minutes": 60
            },
            timestamp=datetime.utcnow()
        ))
        
        print(f"  📈 Capacity directive: Scale {prediction.resource_type} by {prediction.recommended_scaling['scale_factor']:.1f}x")
    
    async def _issue_maintenance_directive(self, assessment: SystemRiskAssessment):
        """Issue maintenance directive for at-risk system"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="proactive.maintenance_required",
            source="proactive_intelligence",
            actor="proactive_intelligence",
            resource=assessment.node_id,
            payload={
                "assessment_id": assessment.assessment_id,
                "risk_level": assessment.risk_level.value,
                "risk_score": assessment.risk_score,
                "time_to_failure_hours": assessment.time_to_failure_estimate,
                "recommended_maintenance": assessment.recommended_maintenance
            },
            timestamp=datetime.utcnow()
        ))
        
        print(f"  🔧 Maintenance required: {assessment.node_id} (risk: {assessment.risk_level.value})")
    
    async def _issue_drift_directive(self, drift: DriftSignal):
        """Issue directive for detected drift"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="proactive.drift_detected",
            source="proactive_intelligence",
            actor="proactive_intelligence",
            resource=drift.node_id,
            payload={
                "signal_id": drift.signal_id,
                "metric": drift.metric,
                "drift_percentage": drift.drift_percentage,
                "estimated_critical_time": drift.estimated_critical_time.isoformat() if drift.estimated_critical_time else None
            },
            timestamp=datetime.utcnow()
        ))
        
        print(f"  📉 Drift detected: {drift.node_id} - {drift.drift_percentage:.1f}% from baseline")


proactive_intelligence = ProactiveIntelligence()
