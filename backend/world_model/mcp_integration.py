"""
MCP (Model Context Protocol) Integration for Grace's World Model

Exposes Grace's internal knowledge via MCP so:
- LLMs can query Grace's world model
- External tools can access Grace's knowledge
- Grace can share her understanding
- Full semantic search via RAG

MCP Resources:
- grace://self - Grace's self-knowledge
- grace://system - System knowledge
- grace://user/{username} - User-specific knowledge
- grace://domain/{domain} - Domain knowledge
- grace://timeline - Temporal knowledge

MCP Tools:
- query_world_model - Search Grace's knowledge
- ask_grace - Ask Grace a question
- add_knowledge - Add to Grace's knowledge
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPIntegration:
    """
    Model Context Protocol integration for Grace's world model
    Makes Grace's knowledge accessible to LLMs and external tools
    """
    
    def __init__(self):
        self.mcp_server_id = "grace_world_model"
        self.mcp_version = "0.1.0"
        self._initialized = False
    
    async def initialize(self):
        """Initialize MCP integration"""
        if self._initialized:
            return
        
        logger.info("[MCP] Initializing Model Context Protocol for world model")
        
        # Initialize world model
        from backend.world_model.grace_world_model import grace_world_model
        
        if not grace_world_model._initialized:
            await grace_world_model.initialize()
        
        self._initialized = True
        logger.info("[MCP] MCP integration ready")
    
    def get_mcp_manifest(self) -> Dict[str, Any]:
        """
        Get MCP server manifest
        Describes available resources and tools
        """
        return {
            'server': {
                'id': self.mcp_server_id,
                'version': self.mcp_version,
                'name': "Grace World Model",
                'description': "Access to Grace's internal knowledge and understanding"
            },
            'resources': [
                {
                    'uri': 'grace://self',
                    'name': "Grace's Self-Knowledge",
                    'description': "What Grace knows about herself",
                    'mime_type': 'application/json'
                },
                {
                    'uri': 'grace://system',
                    'name': "System Knowledge",
                    'description': "What Grace knows about her systems",
                    'mime_type': 'application/json'
                },
                {
                    'uri': 'grace://domain/{domain_id}',
                    'name': "Domain Knowledge",
                    'description': "Knowledge for specific domain",
                    'mime_type': 'application/json'
                },
                {
                    'uri': 'grace://timeline',
                    'name': "Temporal Knowledge",
                    'description': "Time-series knowledge and history",
                    'mime_type': 'application/json'
                }
            ],
            'tools': [
                {
                    'name': 'query_world_model',
                    'description': "Query Grace's world model using semantic search",
                    'parameters': {
                        'query': {'type': 'string', 'required': True},
                        'category': {'type': 'string', 'required': False},
                        'top_k': {'type': 'integer', 'default': 5}
                    }
                },
                {
                    'name': 'ask_grace',
                    'description': "Ask Grace a question about herself or her knowledge",
                    'parameters': {
                        'question': {'type': 'string', 'required': True}
                    }
                },
                {
                    'name': 'add_knowledge',
                    'description': "Add knowledge to Grace's world model",
                    'parameters': {
                        'category': {'type': 'string', 'required': True},
                        'content': {'type': 'string', 'required': True},
                        'source': {'type': 'string', 'required': True}
                    }
                }
            ]
        }
    
    async def handle_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle MCP resource request
        
        Args:
            uri: Resource URI (e.g., 'grace://self')
        
        Returns:
            Resource content
        """
        from backend.world_model.grace_world_model import grace_world_model
        
        logger.info(f"[MCP] Resource request: {uri}")
        
        if uri == 'grace://self':
            # Return self-knowledge
            knowledge = grace_world_model.get_self_knowledge()
            
            return {
                'uri': uri,
                'content': [k.to_dict() for k in knowledge],
                'mime_type': 'application/json',
                'accessed_at': datetime.utcnow().isoformat()
            }
        
        elif uri == 'grace://system':
            # Return system knowledge
            knowledge = grace_world_model.get_system_knowledge()
            
            return {
                'uri': uri,
                'content': [k.to_dict() for k in knowledge],
                'mime_type': 'application/json',
                'accessed_at': datetime.utcnow().isoformat()
            }
        
        elif uri.startswith('grace://domain/'):
            # Return domain-specific knowledge
            domain_id = uri.replace('grace://domain/', '')
            
            knowledge = await grace_world_model.query(
                query=f"domain:{domain_id}",
                category='domain'
            )
            
            return {
                'uri': uri,
                'content': [k.to_dict() for k in knowledge],
                'mime_type': 'application/json',
                'accessed_at': datetime.utcnow().isoformat()
            }
        
        elif uri == 'grace://timeline':
            # Return temporal knowledge
            knowledge_items = [
                grace_world_model.knowledge_base[kid]
                for kid in grace_world_model.categories['temporal']
                if kid in grace_world_model.knowledge_base
            ]
            
            return {
                'uri': uri,
                'content': [k.to_dict() for k in knowledge_items],
                'mime_type': 'application/json',
                'accessed_at': datetime.utcnow().isoformat()
            }
        
        else:
            return {
                'error': 'unknown_resource',
                'uri': uri
            }
    
    async def handle_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle MCP tool call
        
        Args:
            tool_name: Name of tool
            parameters: Tool parameters
        
        Returns:
            Tool execution result
        """
        from backend.world_model.grace_world_model import grace_world_model
        
        logger.info(f"[MCP] Tool call: {tool_name}")
        
        if tool_name == 'query_world_model':
            # Query world model
            results = await grace_world_model.query(
                query=parameters['query'],
                category=parameters.get('category'),
                top_k=parameters.get('top_k', 5)
            )
            
            return {
                'tool': tool_name,
                'results': [k.to_dict() for k in results],
                'total_results': len(results)
            }
        
        elif tool_name == 'ask_grace':
            # Ask Grace a question
            answer = await grace_world_model.ask_self(
                question=parameters['question']
            )
            
            return {
                'tool': tool_name,
                'question': parameters['question'],
                'answer': answer
            }
        
        elif tool_name == 'add_knowledge':
            # Add knowledge
            knowledge_id = await grace_world_model.add_knowledge(
                category=parameters['category'],
                content=parameters['content'],
                source=parameters['source']
            )
            
            return {
                'tool': tool_name,
                'success': True,
                'knowledge_id': knowledge_id
            }
        
        else:
            return {
                'error': 'unknown_tool',
                'tool': tool_name
            }


# Singleton instance
mcp_integration = MCPIntegration()
