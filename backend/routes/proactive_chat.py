"""
Proactive Chat System - Grace initiates conversations
Grace can send notifications, ask questions, discuss ideas
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
from ..base_models import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

router = APIRouter(prefix="/api/proactive", tags=["proactive"])

# Active WebSocket connections for proactive messaging
active_connections: List[WebSocket] = []

class ProactiveMessage(Base):
    """Messages initiated by Grace"""
    __tablename__ = "proactive_messages"
    
    id = Column(Integer, primary_key=True)
    message_type = Column(String(50))  # notification, question, idea, consensus_request
    content = Column(Text)
    domain = Column(String(50))
    priority = Column(String(20))  # critical, high, normal, low
    requires_response = Column(Boolean, default=False)
    user_response = Column(Text, nullable=True)
    status = Column(String(20), default="sent")  # sent, acknowledged, responded, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

# ===== Proactive Messaging Functions =====

async def grace_notify(message: str, domain: str = "core", priority: str = "normal"):
    """Grace sends a notification to user"""
    await broadcast_to_users({
        "type": "notification",
        "content": message,
        "domain": domain,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "from": "grace"
    })

async def grace_ask(question: str, domain: str = "core", context: Dict = None):
    """Grace asks user a question"""
    await broadcast_to_users({
        "type": "question",
        "content": question,
        "domain": domain,
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "from": "grace",
        "requires_response": True
    })

async def grace_propose(idea: str, domain: str = "core", rationale: str = None):
    """Grace proposes an idea for discussion"""
    await broadcast_to_users({
        "type": "idea",
        "content": idea,
        "rationale": rationale,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "from": "grace",
        "requires_response": True
    })

async def grace_seek_consensus(topic: str, options: List[str], domain: str = "core"):
    """Grace asks for consensus on a decision"""
    await broadcast_to_users({
        "type": "consensus_request",
        "content": topic,
        "options": options,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "from": "grace",
        "requires_response": True
    })

async def broadcast_to_users(message: Dict[str, Any]):
    """Broadcast message to all connected users"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            active_connections.remove(connection)

# ===== WebSocket for Bidirectional Communication =====

@router.websocket("/ws")
async def proactive_websocket(websocket: WebSocket):
    """
    Bidirectional WebSocket - Grace can initiate conversations
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send welcome message from Grace
    await websocket.send_json({
        "type": "system",
        "content": "[AI] Grace is now online and can proactively reach out to you.",
        "domain": "core",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Listen for user messages AND send Grace's proactive messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle user response to Grace's questions
            if message.get("type") == "response":
                await handle_user_response(message)
            
            # Echo back for testing
            await websocket.send_json({
                "type": "echo",
                "content": f"Received: {message.get('content', '')}",
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def handle_user_response(message: Dict):
    """Process user's response to Grace's question/idea"""
    # Store response, update consensus, etc.
    pass

# ===== Background Task: Grace's Autonomous Thinking =====

async def grace_autonomous_loop():
    """
    Grace's background loop - she thinks and reaches out proactively
    """
    await asyncio.sleep(10)  # Initial delay
    
    while True:
        try:
            # Example: Grace detects something and notifies user
            await grace_notify(
                "I've analyzed recent system metrics and noticed an optimization opportunity. Would you like to discuss?",
                domain="meta_loop",
                priority="normal"
            )
            
            await asyncio.sleep(120)  # Check every 2 minutes
            
            # Example: Grace asks for input
            await grace_ask(
                "I'm planning to scale down resources during low-traffic hours. Should I proceed with this optimization?",
                domain="resource",
                context={"current_usage": "45%", "projected_savings": "20%"}
            )
            
            await asyncio.sleep(180)  # Check every 3 minutes
            
        except Exception as e:
            print(f"Autonomous loop error: {e}")
            await asyncio.sleep(60)

# Export functions for use by other Grace subsystems
__all__ = ['grace_notify', 'grace_ask', 'grace_propose', 'grace_seek_consensus', 'router']
