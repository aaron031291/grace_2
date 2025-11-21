"""
Agentic Connectivity Protocol
Standardized schema for agents to request help and provide answers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class AgentRequest(BaseModel):
    """A request for help from one agent to another"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str
    target_capability: str  # e.g., "research", "code_review", "security_scan"
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_agent": self.source_agent,
            "target_capability": self.target_capability,
            "query": self.query,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class AgentResponse(BaseModel):
    """A response to an agent request"""
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    source_agent: str
    content: str
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "success"  # success, failure, partial
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "source_agent": self.source_agent,
            "content": self.content,
            "artifacts": self.artifacts,
            "status": self.status,
            "timestamp": self.timestamp.isoformat()
        }

class AgentProtocol:
    """Helper for using the protocol"""
    
    TOPIC_REQUEST = "agent.request"
    TOPIC_RESPONSE = "agent.response"
    
    @staticmethod
    def create_request(source: str, capability: str, query: str, context: Dict = None) -> AgentRequest:
        return AgentRequest(
            source_agent=source,
            target_capability=capability,
            query=query,
            context=context or {}
        )
    
    @staticmethod
    def create_response(request_id: str, source: str, content: str, artifacts: List = None) -> AgentResponse:
        return AgentResponse(
            request_id=request_id,
            source_agent=source,
            content=content,
            artifacts=artifacts or []
        )
