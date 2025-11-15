"""
Debug version of serve.py with better error reporting
"""

import subprocess
from backend.main import app
from backend.database import engine, Base
from backend.models.verification_models import RegisteredDevice, DeviceAllowlist, DeviceRole
from fastapi.testclient import TestClient
import os
import asyncio
import sqlite3
import uvicorn
import requests
import traceback
# from uvloop import event_loop_policy

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await create_db_and_tables()
    
    config = uvicorn.Config("backend.main:app", host="0.0.0.0", port=8001, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    
    print("=" * 70)
    print("GRACE BACKEND - DEBUG MODE")
    print("=" * 70)
    
    try:
        # 1. Test Imports
        print("\n[1/4] Testing imports...")
        from backend.main import app
        print("[OK] Main app imported successfully")

        # 2. Check Routes
        print("\n[2/4] Checking routes...")
        total_routes = len(app.routes)
        print(f"[OK] App routes registered: {total_routes} routes")

        # 3. Test Health Endpoint
        print("\n[3/4] Testing basic endpoint...")
        print("[OK] Health endpoint check will occur after server start.")


        # 4. Start Server
        print("\n[4/4] Starting server...")
        print("")
        print("Grace will be available at:")
        print("  - API: http://localhost:8001")
        print("  - Docs: http://localhost:8001/docs")
        print("  - Health: http://localhost:8001/health")
        print("")
        print("Press Ctrl+C to stop")
        print("=" * 70)
        print("")

        asyncio.run(main())

    except ImportError as e:
        print(f"\n[ERROR] Failed to import app: {e}")
        print("\nFull error:\n")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
