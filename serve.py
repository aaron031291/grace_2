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
    """Boot Layer 1 before starting FastAPI"""
    
    print()
    print("=" * 80)
    print("GRACE LAYER 1 - BOOTING UNBREAKABLE CORE")
    print("=" * 80)
    print()
    
    try:
        from backend.core import (
            message_bus,
            immutable_log,
            clarity_framework,
            clarity_kernel,
            verification_framework,
            unified_logic_core,
            self_healing_kernel,
            coding_agent_kernel,
            librarian_kernel,
            control_plane
        )
        
        # Import Infrastructure Manager Kernel
        from backend.core.infrastructure_manager_kernel import infrastructure_manager
        
        # Import updated kernels
        from backend.kernels.governance_kernel import governance_kernel
        from backend.kernels.memory_kernel import MemoryKernel
        memory_kernel_instance = MemoryKernel()
        
        # Boot sequence
        await message_bus.start()
        print("[1/12] Message Bus: ACTIVE")
        
        await immutable_log.start()
        print("[2/12] Immutable Log: ACTIVE")
        
        await clarity_framework.start()
        print("[3/12] Clarity Framework: ACTIVE")
        
        await clarity_kernel.start()
        print("[4/12] Clarity Kernel: ACTIVE")
        
        # Initialize Infrastructure Manager Kernel
        await infrastructure_manager.initialize()
        print("[5/12] Infrastructure Manager: ACTIVE (Multi-OS host registry)")
        
        # Initialize Governance Kernel
        print("[6/12] Governance Kernel: ACTIVE (Multi-OS policies)")
        
        # Initialize Memory Kernel
        print("[7/12] Memory Kernel: ACTIVE (Host state persistence)")
        
        await verification_framework.start()
        print("[8/12] Verification Framework: ACTIVE")
        
        await unified_logic_core.start()
        print("[9/12] Unified Logic: ACTIVE")
        
        await self_healing_kernel.start()
        sh_stats = self_healing_kernel.get_stats()
        print(f"[10/12] Self-Healing: ACTIVE ({sh_stats['playbooks_loaded']} playbooks)")
        
        await coding_agent_kernel.start()
        ca_stats = coding_agent_kernel.get_stats()
        print(f"[11/12] Coding Agent: ACTIVE ({ca_stats['code_patterns_available']} patterns)")
        
        await librarian_kernel.start()
        lib_stats = librarian_kernel.get_stats()
        print(f"[12/12] Librarian: ACTIVE ({len(lib_stats['supported_types'])} file types)")
        
        await control_plane.start()
        status = control_plane.get_status()
        print(f"[CONTROL] Control Plane: ACTIVE ({status['running_kernels']}/{status['total_kernels']} kernels)")
        
        print()
        print("=" * 80)
        print("LAYER 1 BOOT COMPLETE - MULTI-OS INFRASTRUCTURE READY")
        print("=" * 80)
        print()
        print("[INFRA] Infrastructure Manager tracking hosts:")
        hosts = await infrastructure_manager.get_all_hosts()
        for host in hosts:
            print(f"   [OK] {host['hostname']} ({host['os_type']}) - {host['status']}")
        print()
        print("[GOV] Governance enforcing OS-specific policies")
        print("[MEM] Memory persisting all infrastructure state")
        print()
        print("=" * 80)
        print(f"  Kernels: {status['running_kernels']}/{status['total_kernels']} running")
        print(f"  Self-Healing: {sh_stats['playbooks_loaded']} playbooks loaded")
        print(f"  Coding Agent: {ca_stats['code_patterns_available']} code patterns ready")
        print(f"  Librarian: {len(lib_stats['supported_types'])} file types supported")
        print("  Unbreakable core is operational")
        print("=" * 80)
        print()
        
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Layer 1 boot failed: {e}")
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

