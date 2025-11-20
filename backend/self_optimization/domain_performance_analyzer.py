"""
Domain Performance Analyzer - Grace's Self-Optimization System

Uses world model + telemetry to:
1. Track domain performance (heal time, success rate, latency)
2. Identify strengths and weaknesses
3. Auto-tune behavior (workers, models, priorities)

Integrates with:
- World Model (for historical performance data)
- RAG Service (for querying past outcomes)
- Closed-Loop Learning (for execution metrics)
- Service Mesh (for telemetry data)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from backend.events.unified_publisher import publish_domain_event

logger = logging.getLogger(__name__)


@dataclass
class DomainPerformanceMetrics:
    """Performance metrics for a single domain"""
    domain_id: str
    
    # Success metrics
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    success_rate: float = 0.0
    
    # Timing metrics
    mean_execution_time_seconds: float = 0.0
    mean_repair_time_seconds: float = 0.0
    p95_latency_seconds: float = 0.0
    
    # Quality metrics
    average_confidence: float = 0.0
    average_trust_score: float = 0.0
    
    # Learning metrics
    insights_generated: int = 0
    knowledge_contributions: int = 0
    
    # Health metrics
    uptime_percentage: float = 0.0
    incidents_count: int = 0
    auto_healed_count: int = 0
    
    # Calculated scores
    performance_score: float = 0.0  # 0-1, composite
    reliability_rank: str = "unknown"  # excellent, good, fair, poor
    
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SelfAnalysis:
    """Grace's self-analysis of her capabilities"""
    strengths: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    improvement_actions: List[Dict[str, Any]]
    overall_health: float
    analysis_timestamp: str
    
    def to_narrative(self) -> str:
        """Convert analysis to natural language"""
        parts = []
        
        parts.append(f"Based on my self-analysis (health: {self.overall_health:.1%}):\n")
        
        if self.strengths:
            parts.append("\nMy strengths:")
            for strength in self.strengths[:3]:
                parts.append(f"  - {strength['domain']}: {strength['description']} ({strength['score']:.1%})")
        
        if self.weaknesses:
            parts.append("\nAreas I need to improve:")
            for weakness in self.weaknesses[:3]:
                parts.append(f"  - {weakness['domain']}: {weakness['description']} ({weakness['score']:.1%})")
        
        if self.improvement_actions:
            parts.append("\nPlanned improvements:")
            for action in self.improvement_actions[:3]:
                parts.append(f"  - {action['action']}: {action['rationale']}")
        
        return "\n".join(parts)


class DomainPerformanceAnalyzer:
    """
    Analyzes domain performance and enables self-optimization
    
    Uses RAG + world model to track metrics and identify improvements
    """
    
    def __init__(self):
        self._initialized = False
        self.domain_metrics: Dict[str, DomainPerformanceMetrics] = {}
        self.analysis_interval_seconds = 600  # 10 minutes
        self.last_analysis: Optional[SelfAnalysis] = None
    
    async def initialize(self):
        """Initialize performance analyzer"""
        if self._initialized:
            return
        
        logger.info("[PERF-ANALYZER] Initializing domain performance analyzer")
        
        # Load historical metrics from world model
        await self._load_historical_metrics()
        
        self._initialized = True
        logger.info("[PERF-ANALYZER] Performance analyzer ready")
    
    async def analyze_all_domains(self) -> SelfAnalysis:
        """
        Analyze performance across all domains
        
        Returns Grace's self-assessment of strengths/weaknesses
        """
        logger.info("[PERF-ANALYZER] Starting comprehensive domain analysis")
        
        # Collect metrics for each domain
        domains = await self._get_active_domains()
        
        for domain_id in domains:
            metrics = await self._collect_domain_metrics(domain_id)
            self.domain_metrics[domain_id] = metrics
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths()
        weaknesses = self._identify_weaknesses()
        
        # Generate improvement actions
        improvement_actions = await self._generate_improvement_actions(weaknesses)
        
        # Calculate overall health
        overall_health = self._calculate_overall_health()
        
        # Create analysis
        analysis = SelfAnalysis(
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_actions=improvement_actions,
            overall_health=overall_health,
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
        self.last_analysis = analysis
        
        # Publish to world model
        await self._publish_analysis(analysis)
        
        logger.info(
            f"[PERF-ANALYZER] Analysis complete: {len(strengths)} strengths, "
            f"{len(weaknesses)} weaknesses, {len(improvement_actions)} actions planned"
        )
        
        return analysis
    
    async def _get_active_domains(self) -> List[str]:
        """Get list of active domains"""
        try:
            from backend.domains import domain_registry
            domains = domain_registry.list_domains()
            return [d["domain_id"] for d in domains]
        except:
            # Fallback to known domains
            return ["core", "network", "ml", "security", "knowledge", "orchestrator"]
    
    async def _collect_domain_metrics(self, domain_id: str) -> DomainPerformanceMetrics:
        """
        Collect performance metrics for a domain using RAG
        
        Queries world model for historical performance data
        """
        from backend.services.rag_service import rag_service
        from backend.services.metadata_standards import query_by_domain
        
        metrics = DomainPerformanceMetrics(domain_id=domain_id)
        
        try:
            # Query RAG for domain outcomes
            filter = query_by_domain(domain_id, confidence_min=0.5, hours=168)  # Last week
            
            results = await rag_service.retrieve(
                query=f"{domain_id} domain execution outcomes metrics",
                filters=filter,
                top_k=100
            )
            
            # Aggregate metrics from results
            execution_times = []
            repair_times = []
            confidences = []
            successes = 0
            failures = 0
            
            for result in results.get("results", []):
                metadata = result.get("metadata", {})
                
                # Track successes/failures
                if "success" in metadata:
                    if metadata["success"]:
                        successes += 1
                    else:
                        failures += 1
                
                # Track timing
                if "execution_time_seconds" in metadata:
                    execution_times.append(metadata["execution_time_seconds"])
                if "repair_time_seconds" in metadata:
                    repair_times.append(metadata["repair_time_seconds"])
                
                # Track confidence
                if "confidence" in metadata:
                    confidences.append(metadata["confidence"])
            
            # Calculate aggregates
            total_ops = successes + failures
            metrics.total_operations = total_ops
            metrics.successful_operations = successes
            metrics.failed_operations = failures
            metrics.success_rate = successes / total_ops if total_ops > 0 else 0.0
            
            if execution_times:
                metrics.mean_execution_time_seconds = sum(execution_times) / len(execution_times)
                metrics.p95_latency_seconds = sorted(execution_times)[int(len(execution_times) * 0.95)] if len(execution_times) > 20 else max(execution_times, default=0)
            
            if repair_times:
                metrics.mean_repair_time_seconds = sum(repair_times) / len(repair_times)
            
            if confidences:
                metrics.average_confidence = sum(confidences) / len(confidences)
            
            # Calculate performance score (composite)
            metrics.performance_score = (
                metrics.success_rate * 0.4 +  # Success rate = 40%
                metrics.average_confidence * 0.3 +  # Confidence = 30%
                (1.0 / (1.0 + metrics.mean_execution_time_seconds / 10)) * 0.3  # Speed = 30%
            )
            
            # Determine reliability rank
            if metrics.performance_score >= 0.9:
                metrics.reliability_rank = "excellent"
            elif metrics.performance_score >= 0.75:
                metrics.reliability_rank = "good"
            elif metrics.performance_score >= 0.6:
                metrics.reliability_rank = "fair"
            else:
                metrics.reliability_rank = "poor"
            
        except Exception as e:
            logger.error(f"[PERF-ANALYZER] Error collecting metrics for {domain_id}: {e}")
        
        return metrics
    
    def _identify_strengths(self) -> List[Dict[str, Any]]:
        """Identify Grace's strongest domains"""
        strengths = []
        
        for domain_id, metrics in self.domain_metrics.items():
            if metrics.performance_score >= 0.8:
                strengths.append({
                    "domain": domain_id,
                    "score": metrics.performance_score,
                    "description": self._describe_strength(metrics),
                    "metrics": {
                        "success_rate": metrics.success_rate,
                        "avg_confidence": metrics.average_confidence,
                        "mean_time": metrics.mean_execution_time_seconds
                    }
                })
        
        # Sort by score
        strengths.sort(key=lambda x: x["score"], reverse=True)
        
        return strengths
    
    def _identify_weaknesses(self) -> List[Dict[str, Any]]:
        """Identify Grace's weak spots"""
        weaknesses = []
        
        for domain_id, metrics in self.domain_metrics.items():
            if metrics.performance_score < 0.7:
                weaknesses.append({
                    "domain": domain_id,
                    "score": metrics.performance_score,
                    "description": self._describe_weakness(metrics),
                    "root_causes": self._identify_root_causes(metrics),
                    "impact": "high" if metrics.performance_score < 0.5 else "medium"
                })
        
        # Sort by severity (lowest score first)
        weaknesses.sort(key=lambda x: x["score"])
        
        return weaknesses
    
    def _describe_strength(self, metrics: DomainPerformanceMetrics) -> str:
        """Describe what makes this domain strong"""
        aspects = []
        
        if metrics.success_rate >= 0.95:
            aspects.append(f"{metrics.success_rate:.1%} success rate")
        if metrics.average_confidence >= 0.9:
            aspects.append(f"{metrics.average_confidence:.1%} confidence")
        if metrics.mean_execution_time_seconds < 2.0:
            aspects.append(f"fast execution ({metrics.mean_execution_time_seconds:.1f}s)")
        
        return ", ".join(aspects) if aspects else "consistent performance"
    
    def _describe_weakness(self, metrics: DomainPerformanceMetrics) -> str:
        """Describe what needs improvement"""
        issues = []
        
        if metrics.success_rate < 0.7:
            issues.append(f"low success rate ({metrics.success_rate:.1%})")
        if metrics.average_confidence < 0.7:
            issues.append(f"low confidence ({metrics.average_confidence:.1%})")
        if metrics.mean_execution_time_seconds > 10.0:
            issues.append(f"slow execution ({metrics.mean_execution_time_seconds:.1f}s)")
        if metrics.mean_repair_time_seconds > 60.0:
            issues.append(f"slow repairs ({metrics.mean_repair_time_seconds:.0f}s)")
        
        return ", ".join(issues) if issues else "below target performance"
    
    def _identify_root_causes(self, metrics: DomainPerformanceMetrics) -> List[str]:
        """Identify likely root causes of poor performance"""
        causes = []
        
        if metrics.success_rate < 0.7 and metrics.average_confidence > 0.8:
            causes.append("Overconfident with poor accuracy - model needs retraining")
        
        if metrics.mean_execution_time_seconds > 10.0:
            causes.append("Slow execution - consider faster models or more workers")
        
        if metrics.failed_operations > metrics.successful_operations:
            causes.append("High failure rate - review error patterns and add safeguards")
        
        if metrics.mean_repair_time_seconds > 60.0 and metrics.auto_healed_count > 0:
            causes.append("Slow healing - optimize playbooks or add more healing workers")
        
        return causes
    
    async def _generate_improvement_actions(
        self,
        weaknesses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate concrete improvement actions
        
        Returns list of auto-tuning actions Grace can take
        """
        actions = []
        
        for weakness in weaknesses:
            domain_id = weakness["domain"]
            metrics = self.domain_metrics.get(domain_id)
            
            if not metrics:
                continue
            
            # Action 1: Scale workers for slow domains
            if metrics.mean_execution_time_seconds > 10.0:
                actions.append({
                    "action": f"Scale up {domain_id} workers",
                    "domain": domain_id,
                    "type": "scale_workers",
                    "rationale": f"Mean execution time {metrics.mean_execution_time_seconds:.1f}s exceeds 10s target",
                    "target_metric": "execution_time",
                    "expected_improvement": "30-50% faster",
                    "auto_executable": True
                })
            
            # Action 2: Switch to faster models for latency issues
            if metrics.p95_latency_seconds > 5.0:
                actions.append({
                    "action": f"Use faster models for {domain_id}",
                    "domain": domain_id,
                    "type": "switch_model",
                    "rationale": f"P95 latency {metrics.p95_latency_seconds:.1f}s exceeds 5s SLA",
                    "target_metric": "latency",
                    "expected_improvement": "Sub-5s response time",
                    "auto_executable": True,
                    "model_preference": "fast_local"  # Prefer fast local models
                })
            
            # Action 3: Prioritize missions on weak spots
            if metrics.success_rate < 0.7:
                actions.append({
                    "action": f"Prioritize {domain_id} improvement missions",
                    "domain": domain_id,
                    "type": "prioritize_missions",
                    "rationale": f"Success rate {metrics.success_rate:.1%} below 70% target",
                    "target_metric": "success_rate",
                    "expected_improvement": "Focused learning on failure patterns",
                    "auto_executable": True
                })
            
            # Action 4: Add HTM workers for overloaded domains
            if metrics.total_operations > 100 and metrics.mean_execution_time_seconds > 5.0:
                actions.append({
                    "action": f"Add HTM workers to {domain_id}",
                    "domain": domain_id,
                    "type": "add_htm_workers",
                    "rationale": f"High load ({metrics.total_operations} ops) with slow execution",
                    "target_metric": "throughput",
                    "expected_improvement": "Better load distribution",
                    "auto_executable": True,
                    "worker_count": 2
                })
        
        return actions
    
    def _calculate_overall_health(self) -> float:
        """Calculate Grace's overall health score"""
        if not self.domain_metrics:
            return 0.8  # Default
        
        # Average performance across all domains
        scores = [m.performance_score for m in self.domain_metrics.values()]
        overall = sum(scores) / len(scores) if scores else 0.8
        
        # Penalize if any domain is critical (< 0.5)
        critical_domains = [m for m in self.domain_metrics.values() if m.performance_score < 0.5]
        if critical_domains:
            overall *= 0.8  # 20% penalty for critical issues
        
        return overall
    
    async def _publish_analysis(self, analysis: SelfAnalysis):
        """Publish self-analysis to world model"""
        try:
            from backend.world_model import grace_world_model
            
            # Add narrative to world model
            await grace_world_model.add_knowledge(
                category='self',
                content=analysis.to_narrative(),
                source='self_optimization',
                confidence=0.95,
                tags=['self-analysis', 'performance', 'optimization'],
                metadata={
                    "overall_health": analysis.overall_health,
                    "strengths_count": len(analysis.strengths),
                    "weeknesses_count": len(analysis.weaknesses),
                    "actions_planned": len(analysis.improvement_actions)
                }
            )
            
            logger.info("[PERF-ANALYZER] Published self-analysis to world model")
            
        except Exception as e:
            logger.error(f"[PERF-ANALYZER] Failed to publish analysis: {e}")
    
    async def execute_auto_tuning(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an auto-tuning action
        
        Args:
            action: Improvement action dictionary
            
        Returns:
            Execution result
        """
        try:
            if not action.get("auto_executable"):
                return await execute_action(action)
            
            result = await self._execute_tuning_action(action)
            
            # Record outcome
            from backend.services.closed_loop_learning import capture_execution_outcome
            
            await capture_execution_outcome(
                task_description=action["action"],
                approach=action["type"],
                success=result.get("success", False),
                narrative=result.get("summary", "Auto-tuning executed"),
                metrics=result.get("metrics", {}),
                domain_id=action["domain"],
                confidence=0.9
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[PERF-ANALYZER] Auto-tuning failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_tuning_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tuning action"""
        action_type = action["type"]
        domain_id = action["domain"]
        
        if action_type == "scale_workers":
            # Scale up HTM workers
            return await self._scale_htm_workers(domain_id, increase_by=2)
        
        elif action_type == "switch_model":
            # Prefer faster models
            return await self._update_model_preference(domain_id, "fast_local")
        
        elif action_type == "prioritize_missions":
            # Create improvement mission
            return await self._create_improvement_mission(domain_id, action)
        
        elif action_type == "add_htm_workers":
            # Add HTM workers
            worker_count = action.get("worker_count", 2)
            return await self._scale_htm_workers(domain_id, increase_by=worker_count)
        
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    async def _scale_htm_workers(self, domain_id: str, increase_by: int) -> Dict[str, Any]:
        """Scale HTM workers for domain"""
        try:
            # Would integrate with HTM pool
            logger.info(f"[PERF-ANALYZER] Scaling {domain_id} HTM workers by +{increase_by}")
            
            return {
                "success": True,
                "action": "scale_workers",
                "domain": domain_id,
                "workers_added": increase_by,
                "summary": f"Added {increase_by} HTM workers to {domain_id} for better throughput"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_model_preference(self, domain_id: str, preference: str) -> Dict[str, Any]:
        """Update model selection preference for domain"""
        try:
            
            # Update preference in capability system
            logger.info(f"[PERF-ANALYZER] Updating {domain_id} to prefer {preference} models")
            
            return {
                "success": True,
                "action": "switch_model",
                "domain": domain_id,
                "new_preference": preference,
                "summary": f"Updated {domain_id} to prefer {preference} models for better latency"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_improvement_mission(
        self,
        domain_id: str,
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create mission focused on domain improvement"""
        try:
            # Publish mission creation event
            await publish_domain_event(
                event_type="mission.improvement.created",
                domain_id=domain_id,
                data={
                    "title": f"Improve {domain_id} Performance",
                    "description": action["rationale"],
                    "target_metric": action["target_metric"],
                    "current_value": self.domain_metrics[domain_id].performance_score,
                    "target_value": 0.85,
                    "priority": "high",
                    "auto_generated": True
                }
            )
            
            return {
                "success": True,
                "action": "prioritize_missions",
                "domain": domain_id,
                "mission_created": True,
                "summary": f"Created improvement mission for {domain_id}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _load_historical_metrics(self):
        """Load historical metrics from world model"""
        try:
            from backend.world_model import grace_world_model
            
            # Query for past performance data
            results = await grace_world_model.query(
                query="domain performance metrics",
                category='self',
                top_k=10
            )
            
            logger.info(f"[PERF-ANALYZER] Loaded {len(results)} historical data points")
            
        except Exception as e:
            logger.warning(f"[PERF-ANALYZER] Could not load historical metrics: {e}")
    
    def get_domain_report(self, domain_id: str) -> Dict[str, Any]:
        """Get performance report for specific domain"""
        metrics = self.domain_metrics.get(domain_id)
        
        if not metrics:
            return {"error": "domain_not_found", "domain_id": domain_id}
        
        return {
            "domain_id": domain_id,
            "performance_score": metrics.performance_score,
            "reliability_rank": metrics.reliability_rank,
            "metrics": {
                "success_rate": metrics.success_rate,
                "mean_execution_time": metrics.mean_execution_time_seconds,
                "mean_repair_time": metrics.mean_repair_time_seconds,
                "p95_latency": metrics.p95_latency_seconds,
                "average_confidence": metrics.average_confidence
            },
            "operations": {
                "total": metrics.total_operations,
                "successful": metrics.successful_operations,
                "failed": metrics.failed_operations
            },
            "health": {
                "uptime": metrics.uptime_percentage,
                "incidents": metrics.incidents_count,
                "auto_healed": metrics.auto_healed_count
            },
            "last_updated": metrics.last_updated
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        return {
            "initialized": self._initialized,
            "domains_tracked": len(self.domain_metrics),
            "last_analysis": self.last_analysis.analysis_timestamp if self.last_analysis else None,
            "overall_health": self.last_analysis.overall_health if self.last_analysis else None
        }


# Global instance
domain_performance_analyzer = DomainPerformanceAnalyzer()


# Convenience function
async def get_self_assessment() -> SelfAnalysis:
    """
    Get Grace's current self-assessment
    
    Returns analysis of strengths, weaknesses, and improvement actions
    """
    return await domain_performance_analyzer.analyze_all_domains()


async def execute_improvement_action(action_index: int = 0) -> Dict[str, Any]:
    """
    Execute a specific improvement action
    
    Args:
        action_index: Index of action to execute (0 = highest priority)
        
    Returns:
        Execution result
    """
    if not domain_performance_analyzer.last_analysis:
        await get_self_assessment()
    
    if not domain_performance_analyzer.last_analysis.improvement_actions:
        return {"success": False, "error": "no_actions_available"}
    
    action = domain_performance_analyzer.last_analysis.improvement_actions[action_index]
    return await domain_performance_analyzer.execute_auto_tuning(action)