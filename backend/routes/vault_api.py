"""
Vault API - Secrets Management Endpoints

Provides:
- POST /api/vault/secrets - Store secret
- GET /api/vault/secrets - List secrets (metadata only)
- GET /api/vault/secrets/{name} - Retrieve secret value
- DELETE /api/vault/secrets/{name} - Revoke secret
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

try:
    from ..security.secrets_vault import secrets_vault
except ImportError:
    # Fallback if path differs
    from backend.security.secrets_vault import secrets_vault

try:
    from ..security.auth import get_current_user
except ImportError:
    from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/vault", tags=["vault"])


# ==================== Request Models ====================

class SecretCreate(BaseModel):
    """Request to create/store a secret"""
    name: str = Field(..., description="Secret identifier/name")
    value: str = Field(..., description="Secret value (will be encrypted)")
    secret_type: str = Field(default="api_key", description="Type: api_key, token, password, etc.")
    service: Optional[str] = Field(None, description="Service this secret belongs to")
    description: Optional[str] = Field(None, description="Human-readable description")
    expires_in_days: Optional[int] = Field(None, description="Auto-expire after N days")
    rotation_days: Optional[int] = Field(None, description="Rotation reminder after N days")


class SecretUpdate(BaseModel):
    """Request to update a secret"""
    value: Optional[str] = None
    description: Optional[str] = None
    expires_in_days: Optional[int] = None


# ==================== Endpoints ====================

@router.post("/secrets")
async def create_secret(
    secret: SecretCreate,
    current_user: str = Depends(get_current_user)
):
    """
    Store a new secret in the vault.
    
    The secret value will be encrypted at rest.
    All access is logged for audit purposes.
    """
    try:
        # Handle both dict and str user types
        username = current_user if isinstance(current_user, str) else current_user.get("username", "unknown")
        
        result = await secrets_vault.store_secret(
            secret_key=secret.name,
            secret_value=secret.value,
            secret_type=secret.secret_type,
            owner=username,
            service=secret.service,
            description=secret.description,
            expires_in_days=secret.expires_in_days,
            rotation_days=secret.rotation_days
        )
        
        return {
            "status": "success",
            "message": f"Secret '{secret.name}' stored successfully",
            "secret_key": secret.name,
            "created_at": result.get("created_at"),
            "encrypted": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/secrets")
async def list_secrets(
    service: Optional[str] = None,
    include_inactive: bool = False,
    current_user: str = Depends(get_current_user)
):
    """
    List all secrets (metadata only, not values).
    
    Query Parameters:
    - service: Filter by service name
    - include_inactive: Include revoked/expired secrets
    
    Returns metadata only - use GET /secrets/{name} to retrieve values.
    """
    try:
        username = current_user if isinstance(current_user, str) else current_user.get("username", "unknown")
        
        secrets = await secrets_vault.list_secrets(
            owner=username,
            service=service,
            include_inactive=include_inactive
        )
        
        return {
            "secrets": secrets,
            "count": len(secrets)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/secrets/{name}")
async def get_secret(
    name: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve a secret value from the vault.
    
    Access is logged for audit purposes.
    Requires proper authentication.
    """
    try:
        username = current_user if isinstance(current_user, str) else current_user.get("username", "unknown")
        
        secret_value = await secrets_vault.retrieve_secret(
            secret_key=name,
            accessor=username
        )
        
        if secret_value is None:
            raise HTTPException(status_code=404, detail=f"Secret '{name}' not found")
        
        return {
            "secret_key": name,
            "secret_value": secret_value,
            "accessed_by": username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/secrets/{name}")
async def revoke_secret(
    name: str,
    reason: str = "User requested revocation",
    current_user: str = Depends(get_current_user)
):
    """
    Revoke/delete a secret from the vault.
    
    The secret will be marked as inactive and cannot be retrieved.
    This action is logged and cannot be undone.
    """
    try:
        username = current_user if isinstance(current_user, str) else current_user.get("username", "unknown")
        
        result = await secrets_vault.revoke_secret(
            secret_key=name,
            actor=username,
            reason=reason
        )
        
        return {
            "status": "success",
            "message": f"Secret '{name}' revoked successfully",
            "revoked_by": username,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def vault_health():
    """Health check for vault service"""
    try:
        # Try to list secrets as a health check
        secrets = await secrets_vault.list_secrets(owner="system", include_inactive=False)
        return {
            "status": "healthy",
            "vault_available": True,
            "total_secrets": len(secrets) if secrets else 0
        }
    except Exception as e:
        return {
            "status": "degraded",
            "vault_available": False,
            "error": str(e)
        }
