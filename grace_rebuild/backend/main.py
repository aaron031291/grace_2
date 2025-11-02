from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .models import Base, engine
from .routes import chat, auth_routes, metrics, reflections, tasks, history, causal, goals, knowledge, evaluation, summaries, sandbox, executor, governance, hunter, health_routes, issues, memory_api, immutable_api, meta_api, websocket_routes, plugin_routes, ingest, trust_api, ml_api, execution, temporal_api, causal_graph_api
from .reflection import reflection_service
from .auth import get_current_user
from .verification_integration import verification_integration

app = FastAPI(title="Grace API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .task_executor import task_executor
from .self_healing import health_monitor
from .trigger_mesh import trigger_mesh, setup_subscriptions
from .meta_loop import meta_loop_engine
from .websocket_manager import setup_ws_subscriptions
from .trusted_sources import trust_manager
from .auto_retrain import auto_retrain_engine

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database initialized")
    print("✓ Grace API server starting...")
    print("  Visit: http://localhost:8000/health")
    print("  Docs: http://localhost:8000/docs")
    
    await trigger_mesh.start()
    await setup_subscriptions()
    await setup_ws_subscriptions()
    await trust_manager.initialize_defaults()
    await reflection_service.start()
    await task_executor.start_workers()
    await health_monitor.start()
    await meta_loop_engine.start()
    await auto_retrain_engine.start()

@app.on_event("shutdown")
async def on_shutdown():
    await reflection_service.stop()
    await task_executor.stop_workers()
    await health_monitor.stop()
    await trigger_mesh.stop()
    await meta_loop_engine.stop()
    await auto_retrain_engine.stop()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Grace API is running"}

@app.get("/api/verification/audit")
async def verification_audit(
    limit: int = 100,
    actor: str = None,
    action_type: str = None,
    hours_back: int = 24,
    current_user: str = Depends(get_current_user)
):
    """Get verification audit log"""
    audit_log = await verification_integration.get_verification_audit_log(
        limit=limit,
        actor=actor,
        action_type=action_type,
        hours_back=hours_back
    )
    return {"audit_log": audit_log, "count": len(audit_log)}

@app.get("/api/verification/stats")
async def verification_stats(
    hours_back: int = 24,
    current_user: str = Depends(get_current_user)
):
    """Get verification statistics"""
    stats = await verification_integration.get_verification_stats(hours_back=hours_back)
    return stats

@app.get("/api/verification/failed")
async def verification_failed(
    limit: int = 50,
    hours_back: int = 24,
    current_user: str = Depends(get_current_user)
):
    """Get failed verifications"""
    failures = await verification_integration.get_failed_verifications(
        limit=limit,
        hours_back=hours_back
    )
    return {"failed_verifications": failures, "count": len(failures)}

app.include_router(auth_routes.router)
app.include_router(chat.router)
app.include_router(metrics.router)
app.include_router(reflections.router)
app.include_router(tasks.router)
app.include_router(history.router)
app.include_router(causal.router)
app.include_router(goals.router)
app.include_router(knowledge.router)
app.include_router(evaluation.router)
app.include_router(summaries.router)
app.include_router(sandbox.router)
app.include_router(executor.router)
app.include_router(governance.router)
app.include_router(hunter.router)
app.include_router(health_routes.router)
app.include_router(issues.router)
app.include_router(memory_api.router)
app.include_router(immutable_api.router)
app.include_router(meta_api.router)
app.include_router(websocket_routes.router)
app.include_router(plugin_routes.router)
app.include_router(ingest.router)
app.include_router(trust_api.router)
app.include_router(ml_api.router)
app.include_router(execution.router)
app.include_router(temporal_api.router)
app.include_router(causal_graph_api.router)

# Grace IDE WebSocket
from grace_ide.api.websocket import router as ide_ws_router
app.include_router(ide_ws_router)
