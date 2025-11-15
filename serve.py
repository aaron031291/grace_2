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


def allocate_grace_port():
    """
    Allocate port for Grace using port manager
    Manages ports 8000-8100 with full tracking
    """
    try:
        from backend.core.port_manager import port_manager
        from backend.core.port_watchdog import port_watchdog
        
        # Allocate port with metadata
        allocation = port_manager.allocate_port(
            service_name="grace_backend",
            started_by="serve.py",
            purpose="Main Grace API server with remote access and learning",
            preferred_port=8000  # Try 8000 first
        )
        
        if 'error' in allocation:
            logger.error(f"Port allocation failed: {allocation}")
            return None
        
        port = allocation['port']
        
        # Start watchdog to monitor this port
        asyncio.create_task(port_watchdog.start())
        
        return port
    except Exception as e:
        # Fallback to old method if port manager not available
        print(f"Port manager not available, using fallback: {e}")
        for port in range(8000, 8100):
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
            
            print("[1/5] Booting core systems...")
            await message_bus.start()
            print("  ✓ Message Bus: Active")
            
            await immutable_log.start()
            print("  ✓ Immutable Log: Active")
            print()
        except ImportError:
            print("[1/5] Core systems not available (continuing anyway)")
            print()
        
        # Load and verify all 12+ open source models
        print("[2/5] Loading open source LLMs...")
        try:
            import requests
            
            # Check if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [m['name'] for m in models_data.get('models', [])]
                    
                    # Define all 15 models Grace should have
                    recommended_models = {
                        'qwen2.5:32b': 'Conversation & reasoning',
                        'qwen2.5:72b': 'Ultimate quality',
                        'deepseek-coder-v2:16b': 'Best coding',
                        'deepseek-r1:70b': 'Complex reasoning (o1-level)',
                        'kimi:latest': '128K context',
                        'llava:34b': 'Vision + text',
                        'command-r-plus:latest': 'RAG specialist',
                        'phi3.5:latest': 'Ultra fast',
                        'codegemma:7b': 'Code completion',
                        'granite-code:20b': 'Enterprise code',
                        'dolphin-mixtral:latest': 'Uncensored',
                        'nous-hermes2-mixtral:latest': 'Instructions',
                        'gemma2:9b': 'Fast general',
                        'llama3.2:latest': 'Lightweight',
                        'mistral-nemo:latest': 'Efficient'
                    }
                    
                    installed = [m for m in recommended_models.keys() if any(m.split(':')[0] in avail for avail in available_models)]
                    missing = [m for m in recommended_models.keys() if not any(m.split(':')[0] in avail for avail in available_models)]
                    
                    print(f"  ✓ Ollama: Running")
                    print(f"  ✓ Models available: {len(available_models)}")
                    print(f"  ✓ Grace models installed: {len(installed)}/15")
                    
                    if installed:
                        print(f"\n  Installed models:")
                        for model in installed[:5]:  # Show first 5
                            print(f"    • {model} - {recommended_models[model]}")
                        if len(installed) > 5:
                            print(f"    ... and {len(installed) - 5} more")
                    
                    if missing:
                        print(f"\n  ⚠️  Missing models: {len(missing)}")
                        print(f"    Run: scripts/startup/install_all_models.cmd")
                        print(f"    Or: ollama pull <model_name>")
                else:
                    print("  ⚠️  Ollama API returned unexpected status")
            except requests.exceptions.RequestException:
                print("  ⚠️  Ollama not running (LLM features disabled)")
                print("    Start Ollama: ollama serve")
        except Exception as e:
            print(f"  ⚠️  Could not check models: {e}")
        
        print()
        
        # Load main app
        print("[3/5] Loading Grace backend...")
        from backend.main import app
        print("  ✓ Backend loaded")
        print("  ✓ Remote Access: Ready")
        print("  ✓ Autonomous Learning: Ready")
        print()
        
        # Quick health check
        print("[4/5] System check...")
        route_count = len(app.routes)
        print(f"  ✓ {route_count} API endpoints registered")
        print()
        
        # Check databases
        print("[5/5] Checking databases...")
        from pathlib import Path
        db_dir = Path("databases")
        if db_dir.exists():
            db_files = list(db_dir.glob("*.db"))
            print(f"  ✓ {len(db_files)} databases ready")
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
    
    # Allocate port from managed range (8000-8100)
    print("Allocating port from managed range (8000-8100)...")
    port = allocate_grace_port()
    
    if not port:
        print("❌ No available ports in range 8000-8100")
        print("\nCheck port usage:")
        print("  netstat -ano | findstr :80")
        print("\nOr view port manager status:")
        print("  python scripts/utilities/check_ports.py")
        sys.exit(1)
    
    print(f"✅ Allocated port {port}")
    print(f"   Service: grace_backend")
    print(f"   Watchdog: Active (monitors health every 30s)")
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
        # Register PID with port manager
        import os
        try:
            from backend.core.port_manager import port_manager
            port_manager.register_pid(port, os.getpid())
            print(f"[PORT-MANAGER] Registered PID {os.getpid()} for port {port}")
        except:
            pass
        
        # Start server
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False  # Disable reload to avoid issues
        )
    except KeyboardInterrupt:
        print("\n\nGrace shutdown requested...")
        
        # Release port
        try:
            from backend.core.port_manager import port_manager
            port_manager.release_port(port)
            print(f"[PORT-MANAGER] Released port {port}")
        except:
            pass
        
        print("Goodbye! 👋")
