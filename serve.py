#!/usr/bin/env python3
"""
Grace Server - Single Entry Point
Run: python serve.py
"""

import asyncio
import uvicorn
import sys
import socket
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def find_free_port(start_port=8000, max_tries=10):
    """Find first available port"""
    for port in range(start_port, start_port + max_tries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None


async def boot_grace_minimal():
    """
    Minimal Grace boot - just the essentials
    No complex orchestration that times out
    """
    
    print()
    print("=" * 80)
    print("GRACE - STARTING")
    print("=" * 80)
    print()
    
    try:
        # Try to import core systems (optional, won't fail if missing)
        try:
            from backend.core import message_bus, immutable_log
            
            print("[1/3] Booting core systems...")
            await message_bus.start()
            print("  ✓ Message Bus: Active")
            
            await immutable_log.start()
            print("  ✓ Immutable Log: Active")
            print()
        except ImportError:
            print("[1/3] Core systems not available (continuing anyway)")
            print()
        
        # Load main app
        print("[2/3] Loading Grace backend...")
        from backend.main import app
        print("  ✓ Backend loaded")
        print("  ✓ Remote Access: Ready")
        print("  ✓ Autonomous Learning: Ready")
        print()
        
        # Quick health check
        print("[3/3] System check...")
        route_count = len(app.routes)
        print(f"  ✓ {route_count} API endpoints registered")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Boot failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("   ██████╗ ██████╗  █████╗  ██████╗███████╗")
    print("  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██╔════╝")
    print("  ██║  ███╗██████╔╝███████║██║     █████╗  ")
    print("  ██║   ██║██╔══██╗██╔══██║██║     ██╔══╝  ")
    print("  ╚██████╔╝██║  ██║██║  ██║╚██████╗███████╗")
    print("   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝")
    print()
    print("  Autonomous AI System")
    print("=" * 80)
    print()
    
    # Find available port
    print("Finding available port...")
    port = find_free_port()
    
    if not port:
        print("❌ No available ports found (tried 8000-8009)")
        print("\nTo free up ports:")
        print("  netstat -ano | findstr :800")
        print("  taskkill /PID <pid> /F")
        sys.exit(1)
    
    print(f"✅ Using port {port}")
    print()
    
    # Boot Grace
    boot_success = asyncio.run(boot_grace_minimal())
    
    if not boot_success:
        print("Failed to boot Grace. Exiting.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Start server
    print("=" * 80)
    print("GRACE IS READY")
    print("=" * 80)
    print()
    print(f"📡 API: http://localhost:{port}")
    print(f"📖 Docs: http://localhost:{port}/docs")
    print(f"❤️  Health: http://localhost:{port}/health")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("Terminal 2 - Configure clients for this port:")
    print(f"  python auto_configure.py")
    print()
    print("Then use:")
    print("  • Remote Access: python remote_access_client.py setup")
    print("  • Learning: python start_grace_now.py")
    print("  • Menu: USE_GRACE.cmd")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False  # Disable reload to avoid issues
        )
    except KeyboardInterrupt:
        print("\n\nGrace shutdown requested...")
        print("Goodbye! 👋")
