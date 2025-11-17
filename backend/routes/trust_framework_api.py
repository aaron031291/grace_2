"""
TRUST Framework API - PRODUCTION
Exposes all TRUST framework systems via REST API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from backend.trust_framework import (
    hallucination_ledger,
    htm_detector_pool,
    verification_mesh,
    model_health_registry,
    adaptive_guardrails,
    ahead_of_user_research,
    data_hygiene_pipeline,
    chaos_drill_runner,
    model_integrity_registry,
    model_rollback_system,
    stress_test_harness,
    trustscore_gate,
    uncertainty_reporting,
    RollbackReason
)
from backend.model_categorization import MODEL_REGISTRY, get_summary

router = APIRouter(prefix="/api/trust", tags=["trust_framework"])


# ============================================================================
# TRUST FRAMEWORK STATUS
# ============================================================================

@router.get("/status")
async def get_trust_framework_status():
    """Get complete TRUST framework status"""
    
    return {
        'framework': 'TRUST Framework v2.0',
        'status': 'active',
        'systems': {
            'htm_anomaly_detection': htm_detector_pool.get_all_stats(),
            'verification_mesh': verification_mesh.get_stats(),
            'model_health': model_health_registry.get_stats(),
            'adaptive_guardrails': adaptive_guardrails.get_stats(),
            'ahead_of_user_research': ahead_of_user_research.get_stats(),
            'data_hygiene': data_hygiene_pipeline.get_stats(),
            'chaos_drills': chaos_drill_runner.get_stats(),
            'model_integrity': model_integrity_registry.get_stats(),
            'model_rollback': model_rollback_system.get_stats(),
            'stress_testing': stress_test_harness.get_stats(),
            'trustscore_gate': trustscore_gate.get_stats(),
            'uncertainty_reporting': uncertainty_reporting.get_stats()
        },
        'models': {
            'total_registered': len(MODEL_REGISTRY),
            'by_specialty': get_summary()
        }
    }


# ============================================================================
# MODEL HEALTH & INTEGRITY
# ============================================================================

@router.get("/models/{model_name}/health")
async def get_model_health(model_name: str):
    """Get health status for specific model"""
    
    snapshot = model_health_registry.get_snapshot(model_name)
    return snapshot.to_dict()


@router.get("/models/health/all")
async def get_all_model_health():
    """Get health snapshots for all models"""
    
    snapshots = model_health_registry.get_all_snapshots()
    return {
        name: snapshot.to_dict()
        for name, snapshot in snapshots.items()
    }


@router.get("/models/{model_name}/integrity")
async def verify_model_integrity(model_name: str):
    """Verify integrity of specific model"""
    
    result = await model_integrity_registry.verify_model(model_name)
    return result


@router.post("/models/{model_name}/stress-test")
async def run_stress_test(model_name: str):
    """Run stress test to map execution window"""
    
    result = await stress_test_harness.run_full_stress_test(model_name)
    return result


@router.get("/models/{model_name}/execution-window")
async def get_execution_window(model_name: str):
    """Get execution window for model"""
    
    window = stress_test_harness.get_execution_window(model_name)
    
    if not window:
        raise HTTPException(status_code=404, detail="Execution window not mapped")
    
    return window.to_dict()


@router.post("/models/{model_name}/rollback")
async def rollback_model(
    model_name: str,
    reason: str = "manual_request",
    snapshot_id: Optional[str] = None
):
    """Rollback model to previous version"""
    
    rollback_reason = RollbackReason.MANUAL_REQUEST
    try:
        rollback_reason = RollbackReason(reason)
    except:
        pass
    
    result = await model_rollback_system.rollback_model(
        model_name,
        rollback_reason,
        snapshot_id
    )
    
    return result


@router.get("/models/{model_name}/snapshots")
async def get_model_snapshots(model_name: str):
    """Get all snapshots for model"""
    
    snapshots = model_rollback_system.snapshots.get(model_name, [])
    
    return {
        'model_name': model_name,
        'snapshot_count': len(snapshots),
        'snapshots': [s.to_dict() for s in snapshots]
    }


# ============================================================================
# HALLUCINATION TRACKING
# ============================================================================

@router.get("/hallucinations/ledger")
async def get_hallucination_ledger():
    """Get hallucination ledger summary"""
    
    return hallucination_ledger.get_ledger_summary()


@router.get("/hallucinations/model/{model_name}")
async def get_model_hallucinations(model_name: str):
    """Get hallucination stats for specific model"""
    
    stats = hallucination_ledger.get_model_stats(model_name)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No stats for model")
    
    return stats


@router.get("/hallucinations/retraining-priorities")
async def get_retraining_priorities():
    """Get models ordered by retraining priority"""
    
    priorities = hallucination_ledger.get_retraining_priorities()
    
    return {
        'priorities': [
            {'model': model, 'priority': priority}
            for model, priority in priorities
        ]
    }


# ============================================================================
# VERIFICATION & GUARDRAILS
# ============================================================================

@router.get("/verification/stats")
async def get_verification_stats():
    """Get verification mesh statistics"""
    
    return verification_mesh.get_stats()


@router.get("/guardrails/status")
async def get_guardrails_status():
    """Get adaptive guardrails status"""
    
    return adaptive_guardrails.get_stats()


# ============================================================================
# DATA HYGIENE
# ============================================================================

@router.get("/data-hygiene/stats")
async def get_data_hygiene_stats():
    """Get data hygiene pipeline statistics"""
    
    return data_hygiene_pipeline.get_stats()


class DataAuditRequest(BaseModel):
    content: str
    metadata: Dict
    existing_data: Optional[List[Dict]] = None


@router.post("/data-hygiene/audit")
async def audit_data(request: DataAuditRequest):
    """Audit data before ingestion"""
    
    result = await data_hygiene_pipeline.audit(
        request.content,
        request.metadata,
        request.existing_data
    )
    
    return result.to_dict()


# ============================================================================
# CHAOS DRILLS
# ============================================================================

@router.get("/chaos-drills/stats")
async def get_chaos_drill_stats():
    """Get chaos drill statistics"""
    
    return chaos_drill_runner.get_stats()


@router.post("/chaos-drills/run/{model_name}")
async def run_chaos_drills(model_name: str):
    """Run full chaos drill suite on model"""
    
    result = await chaos_drill_runner.run_full_drill_suite(model_name)
    return result


# ============================================================================
# CONTEXT PROVENANCE
# ============================================================================

@router.get("/context/trustscore-gate/stats")
async def get_trustscore_gate_stats():
    """Get trustscore gate statistics"""
    
    return trustscore_gate.get_stats()


# ============================================================================
# UNCERTAINTY REPORTING
# ============================================================================

@router.get("/uncertainty/stats")
async def get_uncertainty_stats():
    """Get uncertainty reporting statistics"""
    
    return uncertainty_reporting.get_stats()


# ============================================================================
# COMPLETE DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def get_trust_dashboard():
    """
    Complete TRUST framework dashboard
    
    Single endpoint with everything
    """
    
    # Get unhealthy models
    unhealthy = model_health_registry.get_unhealthy_models()
    
    # Get quarantined models
    quarantined = list(model_integrity_registry.quarantined_models)
    
    # Get hallucination summary
    hall_summary = hallucination_ledger.get_ledger_summary()
    
    # Get retraining priorities
    retraining = hallucination_ledger.get_retraining_priorities()[:5]  # Top 5
    
    # Overall health score
    total_models = len(MODEL_REGISTRY)
    healthy_models = total_models - len(unhealthy) - len(quarantined)
    health_score = healthy_models / total_models if total_models > 0 else 0.0
    
    return {
        'summary': {
            'overall_health_score': health_score,
            'total_models': total_models,
            'healthy_models': healthy_models,
            'unhealthy_models': len(unhealthy),
            'quarantined_models': len(quarantined),
            'total_hallucinations': hall_summary.get('total_hallucinations', 0),
            'models_needing_retraining': len(hall_summary.get('models_needing_retraining', []))
        },
        'alerts': {
            'unhealthy_models': unhealthy,
            'quarantined_models': quarantined,
            'high_risk_models': hall_summary.get('highest_risk_models', []),
            'retraining_priorities': [
                {'model': m, 'priority': p} for m, p in retraining
            ]
        },
        'systems_active': {
            'htm_anomaly_detection': True,
            'verification_mesh': True,
            'model_health_monitoring': True,
            'adaptive_guardrails': True,
            'ahead_of_user_research': True,
            'data_hygiene': True,
            'chaos_drills': True,
            'model_integrity': True,
            'model_rollback': True,
            'stress_testing': True,
            'context_provenance': True,
            'uncertainty_reporting': True
        },
        'timestamp': datetime.utcnow().isoformat()
    }
