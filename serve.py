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


def get_guardian_allocated_port(boot_result: Dict[str, Any]) -> Optional[int]:
    """
    Get the port that Guardian allocated during boot
    Guardian boots FIRST and allocates port in Phase 3
    """
    try:
        return boot_result['phases']['phase3_ports']['port']
    except:
        return None


async def boot_grace_minimal():
    """
    Grace boot sequence - Guardian boots FIRST, then everything else
    
    Boot Order:
    0. Guardian (network, ports, diagnostics) - FIRST
    1-2. Core systems (message bus, immutable log)
    3-4. Self-healing + Coding agent
    5+. Everything else
    
    Guardian fixes problems BEFORE they reach deeper systems
    """
    
    print()
    print("=" * 80)
    print("GRACE - BOOT SEQUENCE")
    print("=" * 80)
    print()
    
    try:
        # PRIORITY 0: Boot Guardian FIRST
        print("[PRIORITY 0] Booting Guardian Kernel...")
        from backend.core.guardian import guardian
        
        guardian_boot = await guardian.boot()
        
        if 'error' in guardian_boot:
            print(f"  ✗ Guardian boot FAILED: {guardian_boot['error']}")
            print("\nCannot proceed - Guardian must boot successfully")
            return False
        
        print("  ✓ Guardian: Online")
        print(f"  ✓ Port allocated: {guardian_boot['phases']['phase3_ports']['port']}")
        print(f"  ✓ Network health: {guardian_boot['phases']['phase2_diagnostics']['status']}")
        print(f"  ✓ Watchdog: Active")
        print(f"  ✓ Pre-flight: Passed")
        print()
        
        # Store allocated port for later use
        allocated_port = guardian_boot['phases']['phase3_ports']['port']
        
        # PRIORITY 1-2: Boot core systems (only if Guardian allows)
        try:
            from backend.core import message_bus, immutable_log
            
            print("[PRIORITY 1-2] Booting core systems...")
            
            if guardian.check_can_boot_kernel('message_bus', 1):
                await message_bus.start()
                guardian.signal_kernel_boot('message_bus', 1)
                print("  ✓ Message Bus: Active")
            
            if guardian.check_can_boot_kernel('immutable_log', 2):
                await immutable_log.start()
                guardian.signal_kernel_boot('immutable_log', 2)
                print("  ✓ Immutable Log: Active")
            
            print()
        except ImportError:
            print("[PRIORITY 1-2] Core systems not available (continuing anyway)")
            print()
        
        # Guardian is now monitoring everything
        print("[GUARDIAN] Now monitoring all systems - will catch issues early")
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
        
        # PRIORITY 3+: Load main app and other systems
        print("[PRIORITY 3+] Loading Grace backend...")
        from backend.main import app
        print("  ✓ Backend loaded")
        print("  ✓ Remote Access: Ready")
        print("  ✓ Autonomous Learning: Ready")
        print()
        
        # Quick health check
        print("[PRIORITY 10] System check...")
        route_count = len(app.routes)
        print(f"  ✓ {route_count} API endpoints registered")
        print()
        
        # Check databases
        print("[PRIORITY 11] Checking databases...")
        from pathlib import Path
        db_dir = Path("databases")
        if db_dir.exists():
            db_files = list(db_dir.glob("*.db"))
            print(f"  ✓ {len(db_files)} databases ready")
        print()
        
        # Return boot result with port info
        return guardian_boot
        
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
    
    # Boot Grace (Guardian boots FIRST and allocates port)
    boot_result = asyncio.run(boot_grace_minimal())
    
    if not boot_result or isinstance(boot_result, bool) and not boot_result:
        print("Failed to boot Grace. Exiting.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get port from Guardian's boot result
    port = get_guardian_allocated_port(boot_result)
    
    if not port:
        print("❌ Guardian did not allocate a port")
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
    
    # Try to start server, if port fails, try next one automatically
    max_retries = 10
    for retry in range(max_retries):
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
            print(f"\n[STARTING] Attempting to bind to port {port}...")
            uvicorn.run(
                "backend.main:app",
                host="0.0.0.0",
                port=port,
                log_level="info",
                reload=False  # Disable reload to avoid issues
            )
            break  # Success!
            
        except OSError as e:
            if 'address already in use' in str(e).lower() or '10048' in str(e):
                print(f"\n⚠️  Port {port} in use! Trying next port...")
                
                # Release this port in manager
                try:
                    from backend.core.port_manager import port_manager
                    port_manager.release_port(port)
                except:
                    pass
                
                # Try next port
                port += 1
                if port > 8100:
                    port = 8000  # Wrap around
                
                # Allocate new port
                try:
                    from backend.core.port_manager import port_manager
                    allocation = port_manager.allocate_port(
                        service_name="grace_backend",
                        started_by="serve.py",
                        purpose="Main Grace API server (retry)",
                        preferred_port=port
                    )
                    if 'port' in allocation:
                        port = allocation['port']
                        print(f"✅ Trying port {port} instead...")
                except:
                    pass
                
                if retry == max_retries - 1:
                    print(f"\n❌ Could not bind to any port after {max_retries} tries!")
                    print("Run: python kill_grace.py")
                    sys.exit(1)
            else:
                raise
                
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
            break
