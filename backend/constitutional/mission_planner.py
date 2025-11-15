"""
Mission Planner Service
Breaks mission pillars into actionable OKRs and Layer 3 intents

Feeds high-level goals into executable tasks while maintaining
alignment with Grace's constitutional charter.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .grace_charter import get_grace_charter, MissionPillar
from backend.agents_core.grace_clarity_integration import get_clarity_integration, FiveWOneH

logger = logging.getLogger(__name__)


@dataclass
class MissionTask:
    """Actionable task derived from mission OKRs"""
    task_id: str
    pillar: MissionPillar
    okr_id: str
    
    # Task details
    title: str
    description: str
    operation: str  # learn_domain, build_business, design_system, etc.
    
    # Layer 3 intent
    layer3_intent: str  # knowledge.learn, business.create, etc.
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    measurable_kpi: Optional[str] = None
    target_value: Optional[float] = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Execution
    status: str = "pending"  # pending, in_progress, completed, blocked
    assigned_to: str = "grace"
    priority: int = 0
    
    # Results
    outcome: Optional[str] = None
    metrics_achieved: Dict[str, float] = field(default_factory=dict)
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MissionPlanner:
    """
    Mission planner service
    
    Responsibilities:
    - Break OKRs into actionable tasks
    - Generate Layer 3 intents from mission goals
    - Track progress toward mission pillars
    - Unlock higher autonomy tiers as KPIs are met
    - Log all planning to Clarity with 5W1H
    """
    
    def __init__(self):
        self.charter = get_grace_charter()
        self.clarity = get_clarity_integration()
        
        # Task queue
        self.tasks: Dict[str, MissionTask] = {}
        
        # Autonomy levels tied to mission progress
        self.autonomy_levels = {
            "base": 1,  # Current level
            "unlocked_at": {},  # Pillar -> autonomy level unlocked
            "thresholds": {
                MissionPillar.KNOWLEDGE_APPLICATION: 2,  # Unlock Tier 2
                MissionPillar.BUSINESS_REVENUE: 3,  # Unlock Tier 3
                MissionPillar.RENEWABLE_ENERGY: 4,  # Unlock advanced autonomy
            }
        }
        
        # Statistics
        self.stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "pillars_unlocked": 1,  # Knowledge is always unlocked
            "current_autonomy_level": 1
        }
    
    async def generate_mission_tasks(self, pillar: MissionPillar) -> List[MissionTask]:
        """Generate actionable tasks from a mission pillar's OKRs"""
        
        pillar_status = self.charter.get_pillar_status(pillar)
        
        if not pillar_status["enabled"]:
            logger.warning(f"[MISSION PLANNER] Pillar {pillar.value} not yet unlocked")
            return []
        
        logger.info(f"[MISSION PLANNER] Generating tasks for {pillar_status['name']}")
        
        tasks = []
        
        # Get OKRs for this pillar
        okrs = [okr for okr in self.charter.okrs.values() if okr.pillar == pillar]
        
        for okr in okrs:
            # Generate tasks from key results
            for i, kr in enumerate(okr.key_results):
                task = await self._create_task_from_key_result(
                    pillar=pillar,
                    okr_id=okr.okr_id,
                    key_result=kr,
                    index=i
                )
                
                if task:
                    tasks.append(task)
                    self.tasks[task.task_id] = task
        
        self.stats["tasks_created"] += len(tasks)
        
        logger.info(f"[MISSION PLANNER] Created {len(tasks)} tasks for {pillar.value}")
        
        return tasks
    
    async def _create_task_from_key_result(
        self,
        pillar: MissionPillar,
        okr_id: str,
        key_result: Dict[str, Any],
        index: int
    ) -> Optional[MissionTask]:
        """Create a mission task from a key result"""
        
        kr_text = key_result["kr"]
        
        task_id = f"mission_{pillar.value}_{okr_id}_{index}"
        
        # Determine operation and Layer 3 intent based on pillar
        if pillar == MissionPillar.KNOWLEDGE_APPLICATION:
            operation = "learn_domain"
            layer3_intent = "knowledge.learn"
            description = f"Learn and master domain to achieve: {kr_text}"
        
        elif pillar == MissionPillar.BUSINESS_REVENUE:
            operation = "build_business"
            layer3_intent = "business.create"
            description = f"Build business capability: {kr_text}"
        
        elif pillar == MissionPillar.RENEWABLE_ENERGY:
            operation = "design_energy_system"
            layer3_intent = "energy.design"
            description = f"Design renewable energy solution: {kr_text}"
        
        elif pillar == MissionPillar.QUANTUM_INFRASTRUCTURE:
            operation = "build_quantum_stack"
            layer3_intent = "quantum.build"
            description = f"Build quantum infrastructure: {kr_text}"
        
        elif pillar == MissionPillar.ATLANTIS_WAKANDA:
            operation = "design_ecosystem"
            layer3_intent = "ecosystem.design"
            description = f"Design Atlantis/Wakanda ecosystem: {kr_text}"
        
        elif pillar == MissionPillar.COHABITATION_INNOVATION:
            operation = "foster_collaboration"
            layer3_intent = "collab.innovate"
            description = f"Foster AI-human collaboration: {kr_text}"
        
        elif pillar == MissionPillar.SCIENCE_BEYOND_LIMITS:
            operation = "explore_science"
            layer3_intent = "science.explore"
            description = f"Push scientific boundaries: {kr_text}"
        
        else:
            return None
        
        task = MissionTask(
            task_id=task_id,
            pillar=pillar,
            okr_id=okr_id,
            title=kr_text,
            description=description,
            operation=operation,
            layer3_intent=layer3_intent,
            target_value=key_result.get("target"),
            priority=self.charter.pillars[pillar]["priority"]
        )
        
        return task
    
    async def execute_mission_task(self, task_id: str, actor: str = "grace") -> Dict[str, Any]:
        """Execute a mission task and log to Clarity"""
        
        task = self.tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        logger.info(f"[MISSION PLANNER] Executing task: {task.title}")
        
        task.status = "in_progress"
        task.assigned_to = actor
        
        # Create 5W1H context for Clarity
        context = FiveWOneH(
            what_component=task.pillar.value,
            what_files=[],
            what_capability=task.operation,
            where_layer="mission_planning",
            where_environment="strategic",
            why_strategic_objective=f"Advance {task.pillar.value} mission pillar",
            why_rationale=task.description,
            who_requesting_actor=actor,
            who_governance_tier="mission_planner",
            how_plan_steps=[task.description]
        )
        
        # Create Grace story
        story = await self.clarity.create_grace_story(
            title=f"Mission Task: {task.title}",
            context=context,
            summary=f"Executing mission task for {task.pillar.value}",
            expected_benefit=f"Progress toward {task.pillar.value} goals"
        )
        
        # Simulate execution (in production, route to appropriate subsystem)
        task.status = "completed"
        task.outcome = "success"
        
        # Update charter metrics
        if task.measurable_kpi and task.target_value:
            self.charter.update_metrics(
                pillar=task.pillar,
                metrics={task.measurable_kpi: task.target_value}
            )
        
        # Update story outcome
        await self.clarity.update_story_outcome(
            story_id=story.story_id,
            outcome="success",
            metrics_after=task.metrics_achieved
        )
        
        self.stats["tasks_completed"] += 1
        
        # Check if autonomy should be unlocked
        await self._check_autonomy_unlock(task.pillar)
        
        logger.info(f"[MISSION PLANNER] Task completed: {task.title}")
        
        return {
            "success": True,
            "task_id": task_id,
            "outcome": task.outcome,
            "story_id": story.story_id
        }
    
    async def _check_autonomy_unlock(self, pillar: MissionPillar):
        """Check if completing this pillar unlocks higher autonomy"""
        
        if pillar not in self.autonomy_levels["thresholds"]:
            return
        
        # Check if pillar's blocking clauses are satisfied
        pillar_clauses = [c for c in self.charter.clauses.values() if c.pillar == pillar and c.blocking]
        
        all_satisfied = all(c.satisfied for c in pillar_clauses)
        
        if all_satisfied and pillar not in self.autonomy_levels["unlocked_at"]:
            new_level = self.autonomy_levels["thresholds"][pillar]
            self.autonomy_levels["unlocked_at"][pillar] = new_level
            self.autonomy_levels["base"] = max(self.autonomy_levels["base"], new_level)
            
            self.stats["current_autonomy_level"] = self.autonomy_levels["base"]
            
            logger.info(f"[MISSION PLANNER] 🎉 AUTONOMY UNLOCKED: Level {new_level} (completed {pillar.value})")
    
    def get_active_tasks(self, pillar: Optional[MissionPillar] = None) -> List[MissionTask]:
        """Get active mission tasks"""
        
        active = [t for t in self.tasks.values() if t.status in ["pending", "in_progress"]]
        
        if pillar:
            active = [t for t in active if t.pillar == pillar]
        
        # Sort by priority
        active.sort(key=lambda t: t.priority)
        
        return active
    
    def get_mission_progress(self) -> Dict[str, Any]:
        """Get overall mission progress"""
        
        progress = {
            "overall_completion": 0.0,
            "pillars": {},
            "autonomy_level": self.autonomy_levels["base"],
            "tasks_completed": self.stats["tasks_completed"],
            "tasks_pending": len([t for t in self.tasks.values() if t.status == "pending"])
        }
        
        # Calculate per-pillar progress
        for pillar in MissionPillar:
            pillar_status = self.charter.get_pillar_status(pillar)
            
            # Count satisfied clauses
            total_clauses = len(pillar_status["clauses"])
            satisfied_clauses = len([c for c in pillar_status["clauses"] if c["satisfied"]])
            
            pillar_completion = satisfied_clauses / total_clauses if total_clauses > 0 else 0.0
            
            progress["pillars"][pillar.value] = {
                "enabled": pillar_status["enabled"],
                "completion": pillar_completion,
                "clauses_satisfied": f"{satisfied_clauses}/{total_clauses}",
                "priority": pillar_status["priority"]
            }
        
        # Overall completion (average of enabled pillars)
        enabled_completions = [
            p["completion"] for p in progress["pillars"].values() if p["enabled"]
        ]
        
        if enabled_completions:
            progress["overall_completion"] = sum(enabled_completions) / len(enabled_completions)
        
        return progress
    
    async def plan_next_quarter(self) -> Dict[str, Any]:
        """Generate mission plan for next quarter"""
        
        logger.info("[MISSION PLANNER] Planning next quarter...")
        
        plan = {
            "quarter": "Q1 2025",
            "focus_pillars": [],
            "tasks": [],
            "autonomy_targets": []
        }
        
        # Get enabled pillars
        for pillar in MissionPillar:
            status = self.charter.get_pillar_status(pillar)
            
            if status["enabled"]:
                plan["focus_pillars"].append(pillar.value)
                
                # Generate tasks for this pillar
                tasks = await self.generate_mission_tasks(pillar)
                plan["tasks"].extend([t.task_id for t in tasks])
        
        logger.info(f"[MISSION PLANNER] Quarterly plan: {len(plan['tasks'])} tasks across {len(plan['focus_pillars'])} pillars")
        
        return plan


# Global mission planner
_mission_planner: Optional[MissionPlanner] = None


async def get_mission_planner() -> MissionPlanner:
    """Get or create the global mission planner"""
    global _mission_planner
    
    if _mission_planner is None:
        _mission_planner = MissionPlanner()
        logger.info("[MISSION PLANNER] Initialized mission planner")
    
    return _mission_planner
