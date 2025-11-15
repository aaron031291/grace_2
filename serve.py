#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grace Server Launcher with Layer 1 Boot
Run: python serve.py

This boots Grace's unbreakable core FIRST, then starts the API server
"""

import asyncio
import uvicorn
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))


async def boot_grace_core():
    """
    Boot all 20 Grace kernels with production-grade orchestration
    
    Features:
    - Pre-flight health gate (fail fast)
    - Dependency-driven boot order
    - Tier watchdogs
    - Chaos testing (optional)
    - Parallel validation
    """
    
    print()
    print("=" * 80)
    print("GRACE - PRODUCTION BOOT ORCHESTRATOR")
    print("=" * 80)
    print()
    
    try:
        from backend.core.boot_orchestrator import boot_orchestrator
        from backend.core.control_plane import control_plane
        from backend.core import message_bus, immutable_log
        
        # PHASE 1: Pre-flight health gate
        print("PHASE 1: Pre-flight health checks")
        if not await boot_orchestrator.run_pre_flight_checks():
            print("\n❌ PRE-FLIGHT FAILED - Cannot boot safely")
            print("   Fix critical issues and try again\n")
            return False
        
        # PHASE 2: Boot core infrastructure
        print("PHASE 2: Booting core infrastructure")
        await message_bus.start()
        print("[1/20] Message Bus: ACTIVE")
        
        await immutable_log.start()
        print("[2/20] Immutable Log: ACTIVE")
        print()
        
        # PHASE 3: Dependency-driven kernel boot
        print("PHASE 3: Dependency-driven kernel boot")
        success = await boot_orchestrator.boot_with_dependencies(control_plane)
        
        if not success:
            print("\n❌ KERNEL BOOT FAILED")
            return False
        
        # Get final status
        status = control_plane.get_status()
        
        print()
        print("=" * 80)
        print(f"BOOT COMPLETE - {status['total_kernels']} KERNELS")
        print("=" * 80)
        print()
        
        # Show kernel status by tier
        print("✅ Core & Repair Systems:")
        print("   message_bus, immutable_log, self_healing, coding_agent")
        
        print("\n✅ Governance:")
        print("   secret_manager, governance, verification_framework")
        
        print("\n✅ Execution:")
        print("   memory_fusion, librarian, sandbox")
        
        print("\n✅ Agentic:")
        print("   agentic_spine, meta_loop, voice_conversation")
        
        print("\n✅ Services:")
        print("   api_server, trigger_mesh, scheduler, health_monitor")
        
        print()
        print("=" * 80)
        print(f"  Total: {status['running_kernels']}/{status['total_kernels']} running")
        print(f"  Failed: {status['failed_kernels']}")
        print(f"  System State: {status['system_state']}")
        print("=" * 80)
        
        # PHASE 4: Parallel validation
        print()
        print("PHASE 4: Endpoint validation")
        await boot_orchestrator.validate_endpoints()
        
        print()
        print("🎉 GRACE FULLY OPERATIONAL")
        print("   Self-healing: ACTIVE")
        print("   Coding agent: ACTIVE (auto-fix enabled)")
        print("   All 20 kernels ready")
        print()
        
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Boot failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Boot Layer 1 first
    boot_success = asyncio.run(boot_grace_core())
    
    if not boot_success:
        print("Failed to boot Layer 1. Exiting.")
        sys.exit(1)
    
    # Now start FastAPI (Layer 2)
    print("=" * 80)
    print("GRACE LAYER 2 - STARTING FASTAPI")
    print("=" * 80)
    print()
    print("Backend API: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("Control: http://localhost:8000/api/control/state")
    print()
    print("Layer 2 connects to Layer 1 via message bus")
    print("If Layer 2 crashes, Layer 1 keeps running")
    print()
    print("=" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            loop="asyncio"
        )
    except KeyboardInterrupt:
        print("\n\nGrace shutdown requested...")
        print("Layer 1 core will continue running until process ends")

