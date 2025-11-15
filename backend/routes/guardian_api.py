"""
Guardian API
Unified system health and protection monitoring
Boot Priority 0 kernel with diagnostics and stress testing
"""

from fastapi import APIRouter
from typing import Dict, Any, List

from ..core.guardian import guardian
from ..core.advanced_network_healer import advanced_network_healer

router = APIRouter(prefix="/api/guardian", tags=["Guardian"])


@router.get("/status")
async def get_guardian_status() -> Dict[str, Any]:
    """
    Get comprehensive Guardian status
    Includes: port manager, watchdog, network health
    """
    return guardian.get_comprehensive_status()


@router.get("/health-check/{port}")
async def health_check_port(port: int) -> Dict[str, Any]:
    """
    Perform comprehensive health check on specific port
    Guardian-level check includes all subsystems
    """
    return guardian.perform_health_check(port)


@router.get("/recommendations")
async def get_recommendations() -> Dict[str, Any]:
    """
    Get Guardian recommendations for system health
    """
    recommendations = guardian.get_recommendations()
    return {
        'recommendations': recommendations,
        'count': len(recommendations)
    }


@router.post("/start")
async def start_guardian() -> Dict[str, Any]:
    """Start the Guardian system"""
    await guardian.start()
    return {'status': 'started', 'running': guardian.running}


@router.post("/stop")
async def stop_guardian() -> Dict[str, Any]:
    """Stop the Guardian system"""
    await guardian.stop()
    return {'status': 'stopped', 'running': guardian.running}


@router.get("/healer/stats")
async def get_healer_stats() -> Dict[str, Any]:
    """
    Get Advanced Network Healer statistics
    Shows scan & heal activity across ALL network layers
    """
    return advanced_network_healer.get_stats()


@router.post("/healer/scan")
async def trigger_comprehensive_scan() -> Dict[str, Any]:
    """
    Manually trigger comprehensive network scan
    Scans ALL OSI layers (2-7) for issues and auto-heals
    """
    scan_result = await advanced_network_healer.comprehensive_scan()
    heal_result = await advanced_network_healer.heal_all_issues(scan_result)
    
    return {
        'scan_result': scan_result,
        'heal_result': heal_result,
        'timestamp': datetime.utcnow().isoformat()
    }


@router.get("/playbooks")
async def get_healing_playbooks() -> Dict[str, Any]:
    """
    Get all Guardian healing playbooks
    Shows what Guardian can auto-heal (30+ playbooks)
    """
    return {
        'playbooks': advanced_network_healer.playbooks,
        'count': len(advanced_network_healer.playbooks),
        'auto_heal_count': sum(1 for p in advanced_network_healer.playbooks.values() if p.get('auto_heal')),
        'coverage': 'OSI Layers 2-7, Performance, Security, Protocols'
    }


@router.get("/boot-status")
async def get_boot_status() -> Dict[str, Any]:
    """
    Get Guardian boot status
    Shows what happened during boot sequence
    """
    return {
        'boot_complete': guardian.boot_complete,
        'pre_flight_passed': guardian.pre_flight_passed,
        'kernels_booted': guardian.kernels_booted,
        'issues_prevented': guardian.issues_prevented,
        'auto_fixes_applied': guardian.auto_fixes_applied,
        'diagnostics_run': guardian.diagnostics_run,
        'stress_tests_run': guardian.stress_tests_run
    }
