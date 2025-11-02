from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import Base, engine
from .routes import chat, auth_routes, metrics, reflections, tasks, history, causal, goals, knowledge, evaluation, summaries, sandbox, executor
from .reflection import reflection_service

app = FastAPI(title="Grace API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .task_executor import task_executor

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database initialized")
    print("✓ Grace API server starting...")
    print("  Visit: http://localhost:8000/health")
    print("  Docs: http://localhost:8000/docs")
    await reflection_service.start()
    await task_executor.start_workers()

@app.on_event("shutdown")
async def on_shutdown():
    await reflection_service.stop()
    await task_executor.stop_workers()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Grace API is running"}

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
