#!/usr/bin/env python3
"""
Grace Server - Layered Boot Sequence
Uses 6-layer structured initialization
"""

import asyncio
import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


async def boot_grace_layered():
    """
    Grace 6-Layer Boot Sequence
    
    Each layer builds on the previous:
    1. Foundation → 2. Guardrails → 3. Agentic → 4. Mission → 5. Capabilities → 6. APIs
    """
    
    from backend.core.layered_boot_orchestrator import (
        layered_boot_orchestrator,
        register_all_layers
    )
    
    # Register all 6 layers
    register_all_layers()
    
    # Execute boot
    boot_result = await layered_boot_orchestrator.execute_boot()
    
    if not boot_result['success']:
        print(f"\n❌ Boot failed at layer {boot_result.get('aborted_at_layer')}")
        print(f"   Reason: {boot_result.get('abort_reason')}")
        return None
    
    print(f"\n✅ All {boot_result['layers_completed']} layers booted successfully")
    print(f"   Total duration: {boot_result['total_duration_ms']:.0f}ms\n")
    
    return boot_result


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("   GRACE - Autonomous AI System (Layered Boot)")
    print("=" * 80)
    print()
    
    # Boot Grace with 6-layer sequence
    boot_result = asyncio.run(boot_grace_layered())
    
    if not boot_result:
        print("\n❌ Failed to boot Grace. Exiting.")
        if sys.stdin.isatty():
            input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Default port
    port = 8017
    
    # Try to get port from Guardian if available
    try:
        from backend.core.guardian import guardian
        if hasattr(guardian, 'allocated_port') and guardian.allocated_port:
            port = guardian.allocated_port
            print(f"[PORT] Using Guardian-allocated port: {port}")
    except:
        print(f"[PORT] Using default port: {port}")
    
    # Start server
    print("=" * 80)
    print("GRACE IS READY")
    print("=" * 80)
    print()
    print(f" 🌐 API:    http://localhost:{port}")
    print(f" 📚 Docs:   http://localhost:{port}/docs")
    print(f" 💚 Health: http://localhost:{port}/health")
    print()
    print("=" * 80)
    print("AVAILABLE ENDPOINTS")
    print("=" * 80)
    print()
    print("  Vault:    POST/GET /api/vault/secrets")
    print("  Chat:     POST /api/chat, POST /api/chat/upload")
    print("  Memory:   GET /api/memory/artifacts")
    print("  Missions: GET /mission-control/missions")
    print("  Logs:     GET /api/logs/recent, /api/logs/governance")
    print("  Learning: GET /api/learning/whitelist, /api/htm/tasks")
    print()
    print("=" * 80)
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Start server
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 Grace shutdown requested...")
        print("Goodbye!")
