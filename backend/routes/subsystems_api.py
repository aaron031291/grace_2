"""
Subsystems Integration API Routes
Endpoints for subsystem logging and monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/api/subsystems", tags=["subsystems"])


# ===== Self-Healing Endpoints =====

class PlaybookExecutionLog(BaseModel):
    playbook_name: str
    trigger_conditions: Dict[str, Any]
    actions: List[Any]
    target_components: List[str]
    execution_result: Dict[str, Any]


@router.post("/self-healing/log")
async def log_self_healing_execution(log: PlaybookExecutionLog):
    """Log a self-healing playbook execution"""
    try:
        from backend.subsystems.self_healing_integration import self_healing_integration
        
        result = await self_healing_integration.log_playbook_execution(
            log.playbook_name,
            log.trigger_conditions,
            log.actions,
            log.target_components,
            log.execution_result
        )
        
        return {
            'success': True,
            'row_id': str(result.id) if result else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-healing/stats/{playbook_name}")
async def get_playbook_stats(playbook_name: str):
    """Get statistics for a specific playbook"""
    try:
        from backend.subsystems.self_healing_integration import self_healing_integration
        
        stats = await self_healing_integration.get_playbook_stats(playbook_name)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-healing/top-playbooks")
async def get_top_playbooks(limit: int = 10):
    """Get top-performing playbooks"""
    try:
        from backend.subsystems.self_healing_integration import self_healing_integration
        
        playbooks = await self_healing_integration.get_top_playbooks(limit)
        
        return {
            'success': True,
            'playbooks': playbooks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Coding Agent Endpoints =====

class WorkOrderCreate(BaseModel):
    work_order_id: str
    title: str
    description: str
    task_type: str = "feature"
    priority: str = "medium"


class CodeChangesLog(BaseModel):
    work_order_id: str
    affected_files: List[str]
    lines_added: int
    lines_removed: int
    code_diff_path: Optional[str] = None


class TestResultsLog(BaseModel):
    work_order_id: str
    test_results: Dict[str, Any]


class DeploymentLog(BaseModel):
    work_order_id: str
    deployment_impact: Dict[str, Any]


@router.post("/coding-agent/work-order")
async def create_work_order(order: WorkOrderCreate):
    """Create a new coding work order"""
    try:
        from backend.subsystems.coding_agent_integration import coding_agent_integration
        
        result = await coding_agent_integration.create_work_order(
            order.work_order_id,
            order.title,
            order.description,
            order.task_type,
            order.priority
        )
        
        return {
            'success': True,
            'row_id': str(result.id) if result else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coding-agent/code-changes")
async def log_code_changes(log: CodeChangesLog):
    """Log code changes for a work order"""
    try:
        from backend.subsystems.coding_agent_integration import coding_agent_integration
        
        result = await coding_agent_integration.log_code_changes(
            log.work_order_id,
            log.affected_files,
            log.lines_added,
            log.lines_removed,
            log.code_diff_path
        )
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coding-agent/test-results")
async def log_test_results(log: TestResultsLog):
    """Log test execution results"""
    try:
        from backend.subsystems.coding_agent_integration import coding_agent_integration
        
        result = await coding_agent_integration.log_test_results(
            log.work_order_id,
            log.test_results
        )
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coding-agent/deployed")
async def mark_deployed(log: DeploymentLog):
    """Mark work order as deployed"""
    try:
        from backend.subsystems.coding_agent_integration import coding_agent_integration
        
        result = await coding_agent_integration.mark_deployed(
            log.work_order_id,
            log.deployment_impact
        )
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coding-agent/stats")
async def get_coding_stats():
    """Get overall coding agent statistics"""
    try:
        from backend.subsystems.coding_agent_integration import coding_agent_integration
        
        stats = await coding_agent_integration.get_work_order_stats()
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Sub-Agents Endpoints =====

class AgentRegistration(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str
    mission: str
    capabilities: List[str]
    constraints: Optional[Dict[str, Any]] = None


class AgentStatusUpdate(BaseModel):
    agent_id: str
    status: str
    current_task: Optional[str] = None


class TaskCompletionLog(BaseModel):
    agent_id: str
    success: bool


@router.post("/sub-agents/register")
async def register_agent(agent: AgentRegistration):
    """Register a new sub-agent"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        result = await sub_agents_integration.register_agent(
            agent.agent_id,
            agent.agent_name,
            agent.agent_type,
            agent.mission,
            agent.capabilities,
            agent.constraints
        )
        
        return {
            'success': True,
            'row_id': str(result.id) if result else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sub-agents/status")
async def update_agent_status(update: AgentStatusUpdate):
    """Update agent status"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        result = await sub_agents_integration.update_agent_status(
            update.agent_id,
            update.status,
            update.current_task
        )
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sub-agents/task-completion")
async def log_task_completion(log: TaskCompletionLog):
    """Log task completion for an agent"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        result = await sub_agents_integration.log_task_completion(
            log.agent_id,
            log.success
        )
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sub-agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str):
    """Send agent heartbeat"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        result = await sub_agents_integration.heartbeat(agent_id)
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-agents/{agent_id}/stats")
async def get_agent_stats(agent_id: str):
    """Get statistics for a specific agent"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        stats = await sub_agents_integration.get_agent_stats(agent_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-agents/active")
async def get_active_agents():
    """Get all active agents"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        agents = await sub_agents_integration.get_active_agents()
        
        return {
            'success': True,
            'agents': agents,
            'count': len(agents)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-agents/fleet-stats")
async def get_fleet_stats():
    """Get overall sub-agent fleet statistics"""
    try:
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        
        stats = await sub_agents_integration.get_fleet_stats()
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
