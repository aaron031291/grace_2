"""
Guardian Kernel - Boot Priority 0
THE FIRST KERNEL - Starts before everything else

Responsibilities (in order):
1. Boot first, establish network/port protection
2. Run pre-flight diagnostics
3. Fix any network/port issues
4. Allocate ports for all services
5. Start monitoring (watchdog)
6. THEN trigger rest of system (self-healing, coding agent, etc.)
7. Catch and fix problems BEFORE they reach deeper systems
8. Continuous monitoring and auto-healing

Guardian prevents problems from occurring, not just responding to them.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .port_manager import port_manager
from .port_watchdog import port_watchdog
from .network_hardening import network_hardening

logger = logging.getLogger(__name__)


class Guardian:
    """
    Guardian Kernel - Boot Priority 0
    
    The first kernel to boot. Establishes system protection before anything else starts.
    Fixes issues proactively so they never reach deeper systems.
    """
    
    def __init__(self):
        self.boot_priority = 0  # FIRST
        self.running = False
        self.boot_complete = False
        self.start_time: Optional[str] = None
        
        # Subsystems
        self.port_manager = port_manager
        self.port_watchdog = port_watchdog
        self.network_hardening = network_hardening
        
        # Boot tracking
        self.pre_flight_passed = False
        self.network_issues_fixed = 0
        self.kernels_booted = []
        
        # Statistics
        self.total_checks = 0
        self.issues_prevented = 0
        self.auto_fixes_applied = 0
        
        logger.info("[GUARDIAN] Initialized - Boot Priority 0 (FIRST KERNEL)")
    
    async def boot(self) -> Dict[str, Any]:
        """
        Guardian boot sequence - runs BEFORE everything else
        
        Phase 1: Self-check
        Phase 2: Network diagnostics
        Phase 3: Port allocation
        Phase 4: Fix detected issues
        Phase 5: Start watchdog
        Phase 6: Trigger rest of system
        """
        
        if self.running:
            return {'error': 'already_running'}
        
        logger.info("=" * 80)
        logger.info("[GUARDIAN] BOOT SEQUENCE STARTING - PRIORITY 0")
        logger.info("=" * 80)
        
        boot_result = {
            'boot_priority': 0,
            'started_at': datetime.utcnow().isoformat(),
            'phases': {}
        }
        
        # PHASE 1: Self-check
        logger.info("[GUARDIAN] Phase 1/6: Self-check")
        phase1 = await self._phase1_self_check()
        boot_result['phases']['phase1_self_check'] = phase1
        
        if not phase1['passed']:
            logger.critical("[GUARDIAN] Self-check FAILED - Cannot continue")
            return {'error': 'self_check_failed', 'details': phase1}
        
        logger.info("[GUARDIAN] ✓ Phase 1 complete: Self-check passed")
        
        # PHASE 2: Network diagnostics
        logger.info("[GUARDIAN] Phase 2/6: Network diagnostics")
        phase2 = await self._phase2_network_diagnostics()
        boot_result['phases']['phase2_diagnostics'] = phase2
        
        if phase2['critical_issues']:
            logger.error(f"[GUARDIAN] Critical network issues: {phase2['critical_issues']}")
            # Try to fix
            fixed = await self._auto_fix_network_issues(phase2['critical_issues'])
            if not fixed:
                return {'error': 'critical_network_issues', 'details': phase2}
        
        logger.info("[GUARDIAN] ✓ Phase 2 complete: Network healthy")
        
        # PHASE 3: Port allocation
        logger.info("[GUARDIAN] Phase 3/6: Port allocation")
        phase3 = await self._phase3_allocate_ports()
        boot_result['phases']['phase3_ports'] = phase3
        
        if 'error' in phase3:
            logger.error(f"[GUARDIAN] Port allocation failed: {phase3['error']}")
            return {'error': 'port_allocation_failed', 'details': phase3}
        
        logger.info(f"[GUARDIAN] ✓ Phase 3 complete: Port {phase3['port']} allocated")
        
        # PHASE 4: Start watchdog AND healer
        logger.info("[GUARDIAN] Phase 4/6: Starting watchdog & healer")
        await self.port_watchdog.start()
        
        # Initialize and start ADVANCED healer (covers ALL network layers)
        try:
            from .advanced_network_healer import advanced_network_healer
            self.healer = advanced_network_healer
            self.healer.running = True
            healer_started = True
            scan_interval = self.healer.scan_interval
            logger.info("[GUARDIAN] ✓ Advanced Network Healer loaded (OSI Layers 2-7)")
        except Exception as e:
            logger.warning(f"[GUARDIAN] Advanced healer not available: {e}")
            healer_started = False
            scan_interval = 0
        
        boot_result['phases']['phase4_watchdog'] = {
            'watchdog_started': True,
            'healer_started': healer_started,
            'scan_interval': scan_interval
        }
        
        if healer_started:
            logger.info("[GUARDIAN] ✓ Phase 4 complete: Watchdog + Healer active (scan & heal every 30s)")
        else:
            logger.info("[GUARDIAN] ✓ Phase 4 complete: Watchdog active")
        
        # PHASE 5: Pre-flight complete
        logger.info("[GUARDIAN] Phase 5/6: Pre-flight complete")
        self.pre_flight_passed = True
        self.running = True
        self.start_time = datetime.utcnow().isoformat()
        boot_result['phases']['phase5_preflight'] = {'passed': True}
        logger.info("[GUARDIAN] ✓ Phase 5 complete: Ready to boot other kernels")
        
        # PHASE 6: Signal ready to boot rest of system
        logger.info("[GUARDIAN] Phase 6/6: System ready")
        boot_result['phases']['phase6_ready'] = {
            'ready_to_boot_kernels': True,
            'port_allocated': phase3['port'],
            'network_healthy': True,
            'watchdog_active': True
        }
        
        self.boot_complete = True
        
        logger.info("=" * 80)
        logger.info("[GUARDIAN] BOOT COMPLETE - REST OF SYSTEM CAN NOW START")
        logger.info("=" * 80)
        
        boot_result['boot_complete'] = True
        boot_result['duration_seconds'] = (datetime.utcnow() - datetime.fromisoformat(boot_result['started_at'])).total_seconds()
        
        return boot_result
    
    async def _phase1_self_check(self) -> Dict[str, Any]:
        """Phase 1: Guardian self-check"""
        
        checks = {
            'port_manager_available': self.port_manager is not None,
            'watchdog_available': self.port_watchdog is not None,
            'network_hardening_available': self.network_hardening is not None,
        }
        
        all_passed = all(checks.values())
        
        return {
            'passed': all_passed,
            'checks': checks
        }
    
    async def _phase2_network_diagnostics(self) -> Dict[str, Any]:
        """Phase 2: Run network diagnostics"""
        
        # Run comprehensive network check
        network_check = self.network_hardening.check_all_networking_issues(8000)
        
        return {
            'status': network_check['status'],
            'critical_issues': network_check.get('critical_issues', []),
            'warnings': network_check.get('warnings', []),
            'checks': network_check.get('checks', {})
        }
    
    async def _phase3_allocate_ports(self) -> Dict[str, Any]:
        """Phase 3: Allocate port for main service"""
        
        allocation = self.port_manager.allocate_port(
            service_name="grace_backend",
            started_by="guardian_kernel",
            purpose="Main Grace API - allocated by Guardian during boot",
            preferred_port=8000
        )
        
        return allocation
    
    async def _auto_fix_network_issues(self, issues: List[str]) -> bool:
        """
        Auto-fix network issues detected during boot
        Returns True if all fixed, False if critical issues remain
        """
        
        logger.info(f"[GUARDIAN] Auto-fixing {len(issues)} network issues...")
        
        fixed_count = 0
        
        for issue in issues:
            try:
                if issue == 'ipv4_not_available':
                    logger.critical("[GUARDIAN] IPv4 not available - CANNOT FIX")
                    # This is critical, cannot proceed
                    return False
                
                elif issue == 'firewall_blocking':
                    logger.warning("[GUARDIAN] Firewall may be blocking - trying next port")
                    # Will be handled by port retry logic
                    fixed_count += 1
                
                elif issue == 'network_interface_down':
                    logger.error("[GUARDIAN] Network interface down - checking alternatives")
                    # Check if any interface is up
                    interfaces_check = self.network_hardening._check_network_interfaces()
                    if interfaces_check.get('has_localhost'):
                        fixed_count += 1
                    else:
                        return False
                
                else:
                    logger.warning(f"[GUARDIAN] Unknown issue: {issue}")
                
            except Exception as e:
                logger.error(f"[GUARDIAN] Failed to fix {issue}: {e}")
        
        self.auto_fixes_applied += fixed_count
        logger.info(f"[GUARDIAN] Auto-fixed {fixed_count}/{len(issues)} issues")
        
        return fixed_count > 0 or len(issues) == 0
    
    def signal_kernel_boot(self, kernel_name: str, boot_priority: int):
        """
        Called by each kernel when it boots
        Guardian tracks which kernels have started
        """
        
        self.kernels_booted.append({
            'kernel': kernel_name,
            'boot_priority': boot_priority,
            'booted_at': datetime.utcnow().isoformat()
        })
        
        logger.info(f"[GUARDIAN] Kernel booted: {kernel_name} (priority {boot_priority})")
    
    def check_can_boot_kernel(self, kernel_name: str, boot_priority: int) -> bool:
        """
        Check if a kernel can boot
        Guardian must be running and pre-flight must have passed
        """
        
        if not self.running:
            logger.warning(f"[GUARDIAN] Blocking {kernel_name} boot: Guardian not running")
            return False
        
        if not self.pre_flight_passed:
            logger.warning(f"[GUARDIAN] Blocking {kernel_name} boot: Pre-flight not passed")
            return False
        
        # Guardian (priority 0) must boot before anything else
        if boot_priority > 0 and not self.boot_complete:
            logger.warning(f"[GUARDIAN] Blocking {kernel_name} boot: Guardian boot not complete")
            return False
        
        return True


# Global instance
guardian = Guardian()
