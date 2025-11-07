"""
Subagent Bridge - Expose parallel processing to UI
Shows multi-threaded subagent operations in real-time
"""

from fastapi import APIRouter, WebSocket
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime

router = APIRouter(prefix="/api/subagents", tags=["subagents"])

# Track active subagents
active_subagents: Dict[str, Dict] = {}
subagent_connections: List[WebSocket] = []

class SubagentTask:
    """Represents a parallel subagent task"""
    def __init__(self, task_id: str, agent_type: str, task: str, domain: str):
        self.task_id = task_id
        self.agent_type = agent_type
        self.task = task
        self.domain = domain
        self.status = "starting"
        self.progress = 0
        self.started_at = datetime.now()
        self.result = None
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "task": self.task,
            "domain": self.domain,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat(),
            "result": self.result
        }

@router.websocket("/ws")
async def subagent_stream(websocket: WebSocket):
    """
    Stream parallel subagent execution to UI
    Shows multi-threading in real-time
    """
    await websocket.accept()
    subagent_connections.append(websocket)
    
    try:
        while True:
            # Send current state of all subagents
            await websocket.send_json({
                "type": "subagent_status",
                "agents": {k: v.to_dict() for k, v in active_subagents.items()},
                "total_active": len([a for a in active_subagents.values() if a.status == "running"]),
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(1)  # Update every second
            
    except:
        subagent_connections.remove(websocket)

async def spawn_subagent(agent_type: str, task: str, domain: str, background: bool = True) -> str:
    """
    Spawn a new subagent for parallel processing.
    Routes to concurrent executor for real multi-threading.
    
    Args:
        agent_type: Type of agent (e.g., "knowledge", "security", "ml")
        task: Task description
        domain: Domain to execute in
        background: Run in background (True) or wait for completion (False)
    
    Returns:
        task_id for tracking
    """
    
    from ..concurrent_executor import concurrent_executor
    
    task_id = f"{agent_type}_{datetime.now().timestamp()}"
    agent = SubagentTask(task_id, agent_type, task, domain)
    active_subagents[task_id] = agent
    
    # Submit to concurrent executor for real parallel execution
    executor_task_id = await concurrent_executor.submit_task(
        domain=domain,
        action=task,
        parameters={"task_description": task, "agent_type": agent_type},
        priority=5,
        background=background
    )
    
    # Update agent status
    agent.status = "running"
    
    # Notify all UI connections
    await broadcast_subagent_update({
        "type": "subagent_spawned",
        "agent": agent.to_dict(),
        "executor_task_id": executor_task_id,
        "timestamp": datetime.now().isoformat()
    })
    
    # Start the agent work in background
    asyncio.create_task(run_subagent(agent))
    
    return task_id

async def run_subagent(agent: SubagentTask):
    """
    Execute subagent task (simulated for now)
    """
    agent.status = "running"
    await broadcast_subagent_update({
        "type": "subagent_progress",
        "task_id": agent.task_id,
        "status": "running",
        "progress": 0
    })
    
    # Simulate work with progress updates
    for progress in range(0, 101, 20):
        agent.progress = progress
        await broadcast_subagent_update({
            "type": "subagent_progress",
            "task_id": agent.task_id,
            "progress": progress
        })
        await asyncio.sleep(2)  # Simulate work
    
    agent.status = "completed"
    agent.result = {"status": "success", "output": f"Completed: {agent.task}"}
    
    await broadcast_subagent_update({
        "type": "subagent_completed",
        "task_id": agent.task_id,
        "result": agent.result
    })
    
    # Cleanup after 30 seconds
    await asyncio.sleep(30)
    if agent.task_id in active_subagents:
        del active_subagents[agent.task_id]

async def broadcast_subagent_update(update: Dict):
    """Broadcast subagent updates to all UI connections"""
    for conn in subagent_connections:
        try:
            await conn.send_json(update)
        except:
            subagent_connections.remove(conn)

@router.get("/active")
async def get_active_subagents():
    """Get all currently active subagents"""
    return {
        "agents": {k: v.to_dict() for k, v in active_subagents.items()},
        "total": len(active_subagents),
        "running": len([a for a in active_subagents.values() if a.status == "running"])
    }

@router.post("/spawn")
async def spawn_agent_endpoint(agent_type: str, task: str, domain: str = "core"):
    """
    API to spawn a new subagent
    Used by Grace or user to start parallel processing
    """
    task_id = await spawn_subagent(agent_type, task, domain)
    return {
        "success": True,
        "task_id": task_id,
        "message": f"Spawned {agent_type} subagent"
    }

# Export for use by Grace subsystems
__all__ = ['spawn_subagent', 'router']
