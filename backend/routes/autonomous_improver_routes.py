"""
Autonomous Improver API Routes
Monitor and control proactive improvement system
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any
import asyncio
from ..autonomous_improver import autonomous_improver
from ..schemas import SuccessResponse

router = APIRouter(prefix="/api/autonomous", tags=["autonomous"])

class AutonmousStatus(BaseModel):
    """Autonomous improver status"""
    running: bool = Field(description="Whether improver is active")
    scan_interval_seconds: int = Field(description="Scan interval")
    fixes_applied: int = Field(description="Total fixes applied")
    errors_found: int = Field(description="Total errors found")
    mode: str = Field(description="Operating mode")

class ConfigUpdate(BaseModel):
    scan_interval: int = Field(ge=60, le=3600, description="Scan interval in seconds")

@router.get("/improver/status", response_model=AutonmousStatus)
async def get_improver_status():
    """Get autonomous improver status"""
    return autonomous_improver.get_status()

@router.post("/improver/trigger", response_model=SuccessResponse)
async def trigger_improvement_scan():
    """Manually trigger an improvement scan"""
    asyncio.create_task(autonomous_improver._run_improvement_cycle())
    return SuccessResponse(
        success=True,
        message="Improvement scan triggered",
        data={"status": "scanning"}
    )

@router.patch("/improver/config", response_model=SuccessResponse)
async def update_improver_config(config: ConfigUpdate):
    """Update improver configuration"""
    autonomous_improver.scan_interval = config.scan_interval
    return SuccessResponse(
        success=True,
        message=f"Scan interval updated to {config.scan_interval}s",
        data={"scan_interval": config.scan_interval}
    )

@router.post("/improver/start", response_model=SuccessResponse)
async def start_improver():
    """Start autonomous improver"""
    await autonomous_improver.start()
    return SuccessResponse(
        success=True,
        message="Autonomous improver started"
    )

@router.post("/improver/stop", response_model=SuccessResponse)
async def stop_improver():
    """Stop autonomous improver"""
    await autonomous_improver.stop()
    return SuccessResponse(
        success=True,
        message="Autonomous improver stopped"
    )
