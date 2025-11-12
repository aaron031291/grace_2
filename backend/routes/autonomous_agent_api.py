"""
Autonomous Pipeline Agent API Routes
Control and monitor the autonomous agents
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/autonomous-agent", tags=["autonomous-agent"])


@router.post("/start")
async def start_agent():
    """Start the autonomous pipeline agent"""
    try:
        from backend.autonomous_pipeline_agent import autonomous_pipeline_agent
        
        await autonomous_pipeline_agent.start()
        
        return {
            'success': True,
            'message': 'Autonomous pipeline agent started'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_agent():
    """Stop the autonomous pipeline agent"""
    try:
        from backend.autonomous_pipeline_agent import autonomous_pipeline_agent
        
        await autonomous_pipeline_agent.stop()
        
        return {
            'success': True,
            'message': 'Autonomous pipeline agent stopped'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status():
    """Get status of the autonomous agent"""
    try:
        from backend.autonomous_pipeline_agent import autonomous_pipeline_agent
        
        status = await autonomous_pipeline_agent.get_status()
        
        return {
            'success': True,
            'status': status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agent_details():
    """Get detailed information about both agents"""
    try:
        from backend.autonomous_pipeline_agent import autonomous_pipeline_agent
        
        staging = autonomous_pipeline_agent.staging_agent
        approval = autonomous_pipeline_agent.approval_agent
        
        return {
            'success': True,
            'staging_agent': {
                'agent_id': staging.agent_id,
                'agent_name': staging.agent_name,
                'capabilities': staging.capabilities,
                'status': staging.status,
                'current_task': staging.current_task,
                'running': staging._running
            },
            'approval_agent': {
                'agent_id': approval.agent_id,
                'agent_name': approval.agent_name,
                'capabilities': approval.capabilities,
                'pending_drafts': len(approval.pending_drafts),
                'running': approval._running
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
