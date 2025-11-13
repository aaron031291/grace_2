"""
Unified Kernels API - Access all 11 domain kernels via FastAPI
Provides status, control, and monitoring for each kernel
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter()

# List of all domain kernels
KERNEL_NAMES = [
    'memory',
    'core', 
    'code',
    'governance',
    'verification',
    'intelligence',
    'infrastructure',
    'federation',
    'ml_dl',
    'self_healing',
    'librarian'
]

@router.get("/kernels")
async def get_all_kernels() -> Dict[str, Any]:
    """Get status of all domain kernels"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        kernels_status = []
        
        if hasattr(orchestrator, 'domain_kernels'):
            for name in KERNEL_NAMES:
                if name in orchestrator.domain_kernels:
                    kernel = orchestrator.domain_kernels[name]
                    status = {
                        "name": name,
                        "status": getattr(kernel, 'status', 'unknown'),
                        "active": hasattr(kernel, '_started') and kernel._started,
                        "metrics": kernel.get_status() if hasattr(kernel, 'get_status') else {}
                    }
                else:
                    status = {
                        "name": name,
                        "status": "not_loaded",
                        "active": False,
                        "metrics": {}
                    }
                kernels_status.append(status)
        
        return {
            "kernels": kernels_status,
            "total": len(KERNEL_NAMES),
            "active": sum(1 for k in kernels_status if k.get('active', False))
        }
    except Exception as e:
        return {
            "kernels": [{"name": name, "status": "unavailable", "active": False} for name in KERNEL_NAMES],
            "total": len(KERNEL_NAMES),
            "active": 0,
            "error": str(e)
        }

@router.get("/kernels/{kernel_name}")
async def get_kernel_status(kernel_name: str) -> Dict[str, Any]:
    """Get detailed status for a specific kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and kernel_name in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels[kernel_name]
            
            status = {
                "name": kernel_name,
                "status": getattr(kernel, 'status', 'unknown'),
                "active": hasattr(kernel, '_started') and kernel._started,
                "domain": getattr(kernel, 'domain', kernel_name),
                "kernel_id": getattr(kernel, 'kernel_id', f"{kernel_name}_001"),
                "metrics": kernel.get_status() if hasattr(kernel, 'get_status') else {},
                "capabilities": getattr(kernel, 'capabilities', [])
            }
            
            return status
        else:
            raise HTTPException(status_code=404, detail=f"Kernel '{kernel_name}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kernels/{kernel_name}/start")
async def start_kernel(kernel_name: str) -> Dict[str, Any]:
    """Start a specific kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and kernel_name in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels[kernel_name]
            
            if hasattr(kernel, 'start'):
                await kernel.start()
                return {"status": "started", "kernel": kernel_name}
            else:
                return {"status": "no_start_method", "kernel": kernel_name}
        else:
            raise HTTPException(status_code=404, detail=f"Kernel '{kernel_name}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kernels/{kernel_name}/stop")
async def stop_kernel(kernel_name: str) -> Dict[str, Any]:
    """Stop a specific kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and kernel_name in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels[kernel_name]
            
            if hasattr(kernel, 'stop'):
                await kernel.stop()
                return {"status": "stopped", "kernel": kernel_name}
            else:
                return {"status": "no_stop_method", "kernel": kernel_name}
        else:
            raise HTTPException(status_code=404, detail=f"Kernel '{kernel_name}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kernels/{kernel_name}/metrics")
async def get_kernel_metrics(kernel_name: str) -> Dict[str, Any]:
    """Get detailed metrics for a kernel"""
    try:
        from backend.unified_grace_orchestrator import orchestrator
        
        if hasattr(orchestrator, 'domain_kernels') and kernel_name in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels[kernel_name]
            
            metrics = kernel.get_status() if hasattr(kernel, 'get_status') else {}
            
            return {
                "kernel": kernel_name,
                "metrics": metrics
            }
        else:
            raise HTTPException(status_code=404, detail=f"Kernel '{kernel_name}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
