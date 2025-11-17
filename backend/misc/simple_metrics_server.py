"""
Simple Metrics Server - Minimal, no fancy output
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

app = FastAPI(title="Grace Metrics", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine("sqlite+aiosqlite:///metrics.db", echo=False)

from .metrics_models import Base as MetricsBase
from .routers.cognition import router as cognition_router

app.include_router(cognition_router)

from .benchmark_scheduler import start_benchmark_scheduler, stop_benchmark_scheduler

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(MetricsBase.metadata.create_all)
    print("Database ready")
    await start_benchmark_scheduler()
    print("Server ready on http://localhost:8001")

@app.on_event("shutdown")
async def shutdown():
    await stop_benchmark_scheduler()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "service": "Grace Metrics",
        "endpoints": ["/health", "/api/cognition/status", "/docs"]
    }
