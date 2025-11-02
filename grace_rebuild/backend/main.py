from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import Base, engine
from .routes import chat, auth_routes

app = FastAPI(title="Grace API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database initialized")
    print("✓ Grace API server starting...")
    print("  Visit: http://localhost:8000/health")
    print("  Docs: http://localhost:8000/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Grace API is running"}

app.include_router(auth_routes.router)
app.include_router(chat.router)
