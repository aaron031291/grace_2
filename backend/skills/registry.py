"""
Skill Registry - Central registry for all Grace skills
Provides uniform interface for agent actions with tracing and governance
"""

import asyncio
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

from backend.event_bus import event_bus, Event, EventType
from backend.action_gateway import action_gateway

class SkillCategory(Enum):
    MEMORY = "memory"
    CODE = "code"
    WEB = "web"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"

@dataclass
class SkillResult:
    """Result of skill execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    execution_time_ms: float = 0.0

@dataclass
class Skill:
    """
    Skill definition with schema and execution
    """
    name: str
    category: SkillCategory
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable
    governance_action_type: str
    timeout_seconds: int = 30
    max_retries: int = 2
    capability_tags: List[str] = field(default_factory=list)
    
    async def execute(
        self,
        agent: str,
        params: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> SkillResult:
        """
        Execute skill with governance, tracing, and error handling
        """
        start_time = datetime.now()
        trace_id = trace_id or f"skill_{self.name}_{start_time.timestamp()}"
        
        approval = await action_gateway.request_action(
            action_type=self.governance_action_type,
            agent=agent,
            params=params,
            trace_id=trace_id
        )
        
        if not approval["approved"]:
            return SkillResult(
                success=False,
                result=None,
                error=f"Governance denied: {approval['reason']}",
                trace_id=trace_id,
                execution_time_ms=0.0
            )
        
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source=agent,
            data={
                "skill": self.name,
                "params": params,
                "governance_approved": True
            },
            trace_id=trace_id
        ))
        
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                if asyncio.iscoroutinefunction(self.handler):
                    result = await asyncio.wait_for(
                        self.handler(params),
                        timeout=self.timeout_seconds
                    )
                else:
                    result = self.handler(params)
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                skill_result = SkillResult(
                    success=True,
                    result=result,
                    trace_id=trace_id,
                    execution_time_ms=execution_time,
                    metadata={
                        "retries": retries,
                        "skill": self.name,
                        "agent": agent
                    }
                )
                
                await action_gateway.record_outcome(
                    trace_id=trace_id,
                    success=True,
                    result=result
                )
                
                return skill_result
                
            except asyncio.TimeoutError:
                last_error = f"Skill timed out after {self.timeout_seconds}s"
                retries += 1
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries > self.max_retries:
                    break
                await asyncio.sleep(0.5 * retries)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        skill_result = SkillResult(
            success=False,
            result=None,
            error=last_error,
            trace_id=trace_id,
            execution_time_ms=execution_time,
            metadata={
                "retries": retries,
                "skill": self.name,
                "agent": agent
            }
        )
        
        await action_gateway.record_outcome(
            trace_id=trace_id,
            success=False,
            result=None,
            error=last_error
        )
        
        return skill_result

class SkillRegistry:
    """
    Central registry for all Grace skills
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
    
    def register(self, skill: Skill) -> None:
        """Register a skill"""
        self.skills[skill.name] = skill
        self.execution_stats[skill.name] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time_ms": 0.0,
            "avg_execution_time_ms": 0.0
        }
        print(f"[SkillRegistry] Registered skill: {skill.name} ({skill.category.value})")
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        return self.skills.get(name)
    
    def list_skills(
        self,
        category: Optional[SkillCategory] = None,
        capability_tag: Optional[str] = None
    ) -> List[Skill]:
        """List skills, optionally filtered"""
        skills = list(self.skills.values())
        
        if category:
            skills = [s for s in skills if s.category == category]
        
        if capability_tag:
            skills = [s for s in skills if capability_tag in s.capability_tags]
        
        return skills
    
    async def execute_skill(
        self,
        skill_name: str,
        agent: str,
        params: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> SkillResult:
        """Execute a skill by name"""
        skill = self.get_skill(skill_name)
        
        if not skill:
            return SkillResult(
                success=False,
                result=None,
                error=f"Skill '{skill_name}' not found",
                trace_id=trace_id
            )
        
        result = await skill.execute(agent, params, trace_id)
        
        stats = self.execution_stats[skill_name]
        stats["total_executions"] += 1
        if result.success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
        stats["total_execution_time_ms"] += result.execution_time_ms
        stats["avg_execution_time_ms"] = (
            stats["total_execution_time_ms"] / stats["total_executions"]
        )
        
        return result
    
    def get_stats(self, skill_name: Optional[str] = None) -> Dict[str, Any]:
        """Get execution statistics"""
        if skill_name:
            return self.execution_stats.get(skill_name, {})
        return self.execution_stats

skill_registry = SkillRegistry()
