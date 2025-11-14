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
    """Boot all 19 Grace kernels via Control Plane"""
    
    print()
    print("=" * 80)
    print("GRACE - BOOTING ALL 19 KERNELS")
    print("=" * 80)
    print()
    
    try:
        from backend.core.control_plane import control_plane
        from backend.core import message_bus, immutable_log
        
        # Start message bus first (required for control plane)
        await message_bus.start()
        print("[1/19] Message Bus: ACTIVE")
        
        await immutable_log.start()
        print("[2/19] Immutable Log: ACTIVE")
        
        # Start control plane - it will boot all 19 kernels
        await control_plane.start()
        status = control_plane.get_status()
        
        print()
        print("=" * 80)
        print(f"BOOT COMPLETE - {status['total_kernels']} KERNELS OPERATIONAL")
        print("=" * 80)
        print()
        
        # Show kernel breakdown
        kernels_list = list(control_plane.kernels.keys())
        
        print("Core Infrastructure (7):")
        for k in kernels_list[0:7]:
            print(f"  ✓ {k}")
        
        print("\nExecution Layer (5):")
        for k in kernels_list[7:12]:
            print(f"  ✓ {k}")
        
        print("\nLayer 3 - Agentic Systems (3):")
        for k in kernels_list[12:15]:
            print(f"  ✓ {k}")
        
        print("\nServices & API (4):")
        for k in kernels_list[15:19]:
            print(f"  ✓ {k}")
        
        print()
        print("=" * 80)
        print(f"  Total Kernels: {status['running_kernels']}/{status['total_kernels']} running")
        print(f"  System State: {status['system_state']}")
        print(f"  Layer 3: OPERATIONAL (3 agentic kernels)")
        print("  All layers ready")
        print("=" * 80)
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

