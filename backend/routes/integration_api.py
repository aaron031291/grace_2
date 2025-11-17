"""
Integration API
REST API for integration orchestration and crypto key management

Endpoints:
- GET /integration/status - Integration status
- GET /integration/map - Integration map
- GET /integration/statistics - Integration statistics
- POST /integration/verify - Verify integration
- GET /crypto/keys - List crypto keys
- POST /crypto/keys/{component_id} - Generate key for component
- POST /crypto/sign - Sign message
- POST /crypto/verify - Verify signature
- GET /crypto/statistics - Crypto statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from ..auth import get_current_user
from ..integration_orchestrator import integration_orchestrator
from ..crypto_key_manager import crypto_key_manager, SignedMessage

router = APIRouter(prefix="/integration", tags=["Integration"])
crypto_router = APIRouter(prefix="/crypto", tags=["Crypto"])


# ========== Request Models ==========

class SignMessageRequest(BaseModel):
    """Request to sign a message"""
    component_id: str
    message: Dict[str, Any]


class VerifyMessageRequest(BaseModel):
    """Request to verify a message"""
    message: Dict[str, Any]
    signature: str
    key_id: str
    component_id: str
    signed_at: str


class TrackDataFlowRequest(BaseModel):
    """Request to track data flow"""
    source: str
    destination: str
    data_type: str
    signed: bool = False


# ========== Integration Endpoints ==========

@router.get("/status")
async def get_integration_status(current_user: str = Depends(get_current_user)):
    """Get integration orchestrator status"""
    try:
        stats = integration_orchestrator.get_statistics()
        return {
            "status": "operational" if integration_orchestrator.running else "stopped",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map")
async def get_integration_map(current_user: str = Depends(get_current_user)):
    """Get complete integration map"""
    try:
        return integration_orchestrator.get_integration_map()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_integration_statistics(current_user: str = Depends(get_current_user)):
    """Get integration statistics"""
    try:
        return integration_orchestrator.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-flow")
async def track_data_flow(
    request: TrackDataFlowRequest,
    current_user: str = Depends(get_current_user)
):
    """Track data flow between systems"""
    try:
        await integration_orchestrator.track_data_flow(
            source=request.source,
            destination=request.destination,
            data_type=request.data_type,
            signed=request.signed
        )
        
        return {
            "success": True,
            "message": "Data flow tracked"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_system_health(current_user: str = Depends(get_current_user)):
    """Get health of all integrated systems"""
    try:
        return {
            "systems": integration_orchestrator.system_health,
            "total_systems": len(integration_orchestrator.CORE_SYSTEMS),
            "healthy_systems": sum(1 for h in integration_orchestrator.system_health.values() if h)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Crypto Endpoints ==========

@crypto_router.get("/keys")
async def list_crypto_keys(current_user: str = Depends(get_current_user)):
    """List all crypto keys"""
    try:
        keys = []
        for key_id, crypto_key in crypto_key_manager.keys.items():
            keys.append({
                "key_id": key_id,
                "component_id": crypto_key.component_id,
                "created_at": crypto_key.created_at.isoformat(),
                "expires_at": crypto_key.expires_at.isoformat() if crypto_key.expires_at else None,
                "rotated": crypto_key.rotated,
                "public_key_pem": crypto_key.get_public_key_pem()
            })
        
        return {
            "total": len(keys),
            "keys": keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crypto_router.post("/keys/{component_id}")
async def generate_key_for_component(
    component_id: str,
    force_new: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Generate crypto key for a component"""
    try:
        crypto_key = await crypto_key_manager.generate_key_for_component(
            component_id=component_id,
            force_new=force_new
        )
        
        return {
            "success": True,
            "key_id": crypto_key.key_id,
            "component_id": crypto_key.component_id,
            "created_at": crypto_key.created_at.isoformat(),
            "expires_at": crypto_key.expires_at.isoformat() if crypto_key.expires_at else None,
            "public_key_pem": crypto_key.get_public_key_pem()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crypto_router.post("/sign")
async def sign_message(
    request: SignMessageRequest,
    current_user: str = Depends(get_current_user)
):
    """Sign a message with component's key"""
    try:
        signed_message = await crypto_key_manager.sign_message(
            component_id=request.component_id,
            message=request.message
        )
        
        return signed_message.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crypto_router.post("/verify")
async def verify_message(
    request: VerifyMessageRequest,
    current_user: str = Depends(get_current_user)
):
    """Verify a signed message"""
    try:
        from datetime import datetime
        
        # Reconstruct SignedMessage
        signed_message = SignedMessage(
            message=request.message,
            signature=request.signature,
            key_id=request.key_id,
            component_id=request.component_id,
            signed_at=datetime.fromisoformat(request.signed_at)
        )
        
        is_valid = await crypto_key_manager.verify_message(signed_message)
        
        return {
            "valid": is_valid,
            "component_id": request.component_id,
            "key_id": request.key_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crypto_router.get("/statistics")
async def get_crypto_statistics(current_user: str = Depends(get_current_user)):
    """Get crypto key manager statistics"""
    try:
        return crypto_key_manager.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@crypto_router.post("/rotate/{component_id}")
async def rotate_key(
    component_id: str,
    current_user: str = Depends(get_current_user)
):
    """Rotate key for a component"""
    try:
        new_key = await crypto_key_manager.rotate_key(component_id)
        
        return {
            "success": True,
            "message": f"Key rotated for {component_id}",
            "new_key_id": new_key.key_id,
            "created_at": new_key.created_at.isoformat(),
            "expires_at": new_key.expires_at.isoformat() if new_key.expires_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== System Integration Test Endpoints ==========

@router.post("/test/mission-control")
async def test_mission_control_integration(current_user: str = Depends(get_current_user)):
    """Test Mission Control integration"""
    try:
        # Send signed message from Mission Control to Elite Systems
        message = {
            "type": "integration_test",
            "timestamp": datetime.now().isoformat(),
            "test": "mission_control_to_elite_systems"
        }
        
        signed_message = await integration_orchestrator.send_signed_message(
            source_system="mission_control_hub",
            target_system="elite_self_healing",
            message=message
        )
        
        # Verify message
        is_valid = await integration_orchestrator.verify_and_receive_message(signed_message)
        
        return {
            "success": True,
            "test": "mission_control_integration",
            "message_signed": True,
            "message_verified": is_valid,
            "signature": signed_message.signature[:32] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/elite-systems")
async def test_elite_systems_integration(current_user: str = Depends(get_current_user)):
    """Test Elite Systems integration"""
    try:
        # Test Elite Self-Healing → Shared Orchestrator
        message1 = {
            "type": "integration_test",
            "test": "elite_self_healing_to_orchestrator"
        }
        
        signed1 = await integration_orchestrator.send_signed_message(
            source_system="elite_self_healing",
            target_system="shared_orchestrator",
            message=message1
        )
        
        # Test Elite Coding Agent → Shared Orchestrator
        message2 = {
            "type": "integration_test",
            "test": "elite_coding_agent_to_orchestrator"
        }
        
        signed2 = await integration_orchestrator.send_signed_message(
            source_system="elite_coding_agent",
            target_system="shared_orchestrator",
            message=message2
        )
        
        return {
            "success": True,
            "test": "elite_systems_integration",
            "self_healing_verified": await integration_orchestrator.verify_and_receive_message(signed1),
            "coding_agent_verified": await integration_orchestrator.verify_and_receive_message(signed2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/full-stack")
async def test_full_stack_integration(current_user: str = Depends(get_current_user)):
    """Test full stack integration"""
    try:
        results = []
        
        # Test all core system integrations
        test_pairs = [
            ("mission_control_hub", "autonomous_coding_pipeline"),
            ("mission_control_hub", "self_healing_workflow"),
            ("elite_self_healing", "shared_orchestrator"),
            ("elite_coding_agent", "shared_orchestrator"),
            ("autonomous_coding_pipeline", "governance_engine"),
            ("autonomous_coding_pipeline", "hunter_engine"),
        ]
        
        for source, target in test_pairs:
            message = {
                "type": "integration_test",
                "test": f"{source}_to_{target}",
                "timestamp": datetime.now().isoformat()
            }
            
            signed = await integration_orchestrator.send_signed_message(
                source_system=source,
                target_system=target,
                message=message
            )
            
            verified = await integration_orchestrator.verify_and_receive_message(signed)
            
            results.append({
                "source": source,
                "target": target,
                "signed": True,
                "verified": verified
            })
        
        return {
            "success": True,
            "test": "full_stack_integration",
            "total_tests": len(results),
            "passed": sum(1 for r in results if r["verified"]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

