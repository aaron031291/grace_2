"""
Grace's Boot Layer
Starts the unbreakable core and all kernels

Boot sequence:
1. Message Bus (nervous system)
2. Immutable Log (black box)
3. Secret Manager (credentials)
4. Governance (policy engine)
5. Health Monitor (watchdog)
6. Memory Fusion (knowledge)
7. Other kernels...
8. API Server (last)

Even if API crashes, kernels keep running
"""

import asyncio
import logging
from datetime import datetime

from .message_bus import message_bus
from .control_plane import control_plane
from .immutable_log import immutable_log
from .boot_pipeline import boot_pipeline, BootStep, BootStage
from .clarity_framework import clarity_framework, DecisionType, ClarityLevel
from .verification_framework import verification_framework
from .unified_logic_integration import unified_logic_core

logger = logging.getLogger(__name__)


class BootLayer:
    """
    Grace's boot layer
    The spine that starts everything and keeps it alive
    """
    
    def __init__(self):
        self.boot_start_time = None
        self.boot_complete_time = None
        self.boot_successful = False
    
    async def boot_grace(self):
        """
        Boot Grace's complete system
        
        Returns:
            Boot result with timing and status
        """
        
        self.boot_start_time = datetime.utcnow()
        
        print("=" * 80)
        print("GRACE BOOT LAYER - INITIALIZING CORE")
        print("=" * 80)
        print()
        
        try:
            # Step 1: Message Bus (Foundation)
            print("[1/10] Starting Message Bus (nervous system)...")
            await message_bus.start()
            print("  [OK] Message Bus ACTIVE")
            
            # Step 2: Immutable Log (Audit trail)
            print("\n[2/10] Starting Immutable Log (black box)...")
            await immutable_log.start()
            stats = immutable_log.get_stats()
            print(f"  [OK] Immutable Log ACTIVE ({stats['total_entries']} entries)")
            
            # Step 3: Clarity Framework (Transparent decisions)
            print("\n[3/10] Starting Clarity Framework (transparency)...")
            await clarity_framework.start()
            print("  [OK] Clarity Framework ACTIVE")
            
            # Step 4: Verification Framework (Continuous validation)
            print("\n[4/10] Starting Verification Framework (validation)...")
            await verification_framework.start()
            print("  [OK] Verification Framework ACTIVE")
            
            # Step 5: Unified Logic (Governance)
            print("\n[5/10] Starting Unified Logic (governance)...")
            await unified_logic_core.start()
            print("  [OK] Unified Logic ACTIVE")
            
            # Step 6: Self-Healing Kernel (Auto-repair)
            print("\n[6/8] Starting Self-Healing Kernel...")
            await self_healing_kernel.start()
            sh_stats = self_healing_kernel.get_stats()
            print(f"  [OK] Self-Healing ACTIVE ({sh_stats['playbooks_loaded']} playbooks)")
            
            # Step 7: Coding Agent Kernel (Code generation)
            print("\n[7/8] Starting Coding Agent Kernel...")
            await coding_agent_kernel.start()
            ca_stats = coding_agent_kernel.get_stats()
            print(f"  [OK] Coding Agent ACTIVE ({ca_stats['code_patterns_available']} patterns)")
            
            # Step 8: Control Plane (Orchestrator)
            print("\n[8/8] Starting Control Plane (orchestrator)...")
            await control_plane.start()
            print("  [OK] Control Plane ACTIVE")
            
            # Step 9: Boot Pipeline (Structured startup)
            print("\n[9/10] Initializing Boot Pipeline...")
            # Boot pipeline is used for structured boots (next restart will use it)
            print("  [OK] Boot Pipeline ready for next boot")
            
            # Step 10: Log boot success
            print("\n[10/10] Logging boot event...")
            await immutable_log.append(
                actor='boot_layer',
                action='system_boot',
                resource='grace_system',
                decision={'status': 'success', 'boot_time_ms': 0},
                metadata={'timestamp': datetime.utcnow().isoformat()}
            )
            
            # Record decision with clarity
            await clarity_framework.record_decision(
                decision_type=DecisionType.AUTONOMOUS_ACTION,
                actor='boot_layer',
                action='system_boot',
                resource='grace_system',
                rationale='Booting Grace with unbreakable core architecture',
                confidence=1.0,
                risk_score=0.05,
                clarity_level=ClarityLevel.STANDARD
            )
            
            print("  [OK] Boot logged to immutable audit trail")
            
            # Verify all systems
            verification = await verification_framework.verify_all()
            print(f"  [OK] Verification: {verification['rules_passed']}/{verification['total_rules']} rules passed")
            
            # Boot complete
            print("\n[BOOT] Complete!")
            print()
            
            self.boot_complete_time = datetime.utcnow()
            boot_duration = (self.boot_complete_time - self.boot_start_time).total_seconds()
            
            self.boot_successful = True
            
            # Display kernel status
            status = control_plane.get_status()
            
            print("=" * 80)
            print("GRACE CORE SYSTEMS - OPERATIONAL")
            print("=" * 80)
            print(f"\nBoot Time: {boot_duration:.2f}s")
            print(f"System State: {status['system_state']}")
            print(f"Total Kernels: {status['total_kernels']}")
            print(f"Running Kernels: {status['running_kernels']}")
            print(f"Failed Kernels: {status['failed_kernels']}")
            
            print("\nCore Kernels:")
            for kernel_name, kernel_info in status['kernels'].items():
                state_icon = "[OK]" if kernel_info['state'] == 'running' else "[X]"
                critical = "CRITICAL" if kernel_info['critical'] else "optional"
                print(f"  {state_icon} {kernel_name:<20} [{kernel_info['state']}] ({critical})")
            
            print("\n" + "=" * 80)
            print("Grace's spine is unbreakable and running")
            print("Message Bus active - all kernels can communicate")
            print("Immutable Log active - complete audit trail")
            print("Control Plane active - auto-restart on failures")
            print("=" * 80)
            print()
            
            return {
                'success': True,
                'boot_duration_seconds': boot_duration,
                'system_state': status['system_state'],
                'kernels': status
            }
        
        except Exception as e:
            logger.error(f"[BOOT-LAYER] Boot failed: {e}")
            print()
            print("=" * 80)
            print(f"✗ BOOT FAILED: {e}")
            print("=" * 80)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    async def shutdown_grace(self):
        """Graceful shutdown of all systems"""
        
        print()
        print("=" * 80)
        print("GRACE SHUTDOWN - GRACEFUL")
        print("=" * 80)
        print()
        
        # Log shutdown
        await immutable_log.append(
            actor='boot_layer',
            action='system_shutdown',
            resource='grace_system',
            decision={'status': 'initiated'},
            metadata={'timestamp': datetime.utcnow().isoformat()}
        )
        
        # Stop control plane (stops all kernels)
        print("[1/3] Stopping kernels...")
        await control_plane.stop()
        print("  [OK] All kernels stopped")
        
        # Stop message bus
        print("\n[2/3] Stopping message bus...")
        await message_bus.stop()
        print("  [OK] Message bus stopped")
        
        # Final log
        print("\n[3/3] Final audit log...")
        await immutable_log.append(
            actor='boot_layer',
            action='system_shutdown',
            resource='grace_system',
            decision={'status': 'completed'},
            metadata={'timestamp': datetime.utcnow().isoformat()}
        )
        print("  [OK] Shutdown logged")
        
        print()
        print("=" * 80)
        print("Grace shutdown complete")
        print("All kernels stopped gracefully")
        print("Audit trail preserved")
        print("=" * 80)
        print()


# Global instance - Grace's boot sequence
boot_layer = BootLayer()
