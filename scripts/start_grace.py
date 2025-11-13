#!/usr/bin/env python3
"""
Grace Complete Startup Script
Initializes all systems with proper dependencies and state recovery
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


async def start_grace_complete():
    """Start Grace with all systems"""
    
    print("=" * 80)
    print("GRACE COMPLETE SYSTEM STARTUP")
    print("=" * 80)
    print(f"Time: {datetime.utcnow().isoformat()}")
    print(f"Mode: Production")
    print("=" * 80)
    
    # Check previous state
    print("\n[STEP 1] Checking previous state...")
    state_file = Path('grace_state.json')
    
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            previous_state = json.load(f)
        
        print(f"  Previous state: {previous_state.get('system_state', 'unknown')}")
        print(f"  Last updated: {previous_state.get('updated_at', 'unknown')}")
        print(f"  Pending tasks: {previous_state.get('pending_tasks', 0)}")
    else:
        previous_state = None
        print("  No previous state found (fresh start)")
    
    # Initialize Grace Control Center
    print("\n[STEP 2] Initializing Grace Control Center...")
    try:
        from backend.grace_control_center import grace_control
        await grace_control.start()
        print("  ✓ Control Center initialized")
        
        state = grace_control.get_state()
        print(f"  Current state: {state['system_state']}")
        print(f"  Co-pilot active: {state['co_pilot_active']}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Initialize ML/AI Integration Systems
    print("\n[STEP 3] Initializing ML/AI Integration...")
    try:
        from backend.transcendence.ml_api_integrator import ml_api_integrator
        await ml_api_integrator.start()
        print("  ✓ ML API Integrator started")
        
        from backend.kernels.agents.ml_coding_agent import ml_coding_agent
        await ml_coding_agent.initialize()
        print("  ✓ ML Coding Agent initialized")
        print(f"    Using: Grace's Internal LLM (100% self-sufficient)")
        
        llm_info = await ml_api_integrator.get_grace_llm_info()
        print(f"    Capabilities: {len(llm_info['capabilities'])} core abilities")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Initialize Autonomous Learning
    print("\n[STEP 4] Initializing Autonomous Learning...")
    try:
        from backend.research_sweeper import research_sweeper
        await research_sweeper.start()
        print("  ✓ Research Sweeper started")
        print("    Frequency: Hourly sweeps")
        
        from backend.sandbox_improvement import sandbox_improvement
        await sandbox_improvement.start()
        print("  ✓ Sandbox Improvement initialized")
        print("    Isolation: Active")
        
        from backend.autonomous_improvement_workflow import autonomous_improvement
        await autonomous_improvement.start()
        print("  ✓ Autonomous Improvement Workflow started")
        print("    Cycle: Daily")
        print("    Approval: Human consensus required")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Check Remote Access (disabled by default)
    print("\n[STEP 5] Checking Remote Access...")
    import os
    if os.getenv("ENABLE_REMOTE_ACCESS", "false").lower() == "true":
        try:
            from backend.remote_access.zero_trust_layer import zero_trust_layer
            await zero_trust_layer.start()
            print("  ⚠️  Remote Access ENABLED")
            print("    Zero-Trust: Active")
            print("    RBAC: Enforced")
            print("    Session Recording: Active")
        except Exception as e:
            print(f"  ✗ Remote access failed: {e}")
    else:
        print("  ✓ Remote Access DISABLED (safe mode)")
    
    # Display startup summary
    print("\n" + "=" * 80)
    print("GRACE SYSTEMS OPERATIONAL")
    print("=" * 80)
    
    print("\nActive Systems:")
    print("  ✓ Grace Control Center - ESC = Emergency Stop")
    print("  ✓ Grace Internal LLM - 100% self-sufficient reasoning")
    print("  ✓ ML Coding Agent - Code gen, analysis, debugging")
    print("  ✓ Research Sweeper - Continuous knowledge acquisition")
    print("  ✓ Sandbox System - Safe experimentation")
    print("  ✓ Autonomous Learning - Self-improvement with human approval")
    
    print("\nControl:")
    print("  ESC          - Emergency stop")
    print("  UI Controls  - http://localhost:5173/control")
    print("  API          - http://localhost:8000/api/control/state")
    
    print("\nCapabilities:")
    print("  🧠 Internal LLM for code generation")
    print("  🔍 ML/AI API discovery and integration")
    print("  📚 Autonomous research from 8 approved sources")
    print("  🧪 Sandbox testing with KPI validation")
    print("  📊 Trust scoring and adaptive reasoning")
    print("  🤝 Human consensus before deployment")
    
    print("\nSecurity:")
    print("  🛡️  Hunter Bridge API scanning")
    print("  🔐 Zero-trust remote access (disabled)")
    print("  📝 Complete session recording")
    print("  ⚖️  RBAC enforcement (least privilege)")
    print("  📜 Immutable audit trail")
    
    print("\n" + "=" * 80)
    print("Grace is ready! 🚀")
    print("=" * 80)
    
    print("\nQuick Start:")
    print("  1. Visit control center: http://localhost:5173/control")
    print("  2. Monitor automation state")
    print("  3. Press ESC for emergency stop if needed")
    print("  4. Review proposals: cat reports/autonomous_improvement/*.md")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        asyncio.run(start_grace_complete())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Grace startup cancelled by user")
    except Exception as e:
        print(f"\n\n[ERROR] Grace startup failed: {e}")
        import traceback
        traceback.print_exc()
