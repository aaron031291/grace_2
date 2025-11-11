"""
GRACE Core - Simplified Unified Autonomous Engine

Consolidates AgenticSpine, memory systems, health monitoring, and governance
into a single, maintainable decision-making engine.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .integrations.slack_integration import slack_integration
from .integrations.pagerduty_integration import pagerduty_integration
from .integrations.github_integration import github_integration


class Decision(Enum):
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"
    MONITOR = "monitor"


@dataclass
class EnrichedEvent:
    """Simplified event with context"""
    event_id: str
    original_event: TriggerEvent
    context: Dict[str, Any]
    confidence: float
    risk_score: float
    intent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionPlan:
    """Simplified action plan"""
    plan_id: str
    actions: List[Dict[str, Any]]
    risk_score: float
    justification: str
    requires_approval: bool
    status: str = "pending"


class UnifiedMemory:
    """Single memory system consolidating all memory types"""

    def __init__(self):
        self.short_term = {}  # Current context and conversations
        self.long_term = {}   # Persistent knowledge and patterns
        self.episodes = []    # Action history for learning
        self.patterns = {}    # Learned behavior patterns

    async def store(self, key: str, data: Any, memory_type: str = "short_term", ttl: int = None):
        """Unified storage interface"""
        entry = {
            "data": data,
            "timestamp": datetime.utcnow(),
            "type": memory_type,
            "ttl": ttl
        }

        if memory_type == "short_term":
            self.short_term[key] = entry
        elif memory_type == "long_term":
            self.long_term[key] = entry
        elif memory_type == "pattern":
            self.patterns[key] = entry
        elif memory_type == "episode":
            self.episodes.append({"key": key, **entry})

        # Auto-cleanup based on TTL
        if ttl:
            asyncio.create_task(self._cleanup_entry(key, memory_type, ttl))

    async def retrieve(self, key: str, memory_type: str = "auto") -> Optional[Any]:
        """Unified retrieval with automatic type detection"""
        if memory_type == "auto":
            # Search all memory types
            for mem_type in ["short_term", "long_term", "patterns"]:
                result = await self._get_from_type(key, mem_type)
                if result:
                    return result

            # Search episodes
            for episode in reversed(self.episodes[-100:]):  # Last 100 episodes
                if episode["key"] == key:
                    return episode["data"]

        else:
            return await self._get_from_type(key, memory_type)

        return None

    async def _get_from_type(self, key: str, mem_type: str) -> Optional[Any]:
        """Get from specific memory type"""
        if mem_type == "short_term" and key in self.short_term:
            return self.short_term[key]["data"]
        elif mem_type == "long_term" and key in self.long_term:
            return self.long_term[key]["data"]
        elif mem_type == "patterns" and key in self.patterns:
            return self.patterns[key]["data"]
        return None

    async def _cleanup_entry(self, key: str, mem_type: str, ttl: int):
        """Remove entry after TTL expires"""
        await asyncio.sleep(ttl)
        if mem_type == "short_term" and key in self.short_term:
            del self.short_term[key]
        elif mem_type == "long_term" and key in self.long_term:
            del self.long_term[key]


class UnifiedPolicyEngine:
    """Consolidated governance, ethics, and trust evaluation"""

    def __init__(self):
        self.policies = {
            "max_risk_score": 0.7,
            "require_approval_threshold": 0.5,
            "restricted_actions": ["data_deletion", "security_change", "production_deploy"],
            "auto_approve_below": 0.3
        }
        self.approval_queue = []

    async def evaluate_action(self, enriched_event: EnrichedEvent) -> Decision:
        """Unified policy evaluation"""
        risk_score = enriched_event.risk_score

        # Auto-approve low risk actions
        if risk_score < self.policies["auto_approve_below"]:
            return Decision.APPROVE

        # Require approval for high risk
        if risk_score > self.policies["require_approval_threshold"]:
            return Decision.ESCALATE

        # Check restricted actions
        if enriched_event.intent in self.policies["restricted_actions"]:
            return Decision.ESCALATE

        # Maximum risk threshold
        if risk_score > self.policies["max_risk_score"]:
            return Decision.DENY

        return Decision.APPROVE

    async def request_approval(self, plan: ActionPlan) -> bool:
        """Request human approval for high-risk actions"""
        approval_request = {
            "plan_id": plan.plan_id,
            "risk_score": plan.risk_score,
            "justification": plan.justification,
            "timestamp": datetime.utcnow(),
            "status": "pending"
        }

        self.approval_queue.append(approval_request)

        # Notify external systems
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.approval_required",
            source="policy_engine",
            actor="grace_core",
            resource=plan.plan_id,
            payload={
                "risk_score": plan.risk_score,
                "justification": plan.justification
            },
            timestamp=datetime.utcnow()
        ))

        return True  # Approval requested


class ActionPlanner:
    """Simplified action planning and execution"""

    def __init__(self):
        self.playbooks = {
            "scale_up": {
                "actions": [{"type": "scale", "direction": "up"}],
                "rollback": [{"type": "scale", "direction": "down"}]
            },
            "restart_service": {
                "actions": [{"type": "restart", "target": "service"}],
                "rollback": []  # Service restart is self-rollback
            },
            "health_check": {
                "actions": [{"type": "probe", "target": "health"}],
                "rollback": []
            }
        }

    async def create_plan(self, enriched_event: EnrichedEvent) -> Optional[ActionPlan]:
        """Create action plan based on enriched event"""
        intent = enriched_event.intent

        if intent == "adjust_capacity":
            playbook = self.playbooks["scale_up"]
        elif intent == "signal_degradation":
            playbook = self.playbooks["restart_service"]
        else:
            playbook = self.playbooks["health_check"]

        plan = ActionPlan(
            plan_id=f"plan_{datetime.utcnow().timestamp()}",
            actions=playbook["actions"],
            risk_score=enriched_event.risk_score,
            justification=f"Automated response to {intent}",
            requires_approval=enriched_event.risk_score > 0.5
        )

        return plan

    async def execute_plan(self, plan: ActionPlan) -> bool:
        """Execute action plan"""
        try:
            for action in plan.actions:
                await self._execute_action(action)

            plan.status = "completed"
            return True

        except Exception as e:
            plan.status = "failed"
            # Attempt rollback
            await self._rollback_plan(plan)
            return False

    async def _execute_action(self, action: Dict[str, Any]):
        """Execute individual action"""
        action_type = action.get("type")

        if action_type == "scale":
            # AWS scaling integration
            from .executors.aws_executor import aws_executor
            await aws_executor.execute_scale_action(
                action.get("resource", "default"),
                2 if action.get("direction") == "up" else 1
            )

        elif action_type == "restart":
            # AWS restart integration
            from .executors.aws_executor import aws_executor
            await aws_executor.execute_restart_action(action.get("resource", "default"))

        elif action_type == "probe":
            # Health probe
            await asyncio.sleep(0.1)  # Mock probe

    async def _rollback_plan(self, plan: ActionPlan):
        """Rollback failed plan"""
        # Simplified rollback - in real system would use playbook rollback steps
        print(f"Rolling back plan {plan.plan_id}")


class LearningEngine:
    """Unified learning from all actions and outcomes"""

    def __init__(self, memory: UnifiedMemory):
        self.memory = memory
        self.success_patterns = {}
        self.failure_patterns = {}

    async def learn_from_action(self, plan: ActionPlan):
        """Learn from action outcomes"""
        # Store episode in memory
        await self.memory.store(
            key=f"episode_{plan.plan_id}",
            data={
                "actions": plan.actions,
                "outcome": plan.status,
                "risk_score": plan.risk_score,
                "justification": plan.justification
            },
            memory_type="episode"
        )

        # Update success/failure patterns
        if plan.status == "completed":
            self.success_patterns[plan.justification] = \
                self.success_patterns.get(plan.justification, 0) + 1
        else:
            self.failure_patterns[plan.justification] = \
                self.failure_patterns.get(plan.justification, 0) + 1

        # Store updated patterns
        await self.memory.store(
            key="success_patterns",
            data=self.success_patterns,
            memory_type="pattern"
        )

        await self.memory.store(
            key="failure_patterns",
            data=self.failure_patterns,
            memory_type="pattern"
        )


class IntegrationHub:
    """Unified external system integration"""

    def __init__(self):
        self.connectors = {
            'slack': slack_integration,
            'pagerduty': pagerduty_integration,
            'github': github_integration
        }

    async def notify(self, system: str, message: Dict[str, Any]):
        """Send notification to external system"""
        if system == "slack":
            await self.connectors['slack'].notify_recovery(message)
        elif system == "pagerduty":
            if message.get("severity") == "critical":
                await self.connectors['pagerduty'].notify_critical_incident(message)
        elif system == "github":
            await self.connectors['github'].notify_system_incident(message)

    async def handle_webhook(self, system: str, payload: Dict[str, Any]):
        """Handle incoming webhook from external system"""
        if system == "slack":
            await self.connectors['slack'].handle_slack_event(
                TriggerEvent(
                    event_type="external.slack_event",
                    source="webhook",
                    actor="slack",
                    resource="message",
                    payload=payload
                )
            )
        elif system == "pagerduty":
            await self.connectors['pagerduty'].handle_pagerduty_webhook(payload)
        elif system == "github":
            await self.connectors['github'].handle_github_webhook(payload)


class GraceCore:
    """
    Simplified unified autonomous engine consolidating all GRACE capabilities
    """

    def __init__(self):
        self.memory = UnifiedMemory()
        self.policy_engine = UnifiedPolicyEngine()
        self.action_planner = ActionPlanner()
        self.learning_engine = LearningEngine(self.memory)
        self.integration_hub = IntegrationHub()
        self.running = False

    async def start(self):
        """Start the unified core"""
        await trigger_mesh.subscribe("*", self._handle_event)
        self.running = True
        print("✓ GRACE Core activated - Simplified autonomous engine running")

    async def stop(self):
        """Stop the unified core"""
        self.running = False
        print("✓ GRACE Core deactivated")

    async def _handle_event(self, event: TriggerEvent):
        """Unified event processing pipeline"""
        if not self.running:
            return

        # Enrich event with context
        enriched = await self._enrich_event(event)

        # Log enrichment
        await immutable_log.append(
            actor="grace_core",
            action="event_processed",
            resource=enriched.event_id,
            subsystem="core",
            payload={
                "confidence": enriched.confidence,
                "intent": enriched.intent,
                "risk_score": enriched.risk_score
            },
            result="processed"
        )

        # Skip low confidence events
        if enriched.confidence < 0.4:
            return

        # Handle different event types
        if event.event_type.startswith(("health.degraded", "alert.", "incident.")):
            await self._handle_incident(enriched)
        elif event.event_type.startswith("external."):
            await self._handle_external_event(event)

    async def _enrich_event(self, event: TriggerEvent) -> EnrichedEvent:
        """Enrich event with context and risk assessment"""
        # Gather context from memory
        context = await self._gather_context(event)

        # Calculate confidence and risk
        confidence = await self._calculate_confidence(event, context)
        risk_score = await self._assess_risk(event, context)
        intent = await self._infer_intent(event)

        return EnrichedEvent(
            event_id=f"{event.source}:{event.event_type}:{datetime.utcnow().timestamp()}",
            original_event=event,
            context=context,
            confidence=confidence,
            risk_score=risk_score,
            intent=intent
        )

    async def _gather_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Gather relevant context from memory"""
        # Query memory for similar events and system state
        similar_events = await self.memory.retrieve(f"similar_{event.event_type}")
        system_state = await self.memory.retrieve("system_health")

        return {
            "similar_events": similar_events or [],
            "system_state": system_state or {"status": "unknown"},
            "event_history": await self.memory.retrieve("recent_events") or []
        }

    async def _calculate_confidence(self, event: TriggerEvent, context: Dict) -> float:
        """Calculate confidence in event interpretation"""
        signal_count = len(context.get("similar_events", []))
        return min(0.5 + (signal_count * 0.05), 0.95)

    async def _assess_risk(self, event: TriggerEvent, context: Dict) -> float:
        """Assess risk level of the event"""
        base_risk = {
            "health.degraded": 0.6,
            "alert.critical": 0.8,
            "incident.": 0.7
        }.get(event.event_type.split(".")[0], 0.4)

        # Adjust based on system state
        if context.get("system_state", {}).get("status") == "critical":
            base_risk += 0.2

        return min(base_risk, 1.0)

    async def _infer_intent(self, event: TriggerEvent) -> str:
        """Infer the intent behind the event"""
        if "deploy" in event.event_type:
            return "deploy_new_version"
        elif "scale" in event.event_type:
            return "adjust_capacity"
        elif "alert" in event.event_type or "incident" in event.event_type:
            return "signal_degradation"
        return "unknown_intent"

    async def _handle_incident(self, enriched: EnrichedEvent):
        """Handle incident with autonomous response"""
        # Evaluate against policy
        decision = await self.policy_engine.evaluate_action(enriched)

        if decision == Decision.DENY:
            await immutable_log.append(
                actor="grace_core",
                action="action_denied",
                resource=enriched.event_id,
                subsystem="policy",
                payload={"reason": "policy_violation", "risk_score": enriched.risk_score},
                result="denied"
            )
            return

        if decision == Decision.ESCALATE:
            # Request approval
            plan = await self.action_planner.create_plan(enriched)
            if plan:
                await self.policy_engine.request_approval(plan)
            return

        # Auto-approve and execute
        plan = await self.action_planner.create_plan(enriched)
        if plan:
            # Notify external systems
            await self.integration_hub.notify("slack", {
                "action": plan.actions[0].get("type", "unknown"),
                "description": plan.justification,
                "risk_score": plan.risk_score,
                "status": "planned"
            })

            # Execute plan
            success = await self.action_planner.execute_plan(plan)

            # Update notifications
            await self.integration_hub.notify("slack", {
                "action": plan.actions[0].get("type", "unknown"),
                "description": plan.justification,
                "risk_score": plan.risk_score,
                "status": "completed" if success else "failed"
            })

            # Learn from outcome
            await self.learning_engine.learn_from_action(plan)

            # Log execution
            await immutable_log.append(
                actor="grace_core",
                action="plan_executed",
                resource=plan.plan_id,
                subsystem="executor",
                payload={"outcome": plan.status, "success": success},
                result="success" if success else "failed"
            )

    async def _handle_external_event(self, event: TriggerEvent):
        """Handle external system events"""
        system = event.event_type.split(".")[1]  # external.slack, external.github, etc.
        await self.integration_hub.handle_webhook(system, event.payload)


# Global instance
grace_core = GraceCore()