#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grace API Server - Factory Pattern
Clean architecture with no circular imports
Run: python serve_factory.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Grace API Server (Factory Pattern)")
    print("=" * 60)
    print("Backend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    print("\nClean Architecture - No Circular Imports\n")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "backend.app_factory:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
        loop="asyncio"  # Windows compatibility
    )
