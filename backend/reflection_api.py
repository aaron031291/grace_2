"""
Reflection API - Endpoints for managing and querying reflections
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from backend.reflection_loop_v2 import reflection_loop
from backend.schemas import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/api/reflections", tags=["reflections"])


@router.get("/", response_model=SuccessResponse)
async def list_reflections(
    limit: int = Query(100, description="Maximum number of reflections to return"),
    agent: Optional[str] = Query(None, description="Filter by agent"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    success: Optional[bool] = Query(None, description="Filter by success status")
):
    """
    Get reflections with optional filtering
    """
    try:
        reflections = await reflection_loop.get_reflections(
            limit=limit, agent=agent, action_type=action_type, success=success
        )

        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(reflections)} reflections",
            data={"reflections": reflections, "count": len(reflections)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reflections: {str(e)}")


@router.get("/insights/summary", response_model=SuccessResponse)
async def get_insights_summary(
    days: int = Query(7, description="Number of days to analyze")
):
    """
    Get aggregated insights summary from recent reflections
    """
    try:
        summary = await reflection_loop.get_insights_summary(days=days)
        return SuccessResponse(
            success=True,
            message=f"Generated insights summary for {days} days",
            data={"summary": summary}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights summary: {str(e)}")


@router.get("/strategy-updates", response_model=SuccessResponse)
async def get_strategy_updates(
    limit: int = Query(50, description="Maximum number of strategy updates to return")
):
    """
    Get recommended strategy updates from recent reflections
    """
    try:
        updates = await reflection_loop.get_strategy_updates(limit=limit)
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(updates)} strategy updates",
            data={"strategy_updates": updates, "count": len(updates)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve strategy updates: {str(e)}")


@router.get("/agents/{agent}/performance", response_model=SuccessResponse)
async def get_agent_performance(
    agent: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """
    Get performance metrics for a specific agent
    """
    try:
        # Get agent-specific reflections
        reflections = await reflection_loop.get_reflections(
            limit=1000, agent=agent
        )

        # Apply days filter
        cutoff_date = datetime.now() - timedelta(days=days)
        reflections = [
            r for r in reflections
            if datetime.fromisoformat(r['timestamp']) >= cutoff_date
        ]

        if not reflections:
            return SuccessResponse(
                success=True,
                message=f"No reflections found for agent {agent}",
                data={"performance": {"total_actions": 0, "success_rate": 0, "insights": []}}
            )

        # Calculate performance metrics
        total_actions = len(reflections)
        successful_actions = sum(1 for r in reflections if r['success'])
        success_rate = successful_actions / total_actions if total_actions > 0 else 0

        # Get recent insights
        recent_insights = []
        for reflection in reflections[:10]:  # Last 10 reflections
            if reflection.get('generated_insights', {}).get('patterns'):
                recent_insights.extend(reflection['generated_insights']['patterns'])

        # Get trust score
        trust_scores = {}
        for reflection in reflections:
            action_type = reflection['action_type']
            if action_type not in trust_scores:
                trust_scores[action_type] = reflection.get('trust_score_after', 0.5)

        performance = {
            "agent": agent,
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": round(success_rate, 3),
            "time_period_days": days,
            "action_type_trust_scores": trust_scores,
            "recent_insights": list(set(recent_insights))[:10],  # Unique, limit to 10
            "latest_reflection": reflections[0] if reflections else None
        }

        return SuccessResponse(
            success=True,
            message=f"Retrieved performance metrics for agent {agent}",
            data={"performance": performance}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent performance: {str(e)}")


@router.get("/actions/{action_type}/analysis", response_model=SuccessResponse)
async def get_action_analysis(
    action_type: str,
    days: int = Query(30, description="Number of days to analyze")
):
    """
    Get analysis for a specific action type
    """
    try:
        # Get action-specific reflections
        reflections = await reflection_loop.get_reflections(
            limit=1000, action_type=action_type
        )

        # Apply days filter
        cutoff_date = datetime.now() - timedelta(days=days)
        reflections = [
            r for r in reflections
            if datetime.fromisoformat(r['timestamp']) >= cutoff_date
        ]

        if not reflections:
            return SuccessResponse(
                success=True,
                message=f"No reflections found for action type {action_type}",
                data={"analysis": {"total_occurrences": 0, "success_rate": 0, "insights": []}}
            )

        # Calculate metrics
        total_occurrences = len(reflections)
        successful_occurrences = sum(1 for r in reflections if r['success'])
        success_rate = successful_occurrences / total_occurrences if total_occurrences > 0 else 0

        # Aggregate insights
        all_patterns = []
        all_improvements = []
        confidence_scores = []

        for reflection in reflections:
            if reflection.get('generated_insights', {}).get('patterns'):
                all_patterns.extend(reflection['generated_insights']['patterns'])
            if reflection.get('identified_improvements', {}).get('high_priority'):
                all_improvements.extend(reflection['identified_improvements']['high_priority'])
            if reflection.get('confidence_score'):
                confidence_scores.append(reflection['confidence_score'])

        # Get most common patterns and improvements
        from collections import Counter
        common_patterns = Counter(all_patterns).most_common(5)
        common_improvements = Counter(all_improvements).most_common(5)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        analysis = {
            "action_type": action_type,
            "total_occurrences": total_occurrences,
            "successful_occurrences": successful_occurrences,
            "success_rate": round(success_rate, 3),
            "average_confidence": round(avg_confidence, 3),
            "time_period_days": days,
            "common_patterns": [{"pattern": p, "count": c} for p, c in common_patterns],
            "common_improvements": [{"improvement": i, "count": c} for i, c in common_improvements],
            "latest_reflection": reflections[0] if reflections else None
        }

        return SuccessResponse(
            success=True,
            message=f"Retrieved analysis for action type {action_type}",
            data={"analysis": analysis}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get action analysis: {str(e)}")


@router.get("/stats", response_model=SuccessResponse)
async def get_reflection_stats(
    days: int = Query(7, description="Number of days to analyze")
):
    """
    Get overall reflection system statistics
    """
    try:
        # Get basic stats
        all_reflections = await reflection_loop.get_reflections(limit=10000)

        # Apply days filter
        cutoff_date = datetime.now() - timedelta(days=days)
        all_reflections = [
            r for r in all_reflections
            if datetime.fromisoformat(r['timestamp']) >= cutoff_date
        ]

        if not all_reflections:
            return SuccessResponse(
                success=True,
                message="No reflections found in the specified period",
                data={"stats": {"total_reflections": 0, "success_rate": 0, "time_period_days": days}}
            )

        total_reflections = len(all_reflections)
        successful_reflections = sum(1 for r in all_reflections if r['success'])
        success_rate = successful_reflections / total_reflections if total_reflections > 0 else 0

        # Agent breakdown
        agent_counts = {}
        action_counts = {}

        for reflection in all_reflections:
            agent = reflection['agent']
            action_type = reflection['action_type']

            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        # Sort by frequency
        top_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        stats = {
            "total_reflections": total_reflections,
            "successful_reflections": successful_reflections,
            "success_rate": round(success_rate, 3),
            "time_period_days": days,
            "unique_agents": len(agent_counts),
            "unique_action_types": len(action_counts),
            "top_agents": [{"agent": a, "count": c} for a, c in top_agents],
            "top_action_types": [{"action_type": a, "count": c} for a, c in top_actions],
            "average_reflections_per_day": round(total_reflections / days, 1) if days > 0 else 0
        }

        return SuccessResponse(
            success=True,
            message=f"Retrieved reflection statistics for {days} days",
            data={"stats": stats}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reflection stats: {str(e)}")</content>
</edit_file>