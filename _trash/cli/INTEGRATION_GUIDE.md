# Grace CLI - Backend Integration Guide

This guide explains how the Grace CLI integrates with the Grace backend and how to extend it.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                   Grace CLI                      │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │     Enhanced Grace CLI (Main)            │  │
│  │  - Menu system                            │  │
│  │  - Authentication                         │  │
│  │  - Plugin management                      │  │
│  └──────────────────────────────────────────┘  │
│           │                                      │
│           ▼                                      │
│  ┌──────────────────────────────────────────┐  │
│  │     Grace API Client                      │  │
│  │  - REST API calls                         │  │
│  │  - WebSocket connections                  │  │
│  │  - Authentication tokens                  │  │
│  │  - Retry logic                            │  │
│  └──────────────────────────────────────────┘  │
│           │                                      │
└───────────┼──────────────────────────────────────┘
            │
            │ HTTP/WebSocket
            ▼
┌─────────────────────────────────────────────────┐
│              Grace Backend                       │
│                                                  │
│  FastAPI Server (localhost:8000)                │
│  - /api/auth/*        Authentication            │
│  - /api/chat          Chat with Grace           │
│  - /api/tasks/*       Task management           │
│  - /api/knowledge/*   Knowledge base            │
│  - /api/hunter/*      Security alerts           │
│  - /api/governance/*  Approval workflow         │
│  - /api/verification/* Audit logs               │
│  - /ws/*              WebSocket endpoints       │
└─────────────────────────────────────────────────┘
```

## API Endpoint Mapping

### Authentication

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.register()` | `/api/auth/register` | POST |
| `client.login()` | `/api/auth/login` | POST |

**Request/Response**:
```python
# Registration
response = await client.register("username", "password")
# Returns: {"access_token": "...", "token_type": "bearer"}

# Login
response = await client.login("username", "password")
# Returns: {"access_token": "...", "token_type": "bearer"}
```

### Chat

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.chat()` | `/api/chat` | POST |
| `client.get_chat_history()` | `/api/memory/history` | GET |

**Request/Response**:
```python
# Send message
response = await client.chat("Hello Grace")
# Request: {"message": "Hello Grace"}
# Returns: {"response": "Hello! How can I help?"}

# Get history
response = await client.get_chat_history(limit=50)
# Returns: {"history": [...]}
```

### Tasks

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.list_tasks()` | `/api/tasks` | GET |
| `client.create_task()` | `/api/tasks` | POST |
| `client.update_task()` | `/api/tasks/{id}` | PUT |
| `client.delete_task()` | `/api/tasks/{id}` | DELETE |
| `client.complete_task()` | `/api/tasks/{id}` | PUT |

**Request/Response**:
```python
# List tasks
response = await client.list_tasks(status="pending")
# Returns: {"tasks": [{id, title, status, priority, ...}]}

# Create task
response = await client.create_task(
    title="My task",
    description="Task description",
    priority="high"
)
# Returns: {"task": {id, title, ...}}
```

### Knowledge Base

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.ingest_url()` | `/api/ingest/url` | POST |
| `client.search_knowledge()` | `/api/knowledge/search` | GET |
| `client.get_knowledge_items()` | `/api/knowledge` | GET |

**Request/Response**:
```python
# Ingest URL
response = await client.ingest_url("https://example.com", trust_score=0.8)
# Request: {"url": "...", "trust_score": 0.8}
# Returns: {"knowledge_item": {...}, "embedding_id": 123}

# Search
response = await client.search_knowledge("AI ethics", limit=10)
# Returns: {"results": [{title, content, trust_score, ...}]}
```

### Security (Hunter)

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.get_alerts()` | `/api/hunter/alerts` | GET |
| `client.acknowledge_alert()` | `/api/hunter/alerts/{id}/ack` | POST |

**Request/Response**:
```python
# Get alerts
response = await client.get_alerts(severity="critical", limit=50)
# Returns: {"alerts": [{id, severity, alert_type, message, ...}]}

# Acknowledge
response = await client.acknowledge_alert(alert_id=42)
# Returns: {"status": "acknowledged"}
```

### Governance

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.get_approval_requests()` | `/api/governance/requests` | GET |
| `client.approve_request()` | `/api/governance/requests/{id}/approve` | POST |
| `client.reject_request()` | `/api/governance/requests/{id}/reject` | POST |

**Request/Response**:
```python
# Get requests
response = await client.get_approval_requests(status="pending")
# Returns: {"requests": [{id, status, request_type, requester, ...}]}

# Approve
response = await client.approve_request(request_id=42, comment="LGTM")
# Returns: {"status": "approved", "request": {...}}
```

### Verification

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.get_audit_log()` | `/api/verification/audit` | GET |
| `client.get_verification_stats()` | `/api/verification/stats` | GET |
| `client.get_failed_verifications()` | `/api/verification/failed` | GET |

**Request/Response**:
```python
# Audit log
response = await client.get_audit_log(
    limit=100,
    actor="alice",
    hours_back=24
)
# Returns: {"audit_log": [{timestamp, actor, action_type, ...}]}

# Statistics
response = await client.get_verification_stats(hours_back=24)
# Returns: {"total_verifications": 100, "successful_verifications": 95, ...}
```

### Voice/Audio

| CLI Method | Backend Endpoint | HTTP Method |
|------------|------------------|-------------|
| `client.upload_audio()` | `/api/audio/upload` | POST (multipart) |
| `client.text_to_speech()` | `/api/audio/tts` | POST |

**Request/Response**:
```python
# Upload audio
response = await client.upload_audio(Path("recording.wav"))
# Returns: {"transcription": "...", "confidence": 0.95}

# Text to speech
response = await client.text_to_speech("Hello world")
# Returns: {"audio_url": "...", "audio_data": "base64..."}
```

## WebSocket Integration

### Real-Time Updates

The CLI supports WebSocket connections for real-time updates:

```python
# Chat updates
async for message in client.chat_stream():
    print(f"New message: {message}")

# Task updates
async for update in client.task_updates():
    print(f"Task updated: {update}")

# Alert stream
async for alert in client.alert_stream():
    print(f"New alert: {alert}")
```

### WebSocket Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/ws/chat` | Real-time chat messages |
| `/ws/tasks` | Task updates |
| `/ws/alerts` | Security alert notifications |
| `/ws/ide` | IDE file system events |

## Adding New Commands

### 1. Create Command Module

Create `commands/my_command.py`:

```python
from rich.console import Console
from ..grace_client import GraceAPIClient

class MyCommand:
    """My custom command"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, *args):
        """Execute the command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        # Your command logic here
        response = await self.client.some_api_call()
        
        if response.success:
            self.console.print("[green]Success![/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
```

### 2. Add to Client

Add method to `grace_client.py`:

```python
async def some_api_call(self, param: str) -> GraceResponse:
    """Call new API endpoint"""
    return await self._request(
        "POST",
        "/api/my-endpoint",
        data={"param": param}
    )
```

### 3. Register Command

In `enhanced_grace_cli.py`:

```python
from commands import MyCommand

class EnhancedGraceCLI:
    def _init_commands(self):
        self.commands = {
            # ... existing commands
            'mycommand': MyCommand(self.client, console),
        }
```

### 4. Add to Menu

```python
menu_items = [
    # ... existing items
    ("mycommand", "🎯 My Command"),
]
```

## Extending the Client

### Custom Headers

```python
class CustomClient(GraceAPIClient):
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        headers["X-Custom-Header"] = "value"
        return headers
```

### Request Signing

For signed requests (verification integration):

```python
import hashlib
import hmac

async def _request(self, method: str, endpoint: str, **kwargs):
    # Sign request
    timestamp = str(int(time.time()))
    message = f"{method}{endpoint}{timestamp}"
    signature = hmac.new(
        self.secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = kwargs.get("headers", {})
    headers.update({
        "X-Timestamp": timestamp,
        "X-Signature": signature
    })
    kwargs["headers"] = headers
    
    return await super()._request(method, endpoint, **kwargs)
```

### WebSocket Authentication

```python
async def connect_websocket(self, endpoint: str):
    ws_url = f"{self.ws_url}{endpoint}"
    
    # Add token to connection
    if self.token:
        ws_url += f"?token={self.token}"
    
    ws = await websockets.connect(ws_url)
    return ws
```

## Error Handling

### Retry Logic

The client includes automatic retry logic:

```python
async def _request(self, method, endpoint, data=None, retry=3):
    for attempt in range(retry):
        try:
            response = await self._client.request(...)
            return GraceResponse(success=True, data=response.json())
        except httpx.HTTPStatusError as e:
            if attempt == retry - 1:
                return GraceResponse(success=False, error=str(e))
            await asyncio.sleep(1 * (attempt + 1))
```

### Custom Error Handling

```python
class MyCommand:
    async def execute(self):
        try:
            response = await self.client.some_call()
            if not response.success:
                self.handle_error(response.error)
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
    
    def handle_error(self, error: str):
        if "401" in error:
            self.console.print("[yellow]Please login again[/yellow]")
        elif "404" in error:
            self.console.print("[yellow]Resource not found[/yellow]")
        else:
            self.console.print(f"[red]Error: {error}[/red]")
```

## Testing Integration

### Mock Backend

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_my_command(mocker):
    client = Mock(spec=GraceAPIClient)
    client.is_authenticated.return_value = True
    client.some_call = AsyncMock(return_value=GraceResponse(
        success=True,
        data={"result": "test"}
    ))
    
    console = Console()
    cmd = MyCommand(client, console)
    
    await cmd.execute()
    
    client.some_call.assert_called_once()
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_full_integration():
    # This requires backend to be running
    async with GraceAPIClient() as client:
        # Test health
        health = await client.health_check()
        assert health.success
        
        # Test auth (use test credentials)
        response = await client.login("test_user", "test_pass")
        assert response.success
```

## Configuration

### Backend URL

Change in config:

```yaml
backend_url: http://localhost:8000  # Default
# backend_url: http://production:8000  # Production
# backend_url: http://staging:8000  # Staging
```

### Timeouts

```python
client = GraceAPIClient(
    base_url="http://localhost:8000",
    timeout=60  # 60 seconds
)
```

### Connection Pooling

```python
# The client uses httpx with connection pooling by default
# Customize limits:
import httpx

async def connect(self):
    self._client = httpx.AsyncClient(
        base_url=self.base_url,
        timeout=self.timeout,
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100
        )
    )
```

## Performance Tips

1. **Reuse Client**: Create one client instance
2. **Use Context Manager**: Properly cleanup connections
3. **Batch Requests**: Group related API calls
4. **Cache Results**: Cache frequently accessed data
5. **WebSocket for Updates**: Use WebSocket instead of polling

## Security

1. **Token Storage**: Tokens stored in system keyring
2. **HTTPS**: Use HTTPS in production
3. **Token Expiry**: Implement token refresh
4. **Request Signing**: Sign sensitive requests
5. **Input Validation**: Validate all user input

## Troubleshooting

### Connection Issues

```python
# Test connection
async with GraceAPIClient() as client:
    health = await client.health_check()
    if health.success:
        print("✓ Connected")
    else:
        print(f"✗ Connection failed: {health.error}")
```

### Authentication Issues

```python
# Check token
if client.token:
    print(f"Token: {client.token[:10]}...")
else:
    print("Not authenticated")

# Re-login
await client.login(username, password)
```

### Debug Mode

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use httpx event hooks
client._client.event_hooks = {
    'request': [lambda r: print(f"Request: {r.method} {r.url}")],
    'response': [lambda r: print(f"Response: {r.status_code}")]
}
```

## Next Steps

- **Add Custom Commands**: Create your own commands
- **Extend API Client**: Add new endpoint methods
- **Build Plugins**: Create plugins for custom workflows
- **Contribute**: Submit improvements to the project

For more information, see:
- [README.md](README.md) - User documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- Backend API docs: http://localhost:8000/docs
