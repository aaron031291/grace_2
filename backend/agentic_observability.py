"""
Agentic Observability - Transparent view into autonomous decisions

Surfaces what the agent sensed, diagnosed, planned, checked, and executed
without overwhelming with internal details. Provides auditable trail of
agentic behavior for humans to understand, monitor, and intervene.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, select
from sqlalchemy.sql import func

from .models import Base, async_session
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class DecisionPhase(Enum):
    SENSING = "sensing"
    DIAGNOSIS = "diagnosis"
    PLANNING = "planning"
    GUARDRAIL_CHECK = "guardrail_check"
    APPROVAL = "approval"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETION = "completion"


class InsightVerbosity(Enum):
    MINIMAL = "minimal"          # Just outcomes
    SUMMARY = "summary"          # Key decisions only
    DETAILED = "detailed"        # Full decision trail
    DEBUG = "debug"              # Everything


@dataclass
class AgenticDecisionPoint:
    """Single decision point in the agentic flow"""
    point_id: str
    run_id: str
    phase: DecisionPhase
    timestamp: datetime
    what_happened: str
    why: str
    confidence: float
    options_considered: List[str]
    chosen_option: str
    guardrails_checked: List[str]
    guardrails_passed: bool
    risk_score: float
    human_approval_required: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgenticInsight(Base):
    """Compact agentic decision ledger"""
    __tablename__ = "agentic_insights"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), nullable=False, index=True)
    phase = Column(String(32), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # What the agent perceived
    signal_type = Column(String(64))
    signal_summary = Column(String(256))
    
    # What the agent diagnosed
    diagnosis = Column(String(256))
    root_cause = Column(String(256))
    
    # What the agent planned
    plan_type = Column(String(64))
    plan_summary = Column(String(512))
    
    # Guardrails and trust
    guardrails_checked = Column(Text)
    guardrails_passed = Column(Boolean)
    risk_score = Column(Float)
    confidence = Column(Float)
    
    # Decision rationale
    rationale = Column(Text)
    options_considered = Column(Text)
    chosen_option = Column(String(256))
    
    # Approval and execution
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String(64))
    approved_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    
    # Outcome
    outcome = Column(String(64))
    outcome_detail = Column(Text)
    verified = Column(Boolean)
    
    # Privacy and metadata
    sensitive_data_redacted = Column(Boolean, default=False)
    metadata = Column(Text)


class AgenticInsightCapture:
    """Captures agentic decision points for observability"""
    
    def __init__(self):
        self.verbosity = InsightVerbosity.SUMMARY
        self.active_runs: Dict[str, Dict] = {}
        self.privacy_filters = ["password", "token", "secret", "key", "credential"]
    
    async def start_run(
        self,
        run_id: str,
        trigger_event: TriggerEvent,
        context: Dict[str, Any]
    ):
        """Start tracking an agentic run"""
        
        self.active_runs[run_id] = {
            "run_id": run_id,
            "started_at": datetime.utcnow(),
            "trigger_event": trigger_event,
            "context": self._redact_sensitive(context),
            "phases": [],
            "current_phase": None
        }
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.SENSING,
            signal_type=trigger_event.event_type,
            signal_summary=f"{trigger_event.source}: {trigger_event.event_type}",
            metadata={"resource": trigger_event.resource}
        )
    
    async def record_diagnosis(
        self,
        run_id: str,
        diagnosis: str,
        root_cause: Optional[str],
        confidence: float
    ):
        """Record agent's diagnosis"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.DIAGNOSIS,
            diagnosis=diagnosis,
            root_cause=root_cause or "unknown",
            confidence=confidence,
            rationale=f"Diagnosed based on {confidence:.0%} confidence"
        )
    
    async def record_plan(
        self,
        run_id: str,
        plan_type: str,
        plan_summary: str,
        options_considered: List[str],
        chosen_option: str,
        rationale: str
    ):
        """Record agent's recovery plan"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.PLANNING,
            plan_type=plan_type,
            plan_summary=plan_summary,
            options_considered="\n".join(options_considered),
            chosen_option=chosen_option,
            rationale=rationale
        )
    
    async def record_guardrail_check(
        self,
        run_id: str,
        guardrails: List[str],
        passed: bool,
        risk_score: float,
        approval_required: bool
    ):
        """Record guardrail validation"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.GUARDRAIL_CHECK,
            guardrails_checked="\n".join(guardrails),
            guardrails_passed=passed,
            risk_score=risk_score,
            approval_required=approval_required,
            rationale=f"Risk score: {risk_score:.2f}, Guardrails: {'✓ passed' if passed else '✗ failed'}"
        )
    
    async def record_approval(
        self,
        run_id: str,
        approved_by: str,
        approved: bool,
        notes: str = ""
    ):
        """Record human approval"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.APPROVAL,
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            rationale=f"{'Approved' if approved else 'Rejected'} by {approved_by}: {notes}"
        )
    
    async def record_execution(
        self,
        run_id: str,
        action_taken: str,
        outcome: str
    ):
        """Record execution of plan"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.EXECUTION,
            executed_at=datetime.utcnow(),
            outcome=outcome,
            rationale=f"Executed: {action_taken}"
        )
    
    async def record_verification(
        self,
        run_id: str,
        verified: bool,
        outcome_detail: str
    ):
        """Record verification of outcome"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.VERIFICATION,
            verified=verified,
            outcome_detail=outcome_detail,
            rationale=f"Verification: {'✓ success' if verified else '✗ failed'}"
        )
    
    async def complete_run(
        self,
        run_id: str,
        final_outcome: str,
        success: bool
    ):
        """Complete an agentic run"""
        
        await self._capture_insight(
            run_id=run_id,
            phase=DecisionPhase.COMPLETION,
            outcome="success" if success else "failed",
            outcome_detail=final_outcome,
            verified=success
        )
        
        if run_id in self.active_runs:
            run = self.active_runs[run_id]
            duration = (datetime.utcnow() - run["started_at"]).total_seconds()
            
            await immutable_log.append(
                actor="agentic_observability",
                action="run_completed",
                resource=run_id,
                subsystem="agentic_observability",
                payload={
                    "duration_seconds": duration,
                    "outcome": final_outcome,
                    "success": success
                },
                result="completed"
            )
            
            del self.active_runs[run_id]
    
    async def _capture_insight(self, run_id: str, phase: DecisionPhase, **kwargs):
        """Capture insight to database"""
        
        if self.verbosity == InsightVerbosity.MINIMAL and phase not in [
            DecisionPhase.COMPLETION, DecisionPhase.VERIFICATION
        ]:
            return
        
        async with async_session() as session:
            insight = AgenticInsight(
                run_id=run_id,
                phase=phase.value,
                **kwargs
            )
            
            session.add(insight)
            await session.commit()
        
        await trigger_mesh.publish(TriggerEvent(
            event_type=f"agentic.insight.{phase.value}",
            source="agentic_observability",
            actor="grace_agent",
            resource=run_id,
            payload={
                "phase": phase.value,
                "run_id": run_id,
                **kwargs
            },
            timestamp=datetime.utcnow()
        ))
    
    def _redact_sensitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information"""
        
        redacted = {}
        for key, value in data.items():
            if any(filter_word in key.lower() for filter_word in self.privacy_filters):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive(value)
            else:
                redacted[key] = value
        
        return redacted


class AgenticReadModels:
    """Read models for querying agentic insights"""
    
    async def get_active_runs(self) -> List[Dict[str, Any]]:
        """Get currently active agentic runs"""
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticInsight)
                .where(AgenticInsight.outcome == None)
                .order_by(AgenticInsight.timestamp.desc())
            )
            insights = result.scalars().all()
            
            runs = {}
            for insight in insights:
                if insight.run_id not in runs:
                    runs[insight.run_id] = {
                        "run_id": insight.run_id,
                        "started_at": insight.timestamp,
                        "current_phase": insight.phase,
                        "signal": insight.signal_summary,
                        "plan": insight.plan_summary,
                        "risk_score": insight.risk_score,
                        "approval_required": insight.approval_required
                    }
            
            return list(runs.values())
    
    async def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """Get detailed trace of a specific run"""
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticInsight)
                .where(AgenticInsight.run_id == run_id)
                .order_by(AgenticInsight.timestamp)
            )
            insights = result.scalars().all()
            
            if not insights:
                return None
            
            return {
                "run_id": run_id,
                "started_at": insights[0].timestamp,
                "phases": [
                    {
                        "phase": i.phase,
                        "timestamp": i.timestamp,
                        "what": i.signal_summary or i.plan_summary or i.outcome_detail,
                        "why": i.rationale,
                        "confidence": i.confidence,
                        "risk_score": i.risk_score,
                        "guardrails_passed": i.guardrails_passed,
                        "approved_by": i.approved_by
                    }
                    for i in insights
                ],
                "outcome": insights[-1].outcome if insights else None,
                "verified": insights[-1].verified if insights else None
            }
    
    async def get_recent_decisions(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent agentic decisions"""
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticInsight)
                .where(
                    AgenticInsight.timestamp >= cutoff,
                    AgenticInsight.phase == DecisionPhase.COMPLETION.value
                )
                .order_by(AgenticInsight.timestamp.desc())
                .limit(limit)
            )
            insights = result.scalars().all()
            
            return [
                {
                    "run_id": i.run_id,
                    "timestamp": i.timestamp,
                    "signal": i.signal_summary,
                    "plan": i.plan_summary,
                    "outcome": i.outcome,
                    "success": i.verified,
                    "risk_score": i.risk_score
                }
                for i in insights
            ]
    
    async def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get runs awaiting human approval"""
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticInsight)
                .where(
                    AgenticInsight.approval_required == True,
                    AgenticInsight.approved_by == None,
                    AgenticInsight.outcome == None
                )
                .order_by(AgenticInsight.timestamp.desc())
            )
            insights = result.scalars().all()
            
            return [
                {
                    "run_id": i.run_id,
                    "timestamp": i.timestamp,
                    "plan": i.plan_summary,
                    "risk_score": i.risk_score,
                    "rationale": i.rationale
                }
                for i in insights
            ]
    
    async def get_statistics(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get agentic performance statistics"""
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(AgenticInsight)
                .where(
                    AgenticInsight.timestamp >= cutoff,
                    AgenticInsight.phase == DecisionPhase.COMPLETION.value
                )
            )
            insights = result.scalars().all()
            
            total = len(insights)
            successful = sum(1 for i in insights if i.verified)
            avg_risk = sum(i.risk_score or 0 for i in insights) / total if total > 0 else 0
            
            required_approval = sum(1 for i in insights if i.approval_required)
            autonomous = total - required_approval
            
            return {
                "total_runs": total,
                "successful_runs": successful,
                "success_rate": successful / total if total > 0 else 0,
                "average_risk_score": avg_risk,
                "autonomous_decisions": autonomous,
                "autonomy_rate": autonomous / total if total > 0 else 0,
                "pending_approvals": len(await self.get_pending_approvals())
            }


class AgenticDashboard:
    """Dashboard data structures for ops visibility"""
    
    def __init__(self, read_models: AgenticReadModels):
        self.read_models = read_models
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get complete dashboard summary"""
        
        return {
            "current_state": await self._get_current_state(),
            "active_runs": await self.read_models.get_active_runs(),
            "pending_approvals": await self.read_models.get_pending_approvals(),
            "recent_decisions": await self.read_models.get_recent_decisions(hours=6, limit=10),
            "statistics_24h": await self.read_models.get_statistics(hours=24),
            "statistics_7d": await self.read_models.get_statistics(hours=168)
        }
    
    async def _get_current_state(self) -> Dict[str, Any]:
        """Get current agentic state"""
        
        active_runs = await self.read_models.get_active_runs()
        pending_approvals = await self.read_models.get_pending_approvals()
        
        return {
            "status": "active" if active_runs else "idle",
            "active_run_count": len(active_runs),
            "pending_approval_count": len(pending_approvals),
            "highest_risk_run": max(
                [r.get("risk_score", 0) for r in active_runs],
                default=0
            )
        }
    
    async def get_run_timeline(self, run_id: str) -> Dict[str, Any]:
        """Get visual timeline of a run"""
        
        details = await self.read_models.get_run_details(run_id)
        if not details:
            return None
        
        timeline = []
        for phase in details["phases"]:
            timeline.append({
                "time": phase["timestamp"].isoformat(),
                "phase": phase["phase"],
                "label": self._phase_label(phase),
                "status": self._phase_status(phase),
                "details": {
                    "what": phase["what"],
                    "why": phase["why"],
                    "confidence": phase["confidence"],
                    "risk": phase["risk_score"]
                }
            })
        
        return {
            "run_id": run_id,
            "timeline": timeline,
            "outcome": details["outcome"],
            "duration_seconds": (
                details["phases"][-1]["timestamp"] - details["phases"][0]["timestamp"]
            ).total_seconds() if details["phases"] else 0
        }
    
    def _phase_label(self, phase: Dict) -> str:
        """Human-readable phase label"""
        labels = {
            "sensing": "📡 Detected signal",
            "diagnosis": "🔍 Diagnosed issue",
            "planning": "📋 Planned response",
            "guardrail_check": "🛡️ Checked guardrails",
            "approval": "✋ Awaiting approval",
            "execution": "⚡ Executing plan",
            "verification": "✅ Verifying outcome",
            "completion": "🎯 Completed"
        }
        return labels.get(phase["phase"], phase["phase"])
    
    def _phase_status(self, phase: Dict) -> str:
        """Status indicator for phase"""
        if phase["phase"] == "approval" and not phase["approved_by"]:
            return "pending"
        elif phase["phase"] == "guardrail_check" and not phase["guardrails_passed"]:
            return "blocked"
        elif phase["phase"] == "verification" and not phase.get("verified"):
            return "failed"
        else:
            return "success"


class AgenticObservability:
    """Main agentic observability coordinator"""
    
    def __init__(self):
        self.capture = AgenticInsightCapture()
        self.read_models = AgenticReadModels()
        self.dashboard = AgenticDashboard(self.read_models)
        self.running = False
    
    async def start(self):
        """Start agentic observability"""
        
        await trigger_mesh.subscribe("agentic.run.*", self._handle_run_event)
        
        self.running = True
        print("✓ Agentic Observability started - Transparent decision tracking")
    
    async def stop(self):
        """Stop agentic observability"""
        self.running = False
    
    async def _handle_run_event(self, event: TriggerEvent):
        """Handle agentic run events"""
        pass
    
    async def set_verbosity(self, level: InsightVerbosity):
        """Set observability verbosity level"""
        self.capture.verbosity = level
        print(f"✓ Agentic observability verbosity set to: {level.value}")
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """Get dashboard summary"""
        return await self.dashboard.get_dashboard_summary()
    
    async def get_run_trace(self, run_id: str) -> Dict[str, Any]:
        """Get detailed trace of a run"""
        return await self.read_models.get_run_details(run_id)


agentic_observability = AgenticObservability()
