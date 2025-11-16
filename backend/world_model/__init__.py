"""
Grace's World Model with RAG and MCP

Grace's unified internal knowledge representation:
- Self-knowledge (what Grace knows about herself)
- System knowledge (Grace's systems and architecture)
- User knowledge (what Grace learns about users)
- Domain knowledge (domain-specific learnings)
- Temporal knowledge (time-series events)

Accessible via:
- RAG (semantic search)
- MCP (Model Context Protocol)
- API endpoints
- Service mesh
"""

from .grace_world_model import grace_world_model, GraceWorldModel, WorldKnowledge
from .mcp_integration import mcp_integration, MCPIntegration

__all__ = [
    'grace_world_model',
    'GraceWorldModel',
    'WorldKnowledge',
    'mcp_integration',
    'MCPIntegration',
]


async def initialize_world_model():
    """
    Initialize Grace's world model
    Call this on startup
    """
    await grace_world_model.initialize()
    await mcp_integration.initialize()
    
    return {
        'world_model': 'initialized',
        'mcp': 'initialized'
    }
