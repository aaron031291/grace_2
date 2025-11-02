"""
Grace API Client - Full backend integration with REST and WebSocket support
"""

import asyncio
import json
from typing import Optional, Dict, Any, List, AsyncIterator
from datetime import datetime, timedelta
import httpx
import websockets
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GraceResponse:
    """Standard response wrapper"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class GraceAPIClient:
    """Full-featured Grace API client with authentication and verification"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.timeout = timeout
        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._ws_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP client"""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
    
    async def disconnect(self):
        """Close connections"""
        if self._client:
            await self._client.aclose()
        for ws in self._ws_connections.values():
            await ws.close()
        self._ws_connections.clear()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry: int = 3
    ) -> GraceResponse:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retry):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 401:
                    return GraceResponse(success=False, error="Authentication required")
                
                response.raise_for_status()
                result = response.json()
                return GraceResponse(success=True, data=result)
                
            except httpx.HTTPStatusError as e:
                if attempt == retry - 1:
                    return GraceResponse(success=False, error=f"HTTP {e.response.status_code}: {e.response.text}")
                await asyncio.sleep(1 * (attempt + 1))
            except httpx.RequestError as e:
                if attempt == retry - 1:
                    return GraceResponse(success=False, error=f"Request failed: {str(e)}")
                await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                return GraceResponse(success=False, error=f"Unexpected error: {str(e)}")
        
        return GraceResponse(success=False, error="Max retries exceeded")
    
    # Authentication
    
    async def register(self, username: str, password: str) -> GraceResponse:
        """Register new user"""
        response = await self._request(
            "POST",
            "/api/auth/register",
            data={"username": username, "password": password}
        )
        if response.success and response.data:
            self.token = response.data.get("access_token")
            self.username = username
        return response
    
    async def login(self, username: str, password: str) -> GraceResponse:
        """Authenticate user"""
        response = await self._request(
            "POST",
            "/api/auth/login",
            data={"username": username, "password": password}
        )
        if response.success and response.data:
            self.token = response.data.get("access_token")
            self.username = username
        return response
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.token is not None
    
    # Chat
    
    async def chat(self, message: str) -> GraceResponse:
        """Send chat message to Grace"""
        return await self._request(
            "POST",
            "/api/chat",
            data={"message": message}
        )
    
    async def get_chat_history(self, limit: int = 50) -> GraceResponse:
        """Get chat history"""
        return await self._request(
            "GET",
            "/api/memory/history",
            params={"limit": limit}
        )
    
    # Tasks
    
    async def list_tasks(self, status: Optional[str] = None) -> GraceResponse:
        """List tasks"""
        params = {"status": status} if status else {}
        return await self._request("GET", "/api/tasks", params=params)
    
    async def create_task(self, title: str, description: str = "", priority: str = "medium") -> GraceResponse:
        """Create new task"""
        return await self._request(
            "POST",
            "/api/tasks",
            data={"title": title, "description": description, "priority": priority}
        )
    
    async def update_task(self, task_id: int, **kwargs) -> GraceResponse:
        """Update task"""
        return await self._request(
            "PUT",
            f"/api/tasks/{task_id}",
            data=kwargs
        )
    
    async def delete_task(self, task_id: int) -> GraceResponse:
        """Delete task"""
        return await self._request("DELETE", f"/api/tasks/{task_id}")
    
    async def complete_task(self, task_id: int) -> GraceResponse:
        """Mark task as completed"""
        return await self.update_task(task_id, status="completed")
    
    # Knowledge
    
    async def ingest_url(self, url: str, trust_score: Optional[float] = None) -> GraceResponse:
        """Ingest knowledge from URL"""
        data = {"url": url}
        if trust_score is not None:
            data["trust_score"] = trust_score
        return await self._request("POST", "/api/ingest/url", data=data)
    
    async def search_knowledge(self, query: str, limit: int = 10) -> GraceResponse:
        """Search knowledge base"""
        return await self._request(
            "GET",
            "/api/knowledge/search",
            params={"query": query, "limit": limit}
        )
    
    async def get_knowledge_items(self, limit: int = 50) -> GraceResponse:
        """Get knowledge items"""
        return await self._request(
            "GET",
            "/api/knowledge",
            params={"limit": limit}
        )
    
    # Hunter (Security Alerts)
    
    async def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> GraceResponse:
        """Get security alerts"""
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        return await self._request("GET", "/api/hunter/alerts", params=params)
    
    async def acknowledge_alert(self, alert_id: int) -> GraceResponse:
        """Acknowledge security alert"""
        return await self._request("POST", f"/api/hunter/alerts/{alert_id}/ack")
    
    # Governance
    
    async def get_approval_requests(self, status: Optional[str] = None) -> GraceResponse:
        """Get governance approval requests"""
        params = {"status": status} if status else {}
        return await self._request("GET", "/api/governance/requests", params=params)
    
    async def approve_request(self, request_id: int, comment: str = "") -> GraceResponse:
        """Approve governance request"""
        return await self._request(
            "POST",
            f"/api/governance/requests/{request_id}/approve",
            data={"comment": comment}
        )
    
    async def reject_request(self, request_id: int, reason: str = "") -> GraceResponse:
        """Reject governance request"""
        return await self._request(
            "POST",
            f"/api/governance/requests/{request_id}/reject",
            data={"reason": reason}
        )
    
    # Verification
    
    async def get_audit_log(
        self,
        limit: int = 100,
        actor: Optional[str] = None,
        action_type: Optional[str] = None,
        hours_back: int = 24
    ) -> GraceResponse:
        """Get verification audit log"""
        params = {
            "limit": limit,
            "hours_back": hours_back
        }
        if actor:
            params["actor"] = actor
        if action_type:
            params["action_type"] = action_type
        return await self._request("GET", "/api/verification/audit", params=params)
    
    async def get_verification_stats(self, hours_back: int = 24) -> GraceResponse:
        """Get verification statistics"""
        return await self._request(
            "GET",
            "/api/verification/stats",
            params={"hours_back": hours_back}
        )
    
    async def get_failed_verifications(self, limit: int = 50, hours_back: int = 24) -> GraceResponse:
        """Get failed verifications"""
        return await self._request(
            "GET",
            "/api/verification/failed",
            params={"limit": limit, "hours_back": hours_back}
        )
    
    # Voice/Audio
    
    async def upload_audio(self, audio_path: Path) -> GraceResponse:
        """Upload audio file for transcription"""
        try:
            with open(audio_path, 'rb') as f:
                files = {'file': (audio_path.name, f, 'audio/wav')}
                response = await self._client.post(
                    f"{self.base_url}/api/audio/upload",
                    files=files,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return GraceResponse(success=True, data=response.json())
        except Exception as e:
            return GraceResponse(success=False, error=str(e))
    
    async def text_to_speech(self, text: str) -> GraceResponse:
        """Convert text to speech"""
        return await self._request(
            "POST",
            "/api/audio/tts",
            data={"text": text}
        )
    
    # Meta Loop
    
    async def get_meta_loops(self, active_only: bool = True) -> GraceResponse:
        """Get meta loops"""
        return await self._request(
            "GET",
            "/api/meta/loops",
            params={"active_only": active_only}
        )
    
    async def trigger_meta_loop(self, loop_type: str, context: Dict[str, Any]) -> GraceResponse:
        """Trigger meta loop"""
        return await self._request(
            "POST",
            "/api/meta/trigger",
            data={"loop_type": loop_type, "context": context}
        )
    
    # WebSocket Connections
    
    async def connect_websocket(self, endpoint: str) -> websockets.WebSocketClientProtocol:
        """Connect to WebSocket endpoint"""
        ws_url = f"{self.ws_url}{endpoint}"
        if self.token:
            ws_url += f"?token={self.token}"
        
        ws = await websockets.connect(ws_url)
        self._ws_connections[endpoint] = ws
        return ws
    
    async def chat_stream(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat updates via WebSocket"""
        ws = await self.connect_websocket("/ws/chat")
        try:
            async for message in ws:
                yield json.loads(message)
        finally:
            await ws.close()
    
    async def task_updates(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream task updates via WebSocket"""
        ws = await self.connect_websocket("/ws/tasks")
        try:
            async for message in ws:
                yield json.loads(message)
        finally:
            await ws.close()
    
    async def alert_stream(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream security alerts via WebSocket"""
        ws = await self.connect_websocket("/ws/alerts")
        try:
            async for message in ws:
                yield json.loads(message)
        finally:
            await ws.close()
    
    # Health & Status
    
    async def health_check(self) -> GraceResponse:
        """Check API health"""
        return await self._request("GET", "/health")
    
    async def get_system_status(self) -> GraceResponse:
        """Get system status"""
        return await self._request("GET", "/api/health/status")


# Singleton instance
_client: Optional[GraceAPIClient] = None


def get_client() -> GraceAPIClient:
    """Get or create global client instance"""
    global _client
    if _client is None:
        _client = GraceAPIClient()
    return _client
