"""
Grace Master Control Panel
Unified interface to control all of Grace's systems
"""

import asyncio
import sys
from datetime import datetime


def print_banner():
    """Print banner"""
    print("\n" + "="*80)
    print("🤖 GRACE MASTER CONTROL PANEL")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


def print_menu():
    """Print main menu"""
    print("📋 CONTROL OPTIONS:\n")
    
    print("🎮 INTERFACES:")
    print("  1. Terminal Control  - Chat & monitor (simple)")
    print("  2. Visual Dashboard  - Real-time monitoring (advanced)")
    print("  3. Web UI           - Browser interface")
    print()
    
    print("🚀 SYSTEM CONTROL:")
    print("  4. Start Backend    - Start Grace's backend server")
    print("  5. Start Frontend   - Start web interface")
    print("  6. Start Both       - Start backend + frontend")
    print()
    
    print("🎓 LEARNING:")
    print("  7. Demo Web Learning       - See Grace learn from internet")
    print("  8. Run Tests              - Test all systems")
    print()
    
    print("📊 STATUS & LOGS:")
    print("  9. View Logs        - Monitor Grace's activities")
    print("  10. Check Status    - System health check")
    print()
    
    print("🛑 EXIT:")
    print("  Q. Quit")
    print()
    print("="*80)


def main():
    """Main control loop"""
    
    print_banner()
    
    while True:
        print_menu()
        
        choice = input("Select option: ").strip().upper()
        
        if choice == '1':
            print("\n🎮 Starting Terminal Control...")
            print("="*80)
            import subprocess
            subprocess.run([sys.executable, "grace_terminal_control.py"])
            
        elif choice == '2':
            print("\n📊 Starting Visual Dashboard...")
            print("="*80)
            import subprocess
            subprocess.run([sys.executable, "grace_monitor_dashboard.py"])
            
        elif choice == '3':
            print("\n🌐 Starting Web UI...")
            print("="*80)
            print("Backend will be available at: http://localhost:8000")
            print("Frontend will be available at: http://localhost:5173")
            print("\nStarting both servers...")
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["start_both.bat"], shell=True)
            else:
                print("Please run: ./start_both.sh")
            
        elif choice == '4':
            print("\n🚀 Starting Backend...")
            print("="*80)
            print("Backend will be available at: http://localhost:8000")
            print("API Docs: http://localhost:8000/docs")
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["restart_backend.bat"], shell=True)
            else:
                subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"])
            
        elif choice == '5':
            print("\n🎨 Starting Frontend...")
            print("="*80)
            print("Frontend will be available at: http://localhost:5173")
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["cd", "frontend", "&&", "npm", "run", "dev"], shell=True)
            else:
                subprocess.run(["npm", "run", "dev"], cwd="frontend")
            
        elif choice == '6':
            print("\n🚀 Starting Backend + Frontend...")
            print("="*80)
            print("Backend: http://localhost:8000")
            print("Frontend: http://localhost:5173")
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["start_both.bat"], shell=True)
            else:
                print("Please run: ./start_both.sh")
            
        elif choice == '7':
            print("\n🎓 Running Web Learning Demo...")
            print("="*80)
            import subprocess
            subprocess.run([sys.executable, "demo_web_learning.py"])
            
        elif choice == '8':
            print("\n🧪 Running All Tests...")
            print("="*80)
            import subprocess
            subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
            
        elif choice == '9':
            print("\n📋 Viewing Logs...")
            print("="*80)
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["view_logs.bat"], shell=True)
            else:
                subprocess.run(["tail", "-f", "logs/grace.log"])
            
        elif choice == '10':
            print("\n📊 Checking System Status...")
            print("="*80)
            print_status()
            input("\nPress Enter to continue...")
            
        elif choice == 'Q':
            print("\n👋 Goodbye!\n")
            break
            
        else:
            print("\n❌ Invalid option. Please try again.\n")
            input("Press Enter to continue...")
        
        print("\n")


def print_status():
    """Print system status"""
    import os
    from pathlib import Path
    
    print("\n🔍 GRACE SYSTEM STATUS\n")
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend: ONLINE (http://localhost:8000)")
        else:
            print("⚠️  Backend: RESPONDING (non-200 status)")
    except:
        print("❌ Backend: OFFLINE")
    
    # Check if frontend is accessible
    try:
        import requests
        response = requests.get("http://localhost:5173", timeout=2)
        if response.status_code in [200, 404]:  # 404 is ok for SPA
            print("✅ Frontend: ONLINE (http://localhost:5173)")
        else:
            print("⚠️  Frontend: RESPONDING")
    except:
        print("❌ Frontend: OFFLINE")
    
    # Check database
    db_path = Path("backend/grace.db")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ Database: EXISTS ({size_mb:.2f} MB)")
    else:
        print("❌ Database: NOT FOUND")
    
    # Check storage directories
    storage_path = Path("storage")
    if storage_path.exists():
        print(f"✅ Storage: EXISTS")
        
        # Check provenance
        prov_path = storage_path / "provenance"
        if prov_path.exists():
            prov_files = len(list(prov_path.glob("*.json")))
            print(f"   📋 Provenance files: {prov_files}")
        
        # Check web knowledge
        web_path = storage_path / "web_knowledge"
        if web_path.exists():
            web_files = len(list(web_path.glob("*.json")))
            print(f"   🌐 Web knowledge files: {web_files}")
    else:
        print("⚠️  Storage: NOT FOUND")
    
    # Check logs
    logs_path = Path("logs")
    if logs_path.exists():
        log_files = len(list(logs_path.glob("*.log")))
        print(f"✅ Logs: {log_files} files")
    else:
        print("⚠️  Logs: NOT FOUND")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
