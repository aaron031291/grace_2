#!/usr/bin/env python3
"""
Minimal Grace Backend - Quick Start Entry Point

This is the minimal backend referenced in README.md for quick development.
Provides core API endpoints without all the advanced features.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Grace Minimal Backend",
    description="Minimal Grace backend for development",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "message": "Grace minimal backend is running"}

# Status endpoint
@app.get("/api/status")
async def get_status():
    """Quick cognition status"""
    return {
        "status": "operational",
        "version": "minimal",
        "message": "Grace minimal backend active"
    }

# Metrics endpoint
@app.get("/api/metrics")
async def get_metrics():
    """Basic metrics summary"""
    return {
        "overall_health": 85.0,
        "overall_trust": 80.0,
        "overall_confidence": 75.0,
        "domains": {
            "core": 90.0,
            "cognition": 85.0
        }
    }

# Cognition status endpoint
@app.get("/api/cognition/status")
async def get_cognition_status():
    """Detailed domain metrics"""
    return {
        "total_intents": 0,
        "completed": 0,
        "failed": 0,
        "success_rate": 0.0,
        "capabilities_registered": 6,
        "status": "operational",
        "domains": {
            "core": {"health": 90.0, "trust": 85.0, "confidence": 80.0},
            "cognition": {"health": 85.0, "trust": 80.0, "confidence": 75.0}
        }
    }

# Readiness report
@app.get("/api/cognition/readiness")
async def get_readiness():
    """SaaS readiness report"""
    return {
        "ready": False,
        "overall_health": 75.6,
        "overall_trust": 71.8,
        "overall_confidence": 69.6,
        "saas_ready": False,
        "next_steps": [
            "Complete backend integration",
            "Fix frontend connections",
            "Add WebSocket support",
            "Resolve encoding issues"
        ]
    }

# Benchmark details
@app.get("/api/cognition/benchmark/{metric}")
async def get_benchmark(metric: str):
    """Benchmark details"""
    benchmarks = {
        "overall_health": {
            "name": "Overall Health",
            "current": 75.6,
            "target": 90.0,
            "sustained": False,
            "trend": "improving"
        },
        "overall_trust": {
            "name": "Overall Trust",
            "current": 71.8,
            "target": 90.0,
            "sustained": False,
            "trend": "stable"
        }
    }

    if metric not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Benchmark {metric} not found")

    return benchmarks[metric]

# Domain update endpoint
@app.post("/api/cognition/domain/{domain_id}/update")
async def update_domain_kpi(domain_id: str, kpi_data: dict):
    """Update domain KPIs"""
    return {
        "domain": domain_id,
        "updated": True,
        "message": f"Domain {domain_id} KPIs updated"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    print("Starting Grace Minimal Backend...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")

    uvicorn.run(
        "minimal_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )