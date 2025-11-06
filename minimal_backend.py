"""
Minimal Grace Backend
Just enough to get frontend + CLI connected
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("grace.minimal")

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
    logger.info("[OK] Cognition router loaded")
except Exception as e:
    logger.warning(f"[WARN] Could not load cognition router: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Minimal backend running"}

@app.get("/api/status")
def quick_status():
    """Quick status endpoint"""
    try:
        from backend.cognition_metrics import get_metrics_engine
    except Exception as e:
        logger.exception("Failed to import metrics engine")
        raise HTTPException(status_code=502, detail="Metrics engine unavailable")

    try:
        engine = get_metrics_engine()
        return engine.get_status()
    except Exception:
        logger.exception("Error while generating quick status")
        raise HTTPException(status_code=502, detail="Failed to compute status")

@app.get("/api/metrics")
def metrics():
    """Metrics summary"""
    try:
        from backend.metrics_service import get_metrics_collector
    except Exception:
        logger.exception("Failed to import metrics collector")
        raise HTTPException(status_code=502, detail="Metrics collector unavailable")

    try:
        collector = get_metrics_collector()
        return {
            "total_metrics": sum(len(q) for q in collector.metrics.values()),
            "domains": list(collector.aggregates.keys()),
            "status": collector.get_all_domains_status(),
        }
    except Exception:
        logger.exception("Error while collecting metrics summary")
        raise HTTPException(status_code=502, detail="Failed to collect metrics summary")

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
            "docs": "/docs",
        },
    }

if __name__ == "__main__":
    import uvicorn
    banner = (
        "\n" + "=" * 60 +
        "\nStarting Grace Minimal Backend\n" +
        "=" * 60 +
        f"\nAPI: http://localhost:8000\nDocs: http://localhost:8000/docs\nPress CTRL+C to stop\n" +
        "=" * 60 + "\n"
    )
    print(banner)
    logger.info("Grace Minimal Backend starting on 127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
