"""
Standalone Metrics Server
Runs independently of main backend to avoid circular import issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Create FastAPI app
app = FastAPI(
    title="Grace Metrics API",
    version="1.0.0",
    description="Real-time cognitive health monitoring for Grace"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
engine = create_async_engine("sqlite+aiosqlite:///metrics.db", echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Import metrics models
from .metrics_models import Base as MetricsBase

# Import routers
from .routers.cognition import router as cognition_router

# Register routes
app.include_router(cognition_router)

# Import services
from .benchmark_scheduler import start_benchmark_scheduler, stop_benchmark_scheduler

@app.on_event("startup")
async def startup():
    """Initialize database and start services"""
    async with engine.begin() as conn:
        await conn.run_sync(MetricsBase.metadata.create_all)
    
    print("=" * 80)
    print("[OK] Grace Metrics API Starting")
    print("=" * 80)
    print("[OK] Database initialized (metrics.db)")
    print("[OK] Cognition router registered")
    print(f"[OK] API ready at http://localhost:8001")
    print(f"[OK] Docs at http://localhost:8001/docs")
    print("=" * 80)
    
    # Start benchmark scheduler
    await start_benchmark_scheduler()
    print("[OK] Benchmark scheduler started (evaluates every hour)")
    print("=" * 80)

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await stop_benchmark_scheduler()
    print("Metrics API shutdown complete")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "service": "grace-metrics",
        "message": "Metrics API is running"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Grace Metrics API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "cognition_status": "/api/cognition/status",
            "cognition_readiness": "/api/cognition/readiness"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\nStarting Grace Metrics API...")
    print("Press CTRL+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
