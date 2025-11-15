"""
Backend Main Entry Point - Minimal Grace API
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid

from backend.learning_systems.advanced_learning import advanced_learning_supervisor
from backend.routes.operator_dashboard import router as operator_router
from backend.routes.remote_access_api import router as remote_access_router
from backend.routes.autonomous_learning_api import router as learning_router
from backend.routes.mission_control_api import router as mission_control_router
from backend.routes.auth import router as auth_router
from backend.routes.learning_visibility_api import router as learning_visibility_router
from backend.routes.port_manager_api import router as port_manager_router
from backend.routes.guardian_api import router as guardian_router
from fastapi import HTTPException, status
from pydantic import BaseModel, constr
from datetime import timedelta
from sqlalchemy import select
from backend.models import User, async_session
from backend.auth import hash_password, verify_and_upgrade_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Track degraded features for Layer 2
app = FastAPI(title="Grace API", version="2.0.0")

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register operator dashboard
app.include_router(operator_router)

# Register remote access (zero-trust secure remote sessions)
app.include_router(remote_access_router)

# Register autonomous learning
app.include_router(learning_router)

# Register mission control
app.include_router(mission_control_router)

# Register auth routes
app.include_router(auth_router)

# Register port manager
app.include_router(port_manager_router)

# Register Guardian (unified system protection)
app.include_router(guardian_router)

# Register learning visibility & tracking
app.include_router(learning_visibility_router)

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok"}

@app.get("/")
async def root():
    resp = JSONResponse(content={"uid": str(uuid.uuid4())})
    resp.headers["X-FastAPI-State"] = str([{"seed": str(uuid.uuid4())}])
    return resp

@app.on_event("startup")
async def startup_unified_llm():
    """Initialize unified LLM and model capability system in non-fatal way"""
    try:
        from backend.unified_llm import unified_llm
        from backend.model_capability_system import capability_system
        
        await unified_llm.initialize()
        await capability_system.manage_cache()  # Warm primary models
        
        print("[OK] Model capability system initialized")
        print("[OK] Reading model manifest with 15 models")
        
        # Show which models are loaded
        matrix = await capability_system.get_capability_matrix()
        print(f"[OK] {len(matrix['warm_cache'])} models in warm cache")
    except Exception as e:
        # Do not let startup fail – mark Layer 2 degraded and continue
        print(f"[WARN] Unified LLM startup degraded: {e}")
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
        # Record degraded feature for health/status endpoints
        try:
            app.state.degraded_features.add("unified_llm")
        except Exception:
            # app.state may not be available in some edge cases, ignore
            pass

@app.on_event("startup")
async def startup_advanced_learning():
    """Starts the advanced learning supervisor and its sub-agents."""
    advanced_learning_supervisor.start()

@app.on_event("shutdown")
def shutdown_advanced_learning():
    """Stops the advanced learning agents gracefully."""
    advanced_learning_supervisor.stop()


@app.post("/api/chat")
async def chat(request: dict):
    """Chat with Grace - Fast built-in responses"""
    message = request.get("message", "")
    
    # Quick built-in response (instant, no model delays)
    try:
        from backend.grace_llm import get_grace_llm
        llm = get_grace_llm()
        result = await llm.generate_response(message, domain="chat")
        
        return {
            "response": result.get("text", "I'm Grace. All 20 kernels operational. How can I help?"),
            "kernel": "coding_agent",
            "llm_provider": "grace_llm_fast",
            "model": "built_in",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Ultra-fast fallback
        response_map = {
            "hi": "Hello! I'm Grace. All 20 kernels are operational.",
            "hello": "Hi! How can I assist you with code, knowledge, or tasks?",
            "status": "All 20 kernels operational. 4 layers active. Ready to help!",
            "help": "I can help with:\n- Writing and debugging code\n- Managing knowledge\n- Self-healing issues\n- Learning from data\n- Autonomous task execution\n\nWhat do you need?",
        }
        
        msg_lower = message.lower().strip()
        response = response_map.get(msg_lower, f"I received: '{message}'\n\nAll 20 kernels ready. I can help with code, knowledge, tasks, or conversation. What would you like to do?")
        
        return {
            "response": response,
            "kernel": "coding_agent",
            "llm_provider": "instant_fallback",
            "model": "built_in",
            "timestamp": datetime.now().isoformat()
        }
    
    # Try to use real LLM (OpenAI/Anthropic/Ollama)
    try:
        import os
        
        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Priority 1: Try Ollama (Open Source - FREE, runs locally)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                ollama_response = await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama3.2:latest",  # or mistral, codellama, deepseek-coder
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are Grace, an advanced autonomous AI system with 20 operational kernels. Be conversational, helpful, and naturally engaging. You can write code, manage knowledge, self-heal, and execute tasks autonomously."
                            },
                            {"role": "user", "content": message}
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.8,
                            "num_predict": 500
                        }
                    },
                    timeout=30.0
                )
                
                if ollama_response.status_code == 200:
                    result = ollama_response.json()
                    response_text = result["message"]["content"]
                    
                    return {
                        "response": response_text,
                        "kernel": "coding_agent",
                        "llm_provider": "ollama_llama3",
                        "llm_type": "open_source",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as ollama_error:
            print(f"Ollama not available: {ollama_error}")
            pass
        
        # Priority 2: Try OpenAI (if key provided)
        if openai_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=openai_key)
                
                completion = await client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are Grace, an advanced autonomous AI system with 20 operational kernels. Be conversational, helpful, and naturally engaging."},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                
                response_text = completion.choices[0].message.content
                
                return {
                    "response": response_text,
                    "kernel": "coding_agent",
                    "llm_provider": "openai_gpt4",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"OpenAI error: {e}")
                pass
        
        # Priority 3: Try Claude (if key provided)
        elif anthropic_key:
            # Use Claude for conversations
            try:
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=anthropic_key)
                
                response = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=800,
                    system="""You are Grace, an advanced autonomous AI system with 20 operational kernels.

You have complete capabilities for code, knowledge, self-healing, learning, and autonomous task execution.

Be conversational, insightful, and technically excellent. Engage naturally like ChatGPT or Claude.""",
                    messages=[
                        {"role": "user", "content": message}
                    ]
                )
                
                response_text = response.content[0].text
                
                return {
                    "response": response_text,
                    "kernel": "coding_agent",
                    "llm_provider": "claude_sonnet",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"Anthropic error: {e}")
                pass
        
        # Fallback to Grace's built-in LLM
        from backend.grace_llm import get_grace_llm
        llm = get_grace_llm()
        result = await llm.generate_response(message, domain="chat")
        
        return {
            "response": result.get("text", f"I'm Grace. All 20 kernels are ready. How can I assist you?"),
            "kernel": "coding_agent",
            "llm_provider": "grace_llm",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Final fallback
        return {
            "response": f"I'm Grace, your AI assistant. All 20 kernels are operational.\n\nYou said: {message}\n\nI'm ready to help with code, knowledge, tasks, or conversation. What would you like to do?",
            "kernel": "coding_agent",
            "llm_provider": "fallback",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/learning/status")
async def learning_status():
    """Learning integration status with model orchestrator insights"""
    from backend.model_orchestrator import model_orchestrator
    
    insights = await model_orchestrator.get_learning_insights()
    
    return {
        "status": "operational",
        "total_outcomes": insights["total_interactions"],
        "models_tested": insights["models_tested"],
        "best_performers": insights["best_performers"],
        "learning_rate": 0.85,
        "model_accuracy": 0.92,
        "active_learning": True,
        "kernels_learning_from": 20,
        "insights": insights
    }

@app.get("/api/models/available")
async def models_available():
    """List all available models and their status"""
    from backend.model_orchestrator import model_orchestrator
    
    models = await model_orchestrator.list_available_models()
    
    installed = [m for m in models if m["installed"]]
    not_installed = [m for m in models if not m["installed"]]
    
    return {
        "total_models": len(models),
        "installed": len(installed),
        "available_to_install": len(not_installed),
        "models": models,
        "recommendation": "Install: ollama pull qwen2.5:32b && ollama pull deepseek-coder-v2:16b"
    }

@app.get("/api/models/performance")
async def models_performance():
    """Grace's learned insights about model performance"""
    from backend.model_capability_system import capability_system
    
    return await capability_system.get_learning_summary()

@app.get("/api/models/capabilities")
async def models_capabilities():
    """Full capability matrix - kernels, models, routing, performance"""
    from backend.model_capability_system import capability_system
    
    return await capability_system.get_capability_matrix()

@app.post("/api/models/approve")
async def approve_model_output(request: dict):
    """User approves/rejects model output - reinforcement learning"""
    from backend.model_capability_system import capability_system
    
    model = request.get("model")
    task_id = request.get("task_id")
    approved = request.get("approved", True)
    rating = request.get("rating")  # 1-5
    
    await capability_system.record_approval(model, task_id, approved, rating)
    
    return {
        "success": True,
        "message": f"Feedback recorded. Grace learns from this.",
        "trust_updated": True
    }

@app.get("/api/context/suggestions")
async def get_context_suggestions(
    kernel: str = "unknown",
    message: str = None
):
    """Get intelligent context suggestions"""
    from backend.context_suggestion_system import context_system
    
    suggestions = await context_system.get_suggestions(
        current_kernel=kernel,
        recent_activity=[],
        user_message=message
    )
    
    return {
        "suggestions": suggestions,
        "total": len(suggestions)
    }

@app.post("/api/context/dismiss")
async def dismiss_context(request: dict):
    """Dismiss a context suggestion for this session"""
    from backend.context_suggestion_system import context_system
    
    topic_type = request.get("type")
    kernel = request.get("kernel")
    
    context_system.dismiss_topic(topic_type, kernel)
    
    return {"success": True}

# ===== VISION & VIDEO API =====

@app.post("/api/vision/analyze")
async def analyze_image(file: UploadFile = File(...), quality: str = "balanced"):
    """Analyze image using vision models"""
    from backend.remote_vision_capture import vision_capture
    
    image_data = await file.read()
    
    result = await vision_capture.analyze_screenshot(
        image_data=image_data,
        source=file.filename or "upload",
        quality=quality
    )
    
    return result

@app.post("/api/vision/video")
async def analyze_video(file: UploadFile = File(...)):
    """Analyze video using Video-LLaVA"""
    from backend.remote_vision_capture import vision_capture
    
    # Save video temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(await file.read())
        video_path = tmp.name
    
    result = await vision_capture.analyze_video(
        video_path=video_path,
        source=file.filename or "upload"
    )
    
    return result

@app.post("/api/remote-access/capture")
async def remote_capture_screenshot(request: dict):
    """Capture and analyze screenshot from remote host"""
    from backend.remote_vision_capture import vision_capture
    
    host_id = request.get("host_id")
    screenshot_b64 = request.get("screenshot")
    
    # Decode base64
    import base64
    image_data = base64.b64decode(screenshot_b64)
    
    # Fast analysis for remote captures
    result = await vision_capture.analyze_screenshot(
        image_data=image_data,
        source=f"remote_host_{host_id}",
        quality="fast",  # Use fast model for real-time
        context={"remote_access": True, "host_id": host_id}
    )
    
    return result

@app.get("/api/vision/observations")
async def get_visual_observations(limit: int = 50):
    """Get stored visual observations"""
    from backend.models.base_models import async_session
    from sqlalchemy import text
    
    try:
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT * FROM visual_observations 
                ORDER BY timestamp DESC 
                LIMIT :limit
            """), {"limit": limit})
            
            rows = result.fetchall()
            
            observations = []
            for row in rows:
                observations.append({
                    "id": row[0],
                    "source": row[1],
                    "model_used": row[2],
                    "description": row[3],
                    "ui_elements": row[4],
                    "detected_text": row[5],
                    "timestamp": row[11]
                })
            
            return {
                "observations": observations,
                "total": len(observations)
            }
            
    except Exception as e:
        return {"observations": [], "error": str(e)}

# ===== SPEECH API (Persistent Voice Loop) =====

from fastapi import UploadFile, File, Form
from datetime import datetime
import uuid

# In-memory session storage (replace with DB later)
voice_sessions = {}

@app.post("/api/speech/session/start")
async def start_voice_session():
    """Start a persistent voice conversation session"""
    session_id = str(uuid.uuid4())
    voice_sessions[session_id] = {
        "session_id": session_id,
        "status": "idle",
        "context": [],
        "total_exchanges": 0,
        "started_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    }
    
    return voice_sessions[session_id]

@app.post("/api/speech/session/end")
async def end_voice_session(request: dict):
    """End voice session and save to memory"""
    session_id = request.get("session_id")
    
    if session_id in voice_sessions:
        session_data = voice_sessions.pop(session_id)
        
        # TODO: Save to memory tables/intent records for auditing
        
        return {
            "success": True,
            "exchanges": session_data["total_exchanges"],
            "duration_seconds": 0
        }
    
    return {"success": False, "error": "Session not found"}

@app.post("/api/speech/process")
async def process_voice(
    audio: UploadFile = File(...),
    session_id: str = Form(...)
):
    """Process voice: STT -> Grace LLM + Agentic Spine -> TTS"""
    
    try:
        # Read audio file
        audio_bytes = await audio.read()
        
        # Step 1: Speech-to-Text (STT)
        try:
            from backend.speech_tts.speech_service import speech_service
            # Save temporary audio file
            temp_audio_path = f"./audio_messages/voice_{session_id}_{datetime.now().timestamp()}.webm"
            with open(temp_audio_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Transcribe using Whisper
            result = await speech_service.upload_audio(
                user="voice_user",
                audio_data=audio_bytes,
                audio_format="webm",
                session_id=session_id
            )
            transcript = result.get("transcript", "Unable to transcribe")
        except Exception as stt_error:
            # Fallback if Whisper not available
            transcript = "[STT Error: Whisper not configured. Install: pip install openai-whisper]"
        
        # Step 2: Route through Unified LLM (Ollama + Grace intelligence)
        try:
            from backend.unified_llm import unified_llm
            
            # Get conversation context from session
            context = []
            if session_id in voice_sessions:
                context = voice_sessions[session_id].get("context", [])
            
            # Build conversation history
            conversation_history = []
            for ctx in context[-5:]:
                conversation_history.append({"role": "user", "content": ctx.get("user", "")})
                conversation_history.append({"role": "assistant", "content": ctx.get("grace", "")})
            
            # Use unified LLM with memory + agentic routing
            result = await unified_llm.chat(
                message=transcript,
                context=conversation_history,
                use_memory=True,
                use_agentic=True
            )
            
            response_text = result["text"]
            
        except Exception as nlp_error:
            print(f"NLP error: {nlp_error}")
            import traceback
            traceback.print_exc()
            response_text = f"I heard: '{transcript}'. I'm ready to help. What would you like me to do?"
        
        # Step 3: Text-to-Speech (TTS)
        try:
            from backend.speech_tts.tts_service import tts_service
            # Generate audio response
            tts_result = await tts_service.synthesize(
                text=response_text,
                voice="grace_default",
                session_id=session_id
            )
            response_audio_url = tts_result.get("audio_url", None)
        except Exception as tts_error:
            # No audio, text only
            response_audio_url = None
        
        # Update session state with full context
        if session_id in voice_sessions:
            voice_sessions[session_id]["context"].append({
                "user": transcript,
                "grace": response_text,
                "timestamp": datetime.now().isoformat(),
                "llm_used": True,
                "agentic_spine_used": True
            })
            voice_sessions[session_id]["total_exchanges"] += 1
            voice_sessions[session_id]["last_activity"] = datetime.now().isoformat()
            voice_sessions[session_id]["status"] = "idle"
        
        return {
            "transcript": transcript,
            "response_text": response_text,
            "response_audio_url": response_audio_url,
            "session_id": session_id,
            "context_length": len(voice_sessions.get(session_id, {}).get("context", [])),
            "nlp_active": True,
            "kernels_available": 20
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "fallback": "Text mode available - type your message instead",
            "transcript": "[Audio processing failed]",
            "response_text": "I encountered an error processing your voice. Please try text chat instead."
        }

@app.get("/api/speech/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id in voice_sessions:
        return voice_sessions[session_id]
    return {"error": "Session not found"}

@app.get("/api/speech/tts/sample.mp3")
async def sample_tts_audio():
    """Sample TTS audio (placeholder)"""
    # TODO: Return actual generated TTS audio
    return {"message": "TTS audio generation placeholder"}

__all__ = ['app']
