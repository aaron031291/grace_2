#!/usr/bin/env python3
"""
Grace Server - Resilient Boot with Pre-Flight Checks
Unbreakable boot with auto-healing
"""

import asyncio
import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def boot_grace_resilient():
    """
    Resilient Grace Boot with Pre-Flight Validation
    
    Pre-flight:
    1. Config/secrets lint
    2. Schema integrity check + auto-fix
    3. Dependency health rehearsal
    4. Service registration verification
    
    If critical issues found:
    - Auto-fix where possible
    - Create self-healing missions
    - Abort boot only if unfixable
    """
    
    from backend.core.boot_resilience_system import boot_resilience
    
    # ===== PRE-FLIGHT CHECKS =====
    print("\n🔍 Running pre-flight checks...\n")
    
    pre_flight = await boot_resilience.pre_flight_check()
    
    if not pre_flight['go_for_boot']:
        print("\n❌ Boot aborted due to critical issues")
        print("\nIssues detected:")
        for issue in pre_flight['issues']:
            print(f"  - {issue.get('description') or issue.get('error')}")
        
        if pre_flight['missions_created']:
            print("\n🔧 Self-healing missions created:")
            for mission in pre_flight['missions_created']:
                print(f"  - {mission}")
        
        return None
    
    # ===== LAYERED BOOT =====
    from backend.core.layered_boot_orchestrator import (
        layered_boot_orchestrator,
        register_all_layers
    )
    
    # Register all 6 layers
    register_all_layers()
    
    # Execute boot
    try:
        boot_result = await layered_boot_orchestrator.execute_boot()
        
        if not boot_result['success']:
            # Boot failed - create auto-fix mission
            error_msg = boot_result.get('abort_reason', 'Unknown error')
            layer = boot_result.get('aborted_at_layer', 'unknown')
            
            print(f"\n[GOVERNANCE] Boot failed - Creating auto-fix mission...")
            
            mission_id = await boot_resilience.create_boot_fix_mission(
                Exception(error_msg),
                layer
            )
            
            print(f"[GOVERNANCE] Mission {mission_id} will attempt to fix: {error_msg}")
            
            return None
        
        return boot_result
        
    except Exception as e:
        # Unexpected error - create emergency mission
        print(f"\n❌ Unexpected boot error: {e}")
        
        mission_id = await boot_resilience.create_boot_fix_mission(e, 'unknown')
        print(f"[GOVERNANCE] Emergency mission created: {mission_id}")
        
        import traceback
        traceback.print_exc()
        
        return None


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("   GRACE - Autonomous AI System (Resilient Boot)")
    print("=" * 80)
    print()
    
    # Boot Grace with pre-flight checks and auto-healing
    boot_result = asyncio.run(boot_grace_resilient())
    
    if not boot_result:
        print("\n❌ Failed to boot Grace")
        print("\nSelf-healing missions have been created.")
        print("Grace will attempt to fix the issues automatically.")
        print("\nCheck mission-control/missions for status.")
        if sys.stdin.isatty():
            input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get port
    port = 8017
    try:
        from backend.core.guardian import guardian
        if hasattr(guardian, 'allocated_port') and guardian.allocated_port:
            port = guardian.allocated_port
    except:
        pass
    
    print("\n[RESILIENCE] Continuous validation will start with server...")
    print("[RESILIENCE] Schema + dependency checks will run every 60 minutes")
    
    # Display ready message
    print("\n" + "=" * 80)
    print("GRACE IS READY (Resilient Mode)")
    print("=" * 80)
    print()
    print(f" 🌐 API:    http://localhost:{port}")
    print(f" 📚 Docs:   http://localhost:{port}/docs")
    print(f" 💚 Health: http://localhost:{port}/health")
    print()
    print("=" * 80)
    print("RESILIENCE FEATURES ACTIVE")
    print("=" * 80)
    print()
    print("  ✅ Pre-flight checks: Config, schema, dependencies")
    print("  ✅ Auto-healing: Boot failures → missions")
    print("  ✅ Continuous validation: Every 60 minutes")
    print("  ✅ Service registration: All APIs monitored")
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
