"""
Mission Outcome Logger

Subscribes to mission lifecycle events and writes outcome narratives to world model.

Process:
1. Listen for mission.completed / mission.failed events
2. Pull mission metadata (objective, trigger, tasks executed, metrics)
3. Re-read KPI metrics to show tangible impact
4. Write knowledge entry to world model: "I fixed X because Y, metrics improved Z"
5. Log to governance for audit
6. Makes Grace able to answer "What did you fix today?" via RAG

Enables full storytelling loop: Grace can cite her own repairs/improvements
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MissionOutcomeLogger:
    """
    Logs mission outcomes to world model for conversational recall
    
    Creates narratives like:
    "I noticed ecommerce latency rising to 450ms. I analyzed capacity,
     added 2 workers, and scaled the service. Latency dropped to 280ms."
    """
    
    def __init__(self):
        self._initialized = False
        self.outcomes_logged = 0
        self.narratives_created = 0
        self.telemetry_backfills = 0  # Track telemetry operations
    
    async def initialize(self):
        """Initialize and subscribe to mission events"""
        if self._initialized:
            return
        
        logger.info("[OUTCOME-LOGGER] Initializing mission outcome logger")
        
        # Subscribe to mission lifecycle events
        try:
            from backend.domains import domain_event_bus
            
            domain_event_bus.subscribe("mission.completed", self._handle_mission_completed)
            domain_event_bus.subscribe("mission.failed", self._handle_mission_failed)
            domain_event_bus.subscribe("mission.auto.completed", self._handle_auto_mission_completed)
            
            logger.info("[OUTCOME-LOGGER] Subscribed to mission events")
        except Exception as e:
            logger.warning(f"[OUTCOME-LOGGER] Could not subscribe to events: {e}")
        
        self._initialized = True
        logger.info("[OUTCOME-LOGGER] Outcome logger ready")
    
    async def log_mission_outcome(
        self,
        mission_id: str,
        mission_data: Dict[str, Any],
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Log mission outcome to world model
        
        Args:
            mission_id: Mission identifier
            mission_data: Mission metadata and results
            success: Whether mission succeeded
            
        Returns:
            {
                "knowledge_id": str,
                "narrative": str,
                "metrics_impact": Dict,
                "success": bool
            }
        """
        try:
            # Step 1: Gather mission context
            mission_context = await self._gather_mission_context(mission_id, mission_data)
            
            # Step 2: Re-read KPIs to measure impact
            metrics_impact = await self._measure_impact(mission_context)
            
            # Step 3: Build narrative
            narrative = self._build_narrative(mission_context, metrics_impact, success)
            
            # Step 4: Store in world model
            knowledge_id = await self._store_narrative(narrative, mission_context, metrics_impact)
            
            # Step 5: Log to governance
            await self._log_governance(mission_id, narrative, success)
            
            # Step 6: NEW - Telemetry Backfill (hard numbers for "Did it work?")
            telemetry_data = await self._backfill_telemetry(
                mission_id=mission_id,
                mission_context=mission_context,
                knowledge_id=knowledge_id
            )
            
            await self._record_to_analytics(
                mission_id=mission_id,
                mission_context=mission_context,
                telemetry_data=telemetry_data,
                success=success
            )
            
            self.outcomes_logged += 1
            self.narratives_created += 1
            
            logger.info(f"[OUTCOME-LOGGER] Logged outcome for {mission_id} with telemetry")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "narrative": narrative,
                "metrics_impact": metrics_impact,
                "telemetry": telemetry_data,
                "mission_id": mission_id
            }
            
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Failed to log outcome: {e}")
            return {
                "success": False,
                "error": str(e),
                "mission_id": mission_id
            }
    
    async def _gather_mission_context(
        self,
        mission_id: str,
        mission_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather complete mission context"""
        return {
            "mission_id": mission_id,
            "title": mission_data.get("title", "Mission"),
            "domain_id": mission_data.get("domain_id", "unknown"),
            "mission_type": mission_data.get("mission_type", "unknown"),
            "trigger_reason": mission_data.get("trigger_reason") or mission_data.get("reason"),
            "tasks_executed": mission_data.get("tasks_executed", []),
            "duration_seconds": mission_data.get("duration_seconds", 0),
            "metrics_before": mission_data.get("metrics_before", {}),
            "metrics_after": mission_data.get("metrics_after", {}),
            "auto_generated": mission_data.get("auto_generated", False)
        }
    
    async def _measure_impact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Re-read KPIs to measure actual impact"""
        try:
            from backend.services.rag_service import rag_service
            
            # Query recent KPIs for this domain
            results = await rag_service.retrieve(
                query=f"{context['domain_id']} KPI metrics performance",
                filters={"domain_id": context['domain_id']},
                top_k=10,
                requested_by="outcome_logger"
            )
            
            # Extract latest metrics
            latest_metrics = {}
            if results.get("results"):
                latest = results["results"][0]
                latest_metrics = latest.get("metadata", {})
            
            # Calculate impact
            before = context.get("metrics_before", {})
            after = latest_metrics

            improvement = {}
            for key in before.keys():
                if key in after and isinstance(before[key], (int, float)) and isinstance(after[key], (int, float)):
                    change = after[key] - before[key]
                    pct_change = (change / before[key] * 100) if before[key] != 0 else 0
                    improvement[key] = {
                        "before": before[key],
                        "after": after[key],
                        "change": change,
                        "percent_change": pct_change
                    }
            
            return {
                "metrics_before": before,
                "metrics_after": after,
                "improvement": improvement,
                "measured_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"[OUTCOME-LOGGER] Could not measure impact: {e}")
            return {}
    
    def _build_narrative(
        self,
        context: Dict[str, Any],
        metrics_impact: Dict[str, Any],
        success: bool
    ) -> str:
        """Build human-readable narrative of what Grace did"""
        
        if success:
            parts = []
            
            # What was noticed
            trigger = context.get("trigger_reason", "an issue")
            parts.append(f"I noticed {trigger}.")

            # What was done
            if context.get("tasks_executed"):
                task_summary = ", ".join(t.get("type", "task") for t in context["tasks_executed"][:3])
                parts.append(f"I {task_summary}.")
            else:
                parts.append(f"I investigated and applied fixes.")

            # Impact
            if metrics_impact.get("improvement"):
                for metric_name, impact in list(metrics_impact["improvement"].items())[:2]:
                    before = impact["before"]
                    after = impact["after"]
                    change_pct = impact["percent_change"]
                    
                    if change_pct < 0:  # Improvement (lower is better for latency/errors)
                        parts.append(f"{metric_name} improved from {before:.1f} to {after:.1f} ({abs(change_pct):.1f}% better).")
                    elif change_pct > 0:  # Improvement (higher is better for success rate)
                        parts.append(f"{metric_name} increased from {before:.1f} to {after:.1f} ({change_pct:.1f}% improvement).")
            else:
                parts.append("Metrics stabilized.")
            
            # Duration
            if context.get("duration_seconds"):
                parts.append(f"Completed in {context['duration_seconds']/60:.1f} minutes.")
            
            return " ".join(parts)
        
        else:
            # Failure narrative
            return f"I attempted to fix {context.get('trigger_reason', 'an issue')} in {context['domain_id']}, but the mission did not complete successfully. Requires human review."
    
    async def _store_narrative(
        self,
        narrative: str,
        context: Dict[str, Any],
        metrics_impact: Dict[str, Any]
    ) -> str:
        """Store narrative in world model"""
        try:
            from backend.world_model import grace_world_model
            
            knowledge_id = await grace_world_model.add_knowledge(
                category='system',
                content=narrative,
                source=f"{context['domain_id']}_mission_outcome",
                confidence=0.95,
                tags=['mission', 'outcome', 'completed', context['domain_id'], context['mission_type']],
                metadata={
                    "mission_id": context["mission_id"],
                    "domain_id": context["domain_id"],
                    "mission_type": context["mission_type"],
                    "auto_generated": context.get("auto_generated", False),
                    "duration_seconds": context.get("duration_seconds", 0),
                    "tasks_count": len(context.get("tasks_executed", [])),
                    "metrics_impact": metrics_impact.get("improvement", {})
                }
            )
            
            return knowledge_id
            
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Failed to store narrative: {e}")
            return ""
    
    async def _log_governance(
        self,
        mission_id: str,
        narrative: str,
        success: bool
    ):
        """Log to governance for audit"""
        try:
            from backend.logging_utils import log_event
            
            log_event(
                action="mission.outcome.logged",
                actor="grace_autonomous",
                resource=mission_id,
                outcome="success" if success else "failure",
                payload={
                    "mission_id": mission_id,
                    "narrative_preview": narrative[:200],
                    "success": success
                }
            )
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Governance logging failed: {e}")
    
    async def _handle_mission_completed(self, event):
        """Handle mission.completed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            await self.log_mission_outcome(
                mission_id=data.get("mission_id", "unknown"),
                mission_data=data,
                success=True
            )
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Error handling completed: {e}")
    
    async def _handle_mission_failed(self, event):
        """Handle mission.failed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            await self.log_mission_outcome(
                mission_id=data.get("mission_id", "unknown"),
                mission_data=data,
                success=False
            )
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Error handling failed: {e}")
    
    async def _handle_auto_mission_completed(self, event):
        """Handle auto-generated mission completion"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            await self.log_mission_outcome(
                mission_id=data.get("mission_id", "unknown"),
                mission_data=data,
                success=data.get("success", True)
            )
        except Exception as e:
            logger.error(f"[OUTCOME-LOGGER] Error handling auto mission: {e}")
    
    async def _backfill_telemetry(
        self,
        mission_id: str,
        mission_context: Dict[str, Any],
        knowledge_id: str
    ) -> Dict[str, Any]:
        """
        Backfill telemetry with hard pre/post metrics
        
        After outcome is logged, re-query actual KPI sources for concrete numbers
        so Grace can answer "Did the fix work?" with hard data.
        
        Returns:
            {
                "metrics_captured": bool,
                "pre_post_comparison": Dict,
                "effectiveness_score": float,
                "data_sources": List[str]
            }
        """
        try:
            domain_id = mission_context.get("domain_id", "unknown")
            
            # Wait a moment for metrics to propagate
            await asyncio.sleep(2)
            
            # Query multiple data sources for comprehensive metrics
            telemetry = {
                "metrics_captured": False,
                "pre_post_comparison": {},
                "effectiveness_score": 0.0,
                "data_sources": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Source 1: RAG for stored KPIs
            rag_metrics = await self._query_rag_metrics(domain_id, mission_context)
            if rag_metrics:
                telemetry["data_sources"].append("rag_kpis")
                telemetry["pre_post_comparison"]["rag"] = rag_metrics
            
            # Source 2: Domain health metrics (if available)
            try:
                from backend.domains import domain_registry
                domain_health = await domain_registry.get_domain_health(domain_id)
                if domain_health:
                    telemetry["data_sources"].append("domain_health")
                    telemetry["pre_post_comparison"]["domain_health"] = {
                        "current_status": domain_health.get("status"),
                        "health_score": domain_health.get("health_score"),
                        "active_alerts": domain_health.get("active_alerts", 0)
                    }
            except Exception as e:
                logger.debug(f"[TELEMETRY] Domain health unavailable: {e}")
            
            # Source 3: Infrastructure metrics (if available)
            try:
                from backend.infrastructure import service_mesh
                service_metrics = await service_mesh.get_service_metrics(domain_id)
                if service_metrics:
                    telemetry["data_sources"].append("service_mesh")
                    telemetry["pre_post_comparison"]["infrastructure"] = service_metrics
            except Exception as e:
                logger.debug(f"[TELEMETRY] Infrastructure metrics unavailable: {e}")
            
            # Calculate effectiveness score
            if telemetry["pre_post_comparison"]:
                telemetry["metrics_captured"] = True
                telemetry["effectiveness_score"] = self._calculate_effectiveness(
                    telemetry["pre_post_comparison"]
                )
                
                # Update world model entry with telemetry
                await self._update_outcome_with_telemetry(knowledge_id, telemetry)
                
                self.telemetry_backfills += 1
                logger.info(f"[TELEMETRY] Backfilled metrics from {len(telemetry['data_sources'])} sources")
            
            return telemetry
            
        except Exception as e:
            logger.error(f"[TELEMETRY] Backfill failed: {e}")
            return {
                "metrics_captured": False,
                "error": str(e)
            }
    
    async def _query_rag_metrics(
        self,
        domain_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query RAG for KPI metrics with pre/post comparison"""
        try:
            from backend.services.rag_service import rag_service
            
            # Get metrics before and after mission
            before_time = datetime.utcnow() - timedelta(hours=1)
            after_time = datetime.utcnow()
            
            # Query for current metrics
            current_results = await rag_service.retrieve(
                query=f"{domain_id} KPI metrics performance status",
                filters={"domain_id": domain_id},
                top_k=5,
                requested_by="telemetry_backfill"
            )
            
            if not current_results.get("results"):
                return {}
            
            # Extract numeric metrics
            current_metrics = {}
            for result in current_results["results"]:
                metadata = result.get("metadata", {})
                for key, value in metadata.items():
                    if isinstance(value, (int, float)) and key not in ["confidence", "score"]:
                        current_metrics[key] = value
            
            # Compare with baseline from mission context
            baseline = context.get("metrics_before", {})
            
            comparison = {}
            for metric_name in set(list(baseline.keys()) + list(current_metrics.keys())):
                before_val = baseline.get(metric_name)
                after_val = current_metrics.get(metric_name)
                
                if before_val is not None and after_val is not None:
                    if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                        delta = after_val - before_val
                        pct_change = (delta / before_val * 100) if before_val != 0 else 0
                        
                        comparison[metric_name] = {
                            "pre": before_val,
                            "post": after_val,
                            "delta": delta,
                            "percent_change": pct_change,
                            "improved": self._is_improvement(metric_name, delta)
                        }
            
            return comparison
            
        except Exception as e:
            logger.warning(f"[TELEMETRY] RAG metrics query failed: {e}")
            return {}
    
    def _is_improvement(self, metric_name: str, delta: float) -> bool:
        """Determine if metric change is an improvement"""
        # Lower is better for these metrics
        lower_is_better = [
            "latency", "error_rate", "errors", "failures", 
            "response_time", "memory_usage", "cpu_usage"
        ]
        
        for pattern in lower_is_better:
            if pattern in metric_name.lower():
                return delta < 0  # Negative change is improvement
        
        # Higher is better for everything else
        return delta > 0
    
    def _calculate_effectiveness(self, pre_post_data: Dict[str, Any]) -> float:
        """
        Calculate mission effectiveness score from pre/post metrics
        
        Returns score 0.0-1.0 based on metric improvements
        """
        total_score = 0.0
        metric_count = 0
        
        for source, metrics in pre_post_data.items():
            if isinstance(metrics, dict):
                for metric_name, metric_data in metrics.items():
                    if isinstance(metric_data, dict) and "improved" in metric_data:
                        if metric_data["improved"]:
                            # Weight by magnitude of improvement
                            pct = abs(metric_data.get("percent_change", 0))
                            score = min(pct / 100, 1.0)  # Cap at 100%
                            total_score += score
                        else:
                            # Negative score for regressions
                            total_score -= 0.1
                        metric_count += 1
        
        if metric_count == 0:
            return 0.5  # Neutral score if no metrics
        
        # Average and normalize to 0-1 range
        avg_score = total_score / metric_count
        return max(0.0, min(1.0, avg_score))
    
    async def _update_outcome_with_telemetry(
        self,
        knowledge_id: str,
        telemetry: Dict[str, Any]
    ):
        """Update world model outcome entry with telemetry data"""
        try:
            from backend.world_model import grace_world_model
            
            # Add telemetry as additional metadata
            await grace_world_model.update_knowledge_metadata(
                knowledge_id=knowledge_id,
                additional_metadata={
                    "telemetry_backfill": telemetry,
                    "effectiveness_score": telemetry.get("effectiveness_score", 0),
                    "metrics_data_sources": telemetry.get("data_sources", [])
                }
            )
            
        except Exception as e:
            logger.error(f"[TELEMETRY] Failed to update outcome: {e}")
    
    async def _record_to_analytics(
        self,
        mission_id: str,
        mission_context: Dict[str, Any],
        telemetry_data: Dict[str, Any],
        success: bool
    ):
        """Record mission to analytics for historical analysis"""
        try:
            from backend.autonomy.mission_analytics import mission_analytics
            
            # Extract metrics delta from telemetry
            metrics_delta = {}
            if telemetry_data.get("pre_post_comparison"):
                for source, metrics in telemetry_data["pre_post_comparison"].items():
                    if isinstance(metrics, dict):
                        for metric_name, metric_data in metrics.items():
                            if isinstance(metric_data, dict) and "percent_change" in metric_data:
                                metrics_delta[metric_name] = metric_data["percent_change"]
            
            await mission_analytics.record_mission(
                mission_id=mission_id,
                domain_id=mission_context.get("domain_id", "unknown"),
                mission_type=mission_context.get("mission_type", "unknown"),
                success=success,
                duration_seconds=mission_context.get("duration_seconds", 0),
                effectiveness_score=telemetry_data.get("effectiveness_score", 0.5),
                metrics_delta=metrics_delta,
                tasks_count=len(mission_context.get("tasks_executed", [])),
                auto_generated=mission_context.get("auto_generated", False),
                metadata={
                    "trigger_reason": mission_context.get("trigger_reason"),
                    "title": mission_context.get("title")
                }
            )
            
        except Exception as e:
            logger.error(f"[ANALYTICS] Failed to record mission: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics"""
        return {
            "initialized": self._initialized,
            "outcomes_logged": self.outcomes_logged,
            "narratives_created": self.narratives_created,
            "telemetry_backfills": self.telemetry_backfills
        }


# Global instance
mission_outcome_logger = MissionOutcomeLogger()


# Convenience function
async def log_mission_completion(mission_id: str, outcome_data: Dict[str, Any]) -> str:
    """
    Log a mission completion with outcome narrative
    
    Returns the created narrative
    """
    result = await mission_outcome_logger.log_mission_outcome(
        mission_id=mission_id,
        mission_data=outcome_data,
        success=outcome_data.get("success", True)
    )
    
    return result.get("narrative", "")