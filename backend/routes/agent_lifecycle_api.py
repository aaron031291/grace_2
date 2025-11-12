"""
Agent Lifecycle API Routes
Control and monitor the agent lifecycle manager
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/agent-lifecycle", tags=["agent-lifecycle"])


class SpawnAgentRequest(BaseModel):
    agent_type: str
    instance_id: Optional[str] = None


class ExecuteJobRequest(BaseModel):
    agent_type: str
    job: Dict[str, Any]
    reuse_agent: bool = False


class RevokeAgentRequest(BaseModel):
    agent_id: str
    reason: str


@router.post("/spawn")
async def spawn_agent(request: SpawnAgentRequest):
    """Spawn a new agent instance"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        agent = await agent_lifecycle_manager.spawn_agent(
            request.agent_type,
            request.instance_id
        )
        
        status = await agent.get_status()
        
        return {
            'success': True,
            'agent': status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-job")
async def execute_job(request: ExecuteJobRequest):
    """Execute a job using an agent"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        result = await agent_lifecycle_manager.execute_job(
            request.agent_type,
            request.job,
            request.reuse_agent
        )
        
        return {
            'success': True,
            'result': result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-job")
async def submit_job(request: ExecuteJobRequest):
    """Submit a job to the queue for async processing"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        job_id = await agent_lifecycle_manager.submit_job_to_queue(
            request.agent_type,
            request.job
        )
        
        return {
            'success': True,
            'job_id': job_id,
            'status': 'queued'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-queue")
async def process_queue(max_concurrent: int = 5):
    """Process queued jobs"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        await agent_lifecycle_manager.process_job_queue(max_concurrent)
        
        metrics = await agent_lifecycle_manager.get_metrics()
        
        return {
            'success': True,
            'message': 'Job queue processing started',
            'metrics': metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/terminate/{agent_id}")
async def terminate_agent(agent_id: str):
    """Terminate a specific agent"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        await agent_lifecycle_manager.terminate_agent(agent_id)
        
        return {
            'success': True,
            'message': f'Agent {agent_id} terminated'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke")
async def revoke_agent(request: RevokeAgentRequest):
    """Revoke an agent"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        await agent_lifecycle_manager.revoke_agent(
            request.agent_id,
            request.reason
        )
        
        return {
            'success': True,
            'message': f'Agent {request.agent_id} revoked'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_all_agents():
    """Get all active agents"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        agents = await agent_lifecycle_manager.get_all_agents()
        
        return {
            'success': True,
            'agents': agents,
            'count': len(agents)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        status = await agent_lifecycle_manager.get_agent_status(agent_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            'success': True,
            'agent': status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    """Get lifecycle manager metrics"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        metrics = await agent_lifecycle_manager.get_metrics()
        
        return {
            'success': True,
            'metrics': metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/start")
async def start_monitoring():
    """Start agent lifecycle monitoring"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        await agent_lifecycle_manager.start_monitoring()
        
        return {
            'success': True,
            'message': 'Agent lifecycle monitoring started'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop agent lifecycle monitoring"""
    try:
        from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager
        
        await agent_lifecycle_manager.stop_monitoring()
        
        return {
            'success': True,
            'message': 'Agent lifecycle monitoring stopped'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
