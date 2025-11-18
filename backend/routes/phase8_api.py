"""
Phase 8 API Routes: End-to-End Testing & Production Readiness
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.production_readiness import (
    ProductionReadinessChecker,
    HealthMonitor,
    IntegrationValidator,
)

router = APIRouter(prefix="/api/phase8", tags=["Phase 8: E2E Testing & Production Readiness"])

readiness_checker = ProductionReadinessChecker()
health_monitor = HealthMonitor()
integration_validator = IntegrationValidator()


@router.get("/summary")
async def get_phase8_summary() -> Dict[str, Any]:
    """Get Phase 8 summary"""
    return {
        "phase": "Phase 8: End-to-End Testing & Production Readiness",
        "description": "Comprehensive testing and production readiness validation",
        "components": [
            "E2E Test Suite",
            "Production Readiness Checker",
            "Health Monitor",
            "Integration Validator",
        ],
        "status": "operational",
        "endpoints": 15,
    }


@router.get("/readiness/checks")
async def get_readiness_checks() -> Dict[str, Any]:
    """Get all production readiness checks"""
    return await readiness_checker.run_all_checks()


@router.get("/readiness/checklist")
async def get_readiness_checklist() -> List[Dict[str, Any]]:
    """Get production readiness checklist"""
    return readiness_checker.get_checklist()


@router.get("/readiness/summary")
async def get_readiness_summary() -> Dict[str, Any]:
    """Get production readiness summary"""
    return readiness_checker.get_summary()


@router.get("/health/system")
async def get_system_health() -> Dict[str, Any]:
    """Get overall system health"""
    return await health_monitor.get_system_health()


@router.get("/health/history")
async def get_health_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Get health history"""
    return await health_monitor.get_health_history(limit)


@router.get("/health/component/{component}")
async def get_component_health(component: str) -> Dict[str, Any]:
    """Get health of a specific component"""
    return await health_monitor.get_component_health(component)


@router.get("/health/metrics")
async def get_health_metrics() -> Dict[str, Any]:
    """Get health metrics summary"""
    return await health_monitor.get_metrics_summary()


@router.get("/integrations/validate")
async def validate_all_integrations() -> Dict[str, Any]:
    """Validate all integrations"""
    return await integration_validator.validate_all_integrations()


@router.get("/integrations/map")
async def get_integration_map() -> Dict[str, Any]:
    """Get integration map"""
    return integration_validator.get_integration_map()


@router.get("/integrations/{integration_id}")
async def validate_integration(integration_id: str) -> Dict[str, Any]:
    """Validate a specific integration"""
    return await integration_validator.validate_integration(integration_id)


@router.get("/tests/status")
async def get_test_status() -> Dict[str, Any]:
    """Get E2E test status"""
    return {
        "test_suite": "Phase 8 E2E Tests",
        "total_tests": 50,
        "test_categories": [
            "Phase 0: Boot Stability",
            "Phase 1: Pillar Hardening",
            "Phase 2: RAG & Memory",
            "Phase 3: Learning Engine",
            "Phase 4: Copilot",
            "Phase 5: World Builder UI",
            "Phase 6: Enterprise API",
            "Phase 7: SaaS Readiness",
            "End-to-End User Flows",
            "Production Readiness",
        ],
        "status": "ready",
        "last_run": None,
    }


@router.get("/tests/results")
async def get_test_results() -> Dict[str, Any]:
    """Get E2E test results"""
    return {
        "test_suite": "Phase 8 E2E Tests",
        "status": "not_run",
        "message": "Run tests with: pytest tests/e2e/test_critical_flows.py -v",
        "total_tests": 50,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
    }


@router.get("/status")
async def get_phase8_status() -> Dict[str, Any]:
    """Get overall Phase 8 status"""
    readiness = await readiness_checker.run_all_checks()
    health = await health_monitor.get_system_health()
    integrations = await integration_validator.validate_all_integrations()
    
    return {
        "phase": "Phase 8: End-to-End Testing & Production Readiness",
        "timestamp": health["timestamp"],
        "overall_status": "operational",
        "readiness": {
            "status": readiness["overall_status"],
            "score": readiness["readiness_score"],
            "total_checks": readiness["total_checks"],
            "passed_checks": readiness["passed_checks"],
        },
        "health": {
            "status": health["status"],
            "cpu_percent": health["components"]["system"]["cpu_percent"],
            "memory_percent": health["components"]["system"]["memory_percent"],
        },
        "integrations": {
            "status": integrations["overall_status"],
            "success_rate": integrations["success_rate"],
            "total_tests": integrations["total_tests"],
            "passed_tests": integrations["passed_tests"],
        },
        "e2e_tests": {
            "status": "ready",
            "total_tests": 50,
        }
    }
