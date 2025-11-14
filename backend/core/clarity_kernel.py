"""
Clarity Kernel
First-class kernel for component registry, trust scoring, and manifest management

Part of Layer 1 - Always running, maintains who's running and their health
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .message_bus import message_bus, MessagePriority
from .immutable_log import immutable_log
from .schemas import MessageType, create_kernel_message, TrustLevel

logger = logging.getLogger(__name__)


class ComponentManifest:
    """Manifest for a registered component/kernel"""
    
    def __init__(
        self,
        component_id: str,
        component_name: str,
        component_type: str,
        capabilities: List[str],
        contracts: Dict[str, Any]
    ):
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.capabilities = capabilities
        self.contracts = contracts
        
        # Status tracking
        self.registered_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.last_status_report = None
        self.trust_score = 50.0  # Start at 50%
        self.health_state = 'unknown'  # unknown, healthy, degraded, unhealthy
        
        # Metrics
        self.kpi_history = []
        self.heartbeat_misses = 0
        self.contract_violations = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'component_name': self.component_name,
            'component_type': self.component_type,
            'capabilities': self.capabilities,
            'contracts': self.contracts,
            'registered_at': self.registered_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'trust_score': self.trust_score,
            'health_state': self.health_state,
            'heartbeat_misses': self.heartbeat_misses,
            'contract_violations': self.contract_violations
        }


class ClarityKernel:
    """
    Clarity Kernel - First-class kernel on the bus
    
    Responsibilities:
    - Component registry (who's running)
    - Manifest management (what they promise)
    - Trust score tracking (how reliable they are)
    - Health validation (are they meeting contracts)
    - Quarantine triggers (if misbehaving)
    
    Listens to:
    - kernel.register (new components)
    - kernel.status (health reports)
    - kernel.heartbeat (liveness)
    
    Publishes:
    - kernel.manifest.updated (manifest changes)
    - trust.score.updated (trust changes)
    - event.quarantine (component misbehaving)
    """
    
    def __init__(self):
        self.running = False
        self.component_registry = {}
        self.register_queue = None
        self.status_queue = None
        self.heartbeat_queue = None
        
        # Configuration
        self.heartbeat_timeout = 60  # seconds
        self.trust_increase_rate = 5.0  # % per successful report
        self.trust_decrease_rate = 10.0  # % per violation
        self.quarantine_threshold = 30.0  # Trust score below this = quarantine
    
    async def start(self):
        """Start Clarity Kernel"""
        
        self.running = True
        
        # Subscribe to registration events
        self.register_queue = await message_bus.subscribe(
            subscriber='clarity_kernel',
            topic='kernel.register'
        )
        
        # Subscribe to status events
        self.status_queue = await message_bus.subscribe(
            subscriber='clarity_kernel',
            topic='kernel.status'
        )
        
        # Subscribe to heartbeats
        self.heartbeat_queue = await message_bus.subscribe(
            subscriber='clarity_kernel',
            topic='kernel.heartbeat'
        )
        
        # Start processing loops
        asyncio.create_task(self._registration_loop())
        asyncio.create_task(self._status_loop())
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._health_check_loop())
        
        logger.info("[CLARITY-KERNEL] Started - component registry active")
    
    async def _registration_loop(self):
        """TRIGGER LOOP: Process component registrations"""
        
        while self.running:
            try:
                # Wait for registration
                message = await self.register_queue.get()
                
                payload = message.payload if hasattr(message, 'payload') else message
                
                # Register component
                component_id = payload.get('component_id', f"comp_{len(self.component_registry)}")
                
                manifest = ComponentManifest(
                    component_id=component_id,
                    component_name=payload.get('component_name', 'unknown'),
                    component_type=payload.get('component_type', 'kernel'),
                    capabilities=payload.get('capabilities', []),
                    contracts=payload.get('contracts', {})
                )
                
                self.component_registry[component_id] = manifest
                
                logger.info(f"[CLARITY-KERNEL] Registered: {manifest.component_name}")
                
                # Publish manifest
                await self._publish_manifest_update(component_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CLARITY-KERNEL] Registration loop error: {e}")
    
    async def _status_loop(self):
        """TRIGGER LOOP: Process status reports"""
        
        while self.running:
            try:
                # Wait for status report
                message = await self.status_queue.get()
                
                payload = message.payload if hasattr(message, 'payload') else message
                
                component_id = payload.get('component_id') or payload.get('kernel_name')
                
                if component_id and component_id in self.component_registry:
                    manifest = self.component_registry[component_id]
                    
                    # Update status
                    manifest.last_status_report = payload
                    manifest.health_state = payload.get('health', 'unknown')
                    
                    # Validate KPIs against contracts
                    metrics = payload.get('metrics', {})
                    contract_met = await self._validate_contract(manifest, metrics)
                    
                    if contract_met:
                        # Increase trust
                        await self._update_trust_score(component_id, increase=True)
                    else:
                        # Decrease trust (contract violation)
                        manifest.contract_violations += 1
                        await self._update_trust_score(component_id, increase=False)
                        
                        # Check if quarantine needed
                        if manifest.trust_score < self.quarantine_threshold:
                            await self._trigger_quarantine(component_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CLARITY-KERNEL] Status loop error: {e}")
    
    async def _heartbeat_loop(self):
        """TRIGGER LOOP: Process heartbeats"""
        
        while self.running:
            try:
                # Wait for heartbeat with timeout
                try:
                    message = await asyncio.wait_for(self.heartbeat_queue.get(), timeout=1.0)
                    
                    payload = message.payload if hasattr(message, 'payload') else message
                    
                    component_id = payload.get('component_id') or payload.get('kernel_name')
                    
                    if component_id and component_id in self.component_registry:
                        manifest = self.component_registry[component_id]
                        manifest.last_heartbeat = datetime.utcnow()
                        manifest.heartbeat_misses = 0
                
                except asyncio.TimeoutError:
                    pass  # No heartbeat this second
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CLARITY-KERNEL] Heartbeat loop error: {e}")
    
    async def _health_check_loop(self):
        """TRIGGER LOOP: Check component health based on heartbeats"""
        
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                now = datetime.utcnow()
                
                for component_id, manifest in self.component_registry.items():
                    # Check heartbeat timeout
                    if manifest.last_heartbeat:
                        time_since = now - manifest.last_heartbeat
                        
                        if time_since.total_seconds() > self.heartbeat_timeout:
                            manifest.heartbeat_misses += 1
                            
                            logger.warning(f"[CLARITY-KERNEL] {manifest.component_name} missed heartbeat")
                            
                            # Decrease trust
                            await self._update_trust_score(component_id, increase=False, reason='heartbeat_miss')
                            
                            # Quarantine if too many misses
                            if manifest.heartbeat_misses > 3:
                                await self._trigger_quarantine(component_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CLARITY-KERNEL] Health check loop error: {e}")
    
    async def _validate_contract(self, manifest: ComponentManifest, metrics: Dict[str, Any]) -> bool:
        """Validate metrics against component's contracts"""
        
        contracts = manifest.contracts
        
        if not contracts:
            return True  # No contracts to validate
        
        # Check each contract
        for key, expected in contracts.items():
            if key in metrics:
                actual = metrics[key]
                
                # Simple threshold check (can be more complex)
                if isinstance(expected, dict):
                    # Range check
                    if 'min' in expected and actual < expected['min']:
                        return False
                    if 'max' in expected and actual > expected['max']:
                        return False
        
        return True
    
    async def _update_trust_score(
        self,
        component_id: str,
        increase: bool,
        reason: str = 'performance'
    ):
        """Update component trust score"""
        
        manifest = self.component_registry.get(component_id)
        
        if not manifest:
            return
        
        old_score = manifest.trust_score
        
        if increase:
            manifest.trust_score = min(100.0, manifest.trust_score + self.trust_increase_rate)
        else:
            manifest.trust_score = max(0.0, manifest.trust_score - self.trust_decrease_rate)
        
        # Publish trust update
        await message_bus.publish(
            source='clarity_kernel',
            topic='trust.score.updated',
            payload={
                'component_id': component_id,
                'component_name': manifest.component_name,
                'old_score': old_score,
                'new_score': manifest.trust_score,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.NORMAL
        )
        
        # Log change
        await immutable_log.append(
            actor='clarity_kernel',
            action='trust_score_update',
            resource=component_id,
            decision={
                'old_score': old_score,
                'new_score': manifest.trust_score,
                'change': manifest.trust_score - old_score,
                'reason': reason
            }
        )
        
        logger.info(f"[CLARITY-KERNEL] Trust updated: {manifest.component_name} {old_score:.1f}% -> {manifest.trust_score:.1f}%")
    
    async def _publish_manifest_update(self, component_id: str):
        """Publish manifest update"""
        
        manifest = self.component_registry.get(component_id)
        
        if not manifest:
            return
        
        await message_bus.publish(
            source='clarity_kernel',
            topic='kernel.manifest.updated',
            payload=manifest.to_dict(),
            priority=MessagePriority.NORMAL
        )
        
        logger.info(f"[CLARITY-KERNEL] Manifest published: {manifest.component_name}")
    
    async def _trigger_quarantine(self, component_id: str):
        """Trigger quarantine for misbehaving component"""
        
        manifest = self.component_registry.get(component_id)
        
        if not manifest:
            return
        
        logger.warning(f"[CLARITY-KERNEL] Quarantining: {manifest.component_name} (trust: {manifest.trust_score:.1f}%)")
        
        # Publish quarantine event
        await message_bus.publish(
            source='clarity_kernel',
            topic='event.quarantine',
            payload={
                'component_id': component_id,
                'component_name': manifest.component_name,
                'reason': 'low_trust_score',
                'trust_score': manifest.trust_score,
                'violations': manifest.contract_violations,
                'heartbeat_misses': manifest.heartbeat_misses,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.HIGH
        )
        
        # Log quarantine
        await immutable_log.append(
            actor='clarity_kernel',
            action='component_quarantined',
            resource=component_id,
            decision={
                'reason': 'low_trust_score',
                'trust_score': manifest.trust_score,
                'violations': manifest.contract_violations
            }
        )
    
    def get_component_manifest(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get manifest for component"""
        
        manifest = self.component_registry.get(component_id)
        
        if manifest:
            return manifest.to_dict()
        
        return None
    
    def get_all_manifests(self) -> List[Dict[str, Any]]:
        """Get all component manifests"""
        return [m.to_dict() for m in self.component_registry.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Clarity Kernel statistics"""
        
        total = len(self.component_registry)
        healthy = sum(1 for m in self.component_registry.values() if m.health_state == 'healthy')
        quarantined = sum(1 for m in self.component_registry.values() if m.trust_score < self.quarantine_threshold)
        
        avg_trust = sum(m.trust_score for m in self.component_registry.values()) / total if total > 0 else 0
        
        return {
            'running': self.running,
            'total_components': total,
            'healthy_components': healthy,
            'quarantined_components': quarantined,
            'avg_trust_score': avg_trust,
            'components': {
                comp_id: {
                    'name': m.component_name,
                    'trust': m.trust_score,
                    'health': m.health_state
                }
                for comp_id, m in self.component_registry.items()
            }
        }


# Global instance - Clarity as a first-class kernel
clarity_kernel = ClarityKernel()
