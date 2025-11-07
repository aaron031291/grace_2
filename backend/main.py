from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
import logging
from .base_models import Base, engine
from .routes import chat, auth_routes, metrics, reflections, tasks, history, causal, goals, knowledge, evaluation, summaries, sandbox, executor, governance, hunter, health_routes, issues, memory_api, immutable_api, meta_api, websocket_routes, plugin_routes, ingest, trust_api, ml_api, execution, temporal_api, causal_graph_api, speech_api, parliament_api, coding_agent_api, constitutional_api, learning, scheduler_observability, meta_focus, proactive_chat, subagent_bridge, autonomy_routes, commit_routes, learning_routes, verification_routes, cognition_api, concurrent_api, verification_api
from .transcendence.dashboards.observatory_dashboard import router as dashboard_router
from .transcendence.business.api import router as business_api_router
from .reflection import reflection_service
from .auth import get_current_user
from .verification_integration import verification_integration
from .routers.cognition import router as cognition_router
from .routers.core_domain import router as core_domain_router
from .routers.transcendence_domain import router as transcendence_domain_router
from .routers.security_domain import router as security_domain_router
from .routers.verification_router import router as verification_router
from .request_id_middleware import RequestIDMiddleware
from .metrics_service import init_metrics_collector

app = FastAPI(title="Grace API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")
    logging.error(f"Unhandled exception [request_id={request_id}]: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An internal error occurred. Please try again.",
            "request_id": request_id
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": request_id
        }
    )

from .task_executor import task_executor
from .self_healing import health_monitor
from .trigger_mesh import trigger_mesh, setup_subscriptions
from .meta_loop import meta_loop_engine
from .websocket_manager import setup_ws_subscriptions
from .trusted_sources import trust_manager
from .auto_retrain import auto_retrain_engine
from .benchmark_scheduler import start_benchmark_scheduler, stop_benchmark_scheduler
from .knowledge_discovery_scheduler import start_discovery_scheduler, stop_discovery_scheduler
from .grace_spine_integration import activate_grace_autonomy, deactivate_grace_autonomy
from .routes.agentic_insights import router as agentic_insights_router
from .self_heal.scheduler import scheduler as self_heal_scheduler
from .self_heal.runner import runner as self_heal_runner
from .shard_orchestrator import shard_orchestrator
from .input_sentinel import input_sentinel
from .policy_engine import policy_engine
from .autonomy_tiers import autonomy_manager
from .concurrent_executor import concurrent_executor
from .domains.all_domain_adapters import domain_registry
from .startup_integration import start_verification_systems, stop_verification_systems
try:
    from .knowledge_preload import KnowledgePreloader
except ImportError:
    KnowledgePreloader = None

@app.on_event("startup")
async def on_startup():
    # Ensure model modules imported so Base.metadata is populated
    try:
        import importlib
        for _mod in ("backend.governance_models", "backend.knowledge_models", "backend.parliament_models"):
            try:
                importlib.import_module(_mod)
            except Exception as e:
                print(f"  Warning: Could not import {_mod}: {e}")
    except Exception as e:
        print(f"  Warning: Model import error: {e}")
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Enable WAL mode for better concurrency
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA busy_timeout=30000"))
        await conn.execute(text("PRAGMA foreign_keys=ON"))
    print("✓ Database initialized (WAL mode enabled, foreign keys enforced)")
    
    # Metrics DB (separate)
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from .metrics_models import Base as MetricsBase
    app.state.metrics_engine = create_async_engine(
        "sqlite+aiosqlite:///./databases/metrics.db",
        echo=False,
        future=True,
        connect_args={"timeout": 30, "check_same_thread": False},
        pool_pre_ping=True
    )
    app.state.metrics_sessionmaker = async_sessionmaker(app.state.metrics_engine, expire_on_commit=False)
    async with app.state.metrics_engine.begin() as mconn:
        await mconn.run_sync(MetricsBase.metadata.create_all)
        await mconn.execute(text("PRAGMA journal_mode=WAL"))
        await mconn.execute(text("PRAGMA busy_timeout=30000"))
        await mconn.execute(text("PRAGMA foreign_keys=ON"))
    
    # Pass session factory instead of shared session
    init_metrics_collector(session_factory=app.state.metrics_sessionmaker)
    
    print("✓ Grace API server starting...")
    print("  Visit: http://localhost:8000/health")
    print("  Docs: http://localhost:8000/docs")
    
    # Start core systems
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
    print(f"✓ Knowledge discovery scheduler started")
    
    print("\n🤖 ==================== ADVANCED AI SYSTEMS ====================")
    
    # Load policy-as-code engine
    await policy_engine.load_policies()
    
    # Wire policy engine to autonomy manager
    autonomy_manager.policy_engine = policy_engine
    
    # Start concurrent executor for multi-threaded background tasks
    await concurrent_executor.start()
    
    # Register all domain adapters
    from .self_heal.adapter import self_healing_adapter
    domain_registry.register_adapter("core", self_healing_adapter)
    print(f"  ✓ Registered {len(domain_registry.get_all_adapters())} domain adapters")
    
    # Start shard orchestrator for parallel multi-agent execution
    await shard_orchestrator.start()
    
    # Start Input Sentinel for agentic error handling
    await input_sentinel.start()
    
    # Preload AI expertise into Grace
    if KnowledgePreloader:
        try:
            print("📚 Loading expert AI knowledge into Grace...")
            preloader = KnowledgePreloader()
            await preloader.preload_ai_expertise()
        except Exception as e:
            print(f"  ⚠️ Knowledge preload partial: {e}")
    else:
        print("  ⚠️ Knowledge preloader not available (missing dependencies)")
    
    print("============================================================\n")
    
    # Start verification and resilience systems
    await start_verification_systems()
    
    # Start GRACE Agentic Spine
    await activate_grace_autonomy()
    print("✓ GRACE Agentic Spine activated")

@app.on_event("shutdown")
async def on_shutdown():
    # Stop agentic spine first
    await deactivate_grace_autonomy()
    
    # Stop verification systems
    await stop_verification_systems()
    
    # Stop concurrent executor
    await concurrent_executor.stop()
    
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
    if hasattr(app.state, "metrics_engine"):
        try:
            await app.state.metrics_engine.dispose()
        except Exception:
            pass
    
    # Dispose core engine
    try:
        await engine.dispose()
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

# Register all routers
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
    if getattr(_settings, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(_settings, "SELF_HEAL_EXECUTE", False):
        app.include_router(_health_unified.router, prefix="/api")
        app.include_router(_playbooks.router)
        app.include_router(_incidents.router)
        app.include_router(_learning.router)
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
app.include_router(agentic_insights_router, prefix="/api")
app.include_router(verification_routes.router)
app.include_router(verification_api.router)
app.include_router(verification_router)
app.include_router(cognition_api.router)
app.include_router(concurrent_api.router)

# Self-heal observability and learning endpoints (feature-gated)
try:
    from .settings import settings as _settings_check
    if getattr(_settings_check, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(_settings_check, "SELF_HEAL_EXECUTE", False) or getattr(_settings_check, "LEARNING_AGGREGATION_ENABLED", False):
        app.include_router(learning.router)
        app.include_router(scheduler_observability.router)
        app.include_router(meta_focus.router)
        app.include_router(proactive_chat.router)
        app.include_router(subagent_bridge.router)
        app.include_router(autonomy_routes.router)
        app.include_router(commit_routes.router)
        app.include_router(learning_routes.router)
except Exception:
    pass

# Grace IDE WebSocket (optional)
import os as _os
if _os.getenv("ENABLE_IDE_WS", "0") in {"1", "true", "True", "YES", "yes"}:
    try:
        from grace_ide.api.websocket import router as ide_ws_router
        app.include_router(ide_ws_router)
    except ImportError:
        pass
