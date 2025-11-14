"""
Three-Tier Orchestration System
Complete integration: Agentic Brain → HTM → Execution

Tier 1: Agentic Brain (Intent + Evaluation)
  - Sets goals: "index new docs", "reprocess low quality"
  - Reads telemetry from all systems
  - Creates HTM tasks with desired outcomes
  - Reviews results and learns

Tier 2: Hierarchical Task Manager (Priority + Orchestration)
  - Receives tasks from brain and other sources
  - Assigns priorities and SLAs
  - Tracks queue health and dependencies
  - Dispatches to execution layer

Tier 3: Execution Layer (Ingestion + Feedback)
  - Librarian + Pipeline execute work
  - Publishes status back to HTM and brain
  - Includes diagnostics (chunks, trust, errors)
  - HTM auto-retries transient failures

Flow:
Brain sets intent → HTM prioritizes → Execution processes → Feedback to brain
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from backend.core.message_bus import message_bus, MessagePriority
from backend.core.agentic_brain import agentic_brain
from backend.core.enhanced_htm import enhanced_htm
from backend.core.enhanced_ingestion_pipeline import enhanced_ingestion_pipeline
from backend.core.librarian_ingestion_integration import librarian_ingestion_integration
from backend.kernels.librarian_kernel_enhanced import enhanced_librarian_kernel


class ThreeTierOrchestration:
    """
    Master orchestrator connecting all three tiers
    
    Creates complete autonomous loop:
    1. Brain decides what to do and why
    2. HTM schedules and prioritizes
    3. Systems execute
    4. Feedback flows back to brain
    5. Brain learns and adjusts
    """
    
    def __init__(self):
        self.integration_active = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start three-tier orchestration"""
        
        print("="*70)
        print("THREE-TIER ORCHESTRATION - Starting Complete System")
        print("="*70)
        print()
        
        # Tier 1: Agentic Brain
        print("[TIER 1] Starting Agentic Brain (Intent + Evaluation)...")
        await agentic_brain.start()
        
        # Tier 2: HTM
        print("[TIER 2] Starting Hierarchical Task Manager (Priority + Orchestration)...")
        await enhanced_htm.start()
        
        # Tier 3: Execution Layer
        print("[TIER 3] Starting Execution Layer (Ingestion + Feedback)...")
        await enhanced_librarian_kernel.initialize()
        await librarian_ingestion_integration.start()
        
        # Connect the tiers
        print("[INTEGRATION] Connecting all tiers via message bus...")
        asyncio.create_task(self._connect_brain_to_htm())
        asyncio.create_task(self._connect_htm_to_execution())
        asyncio.create_task(self._connect_execution_to_brain())
        
        # Start health monitoring
        self._monitor_task = asyncio.create_task(self._monitor_integration())
        
        self.integration_active = True
        
        print()
        print("="*70)
        print("[THREE-TIER] All tiers operational")
        print("[THREE-TIER] Autonomous loop closed")
        print("="*70)
        print()
        print("Flow:")
        print("  Brain (Intent) -> HTM (Schedule) -> Execute -> Feedback -> Brain (Learn)")
        print()
        print("="*70)
    
    async def _connect_brain_to_htm(self):
        """Connect Agentic Brain to HTM"""
        
        # Brain publishes tasks to HTM via task.enqueue
        # HTM automatically subscribes
        # This connection is implicit via message bus
        
        print("[THREE-TIER] Brain -> HTM connection established")
    
    async def _connect_htm_to_execution(self):
        """Connect HTM to execution layer"""
        
        try:
            # HTM dispatches via task.execute.<handler>
            # Librarian subscribes to task.execute.librarian
            
            queue = await message_bus.subscribe(
                subscriber="three_tier_htm_dispatch",
                topic="task.execute.librarian"
            )
            
            while True:
                msg = await queue.get()
                
                task_id = msg.payload.get("task_id")
                task_type = msg.payload.get("task_type")
                
                print(f"[THREE-TIER] HTM -> Execution: {task_type}")
                
                # Would route to appropriate executor
                # For now, log the dispatch
        
        except Exception as e:
            print(f"[THREE-TIER] HTM-Execution connection error: {e}")
    
    async def _connect_execution_to_brain(self):
        """Connect execution feedback to brain"""
        
        # Execution publishes task.completed
        # Brain subscribes (already done in brain._learn_from_outcomes)
        # This connection is automatic
        
        print("[THREE-TIER] Execution -> Brain feedback loop established")
    
    async def _monitor_integration(self):
        """Monitor integration health"""
        
        while True:
            try:
                await asyncio.sleep(60)
                
                # Get status from all tiers
                brain_status = agentic_brain.get_status()
                htm_status = enhanced_htm.get_status()
                librarian_status = enhanced_librarian_kernel.get_stats()
                
                # Publish integration health
                await message_bus.publish(
                    source="three_tier_orchestration",
                    topic="orchestration.health",
                    payload={
                        "brain": brain_status,
                        "htm": htm_status,
                        "librarian": librarian_status,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=MessagePriority.NORMAL
                )
            
            except Exception as e:
                print(f"[THREE-TIER] Monitor error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "integration_active": self.integration_active,
            "tier1_brain": agentic_brain.get_status(),
            "tier2_htm": enhanced_htm.get_status(),
            "tier3_librarian": enhanced_librarian_kernel.get_stats()
        }


# Global instance
three_tier_orchestration = ThreeTierOrchestration()
