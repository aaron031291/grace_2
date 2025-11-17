"""
World Model API
Grace's internal knowledge accessible via REST and MCP
"""

from fastapi import APIRouter
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.world_model import grace_world_model, mcp_integration

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
    return grace_world_model.get_stats()


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
