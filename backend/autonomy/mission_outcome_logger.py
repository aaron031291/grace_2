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
            
            self.outcomes_logged += 1
            self.narratives_created += 1
            
            logger.info(f"[OUTCOME-LOGGER] Logged outcome for {mission_id}")
            
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "narrative": narrative,
                "metrics_impact": metrics_impact,
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics"""
        return {
            "initialized": self._initialized,
            "outcomes_logged": self.outcomes_logged,
            "narratives_created": self.narratives_created
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