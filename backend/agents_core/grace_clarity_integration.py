"""
Clarity Framework Integration with 5W1H Decision Records
Narrative-aware documentation for all coding agent changes

Every change creates a "Grace story" with:
- What: components, models, capabilities affected
- Where: layer/tier, environment
- When: timestamp, SLA, cadence
- Why: telemetry incident, strategic objective
- Who: actor, approvals
- How: step-by-step plan, playbooks, tests

Plus telemetry feedback loop and best practices library.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import json

from backend.execution.immutable_log import immutable_log

logger = logging.getLogger(__name__)


@dataclass
class FiveWOneH:
    """5W1H decision record"""
    # What
    what_component: str
    what_files: List[str]
    what_models: List[str] = field(default_factory=list)
    what_capability: str = ""
    
    # Where
    where_layer: str = ""  # layer1, layer2, layer3
    where_tier: str = ""  # tier1_safe, tier2_internal, tier3_sensitive
    where_environment: str = "production"
    
    # When
    when_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    when_sla_completion: Optional[str] = None
    when_audit_cadence: str = "15_actions"
    
    # Why
    why_telemetry_incident: Optional[str] = None
    why_chaos_signature: Optional[str] = None
    why_strategic_objective: Optional[str] = None
    why_rationale: str = ""
    
    # Who
    who_requesting_actor: str = ""
    who_approvals: List[str] = field(default_factory=list)
    who_governance_tier: str = ""
    
    # How
    how_plan_steps: List[str] = field(default_factory=list)
    how_playbooks_used: List[str] = field(default_factory=list)
    how_tests_run: List[str] = field(default_factory=list)
    how_rollback_plan: Optional[str] = None


@dataclass
class GraceStory:
    """
    Narrative-aware documentation of a change
    
    Tells the story of what capability improved, which kernels/models
    involved, how governance approved it
    """
    story_id: str
    title: str
    
    # 5W1H context
    context: FiveWOneH
    
    # Narrative
    summary: str
    detailed_narrative: str = ""
    
    # Impact
    capabilities_improved: List[str] = field(default_factory=list)
    kernels_affected: List[str] = field(default_factory=list)
    models_involved: List[str] = field(default_factory=list)
    
    # Decision rationale
    expected_benefit: str = ""
    risks_identified: List[str] = field(default_factory=list)
    guardrails_checked: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    
    # Governance
    governance_approval_tier: str = ""
    constitutional_principles: List[str] = field(default_factory=list)
    
    # Results
    outcome: str = "pending"  # pending, success, failed, rolled_back
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    
    # Audit trail
    immutable_log_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TelemetryFeedback:
    """Telemetry feedback after deployment"""
    story_id: str
    
    # KPIs monitored
    self_healing_kpi: Dict[str, float] = field(default_factory=dict)
    governance_audit_metrics: Dict[str, Any] = field(default_factory=dict)
    layer3_intent_success: float = 1.0
    
    # Drift detection
    metric_drifts: List[str] = field(default_factory=list)
    performance_degradation: bool = False
    
    # Auto-fix triggered
    follow_up_fix_needed: bool = False
    follow_up_story_id: Optional[str] = None


@dataclass
class BestPractice:
    """Proven practice from successful changes"""
    practice_id: str
    name: str
    description: str
    
    # Pattern
    pattern_type: str  # playbook, adapter_api, test_suite, telemetry_hook
    code_template: Optional[str] = None
    
    # Success metrics
    times_used: int = 0
    success_rate: float = 1.0
    avg_trust_score: float = 0.9
    
    # Context
    applicable_to: List[str] = field(default_factory=list)  # domains, layers
    not_applicable_to: List[str] = field(default_factory=list)
    
    # References
    source_stories: List[str] = field(default_factory=list)
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ClarityIntegration:
    """
    Clarity Framework integration for coding agent
    
    Features:
    - 5W1H decision records
    - Grace story generation
    - Telemetry feedback loop
    - Best practices library
    """
    
    def __init__(self):
        self.stories: Dict[str, GraceStory] = {}
        self.telemetry_feedback: Dict[str, TelemetryFeedback] = {}
        self.best_practices: Dict[str, BestPractice] = {}
        
        # Storage
        self.storage_dir = Path(__file__).parent.parent.parent / ".grace_stories"
        self.storage_dir.mkdir(exist_ok=True)
        
        # Load existing practices
        self._load_best_practices()
    
    async def create_grace_story(
        self,
        title: str,
        context: FiveWOneH,
        summary: str,
        expected_benefit: str = "",
        risks: List[str] = None,
        alternatives: List[str] = None
    ) -> GraceStory:
        """Create a Grace story for a change"""
        
        story_id = f"story_{len(self.stories)}_{datetime.utcnow().timestamp()}"
        
        story = GraceStory(
            story_id=story_id,
            title=title,
            context=context,
            summary=summary,
            expected_benefit=expected_benefit,
            risks_identified=risks or [],
            alternatives_considered=alternatives or []
        )
        
        # Extract capabilities, kernels, models from context
        story.capabilities_improved = [context.what_capability] if context.what_capability else []
        story.kernels_affected = [f for f in context.what_files if 'kernel' in f.lower()]
        story.models_involved = context.what_models
        
        # Log to immutable log
        log_id = await immutable_log.record(
            actor=context.who_requesting_actor,
            action="grace_story.create",
            result=asdict(story),
            trust_score=0.9
        )
        story.immutable_log_id = log_id
        
        # Store
        self.stories[story_id] = story
        
        # Save to disk
        await self._save_story(story)
        
        logger.info(f"[CLARITY] Created Grace story: {title}")
        
        return story
    
    async def update_story_outcome(
        self,
        story_id: str,
        outcome: str,
        metrics_after: Dict[str, float]
    ):
        """Update story with outcome and metrics"""
        
        story = self.stories.get(story_id)
        if not story:
            return
        
        story.outcome = outcome
        story.metrics_after = metrics_after
        
        # Save
        await self._save_story(story)
        
        # If successful, extract best practices
        if outcome == "success":
            await self._extract_best_practice(story)
    
    async def start_telemetry_monitoring(self, story_id: str):
        """Start monitoring telemetry for a deployed change"""
        
        story = self.stories.get(story_id)
        if not story:
            return
        
        feedback = TelemetryFeedback(story_id=story_id)
        self.telemetry_feedback[story_id] = feedback
        
        # Start background monitoring task
        asyncio.create_task(self._monitor_telemetry(story_id))
        
        logger.info(f"[CLARITY] Started telemetry monitoring for {story_id}")
    
    async def _monitor_telemetry(self, story_id: str):
        """Monitor telemetry and detect drift"""
        
        feedback = self.telemetry_feedback.get(story_id)
        if not feedback:
            return
        
        # Monitor for 24 hours
        for _ in range(24):  # Check every hour
            await asyncio.sleep(3600)
            
            # Collect metrics (in production, query actual telemetry)
            # For now, simulate
            current_metrics = await self._collect_telemetry()
            
            # Check for drift
            story = self.stories.get(story_id)
            if story and story.metrics_after:
                for metric, value in current_metrics.items():
                    if metric in story.metrics_after:
                        baseline = story.metrics_after[metric]
                        drift = abs(value - baseline) / baseline if baseline > 0 else 0
                        
                        if drift > 0.2:  # 20% drift
                            feedback.metric_drifts.append(f"{metric}: {drift:.1%} drift")
                            feedback.performance_degradation = True
                            
                            logger.warning(f"[CLARITY] Metric drift detected in {story_id}: {metric}")
            
            # If drift detected, create follow-up fix
            if feedback.performance_degradation and not feedback.follow_up_fix_needed:
                feedback.follow_up_fix_needed = True
                await self._create_follow_up_fix(story_id, feedback)
                break
    
    async def _collect_telemetry(self) -> Dict[str, float]:
        """Collect current telemetry metrics"""
        
        # In production, query:
        # - Self-healing KPIs (trigger success rate, playbook success, MTTR)
        # - Governance audit logs (approval latency, policy violations)
        # - Layer 3 intent success rate
        
        # Simulated for now
        return {
            "self_healing_success_rate": 0.95,
            "playbook_success_rate": 0.92,
            "governance_approval_latency_ms": 500,
            "layer3_intent_success_rate": 0.88
        }
    
    async def _create_follow_up_fix(self, original_story_id: str, feedback: TelemetryFeedback):
        """Automatically create follow-up fix for drifted metrics"""
        
        logger.warning(f"[CLARITY] Creating follow-up fix for {original_story_id}")
        
        original_story = self.stories.get(original_story_id)
        if not original_story:
            return
        
        # Create new 5W1H context
        followup_context = FiveWOneH(
            what_component=original_story.context.what_component,
            what_files=original_story.context.what_files,
            what_models=original_story.context.what_models,
            where_layer=original_story.context.where_layer,
            why_telemetry_incident=f"Metric drift from {original_story_id}",
            why_rationale=f"Auto-fix for performance degradation: {', '.join(feedback.metric_drifts)}",
            who_requesting_actor="telemetry_monitor",
            how_rollback_plan=f"Revert to state before {original_story_id}"
        )
        
        # Create follow-up story
        followup_story = await self.create_grace_story(
            title=f"Auto-fix for {original_story.title}",
            context=followup_context,
            summary=f"Automatic correction due to metric drift detected in {original_story_id}",
            expected_benefit="Restore performance to baseline",
            risks=["May not address root cause"],
            alternatives=["Manual investigation", "Rollback to previous state"]
        )
        
        feedback.follow_up_story_id = followup_story.story_id
        
        logger.info(f"[CLARITY] Created follow-up story: {followup_story.story_id}")
    
    async def _extract_best_practice(self, story: GraceStory):
        """Extract best practice from successful story"""
        
        if story.outcome != "success":
            return
        
        # Check if this pattern is reusable
        if not story.context.how_playbooks_used and not story.context.how_plan_steps:
            return
        
        practice_id = f"practice_{len(self.best_practices)}_{datetime.utcnow().timestamp()}"
        
        practice = BestPractice(
            practice_id=practice_id,
            name=f"Pattern from: {story.title}",
            description=story.summary,
            pattern_type="playbook" if story.context.how_playbooks_used else "refactor",
            applicable_to=[story.context.where_layer, story.context.what_component],
            source_stories=[story.story_id],
            times_used=1,
            success_rate=1.0,
            avg_trust_score=story.metrics_after.get("trust_score", 0.9)
        )
        
        # Build code template from plan steps
        if story.context.how_plan_steps:
            practice.code_template = "\n".join(f"# {step}" for step in story.context.how_plan_steps)
        
        self.best_practices[practice_id] = practice
        
        logger.info(f"[CLARITY] Extracted best practice: {practice.name}")
        
        # Save
        await self._save_best_practice(practice)
    
    def find_similar_practices(self, context: FiveWOneH) -> List[BestPractice]:
        """Find similar best practices for reuse"""
        
        similar = []
        
        for practice in self.best_practices.values():
            # Check if applicable
            if context.where_layer in practice.applicable_to:
                similar.append(practice)
            elif context.what_component in practice.applicable_to:
                similar.append(practice)
        
        # Sort by success rate
        similar.sort(key=lambda p: p.success_rate * p.avg_trust_score, reverse=True)
        
        return similar[:5]  # Top 5
    
    async def _save_story(self, story: GraceStory):
        """Save story to disk"""
        
        story_file = self.storage_dir / f"{story.story_id}.json"
        
        with open(story_file, 'w') as f:
            json.dump(asdict(story), f, indent=2)
    
    async def _save_best_practice(self, practice: BestPractice):
        """Save best practice to library"""
        
        practices_file = self.storage_dir / "best_practices.json"
        
        all_practices = {}
        if practices_file.exists():
            with open(practices_file, 'r') as f:
                all_practices = json.load(f)
        
        all_practices[practice.practice_id] = asdict(practice)
        
        with open(practices_file, 'w') as f:
            json.dump(all_practices, f, indent=2)
    
    def _load_best_practices(self):
        """Load best practices from library"""
        
        practices_file = self.storage_dir / "best_practices.json"
        
        if not practices_file.exists():
            return
        
        try:
            with open(practices_file, 'r') as f:
                all_practices = json.load(f)
            
            for pid, data in all_practices.items():
                self.best_practices[pid] = BestPractice(**data)
            
            logger.info(f"[CLARITY] Loaded {len(self.best_practices)} best practices")
        
        except Exception as e:
            logger.error(f"[CLARITY] Error loading best practices: {e}")
    
    def get_story(self, story_id: str) -> Optional[GraceStory]:
        """Get a Grace story"""
        return self.stories.get(story_id)
    
    def get_recent_stories(self, limit: int = 10) -> List[GraceStory]:
        """Get recent Grace stories"""
        sorted_stories = sorted(
            self.stories.values(),
            key=lambda s: s.created_at,
            reverse=True
        )
        return sorted_stories[:limit]


# Global Clarity integration
_clarity_integration: Optional[ClarityIntegration] = None


def get_clarity_integration() -> ClarityIntegration:
    """Get or create the global Clarity integration"""
    global _clarity_integration
    
    if _clarity_integration is None:
        _clarity_integration = ClarityIntegration()
    
    return _clarity_integration
