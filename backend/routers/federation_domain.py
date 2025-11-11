"""
Federation Domain Router
Consolidates all external system integrations: webhooks, connectors, OAuth flows

Bounded Context: External system integrations
- Webhooks: incoming webhook handling and processing
- Connectors: external API connections and management
- OAuth: authentication flows and token management
- Dispatch: outgoing event distribution

Canonical Verbs: connect, webhook, dispatch, authenticate, sync
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..integration_orchestrator import integration_orchestrator
from ..webhook_manager import webhook_manager
from ..oauth_manager import oauth_manager

router = APIRouter(prefix="/api/federation", tags=["Federation Domain"])


class ConnectorRequest(BaseModel):
    system_name: str
    system_type: str  # "slack", "github", "pagerduty", "webhook"
    config: Dict[str, Any]
    enabled: bool = True


class WebhookRequest(BaseModel):
    system: str
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None


class DispatchRequest(BaseModel):
    target_system: str
    event_type: str
    payload: Dict[str, Any]
    priority: str = "normal"


class OAuthRequest(BaseModel):
    provider: str
    scope: List[str]
    redirect_uri: Optional[str] = None


class SyncRequest(BaseModel):
    system: str
    resource_type: str
    sync_direction: str = "pull"  # "pull", "push", "bidirectional"
    filters: Optional[Dict[str, Any]] = None


@router.post("/connect")
async def create_connector(
    request: ConnectorRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new external system connector"""
    try:
        connector = await integration_orchestrator.create_connector(
            system_name=request.system_name,
            system_type=request.system_type,
            config=request.config,
            enabled=request.enabled
        )

        return {
            "connector_id": connector.get("id"),
            "system_name": request.system_name,
            "system_type": request.system_type,
            "status": "connected" if request.enabled else "disabled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def process_webhook(
    request: WebhookRequest
) -> Dict[str, Any]:
    """Process incoming webhook (no auth required for webhooks)"""
    try:
        result = await webhook_manager.process_webhook(
            system=request.system,
            event_type=request.event_type,
            payload=request.payload,
            signature=request.signature
        )

        return {
            "system": request.system,
            "event_type": request.event_type,
            "processed": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dispatch")
async def dispatch_event(
    request: DispatchRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Dispatch event to external system"""
    try:
        dispatch = await integration_orchestrator.dispatch_event(
            target_system=request.target_system,
            event_type=request.event_type,
            payload=request.payload,
            priority=request.priority
        )

        return {
            "dispatch_id": dispatch.get("id"),
            "target_system": request.target_system,
            "event_type": request.event_type,
            "status": "dispatched",
            "priority": request.priority
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/oauth/initiate")
async def initiate_oauth(
    request: OAuthRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Initiate OAuth flow"""
    try:
        oauth_flow = await oauth_manager.initiate_flow(
            provider=request.provider,
            scope=request.scope,
            user_id=current_user,
            redirect_uri=request.redirect_uri
        )

        return {
            "flow_id": oauth_flow.get("id"),
            "provider": request.provider,
            "auth_url": oauth_flow.get("auth_url"),
            "scope": request.scope,
            "status": "initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_data(
    request: SyncRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Synchronize data with external system"""
    try:
        sync = await integration_orchestrator.sync_data(
            system=request.system,
            resource_type=request.resource_type,
            direction=request.sync_direction,
            filters=request.filters
        )

        return {
            "sync_id": sync.get("id"),
            "system": request.system,
            "resource_type": request.resource_type,
            "direction": request.sync_direction,
            "status": "syncing",
            "records_processed": sync.get("processed", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connectors")
async def list_connectors(
    system_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List configured connectors"""
    try:
        connectors = await integration_orchestrator.list_connectors(system_type=system_type)
        return {
            "connectors": connectors,
            "count": len(connectors),
            "filter": {"system_type": system_type} if system_type else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks")
async def list_webhooks(
    system: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List webhook configurations"""
    try:
        webhooks = await webhook_manager.list_webhooks(system=system)
        return {
            "webhooks": webhooks,
            "count": len(webhooks),
            "filter": {"system": system} if system else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth/tokens")
async def list_oauth_tokens(
    provider: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List OAuth tokens"""
    try:
        tokens = await oauth_manager.list_tokens(
            user_id=current_user,
            provider=provider
        )
        return {
            "tokens": tokens,
            "count": len(tokens),
            "filter": {"provider": provider} if provider else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/connector/{connector_id}")
async def delete_connector(
    connector_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a connector"""
    try:
        result = await integration_orchestrator.delete_connector(connector_id)
        return {
            "connector_id": connector_id,
            "status": "deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/oauth/refresh/{token_id}")
async def refresh_oauth_token(
    token_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Refresh an OAuth token"""
    try:
        refresh = await oauth_manager.refresh_token(token_id, current_user)
        return {
            "token_id": token_id,
            "status": "refreshed",
            "expires_at": refresh.get("expires_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status")
async def get_sync_status(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get synchronization status"""
    try:
        status = await integration_orchestrator.get_sync_status()
        return {
            "sync_status": status,
            "active_syncs": len([s for s in status if s.get("status") == "active"]),
            "total_syncs": len(status)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{connector_id}")
async def test_connector(
    connector_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test a connector configuration"""
    try:
        test_result = await integration_orchestrator.test_connector(connector_id)
        return {
            "connector_id": connector_id,
            "test_result": test_result,
            "status": "success" if test_result.get("success") else "failed",
            "details": test_result.get("details", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))