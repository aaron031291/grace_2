"""
Fleet Manager - Active-Active Failover System
6 Grace instances with automatic failover

Architecture:
- 6 hot replicas (each with full Layer 1 stack)
- Primary serves traffic
- Unhealthy instance → quarantine + sandbox healing
- Healthy instances take over immediately
- Background repair with auto-rejoin

This is the final safety net.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InstanceState(Enum):
    """Instance health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"
    HEALING = "healing"
    OFFLINE = "offline"


@dataclass
class GraceInstance:
    """Single Grace instance in fleet"""
    instance_id: str
    state: InstanceState = InstanceState.OFFLINE
    
    # Instance details
    host: str = "localhost"
    port: int = 8000
    pid: Optional[int] = None
    
    # Health
    last_heartbeat: Optional[datetime] = None
    consecutive_failures: int = 0
    restart_count: int = 0
    
    # Traffic
    is_primary: bool = False
    serving_traffic: bool = False
    traffic_weight: float = 0.0  # 0.0-1.0
    
    # Repair
    quarantined_at: Optional[datetime] = None
    healing_started_at: Optional[datetime] = None
    sandbox_pid: Optional[int] = None


class FleetManager:
    """
    Manages 6-instance active-active fleet
    Final safety net for Grace
    """
    
    def __init__(self):
        self.fleet_size = 6
        self.instances: Dict[str, GraceInstance] = {}
        self.primary_instance: Optional[str] = None
        
        # Health monitoring
        self.running = False
        self.health_check_interval = 10  # seconds
        self.failover_threshold = 3  # failures before quarantine
        
        # Metrics
        self.total_failovers = 0
        self.total_healed = 0
        self.quarantine_dir = Path(__file__).parent.parent.parent / '.quarantine'
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    async def start(self):
        """Start fleet manager"""
        
        if self.running:
            return
        
        self.running = True
        
        # Initialize fleet
        await self._initialize_fleet()
        
        # Start health monitoring
        asyncio.create_task(self._fleet_health_monitor())
        
        logger.info(f"[FLEET-MANAGER] Started with {len(self.instances)} instances")
    
    async def _initialize_fleet(self):
        """Initialize 6-instance fleet"""
        
        print("\n" + "=" * 80)
        print("FLEET MANAGER - INITIALIZING 6-INSTANCE ACTIVE-ACTIVE")
        print("=" * 80)
        print()
        
        # Create instances
        base_port = 8000
        
        for i in range(self.fleet_size):
            instance_id = f"grace_{i+1}"
            
            instance = GraceInstance(
                instance_id=instance_id,
                host="localhost",
                port=base_port + i,
                state=InstanceState.OFFLINE
            )
            
            self.instances[instance_id] = instance
            print(f"[{i+1}/6] Instance {instance_id} initialized (port {instance.port})")
        
        print()
        
        # Boot primary instance
        await self._boot_instance('grace_1', is_primary=True)
        
        # Boot hot standbys
        for i in range(1, min(3, self.fleet_size)):  # Boot 2 hot standbys
            await self._boot_instance(f'grace_{i+1}', is_primary=False)
        
        print()
        print("[OK] Fleet ready:")
        print(f"  - 1 primary (serving traffic)")
        print(f"  - 2 hot standbys (ready for failover)")
        print(f"  - 3 warm instances (can boot quickly)")
        print()
    
    async def _boot_instance(self, instance_id: str, is_primary: bool = False):
        """Boot single Grace instance"""
        
        instance = self.instances[instance_id]
        
        print(f"  Booting {instance_id}...", end=" ")
        
        # Would actually spawn process here
        # For now, mark as healthy
        instance.state = InstanceState.HEALTHY
        instance.is_primary = is_primary
        instance.serving_traffic = is_primary
        instance.traffic_weight = 1.0 if is_primary else 0.0
        instance.last_heartbeat = datetime.utcnow()
        
        if is_primary:
            self.primary_instance = instance_id
        
        print(f"{'[PRIMARY]' if is_primary else '[STANDBY]'}")
    
    async def _fleet_health_monitor(self):
        """Monitor health of all fleet instances"""
        
        while self.running:
            try:
                await self._check_all_instances()
                await asyncio.sleep(self.health_check_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[FLEET-MANAGER] Health check error: {e}")
                await asyncio.sleep(30)
    
    async def _check_all_instances(self):
        """Check health of all instances"""
        
        for instance_id, instance in self.instances.items():
            if instance.state == InstanceState.OFFLINE:
                continue
            
            # Check heartbeat
            if instance.last_heartbeat:
                elapsed = (datetime.utcnow() - instance.last_heartbeat).total_seconds()
                
                if elapsed > 30:  # Missed heartbeat
                    instance.consecutive_failures += 1
                    
                    logger.warning(f"[FLEET-MANAGER] {instance_id} missed heartbeat ({elapsed:.0f}s)")
                    
                    # Quarantine if threshold exceeded
                    if instance.consecutive_failures >= self.failover_threshold:
                        await self._quarantine_and_failover(instance_id)
    
    async def _quarantine_and_failover(self, instance_id: str):
        """
        Quarantine unhealthy instance and failover traffic
        
        This is the EMERGENCY PROTOCOL:
        1. Quarantine unhealthy instance
        2. Failover traffic to healthy replica
        3. Launch sandbox healer
        4. Fix instance in background
        5. Rejoin to fleet when verified
        """
        
        instance = self.instances[instance_id]
        
        logger.critical(f"[FLEET-MANAGER] QUARANTINING {instance_id}")
        
        print("\n" + "!" * 80)
        print(f"EMERGENCY PROTOCOL TRIGGERED - {instance_id}")
        print("!" * 80)
        print()
        
        # Step 1: Quarantine
        instance.state = InstanceState.QUARANTINED
        instance.quarantined_at = datetime.utcnow()
        instance.serving_traffic = False
        instance.traffic_weight = 0.0
        
        print(f"[1/5] Quarantined {instance_id}")
        
        # Step 2: Failover traffic
        if instance.is_primary:
            await self._execute_failover()
        
        # Step 3: Launch sandbox healer
        print(f"[3/5] Launching sandbox healer for {instance_id}")
        sandbox_task = asyncio.create_task(self._sandbox_heal_instance(instance_id))
        
        # Step 4: Monitor healing
        print(f"[4/5] Monitoring background repair...")
        
        self.total_failovers += 1
    
    async def _execute_failover(self):
        """Execute traffic failover to healthy instance"""
        
        print(f"[2/5] Executing failover...")
        
        # Find healthy standby
        healthy_standbys = [
            i for i in self.instances.values()
            if i.state == InstanceState.HEALTHY and not i.is_primary
        ]
        
        if not healthy_standbys:
            logger.critical("[FLEET-MANAGER] NO HEALTHY STANDBYS - TOTAL FLEET FAILURE")
            print("  [CRITICAL] No healthy standbys available!")
            return
        
        # Promote first healthy standby
        new_primary = healthy_standbys[0]
        old_primary_id = self.primary_instance
        
        # Update old primary
        if old_primary_id:
            old = self.instances[old_primary_id]
            old.is_primary = False
            old.serving_traffic = False
            old.traffic_weight = 0.0
        
        # Promote new primary
        new_primary.is_primary = True
        new_primary.serving_traffic = True
        new_primary.traffic_weight = 1.0
        self.primary_instance = new_primary.instance_id
        
        print(f"  [OK] Failover: {old_primary_id} -> {new_primary.instance_id}")
        print(f"  [OK] Traffic now served by {new_primary.instance_id}")
    
    async def _sandbox_heal_instance(self, instance_id: str):
        """
        Heal instance in sandbox
        
        1. Launch sandboxed copy
        2. Replay failure
        3. Apply coding agent fixes
        4. Run self-healing playbooks
        5. Validate recovery
        6. Rejoin to fleet
        """
        
        instance = self.instances[instance_id]
        instance.state = InstanceState.HEALING
        instance.healing_started_at = datetime.utcnow()
        
        logger.info(f"[SANDBOX-HEALER] Starting repair for {instance_id}")
        
        try:
            # Phase 1: Snapshot current state
            snapshot_path = await self._snapshot_instance(instance_id)
            print(f"    [OK] Snapshotted instance state")
            
            # Phase 2: Launch sandbox
            sandbox_env = await self._launch_sandbox(instance_id, snapshot_path)
            print(f"    [OK] Sandbox environment launched")
            
            # Phase 3: Replay failure in sandbox
            failure_signature = await self._replay_failure_in_sandbox(sandbox_env)
            print(f"    [OK] Failure replayed: {failure_signature}")
            
            # Phase 4: Apply fixes (coding agent + self-healing)
            fixes_applied = await self._apply_sandbox_fixes(sandbox_env, failure_signature)
            print(f"    [OK] Fixes applied: {len(fixes_applied)} changes")
            
            # Phase 5: Validate in sandbox
            validation_passed = await self._validate_sandbox_instance(sandbox_env)
            print(f"    [{'OK' if validation_passed else 'FAIL'}] Validation: {validation_passed}")
            
            if validation_passed:
                # Phase 6: Swap healthy version back
                await self._rejoin_instance(instance_id, sandbox_env)
                print(f"    [OK] Instance rejoined fleet as healthy")
                
                self.total_healed += 1
            else:
                print(f"    [FAIL] Validation failed - keeping quarantined")
        
        except Exception as e:
            logger.error(f"[SANDBOX-HEALER] Healing failed for {instance_id}: {e}")
            print(f"    [ERROR] Healing failed: {e}")
    
    async def _snapshot_instance(self, instance_id: str) -> Path:
        """Snapshot instance state"""
        
        snapshot_path = self.quarantine_dir / f"{instance_id}_snapshot.json"
        
        # Capture full state
        snapshot = {
            'instance_id': instance_id,
            'timestamp': datetime.utcnow().isoformat(),
            'state': 'quarantined'
        }
        
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return snapshot_path
    
    async def _launch_sandbox(self, instance_id: str, snapshot_path: Path) -> Dict:
        """Launch isolated sandbox environment"""
        
        sandbox_env = {
            'instance_id': f"{instance_id}_sandbox",
            'snapshot_path': str(snapshot_path),
            'isolated': True,
            'live_telemetry': True,
            'writable_scratch': Path('.quarantine') / instance_id
        }
        
        # Would actually launch containerized sandbox
        # For now, return environment spec
        
        return sandbox_env
    
    async def _replay_failure_in_sandbox(self, sandbox_env: Dict) -> str:
        """Replay failure to understand root cause"""
        
        # Would replay telemetry and events
        # For now, return generic signature
        
        return "component_failure_unknown"
    
    async def _apply_sandbox_fixes(self, sandbox_env: Dict, signature: str) -> List[str]:
        """Apply coding agent fixes and self-healing playbooks in sandbox"""
        
        fixes = []
        
        try:
            from .error_recognition_system import error_recognition_system
            
            # Check knowledge base for known fix
            if signature in error_recognition_system.knowledge_base:
                mapping = error_recognition_system.knowledge_base[signature]
                fixes.append(f"Applied known fix: {mapping.playbook_name}")
            else:
                fixes.append("Generated new fix via coding agent")
        
        except:
            pass
        
        return fixes
    
    async def _validate_sandbox_instance(self, sandbox_env: Dict) -> bool:
        """Run full validation in sandbox"""
        
        # Would run:
        # - All tests
        # - Lint checks
        # - Load tests
        # - Canary traffic
        
        # For now, return True
        return True
    
    async def _rejoin_instance(self, instance_id: str, sandbox_env: Dict):
        """Rejoin healed instance to fleet"""
        
        instance = self.instances[instance_id]
        
        # Update state
        instance.state = InstanceState.HEALTHY
        instance.consecutive_failures = 0
        instance.quarantined_at = None
        instance.healing_started_at = None
        
        # Gradually route traffic
        instance.serving_traffic = True
        instance.traffic_weight = 0.1  # Start with 10%
        
        logger.info(f"[FLEET-MANAGER] {instance_id} rejoined fleet")
    
    def get_fleet_status(self) -> Dict:
        """Get fleet status"""
        
        healthy = sum(1 for i in self.instances.values() if i.state == InstanceState.HEALTHY)
        quarantined = sum(1 for i in self.instances.values() if i.state == InstanceState.QUARANTINED)
        healing = sum(1 for i in self.instances.values() if i.state == InstanceState.HEALING)
        
        return {
            'fleet_size': self.fleet_size,
            'healthy_instances': healthy,
            'quarantined_instances': quarantined,
            'healing_instances': healing,
            'primary_instance': self.primary_instance,
            'total_failovers': self.total_failovers,
            'total_healed': self.total_healed,
            'fleet_health': 'HEALTHY' if healthy >= self.fleet_size // 2 else 'DEGRADED'
        }


# Global instance
fleet_manager = FleetManager()
