"""
Agent Core - Unified agentic layer powering all 10 domains

Provides shared sensing, trust, planning, execution, and learning
infrastructure that all domains plug into. Each domain becomes an
agentic participant through a standardized adapter interface.

This is the contract that domains must implement to leverage
GRACE's autonomous capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class DomainType(Enum):
    CORE = "core"                     # Platform ops, governance, self-healing
    TRANSCENDENCE = "transcendence"   # Agentic dev, code gen, task orchestration
    KNOWLEDGE = "knowledge"           # Information ingestion, search, trust scoring
    SECURITY = "security"             # Hunter: threat detection, quarantine
    ML = "ml"                         # Model training, deployment, auto-retrain
    TEMPORAL = "temporal"             # Causal reasoning, forecasting, simulation
    PARLIAMENT = "parliament"         # Governance proposals, voting, meta-learning
    FEDERATION = "federation"         # External integrations, connectors, vault
    SPEECH = "speech"                 # Voice interaction, TTS, recognition
    COGNITION = "cognition"           # Cross-domain intelligence, metrics, benchmarking


@dataclass
class TelemetrySchema:
    """Schema for domain telemetry"""
    metric_name: str
    metric_type: str  # "gauge", "counter", "histogram"
    unit: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class DomainHealthNode:
    """Health graph node contributed by domain"""
    node_id: str
    node_type: str
    name: str
    kpis: List[str]
    dependencies: List[str]
    risk_tier: str  # "critical", "high", "medium", "low"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainPlaybook:
    """Playbook contributed by domain"""
    playbook_id: str
    name: str
    description: str
    triggers: List[str]  # Event patterns that trigger this playbook
    preconditions: List[Dict]
    steps: List[Dict]
    verifications: List[Dict]
    rollback_steps: List[Dict]
    risk_level: str
    requires_approval: bool
    estimated_duration_seconds: int
    success_rate_baseline: float = 0.0


@dataclass
class DomainMetrics:
    """Standard metrics from domain"""
    domain: str
    timestamp: datetime
    health_score: float  # 0-100
    active_tasks: int
    completed_tasks_24h: int
    failed_tasks_24h: int
    avg_latency_seconds: float
    error_rate: float
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class DomainAdapter(ABC):
    """
    Base class for domain adapters.
    
    Each of the 10 domains implements this interface to integrate
    with the agentic spine. The adapter bridges domain-specific
    logic with the unified autonomous capabilities.
    """
    
    def __init__(self, domain_type: DomainType):
        self.domain_type = domain_type
        self.domain_id = domain_type.value
        self.enabled = True
        self.shard_id: Optional[str] = None
    
    @abstractmethod
    async def register_telemetry(self) -> List[TelemetrySchema]:
        """
        Define what metrics this domain publishes.
        
        The agentic spine will monitor these for anomalies,
        drift, and capacity needs.
        """
        pass
    
    @abstractmethod
    async def register_health_nodes(self) -> List[DomainHealthNode]:
        """
        Define health graph nodes for this domain.
        
        Nodes represent services, resources, or capabilities
        this domain manages. Used for blast radius calculation
        and dependency mapping.
        """
        pass
    
    @abstractmethod
    async def register_playbooks(self) -> List[DomainPlaybook]:
        """
        Define recovery playbooks for this domain.
        
        Playbooks encode domain expertise for autonomous
        incident resolution.
        """
        pass
    
    @abstractmethod
    async def collect_metrics(self) -> DomainMetrics:
        """
        Collect current metrics from this domain.
        
        Called periodically by the agentic spine to gather
        health and performance data.
        """
        pass
    
    @abstractmethod
    async def execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute domain-specific action.
        
        Called by autonomous planner when executing playbooks.
        Must return result with success/failure indication.
        """
        pass
    
    @abstractmethod
    async def verify_state(
        self,
        expected_state: Dict[str, Any]
    ) -> bool:
        """
        Verify domain reached expected state.
        
        Called after action execution to verify success.
        """
        pass
    
    async def publish_event(
        self,
        event_type: str,
        resource: str,
        payload: Dict[str, Any]
    ):
        """Publish domain event to trigger mesh"""
        await trigger_mesh.publish(TriggerEvent(
            event_type=f"{self.domain_id}.{event_type}",
            source=self.domain_id,
            actor=self.domain_id,
            resource=resource,
            payload=payload,
            timestamp=datetime.utcnow()
        ))
    
    async def log_action(
        self,
        action: str,
        resource: str,
        payload: Dict,
        result: str
    ):
        """Log domain action to immutable ledger"""
        await immutable_log.append(
            actor=self.domain_id,
            action=action,
            resource=resource,
            subsystem=self.domain_id,
            payload=payload,
            result=result
        )
    
    async def request_memory(
        self,
        memory_type: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        include_cross_domain: bool = False
    ) -> Dict[str, Any]:
        """
        Request memory through agentic memory broker.
        
        Domains NEVER access raw storage - always through the broker
        which applies governance, context, and policy-aware filtering.
        
        Args:
            memory_type: "episodic", "semantic", "procedural", "working"
            query: Natural language query or search terms
            context: Additional context for ranking
            limit: Max results to return
            include_cross_domain: Request cross-domain memories (requires approval)
        
        Returns:
            Response with filtered/ranked memories and explanation
        """
        from .agentic_memory import agentic_memory, MemoryRequest, MemoryType
        
        request = MemoryRequest(
            request_id=f"{self.domain_id}_{int(datetime.utcnow().timestamp())}",
            requesting_domain=self.domain_id,
            requesting_actor=self.domain_id,
            memory_type=MemoryType(memory_type),
            query=query,
            context=context or {},
            limit=limit,
            include_cross_domain=include_cross_domain
        )
        
        response = await agentic_memory.request_memory(request)
        
        return {
            "memories": [
                {
                    "id": m.entry_id,
                    "content": m.content,
                    "tags": m.tags,
                    "timestamp": m.timestamp.isoformat(),
                    "relevance": m.relevance_score,
                    "domain": m.domain
                }
                for m in response.memories
            ],
            "total_found": response.total_count,
            "filtered": response.filtered_count,
            "access_level": response.access_level.value,
            "explanation": response.explanation,
            "policies_applied": response.applied_policies
        }
    
    async def store_memory(
        self,
        memory_type: str,
        content: Dict[str, Any],
        tags: List[str]
    ) -> str:
        """
        Store memory through agentic memory broker.
        
        All storage goes through the broker for governance and logging.
        """
        from .agentic_memory import agentic_memory, MemoryType
        
        return await agentic_memory.store_memory(
            domain=self.domain_id,
            memory_type=MemoryType(memory_type),
            content=content,
            tags=tags,
            actor=self.domain_id
        )


class AgentCore:
    """
    Agent Core - Unified agentic infrastructure
    
    Provides sensing, trust, planning, execution, and learning
    services that all domains share. Domains register with the
    core and receive autonomous capabilities.
    """
    
    def __init__(self):
        self.domains: Dict[str, DomainAdapter] = {}
        self.domain_shards: Dict[str, str] = {}
        self.lifecycle_stages = [
            "sensing",      # Detect signals
            "enrichment",   # Add context & intent
            "diagnosis",    # Understand root cause
            "planning",     # Generate recovery plan
            "trust_check",  # Validate against policies
            "approval",     # Get human approval if needed
            "execution",    # Execute the plan
            "verification", # Verify expected outcome
            "learning"      # Record outcome, improve
        ]
    
    async def register_domain(self, adapter: DomainAdapter):
        """Register a domain adapter with the agent core"""
        
        domain_id = adapter.domain_id
        self.domains[domain_id] = adapter
        
        print(f"  -> Registering domain: {domain_id}")
        
        # Register domain telemetry
        telemetry = await adapter.register_telemetry()
        print(f"     Telemetry schemas: {len(telemetry)}")
        
        # Register health nodes
        nodes = await adapter.register_health_nodes()
        print(f"     Health nodes: {len(nodes)}")
        for node in nodes:
            await self._register_health_node(node, domain_id)
        
        # Register playbooks
        playbooks = await adapter.register_playbooks()
        print(f"     Playbooks: {len(playbooks)}")
        for playbook in playbooks:
            await self._register_playbook(playbook, domain_id)
        
        # Subscribe to domain events
        trigger_mesh.subscribe(f"{domain_id}.*", self._handle_domain_event)
        
        # Assign shard (if multi-agent sharding enabled)
        await self._assign_shard(adapter)
        
        await immutable_log.append(
            actor="agent_core",
            action="domain_registered",
            resource=domain_id,
            subsystem="agent_core",
            payload={
                "domain_type": adapter.domain_type.value,
                "telemetry_count": len(telemetry),
                "nodes_count": len(nodes),
                "playbooks_count": len(playbooks)
            },
            result="registered"
        )
        
        print(f"  [OK] Domain {domain_id} integrated with agent core")
    
    async def _register_health_node(self, node: DomainHealthNode, domain_id: str):
        """Register health node in unified graph"""
        from .agentic_spine import agentic_spine, HealthNode
        
        health_node = HealthNode(
            node_id=node.node_id,
            node_type=node.node_type,
            name=node.name,
            status="healthy",
            kpis={},
            dependencies=node.dependencies,
            dependents=[],
            blast_radius=0,
            priority=0,
            metadata={**node.metadata, "domain": domain_id, "risk_tier": node.risk_tier}
        )
        
        await agentic_spine.health_graph.register_node(health_node)
    
    async def _register_playbook(self, domain_playbook: DomainPlaybook, domain_id: str):
        """Register playbook with autonomous planner"""
        from .agentic_spine import agentic_spine, Playbook, RiskLevel
        
        risk_map = {
            "low": RiskLevel.LOW,
            "moderate": RiskLevel.MODERATE,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL
        }
        
        playbook = Playbook(
            playbook_id=f"{domain_id}.{domain_playbook.playbook_id}",
            name=domain_playbook.name,
            description=domain_playbook.description,
            preconditions=domain_playbook.preconditions,
            steps=domain_playbook.steps,
            verifications=domain_playbook.verifications,
            rollback_steps=domain_playbook.rollback_steps,
            risk_level=risk_map.get(domain_playbook.risk_level, RiskLevel.MODERATE),
            requires_approval=domain_playbook.requires_approval,
            success_rate=domain_playbook.success_rate_baseline,
            execution_count=0,
            metadata={"domain": domain_id, "estimated_duration": domain_playbook.estimated_duration_seconds}
        )
        
        await agentic_spine.planner.register_playbook(playbook)
    
    async def _assign_shard(self, adapter: DomainAdapter):
        """Assign domain to a shard for distributed processing"""
        from .multi_agent_shards import shard_coordinator, ShardType, ShardScope, CapabilityType
        from .agentic_config import agentic_config
        
        if not agentic_config.is_enabled("sharding"):
            return
        
        # Spawn domain-specific shard
        shard = await shard_coordinator.spawn_shard(
            shard_type=ShardType.DOMAIN,
            scope=ShardScope(domain=adapter.domain_id),
            capabilities=await self._infer_capabilities(adapter)
        )
        
        adapter.shard_id = shard.shard_id
        self.domain_shards[adapter.domain_id] = shard.shard_id
    
    async def _infer_capabilities(self, adapter: DomainAdapter) -> List:
        """Infer shard capabilities from domain type"""
        from .multi_agent_shards import CapabilityType
        
        # Default capabilities based on domain
        capability_map = {
            DomainType.CORE: [CapabilityType.SELF_HEALING, CapabilityType.CAPACITY_PLANNER],
            DomainType.SECURITY: [CapabilityType.SECURITY_SENTINEL],
            DomainType.KNOWLEDGE: [CapabilityType.INGESTION_LEAD, CapabilityType.MEMORY_STEWARD],
            DomainType.ML: [CapabilityType.CAPACITY_PLANNER],
            DomainType.PARLIAMENT: [CapabilityType.COMPLIANCE_AUDITOR],
            DomainType.FEDERATION: [CapabilityType.COST_OPTIMIZER],
        }
        
        return capability_map.get(adapter.domain_type, [CapabilityType.SELF_HEALING])
    
    async def _handle_domain_event(self, event: TriggerEvent):
        """Handle events from registered domains"""
        
        domain_id = event.source
        
        if domain_id not in self.domains:
            return
        
        # Domain events flow through standard agentic pipeline
        # (Already handled by agentic_spine which subscribes to "*")
    
    async def get_domain_status(self) -> Dict[str, Any]:
        """Get status of all registered domains"""
        
        status = {}
        
        for domain_id, adapter in self.domains.items():
            metrics = await adapter.collect_metrics()
            
            status[domain_id] = {
                "domain_type": adapter.domain_type.value,
                "enabled": adapter.enabled,
                "shard_id": adapter.shard_id,
                "health_score": metrics.health_score,
                "active_tasks": metrics.active_tasks,
                "success_rate_24h": (
                    metrics.completed_tasks_24h / 
                    (metrics.completed_tasks_24h + metrics.failed_tasks_24h)
                ) if (metrics.completed_tasks_24h + metrics.failed_tasks_24h) > 0 else 1.0,
                "error_rate": metrics.error_rate
            }
        
        return status


agent_core = AgentCore()
