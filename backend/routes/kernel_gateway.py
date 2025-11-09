"""
Kernel Gateway - Single entry point for all domain kernels
Replaces direct API calls with intelligent kernel routing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from ..kernels.memory_kernel import memory_kernel
from ..kernels.core_kernel import core_kernel
from ..kernels.code_kernel import code_kernel
from ..kernels.governance_kernel import governance_kernel
from ..kernels.verification_kernel import verification_kernel
from ..kernels.intelligence_kernel import intelligence_kernel
from ..kernels.infrastructure_kernel import infrastructure_kernel
from ..kernels.federation_kernel import federation_kernel
from ..schemas import ExecutionTrace, DataProvenance

router = APIRouter(prefix="/kernel", tags=["Domain Kernels"])


class KernelRequest(BaseModel):
    """Request to a domain kernel"""
    intent: str = Field(description="Natural language intent")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    user_id: Optional[str] = None


class KernelResponseSchema(BaseModel):
    """Response from domain kernel"""
    kernel_name: str
    answer: str
    data: Optional[Dict[str, Any]] = None
    apis_called: List[str]
    kernels_consulted: List[str]
    execution_trace: ExecutionTrace
    data_provenance: List[DataProvenance]
    trust_score: float
    suggested_panels: List[Dict[str, Any]]
    confidence: float


# ============ Kernel Endpoints ============

@router.post("/memory", response_model=KernelResponseSchema)
async def memory_kernel_endpoint(request: KernelRequest):
    """
    Memory Kernel - Intelligent memory & knowledge agent
    
    Handles:
    - Memory queries
    - Knowledge search
    - Data ingestion
    - Context assembly
    
    Example:
    ```
    POST /kernel/memory
    {
        "intent": "Find all documents about sales pipelines",
        "context": {"domain": "sales"}
    }
    ```
    
    The kernel will:
    - Parse your intent
    - Decide which APIs to call (memory tree, knowledge query, etc.)
    - Execute intelligently
    - Return aggregated results
    """
    try:
        result = await memory_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Active Kernel Endpoints ============

@router.post("/core", response_model=KernelResponseSchema)
async def core_kernel_endpoint(request: KernelRequest):
    """
    Core Kernel - System operations & user interaction
    
    Manages 35 endpoints: chat, auth, tasks, health, metrics, history, 
    reflections, summaries, plugins, issues, speech, evaluation
    """
    try:
        result = await core_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code", response_model=KernelResponseSchema)
async def code_kernel_endpoint(request: KernelRequest):
    """
    Code Kernel - Code generation, execution, understanding
    
    Manages 30 endpoints: coding, sandbox, execution, commits, grace-architect
    """
    try:
        result = await code_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/governance", response_model=KernelResponseSchema)
async def governance_kernel_endpoint(request: KernelRequest):
    """
    Governance Kernel - Policy, safety, approvals
    
    Manages 40 endpoints: governance, constitutional, hunter, autonomy, parliament
    """
    try:
        result = await governance_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verification", response_model=KernelResponseSchema)
async def verification_kernel_endpoint(request: KernelRequest):
    """
    Verification Kernel - Contracts, snapshots, benchmarks
    
    Manages 25 endpoints: verification contracts, autonomous improver
    """
    try:
        result = await verification_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intelligence", response_model=KernelResponseSchema)
async def intelligence_kernel_endpoint(request: KernelRequest):
    """
    Intelligence Kernel - ML, predictions, causal reasoning
    
    Manages 45 endpoints: ML, temporal, causal, learning, meta, cognition
    """
    try:
        result = await intelligence_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/infrastructure", response_model=KernelResponseSchema)
async def infra_kernel_endpoint(request: KernelRequest):
    """
    Infrastructure Kernel - Monitoring, scheduling, workers
    
    Manages 35 endpoints: self-heal, scheduler, healing, concurrent, hardware, terminal, multimodal
    """
    try:
        result = await infrastructure_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/federation", response_model=KernelResponseSchema)
async def federation_kernel_endpoint(request: KernelRequest):
    """
    Federation Kernel - External integrations
    
    Manages 35 endpoints: web-learning, external-api, agentic, uploads, websockets, GitHub, Slack, AWS
    """
    try:
        result = await federation_kernel.process(request.intent, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
