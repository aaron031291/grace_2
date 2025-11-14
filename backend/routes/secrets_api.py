"""
Secrets API - Secure Secret Capture and Management

SECURITY:
- Secrets NEVER returned in API responses
- Immediate encryption on receipt
- All access logged
- Governance integrated
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.security.secrets_service import secrets_service, SecretType


router = APIRouter(prefix="/api/secrets", tags=["secrets"])


class StoreSecretRequest(BaseModel):
    """Request to store a secret"""
    name: str = Field(..., description="User-friendly label", example="Stripe API Key")
    value: str = Field(..., description="The secret value (will be encrypted)")
    secret_type: str = Field(..., description="Type of secret", example="api_key")
    scope: str = Field(..., description="What it's for", example="payment_processing")
    environment: str = Field(default="production", example="production")
    service_name: Optional[str] = Field(None, example="Stripe")
    description: Optional[str] = Field(None)
    expires_days: Optional[int] = Field(None, description="Days until expiration")
    high_privilege: bool = Field(default=False, description="Has write/admin access")
    allowed_agents: Optional[List[str]] = Field(default=None, description="Which agents can access")


class StoreSecretResponse(BaseModel):
    """Response after storing secret"""
    secret_id: str
    name: str
    type: str
    encrypted: bool = True
    requires_validation: bool = True
    requires_approval: bool = True
    librarian_task_created: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret_id": "secret_api_key_1234567890",
                "name": "Stripe API Key",
                "type": "api_key",
                "encrypted": True,
                "requires_validation": True,
                "requires_approval": True,
                "librarian_task_created": True
            }
        }


class ListSecretsResponse(BaseModel):
    """List of secrets (metadata only)"""
    secrets: List[Dict[str, Any]]
    total: int


class DetectSecretsRequest(BaseModel):
    """Request to detect secrets/emails in text"""
    text: str


class DetectSecretsResponse(BaseModel):
    """Detection results with governance prompts"""
    secrets_detected: List[Dict[str, Any]]
    emails_detected: List[str]
    requires_confirmation: bool
    redacted_text: str
    prompts: List[Dict[str, Any]]


class StoreContactRequest(BaseModel):
    """Request to store contact with consent"""
    contact_value: str = Field(..., example="user@example.com")
    contact_type: str = Field(..., example="email")
    purpose: str = Field(..., example="login")
    service_name: Optional[str] = Field(None, example="Salesforce")
    consent_given: bool = Field(..., description="User must explicitly consent")


@router.post("/store", response_model=StoreSecretResponse)
async def store_secret(
    request: StoreSecretRequest,
    created_by: str = "ui_user"  # Should come from auth context
) -> StoreSecretResponse:
    """
    Store secret in encrypted vault
    
    SECURITY FLOW:
    1. Secret received over TLS
    2. Immediately encrypted (never logged)
    3. Stored in encrypted table
    4. Librarian task created for validation
    5. Governance approval required
    6. Only masked value returned
    
    The original value is NEVER returned or logged!
    """
    
    secret_id = await secrets_service.store_secret(
        name=request.name,
        value=request.value,  # Encrypted immediately inside store_secret
        secret_type=request.secret_type,
        scope=request.scope,
        created_by=created_by,
        environment=request.environment,
        service_name=request.service_name,
        description=request.description,
        expires_days=request.expires_days,
        high_privilege=request.high_privilege,
        allowed_agents=request.allowed_agents
    )
    
    return StoreSecretResponse(
        secret_id=secret_id,
        name=request.name,
        type=request.secret_type,
        encrypted=True,
        requires_validation=True,
        requires_approval=True,
        librarian_task_created=True
    )


@router.get("/list", response_model=ListSecretsResponse)
async def list_secrets(
    requested_by: str = "ui_user",
    include_inactive: bool = False
) -> ListSecretsResponse:
    """
    List all secrets (metadata only, NO VALUES)
    
    Returns only:
    - Secret ID, name, type, scope
    - Validation status
    - Access counts
    - NEVER the actual secret value
    """
    
    secrets = await secrets_service.list_secrets(
        requested_by=requested_by,
        include_inactive=include_inactive
    )
    
    return ListSecretsResponse(
        secrets=secrets,
        total=len(secrets)
    )


@router.post("/detect", response_model=DetectSecretsResponse)
async def detect_secrets_and_emails(
    request: DetectSecretsRequest
) -> DetectSecretsResponse:
    """
    Detect secrets and emails in text
    
    Returns:
    - Detected secrets (masked)
    - Detected emails
    - Governance prompts for user confirmation
    - Redacted text (safe to display)
    
    UI should call this BEFORE storing any user input!
    """
    
    # Detect secrets
    secrets_detected = secrets_service.detect_secrets(request.text)
    
    # Detect emails
    emails_detected = secrets_service.detect_emails(request.text)
    
    # Generate redacted text (safe to display)
    redacted_text = secrets_service.redact(request.text)
    
    # Generate governance prompts
    prompts = []
    
    for secret in secrets_detected:
        prompts.append({
            "type": "secret_confirmation",
            "severity": "high",
            "message": f"Grace detected an {secret['type'].replace('_', ' ')}. Save securely?",
            "options": ["Yes - Save encrypted", "No - Discard"],
            "metadata": {
                "secret_type": secret['type'],
                "masked_value": secret['masked']
            }
        })
    
    for email in emails_detected:
        prompts.append({
            "type": "email_confirmation",
            "severity": "medium",
            "message": f"Grace detected email address: {email}. Save as contact?",
            "options": ["Yes - Save with purpose", "No - Don't save"],
            "metadata": {
                "email": email,
                "requires_purpose": True
            }
        })
    
    return DetectSecretsResponse(
        secrets_detected=secrets_detected,
        emails_detected=emails_detected,
        requires_confirmation=len(prompts) > 0,
        redacted_text=redacted_text,
        prompts=prompts
    )


@router.post("/contacts/store")
async def store_contact(
    request: StoreContactRequest,
    created_by: str = "ui_user"
) -> Dict[str, Any]:
    """
    Store contact information with explicit consent
    
    REQUIRES: consent_given = True
    Separate from secrets - emails stored only with opt-in
    """
    
    if not request.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Contact storage requires explicit user consent"
        )
    
    contact_id = await secrets_service.store_contact(
        contact_value=request.contact_value,
        contact_type=request.contact_type,
        purpose=request.purpose,
        created_by=created_by,
        service_name=request.service_name,
        consent_given=True
    )
    
    return {
        "contact_id": contact_id,
        "contact_type": request.contact_type,
        "purpose": request.purpose,
        "consent_given": True,
        "stored_at": datetime.now().isoformat()
    }


@router.post("/validate/{secret_id}")
async def validate_secret_endpoint(
    secret_id: str,
    test_endpoint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trigger secret validation
    
    Called by Librarian workflow to test if secret works
    """
    
    validation_passed = await secrets_service.validate_secret(
        secret_id=secret_id,
        validation_method="test_api_call" if test_endpoint else "basic",
        test_endpoint=test_endpoint
    )
    
    return {
        "secret_id": secret_id,
        "validation_passed": validation_passed,
        "validated_at": datetime.now().isoformat()
    }


# Export router
__all__ = ['router']
