#!/usr/bin/env python3
"""Grace - Autonomous AI System CLI"""

import os
import sys
import subprocess
import argparse
import asyncio
from pathlib import Path

GRACE_ROOT = Path(__file__).parent
BACKEND_DIR = GRACE_ROOT / "backend"
FRONTEND_DIR = GRACE_ROOT / "grace-frontend"
SANDBOX_DIR = GRACE_ROOT / "sandbox"

def install():
    """Install Grace dependencies"""
    print("📦 Installing Grace...")
    
    print("\n1️⃣ Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=GRACE_ROOT)
    
    print("\n2️⃣ Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True)
    
    print("\n3️⃣ Initializing database...")
    subprocess.run([sys.executable, "reset_db.py"], cwd=GRACE_ROOT)
    
    print("\n✅ Grace installed successfully!")
    print("Run: grace start")

def start():
    """Start Grace services"""
    print("🚀 Starting Grace...")
    
    print("\n1️⃣ Starting backend (http://localhost:8000)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"],
        cwd=GRACE_ROOT
    )
    
    print("\n2️⃣ Starting frontend (http://localhost:5173)...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True
    )
    
    print("\n✅ Grace is running!")
    print("   Backend:  http://localhost:8000/docs")
    print("   Frontend: http://localhost:5173")
    print("   Press Ctrl+C to stop")
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping Grace...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ Grace stopped")

def status():
    """Check Grace service status"""
    print("📊 Grace Status\n")
    
    try:
        import requests
        
        backend_status = requests.get("http://localhost:8000/health", timeout=2)
        print("✅ Backend: Running")
        
        health = requests.get("http://localhost:8000/api/health/status", timeout=2).json()
        print(f"   Mode: {health.get('system_mode', 'unknown')}")
        
        for check in health.get('checks', [])[:4]:
            status_icon = "✅" if check['status'] == 'ok' else "❌"
            print(f"   {status_icon} {check['component']}: {check['status']}")
    except:
        print("❌ Backend: Not running")
    
    try:
        import requests
        requests.get("http://localhost:5173", timeout=2)
        print("✅ Frontend: Running")
    except:
        print("❌ Frontend: Not running")

def sandbox_reset():
    """Reset sandbox environment"""
    print("🧹 Resetting sandbox...")
    
    try:
        import requests
        token = input("Enter your auth token (or press Enter to use stored): ").strip()
        if not token:
            token = Path(GRACE_ROOT / ".token").read_text().strip() if Path(GRACE_ROOT / ".token").exists() else ""
        
        if not token:
            print("❌ No token provided. Login first.")
            return
        
        response = requests.post(
            "http://localhost:8000/api/sandbox/reset",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ Sandbox reset: {data.get('files_deleted', 0)} files deleted")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def upgrade():
    """Upgrade Grace to latest version"""
    print("⬆️ Upgrading Grace...")
    
    print("\n1️⃣ Pulling latest code...")
    subprocess.run(["git", "pull"], cwd=GRACE_ROOT)
    
    print("\n2️⃣ Updating backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"], cwd=GRACE_ROOT)
    
    print("\n3️⃣ Updating frontend dependencies...")
    subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True)
    
    print("\n4️⃣ Running migrations...")
    print("   (Database migrations will be added in future version)")
    
    print("\n✅ Grace upgraded!")

def main():
    parser = argparse.ArgumentParser(
        description="Grace - Autonomous AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('install', help='Install Grace dependencies')
    subparsers.add_parser('start', help='Start Grace services')
    subparsers.add_parser('status', help='Check service status')
    subparsers.add_parser('sandbox', help='Reset sandbox environment').add_argument('action', choices=['reset'])
    subparsers.add_parser('upgrade', help='Upgrade Grace')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'install':
        install()
    elif args.command == 'start':
        start()
    elif args.command == 'status':
        status()
    elif args.command == 'sandbox':
        sandbox_reset()
    elif args.command == 'upgrade':
        upgrade()

if __name__ == "__main__":
    main()
