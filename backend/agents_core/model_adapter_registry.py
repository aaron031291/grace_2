"""
Model Adapter Registry - Unified Model Contract System
Pillar 1: Model adapters + verification

Manages the 15 open-source models with uniform adapters.
Each adapter registers capabilities, contracts, and health checks.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """Model capability types"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    VISION = "vision"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


@dataclass
class ModelContract:
    """Contract defining model's expected behavior"""
    model_name: str
    capabilities: List[ModelCapability]
    
    # Input/Output specs
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
    # Performance requirements
    max_latency_ms: int = 5000
    min_accuracy: float = 0.7
    max_tokens: int = 4096
    
    # Health requirements
    health_check_interval: int = 300  # seconds
    max_consecutive_failures: int = 3
    
    # Contract versioning
    contract_version: str = "1.0"
    contract_hash: str = field(init=False)
    
    def __post_init__(self):
        # Generate contract hash
        contract_data = f"{self.model_name}:{self.contract_version}:{self.capabilities}"
        self.contract_hash = hashlib.sha256(contract_data.encode()).hexdigest()[:16]


@dataclass
class ModelHealth:
    """Model health metrics"""
    model_name: str
    is_healthy: bool
    last_check: str
    
    # Metrics
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    
    # Governance
    trust_score: float = 1.0
    governance_approved: bool = True


@dataclass
class ModelAdapter:
    """Unified adapter for an OSS model"""
    adapter_id: str
    model_name: str
    model_type: str  # llama, mistral, phi, qwen, etc.
    contract: ModelContract
    
    # Configuration
    provider: str  # ollama, llamacpp, transformers
    model_path: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    # State
    is_loaded: bool = False
    health: Optional[ModelHealth] = None
    
    # Registration
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    registered_by: str = "system"


class ModelAdapterRegistry:
    """
    Registry for all model adapters
    
    Provides:
    - Uniform adapter interface for 15 OSS models
    - Contract enforcement
    - Health monitoring
    - Governance integration
    """
    
    def __init__(self):
        self.adapters: Dict[str, ModelAdapter] = {}
        self.contracts: Dict[str, ModelContract] = {}
        self.health_checks: Dict[str, ModelHealth] = {}
        
        # Monitoring
        self.health_check_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the registry"""
        logger.info("[MODEL REGISTRY] Starting model adapter registry")
        
        # Register default adapters for Grace's 15 models
        await self._register_default_adapters()
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"[MODEL REGISTRY] {len(self.adapters)} adapters registered")
    
    async def _register_default_adapters(self):
        """Register adapters for Grace's 15 OSS models"""
        
        # 1. Llama 3.2 3B (Primary)
        await self.register_adapter(
            adapter_id="llama_3.2_3b",
            model_name="llama3.2:3b",
            model_type="llama",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
            input_schema={"prompt": "str", "max_tokens": "int"},
            output_schema={"text": "str", "tokens_used": "int"},
            provider="ollama",
            max_latency_ms=3000
        )
        
        # 2. Mistral 7B (Balanced)
        await self.register_adapter(
            adapter_id="mistral_7b",
            model_name="mistral:7b",
            model_type="mistral",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
            input_schema={"prompt": "str", "max_tokens": "int"},
            output_schema={"text": "str"},
            provider="ollama",
            max_latency_ms=4000
        )
        
        # 3. Phi-3 Medium (Efficiency)
        await self.register_adapter(
            adapter_id="phi3_medium",
            model_name="phi3:medium",
            model_type="phi",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
            input_schema={"prompt": "str"},
            output_schema={"text": "str"},
            provider="ollama",
            max_latency_ms=2000
        )
        
        # 4. Qwen 2.5 Coder (Code Specialist)
        await self.register_adapter(
            adapter_id="qwen_coder",
            model_name="qwen2.5-coder:7b",
            model_type="qwen",
            capabilities=[ModelCapability.CODE_GENERATION],
            input_schema={"prompt": "str", "language": "str"},
            output_schema={"code": "str"},
            provider="ollama",
            max_latency_ms=3000
        )
        
        # 5. Gemma 2 9B (Google)
        await self.register_adapter(
            adapter_id="gemma2_9b",
            model_name="gemma2:9b",
            model_type="gemma",
            capabilities=[ModelCapability.TEXT_GENERATION],
            input_schema={"prompt": "str"},
            output_schema={"text": "str"},
            provider="ollama",
            max_latency_ms=4000
        )
        
        # 6-15: Additional models (stubs for now, add as needed)
        for i, model_info in enumerate([
            ("codellama:7b", "codellama", [ModelCapability.CODE_GENERATION]),
            ("deepseek-coder:6.7b", "deepseek", [ModelCapability.CODE_GENERATION]),
            ("starcoder2:7b", "starcoder", [ModelCapability.CODE_GENERATION]),
            ("solar:10.7b", "solar", [ModelCapability.TEXT_GENERATION]),
            ("yi:6b", "yi", [ModelCapability.TEXT_GENERATION]),
            ("orca-mini:3b", "orca", [ModelCapability.TEXT_GENERATION]),
            ("vicuna:7b", "vicuna", [ModelCapability.TEXT_GENERATION]),
            ("openhermes:7b", "openhermes", [ModelCapability.TEXT_GENERATION]),
            ("wizardcoder:7b", "wizardcoder", [ModelCapability.CODE_GENERATION]),
            ("nous-hermes2:10.7b", "nous", [ModelCapability.TEXT_GENERATION])
        ], start=6):
            model_name, model_type, capabilities = model_info
            await self.register_adapter(
                adapter_id=f"model_{i}_{model_type}",
                model_name=model_name,
                model_type=model_type,
                capabilities=capabilities,
                input_schema={"prompt": "str"},
                output_schema={"text": "str"},
                provider="ollama"
            )
    
    async def register_adapter(
        self,
        adapter_id: str,
        model_name: str,
        model_type: str,
        capabilities: List[ModelCapability],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        provider: str = "ollama",
        max_latency_ms: int = 5000,
        **kwargs
    ):
        """Register a model adapter"""
        
        # Create contract
        contract = ModelContract(
            model_name=model_name,
            capabilities=capabilities,
            input_schema=input_schema,
            output_schema=output_schema,
            max_latency_ms=max_latency_ms
        )
        
        # Create adapter
        adapter = ModelAdapter(
            adapter_id=adapter_id,
            model_name=model_name,
            model_type=model_type,
            contract=contract,
            provider=provider,
            config=kwargs
        )
        
        # Initialize health
        adapter.health = ModelHealth(
            model_name=model_name,
            is_healthy=True,
            last_check=datetime.utcnow().isoformat()
        )
        
        # Register
        self.adapters[adapter_id] = adapter
        self.contracts[adapter_id] = contract
        self.health_checks[adapter_id] = adapter.health
        
        logger.info(f"[MODEL REGISTRY] Registered {adapter_id} ({model_name})")
    
    async def verify_contract(self, adapter_id: str, actual_output: Any) -> Dict[str, Any]:
        """
        Verify that model output matches contract
        
        Returns verification result with pass/fail + details
        """
        
        adapter = self.adapters.get(adapter_id)
        if not adapter:
            return {"verified": False, "error": "Adapter not found"}
        
        contract = adapter.contract
        
        # Basic schema validation
        output_schema = contract.output_schema
        
        if isinstance(actual_output, dict):
            missing_keys = set(output_schema.keys()) - set(actual_output.keys())
            if missing_keys:
                return {
                    "verified": False,
                    "contract_hash": contract.contract_hash,
                    "error": f"Missing output keys: {missing_keys}"
                }
        
        return {
            "verified": True,
            "contract_hash": contract.contract_hash,
            "adapter_id": adapter_id
        }
    
    async def health_check(self, adapter_id: str) -> ModelHealth:
        """Run health check on a model adapter"""
        
        adapter = self.adapters.get(adapter_id)
        if not adapter or not adapter.health:
            raise ValueError(f"Adapter {adapter_id} not found")
        
        health = adapter.health
        
        try:
            # Try a simple inference
            # In production, this would call the actual model
            test_input = {"prompt": "test"}
            
            # Simulate check (replace with actual model call)
            import random
            is_healthy = random.random() > 0.1  # 90% success rate
            
            if is_healthy:
                health.is_healthy = True
                health.consecutive_failures = 0
                health.successful_requests += 1
            else:
                health.consecutive_failures += 1
                if health.consecutive_failures >= adapter.contract.max_consecutive_failures:
                    health.is_healthy = False
            
            health.total_requests += 1
            health.error_rate = 1.0 - (health.successful_requests / health.total_requests)
            health.last_check = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"[MODEL REGISTRY] Health check failed for {adapter_id}: {e}")
            health.is_healthy = False
            health.consecutive_failures += 1
        
        return health
    
    async def _health_check_loop(self):
        """Background health check loop"""
        
        while True:
            try:
                for adapter_id in self.adapters.keys():
                    await self.health_check(adapter_id)
                
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"[MODEL REGISTRY] Health check loop error: {e}")
                await asyncio.sleep(60)
    
    def get_adapters_by_capability(self, capability: ModelCapability) -> List[ModelAdapter]:
        """Get all adapters with a specific capability"""
        
        return [
            adapter for adapter in self.adapters.values()
            if capability in adapter.contract.capabilities
        ]
    
    def get_healthy_adapters(self) -> List[ModelAdapter]:
        """Get all healthy adapters"""
        
        return [
            adapter for adapter in self.adapters.values()
            if adapter.health and adapter.health.is_healthy
        ]
    
    def get_adapter_info(self, adapter_id: str) -> Dict[str, Any]:
        """Get full adapter information"""
        
        adapter = self.adapters.get(adapter_id)
        if not adapter:
            return {}
        
        return {
            "adapter": asdict(adapter),
            "contract": asdict(adapter.contract),
            "health": asdict(adapter.health) if adapter.health else None
        }
    
    def export_registry(self) -> Dict[str, Any]:
        """Export full registry state"""
        
        return {
            "adapters": {aid: asdict(adapter) for aid, adapter in self.adapters.items()},
            "total_adapters": len(self.adapters),
            "healthy_adapters": len(self.get_healthy_adapters()),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global registry instance
_model_registry: Optional[ModelAdapterRegistry] = None


async def get_model_registry() -> ModelAdapterRegistry:
    """Get or create the global model registry"""
    global _model_registry
    
    if _model_registry is None:
        _model_registry = ModelAdapterRegistry()
        await _model_registry.start()
    
    return _model_registry
