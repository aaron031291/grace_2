"""
Port Manager API
View and manage port allocations with network hardening
"""

from fastapi import APIRouter
from typing import Dict, Any, List

from ..core.port_manager import port_manager
from ..core.port_watchdog import port_watchdog
from ..core.network_hardening import network_hardening

router = APIRouter(prefix="/api/ports", tags=["Port Manager"])


@router.get("/status")
async def get_port_status() -> Dict[str, Any]:
    """Get port manager and watchdog status"""
    return {
        'port_manager': port_manager.get_stats(),
        'watchdog': port_watchdog.get_status()
    }


@router.get("/allocations")
async def get_allocations() -> Dict[str, Any]:
    """Get all port allocations"""
    allocations = port_manager.get_all_allocations()
    return {
        'allocations': allocations,
        'count': len(allocations)
    }


@router.get("/allocations/{port}")
async def get_allocation(port: int) -> Dict[str, Any]:
    """Get specific port allocation"""
    allocation = port_manager.get_allocation(port)
    if not allocation:
        return {'error': 'port_not_allocated'}
    return allocation


@router.post("/health-check")
async def trigger_health_check() -> Dict[str, Any]:
    """Manually trigger health check on all ports"""
    health_reports = port_manager.health_check_all()
    
    active = sum(1 for h in health_reports if h['status'] == 'active')
    dead = sum(1 for h in health_reports if h['status'] == 'dead')
    
    return {
        'health_reports': health_reports,
        'summary': {
            'active': active,
            'dead': dead,
            'total_checked': len(health_reports)
        }
    }


@router.get("/watchdog/status")
async def get_watchdog_status() -> Dict[str, Any]:
    """Get watchdog status"""
    return port_watchdog.get_status()


@router.get("/network/health")
async def get_network_health() -> Dict[str, Any]:
    """
    Get comprehensive network health check
    Checks: IPv4/IPv6, firewall, file descriptors, connections, DNS
    """
    # Check for a sample port
    health = network_hardening.check_all_networking_issues(8000)
    return health


@router.get("/network/stats")
async def get_network_stats() -> Dict[str, Any]:
    """
    Get current network statistics
    Bytes sent/recv, packets, errors, connections by state
    """
    return network_hardening.get_network_stats()


@router.get("/network/port-exhaustion")
async def check_port_exhaustion() -> Dict[str, Any]:
    """
    Check if system is running out of ephemeral ports
    Monitors ports 49152-65535
    """
    return network_hardening.detect_port_exhaustion()


@router.get("/network/ssl-readiness")
async def check_ssl_readiness() -> Dict[str, Any]:
    """Check SSL/TLS configuration readiness"""
    return network_hardening.check_ssl_readiness()
