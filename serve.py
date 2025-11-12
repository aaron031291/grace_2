#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Grace Server Launcher
Run: python serve.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Grace API Server")
    print("=" * 60)
    print("Backend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Clarity Status: http://localhost:8000/api/clarity/status")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        "backend.unified_grace_orchestrator:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        loop="asyncio"  # Windows compatibility
    )
