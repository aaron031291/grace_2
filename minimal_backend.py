"""
Minimal Grace Backend
Just enough to get frontend + CLI connected
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(title="Grace Minimal API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load cognition router
try:
    from backend.routers.cognition import router as cognition_router
    app.include_router(cognition_router)
    print("[OK] Cognition router loaded")
except Exception as e:
    print(f"[WARN] Could not load cognition router: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Minimal backend running"}

@app.get("/api/status")
def quick_status():
    """Quick status endpoint"""
    try:
        from backend.cognition_metrics import get_metrics_engine
        engine = get_metrics_engine()
        return engine.get_status()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/metrics")
def metrics():
    """Metrics summary"""
    try:
        from backend.metrics_service import get_metrics_collector
        collector = get_metrics_collector()
        return {
            "total_metrics": sum(len(q) for q in collector.metrics.values()),
            "domains": list(collector.aggregates.keys()),
            "status": collector.get_all_domains_status()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {
        "service": "Grace Minimal Backend",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "metrics": "/api/metrics",
            "cognition": "/api/cognition/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("Starting Grace Minimal Backend")
    print("=" * 60)
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
