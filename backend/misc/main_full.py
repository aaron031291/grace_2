from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base, engine
from .metrics_models import Base as MetricsBase
from .routes import chat, auth_routes, metrics, reflections, tasks, history, causal, goals, knowledge, evaluation, summaries, sandbox, executor, governance, hunter, health_routes, issues, memory_api, immutable_api, meta_api, websocket_routes, plugin_routes, ingest, trust_api, ml_api, execution, temporal_api, causal_graph_api, speech_api, parliament_api, coding_agent_api, constitutional_api
from .transcendence.dashboards.observatory_dashboard import router as dashboard_router
from .transcendence.business.api import router as business_api_router
from .reflection import reflection_service
from .auth import get_current_user
from .verification_integration import verification_integration
from .routers.cognition import router as cognition_router
from .routers.core_domain import router as core_domain_router
from .routers.transcendence_domain import router as transcendence_domain_router
from .routers.security_domain import router as security_domain_router
from .metrics_service import init_metrics_collector
from .request_id_middleware import RequestIDMiddleware
from .logging_utils import ensure_utf8_console
    # Core app DB
    # Ensure model modules are imported so Base.metadata is populated
    try:
        import importlib
        for _mod in (
            "backend.governance_models",
            "backend.knowledge_models",
            "backend.parliament_models",
        ):
            try:
                importlib.import_module(_mod)
            except Exception:
                # Optional modules may not import if they have side effects; ignore
                pass
    except Exception:
        pass

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database initialized")

    # Metrics DB (separate to avoid coupling)
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from .metrics_models import Base as MetricsBase
    app.state.metrics_engine = create_async_engine("sqlite+aiosqlite:///./databases/metrics.db", echo=False, future=True)
    app.state.metrics_sessionmaker = async_sessionmaker(app.state.metrics_engine, expire_on_commit=False)
    async with app.state.metrics_engine.begin() as mconn:
        await mconn.run_sync(MetricsBase.metadata.create_all)
    # Create a long-lived session for the collector
    app.state.metrics_session = await app.state.metrics_sessionmaker().__aenter__()

    # Initialize global metrics collector with persistence enabled
    init_metrics_collector(db_session=app.state.metrics_session)

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
    await start_benchmark_scheduler()
    print("✓ Benchmark scheduler started (evaluates every hour)")

    # Knowledge discovery scheduler (configurable via env)
    try:
        interval_env = _os.getenv("DISCOVERY_INTERVAL_SECS")
        seeds_env = _os.getenv("DISCOVERY_SEEDS_PER_CYCLE")
        interval_val = int(interval_env) if interval_env else None
        seeds_val = int(seeds_env) if seeds_env else None
    except Exception:
        interval_val = None
        seeds_val = None

    await start_discovery_scheduler(interval_val, seeds_val)
    if interval_val or seeds_val:
        print(f"✓ Knowledge discovery scheduler started (interval={interval_val or 'default'}s, seeds={seeds_val or 'default'})")
    else:
        print("✓ Knowledge discovery scheduler started")

@app.on_event("shutdown")
async def on_shutdown():
    await reflection_service.stop()
    await task_executor.stop_workers()
    await health_monitor.stop()
    await trigger_mesh.stop()
    await meta_loop_engine.stop()
    await auto_retrain_engine.stop()
    await stop_benchmark_scheduler()
    await stop_discovery_scheduler()

    # Clean up metrics DB resources
    metrics_sess = getattr(app.state, "metrics_session", None)
    if metrics_sess:
        try:
            await metrics_sess.close()
        except Exception:
            pass
    metrics_engine = getattr(app.state, "metrics_engine", None)
    if metrics_engine:
        try:
            await metrics_engine.dispose()
        except Exception:
            pass

    # Dispose core application DB engine to avoid aiosqlite warnings on shutdown
    try:
        from .models import engine as core_engine  # local import to avoid early side effects
        await core_engine.dispose()
    except Exception:
        pass

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
# Conditionally include unified health/triage endpoints (observe-only by default)
try:
    from .settings import settings as _settings
    from .routes import health_unified as _health_unified
    if getattr(_settings, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(_settings, "SELF_HEAL_EXECUTE", False):
        app.include_router(_health_unified.router, prefix="/api")
except Exception:
    # Keep startup resilient if optional modules/imports fail
    pass
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
app.include_router(speech_api.router)
app.include_router(parliament_api.router)
app.include_router(coding_agent_api.router)
app.include_router(constitutional_api.router)
app.include_router(dashboard_router)
app.include_router(business_api_router)
app.include_router(cognition_router)
app.include_router(core_domain_router)
app.include_router(transcendence_domain_router)
app.include_router(security_domain_router)

# Grace IDE WebSocket (optional)
# Enabled only when ENABLE_IDE_WS is truthy; safely gated to avoid import-time failure
import os as _os
if _os.getenv("ENABLE_IDE_WS", "0") in {"1", "true", "True", "YES", "yes"}:
    try:
        from grace_ide.api.websocket import router as ide_ws_router
        app.include_router(ide_ws_router)
    except ImportError:
        # Optional dependency not present; continue without IDE websocket
        pass
