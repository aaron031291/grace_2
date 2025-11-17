"""
Metric Publishers for All Domains
Integration hooks that publish KPIs from existing systems
"""

import logging

try:
    from backend.metrics_service import publish_metric, publish_batch
except ImportError:
    from metrics_service import publish_metric, publish_batch

logger = logging.getLogger(__name__)


class OrchestratorMetrics:
    """Publishes metrics from agentic orchestrator"""
    
    @staticmethod
    async def publish_plan_created(plan_quality: float = 0.88):
        """Publish when orchestrator creates a plan"""
        await publish_metric("transcendence", "planning_accuracy", plan_quality)
    
    @staticmethod
    async def publish_task_completed(success: bool, quality: float = 0.85):
        """Publish when orchestrator completes a task"""
        await publish_batch("transcendence", {
            "task_success": 1.0 if success else 0.0,
            "code_quality": quality if success else 0.0
        })
    
    @staticmethod
    async def publish_subagent_result(agent_type: str, success: bool):
        """Publish subagent execution result"""
        await publish_metric("transcendence", f"{agent_type}_success", 1.0 if success else 0.0)


class HunterMetrics:
    """Publishes metrics from Hunter security system"""
    
    @staticmethod
    async def publish_scan_completed(threats_found: int, coverage: float, scan_time: float):
        """Publish when security scan completes"""
        await publish_batch("security", {
            "threats_detected": float(threats_found),
            "scan_coverage": coverage,
            "response_time": scan_time
        })
    
    @staticmethod
    async def publish_threat_quarantined(auto_fixed: bool = False):
        """Publish when threat is quarantined"""
        if auto_fixed:
            await publish_metric("security", "auto_fix_success", 1.0)
    
    @staticmethod
    async def publish_false_positive(is_false_positive: bool):
        """Publish false positive detection"""
        await publish_metric("security", "false_positive_rate", 1.0 if is_false_positive else 0.0)


class KnowledgeMetrics:
    """Publishes metrics from knowledge ingestion system"""
    
    @staticmethod
    async def publish_ingestion_completed(trust_score: float, source_count: int):
        """Publish when knowledge ingestion completes"""
        await publish_batch("knowledge", {
            "trust_score": trust_score,
            "ingestion_rate": float(source_count)
        })
    
    @staticmethod
    async def publish_search_performed(recall_accuracy: float, result_count: int):
        """Publish when knowledge search is performed"""
        await publish_batch("knowledge", {
            "recall_accuracy": recall_accuracy,
            "source_diversity": min(1.0, result_count / 10.0)
        })
    
    @staticmethod
    async def publish_knowledge_freshness(avg_age_days: float):
        """Publish knowledge freshness metric"""
        # Convert age to freshness score (newer = better)
        freshness = max(0.0, 1.0 - (avg_age_days / 365.0))
        await publish_metric("knowledge", "knowledge_freshness", freshness)


class MLMetrics:
    """Publishes metrics from ML training and deployment"""
    
    @staticmethod
    async def publish_training_completed(accuracy: float, training_time: float):
        """Publish when model training completes"""
        efficiency = 1.0 / max(1.0, training_time / 3600.0)  # Inverse of hours
        await publish_batch("ml", {
            "model_accuracy": accuracy,
            "training_efficiency": min(1.0, efficiency)
        })
    
    @staticmethod
    async def publish_deployment_completed(success: bool, latency: float = 0.032):
        """Publish when model deployment completes"""
        await publish_batch("ml", {
            "deployment_success": 1.0 if success else 0.0,
            "inference_latency": latency
        })
    
    @staticmethod
    async def publish_auto_retrain_triggered():
        """Publish when auto-retrain is triggered"""
        await publish_metric("ml", "auto_retrain_triggers", 1.0)


class TemporalMetrics:
    """Publishes metrics from temporal/causal systems"""
    
    @staticmethod
    async def publish_prediction_made(accuracy: float):
        """Publish temporal prediction accuracy"""
        await publish_metric("temporal", "prediction_accuracy", accuracy)
    
    @staticmethod
    async def publish_causal_graph_updated(completeness: float):
        """Publish causal graph completeness"""
        await publish_metric("temporal", "graph_completeness", completeness)
    
    @staticmethod
    async def publish_simulation_completed(quality: float, event_latency: float):
        """Publish simulation results"""
        await publish_batch("temporal", {
            "sim_quality": quality,
            "event_latency": event_latency
        })
    
    @staticmethod
    async def publish_impact_analysis(precision: float):
        """Publish impact analysis precision"""
        await publish_metric("temporal", "impact_precision", precision)


class ParliamentMetrics:
    """Publishes metrics from Parliament and meta-loop"""
    
    @staticmethod
    async def publish_vote_completed(participation_rate: float):
        """Publish when vote completes"""
        await publish_metric("parliament", "vote_participation", participation_rate)
    
    @staticmethod
    async def publish_recommendation_adopted(adopted: bool):
        """Publish when meta-loop recommendation is adopted"""
        await publish_metric("parliament", "recommendation_adoption", 1.0 if adopted else 0.0)
    
    @staticmethod
    async def publish_compliance_check(score: float):
        """Publish compliance check result"""
        await publish_metric("parliament", "compliance_score", score)
    
    @staticmethod
    async def publish_reflection_quality(quality: float):
        """Publish reflection quality score"""
        await publish_metric("parliament", "reflection_quality", quality)
    
    @staticmethod
    async def publish_meta_convergence(convergence: float):
        """Publish meta-loop convergence rate"""
        await publish_metric("parliament", "meta_convergence", convergence)


class FederationMetrics:
    """Publishes metrics from federation/external systems"""
    
    @staticmethod
    async def publish_connector_health(connector: str, health: float):
        """Publish connector health status"""
        await publish_metric("federation", "connector_health", health, {"connector": connector})
    
    @staticmethod
    async def publish_api_call(success: bool, connector: str):
        """Publish API call result"""
        await publish_metric("federation", "api_success", 1.0 if success else 0.0, {"connector": connector})
    
    @staticmethod
    async def publish_secret_rotation(compliant: bool):
        """Publish secret rotation compliance"""
        await publish_metric("federation", "secret_rotation", 1.0 if compliant else 0.0)
    
    @staticmethod
    async def publish_plugin_uptime(uptime: float):
        """Publish plugin uptime"""
        await publish_metric("federation", "plugin_uptime", uptime)
    
    @staticmethod
    async def publish_sandbox_isolation(score: float):
        """Publish sandbox isolation score"""
        await publish_metric("federation", "sandbox_isolation", score)


class CoreMetrics:
    """Publishes metrics from core platform operations"""
    
    @staticmethod
    async def publish_uptime(uptime: float):
        """Publish platform uptime"""
        await publish_metric("core", "uptime", uptime)
    
    @staticmethod
    async def publish_governance_score(score: float):
        """Publish governance compliance score"""
        await publish_metric("core", "governance_score", score)
    
    @staticmethod
    async def publish_healing_action():
        """Publish when self-healing triggers"""
        await publish_metric("core", "healing_actions", 1.0)
    
    @staticmethod
    async def publish_verification_failure():
        """Publish verification failure"""
        await publish_metric("core", "verification_failures", 1.0)
    
    @staticmethod
    async def publish_event_bus_latency(latency_ms: float):
        """Publish event bus latency"""
        # Convert to 0-1 score (lower latency = better)
        score = max(0.0, 1.0 - (latency_ms / 1000.0))
        await publish_metric("core", "event_bus_latency", score)


class SpeechMetrics:
    """Publishes metrics from speech/voice system"""
    
    @staticmethod
    async def publish_recognition(accuracy: float):
        """Publish speech recognition accuracy"""
        await publish_metric("speech", "recognition_accuracy", accuracy)
    
    @staticmethod
    async def publish_synthesis(quality: float):
        """Publish TTS quality"""
        await publish_metric("speech", "synthesis_quality", quality)
    
    @staticmethod
    async def publish_voice_command(success: bool, latency: float):
        """Publish voice command result"""
        await publish_batch("speech", {
            "command_success": 1.0 if success else 0.0,
            "latency": min(1.0, 1.0 - (latency / 5.0))  # 5s = 0 score
        })


# Convenience exports
__all__ = [
    "OrchestratorMetrics",
    "HunterMetrics",
    "KnowledgeMetrics",
    "MLMetrics",
    "TemporalMetrics",
    "ParliamentMetrics",
    "FederationMetrics",
    "CoreMetrics",
    "SpeechMetrics"
]
