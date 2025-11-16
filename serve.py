"""
Grace Backend Server Launcher

Starts the FastAPI backend with proper configuration
"""

import uvicorn
import os

if __name__ == "__main__":
    # Configuration
    host = os.getenv("GRACE_HOST", "0.0.0.0")
    port = int(os.getenv("GRACE_PORT", "8000"))
    reload = os.getenv("GRACE_RELOAD", "true").lower() == "true"
    
    print(f"Starting Grace Backend on {host}:{port}")
    print(f"Reload: {reload}")
    print("=" * 60)
    
    # Start server
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )