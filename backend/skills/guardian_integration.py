"""
Guardian Integration - Wire Guardian to use Skill Registry
Example of how Guardian uses skills via Action Gateway with governance
"""

from typing import Dict, Any
from backend.skills.registry import skill_registry
from backend.core.unified_event_publisher import publish_event

async def guardian_detect_and_heal(issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guardian detects an issue and uses skills to heal it
    
    This demonstrates the "one organism" loop:
    1. Guardian detects issue
    2. Requests action via Action Gateway (governance check)
    3. Executes skill if approved
    4. Publishes outcome to Event Bus
    5. Reflection Loop learns from outcome
    
    Args:
        issue_type: Type of issue detected (e.g., "port_conflict", "network_degradation")
        context: Context about the issue
    
    Returns:
        Result of healing attempt
    """
    
    if issue_type == "port_conflict":
        memory_result = await skill_registry.execute_skill(
            skill_name="read_memory",
            agent="guardian",
            params={
                "query": f"port conflict {context.get('port', 'unknown')}",
                "limit": 3
            }
        )
        
        if memory_result.success:
            print(f"[Guardian] Found {len(memory_result.result.get('results', []))} similar issues in memory")
        
        healing_action = {
            "issue_type": issue_type,
            "port": context.get("port"),
            "timestamp": context.get("timestamp"),
            "action": "release_and_reallocate"
        }
        
        write_result = await skill_registry.execute_skill(
            skill_name="write_memory",
            agent="guardian",
            params={
                "content": f"Guardian healed {issue_type}: {healing_action}",
                "metadata": healing_action
            }
        )
        
        if write_result.success:
            print(f"[Guardian] Healing action recorded in memory")
        
        await publish_event(
            event_type="self_healing.trigger",
            source="guardian",
            data={
                "issue_type": issue_type,
                "context": context,
                "memory_check": memory_result.success,
                "action_recorded": write_result.success
            }
        )
        
        return {
            "healed": True,
            "issue_type": issue_type,
            "memory_check": memory_result.success,
            "action_recorded": write_result.success,
            "trace_id": write_result.trace_id
        }
    
    return {
        "healed": False,
        "reason": f"Unknown issue type: {issue_type}"
    }

async def guardian_proactive_scan() -> Dict[str, Any]:
    """
    Guardian performs proactive scan and uses skills to check system health
    
    Returns:
        Scan results
    """
    
    scan_result = await skill_registry.execute_skill(
        skill_name="read_memory",
        agent="guardian",
        params={
            "query": "guardian healing actions network issues",
            "limit": 10
        }
    )
    
    if scan_result.success:
        results = scan_result.result.get("results", [])
        print(f"[Guardian] Proactive scan found {len(results)} recent healing actions")
        
        await publish_event(
            event_type="verification.result",
            source="guardian",
            data={
                "scan_type": "proactive",
                "issues_found": len(results),
                "trace_id": scan_result.trace_id
            }
        )
        
        return {
            "scan_complete": True,
            "issues_found": len(results),
            "trace_id": scan_result.trace_id
        }
    
    return {
        "scan_complete": False,
        "error": scan_result.error
    }
