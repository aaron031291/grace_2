"""
Grace's World Model with RAG and MCP

Provides:
- Internal knowledge representation (self, system, user, domain, temporal)
- Semantic search via RAG
- External access via MCP (Model Context Protocol)
- Automatic domain summary ingestion
"""

from .grace_world_model import grace_world_model, GraceWorldModel, WorldKnowledge
from .world_model_service import world_model_service, WorldModelService
from .mcp_integration import mcp_integration, MCPIntegration
from .world_model_summary_pipeline import (
    world_model_summary_pipeline,
    WorldModelSummaryPipeline,
    DomainSummary,
    publish_mission_summary,
    publish_incident_summary,
    publish_insight_summary
)

__all__ = [
    'grace_world_model',
    'GraceWorldModel',
    'WorldKnowledge',
    'world_model_service',
    'WorldModelService',
    'mcp_integration',
    'MCPIntegration',
    'world_model_summary_pipeline',
    'WorldModelSummaryPipeline',
    'DomainSummary',
    'publish_mission_summary',
    'publish_incident_summary',
    'publish_insight_summary',
]


async def initialize_world_model():
    """
    Initialize the complete world model system
    Call this on Grace startup
    """
    # Initialize core world model
    await grace_world_model.initialize()
    
    # Initialize world model service
    await world_model_service.initialize()
    
    # Initialize MCP integration
    await mcp_integration.initialize()
    
    # Initialize summary pipeline
    await world_model_summary_pipeline.initialize()
    
    return {
        'world_model': 'initialized',
        'world_model_service': 'initialized',
        'mcp': 'initialized',
        'summary_pipeline': 'initialized'
    }
