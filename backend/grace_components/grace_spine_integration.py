"""
GRACE Agentic Spine Integration

Coordinates all agentic subsystems and provides unified startup/shutdown.
This is the main entry point for activating GRACE's autonomous capabilities.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .agentic_spine import agentic_spine
from .learning_integration import learning_integration
from .human_collaboration import human_collaboration
from .resource_stewardship import resource_stewardship
from .ethics_sentinel import ethics_sentinel
from .meta_loop_supervisor import meta_loop_supervisor
from .proactive_intelligence import proactive_intelligence
from .agentic_observability import agentic_observability
from .multi_agent_shards import shard_coordinator
from .trigger_mesh import trigger_mesh
from .immutable_log import immutable_log


class GraceAgenticSystem:
    """
    Unified coordinator for GRACE's agentic capabilities.
    
    This integrates:
    - Event enrichment with intent and context
    - Trust cores as decision partners
    - Ledger reasoning hooks
    - Unified health graph
    - Policy-aware playbooks
    - Autonomous planning and triage
    - Meta-loop autonomy
    - Learning integration
    - Human collaboration
    - Resource stewardship
    - Ethics/compliance sentinel
    """
    
    def __init__(self):
        self.systems = {
            "trigger_mesh": trigger_mesh,
            "shard_coordinator": shard_coordinator,
            "agentic_observability": agentic_observability,
            "proactive_intelligence": proactive_intelligence,
            "agentic_spine": agentic_spine,
            "learning_integration": learning_integration,
            "human_collaboration": human_collaboration,
            "resource_stewardship": resource_stewardship,
            "ethics_sentinel": ethics_sentinel,
            "meta_loop_supervisor": meta_loop_supervisor
        }
        self.running = False
        self.started_at: Optional[datetime] = None
    
    async def start(self):
        """Start all agentic systems in proper order"""
        
        print("=" * 60)
        print("GRACE AGENTIC SPINE - AUTONOMOUS ACTIVATION")
        print("=" * 60)
        
        print("\n🔧 Starting foundational systems...")
        await trigger_mesh.start()
        
        print("\n🌐 Starting multi-agent shard coordinator...")
        await shard_coordinator.start()
        
        print("\n👁️  Starting agentic observability...")
        await agentic_observability.start()
        
        print("\n🔮 Starting proactive intelligence...")
        await proactive_intelligence.start()
        
        print("\n🧠 Activating autonomous decision core...")
        await agentic_spine.start()
        
        print("\n📊 Starting learning integration...")
        await learning_integration.start()
        
        print("\n👥 Enabling human collaboration...")
        await human_collaboration.start()
        
        print("\n♻️  Activating resource stewardship...")
        await resource_stewardship.start()
        
        print("\n⚖️  Starting ethics & compliance sentinel...")
        await ethics_sentinel.start()
        
        print("\n🔄 Starting meta loop supervisor...")
        await meta_loop_supervisor.start()
        
        self.running = True
        self.started_at = datetime.utcnow()
        
        await immutable_log.append(
            actor="system",
            action="agentic_spine_started",
            resource="grace_agentic_system",
            subsystem="integration",
            payload={
                "systems": list(self.systems.keys()),
                "started_at": self.started_at.isoformat()
            },
            result="activated"
        )
        
        print("\n" + "=" * 60)
        print("✅ GRACE AGENTIC SPINE FULLY OPERATIONAL")
        print("=" * 60)
        print("\nGRACE is now autonomous and can:")
        print("  • Predict incidents before they occur (proactive)")
        print("  • Enrich events with intent and context")
        print("  • Make decisions with trust core partnership")
        print("  • Plan and execute recovery actions")
        print("  • Learn from outcomes and self-improve")
        print("  • Collaborate with humans proactively")
        print("  • Manage her own resources")
        print("  • Monitor ethics and compliance")
        print("  • Supervise her own behavior cross-domain")
        print("\n" + "=" * 60)
    
    async def stop(self):
        """Gracefully stop all agentic systems"""
        
        print("\n🛑 Gracefully shutting down GRACE agentic spine...")
        
        await shard_coordinator.stop()
        print("  ✓ Shard coordinator stopped")
        
        await agentic_observability.stop()
        print("  ✓ Agentic observability stopped")
        
        await proactive_intelligence.stop()
        print("  ✓ Proactive intelligence stopped")
        
        await meta_loop_supervisor.stop()
        print("  ✓ Meta loop supervisor stopped")
        
        await ethics_sentinel.stop()
        print("  ✓ Ethics sentinel stopped")
        
        await resource_stewardship.stop()
        print("  ✓ Resource stewardship stopped")
        
        await human_collaboration.stop()
        print("  ✓ Human collaboration stopped")
        
        await agentic_spine.stop()
        print("  ✓ Agentic spine stopped")
        
        await trigger_mesh.stop()
        print("  ✓ Trigger mesh stopped")
        
        self.running = False
        
        uptime = (datetime.utcnow() - self.started_at).total_seconds() if self.started_at else 0
        
        await immutable_log.append(
            actor="system",
            action="agentic_spine_stopped",
            resource="grace_agentic_system",
            subsystem="integration",
            payload={
                "uptime_seconds": uptime,
                "stopped_at": datetime.utcnow().isoformat()
            },
            result="deactivated"
        )
        
        print("\n✅ GRACE agentic spine shutdown complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agentic systems"""
        
        health = {
            "status": "operational" if self.running else "stopped",
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "uptime_seconds": (datetime.utcnow() - self.started_at).total_seconds() if self.started_at else 0,
            "systems": {}
        }
        
        for name, system in self.systems.items():
            if hasattr(system, 'running'):
                health["systems"][name] = "running" if system.running else "stopped"
            else:
                health["systems"][name] = "unknown"
        
        return health
    
    async def get_status(self) -> Dict[str, Any]:
        """Get detailed status of agentic capabilities"""
        
        status = {
            "system": "grace_agentic_spine",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "operational": self.running,
            "health": await self.health_check(),
            "capabilities": {
                "proactive_intelligence": {
                    "enabled": True,
                    "description": "Predicts incidents, capacity needs, and system failures before they occur"
                },
                "event_enrichment": {
                    "enabled": True,
                    "description": "Enriches events with signer identity, context, and expected outcomes"
                },
                "trust_core_partnership": {
                    "enabled": True,
                    "description": "Trust cores as decision partners, not just gatekeepers"
                },
                "ledger_reasoning": {
                    "enabled": True,
                    "description": "Real-time queries over immutable log for pattern detection"
                },
                "health_graph": {
                    "enabled": True,
                    "description": "Dynamic graph of services, dependencies, and KPIs"
                },
                "autonomous_planning": {
                    "enabled": True,
                    "description": "Autonomous triage and recovery planning"
                },
                "meta_loop": {
                    "enabled": True,
                    "description": "Self-improvement through retrospectives and threshold tuning"
                },
                "learning": {
                    "enabled": True,
                    "description": "Continuous learning from decision outcomes"
                },
                "human_collaboration": {
                    "enabled": True,
                    "description": "Proactive engagement with signed briefs and approvals"
                },
                "resource_stewardship": {
                    "enabled": True,
                    "description": "Self-management of capacity, credentials, and keys"
                },
                "ethics_compliance": {
                    "enabled": True,
                    "description": "Bias detection and policy compliance monitoring"
                },
                "meta_loop_supervisor": {
                    "enabled": True,
                    "description": "Cross-domain oversight and systemic optimization"
                }
            }
        }
        
        return status


grace_agentic_system = GraceAgenticSystem()


async def activate_grace_autonomy():
    """
    Convenience function to activate GRACE's autonomous capabilities.
    Call this from your main application startup.
    """
    await grace_agentic_system.start()


async def deactivate_grace_autonomy():
    """
    Convenience function to gracefully deactivate GRACE's autonomous capabilities.
    Call this during application shutdown.
    """
    await grace_agentic_system.stop()


if __name__ == "__main__":
    async def main():
        await activate_grace_autonomy()
        
        try:
            while True:
                await asyncio.sleep(10)
                status = await grace_agentic_system.get_status()
                print(f"\n[Health Check] Systems operational: {status['health']['status']}")
        except KeyboardInterrupt:
            print("\n\nReceived shutdown signal...")
            await deactivate_grace_autonomy()
    
    asyncio.run(main())
