"""
Hardware Awareness API
Grace understands her capacity and optimizes resource usage
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import platform

from ..hardware_awareness import hardware_profile

router = APIRouter(prefix="/api/hardware", tags=["hardware"])

class PowerModeRequest(BaseModel):
    mode: str = Field(description="idle, balanced, performance, maximum")
    reason: str = Field(description="Why changing power mode")

class TaskAllocationRequest(BaseModel):
    task_type: str = Field(description="ml_training, inference, code_generation, data_processing, idle")
    estimated_duration_seconds: Optional[int] = None

@router.get("/capacity")
async def get_hardware_capacity():
    """
    Get Grace's current hardware capacity and utilization
    
    Shows:
    - CPU usage and power
    - Memory usage
    - GPU availability and power
    - Storage usage
    - Power consumption estimates
    - Cooling status
    """
    return hardware_profile.get_current_capacity()

@router.get("/specs")
async def get_hardware_specs():
    """
    Get Grace's known hardware specifications
    
    Returns full PC build details:
    - AMD Ryzen 9 9950X3D (16 cores, 32 threads)
    - RTX 5090 32GB
    - 64GB DDR5 6000MHz
    - 4TB Samsung 990 PRO NVMe
    - Custom water cooling
    - 1000W PSU
    """
    return {
        "hardware": hardware_profile.KNOWN_SPECS,
        "detected": {
            "gpu_available": hardware_profile.gpu_available,
            "gpu_count": getattr(hardware_profile, 'gpu_count', 0),
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
    }

@router.post("/power-mode")
async def set_power_mode(request: PowerModeRequest):
    """
    Set power/performance mode
    
    Modes:
    - idle: Minimal power, background tasks
    - balanced: Normal operation
    - performance: High CPU/GPU for demanding tasks
    - maximum: Full power for ML training, benchmarks
    """
    hardware_profile.set_power_mode(request.mode, request.reason)
    return {
        "success": True,
        "mode": request.mode,
        "message": f"Power mode set to {request.mode}"
    }

@router.post("/allocate")
async def allocate_resources(request: TaskAllocationRequest):
    """
    Intelligently allocate resources for a task
    
    Grace decides how much CPU/GPU/RAM to use based on task type.
    Optimizes power consumption - only uses GPU when needed.
    """
    allocation = await hardware_profile.allocate_for_task(request.task_type)
    return allocation

@router.post("/benchmark")
async def benchmark_if_needed(task_type: str):
    """
    Run benchmark ONLY when needed for high-power tasks
    
    Skips benchmarking for light tasks to save power.
    Only benchmarks when ML/inference tasks require GPU validation.
    """
    result = await hardware_profile.benchmark_when_needed(task_type)
    
    if result:
        return {
            "benchmarked": True,
            "results": result,
            "message": "Benchmark completed for high-power task"
        }
    else:
        return {
            "benchmarked": False,
            "message": f"Skipped benchmark for {task_type} (light task, power saved)"
        }

@router.get("/recommendations")
async def get_hardware_recommendations():
    """
    Get optimization recommendations based on current usage
    
    Grace analyzes current load and suggests optimizations.
    """
    recommendations = hardware_profile.get_recommendations()
    capacity = hardware_profile.get_current_capacity()
    
    return {
        "recommendations": recommendations,
        "current_capacity": capacity,
        "power_mode": hardware_profile.power_mode,
        "workload": hardware_profile.current_workload
    }

@router.get("/status")
async def hardware_status():
    """Quick hardware status"""
    capacity = hardware_profile.get_current_capacity()
    
    return {
        "status": "operational",
        "power_mode": hardware_profile.power_mode,
        "cpu_usage": capacity["cpu"]["usage_percent"],
        "memory_usage": capacity["memory"]["percent"],
        "gpu_active": capacity["gpu"]["active"],
        "power_consumption_watts": capacity["power"]["current_watts_estimated"],
        "power_headroom_watts": capacity["power"]["headroom_watts"]
    }
