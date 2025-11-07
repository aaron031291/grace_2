"""
Cognition Intent System - Central Authority for Decision-Making

The cognition domain is the AUTHORITY that:
- Parses user intent from utterances
- Creates structured plans
- Executes through agentic safeguards
- Returns structured results

The LLM is just a NARRATOR that verbalizes cognition's structured outputs.

Intent Flow:
User Input → Cognition Parses Intent → Cognition Plans → Agentic Execution → Structured Result → LLM Narrates
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy import Column, String, JSON, DateTime, Integer, Boolean
from .models import Base, async_session
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class IntentStatus(Enum):
    """Intent lifecycle states"""
    CREATED = "created"
    PARSING = "parsing"
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CognitionIntent(Base):
    """
    Structured intent extracted from user utterance.
    This is cognition's understanding of what the user wants.
    """
    __tablename__ = "cognition_intents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), nullable=False)
    
    # Raw input
    raw_utterance = Column(String, nullable=False)
    user_id = Column(String(128), nullable=True)
    
    # Parsed intent
    intent_type = Column(String(128), nullable=False)  # e.g., "task.list", "chat.respond", "code.edit"
    intent_parameters = Column(JSON, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Planning
    plan_id = Column(String(128), nullable=True)
    planned_actions = Column(JSON, nullable=True)  # List of action specs
    
    # Execution
    status = Column(String(32), nullable=False)
    execution_result = Column(JSON, nullable=True)
    
    # Approval (if needed)
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(String(128), nullable=True)
    
    # Timing
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    context = Column(JSON, nullable=True)


@dataclass
class Intent:
    """Structured representation of user intent"""
    type: str  # e.g., "task.create", "knowledge.search", "code.edit"
    parameters: Dict[str, Any]
    confidence: float = 1.0
    context: Optional[Dict[str, Any]] = None


@dataclass
class Plan:
    """Execution plan from cognition"""
    plan_id: str
    intent_type: str
    actions: List[Dict[str, Any]]  # Structured action specs
    requires_approval: bool = False
    estimated_duration: float = 0.0
    risk_level: str = "low"


@dataclass
class ExecutionResult:
    """Structured result from plan execution"""
    plan_id: str
    success: bool
    actions_completed: int
    actions_failed: int
    outputs: Dict[str, Any]
    verification: Optional[Dict[str, Any]] = None
    rollback_available: bool = False
    confidence: float = 0.0


class CognitionAuthority:
    """
    Central cognition authority that owns all decision-making.
    LLM is relegated to verbalization only.
    """
    
    async def parse_intent(
        self,
        utterance: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Parse user utterance into structured intent.
        Uses lightweight NLU (not full LLM).
        """
        
        # Simple pattern matching for common intents
        # In production, would use NLU model or lightweight classifier
        
        utterance_lower = utterance.lower()
        
        # Task intents
        if any(word in utterance_lower for word in ["task", "todo", "list tasks"]):
            if "create" in utterance_lower or "add" in utterance_lower:
                return Intent(
                    type="task.create",
                    parameters={"title": utterance},
                    confidence=0.8,
                    context=context
                )
            else:
                return Intent(
                    type="task.list",
                    parameters={"status": "in-progress"},
                    confidence=0.9,
                    context=context
                )
        
        # Knowledge intents
        elif any(word in utterance_lower for word in ["search", "find", "lookup", "knowledge"]):
            return Intent(
                type="knowledge.search",
                parameters={"query": utterance},
                confidence=0.85,
                context=context
            )
        
        # Code intents
        elif any(word in utterance_lower for word in ["code", "edit", "fix", "implement"]):
            return Intent(
                type="code.edit",
                parameters={"request": utterance},
                confidence=0.75,
                context=context
            )
        
        # Hunter/security intents
        elif any(word in utterance_lower for word in ["security", "alert", "threat", "hunter"]):
            return Intent(
                type="hunter.check",
                parameters={"scope": "recent"},
                confidence=0.8,
                context=context
            )
        
        # Governance intents
        elif any(word in utterance_lower for word in ["approve", "reject", "policy", "governance"]):
            return Intent(
                type="governance.review",
                parameters={},
                confidence=0.7,
                context=context
            )
        
        # Default: chat intent
        else:
            return Intent(
                type="chat.respond",
                parameters={"message": utterance},
                confidence=0.6,
                context=context
            )
    
    async def create_plan(self, intent: Intent) -> Plan:
        """
        Create execution plan from intent.
        Returns structured plan with actions, not LLM-generated text.
        """
        
        from .capability_registry import capability_registry
        
        # Get capability for this intent type
        capability = capability_registry.get_capability(intent.type)
        
        if not capability:
            # Unknown intent, create minimal plan
            return Plan(
                plan_id=f"plan-{datetime.now(timezone.utc).timestamp()}",
                intent_type=intent.type,
                actions=[{
                    "action": "chat.fallback",
                    "parameters": intent.parameters
                }],
                requires_approval=False
            )
        
        # Build plan from capability definition
        plan_id = f"plan-{datetime.now(timezone.utc).timestamp()}"
        
        actions = []
        for step in capability.get("steps", []):
            actions.append({
                "action": step["action"],
                "parameters": {**step.get("parameters", {}), **intent.parameters},
                "tier": step.get("tier", "tier_1"),
                "timeout": step.get("timeout", 30)
            })
        
        return Plan(
            plan_id=plan_id,
            intent_type=intent.type,
            actions=actions,
            requires_approval=capability.get("requires_approval", False),
            estimated_duration=capability.get("estimated_duration", 1.0),
            risk_level=capability.get("risk_level", "low")
        )
    
    async def execute_plan(
        self,
        plan: Plan,
        session_id: str
    ) -> ExecutionResult:
        """
        Execute plan through agentic safeguards.
        All actions go through autonomy tiers, verification, and logging.
        """
        
        from .action_executor import action_executor
        from .action_contract import ExpectedEffect
        
        outputs = {}
        actions_completed = 0
        actions_failed = 0
        verification_results = []
        
        # Publish plan execution event
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.plan.executing",
            source="cognition",
            actor="cognition_authority",
            resource=plan.plan_id,
            payload={
                "plan_id": plan.plan_id,
                "intent_type": plan.intent_type,
                "action_count": len(plan.actions)
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Execute each action
        for action_spec in plan.actions:
            action_type = action_spec["action"]
            params = action_spec["parameters"]
            tier = action_spec.get("tier", "tier_1")
            
            try:
                # For high-tier actions, use full verification
                if tier in ["tier_2", "tier_3"]:
                    expected_effect = ExpectedEffect(
                        target_resource=action_type,
                        target_state={"status": "completed"},
                        success_criteria=[
                            {"type": "state_match", "key": "status", "value": "completed"}
                        ]
                    )
                    
                    result = await action_executor.execute_verified_action(
                        action_type=action_type,
                        playbook_id=None,
                        run_id=None,
                        expected_effect=expected_effect,
                        baseline_state={"parameters": params},
                        tier=tier,
                        triggered_by=f"cognition:{plan.plan_id}"
                    )
                    
                    if result.get("success"):
                        actions_completed += 1
                    else:
                        actions_failed += 1
                    
                    verification_results.append(result.get("verification", {}))
                    outputs[action_type] = result
                
                else:
                    # Tier 1: Direct execution through capability
                    result = await self._execute_capability(action_type, params)
                    
                    if result.get("ok", True):
                        actions_completed += 1
                    else:
                        actions_failed += 1
                    
                    outputs[action_type] = result
                    
            except Exception as e:
                actions_failed += 1
                outputs[action_type] = {"ok": False, "error": str(e)}
        
        success = (actions_failed == 0)
        
        # Publish completion event
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.plan.completed" if success else "agentic.plan.failed",
            source="cognition",
            actor="cognition_authority",
            resource=plan.plan_id,
            payload={
                "plan_id": plan.plan_id,
                "success": success,
                "actions_completed": actions_completed,
                "actions_failed": actions_failed
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        return ExecutionResult(
            plan_id=plan.plan_id,
            success=success,
            actions_completed=actions_completed,
            actions_failed=actions_failed,
            outputs=outputs,
            verification=verification_results[0] if verification_results else None,
            rollback_available=(len(verification_results) > 0),
            confidence=sum(v.get("confidence", 0) for v in verification_results) / len(verification_results) if verification_results else 0.0
        )
    
    async def _execute_capability(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a capability directly (tier 1 actions)"""
        
        from . import capability_handlers
        
        # Map action to handler
        handler_map = {
            "task.list": capability_handlers.handle_task_list,
            "task.create": capability_handlers.handle_task_create,
            "knowledge.search": capability_handlers.handle_knowledge_search,
            "chat.respond": capability_handlers.handle_chat_respond,
            "verification.status": capability_handlers.handle_verification_status,
            "benchmark.run": capability_handlers.handle_benchmark_run,
        }
        
        handler = handler_map.get(action_type)
        
        if handler:
            return await handler(parameters)
        else:
            return {
                "ok": False,
                "error": f"No handler for capability: {action_type}",
                "action": action_type
            }
    
    async def process_user_request(
        self,
        utterance: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete flow: Parse → Plan → Execute → Return structured result.
        This is what grace.py and CLI should call instead of direct LLM.
        """
        
        session_id = session_id or f"session-{datetime.now(timezone.utc).timestamp()}"
        
        # 1. Parse intent
        intent = await self.parse_intent(utterance, user_id, context={"session_id": session_id})
        
        # Publish intent event
        await trigger_mesh.publish(TriggerEvent(
            event_type="cognition.intent.created",
            source="cognition",
            actor=user_id or "user",
            resource=session_id,
            payload={
                "intent_type": intent.type,
                "parameters": intent.parameters,
                "confidence": intent.confidence
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Save intent to database
        async with async_session() as db_session:
            db_intent = CognitionIntent(
                session_id=session_id,
                raw_utterance=utterance,
                user_id=user_id,
                intent_type=intent.type,
                intent_parameters=intent.parameters,
                confidence_score=int(intent.confidence * 100),
                status=IntentStatus.CREATED.value,
                created_at=datetime.now(timezone.utc)
            )
            db_session.add(db_intent)
            await db_session.commit()
            intent_id = db_intent.id
        
        # 2. Create plan
        plan = await self.create_plan(intent)
        
        # Update intent with plan
        async with async_session() as db_session:
            db_intent = await db_session.get(CognitionIntent, intent_id)
            if db_intent:
                db_intent.plan_id = plan.plan_id
                db_intent.planned_actions = plan.actions
                db_intent.status = IntentStatus.PLANNED.value
                db_intent.requires_approval = plan.requires_approval
                await db_session.commit()
        
        # Publish plan event
        await trigger_mesh.publish(TriggerEvent(
            event_type="agentic.plan.ready",
            source="cognition",
            actor="cognition_authority",
            resource=plan.plan_id,
            payload=asdict(plan),
            timestamp=datetime.now(timezone.utc)
        ))
        
        # 3. Execute plan (if approved or tier 1)
        if plan.requires_approval:
            # Create approval request and wait
            from .autonomy_tiers import autonomy_manager
            
            can_execute, approval_id = await autonomy_manager.can_execute(
                plan.intent_type,
                {"plan": asdict(plan)}
            )
            
            if not can_execute:
                # Update intent status
                async with async_session() as db_session:
                    db_intent = await db_session.get(CognitionIntent, intent_id)
                    if db_intent:
                        db_intent.status = IntentStatus.CREATED.value
                        db_intent.approval_id = approval_id
                        await db_session.commit()
                
                return {
                    "status": "pending_approval",
                    "intent_id": intent_id,
                    "intent_type": intent.type,
                    "plan_id": plan.plan_id,
                    "approval_id": approval_id,
                    "message": "Action requires approval",
                    "requires_approval": True
                }
        
        # Execute
        async with async_session() as db_session:
            db_intent = await db_session.get(CognitionIntent, intent_id)
            if db_intent:
                db_intent.status = IntentStatus.EXECUTING.value
                await db_session.commit()
        
        result = await self.execute_plan(plan, session_id)
        
        # Update intent with result
        async with async_session() as db_session:
            db_intent = await db_session.get(CognitionIntent, intent_id)
            if db_intent:
                db_intent.status = IntentStatus.COMPLETED.value if result.success else IntentStatus.FAILED.value
                db_intent.execution_result = asdict(result)
                db_intent.completed_at = datetime.now(timezone.utc)
                await db_session.commit()
        
        # Return structured result for LLM verbalization
        return {
            "status": "completed" if result.success else "failed",
            "intent_id": intent_id,
            "intent_type": intent.type,
            "plan_id": plan.plan_id,
            "result": asdict(result),
            "structured_output": result.outputs,
            "message": None  # LLM will generate this
        }


# Singleton
cognition_authority = CognitionAuthority()
