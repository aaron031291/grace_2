"""
Grace Chat Bridge - Lightweight backend for UI
Translates Grace's internal bus events into chat-friendly messages
Handles intent commands, approvals, and provides cached state
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import httpx
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Grace Chat Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GRACE_BACKEND = "http://localhost:8000"
ACTIVE_CONNECTIONS: List[WebSocket] = []

# Models
class ChatMessage(BaseModel):
    message: str
    domain: Optional[str] = "chat"

class IntentCommand(BaseModel):
    command: str
    args: Optional[Dict[str, Any]] = {}

class ApprovalRequest(BaseModel):
    recommendation_id: int
    action: str  # "approve" | "reject"
    reason: Optional[str] = None

# Cache for domain state (refreshed periodically)
domain_cache = {
    "health": {},
    "meta_loop": {},
    "self_heal": {},
    "resources": {},
    "last_updated": None
}

# ===== Authentication Proxy =====
async def proxy_auth(username: str, password: str, action: str = "login"):
    """Proxy auth to main Grace backend"""
    async with httpx.AsyncClient() as client:
        url = f"{GRACE_BACKEND}/api/auth/{action}"
        
        try:
            if action == "login":
                response = await client.post(url, json={"username": username, "password": password})
            else:  # register
                response = await client.post(url, json={"username": username, "password": password})
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Grace backend offline")

@app.post("/api/auth/login")
async def login(username: str, password: str):
    return await proxy_auth(username, password, "login")

@app.post("/api/auth/register")
async def register(username: str, password: str):
    return await proxy_auth(username, password, "register")

# ===== Chat Endpoint with Intent Detection =====
@app.post("/api/chat")
async def chat(msg: ChatMessage, token: Optional[str] = None):
    """
    Enhanced chat that detects intents and routes to appropriate domain
    """
    user_msg = msg.message.strip()
    
    # Detect domain intent from message
    detected_domain = detect_domain_intent(user_msg)
    
    # Check for action intents
    if is_action_intent(user_msg):
        return await handle_action_intent(user_msg, detected_domain, token)
    
    # Regular chat - proxy to main backend
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            response = await client.post(
                f"{GRACE_BACKEND}/api/chat",
                json={"message": user_msg},
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", "Received"),
                    "domain": detected_domain,
                    "intent": "conversation"
                }
            else:
                return {"response": "Error from Grace backend", "domain": "core"}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"response": f"Backend error: {str(e)}", "domain": "core"}

def detect_domain_intent(message: str) -> str:
    """Detect which domain the message is about"""
    msg_lower = message.lower()
    
    if any(kw in msg_lower for kw in ['security', 'threat', 'hunter', 'alert', 'scan']):
        return 'security'
    elif any(kw in msg_lower for kw in ['meta', 'governance', 'approval', 'recommendation']):
        return 'meta_loop'
    elif any(kw in msg_lower for kw in ['heal', 'health', 'fix', 'recover', 'playbook']):
        return 'self_heal'
    elif any(kw in msg_lower for kw in ['knowledge', 'ingest', 'search', 'learn']):
        return 'knowledge'
    elif any(kw in msg_lower for kw in ['code', 'generate', 'transcendence', 'ide']):
        return 'transcendence'
    elif any(kw in msg_lower for kw in ['memory', 'remember', 'context']):
        return 'memory'
    elif any(kw in msg_lower for kw in ['resource', 'capacity', 'scale']):
        return 'resource'
    else:
        return 'chat'

def is_action_intent(message: str) -> bool:
    """Check if message is requesting an action"""
    action_words = ['show', 'list', 'get', 'create', 'execute', 'run', 'scale', 'approve', 'reject']
    msg_lower = message.lower()
    return any(word in msg_lower for word in action_words)

async def handle_action_intent(message: str, domain: str, token: Optional[str]) -> Dict:
    """Handle action-oriented messages by calling appropriate backend APIs"""
    msg_lower = message.lower()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with httpx.AsyncClient() as client:
        try:
            # Health/Status queries
            if 'health' in msg_lower or 'status' in msg_lower:
                res = await client.get(f"{GRACE_BACKEND}/health", headers=headers)
                data = res.json()
                return {
                    "response": f"✅ System Status: {json.dumps(data, indent=2)}",
                    "domain": "core",
                    "intent": "status_check",
                    "metadata": data
                }
            
            # Meta loop queries
            elif 'meta' in msg_lower and 'recommendation' in msg_lower:
                res = await client.get(f"{GRACE_BACKEND}/api/meta/recommendations", headers=headers)
                data = res.json()
                return {
                    "response": f"🧠 Meta Recommendations: {len(data)} pending",
                    "domain": "meta_loop",
                    "intent": "list_recommendations",
                    "metadata": data
                }
            
            # Security alerts
            elif 'alert' in msg_lower or 'security' in msg_lower:
                res = await client.get(f"{GRACE_BACKEND}/api/hunter/alerts?limit=10", headers=headers)
                data = res.json()
                return {
                    "response": f"🛡️ Security Alerts: Found {len(data)} alerts",
                    "domain": "security",
                    "intent": "list_alerts",
                    "metadata": data
                }
            
            # Knowledge queries
            elif 'knowledge' in msg_lower or 'artifacts' in msg_lower:
                res = await client.get(f"{GRACE_BACKEND}/api/ingest/artifacts?limit=20", headers=headers)
                data = res.json()
                return {
                    "response": f"📚 Knowledge Base: {len(data)} artifacts",
                    "domain": "knowledge",
                    "intent": "list_knowledge",
                    "metadata": data
                }
            
            # Default: pass to main chat
            else:
                res = await client.post(
                    f"{GRACE_BACKEND}/api/chat",
                    json={"message": message},
                    headers=headers
                )
                data = res.json()
                return {
                    "response": data.get("response", "Received"),
                    "domain": domain,
                    "intent": "conversation"
                }
                
        except Exception as e:
            logger.error(f"Action intent error: {e}")
            return {
                "response": f"Error executing action: {str(e)}",
                "domain": "core"
            }

# ===== WebSocket Event Stream =====
@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    Stream Grace backend events to UI in chat-friendly format
    Subscribes to main Grace WebSocket and translates events
    """
    await websocket.accept()
    ACTIVE_CONNECTIONS.append(websocket)
    
    # Connect to main Grace backend WebSocket
    grace_ws_url = "ws://localhost:8000/ws/cognition"
    
    try:
        async with httpx.AsyncClient() as client:
            # Subscribe to Grace's cognition stream
            try:
                async for event in subscribe_to_grace_events(grace_ws_url):
                    # Translate to chat-friendly format
                    chat_event = translate_event_to_chat(event)
                    await websocket.send_json(chat_event)
            except Exception as e:
                logger.error(f"Grace WS error: {e}")
                await websocket.send_json({
                    "type": "system",
                    "content": "⚠️ Lost connection to Grace event stream",
                    "domain": "core",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        ACTIVE_CONNECTIONS.remove(websocket)
        logger.info("Client disconnected from event stream")

async def subscribe_to_grace_events(ws_url: str):
    """Generator that yields events from Grace backend"""
    # This would connect to actual Grace WebSocket
    # For now, simulate events
    while True:
        await asyncio.sleep(5)
        yield {
            "event_type": "meta_loop_cycle",
            "cycle_number": 1,
            "summary": "System optimization in progress",
            "domain": "meta_loop"
        }

def translate_event_to_chat(event: Dict) -> Dict:
    """Translate internal Grace events to chat UI format"""
    event_type = event.get("event_type", "unknown")
    
    chat_message = {
        "id": f"evt_{datetime.now().timestamp()}",
        "type": "event",
        "domain": event.get("domain", "core"),
        "timestamp": datetime.now().isoformat(),
        "metadata": event
    }
    
    if event_type == "meta_loop_cycle":
        chat_message["type"] = "playbook"
        chat_message["content"] = f"🧠 Meta Loop Cycle {event.get('cycle_number')}: {event.get('summary')}"
    elif event_type == "resource_scaled":
        chat_message["content"] = f"📊 Resource {event.get('action')}: {event.get('resource')}"
    elif event_type == "playbook_executed":
        chat_message["type"] = "playbook"
        chat_message["content"] = f"📋 Playbook: {event.get('playbook_name')} - {event.get('status')}"
    elif event_type == "self_heal_action":
        chat_message["content"] = f"🔧 Self-Heal: {event.get('action')} on {event.get('service')}"
    else:
        chat_message["content"] = event.get("message", f"Event: {event_type}")
    
    return chat_message

# ===== Command Execution with Guardrails =====
@app.post("/api/command")
async def execute_command(cmd: IntentCommand, token: Optional[str] = None):
    """
    Execute slash commands with guardrails and logging
    """
    command = cmd.command.lower()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    logger.info(f"Command: {command} with args: {cmd.args}")
    
    async with httpx.AsyncClient() as client:
        try:
            if command == "status":
                res = await client.get(f"{GRACE_BACKEND}/health", headers=headers)
                return {"success": True, "data": res.json(), "domain": "core"}
            
            elif command == "meta":
                res = await client.get(f"{GRACE_BACKEND}/api/meta/focus", headers=headers)
                return {"success": True, "data": res.json(), "domain": "meta_loop"}
            
            elif command == "playbook":
                # Dry run first, require approval
                return {
                    "success": True,
                    "data": {"message": "Playbook dry-run ready. Approve to execute?"},
                    "domain": "self_heal",
                    "requires_approval": True
                }
            
            elif command == "forecast":
                res = await client.get(f"{GRACE_BACKEND}/api/temporal/forecast", headers=headers)
                return {"success": True, "data": res.json(), "domain": "temporal"}
            
            elif command == "memory":
                query = cmd.args.get("query", "")
                # Proxy to memory API
                return {
                    "success": True,
                    "data": {"message": f"Searching memory for: {query}"},
                    "domain": "memory"
                }
            
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"success": False, "error": str(e)}

# ===== Approval Workflow =====
@app.post("/api/approval")
async def handle_approval(approval: ApprovalRequest, token: Optional[str] = None):
    """
    Handle approval/rejection of recommendations
    Shows in chat before executing
    """
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{GRACE_BACKEND}/api/meta/recommendations/{approval.recommendation_id}/{approval.action}"
            res = await client.post(url, headers=headers, json={"reason": approval.reason})
            
            return {
                "success": True,
                "action": approval.action,
                "recommendation_id": approval.recommendation_id,
                "result": res.json()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ===== Cached Domain State =====
@app.get("/api/state/{domain}")
async def get_domain_state(domain: str, token: Optional[str] = None):
    """
    Return cached/denormalized domain state for dashboard rendering
    """
    if domain in domain_cache and domain_cache["last_updated"]:
        # Check if cache is fresh (< 30 seconds old)
        if (datetime.now().timestamp() - domain_cache["last_updated"]) < 30:
            return domain_cache[domain]
    
    # Fetch fresh data
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with httpx.AsyncClient() as client:
        try:
            if domain == "health":
                res = await client.get(f"{GRACE_BACKEND}/health", headers=headers)
                domain_cache[domain] = res.json()
            elif domain == "meta_loop":
                res = await client.get(f"{GRACE_BACKEND}/api/meta/focus", headers=headers)
                domain_cache[domain] = res.json()
            elif domain == "self_heal":
                # Aggregate self-heal status
                domain_cache[domain] = {
                    "playbooks": "Available",
                    "scheduler": "Running",
                    "mode": "observe_only"
                }
            elif domain == "resources":
                # Resource metrics
                domain_cache[domain] = {
                    "cpu": "45%",
                    "memory": "60%",
                    "capacity": "75%"
                }
            
            domain_cache["last_updated"] = datetime.now().timestamp()
            return domain_cache[domain]
        
        except Exception as e:
            logger.error(f"State fetch error for {domain}: {e}")
            return {"error": str(e)}

# ===== Simulation/Dry Run =====
@app.post("/api/simulate")
async def simulate_action(action: Dict[str, Any], token: Optional[str] = None):
    """
    Run dry-run simulation before actual execution
    Returns projected outcome for user review
    """
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                f"{GRACE_BACKEND}/api/simulation/run",
                json=action,
                headers=headers
            )
            
            return {
                "success": True,
                "simulation": res.json(),
                "requires_approval": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ===== Background Cache Refresh =====
@app.on_event("startup")
async def startup_cache_refresh():
    """Periodically refresh domain cache"""
    asyncio.create_task(cache_refresh_loop())
    logger.info("✓ Grace Chat Bridge started")
    logger.info(f"  Proxying to: {GRACE_BACKEND}")
    logger.info(f"  WebSocket events: /ws/events")

async def cache_refresh_loop():
    """Background task to keep domain cache fresh"""
    while True:
        try:
            await asyncio.sleep(30)
            # Refresh critical domain states
            async with httpx.AsyncClient() as client:
                try:
                    res = await client.get(f"{GRACE_BACKEND}/health")
                    domain_cache["health"] = res.json()
                    domain_cache["last_updated"] = datetime.now().timestamp()
                except:
                    pass
        except Exception as e:
            logger.error(f"Cache refresh error: {e}")

# ===== Health Check =====
@app.get("/health")
async def health():
    """Bridge health check"""
    # Check connection to main backend
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{GRACE_BACKEND}/health", timeout=2.0)
            backend_ok = res.status_code == 200
    except:
        backend_ok = False
    
    return {
        "status": "ok",
        "bridge": "running",
        "backend_connected": backend_ok,
        "active_connections": len(ACTIVE_CONNECTIONS),
        "cache_age": datetime.now().timestamp() - (domain_cache.get("last_updated", 0) or 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
