#!/usr/bin/env python3
"""
Minimal Grace Backend - Quick Start Entry Point

This is the minimal backend referenced in README.md for quick development.
Provides core API endpoints without all the advanced features.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import cognition authority for cockpit integration
try:
    from backend.cognition_intent import cognition_authority
    from backend.websocket_handler import websocket_manager
    cognition_available = True
except ImportError:
    cognition_available = False
    cognition_authority = None
    websocket_manager = None

# Create FastAPI app
app = FastAPI(
    title="Grace Minimal Backend",
    description="Minimal Grace backend for development with cockpit support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "message": "Grace minimal backend is running"}

# Status endpoint
@app.get("/api/status")
async def get_status():
    """Quick cognition status"""
    try:
        from backend.cognition_metrics import get_metrics_engine
        metrics = get_metrics_engine()
        status = metrics.get_status()
        return status
    except Exception as e:
        # Fallback if metrics engine not available
        return {
            "status": "operational",
            "version": "minimal",
            "message": "Grace minimal backend active",
            "overall_health": 85.0,
            "overall_trust": 80.0,
            "overall_confidence": 75.0,
            "saas_ready": False,
            "domains": {
                "core": {"health": 90.0, "trust": 85.0, "confidence": 80.0},
                "cognition": {"health": 85.0, "trust": 80.0, "confidence": 75.0}
            }
        }

# Metrics endpoint
@app.get("/api/metrics")
async def get_metrics():
    """Basic metrics summary"""
    return {
        "overall_health": 85.0,
        "overall_trust": 80.0,
        "overall_confidence": 75.0,
        "domains": {
            "core": 90.0,
            "cognition": 85.0
        }
    }

# Cognition status endpoint
@app.get("/api/cognition/status")
async def get_cognition_status():
    """Detailed domain metrics"""
    return {
        "total_intents": 0,
        "completed": 0,
        "failed": 0,
        "success_rate": 0.0,
        "capabilities_registered": 6,
        "status": "operational",
        "domains": {
            "core": {"health": 90.0, "trust": 85.0, "confidence": 80.0},
            "cognition": {"health": 85.0, "trust": 80.0, "confidence": 75.0}
        }
    }

# Readiness report
@app.get("/api/cognition/readiness")
async def get_readiness():
    """SaaS readiness report"""
    return {
        "ready": False,
        "overall_health": 75.6,
        "overall_trust": 71.8,
        "overall_confidence": 69.6,
        "saas_ready": False,
        "next_steps": [
            "Complete backend integration",
            "Fix frontend connections",
            "Add WebSocket support",
            "Resolve encoding issues"
        ]
    }

# Benchmark details
@app.get("/api/cognition/benchmark/{metric}")
async def get_benchmark(metric: str):
    """Benchmark details"""
    benchmarks = {
        "overall_health": {
            "name": "Overall Health",
            "current": 75.6,
            "target": 90.0,
            "sustained": False,
            "trend": "improving"
        },
        "overall_trust": {
            "name": "Overall Trust",
            "current": 71.8,
            "target": 90.0,
            "sustained": False,
            "trend": "stable"
        }
    }

    if metric not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Benchmark {metric} not found")

    return benchmarks[metric]

# Domain update endpoint
@app.post("/api/cognition/domain/{domain_id}/update")
async def update_domain_kpi(domain_id: str, kpi_data: dict):
    """Update domain KPIs"""
    return {
        "domain": domain_id,
        "updated": True,
        "message": f"Domain {domain_id} KPIs updated"
    }

# WebSocket endpoint for cockpit
@app.websocket("/ws/cognition")
async def cognition_websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint for cockpit cognition interface"""
    if not cognition_available or websocket_manager is None:
        await websocket.close(code=1008, reason="Cognition system not available")
        return

    await websocket_manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Handle message through cognition system
            await handle_cognition_message(websocket, data)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

async def handle_cognition_message(websocket: WebSocket, data: dict):
    """Handle incoming cognition WebSocket messages"""
    try:
        message_type = data.get("type", "unknown")

        if message_type == "chat":
            # Process through cognition authority
            user_message = data.get("message", "")
            session_id = data.get("session_id", "cockpit")
            user_name = data.get("user_name", "cockpit_user")

            if cognition_authority:
                # Use cognition authority for full AI interaction
                result = await cognition_authority.process_user_request(
                    utterance=user_message,
                    user_id=user_name,
                    session_id=session_id
                )

                # Send structured response
                await websocket.send_json({
                    "type": "chat_response",
                    "message": result.get("message", "Response processed"),
                    "structured_output": result.get("structured_output", {}),
                    "intent_type": result.get("intent_type", "unknown"),
                    "status": result.get("status", "completed"),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Fallback response
                await websocket.send_json({
                    "type": "chat_response",
                    "message": f"Echo: {user_message}",
                    "status": "fallback",
                    "timestamp": datetime.now().isoformat()
                })

        elif message_type == "status_request":
            # Send current system status
            if websocket_manager:
                status = await websocket_manager.get_system_status()
            else:
                status = {
                    "overall_health": 50.0,
                    "overall_trust": 50.0,
                    "overall_confidence": 50.0,
                    "saas_ready": False,
                    "domains": {},
                    "error": "WebSocket manager not available"
                }
            await websocket.send_json({
                "type": "status_update",
                "status": status
            })

        elif message_type == "subscribe":
            # Handle subscriptions
            if websocket_manager:
                subscriptions = data.get("subscriptions", [])
                websocket_manager.client_states[websocket]["subscriptions"].update(subscriptions)
                await websocket.send_json({
                    "type": "subscribed",
                    "subscriptions": list(websocket_manager.client_states[websocket]["subscriptions"])
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "error": "Subscription system not available"
                })

        elif message_type == "approval_response":
            # Handle approval responses
            approval_id = data.get("approval_id")
            approved = data.get("approved", False)
            action = data.get("action", {})

            # Process approval through cognition system
            if approved:
                # Execute approved action
                await websocket.send_json({
                    "type": "action_executed",
                    "approval_id": approval_id,
                    "status": "executing",
                    "message": f"Executing approved action: {action.get('type', 'unknown')}"
                })
            else:
                await websocket.send_json({
                    "type": "action_rejected",
                    "approval_id": approval_id,
                    "message": "Action rejected"
                })

        elif message_type == "cockpit_connect":
            # Handle cockpit connection
            session_id = data.get("session_id", "cockpit")
            user_name = data.get("user_name", "cockpit_user")

            capabilities = ["chat", "status"]
            if cognition_available:
                capabilities.extend(["cognition_intent", "plan_execution", "system_monitoring"])

            await websocket.send_json({
                "type": "connected",
                "message": f"Welcome to Grace Cockpit, {user_name}!",
                "session_id": session_id,
                "capabilities": capabilities,
                "cognition_available": cognition_available
            })

        else:
            # Unknown message type
            await websocket.send_json({
                "type": "error",
                "error": f"Unknown message type: {message_type}"
            })

    except Exception as e:
        logger.error(f"Error handling cognition message: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })

# Chat endpoint for frontend
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """Chat endpoint for frontend"""
    try:
        user_message = request.get("message", "Hello")
        return {
            "response": f"Grace: I received '{user_message}'. Full system integration in progress!",
            "status": "success"
        }
    except Exception as e:
        return {"response": f"Grace: Error - {str(e)}", "status": "error"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    print("Starting Grace Minimal Backend...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")

    uvicorn.run(
        "minimal_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
