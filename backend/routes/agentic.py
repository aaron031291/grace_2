"""Agentic dashboard API endpoints"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..auth import get_current_user

router = APIRouter()

@router.get("/api/metrics/recent")
async def get_recent_metrics(current_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Get recent metrics data for dashboard"""
    try:
        from ..metrics_service import get_metrics_collector
        collector = get_metrics_collector()

        # Get recent metrics from collector
        recent_metrics = []
        if hasattr(collector, 'aggregates'):
            for domain, kpis in collector.aggregates.items():
                for kpi_name, kpi_data in kpis.items():
                    if isinstance(kpi_data, dict) and 'value' in kpi_data:
                        recent_metrics.append({
                            "metric_id": f"{domain}.{kpi_name}",
                            "category": domain,
                            "value": kpi_data['value'],
                            "unit": kpi_data.get('unit', ''),
                            "status": _calculate_status(kpi_data.get('value', 0), domain, kpi_name),
                            "timestamp": kpi_data.get('timestamp', '')
                        })

        return {"metrics": recent_metrics[:20]}  # Return last 20 metrics
    except Exception as e:
        return {"metrics": [], "error": str(e)}

@router.get("/api/agentic/actions")
async def get_agentic_actions(current_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Get recent agentic actions for dashboard"""
    try:
        from ..immutable_log import immutable_log

        # Query recent agentic actions from immutable log
        actions = await immutable_log.query_recent_actions(
            actor="agentic_spine",
            limit=20
        )

        formatted_actions = []
        for action in actions:
            formatted_actions.append({
                "id": action.get("id", ""),
                "type": action.get("action", "").replace("_", " "),
                "status": _map_action_status(action.get("result", "")),
                "description": _format_action_description(action),
                "timestamp": action.get("timestamp", ""),
                "risk_score": _calculate_risk_score(action)
            })

        return {"actions": formatted_actions}
    except Exception as e:
        return {"actions": [], "error": str(e)}

def _calculate_status(value: float, domain: str, metric: str) -> str:
    """Calculate status based on metric value and thresholds"""
    if domain == "health":
        if metric == "overall_health":
            return "good" if value > 60 else "warning" if value > 40 else "critical"
        elif metric == "error_rate":
            return "good" if value < 0.15 else "warning" if value < 0.25 else "critical"
    elif domain == "performance":
        if "latency" in metric:
            return "good" if value < 5000 else "warning" if value < 10000 else "critical"
        elif "throughput" in metric:
            return "good" if value > 50 else "warning" if value > 25 else "critical"

    # Default logic - make thresholds more lenient
    if value > 0.6:
        return "good"
    elif value > 0.4:
        return "warning"
    else:
        return "critical"

def _map_action_status(result: str) -> str:
    """Map immutable log result to action status"""
    if result == "success":
        return "completed"
    elif result in ["failed", "error"]:
        return "failed"
    elif result == "planned":
        return "pending"
    else:
        return "executing"

def _format_action_description(action: Dict[str, Any]) -> str:
    """Format action details into human-readable description"""
    action_type = action.get("action", "")
    resource = action.get("resource", "")
    payload = action.get("payload", {})

    if action_type == "recovery_planned":
        playbook = payload.get("playbook", "Unknown")
        return f"Planned recovery using playbook: {playbook}"
    elif action_type == "recovery_executed":
        outcome = payload.get("outcome", "unknown")
        return f"Executed recovery action with outcome: {outcome}"
    elif action_type == "event_enriched":
        confidence = payload.get("confidence", 0)
        return f"Enriched event with {confidence:.2f} confidence"
    else:
        return f"{action_type.replace('_', ' ')} on {resource}"

def _calculate_risk_score(action: Dict[str, Any]) -> float:
    """Calculate risk score for action display"""
    payload = action.get("payload", {})

    # Extract risk score from payload if available
    if "risk_score" in payload:
        return payload["risk_score"]

    # Default risk scoring based on action type
    action_type = action.get("action", "")
    if "recovery" in action_type:
        return 0.7  # Recovery actions are moderately risky
    elif "enrich" in action_type:
        return 0.2  # Enrichment is low risk
    else:
        return 0.5  # Default moderate risk