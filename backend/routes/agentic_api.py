"""
Agentic API - Observability endpoints for Grace's agentic organism
View events, actions, reflections, and skill execution stats
"""

from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.event_bus import event_bus
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop
from backend.skills.registry import skill_registry

router = APIRouter(prefix="/api/agentic", tags=["agentic"])

@router.get("/events")
async def get_events(
    limit: int = Query(50, ge=1, le=1000),
    event_type: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent events from the Event Bus
    
    Args:
        limit: Maximum number of events to return
        event_type: Filter by event type (optional)
        trace_id: Filter by trace ID (optional)
    """
    events = event_bus.event_log[-limit:]
    
    if event_type:
        events = [e for e in events if e.event_type.value == event_type]
    
    if trace_id:
        events = [e for e in events if e.trace_id == trace_id]
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "source": e.source,
                "timestamp": e.timestamp.isoformat(),
                "trace_id": e.trace_id,
                "data": e.data
            }
            for e in events
        ],
        "count": len(events),
        "total_in_log": len(event_bus.event_log)
    }

@router.get("/actions")
async def get_actions(
    limit: int = Query(50, ge=1, le=1000),
    agent: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent actions from the Action Gateway
    
    Args:
        limit: Maximum number of actions to return
        agent: Filter by agent name (optional)
        trace_id: Filter by trace ID (optional)
    """
    actions = action_gateway.action_log[-limit:]
    
    if agent:
        actions = [a for a in actions if a.get("agent") == agent]
    
    if trace_id:
        actions = [a for a in actions if a.get("trace_id") == trace_id]
    
    return {
        "actions": actions,
        "count": len(actions),
        "total_in_log": len(action_gateway.action_log)
    }

@router.get("/reflections")
async def get_reflections(
    limit: int = Query(50, ge=1, le=1000),
    agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent reflections from the Reflection Loop
    
    Args:
        limit: Maximum number of reflections to return
        agent: Filter by agent name (optional)
    """
    reflections = reflection_loop.reflections[-limit:]
    
    if agent:
        reflections = [r for r in reflections if r.get("agent") == agent]
    
    return {
        "reflections": reflections,
        "count": len(reflections),
        "total_reflections": len(reflection_loop.reflections)
    }

@router.get("/trust_scores")
async def get_trust_scores() -> Dict[str, Any]:
    """
    Get trust scores for all agent/action combinations
    """
    return {
        "trust_scores": reflection_loop.trust_scores,
        "count": len(reflection_loop.trust_scores)
    }

@router.get("/strategy_updates")
async def get_strategy_updates(
    limit: int = Query(20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get recent strategy updates from the Reflection Loop
    """
    updates = reflection_loop.strategy_updates[-limit:]
    
    return {
        "strategy_updates": updates,
        "count": len(updates),
        "total_updates": len(reflection_loop.strategy_updates)
    }

@router.get("/skills")
async def list_skills(
    category: Optional[str] = None,
    capability_tag: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all registered skills
    
    Args:
        category: Filter by category (optional)
        capability_tag: Filter by capability tag (optional)
    """
    from backend.skills.registry import SkillCategory
    
    category_enum = None
    if category:
        try:
            category_enum = SkillCategory(category)
        except ValueError:
            pass
    
    skills = skill_registry.list_skills(
        category=category_enum,
        capability_tag=capability_tag
    )
    
    return {
        "skills": [
            {
                "name": s.name,
                "category": s.category.value,
                "description": s.description,
                "governance_action_type": s.governance_action_type,
                "timeout_seconds": s.timeout_seconds,
                "max_retries": s.max_retries,
                "capability_tags": s.capability_tags,
                "input_schema": s.input_schema,
                "output_schema": s.output_schema
            }
            for s in skills
        ],
        "count": len(skills)
    }

@router.get("/skills/{skill_name}/stats")
async def get_skill_stats(skill_name: str) -> Dict[str, Any]:
    """
    Get execution statistics for a specific skill
    """
    stats = skill_registry.get_stats(skill_name)
    
    if not stats:
        return {
            "error": f"Skill '{skill_name}' not found",
            "skill_name": skill_name
        }
    
    return {
        "skill_name": skill_name,
        "stats": stats
    }

@router.get("/skills/stats")
async def get_all_skill_stats() -> Dict[str, Any]:
    """
    Get execution statistics for all skills
    """
    return {
        "stats": skill_registry.get_stats(),
        "total_skills": len(skill_registry.skills)
    }

@router.get("/health")
async def agentic_health() -> Dict[str, Any]:
    """
    Get health status of the agentic organism
    """
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "event_bus": {
                "status": "operational",
                "total_events": len(event_bus.event_log),
                "subscribers": len(event_bus.subscribers)
            },
            "action_gateway": {
                "status": "operational",
                "total_actions": len(action_gateway.action_log),
                "governance_rules": len(action_gateway.governance_rules)
            },
            "reflection_loop": {
                "status": "operational",
                "total_reflections": len(reflection_loop.reflections),
                "trust_scores": len(reflection_loop.trust_scores)
            },
            "skill_registry": {
                "status": "operational",
                "total_skills": len(skill_registry.skills)
            }
        }
    }

@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Get all events, actions, and reflections for a specific trace ID
    """
    events = [e for e in event_bus.event_log if e.trace_id == trace_id]
    actions = [a for a in action_gateway.action_log if a.get("trace_id") == trace_id]
    reflections = [r for r in reflection_loop.reflections if r.get("trace_id") == trace_id]
    
    return {
        "trace_id": trace_id,
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "source": e.source,
                "timestamp": e.timestamp.isoformat(),
                "data": e.data
            }
            for e in events
        ],
        "actions": actions,
        "reflections": reflections,
        "total_events": len(events),
        "total_actions": len(actions),
        "total_reflections": len(reflections)
    }
