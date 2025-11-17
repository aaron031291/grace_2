"""
Multi-Agent Shard System - Distributed autonomous sub-agents

Shards GRACE into multiple autonomous sub-agents that:
- Operate independently within their domain/scope
- Coordinate peer-to-peer via signed messages
- Share common spine (trigger mesh, trust cores, ledger)
- Self-organize based on capabilities and workload
- Scale elastically under meta loop orchestration
"""

import asyncio
import hashlib
import secrets
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class ShardType(Enum):
    DOMAIN = "domain"              # Owns specific domain (infra, app, data)
    GEOGRAPHIC = "geographic"      # Owns specific region/zone
    WORKLOAD = "workload"          # Specialized workload (incident, preventive)
    SWAT = "swat"                  # Temporary specialist team
    REPLICA = "replica"            # Fault-tolerant replica


class ShardStatus(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    OVERLOADED = "overloaded"
    DEGRADED = "degraded"
    RETIRING = "retiring"
    TERMINATED = "terminated"


class CapabilityType(Enum):
    MEMORY_STEWARD = "memory_steward"
    INGESTION_LEAD = "ingestion_lead"
    SELF_HEALING = "self_healing"
    SECURITY_SENTINEL = "security_sentinel"
    CAPACITY_PLANNER = "capacity_planner"
    COST_OPTIMIZER = "cost_optimizer"
    COMPLIANCE_AUDITOR = "compliance_auditor"


class MessageType(Enum):
    OFFER = "offer"               # "I can help with X"
    NEED = "need"                 # "I need help with Y"
    REQUEST = "request"           # "Please do X"
    RESPONSE = "response"         # "Here's the result"
    STATE_DELTA = "state_delta"   # "My state changed"
    HANDOFF = "handoff"           # "Taking over responsibility"
    NEGOTIATION = "negotiation"   # "Let's coordinate"


@dataclass
class ShardIdentity:
    """Cryptographic identity for a shard"""
    shard_id: str
    public_key: str
    private_key: str
    capabilities: List[CapabilityType]
    trust_level: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def sign_message(self, message: str) -> str:
        """Sign message with private key"""
        data = f"{message}:{self.private_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self, message: str, signature: str, sender_public_key: str) -> bool:
        """Verify message signature"""
        # Simplified verification - in production use proper crypto
        expected = hashlib.sha256(f"{message}:{sender_public_key}".encode()).hexdigest()
        return signature == expected


@dataclass
class ShardScope:
    """Defines what a shard is responsible for"""
    domain: Optional[str] = None        # e.g., "infrastructure", "application"
    geography: Optional[str] = None     # e.g., "us-east", "eu-west"
    workload_type: Optional[str] = None # e.g., "incident_response", "preventive"
    resource_pattern: Optional[str] = None  # Regex for resources
    policy_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class P2PMessage:
    """Peer-to-peer message between shards"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: Optional[str]  # None = broadcast
    payload: Dict[str, Any]
    signature: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl: int = 300  # seconds


@dataclass
class StateDelta:
    """State change that can be merged across shards"""
    delta_id: str
    shard_id: str
    entity_type: str
    entity_id: str
    operation: str  # "create", "update", "delete"
    changes: Dict[str, Any]
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def merge(self, other: 'StateDelta') -> 'StateDelta':
        """Merge two state deltas (CRDT-like)"""
        # Last-write-wins with timestamp
        if self.timestamp > other.timestamp:
            return self
        else:
            return other


class AgentShard:
    """Single autonomous agent shard"""
    
    def __init__(
        self,
        shard_type: ShardType,
        scope: ShardScope,
        capabilities: List[CapabilityType]
    ):
        self.shard_id = f"shard_{secrets.token_hex(8)}"
        self.shard_type = shard_type
        self.scope = scope
        self.status = ShardStatus.INITIALIZING
        
        # Identity & security
        self.identity = ShardIdentity(
            shard_id=self.shard_id,
            public_key=secrets.token_hex(32),
            private_key=secrets.token_hex(32),
            capabilities=capabilities,
            trust_level=5
        )
        
        # Local state
        self.local_state: Dict[str, Any] = {}
        self.workload_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Any] = {}
        
        # P2P communication
        self.peers: Dict[str, Dict] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_requests: Dict[str, P2PMessage] = {}
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_latency_seconds": 0.0,
            "load_factor": 0.0,
            "uptime_seconds": 0.0
        }
        
        self.started_at: Optional[datetime] = None
        self.running = False
    
    async def start(self):
        """Start the shard"""
        self.status = ShardStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.running = True
        
        # Subscribe to trigger mesh for relevant events
        await self._subscribe_to_events()
        
        # Start background tasks
        asyncio.create_task(self._process_workload())
        asyncio.create_task(self._process_messages())
        asyncio.create_task(self._heartbeat())
        
        await immutable_log.append(
            actor=self.shard_id,
            action="shard_started",
            resource=self.shard_id,
            subsystem="multi_agent_shards",
            payload={
                "shard_type": self.shard_type.value,
                "capabilities": [c.value for c in self.identity.capabilities]
            },
            result="started"
        )
        
        print(f"✓ Shard {self.shard_id} started ({self.shard_type.value})")
    
    async def stop(self):
        """Stop the shard gracefully"""
        self.status = ShardStatus.RETIRING
        
        # Hand off active tasks
        for task_id in list(self.active_tasks.keys()):
            await self._handoff_task(task_id)
        
        self.running = False
        self.status = ShardStatus.TERMINATED
        
        await immutable_log.append(
            actor=self.shard_id,
            action="shard_stopped",
            resource=self.shard_id,
            subsystem="multi_agent_shards",
            payload={},
            result="stopped"
        )
    
    async def register_peer(self, peer_id: str, peer_info: Dict):
        """Register another shard as peer"""
        self.peers[peer_id] = {
            **peer_info,
            "registered_at": datetime.utcnow(),
            "last_seen": datetime.utcnow()
        }
    
    async def send_message(
        self,
        message_type: MessageType,
        recipient_id: Optional[str],
        payload: Dict[str, Any]
    ):
        """Send P2P message to another shard"""
        message = P2PMessage(
            message_id=f"msg_{secrets.token_hex(8)}",
            message_type=message_type,
            sender_id=self.shard_id,
            recipient_id=recipient_id,
            payload=payload,
            signature=self.identity.sign_message(json.dumps(payload))
        )
        
        # Publish to P2P mesh
        await trigger_mesh.publish(TriggerEvent(
            event_type=f"shard.p2p.{message_type.value}",
            source=self.shard_id,
            actor=self.shard_id,
            resource=recipient_id or "broadcast",
            payload={
                "message_id": message.message_id,
                "recipient": recipient_id,
                "payload": payload,
                "signature": message.signature
            },
            timestamp=datetime.utcnow()
        ))
    
    async def offer_capability(self, capability: CapabilityType, details: Dict):
        """Offer capability to peer shards"""
        await self.send_message(
            message_type=MessageType.OFFER,
            recipient_id=None,  # Broadcast
            payload={
                "capability": capability.value,
                "details": details,
                "load_factor": self.metrics["load_factor"]
            }
        )
    
    async def request_help(self, need_type: str, details: Dict):
        """Request help from peer shards"""
        await self.send_message(
            message_type=MessageType.NEED,
            recipient_id=None,  # Broadcast
            payload={
                "need_type": need_type,
                "details": details,
                "urgency": details.get("urgency", "normal")
            }
        )
    
    async def publish_state_delta(self, delta: StateDelta):
        """Publish local state change to peers"""
        await self.send_message(
            message_type=MessageType.STATE_DELTA,
            recipient_id=None,  # Broadcast
            payload={
                "delta_id": delta.delta_id,
                "entity_type": delta.entity_type,
                "entity_id": delta.entity_id,
                "operation": delta.operation,
                "changes": delta.changes,
                "version": delta.version
            }
        )
    
    async def _subscribe_to_events(self):
        """Subscribe to relevant events based on scope"""
        
        # Subscribe to events matching scope
        if self.scope.domain:
            await trigger_mesh.subscribe(f"{self.scope.domain}.*", self._handle_event)
        
        # Subscribe to P2P messages
        await trigger_mesh.subscribe("shard.p2p.*", self._handle_p2p_message)
    
    async def _handle_event(self, event: TriggerEvent):
        """Handle event from trigger mesh"""
        
        # Check if this event is in our scope
        if not await self._is_in_scope(event):
            return
        
        # Add to workload queue
        await self.workload_queue.put({
            "type": "event",
            "event": event,
            "received_at": datetime.utcnow()
        })
    
    async def _handle_p2p_message(self, event: TriggerEvent):
        """Handle P2P message from another shard"""
        
        # Check if message is for us
        recipient = event.payload.get("recipient")
        if recipient and recipient != self.shard_id:
            return
        
        message = P2PMessage(
            message_id=event.payload["message_id"],
            message_type=MessageType[event.event_type.split(".")[-1].upper()],
            sender_id=event.source,
            recipient_id=recipient,
            payload=event.payload.get("payload", {}),
            signature=event.payload.get("signature", "")
        )
        
        await self.message_queue.put(message)
    
    async def _is_in_scope(self, event: TriggerEvent) -> bool:
        """Check if event is in this shard's scope"""
        
        if self.scope.domain and not event.source.startswith(self.scope.domain):
            return False
        
        if self.scope.workload_type:
            if self.scope.workload_type == "preventive" and "alert" in event.event_type:
                return False
            if self.scope.workload_type == "incident_response" and "proactive" in event.event_type:
                return False
        
        return True
    
    async def _process_workload(self):
        """Process queued workload"""
        
        while self.running:
            try:
                work = await asyncio.wait_for(
                    self.workload_queue.get(),
                    timeout=1.0
                )
                
                if self.status == ShardStatus.OVERLOADED:
                    # Offload to peer
                    await self._offload_work(work)
                else:
                    await self._execute_work(work)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"✗ Shard {self.shard_id} workload error: {e}")
    
    async def _process_messages(self):
        """Process P2P messages"""
        
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                if message.message_type == MessageType.OFFER:
                    await self._handle_offer(message)
                elif message.message_type == MessageType.NEED:
                    await self._handle_need(message)
                elif message.message_type == MessageType.REQUEST:
                    await self._handle_request(message)
                elif message.message_type == MessageType.STATE_DELTA:
                    await self._handle_state_delta(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"✗ Shard {self.shard_id} message error: {e}")
    
    async def _heartbeat(self):
        """Send heartbeat and update metrics"""
        
        while self.running:
            await asyncio.sleep(30)
            
            if self.started_at:
                self.metrics["uptime_seconds"] = (
                    datetime.utcnow() - self.started_at
                ).total_seconds()
            
            self.metrics["load_factor"] = (
                self.workload_queue.qsize() / 100.0
            )
            
            # Publish heartbeat
            await trigger_mesh.publish(TriggerEvent(
                event_type="shard.heartbeat",
                source=self.shard_id,
                actor=self.shard_id,
                resource=self.shard_id,
                payload={
                    "status": self.status.value,
                    "metrics": self.metrics,
                    "active_tasks": len(self.active_tasks)
                },
                timestamp=datetime.utcnow()
            ))
    
    async def _execute_work(self, work: Dict):
        """Execute work item"""
        task_id = f"task_{secrets.token_hex(8)}"
        self.active_tasks[task_id] = work
        
        start = datetime.utcnow()
        
        try:
            # Placeholder for actual work execution
            await asyncio.sleep(0.1)
            
            duration = (datetime.utcnow() - start).total_seconds()
            
            # Update metrics
            self.metrics["tasks_completed"] += 1
            self.metrics["avg_latency_seconds"] = (
                (self.metrics["avg_latency_seconds"] * (self.metrics["tasks_completed"] - 1) + duration) /
                self.metrics["tasks_completed"]
            )
            
        except Exception as e:
            self.metrics["tasks_failed"] += 1
        finally:
            del self.active_tasks[task_id]
    
    async def _offload_work(self, work: Dict):
        """Offload work to less-loaded peer"""
        
        # Find least loaded peer with matching capability
        best_peer = None
        min_load = float('inf')
        
        for peer_id, peer_info in self.peers.items():
            load = peer_info.get("load_factor", 1.0)
            if load < min_load:
                min_load = load
                best_peer = peer_id
        
        if best_peer:
            await self.send_message(
                message_type=MessageType.REQUEST,
                recipient_id=best_peer,
                payload={"work": work}
            )
    
    async def _handoff_task(self, task_id: str):
        """Hand off task to another shard"""
        
        if task_id not in self.active_tasks:
            return
        
        task = self.active_tasks[task_id]
        
        await self.send_message(
            message_type=MessageType.HANDOFF,
            recipient_id=None,  # Let any peer pick it up
            payload={"task_id": task_id, "task": task}
        )
    
    async def _handle_offer(self, message: P2PMessage):
        """Handle capability offer from peer"""
        capability = message.payload.get("capability")
        print(f"  -> Shard {self.shard_id} received offer: {capability} from {message.sender_id}")
    
    async def _handle_need(self, message: P2PMessage):
        """Handle help request from peer"""
        need_type = message.payload.get("need_type")
        
        # Check if we can help
        if await self._can_help_with(need_type):
            await self.send_message(
                message_type=MessageType.OFFER,
                recipient_id=message.sender_id,
                payload={"can_help_with": need_type}
            )
    
    async def _handle_request(self, message: P2PMessage):
        """Handle work request from peer"""
        work = message.payload.get("work")
        if work:
            await self.workload_queue.put(work)
    
    async def _handle_state_delta(self, message: P2PMessage):
        """Handle state delta from peer"""
        delta = StateDelta(
            delta_id=message.payload["delta_id"],
            shard_id=message.sender_id,
            entity_type=message.payload["entity_type"],
            entity_id=message.payload["entity_id"],
            operation=message.payload["operation"],
            changes=message.payload["changes"],
            version=message.payload["version"]
        )
        
        # Merge into local state
        await self._merge_state_delta(delta)
    
    async def _can_help_with(self, need_type: str) -> bool:
        """Check if shard can help with request"""
        return self.metrics["load_factor"] < 0.7
    
    async def _merge_state_delta(self, delta: StateDelta):
        """Merge state delta into local state"""
        # Simplified CRDT-like merge
        key = f"{delta.entity_type}:{delta.entity_id}"
        self.local_state[key] = delta.changes


class ShardCoordinator:
    """Coordinates fleet of agent shards"""
    
    def __init__(self):
        self.shards: Dict[str, AgentShard] = {}
        self.shard_registry: Dict[str, Dict] = {}
        self.running = False
    
    async def start(self):
        """Start shard coordinator"""
        self.running = True
        
        # Start default shards
        await self._spawn_default_shards()
        
        # Start coordinator loop
        asyncio.create_task(self._coordination_loop())
        
        print("✓ Shard Coordinator started")
    
    async def stop(self):
        """Stop all shards"""
        self.running = False
        
        for shard in list(self.shards.values()):
            await shard.stop()
        
        print("✓ All shards stopped")
    
    async def spawn_shard(
        self,
        shard_type: ShardType,
        scope: ShardScope,
        capabilities: List[CapabilityType]
    ) -> AgentShard:
        """Spawn new shard"""
        
        shard = AgentShard(shard_type, scope, capabilities)
        await shard.start()
        
        self.shards[shard.shard_id] = shard
        self.shard_registry[shard.shard_id] = {
            "shard_type": shard_type.value,
            "status": shard.status.value,
            "capabilities": [c.value for c in capabilities],
            "scope": scope,
            "created_at": datetime.utcnow()
        }
        
        # Introduce to existing shards
        for existing_shard in self.shards.values():
            if existing_shard.shard_id != shard.shard_id:
                await shard.register_peer(existing_shard.shard_id, {
                    "capabilities": existing_shard.identity.capabilities
                })
                await existing_shard.register_peer(shard.shard_id, {
                    "capabilities": shard.identity.capabilities
                })
        
        await immutable_log.append(
            actor="shard_coordinator",
            action="shard_spawned",
            resource=shard.shard_id,
            subsystem="multi_agent_shards",
            payload={
                "shard_type": shard_type.value,
                "capabilities": [c.value for c in capabilities]
            },
            result="spawned"
        )
        
        return shard
    
    async def retire_shard(self, shard_id: str):
        """Gracefully retire a shard"""
        
        if shard_id not in self.shards:
            return
        
        shard = self.shards[shard_id]
        await shard.stop()
        
        del self.shards[shard_id]
        del self.shard_registry[shard_id]
        
        await immutable_log.append(
            actor="shard_coordinator",
            action="shard_retired",
            resource=shard_id,
            subsystem="multi_agent_shards",
            payload={},
            result="retired"
        )
    
    async def _spawn_default_shards(self):
        """Spawn default shard fleet"""
        
        # Domain shards
        await self.spawn_shard(
            shard_type=ShardType.DOMAIN,
            scope=ShardScope(domain="infrastructure"),
            capabilities=[
                CapabilityType.SELF_HEALING,
                CapabilityType.CAPACITY_PLANNER
            ]
        )
        
        await self.spawn_shard(
            shard_type=ShardType.DOMAIN,
            scope=ShardScope(domain="application"),
            capabilities=[
                CapabilityType.SELF_HEALING,
                CapabilityType.INGESTION_LEAD
            ]
        )
        
        # Workload shards
        await self.spawn_shard(
            shard_type=ShardType.WORKLOAD,
            scope=ShardScope(workload_type="preventive"),
            capabilities=[CapabilityType.CAPACITY_PLANNER]
        )
    
    async def _coordination_loop(self):
        """Background coordination loop"""
        
        while self.running:
            await asyncio.sleep(60)
            
            # Check shard health
            for shard_id, shard in list(self.shards.items()):
                if shard.status == ShardStatus.OVERLOADED:
                    await self._rebalance_load(shard_id)
                elif shard.status == ShardStatus.IDLE:
                    # Consider retiring if idle too long
                    pass
    
    async def _rebalance_load(self, overloaded_shard_id: str):
        """Rebalance load from overloaded shard"""
        
        # Spawn helper shard with same capabilities
        overloaded = self.shards[overloaded_shard_id]
        
        await self.spawn_shard(
            shard_type=ShardType.REPLICA,
            scope=overloaded.scope,
            capabilities=overloaded.identity.capabilities
        )
    
    async def get_fleet_status(self) -> Dict[str, Any]:
        """Get status of entire shard fleet"""
        
        return {
            "total_shards": len(self.shards),
            "shards": [
                {
                    "shard_id": shard.shard_id,
                    "type": shard.shard_type.value,
                    "status": shard.status.value,
                    "metrics": shard.metrics,
                    "active_tasks": len(shard.active_tasks)
                }
                for shard in self.shards.values()
            ]
        }


shard_coordinator = ShardCoordinator()
