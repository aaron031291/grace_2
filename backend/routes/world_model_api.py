"""
World Model API
Grace's internal knowledge accessible via REST and MCP
"""

from fastapi import APIRouter, File, UploadFile
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import os
import tempfile
from pathlib import Path

from backend.world_model import grace_world_model, mcp_integration
from backend.developer.developer_agent import developer_agent

router = APIRouter(prefix="/world-model", tags=["Grace's World Model"])


class KnowledgeAddition(BaseModel):
    """Add knowledge to world model"""
    category: str
    content: str
    source: str
    confidence: float = 1.0
    tags: Optional[List[str]] = None


class WorldQuery(BaseModel):
    """Query world model"""
    query: str
    category: Optional[str] = None
    min_confidence: float = 0.5
    top_k: int = 5


# ============================================================================
# World Model Endpoints
# ============================================================================

@router.post("/add-knowledge")
async def add_knowledge(knowledge: KnowledgeAddition) -> Dict[str, Any]:
    """Add knowledge to Grace's world model"""
    knowledge_id = await grace_world_model.add_knowledge(
        category=knowledge.category,
        content=knowledge.content,
        source=knowledge.source,
        confidence=knowledge.confidence,
        tags=knowledge.tags
    )
    
    return {
        'success': True,
        'knowledge_id': knowledge_id,
        'category': knowledge.category
    }


@router.post("/query")
async def query_world_model(query: WorldQuery) -> Dict[str, Any]:
    """Query Grace's world model using RAG"""
    results = await grace_world_model.query(
        query=query.query,
        category=query.category,
        min_confidence=query.min_confidence,
        top_k=query.top_k
    )
    
    return {
        'query': query.query,
        'results': [k.to_dict() for k in results],
        'total': len(results)
    }


@router.post("/ask-grace")
async def ask_grace(question: str) -> Dict[str, Any]:
    """Ask Grace a question about herself"""
    answer = await grace_world_model.ask_self(question)
    return answer


@router.get("/self-knowledge")
async def get_self_knowledge() -> Dict[str, Any]:
    """Get Grace's self-knowledge"""
    knowledge = grace_world_model.get_self_knowledge()
    
    return {
        'category': 'self',
        'knowledge': [k.to_dict() for k in knowledge],
        'total': len(knowledge)
    }


@router.get("/system-knowledge")
async def get_system_knowledge() -> Dict[str, Any]:
    """Get Grace's system knowledge"""
    knowledge = grace_world_model.get_system_knowledge()
    
    return {
        'category': 'system',
        'knowledge': [k.to_dict() for k in knowledge],
        'total': len(knowledge)
    }


@router.get("/stats")
async def get_world_model_stats() -> Dict[str, Any]:
    """Get world model statistics"""
    stats = grace_world_model.get_stats()
    if "total_knowledge" in stats and "total_entries" not in stats:
        stats["total_entries"] = stats["total_knowledge"]
    return stats


# ============================================================================
# MCP Protocol Endpoints
# ============================================================================

@router.get("/mcp/manifest")
async def get_mcp_manifest() -> Dict[str, Any]:
    """Get MCP server manifest"""
    return mcp_integration.get_mcp_manifest()


@router.get("/mcp/resource")
async def get_mcp_resource(uri: str) -> Dict[str, Any]:
    """
    Get MCP resource
    
    URIs:
    - grace://self
    - grace://system
    - grace://domain/{domain_id}
    - grace://timeline
    """
    return await mcp_integration.handle_resource_request(uri)


@router.post("/mcp/tool")
async def call_mcp_tool(
    tool_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call MCP tool
    
    Tools:
    - query_world_model
    - ask_grace
    - add_knowledge
    """
    return await mcp_integration.handle_tool_call(tool_name, parameters)


@router.post("/initialize")
async def initialize_world_model() -> Dict[str, str]:
    """Initialize Grace's world model and MCP"""
    from backend.world_model import initialize_world_model
    
    result = await initialize_world_model()
    
    return {
        'status': 'initialized',
        'world_model': result['world_model'],
        'mcp': result['mcp']
    }


# ============================================================================
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message with optional session context"""
    message: str
    session_id: Optional[str] = None


@router.post("/chat")
async def handle_chat(chat: ChatMessage) -> Dict[str, Any]:
    """
    Handle chat messages with slash command support
    
    Supported commands:
    - /build <spec> - Start a new software development build
    - /status <job_id> - Get status of a build job
    - /approve <job_id> - Approve a build job (governance or user)
    - /reject <job_id> - Reject a build job
    """
    message = chat.message.strip()
    
    if message.startswith("/build"):
        spec = message[6:].strip()
        if not spec:
            return {
                "type": "error",
                "message": "Please provide a specification. Usage: /build <what to build>"
            }
        
        job = await developer_agent.create_job(spec, chat.session_id)
        
        import asyncio
        asyncio.create_task(developer_agent.run_pipeline_with_approvals(job))
        
        return {
            "type": "build_started",
            "job_id": job.job_id,
            "spec": spec,
            "message": f"Build job {job.job_id} started! I'll generate a plan and wait for your approval.",
            "card": {
                "type": "BuildProgressCard",
                "job_id": job.job_id,
                "status": "planning",
                "spec": spec
            }
        }
    
    elif message.startswith("/status"):
        parts = message.split()
        if len(parts) < 2:
            return {
                "type": "error",
                "message": "Please provide a job ID. Usage: /status <job_id>"
            }
        
        job_id = parts[1]
        job = developer_agent.get_job(job_id)
        
        if not job:
            return {
                "type": "error",
                "message": f"Job {job_id} not found"
            }
        
        return {
            "type": "build_status",
            "job": job.to_dict(),
            "card": {
                "type": "BuildProgressCard",
                "job_id": job.job_id,
                "status": job.status,
                "spec": job.spec,
                "trust_score": job.trust_score,
                "approvals": job.approvals
            }
        }
    
    elif message.startswith("/approve"):
        parts = message.split()
        if len(parts) < 2:
            return {
                "type": "error",
                "message": "Please provide a job ID. Usage: /approve <job_id>"
            }
        
        job_id = parts[1]
        job = developer_agent.get_job(job_id)
        
        if not job:
            return {
                "type": "error",
                "message": f"Job {job_id} not found"
            }
        
        if job.status == "waiting_for_governance":
            import asyncio
            asyncio.create_task(developer_agent.resume_after_governance_approval(job, "user"))
            return {
                "type": "approval_granted",
                "stage": "governance",
                "message": f"Governance approval granted for {job_id}. Running quality scans..."
            }
        elif job.status == "waiting_for_user_approval":
            import asyncio
            asyncio.create_task(developer_agent.resume_after_user_approval(job, "user"))
            return {
                "type": "approval_granted",
                "stage": "user_final",
                "message": f"User approval granted for {job_id}. Applying changes and opening PR..."
            }
        else:
            return {
                "type": "error",
                "message": f"Job {job_id} is not waiting for approval (status: {job.status})"
            }
    
    elif message.startswith("/reject"):
        parts = message.split()
        if len(parts) < 2:
            return {
                "type": "error",
                "message": "Please provide a job ID. Usage: /reject <job_id> [reason]"
            }
        
        job_id = parts[1]
        reason = " ".join(parts[2:]) if len(parts) > 2 else "User rejected"
        
        job = developer_agent.get_job(job_id)
        
        if not job:
            return {
                "type": "error",
                "message": f"Job {job_id} not found"
            }
        
        job.status = "rejected"
        job.add_error(f"Job rejected: {reason}")
        
        return {
            "type": "job_rejected",
            "job_id": job_id,
            "reason": reason,
            "message": f"Job {job_id} rejected: {reason}"
        }
    
    else:
        answer = await grace_world_model.ask_self(message)
        return {
            "type": "chat_response",
            "message": answer.get("answer", "I'm not sure how to respond to that."),
            "sources": answer.get("sources", [])
        }
