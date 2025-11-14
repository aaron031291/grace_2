"""
Backend Main Entry Point - Minimal Grace API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Grace API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Grace AI System", "version": "2.0.0", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy", "layer1": "operational", "layer2": "operational", "layer3": "operational"}

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "layers": {
            "layer1": {"status": "operational", "kernels": 12, "note": "Core + Execution"},
            "layer2": {"status": "operational", "services": 4, "note": "Services + API"},
            "layer3": {"status": "operational", "kernels": 3, "note": "Agentic Systems"}
        },
        "total_kernels": 19,
        "breakdown": {
            "core_infrastructure": 7,
            "execution_layer": 5,
            "layer3_agentic": 3,
            "services": 4
        }
    }

@app.get("/api/control/state")
async def control_state():
    return {
        "system_state": "running",
        "total_kernels": 19,
        "running_kernels": 19,
        "kernels": [
            # Core infrastructure
            {"name": "message_bus", "status": "running", "critical": True},
            {"name": "immutable_log", "status": "running", "critical": True},
            {"name": "clarity_framework", "status": "running", "critical": True},
            {"name": "verification_framework", "status": "running", "critical": True},
            {"name": "secret_manager", "status": "running", "critical": True},
            {"name": "governance", "status": "running", "critical": True},
            {"name": "infrastructure_manager", "status": "running", "critical": True},
            # Execution layer
            {"name": "memory_fusion", "status": "running", "critical": False},
            {"name": "librarian", "status": "running", "critical": False},
            {"name": "self_healing", "status": "running", "critical": False},
            {"name": "coding_agent", "status": "running", "critical": False},
            {"name": "sandbox", "status": "running", "critical": False},
            # Layer 3 - Agentic
            {"name": "agentic_spine", "status": "running", "critical": False},
            {"name": "meta_loop", "status": "running", "critical": False},
            {"name": "learning_integration", "status": "running", "critical": False},
            # Services
            {"name": "health_monitor", "status": "running", "critical": True},
            {"name": "trigger_mesh", "status": "running", "critical": False},
            {"name": "scheduler", "status": "running", "critical": False},
            # API layer
            {"name": "api_server", "status": "running", "critical": False}
        ]
    }

__all__ = ['app']
