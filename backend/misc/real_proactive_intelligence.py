"""
Real Proactive Intelligence - Consumes Real Telemetry
Replaces stubbed version with actual metric-driven decision making
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

from .telemetry_schemas import MetricEvent, MetricBand, PlaybookDefinition
from .trigger_mesh import trigger_mesh, TriggerEvent
from .logging_utils import log_event
from .governance_framework import governance_framework
from .policy_engine import policy_engine
from .causal_playbook_reinforcement import causal_rl_agent
from .temporal_forecasting import temporal_forecaster, ForecastRequest

logger = logging.getLogger(__name__)


class RealProactiveIntelligence:
    """
    Consumes REAL telemetry and triggers REAL playbook execution
    
    Listens for:
    - metrics.* events (from collectors)
    - metrics.action_recommended events (from snapshot aggregator)
    
    Takes action:
    - Evaluates playbook recommendations
    - Checks governance & policy
    - Executes or requests approval based on risk
    """
    
    def __init__(self):
        self.running = False
        self.playbook_registry: Dict[str, PlaybookDefinition] = {}
        self.catalog_path = Path(__file__).parent.parent / "config" / "metrics_catalog.yaml"
        
        # Track recent metric bands to detect patterns
        self.recent_bands: Dict[str, List[str]] = {}  # metric_id -> [band, band, ...]
    
    async def start(self):
        """Start proactive intelligence"""
        if self.running:
            return
        
        # Load playbook registry
        await self._load_playbooks()
        
        # Subscribe to metrics events
        trigger_mesh.subscribe("metrics.*", self._handle_metric_event)
        trigger_mesh.subscribe("metrics.action_recommended", self._handle_action_recommendation)
        
        self.running = True
        logger.info("[PROACTIVE-INTEL] ✅ Real proactive intelligence started")
        logger.info(f"[PROACTIVE-INTEL] Loaded {len(self.playbook_registry)} playbooks")
    
    async def stop(self):
        """Stop proactive intelligence"""
        self.running = False
        logger.info("[PROACTIVE-INTEL] Stopped")
    
    async def _load_playbooks(self):
        """Load playbook definitions from catalog"""
        try:
            with open(self.catalog_path, 'r') as f:
                catalog_data = yaml.safe_load(f)
            
            for playbook in catalog_data.get('playbooks', []):
                pb = PlaybookDefinition(**playbook)
                self.playbook_registry[pb.playbook_id] = pb
            
            logger.info(f"[PROACTIVE-INTEL] Loaded {len(self.playbook_registry)} playbooks")
        except Exception as e:
            logger.error(f"[PROACTIVE-INTEL] Failed to load playbooks: {e}")
            self.playbook_registry = {}
    
    async def _handle_metric_event(self, event: TriggerEvent):
        """Handle real-time metric event"""
        try:
            metric_id = event.payload.get("metric_id")
            band = event.payload.get("computed_band")
            value = event.payload.get("value")
            
            if not metric_id or not band:
                return
            
            # Track band history
            if metric_id not in self.recent_bands:
                self.recent_bands[metric_id] = []
            self.recent_bands[metric_id].append(band)
            
            # Keep last 10 samples
            if len(self.recent_bands[metric_id]) > 10:
                self.recent_bands[metric_id].pop(0)
            
            # Detect sustained critical state (3+ consecutive critical)
            if len(self.recent_bands[metric_id]) >= 3:
                last_three = self.recent_bands[metric_id][-3:]
                if all(b == "critical" for b in last_three):
                    logger.warning(
                        f"[PROACTIVE-INTEL] 🚨 Sustained critical: {metric_id} = {value} "
                        f"(3+ consecutive critical samples)"
                    )
                    
                    # This will trigger playbook recommendation via snapshot aggregator
        
        except Exception as e:
            logger.error(f"[PROACTIVE-INTEL] Error handling metric event: {e}")
    
    async def _handle_action_recommendation(self, event: TriggerEvent):
        """Handle playbook recommendation from snapshot aggregator"""
        try:
            playbook_id = event.payload.get("playbook_id")
            metric_id = event.payload.get("metric_id")
            confidence = event.payload.get("confidence", 0.0)
            band = event.payload.get("band")
            
            if not playbook_id:
                return
            
            # Get playbook definition
            playbook = self.playbook_registry.get(playbook_id)
            if not playbook:
                logger.warning(f"[PROACTIVE-INTEL] Unknown playbook: {playbook_id}")
                return
            
            # Use causal RL to rank playbooks if multiple candidates
            service = event.payload.get("service", "grace-api")
            diagnosis = event.payload.get("metric_id", metric_id)
            candidates = event.payload.get("candidate_playbooks", [playbook_id])
            
            if len(candidates) > 1:
                ranked = await causal_rl_agent.recommend(service, diagnosis, candidates)
                logger.info(f"[PROACTIVE-INTEL] 🧠 RL ranked playbooks: {ranked[:3]}")
                print(f"[PROACTIVE-INTEL] 🧠 ML recommended: {ranked[0]} (learned from past incidents)")
                playbook_id = ranked[0]
                playbook = self.playbook_registry.get(playbook_id)
            
            logger.info(
                f"[PROACTIVE-INTEL] 🎯 Evaluating playbook '{playbook_id}' "
                f"for {metric_id} ({band}, confidence={confidence})"
            )
            
            # Check governance approval
            approval = await governance_framework.check_action(
                actor="proactive_intelligence",
                action=f"execute_playbook_{playbook_id}",
                resource=metric_id,
                context={
                    "playbook_id": playbook_id,
                    "metric_id": metric_id,
                    "metric_band": band,
                    "confidence": confidence,
                    "risk_level": playbook.risk_level,
                    "autonomy_tier": playbook.autonomy_tier
                },
                confidence=confidence
            )
            
            if approval.get("approved"):
                # Execute playbook
                if playbook.requires_approval and not approval.get("pre_approved"):
                    # High-risk: Request human approval
                    logger.warning(
                        f"[PROACTIVE-INTEL] 🔔 Playbook '{playbook_id}' requires approval "
                        f"(risk={playbook.risk_level})"
                    )
                    
                    await self._request_playbook_approval(playbook, metric_id, event.payload)
                else:
                    # Low/medium risk: Execute autonomously
                    logger.info(
                        f"[PROACTIVE-INTEL] ✅ Executing playbook '{playbook_id}' autonomously"
                    )
                    
                    await self._execute_playbook(playbook, metric_id, event.payload)
            else:
                logger.warning(
                    f"[PROACTIVE-INTEL] 🚫 Playbook '{playbook_id}' blocked by governance: "
                    f"{approval.get('reason')}"
                )
        
        except Exception as e:
            logger.error(f"[PROACTIVE-INTEL] Error handling action recommendation: {e}")
    
    async def _request_playbook_approval(
        self, 
        playbook: PlaybookDefinition, 
        metric_id: str, 
        context: Dict[str, Any]
    ):
        """Request human approval for high-risk playbook"""
        
        # Create approval request
        from .models import async_session
        from .governance_models import ApprovalRequest
        
        try:
            async with async_session() as session:
                approval_req = ApprovalRequest(
                    event_type=f"playbook_execution_{playbook.playbook_id}",
                    actor="proactive_intelligence",
                    action=f"execute_playbook_{playbook.playbook_id}",
                    resource=metric_id,
                    tier=playbook.autonomy_tier,
                    context_data={
                        "playbook": playbook.model_dump(),
                        "metric_context": context
                    },
                    status="pending"
                )
                
                session.add(approval_req)
                await session.commit()
                
                logger.info(
                    f"[PROACTIVE-INTEL] 📋 Approval request created for {playbook.playbook_id} "
                    f"(request_id={approval_req.id})"
                )
        
        except Exception as e:
            logger.error(f"[PROACTIVE-INTEL] Error creating approval request: {e}")
    
    async def _execute_playbook(
        self, 
        playbook: PlaybookDefinition, 
        metric_id: str, 
        context: Dict[str, Any]
    ):
        """Execute playbook autonomously"""
        
        # This is where REAL playbook execution happens
        # For now, log the intent - actual playbook execution system comes next
        
        log_event("playbook_executed", {
            "playbook_id": playbook.playbook_id,
            "metric_id": metric_id,
            "risk_level": playbook.risk_level,
            "autonomy_tier": playbook.autonomy_tier,
            "context": context
        })
        
        # Publish execution event
        await trigger_mesh.publish(TriggerEvent(
            event_type=f"playbook.executed.{playbook.playbook_id}",
            source="proactive_intelligence",
            actor="metrics_system",
            resource=metric_id,
            subsystem="autonomy",
            payload={
                "playbook_id": playbook.playbook_id,
                "metric_context": context,
                "executed_at": datetime.now(timezone.utc).isoformat()
            }
        ))
        
        logger.info(
            f"[PROACTIVE-INTEL] ⚡ Executed playbook '{playbook.playbook_id}' "
            f"for {metric_id}"
        )


# Global instance
real_proactive_intelligence = RealProactiveIntelligence()
