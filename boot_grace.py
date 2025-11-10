#!/usr/bin/env python3
"""
Simple Grace Boot Script
"""

import subprocess
import sys
import os
import time

def kill_existing():
    """Kill existing Python processes"""
    try:
        if os.name == 'nt':  # Windows
            os.system('taskkill /F /IM python.exe 2>nul')
        time.sleep(2)
    except:
        pass

def start_grace():
    """Start Grace backend"""
    print("🚀 Starting Grace AI Platform...")
    
    # Kill existing processes
    kill_existing()
    
    # Start backend
    try:
        print("Starting backend on http://localhost:8000")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--reload",
            "--port", "8000",
            "--host", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n✅ Grace stopped")
    except Exception as e:
        print(f"❌ Error starting Grace: {e}")

if __name__ == "__main__":
    start_grace()