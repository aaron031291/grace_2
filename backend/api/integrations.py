"""
Integrations API

Safe installation and management of external APIs:
- Stripe, Shopify, HubSpot (business data)
- OpenAI, Hugging Face, Replicate (AI/ML)
- Ethereum, Solana (blockchain)
- AWS, Azure, GCP (cloud infrastructure)

All go through Hunter Bridge + Verification Charter.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/integrations", tags=["Integrations"])


class IntegrationInstallRequest(BaseModel):
    integration_name: str
    vendor: str
    purpose: str
    api_endpoint: str
    auth_method: str
    scopes: List[str]
    risk_level: str  # low, medium, high, critical
    credentials: Optional[Dict[str, str]] = None


@router.post("/install")
async def install_integration(request: IntegrationInstallRequest) -> Dict[str, Any]:
    """
    Install new integration (safe installation flow)
    
    Flow:
    1. Validate request
    2. Hunter Bridge scans for security
    3. Verification Charter checks policy
    4. Submit to Unified Logic if needed
    5. Activate if approved
    """
    
    from backend.governance.verification_charter import get_verification_charter, RiskLevel
    from backend.kernels.hunter_bridge import get_hunter_bridge
    
    charter = get_verification_charter()
    hunter = get_hunter_bridge()
    
    # Step 1: Hunter Bridge security scan
    scan_results = await hunter.scan_integration(
        integration_name=request.integration_name,
        api_endpoint=request.api_endpoint,
        auth_method=request.auth_method,
        scopes=request.scopes
    )
    
    if not scan_results['passed']:
        return {
            "success": False,
            "status": "security_failed",
            "message": "Integration failed security scan",
            "scan_id": scan_results['scan_id'],
            "findings": scan_results['findings'],
            "risk_score": scan_results['risk_score']
        }
    
    # Step 2: Submit to Verification Charter
    risk_enum = RiskLevel[request.risk_level.upper()]
    
    charter_result = await charter.request_integration(
        integration_name=request.integration_name,
        vendor=request.vendor,
        purpose=request.purpose,
        api_endpoint=request.api_endpoint,
        auth_method=request.auth_method,
        scopes=request.scopes,
        risk_level=risk_enum,
        requested_by="user"
    )
    
    return {
        "success": True,
        "status": charter_result['status'],
        "request_id": charter_result['request_id'],
        "scan_passed": True,
        "scan_id": scan_results['scan_id'],
        "risk_score": scan_results['risk_score'],
        "message": charter_result['message'],
        "next_steps": "Wait for approval" if charter_result['status'] == 'pending_approval' else "Integration ready"
    }


@router.get("/pending")
async def get_pending_integrations() -> Dict[str, Any]:
    """Get integrations pending approval"""
    
    from backend.governance.verification_charter import get_verification_charter
    
    charter = get_verification_charter()
    pending = charter.get_pending_requests()
    
    return {
        'pending_requests': pending,
        'count': len(pending),
        'message': 'Submit to Unified Logic for approval'
    }


@router.post("/approve/{request_id}")
async def approve_integration(
    request_id: str,
    approved_by: str = "admin",
    notes: str = ""
) -> Dict[str, Any]:
    """Approve pending integration"""
    
    from backend.governance.verification_charter import get_verification_charter
    
    charter = get_verification_charter()
    success = await charter.approve_integration(request_id, approved_by, notes)
    
    if success:
        return {
            "success": True,
            "status": "approved",
            "request_id": request_id,
            "approved_by": approved_by,
            "message": "Integration approved and added to whitelist"
        }
    else:
        raise HTTPException(status_code=404, detail="Request not found")


@router.post("/reject/{request_id}")
async def reject_integration(
    request_id: str,
    rejected_by: str = "admin",
    reason: str = "Policy violation"
) -> Dict[str, Any]:
    """Reject pending integration"""
    
    from backend.governance.verification_charter import get_verification_charter
    
    charter = get_verification_charter()
    success = await charter.reject_integration(request_id, rejected_by, reason)
    
    if success:
        return {
            "success": True,
            "status": "rejected",
            "request_id": request_id,
            "rejected_by": rejected_by,
            "reason": reason
        }
    else:
        raise HTTPException(status_code=404, detail="Request not found")


@router.get("/approved")
async def get_approved_integrations() -> Dict[str, Any]:
    """Get all approved integrations"""
    
    from backend.governance.verification_charter import get_verification_charter
    
    charter = get_verification_charter()
    approved = charter.get_approved_integrations()
    
    return {
        'integrations': approved,
        'count': len(approved),
        'by_risk_level': {
            'low': len([i for i in approved if i['risk_level'] == 'low']),
            'medium': len([i for i in approved if i['risk_level'] == 'medium']),
            'high': len([i for i in approved if i['risk_level'] == 'high']),
            'critical': len([i for i in approved if i['risk_level'] == 'critical'])
        }
    }


@router.get("/scan/{integration_name}")
async def get_scan_history(integration_name: str) -> Dict[str, Any]:
    """Get security scan history"""
    
    from backend.kernels.hunter_bridge import get_hunter_bridge
    
    hunter = get_hunter_bridge()
    scans = hunter.get_scan_history(integration_name)
    
    return {
        'integration': integration_name,
        'scans': scans,
        'count': len(scans),
        'latest_risk_score': scans[0]['risk_score'] if scans else None
    }


@router.get("/categories")
async def get_integration_categories() -> Dict[str, Any]:
    """Get available integration categories"""
    
    return {
        'categories': {
            'payments': {
                'name': 'Payment Processors',
                'integrations': ['Stripe', 'PayPal', 'Square'],
                'risk_level': 'high',
                'requires_approval': True
            },
            'ecommerce': {
                'name': 'E-commerce Platforms',
                'integrations': ['Shopify', 'WooCommerce', 'BigCommerce'],
                'risk_level': 'medium',
                'requires_approval': True
            },
            'crm': {
                'name': 'CRM Systems',
                'integrations': ['HubSpot', 'Salesforce', 'Pipedrive'],
                'risk_level': 'medium',
                'requires_approval': True
            },
            'ai_ml': {
                'name': 'AI/ML Platforms',
                'integrations': ['OpenAI', 'Hugging Face', 'Replicate', 'Anthropic'],
                'risk_level': 'medium',
                'requires_approval': False  # Grace's domain
            },
            'blockchain': {
                'name': 'Blockchain Networks',
                'integrations': ['Ethereum', 'Solana', 'Polygon'],
                'risk_level': 'critical',
                'requires_approval': True
            },
            'cloud': {
                'name': 'Cloud Infrastructure',
                'integrations': ['AWS', 'Azure', 'GCP', 'DigitalOcean'],
                'risk_level': 'critical',
                'requires_approval': True
            },
            'analytics': {
                'name': 'Analytics & Ads',
                'integrations': ['Google Analytics', 'Facebook Ads', 'Google Ads'],
                'risk_level': 'low',
                'requires_approval': False
            }
        }
    }


@router.post("/health-check/{integration_id}")
async def run_health_check(integration_id: str) -> Dict[str, Any]:
    """Run health check on active integration"""
    
    from backend.kernels.hunter_bridge import get_hunter_bridge
    
    hunter = get_hunter_bridge()
    
    # Re-scan the integration
    # In production, fetch from verification_matrix and re-scan
    
    return {
        'integration_id': integration_id,
        'health': 'healthy',
        'last_check': datetime.now().isoformat(),
        'message': 'Health check placeholder - will implement full check'
    }
