"""
Application Factory
Creates and configures the FastAPI application
No circular imports - clean dependency tree
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    This factory pattern eliminates circular imports by:
    1. Creating the app first
    2. Importing routers only when needed
    3. Registering routers in order of priority
    """
    
    app = FastAPI(
        title="Grace API",
        version="2.0.0",
        description="Autonomous AI system with self-healing, knowledge management, and multi-domain intelligence"
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and register routers from the new api package
    # These are clean, self-contained modules with no circular dependencies
    
    from backend.api import (
        trusted_sources,
        librarian,
        self_healing,
        system,
        memory,
        ingestion,
        events,
        automation,
    )
    
    # Register API routers (order matters for route precedence)
    app.include_router(system.router)
    app.include_router(self_healing.router)
    app.include_router(librarian.router)
    app.include_router(trusted_sources.router)
    app.include_router(memory.router)
    app.include_router(ingestion.router)
    app.include_router(events.router)
    app.include_router(automation.router)
    
    # Startup event
    @app.on_event("startup")
    async def startup():
        print("\n[Factory] Starting Grace API services...")
        
        # Start log watcher
        try:
            from backend.services.log_watcher import log_watcher
            await log_watcher.start()
            print("[Factory] Log watcher started")
        except Exception as e:
            print(f"[Factory] Log watcher failed to start: {e}")
        
        print("[Factory] All services started successfully!\n")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown():
        print("\n[Factory] Shutting down Grace API services...")
        
        try:
            from backend.services.log_watcher import log_watcher
            await log_watcher.stop()
            print("[Factory] Log watcher stopped")
        except Exception:
            pass
        
        print("[Factory] Shutdown complete\n")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        from backend.services.log_watcher import log_watcher
        from backend.services.event_bus import event_bus
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "api_type": "factory_pattern",
            "services": {
                "log_watcher": log_watcher.get_status(),
                "event_bus": event_bus.get_stats()
            }
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Grace API - Factory Pattern",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# For backwards compatibility with existing code that imports app directly
app = create_app()
