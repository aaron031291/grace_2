"""
Elite Systems API
API endpoints for Elite Self-Healing and Elite Coding Agent

Endpoints:
- GET /elite/status - Get status of all elite systems
- POST /elite/healing/task - Submit a healing task
- POST /elite/coding/task - Submit a coding task
- POST /elite/orchestration/task - Submit an orchestrated task
- GET /elite/healing/knowledge - Get healing knowledge base
- GET /elite/coding/knowledge - Get coding knowledge base
- GET /elite/orchestration/status - Get orchestration status
- GET /elite/tasks - Get all tasks
- GET /elite/tasks/{task_id} - Get specific task
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..auth import get_current_user

# Lazy imports to avoid circular dependencies
def get_elite_systems():
    """Lazy load elite systems"""
    try:
        from ..elite_self_healing import elite_self_healing, HealingDomain
        from ..elite_coding_agent import elite_coding_agent, CodingTaskType, ExecutionMode
        from ..shared_orchestration import shared_orchestrator, AgentType, TaskPriority
        return elite_self_healing, elite_coding_agent, shared_orchestrator, HealingDomain, CodingTaskType, ExecutionMode, AgentType, TaskPriority
    except Exception as e:
        return None, None, None, None, None, None, None, None

router = APIRouter(prefix="/elite", tags=["Elite Systems"])


# ========== Request Models ==========

class HealingTaskRequest(BaseModel):
    """Request to submit a healing task"""
    problem_description: str
    domain: str  # internal_code, internal_config, etc.
    severity: str = "medium"  # critical, high, medium, low
    auto_execute: bool = False


class CodingTaskRequest(BaseModel):
    """Request to submit a coding task"""
    task_type: str  # build_feature, fix_bug, refactor, etc.
    description: str
    requirements: Dict[str, Any] = {}
    execution_mode: str = "auto"  # sandbox, review, live, auto
    priority: int = 5


class OrchestrationTaskRequest(BaseModel):
    """Request to submit an orchestrated task"""
    agent_type: str  # self_healing, coding, both
    priority: int = 5
    description: str
    payload: Dict[str, Any] = {}
    dependencies: Optional[List[str]] = None


# ========== Status Endpoints ==========

@router.get("/status")
async def get_elite_status(current_user: str = Depends(get_current_user)):
    """Get status of all elite systems"""

    elite_self_healing, elite_coding_agent, shared_orchestrator, _, _, _, _, _ = get_elite_systems()

    if not elite_self_healing:
        return {
            "status": "not_available",
            "message": "Elite systems not loaded",
            "timestamp": datetime.utcnow().isoformat()
        }

    healing_status = {
        "running": elite_self_healing.running,
        "active_tasks": len(elite_self_healing.active_tasks),
        "knowledge_entries": len(elite_self_healing.knowledge_base),
        "healing_history": len(elite_self_healing.healing_history)
    }

    coding_status = {
        "running": elite_coding_agent.running,
        "active_tasks": len(elite_coding_agent.active_tasks),
        "task_queue": len(elite_coding_agent.task_queue),
        "completed_tasks": len(elite_coding_agent.completed_tasks),
        "knowledge_entries": len(elite_coding_agent.knowledge_base)
    }

    orchestration_status = shared_orchestrator.get_status()

    return {
        "status": "operational",
        "self_healing": healing_status,
        "coding_agent": coding_status,
        "orchestration": orchestration_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# ========== Healing Endpoints ==========

@router.post("/healing/task")
async def submit_healing_task(
    request: HealingTaskRequest,
    current_user: str = Depends(get_current_user)
):
    """Submit a healing task"""
    
    try:
        # Map domain string to enum
        domain_map = {
            "internal_code": HealingDomain.INTERNAL_CODE,
            "internal_config": HealingDomain.INTERNAL_CONFIG,
            "internal_data": HealingDomain.INTERNAL_DATA,
            "internal_performance": HealingDomain.INTERNAL_PERFORMANCE,
            "external_api": HealingDomain.EXTERNAL_API,
            "external_integration": HealingDomain.EXTERNAL_INTEGRATION,
            "external_infrastructure": HealingDomain.EXTERNAL_INFRASTRUCTURE
        }
        
        domain = domain_map.get(request.domain)
        if not domain:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {request.domain}")
        
        # Create task through orchestrator
        task_id = await shared_orchestrator.submit_task(
            agent_type=AgentType.SELF_HEALING,
            priority=TaskPriority.MEDIUM,
            description=request.problem_description,
            payload={
                "domain": request.domain,
                "severity": request.severity,
                "auto_execute": request.auto_execute,
                "submitted_by": current_user
            }
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Healing task submitted",
            "domain": request.domain,
            "severity": request.severity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/healing/knowledge")
async def get_healing_knowledge(current_user: str = Depends(get_current_user)):
    """Get healing knowledge base"""
    
    knowledge = []
    for entry in elite_self_healing.knowledge_base:
        knowledge.append({
            "problem_pattern": entry.problem_pattern,
            "solution_pattern": entry.solution_pattern,
            "success_rate": entry.success_rate,
            "confidence": entry.confidence,
            "domain": entry.domain.value,
            "capabilities": [c.value for c in entry.capabilities_used],
            "learned_from": entry.learned_from
        })
    
    return {
        "knowledge_entries": len(knowledge),
        "knowledge": knowledge
    }


# ========== Coding Agent Endpoints ==========

@router.post("/coding/task")
async def submit_coding_task(
    request: CodingTaskRequest,
    current_user: str = Depends(get_current_user)
):
    """Submit a coding task"""
    
    try:
        # Map task type string to enum
        task_type_map = {
            "build_feature": CodingTaskType.BUILD_FEATURE,
            "fix_bug": CodingTaskType.FIX_BUG,
            "refactor": CodingTaskType.REFACTOR,
            "optimize": CodingTaskType.OPTIMIZE,
            "add_tests": CodingTaskType.ADD_TESTS,
            "extend_grace": CodingTaskType.EXTEND_GRACE,
            "integrate_system": CodingTaskType.INTEGRATE_SYSTEM
        }
        
        task_type = task_type_map.get(request.task_type)
        if not task_type:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {request.task_type}")
        
        # Map execution mode
        exec_mode_map = {
            "sandbox": ExecutionMode.SANDBOX,
            "review": ExecutionMode.REVIEW,
            "live": ExecutionMode.LIVE,
            "auto": ExecutionMode.AUTO
        }
        
        exec_mode = exec_mode_map.get(request.execution_mode, ExecutionMode.AUTO)
        
        # Submit through orchestrator
        task_id = await shared_orchestrator.submit_task(
            agent_type=AgentType.CODING,
            priority=TaskPriority(request.priority),
            description=request.description,
            payload={
                "task_type": request.task_type,
                "requirements": request.requirements,
                "execution_mode": request.execution_mode,
                "submitted_by": current_user
            }
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Coding task submitted",
            "task_type": request.task_type,
            "execution_mode": request.execution_mode
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coding/knowledge")
async def get_coding_knowledge(current_user: str = Depends(get_current_user)):
    """Get coding knowledge base"""
    
    knowledge = []
    for topic, entry in elite_coding_agent.knowledge_base.items():
        knowledge.append({
            "topic": entry.topic,
            "category": entry.category,
            "content": entry.content,
            "examples": entry.examples,
            "related_topics": entry.related_topics,
            "confidence": entry.confidence,
            "source": entry.source
        })
    
    return {
        "knowledge_entries": len(knowledge),
        "knowledge": knowledge
    }


# ========== Orchestration Endpoints ==========

@router.post("/orchestration/task")
async def submit_orchestration_task(
    request: OrchestrationTaskRequest,
    current_user: str = Depends(get_current_user)
):
    """Submit a task to the orchestrator"""
    
    try:
        # Map agent type
        agent_type_map = {
            "self_healing": AgentType.SELF_HEALING,
            "coding": AgentType.CODING,
            "both": AgentType.BOTH
        }
        
        agent_type = agent_type_map.get(request.agent_type)
        if not agent_type:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {request.agent_type}")
        
        # Submit task
        task_id = await shared_orchestrator.submit_task(
            agent_type=agent_type,
            priority=TaskPriority(request.priority),
            description=request.description,
            payload={
                **request.payload,
                "submitted_by": current_user
            },
            dependencies=request.dependencies
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task submitted to orchestrator",
            "agent_type": request.agent_type,
            "priority": request.priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestration/status")
async def get_orchestration_status(current_user: str = Depends(get_current_user)):
    """Get orchestration system status"""
    return shared_orchestrator.get_status()


# ========== Task Management Endpoints ==========

@router.get("/tasks")
async def get_all_tasks(
    status: Optional[str] = None,
    agent_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get all tasks with optional filtering"""
    
    tasks = []
    
    # Get tasks from orchestrator
    for task in shared_orchestrator.active_tasks.values():
        if status and task.status != status:
            continue
        if agent_type and task.agent_type.value != agent_type:
            continue
        
        tasks.append({
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "priority": task.priority.value,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        })
    
    # Also get completed tasks
    for task in shared_orchestrator.completed_tasks[-50:]:  # Last 50
        if status and task.status != status:
            continue
        if agent_type and task.agent_type.value != agent_type:
            continue
        
        tasks.append({
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "priority": task.priority.value,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result
        })
    
    return {
        "total_tasks": len(tasks),
        "tasks": tasks
    }


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get specific task details"""
    
    # Check active tasks
    task = shared_orchestrator.active_tasks.get(task_id)
    
    # Check completed tasks
    if not task:
        for completed_task in shared_orchestrator.completed_tasks:
            if completed_task.task_id == task_id:
                task = completed_task
                break
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {
        "task_id": task.task_id,
        "agent_type": task.agent_type.value,
        "priority": task.priority.value,
        "description": task.description,
        "payload": task.payload,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "assigned_to": task.assigned_to,
        "result": task.result,
        "dependencies": task.dependencies
    }

