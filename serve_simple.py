"""
Simple Grace Server - No Boot Orchestration
Just starts the API server directly
"""

import uvicorn
import sys
from pathlib import Path

print("\n" + "="*70)
print("GRACE - SIMPLE START MODE")
print("="*70)
print()
print("Skipping Layer 1 boot orchestration...")
print("Starting FastAPI server directly...")
print()
print("Backend API: http://localhost:8000")
print("API Docs: http://localhost:8000/docs")
print("Health: http://localhost:8000/health")
print()
print("Available Features:")
print("  ✅ Remote Access API")
print("  ✅ Autonomous Learning API")
print("  ✅ Health Endpoints")
print()
print("Press Ctrl+C to stop")
print("="*70)
print()

if __name__ == "__main__":
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to avoid issues
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
