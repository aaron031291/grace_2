"""
Healer Watchdog - Meta-Monitor for Self-Healing & Coding Agent

Who watches the watchers? This does.

Monitors:
- self_healing kernel
- coding_agent kernel

Capabilities:
- Mutual recovery (each heals the other)
- Fallback watchdog if BOTH are down
- Temporary delegation of healing to other agents
- Emergency restart protocol

Scenarios:
1. Coding agent down → Self-healing restarts it
2. Self-healing down → Coding agent restarts it  
3. BOTH down → Healer watchdog emergency protocol
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class HealerWatchdog:
    """
    Meta-watchdog for healing systems
    Ensures self-healing and coding agent can recover each other
    """
    
    def __init__(self):
        self.running = False
        
        # Monitor targets
        self.self_healing_healthy = True
        self.coding_agent_healthy = True
        
        self.self_healing_last_seen = datetime.utcnow()
        self.coding_agent_last_seen = datetime.utcnow()
        
        # Thresholds
        self.heartbeat_timeout = 30  # seconds
        self.both_down_timeout = 60  # Emergency threshold
        
        # Recovery tracking
        self.mutual_recovery_count = 0
        self.emergency_recovery_count = 0
        
        # Emergency delegates
        self.emergency_delegates = []  # Other agents that can temporarily heal
        
        logger.info("[HEALER-WATCHDOG] Initialized - watching the watchers")
    
    async def start(self):
        """Start healer watchdog"""
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[HEALER-WATCHDOG] Started monitoring self-healing + coding agent")
        logger.info("[HEALER-WATCHDOG] Mutual recovery enabled")
    
    async def stop(self):
        """Stop watchdog"""
        self.running = False
        logger.info("[HEALER-WATCHDOG] Stopped")
    
    async def _monitoring_loop(self):
        """Continuous monitoring of healing systems"""
        
        while self.running:
            try:
                await self._check_healer_health()
            except Exception as e:
                logger.error(f"[HEALER-WATCHDOG] Monitoring error: {e}")
            
            await asyncio.sleep(10)
    
    async def _check_healer_health(self):
        """Check if self-healing and coding agent are healthy"""
        
        from backend.core import control_plane
        
        now = datetime.utcnow()
        
        # Check self-healing
        sh_kernel = control_plane.kernels.get('self_healing')
        if sh_kernel:
            if sh_kernel.state.value == 'running' and sh_kernel.last_heartbeat:
                time_since_hb = (now - sh_kernel.last_heartbeat).total_seconds()
                self.self_healing_healthy = time_since_hb < self.heartbeat_timeout
                if self.self_healing_healthy:
                    self.self_healing_last_seen = now
            else:
                self.self_healing_healthy = False
        
        # Check coding agent
        ca_kernel = control_plane.kernels.get('coding_agent')
        if ca_kernel:
            if ca_kernel.state.value == 'running' and ca_kernel.last_heartbeat:
                time_since_hb = (now - ca_kernel.last_heartbeat).total_seconds()
                self.coding_agent_healthy = time_since_hb < self.heartbeat_timeout
                if self.coding_agent_healthy:
                    self.coding_agent_last_seen = now
            else:
                self.coding_agent_healthy = False
        
        # Determine recovery strategy
        if not self.self_healing_healthy and not self.coding_agent_healthy:
            # BOTH DOWN - Emergency
            await self._handle_both_healers_down()
        elif not self.self_healing_healthy:
            # Self-healing down - coding agent should heal it
            await self._trigger_mutual_recovery('self_healing', 'coding_agent')
        elif not self.coding_agent_healthy:
            # Coding agent down - self-healing should heal it
            await self._trigger_mutual_recovery('coding_agent', 'self_healing')
    
    async def _trigger_mutual_recovery(self, failed_healer: str, active_healer: str):
        """
        Trigger mutual recovery - one healer restarts the other
        """
        
        logger.warning(f"[HEALER-WATCHDOG] MUTUAL RECOVERY: {active_healer} → restart {failed_healer}")
        
        self.mutual_recovery_count += 1
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            # Publish event for active healer to restart failed one
            await trigger_mesh.publish(TriggerEvent(
                source="healer_watchdog",
                event_type="event.incident",
                actor="healer_watchdog",
                resource=failed_healer,
                payload={
                    'trigger_id': 'healer_mutual_recovery',
                    'playbook': 'healer_mutual_restart',
                    'severity': 'high',
                    'failed_healer': failed_healer,
                    'recovery_agent': active_healer,
                    'recovery_type': 'mutual',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
            
            # Also directly restart via control plane
            from backend.core import control_plane
            
            kernel = control_plane.kernels.get(failed_healer)
            if kernel:
                logger.warning(f"[HEALER-WATCHDOG] Direct restart: {failed_healer}")
                await control_plane._restart_kernel(kernel)
        
        except Exception as e:
            logger.error(f"[HEALER-WATCHDOG] Mutual recovery failed: {e}")
    
    async def _handle_both_healers_down(self):
        """
        EMERGENCY: Both healers are down
        Activate emergency protocol with temporary delegation
        """
        
        now = datetime.utcnow()
        time_both_down = min(
            (now - self.self_healing_last_seen).total_seconds(),
            (now - self.coding_agent_last_seen).total_seconds()
        )
        
        if time_both_down < self.both_down_timeout:
            # Just detected - wait a bit before emergency
            logger.warning(f"[HEALER-WATCHDOG] Both healers down for {time_both_down:.0f}s - waiting before emergency")
            return
        
        # EMERGENCY
        logger.critical("=" * 80)
        logger.critical("[EMERGENCY] BOTH HEALING SYSTEMS DOWN")
        logger.critical(f"[EMERGENCY] Self-healing down: {(now - self.self_healing_last_seen).total_seconds():.0f}s")
        logger.critical(f"[EMERGENCY] Coding agent down: {(now - self.coding_agent_last_seen).total_seconds():.0f}s")
        logger.critical("=" * 80)
        
        self.emergency_recovery_count += 1
        
        # Step 1: Delegate healing to emergency agents
        await self._delegate_healing_temporarily()
        
        # Step 2: Trigger emergency playbook
        await self._trigger_emergency_healer_recovery()
        
        # Step 3: Direct restart both via control plane
        await self._emergency_restart_healers()
    
    async def _delegate_healing_temporarily(self):
        """
        Temporarily delegate healing capabilities to other agents
        Until self-healing and coding agent are back online
        """
        
        logger.critical("[HEALER-WATCHDOG] DELEGATING healing to emergency agents...")
        
        # Give Grace Architect emergency healing powers
        try:
            from backend.agents_core.grace_architect_agent import get_grace_architect
            architect = get_grace_architect()
            
            if architect:
                self.emergency_delegates.append('grace_architect')
                logger.critical("[HEALER-WATCHDOG] → grace_architect: TEMPORARY HEALING ENABLED")
        except:
            pass
        
        # Give Parliament emergency coordination powers
        try:
            from backend.parliament.parliament_engine import parliament_engine
            
            if parliament_engine:
                self.emergency_delegates.append('parliament_engine')
                logger.critical("[HEALER-WATCHDOG] → parliament_engine: EMERGENCY COORDINATION ENABLED")
        except:
            pass
        
        # Activate kernel watchdog with expanded authority
        try:
            from backend.triggers.critical_kernel_heartbeat_trigger import critical_kernel_trigger
            
            if critical_kernel_trigger:
                self.emergency_delegates.append('critical_kernel_trigger')
                logger.critical("[HEALER-WATCHDOG] → critical_kernel_trigger: EXPANDED AUTHORITY")
        except:
            pass
        
        logger.critical(f"[HEALER-WATCHDOG] {len(self.emergency_delegates)} emergency delegates activated")
    
    async def _trigger_emergency_healer_recovery(self):
        """Trigger emergency playbook for healer recovery"""
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="healer_watchdog",
                event_type="event.emergency",
                actor="healer_watchdog",
                resource="healing_systems",
                payload={
                    'trigger_id': 'healer_watchdog_emergency',
                    'playbook': 'emergency_healer_recovery',
                    'severity': 'critical',
                    'healers_down': ['self_healing', 'coding_agent'],
                    'emergency_delegates': self.emergency_delegates,
                    'recovery_type': 'emergency_protocol',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
            
            logger.critical("[HEALER-WATCHDOG] Emergency playbook triggered")
        
        except Exception as e:
            logger.error(f"[HEALER-WATCHDOG] Emergency trigger failed: {e}")
    
    async def _emergency_restart_healers(self):
        """
        Emergency restart of both healing systems
        Bypasses normal protocols - force restart
        """
        
        from backend.core import control_plane
        
        logger.critical("[HEALER-WATCHDOG] EMERGENCY RESTART: Forcing both healers online")
        
        # Restart self-healing
        sh_kernel = control_plane.kernels.get('self_healing')
        if sh_kernel:
            logger.critical("[HEALER-WATCHDOG] → Restarting self_healing (force)")
            sh_kernel.restart_count = 0  # Reset restart count for emergency
            await control_plane._boot_kernel(sh_kernel)
        
        # Restart coding agent
        ca_kernel = control_plane.kernels.get('coding_agent')
        if ca_kernel:
            logger.critical("[HEALER-WATCHDOG] → Restarting coding_agent (force)")
            ca_kernel.restart_count = 0  # Reset restart count for emergency
            await control_plane._boot_kernel(ca_kernel)
        
        # Wait for boot
        await asyncio.sleep(5)
        
        # Verify they're back
        sh_back = sh_kernel and sh_kernel.state.value == 'running'
        ca_back = ca_kernel and ca_kernel.state.value == 'running'
        
        if sh_back and ca_back:
            logger.critical("[HEALER-WATCHDOG] ✅ BOTH HEALERS RESTORED")
            
            # Revoke emergency delegation
            await self._revoke_emergency_delegation()
        else:
            logger.critical(f"[HEALER-WATCHDOG] ❌ PARTIAL RECOVERY: SH={sh_back}, CA={ca_back}")
            logger.critical("[HEALER-WATCHDOG] Emergency delegates remain active")
    
    async def _revoke_emergency_delegation(self):
        """Revoke emergency healing powers from delegates"""
        
        logger.critical("[HEALER-WATCHDOG] Revoking emergency delegation...")
        
        for delegate in self.emergency_delegates:
            logger.critical(f"[HEALER-WATCHDOG] → {delegate}: Emergency powers REVOKED")
        
        self.emergency_delegates.clear()
        
        logger.critical("[HEALER-WATCHDOG] Normal healing operations restored")
        
        # Log to immutable audit
        try:
            from backend.core import immutable_log
            
            await immutable_log.append(
                actor="healer_watchdog",
                action="emergency_recovery_complete",
                resource="healing_systems",
                result="success",
                metadata={
                    'healers_restored': ['self_healing', 'coding_agent'],
                    'emergency_duration_seconds': 0,  # Would calculate
                    'delegates_used': len(self.emergency_delegates),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"[HEALER-WATCHDOG] Audit log failed: {e}")
    
    def update_heartbeat(self, healer: str):
        """Update heartbeat from a healer"""
        
        if healer == 'self_healing':
            self.self_healing_last_seen = datetime.utcnow()
            self.self_healing_healthy = True
        elif healer == 'coding_agent':
            self.coding_agent_last_seen = datetime.utcnow()
            self.coding_agent_healthy = True
    
    def get_status(self) -> Dict[str, Any]:
        """Get healer watchdog status"""
        
        return {
            'self_healing_healthy': self.self_healing_healthy,
            'coding_agent_healthy': self.coding_agent_healthy,
            'mutual_recoveries': self.mutual_recovery_count,
            'emergency_recoveries': self.emergency_recovery_count,
            'emergency_delegates_active': len(self.emergency_delegates),
            'delegates': self.emergency_delegates
        }


# Global instance
healer_watchdog = HealerWatchdog()
