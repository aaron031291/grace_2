"""
Model Health Telemetry System - PRODUCTION
Token-level metrics, execution windows, grey zone detection
"""

import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path
from enum import Enum


class HealthStatus(Enum):
    """Model health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    GREY_ZONE = "grey_zone"  # Approaching hallucination
    CRITICAL = "critical"
    QUARANTINED = "quarantined"


@dataclass
class TokenMetrics:
    """Metrics for a single token generation"""
    token_id: int
    probability: float
    perplexity: float
    entropy: float
    latency_ms: float
    timestamp: float = field(default_factory=time.time)
    
    def is_anomalous(self) -> bool:
        """Check if metrics indicate anomaly"""
        return (
            self.perplexity > 100 or  # High uncertainty
            self.entropy > 5.0 or  # High randomness
            self.latency_ms > 5000  # Slow generation
        )


@dataclass
class ExecutionWindow:
    """Safe execution window for a model"""
    model_name: str
    
    # Token limits
    safe_max_tokens: int  # Safe limit
    grey_zone_tokens: int  # When quality starts degrading
    critical_tokens: int  # Hard limit
    
    # Quality thresholds
    perplexity_threshold: float = 50.0
    entropy_threshold: float = 4.0
    latency_threshold_ms: float = 3000.0
    
    # Cost curve
    tokens_to_quality: Dict[int, float] = field(default_factory=dict)
    
    # Hallucination signature
    hallucination_patterns: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    stress_tests_run: int = 0
    
    def get_status_at_tokens(self, token_count: int) -> HealthStatus:
        """Get health status at given token count"""
        if token_count <= self.safe_max_tokens:
            return HealthStatus.HEALTHY
        elif token_count <= self.grey_zone_tokens:
            return HealthStatus.DEGRADED
        elif token_count <= self.critical_tokens:
            return HealthStatus.GREY_ZONE
        else:
            return HealthStatus.CRITICAL
    
    def to_dict(self) -> Dict:
        return {
            'model_name': self.model_name,
            'safe_max_tokens': self.safe_max_tokens,
            'grey_zone_tokens': self.grey_zone_tokens,
            'critical_tokens': self.critical_tokens,
            'thresholds': {
                'perplexity': self.perplexity_threshold,
                'entropy': self.entropy_threshold,
                'latency_ms': self.latency_threshold_ms
            },
            'quality_curve_points': len(self.tokens_to_quality),
            'hallucination_patterns': self.hallucination_patterns,
            'last_updated': self.last_updated,
            'stress_tests_run': self.stress_tests_run
        }


@dataclass
class ModelHealthSnapshot:
    """Point-in-time health snapshot"""
    model_name: str
    status: HealthStatus
    
    # Current metrics
    current_tokens: int
    avg_perplexity: float
    avg_entropy: float
    avg_latency_ms: float
    
    # Trends (last 100 tokens)
    perplexity_trend: str  # "rising", "stable", "falling"
    entropy_trend: str
    latency_trend: str
    
    # Alerts
    warnings: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    
    # Recommendations
    recommended_action: str = ""
    
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def needs_intervention(self) -> bool:
        """Check if immediate intervention needed"""
        return (
            self.status in [HealthStatus.CRITICAL, HealthStatus.QUARANTINED] or
            len(self.critical_issues) > 0 or
            self.avg_perplexity > 100
        )
    
    def to_dict(self) -> Dict:
        return {
            'model_name': self.model_name,
            'status': self.status.value,
            'metrics': {
                'current_tokens': self.current_tokens,
                'avg_perplexity': self.avg_perplexity,
                'avg_entropy': self.avg_entropy,
                'avg_latency_ms': self.avg_latency_ms
            },
            'trends': {
                'perplexity': self.perplexity_trend,
                'entropy': self.entropy_trend,
                'latency': self.latency_trend
            },
            'warnings': self.warnings,
            'critical_issues': self.critical_issues,
            'recommended_action': self.recommended_action,
            'needs_intervention': self.needs_intervention(),
            'timestamp': self.timestamp
        }


class ModelHealthMonitor:
    """
    Production health monitoring for a single model
    Tracks token-level metrics and detects degradation
    """
    
    def __init__(
        self,
        model_name: str,
        window_size: int = 100,
        storage_path: Optional[str] = None
    ):
        self.model_name = model_name
        self.window_size = window_size
        
        # Storage
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path("databases/model_health") / model_name
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Metrics history (rolling window)
        self.metrics_history: deque = deque(maxlen=window_size)
        
        # Execution window (learned from stress tests)
        self.execution_window: Optional[ExecutionWindow] = None
        
        # Current session
        self.session_tokens = 0
        self.session_start = time.time()
        
        # Health status
        self.current_status = HealthStatus.HEALTHY
        self.quarantined = False
        self.quarantine_reason = ""
        
        # Statistics
        self.total_tokens_generated = 0
        self.anomaly_count = 0
        self.degradation_episodes = 0
        
        # Load existing data
        self._load_execution_window()
    
    def _load_execution_window(self):
        """Load execution window from disk"""
        window_file = self.storage_path / "execution_window.json"
        
        if window_file.exists():
            try:
                with open(window_file, 'r') as f:
                    data = json.load(f)
                    self.execution_window = ExecutionWindow(
                        model_name=data['model_name'],
                        safe_max_tokens=data['safe_max_tokens'],
                        grey_zone_tokens=data['grey_zone_tokens'],
                        critical_tokens=data['critical_tokens'],
                        perplexity_threshold=data['thresholds']['perplexity'],
                        entropy_threshold=data['thresholds']['entropy'],
                        latency_threshold_ms=data['thresholds']['latency_ms'],
                        tokens_to_quality=data.get('tokens_to_quality', {}),
                        hallucination_patterns=data.get('hallucination_patterns', []),
                        last_updated=data.get('last_updated', ''),
                        stress_tests_run=data.get('stress_tests_run', 0)
                    )
                    print(f"[HEALTH-{self.model_name}] Loaded execution window: safe={self.execution_window.safe_max_tokens}")
            except Exception as e:
                print(f"[HEALTH-{self.model_name}] Failed to load window: {e}")
    
    def _save_execution_window(self):
        """Save execution window to disk"""
        if not self.execution_window:
            return
        
        window_file = self.storage_path / "execution_window.json"
        
        try:
            with open(window_file, 'w') as f:
                json.dump(self.execution_window.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[HEALTH-{self.model_name}] Failed to save window: {e}")
    
    def record_token(
        self,
        token_id: int,
        probability: float,
        perplexity: float,
        latency_ms: float
    ):
        """Record metrics for a generated token"""
        
        # Calculate entropy from probability
        entropy = -np.log2(probability) if probability > 0 else 10.0
        
        metrics = TokenMetrics(
            token_id=token_id,
            probability=probability,
            perplexity=perplexity,
            entropy=entropy,
            latency_ms=latency_ms
        )
        
        self.metrics_history.append(metrics)
        self.session_tokens += 1
        self.total_tokens_generated += 1
        
        # Check for anomalies
        if metrics.is_anomalous():
            self.anomaly_count += 1
        
        # Update status
        self._update_health_status()
    
    def _update_health_status(self):
        """Update current health status based on metrics"""
        
        if not self.metrics_history:
            return
        
        # Get recent metrics (last 10 tokens)
        recent = list(self.metrics_history)[-10:]
        
        avg_perplexity = np.mean([m.perplexity for m in recent])
        avg_entropy = np.mean([m.entropy for m in recent])
        avg_latency = np.mean([m.latency_ms for m in recent])
        
        # Check execution window
        if self.execution_window:
            window_status = self.execution_window.get_status_at_tokens(self.session_tokens)
            self.current_status = window_status
        else:
            # Use metric thresholds
            if avg_perplexity > 100 or avg_entropy > 5.0:
                self.current_status = HealthStatus.CRITICAL
            elif avg_perplexity > 50 or avg_entropy > 4.0:
                self.current_status = HealthStatus.GREY_ZONE
            elif avg_perplexity > 30 or avg_entropy > 3.0:
                self.current_status = HealthStatus.DEGRADED
            else:
                self.current_status = HealthStatus.HEALTHY
        
        # Track degradation episodes
        if self.current_status in [HealthStatus.GREY_ZONE, HealthStatus.CRITICAL]:
            self.degradation_episodes += 1
    
    def get_snapshot(self) -> ModelHealthSnapshot:
        """Get current health snapshot"""
        
        if not self.metrics_history:
            return ModelHealthSnapshot(
                model_name=self.model_name,
                status=HealthStatus.HEALTHY,
                current_tokens=0,
                avg_perplexity=0.0,
                avg_entropy=0.0,
                avg_latency_ms=0.0,
                perplexity_trend="stable",
                entropy_trend="stable",
                latency_trend="stable"
            )
        
        recent = list(self.metrics_history)
        
        # Calculate averages
        avg_perplexity = np.mean([m.perplexity for m in recent])
        avg_entropy = np.mean([m.entropy for m in recent])
        avg_latency = np.mean([m.latency_ms for m in recent])
        
        # Calculate trends
        perplexity_trend = self._calculate_trend([m.perplexity for m in recent])
        entropy_trend = self._calculate_trend([m.entropy for m in recent])
        latency_trend = self._calculate_trend([m.latency_ms for m in recent])
        
        # Collect warnings and issues
        warnings = []
        critical_issues = []
        
        if self.current_status == HealthStatus.DEGRADED:
            warnings.append("Model performance degrading")
        elif self.current_status == HealthStatus.GREY_ZONE:
            warnings.append("Entering grey zone - hallucination risk increasing")
        elif self.current_status == HealthStatus.CRITICAL:
            critical_issues.append("Critical degradation - immediate intervention required")
        
        if avg_perplexity > 50:
            warnings.append(f"High perplexity: {avg_perplexity:.2f}")
        
        if avg_entropy > 4.0:
            warnings.append(f"High entropy: {avg_entropy:.2f}")
        
        if self.quarantined:
            critical_issues.append(f"Model quarantined: {self.quarantine_reason}")
        
        # Recommend action
        recommended_action = ""
        if self.current_status == HealthStatus.CRITICAL:
            recommended_action = "Reset context window or switch to backup model"
        elif self.current_status == HealthStatus.GREY_ZONE:
            recommended_action = "Consider context summarization or reduction"
        elif self.current_status == HealthStatus.DEGRADED:
            recommended_action = "Monitor closely, prepare fallback"
        
        return ModelHealthSnapshot(
            model_name=self.model_name,
            status=self.current_status,
            current_tokens=self.session_tokens,
            avg_perplexity=avg_perplexity,
            avg_entropy=avg_entropy,
            avg_latency_ms=avg_latency,
            perplexity_trend=perplexity_trend,
            entropy_trend=entropy_trend,
            latency_trend=latency_trend,
            warnings=warnings,
            critical_issues=critical_issues,
            recommended_action=recommended_action
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "rising"
        elif slope < -0.1:
            return "falling"
        else:
            return "stable"
    
    def quarantine(self, reason: str):
        """Quarantine model (stop using it)"""
        self.quarantined = True
        self.quarantine_reason = reason
        self.current_status = HealthStatus.QUARANTINED
        print(f"[HEALTH-{self.model_name}] QUARANTINED: {reason}")
    
    def reset_session(self):
        """Reset session metrics"""
        self.session_tokens = 0
        self.session_start = time.time()
        self.current_status = HealthStatus.HEALTHY
        print(f"[HEALTH-{self.model_name}] Session reset")
    
    def set_execution_window(self, window: ExecutionWindow):
        """Set execution window from stress test results"""
        self.execution_window = window
        self._save_execution_window()
        print(f"[HEALTH-{self.model_name}] Execution window updated: {window.safe_max_tokens} safe tokens")
    
    def get_stats(self) -> Dict:
        """Get monitor statistics"""
        return {
            'model_name': self.model_name,
            'status': self.current_status.value,
            'quarantined': self.quarantined,
            'session': {
                'tokens': self.session_tokens,
                'duration_seconds': time.time() - self.session_start
            },
            'lifetime': {
                'total_tokens': self.total_tokens_generated,
                'anomalies': self.anomaly_count,
                'degradation_episodes': self.degradation_episodes
            },
            'execution_window': self.execution_window.to_dict() if self.execution_window else None
        }


class ModelHealthRegistry:
    """
    Central registry for all model health monitors
    """
    
    def __init__(self):
        self.monitors: Dict[str, ModelHealthMonitor] = {}
    
    def get_monitor(self, model_name: str) -> ModelHealthMonitor:
        """Get or create monitor for model"""
        if model_name not in self.monitors:
            self.monitors[model_name] = ModelHealthMonitor(model_name)
        return self.monitors[model_name]
    
    def record_token(
        self,
        model_name: str,
        token_id: int,
        probability: float,
        perplexity: float,
        latency_ms: float
    ):
        """Record token for model"""
        monitor = self.get_monitor(model_name)
        monitor.record_token(token_id, probability, perplexity, latency_ms)
    
    def get_snapshot(self, model_name: str) -> ModelHealthSnapshot:
        """Get health snapshot for model"""
        monitor = self.get_monitor(model_name)
        return monitor.get_snapshot()
    
    def get_all_snapshots(self) -> Dict[str, ModelHealthSnapshot]:
        """Get snapshots for all models"""
        return {
            name: monitor.get_snapshot()
            for name, monitor in self.monitors.items()
        }
    
    def get_unhealthy_models(self) -> List[str]:
        """Get list of unhealthy models"""
        unhealthy = []
        
        for name, monitor in self.monitors.items():
            snapshot = monitor.get_snapshot()
            if snapshot.status not in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                unhealthy.append(name)
        
        return unhealthy
    
    def quarantine_model(self, model_name: str, reason: str):
        """Quarantine a model"""
        monitor = self.get_monitor(model_name)
        monitor.quarantine(reason)
    
    def get_stats(self) -> Dict:
        """Get registry-wide statistics"""
        total_monitors = len(self.monitors)
        
        status_counts = {}
        for monitor in self.monitors.values():
            status = monitor.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_models': total_monitors,
            'status_distribution': status_counts,
            'unhealthy_models': self.get_unhealthy_models()
        }


# Global registry
model_health_registry = ModelHealthRegistry()
