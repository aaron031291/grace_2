"""
Base Domain Kernel
Foundation for all intelligent domain kernels
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

from ..grace_llm import get_grace_llm
from ..logging_utils import log_event
from ..schemas import ExecutionTrace, DataProvenance


@dataclass
class KernelIntent:
    """Parsed user intent for domain"""
    original_request: str
    understood_intent: str
    required_actions: List[str]
    data_needed: List[str]
    confidence: float


@dataclass
class KernelPlan:
    """Execution plan created by kernel"""
    plan_id: str
    actions: List[Dict[str, Any]]
    sequence: str  # "sequential", "parallel", "conditional"
    estimated_duration_ms: float
    risk_level: str  # "low", "medium", "high"


@dataclass
class KernelResponse:
    """Unified response from domain kernel"""
    kernel_name: str
    answer: str
    data: Optional[Dict[str, Any]]
    apis_called: List[str]
    kernels_consulted: List[str]
    execution_trace: ExecutionTrace
    data_provenance: List[DataProvenance]
    trust_score: float
    suggested_panels: List[Dict[str, Any]]
    confidence: float


class BaseDomainKernel(ABC):
    """
    Base class for intelligent domain kernels
    Each kernel is an AI agent managing its domain
    """
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.llm = None
        self.apis_called = []
        self.start_time = None
    
    async def initialize(self):
        """Initialize kernel (load models, etc.)"""
        self.llm = await get_grace_llm()
        await log_event(
            f"kernel_{self.domain_name}_initialized",
            "system",
            {"domain": self.domain_name}
        )
    
    async def process(self, intent: str, context: Dict[str, Any]) -> KernelResponse:
        """
        Main entry point - intelligent processing
        
        Flow:
        1. Parse intent (understand what user wants)
        2. Create plan (decide what APIs to call)
        3. Execute plan (call APIs, aggregate)
        4. Respond (unified intelligent response)
        """
        self.start_time = datetime.utcnow()
        self.apis_called = []
        
        # Step 1: Parse intent
        parsed = await self.parse_intent(intent, context)
        
        # Step 2: Create plan
        plan = await self.create_plan(parsed, context)
        
        # Step 3: Execute
        results = await self.execute_plan(plan, context)
        
        # Step 4: Aggregate & respond
        response = await self.aggregate_response(results, parsed, context)
        
        return response
    
    @abstractmethod
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """
        Parse user intent for this domain
        Uses LLM to understand what user wants
        """
        pass
    
    @abstractmethod
    async def create_plan(self, intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """
        Create execution plan
        Decides which APIs to call and in what order
        """
        pass
    
    @abstractmethod
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plan by calling underlying APIs
        Handles errors, retries, governance checks
        """
        pass
    
    @abstractmethod
    async def aggregate_response(
        self, 
        results: Dict[str, Any], 
        intent: KernelIntent, 
        context: Dict[str, Any]
    ) -> KernelResponse:
        """
        Intelligently aggregate results into unified response
        Uses LLM to create coherent answer
        """
        pass
    
    async def call_api(self, endpoint: str, method: str = "GET", data: Any = None) -> Any:
        """Helper to call underlying APIs"""
        self.apis_called.append(endpoint)
        # Implementation would use http client to call internal APIs
        pass
    
    async def consult_kernel(self, kernel_name: str, intent: str, context: Dict[str, Any]) -> Any:
        """Cross-kernel consultation"""
        # Allows kernels to collaborate
        pass
    
    def create_execution_trace(self, steps: List[Dict]) -> ExecutionTrace:
        """Create execution trace for response"""
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        
        return ExecutionTrace(
            request_id=f"{self.domain_name}_{datetime.utcnow().timestamp()}",
            total_duration_ms=duration,
            steps=steps,
            data_sources_used=[],
            agents_involved=[self.domain_name],
            governance_checks=0,
            cache_hits=0,
            database_queries=0
        )
