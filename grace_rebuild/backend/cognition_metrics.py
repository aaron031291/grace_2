"""
Cognition Metrics System
Tracks Grace's cognitive health, trust, and confidence across all 10 domains
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import deque
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func

@dataclass
class DomainMetrics:
    """Metrics for a single domain"""
    domain_id: str
    health: float  # 0.0 to 1.0
    trust: float   # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    kpis: Dict[str, Any]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data


@dataclass
class BenchmarkWindow:
    """Rolling window for tracking 90% benchmark achievement"""
    metric_name: str
    values: deque
    window_days: int
    threshold: float
    
    def add_value(self, value: float, timestamp: datetime):
        """Add a new value to the window"""
        self.values.append((timestamp, value))
        
        cutoff = datetime.now() - timedelta(days=self.window_days)
        while self.values and self.values[0][0] < cutoff:
            self.values.popleft()
    
    def is_sustained(self) -> bool:
        """Check if threshold is sustained over the window"""
        if not self.values:
            return False
        
        return all(value >= self.threshold for _, value in self.values)
    
    def average(self) -> float:
        """Get average value in window"""
        if not self.values:
            return 0.0
        return sum(v for _, v in self.values) / len(self.values)


class CognitionMetricsEngine:
    """Central engine for tracking Grace's cognition across all domains"""
    
    def __init__(self, db: Session):
        self.db = db
        self.domains: Dict[str, DomainMetrics] = {}
        
        self.benchmarks = {
            "overall_health": BenchmarkWindow("overall_health", deque(), window_days=7, threshold=0.90),
            "overall_trust": BenchmarkWindow("overall_trust", deque(), window_days=7, threshold=0.90),
            "overall_confidence": BenchmarkWindow("overall_confidence", deque(), window_days=7, threshold=0.90)
        }
        
        self._initialize_domains()
    
    def _initialize_domains(self):
        """Initialize all 10 domains with default metrics"""
        
        domain_configs = {
            "core": {
                "kpis": {"uptime": 0.95, "governance_score": 0.85, "healing_actions": 12}
            },
            "transcendence": {
                "kpis": {"task_success": 0.88, "code_quality": 0.82, "memory_recall": 0.79}
            },
            "knowledge": {
                "kpis": {"trust_score": 0.87, "ingestion_rate": 145, "recall_accuracy": 0.91}
            },
            "security": {
                "kpis": {"threats_detected": 3, "scan_coverage": 0.94, "response_time": 0.015}
            },
            "ml": {
                "kpis": {"model_accuracy": 0.89, "deployment_success": 0.92, "inference_latency": 0.032}
            },
            "temporal": {
                "kpis": {"prediction_accuracy": 0.84, "graph_completeness": 0.78, "sim_quality": 0.81}
            },
            "parliament": {
                "kpis": {"vote_participation": 0.93, "recommendation_adoption": 0.76, "compliance_score": 0.96}
            },
            "federation": {
                "kpis": {"connector_health": 0.88, "api_success": 0.95, "secret_rotation": 0.99}
            }
        }
        
        for domain_id, config in domain_configs.items():
            kpis = config.get("kpis", {})
            
            health = sum(v for v in kpis.values() if isinstance(v, float) and v <= 1.0) / max(1, len([v for v in kpis.values() if isinstance(v, float) and v <= 1.0]))
            
            self.domains[domain_id] = DomainMetrics(
                domain_id=domain_id,
                health=health,
                trust=health * 0.95,
                confidence=health * 0.92,
                kpis=kpis,
                last_updated=datetime.now()
            )
    
    def update_domain(self, domain_id: str, kpis: Dict[str, Any]):
        """Update metrics for a specific domain"""
        
        if domain_id not in self.domains:
            return
        
        domain = self.domains[domain_id]
        domain.kpis.update(kpis)
        
        percentage_kpis = [v for v in domain.kpis.values() if isinstance(v, float) and v <= 1.0]
        if percentage_kpis:
            domain.health = sum(percentage_kpis) / len(percentage_kpis)
            domain.trust = domain.health * 0.95
            domain.confidence = domain.health * 0.92
        
        domain.last_updated = datetime.now()
        
        self._update_benchmarks()
    
    def _update_benchmarks(self):
        """Update rolling benchmark windows"""
        
        overall_health = self.get_overall_health()
        overall_trust = self.get_overall_trust()
        overall_confidence = self.get_overall_confidence()
        
        now = datetime.now()
        self.benchmarks["overall_health"].add_value(overall_health, now)
        self.benchmarks["overall_trust"].add_value(overall_trust, now)
        self.benchmarks["overall_confidence"].add_value(overall_confidence, now)
    
    def get_overall_health(self) -> float:
        """Calculate overall system health"""
        if not self.domains:
            return 0.0
        return sum(d.health for d in self.domains.values()) / len(self.domains)
    
    def get_overall_trust(self) -> float:
        """Calculate overall system trust"""
        if not self.domains:
            return 0.0
        return sum(d.trust for d in self.domains.values()) / len(self.domains)
    
    def get_overall_confidence(self) -> float:
        """Calculate overall system confidence"""
        if not self.domains:
            return 0.0
        return sum(d.confidence for d in self.domains.values()) / len(self.domains)
    
    def is_saas_ready(self) -> bool:
        """Check if all benchmarks are sustained at 90%+"""
        return all(
            benchmark.is_sustained()
            for benchmark in self.benchmarks.values()
        )
    
    def get_readiness_report(self) -> Dict[str, Any]:
        """Generate SaaS readiness report"""
        
        return {
            "ready": self.is_saas_ready(),
            "overall_health": self.get_overall_health(),
            "overall_trust": self.get_overall_trust(),
            "overall_confidence": self.get_overall_confidence(),
            "benchmarks": {
                name: {
                    "sustained": bench.is_sustained(),
                    "average": bench.average(),
                    "threshold": bench.threshold,
                    "window_days": bench.window_days,
                    "sample_count": len(bench.values)
                }
                for name, bench in self.benchmarks.items()
            },
            "domains": {
                domain_id: {
                    "health": domain.health,
                    "trust": domain.trust,
                    "confidence": domain.confidence,
                    "last_updated": domain.last_updated.isoformat()
                }
                for domain_id, domain in self.domains.items()
            },
            "next_steps": self._generate_next_steps()
        }
    
    def _generate_next_steps(self) -> List[str]:
        """Generate recommendations for SaaS readiness"""
        
        steps = []
        
        if not self.is_saas_ready():
            for name, bench in self.benchmarks.items():
                if not bench.is_sustained():
                    avg = bench.average()
                    gap = (bench.threshold - avg) * 100
                    steps.append(f"Improve {name} by {gap:.1f}% to reach {bench.threshold:.0%} threshold")
        
        weak_domains = [(d_id, d) for d_id, d in self.domains.items() if d.health < 0.9]
        for domain_id, domain in weak_domains:
            steps.append(f"Strengthen {domain_id} domain (currently {domain.health:.1%})")
        
        if self.is_saas_ready():
            steps.extend([
                "Implement multi-tenant authentication",
                "Set up billing infrastructure",
                "Create deployment automation",
                "Build support playbooks",
                "Launch beta program"
            ])
        
        return steps
    
    def get_status(self) -> Dict[str, Any]:
        """Get current cognition status for all domains"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": self.get_overall_health(),
            "overall_trust": self.get_overall_trust(),
            "overall_confidence": self.get_overall_confidence(),
            "saas_ready": self.is_saas_ready(),
            "domains": {
                domain_id: domain.to_dict()
                for domain_id, domain in self.domains.items()
            }
        }


_global_metrics_engine: Optional[CognitionMetricsEngine] = None


def get_metrics_engine(db: Session) -> CognitionMetricsEngine:
    """Get or create the global metrics engine"""
    global _global_metrics_engine
    
    if _global_metrics_engine is None:
        _global_metrics_engine = CognitionMetricsEngine(db)
    
    return _global_metrics_engine
