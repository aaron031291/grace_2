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

app = FastAPI(title="Grace API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Inject/propagate X-Request-ID for log correlation
app.add_middleware(RequestIDMiddleware)

from .task_executor import task_executor
from .self_healing import health_monitor
from .trigger_mesh import trigger_mesh, setup_subscriptions
from .meta_loop import meta_loop_engine
from .websocket_manager import setup_ws_subscriptions
from .trusted_sources import trust_manager
from .auto_retrain import auto_retrain_engine
from .benchmark_scheduler import start_benchmark_scheduler, stop_benchmark_scheduler
from .knowledge_discovery_scheduler import start_discovery_scheduler, stop_discovery_scheduler
from .self_heal.scheduler import scheduler as self_heal_scheduler
from .self_heal.runner import runner as self_heal_runner

@app.on_event("startup")
async def on_startup():
    # Ensure console is UTF-8 safe to avoid crashes on Windows terminals
    try:
        ensure_utf8_console()
    except Exception:
        pass
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

    # Compatibility shim: ensure verification_events.passed column exists
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            # SQLite pragma to list columns
            result = await conn.exec_driver_sql("PRAGMA table_info(verification_events);")
            cols = [row[1] for row in result.fetchall()]
            if "passed" not in cols:
                await conn.exec_driver_sql("ALTER TABLE verification_events ADD COLUMN passed BOOLEAN;")
                print("✓ Added missing column: verification_events.passed")
    except Exception as e:
        # Non-fatal; meta loop verification may still fail until migrations are applied
        print(f"⚠ Verification schema check failed or not needed: {e}")

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
    # Cognition alerts subscriptions (non-fatal if unavailable)
    try:
        from .cognition_alerts import setup_alert_subscriptions as _setup_alerts
        await _setup_alerts()
    except Exception:
        pass
    await trust_manager.initialize_defaults()
    await reflection_service.start()
    await task_executor.start_workers()
    await health_monitor.start()
    await meta_loop_engine.start()
    await auto_retrain_engine.start()
    await start_benchmark_scheduler()
    print("✓ Benchmark scheduler started (evaluates every hour)")

    # Self-heal observe-only scheduler (feature-gated)
    try:
        from .settings import settings as _settings2
        if getattr(_settings2, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(_settings2, "SELF_HEAL_EXECUTE", False):
            await self_heal_scheduler.start()
            print("✓ Self-heal observe-only scheduler started")
    except Exception:
        # keep startup resilient
        pass

    # Start execution runner only when execute mode is enabled
    try:
        from .settings import settings as _settings3
        if getattr(_settings3, "SELF_HEAL_EXECUTE", False):
            await self_heal_runner.start()
            print("✓ Self-heal execution runner started (execute mode)")
    except Exception:
        pass

    # Knowledge discovery scheduler (configurable via env)
    import os as _os
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

    # Stop self-heal observe-only scheduler if running
    try:
        await self_heal_scheduler.stop()
    except Exception:
        pass

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

@app.get("/api/status")
async def api_status():
    """Public status endpoint used by CLI smoke tests.
    Returns overall cognition metrics and domain details.
    """
    try:
        # Lazy imports to avoid startup import ordering issues
        from .metrics_service import get_metrics_collector
        from .cognition_metrics import get_metrics_engine

        collector = get_metrics_collector()
        engine = get_metrics_engine()

        # Sync latest aggregates from collector into the engine
        for domain, kpis in getattr(collector, "aggregates", {}).items():
            if domain in getattr(engine, "domains", {}):
                engine.update_domain(domain, kpis)

        status = engine.get_status()
        # Ensure required keys exist (shape expected by scripts/cli_test.py)
        required = {
            "overall_health": status.get("overall_health", 0.0),
            "overall_trust": status.get("overall_trust", 0.0),
            "overall_confidence": status.get("overall_confidence", 0.0),
            "saas_ready": status.get("saas_ready", False),
            "domains": status.get("domains", {}),
        }
        status.update(required)
        return status
    except Exception as e:
        # Non-fatal: return a minimal payload with required keys so clients don't break
        return {
            "timestamp": None,
            "overall_health": 0.0,
            "overall_trust": 0.0,
            "overall_confidence": 0.0,
            "saas_ready": False,
            "domains": {},
            "error": str(e),
        }

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
    from .routes import playbooks as _playbooks
    from .routes import incidents as _incidents
    from .routes import learning as _learning
    from .routes import meta_focus as _meta_focus
    from .routes import self_heal_debug as _self_heal_debug
    if getattr(_settings, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(_settings, "SELF_HEAL_EXECUTE", False):
        app.include_router(_health_unified.router, prefix="/api")
        app.include_router(_playbooks.router)
        app.include_router(_incidents.router)
        app.include_router(_learning.router)
        app.include_router(_meta_focus.router)
        app.include_router(_self_heal_debug.router)
except Exception:
    pass
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
include_router(websocket_routes.router)
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
