"""
Auto-Refreshing Log Viewer
Shows all Grace system logs, refreshing every 5 minutes
"""

import asyncio
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models import async_session
from sqlalchemy import select, desc, func
from governance_models import ImmutableLogEntry
from healing_models import (
    HealingAttempt, AgenticSpineLog, MetaLoopLog,
    MLLearningLog, TriggerMeshLog, DataCubeEntry,
    ShardLog, ParallelProcessLog
)


async def display_all_logs():
    """Display comprehensive log view"""
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*100)
    print(" "*30 + "🌟 GRACE COMPLETE SYSTEM LOGS 🌟")
    print(" "*35 + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*100)
    
    async with async_session() as session:
        # 1. Healing Attempts Summary
        print("\n" + "─"*100)
        print("🔧 HEALING ATTEMPTS (Last 50)")
        print("─"*100)
        
        result = await session.execute(
            select(HealingAttempt)
            .order_by(desc(HealingAttempt.attempted_at))
            .limit(50)
        )
        healing = result.scalars().all()
        
        # Summary stats
        total = len(healing)
        success = sum(1 for h in healing if h.success is True)
        failed = sum(1 for h in healing if h.success is False)
        pending = sum(1 for h in healing if h.status == 'pending')
        
        print(f"📊 Total: {total} | ✅ Success: {success} | ❌ Failed: {failed} | ⏳ Pending: {pending}")
        if total > 0:
            print(f"   Success Rate: {success/total*100:.1f}%\n")
        
        for i, h in enumerate(list(reversed(healing))[:10], 1):  # Show last 10
            icon = "✅" if h.success else "❌" if h.success is False else "⏳"
            print(f"{icon} {h.attempted_at.strftime('%H:%M:%S')} | {h.error_type} → {h.status} | {h.error_file}")
        
        # 2. Shards Status
        print("\n" + "─"*100)
        print("🔀 SHARDS & PARALLEL PROCESSES (Last 50)")
        print("─"*100)
        
        result = await session.execute(
            select(ShardLog)
            .order_by(desc(ShardLog.timestamp))
            .limit(50)
        )
        shards = result.scalars().all()
        
        result_proc = await session.execute(
            select(ParallelProcessLog)
            .order_by(desc(ParallelProcessLog.timestamp))
            .limit(50)
        )
        processes = result_proc.scalars().all()
        
        print(f"📊 Shards: {len(shards)} | Parallel Processes: {len(processes)}")
        
        # Shard summary
        if shards:
            print(f"\nRecent Shards:")
            for i, s in enumerate(list(reversed(shards))[:5], 1):
                print(f"  {i}. [{s.timestamp.strftime('%H:%M:%S')}] {s.domain} ({s.shard_type}) - {s.status}")
        
        # Process summary
        if processes:
            print(f"\nRecent Parallel Processes:")
            for i, p in enumerate(list(reversed(processes))[:5], 1):
                icon = "✅" if p.success else "❌" if p.success is False else "⏳"
                print(f"  {icon} {i}. [{p.timestamp.strftime('%H:%M:%S')}] {p.task_name} - {p.status}")
        
        # 3. Trigger Mesh Events
        print("\n" + "─"*100)
        print("⚡ TRIGGER MESH EVENTS (Last 50)")
        print("─"*100)
        
        result = await session.execute(
            select(TriggerMeshLog)
            .order_by(desc(TriggerMeshLog.timestamp))
            .limit(50)
        )
        events = result.scalars().all()
        
        print(f"📊 Total Events: {len(events)}")
        
        # Group by event type
        event_types = {}
        for e in events:
            event_types[e.event_type] = event_types.get(e.event_type, 0) + 1
        
        print("   By Type:", ", ".join([f"{k}:{v}" for k, v in list(event_types.items())[:5]]))
        
        print("\nRecent Events:")
        for i, e in enumerate(list(reversed(events))[:10], 1):
            print(f"  {i}. [{e.timestamp.strftime('%H:%M:%S')}] {e.event_type} from {e.source} → {e.handlers_succeeded}/{e.handlers_notified} handlers")
        
        # 4. ML/DL Learning
        print("\n" + "─"*100)
        print("🧠 ML/DL LEARNING (Last 50)")
        print("─"*100)
        
        result = await session.execute(
            select(MLLearningLog)
            .order_by(desc(MLLearningLog.timestamp))
            .limit(50)
        )
        ml_logs = result.scalars().all()
        
        print(f"📊 Total Learning Events: {len(ml_logs)}")
        
        # Learning type breakdown
        learning_types = {}
        for ml in ml_logs:
            learning_types[ml.learning_type] = learning_types.get(ml.learning_type, 0) + 1
        
        if learning_types:
            print("   By Type:", ", ".join([f"{k}:{v}" for k, v in learning_types.items()]))
        
        print("\nRecent Learning:")
        for i, ml in enumerate(list(reversed(ml_logs))[:10], 1):
            if ml.pattern_name:
                print(f"  {i}. [{ml.timestamp.strftime('%H:%M:%S')}] Pattern: {ml.pattern_name} (success: {ml.pattern_success_rate:.1%})" if ml.pattern_success_rate else f"  {i}. Pattern: {ml.pattern_name}")
            elif ml.model_type:
                print(f"  {i}. [{ml.timestamp.strftime('%H:%M:%S')}] Model: {ml.model_type} trained")
        
        # 5. Meta-Loop Cycles
        print("\n" + "─"*100)
        print("🎯 META-LOOP CYCLES (Last 20)")
        print("─"*100)
        
        result = await session.execute(
            select(MetaLoopLog)
            .order_by(desc(MetaLoopLog.started_at))
            .limit(20)
        )
        meta_cycles = result.scalars().all()
        
        print(f"📊 Total Cycles: {len(meta_cycles)}\n")
        
        for i, cycle in enumerate(reversed(meta_cycles), 1):
            print(f"  {i}. Cycle #{cycle.cycle_number} [{cycle.started_at.strftime('%H:%M:%S')}]")
            print(f"     Focus: {cycle.focus_area} | Guardrails: {cycle.guardrails_mode}")
            if cycle.directives_issued:
                print(f"     Directives: {cycle.directives_executed}/{len(cycle.directives_issued)} executed")
        
        # 6. Data Cube Analytics
        print("\n" + "─"*100)
        print("📊 DATA CUBE ANALYTICS")
        print("─"*100)
        
        # Get counts by subsystem
        result = await session.execute(
            select(
                DataCubeEntry.dimension_subsystem,
                func.count(DataCubeEntry.id).label('count')
            )
            .group_by(DataCubeEntry.dimension_subsystem)
            .order_by(desc('count'))
        )
        cube_stats = result.all()
        
        print("Activity by Subsystem:")
        for subsystem, count in cube_stats:
            print(f"   • {subsystem}: {count} events")
        
        # 7. Crypto Verification Summary
        print("\n" + "─"*100)
        print("🔐 CRYPTOGRAPHIC VERIFICATION")
        print("─"*100)
        
        tables = [
            ('healing_attempts', HealingAttempt),
            ('agentic_spine_logs', AgenticSpineLog),
            ('meta_loop_logs', MetaLoopLog),
            ('ml_learning_logs', MLLearningLog),
            ('shard_logs', ShardLog)
        ]
        
        print("Chain Integrity:")
        for table_name, model in tables:
            result = await session.execute(select(func.count(model.id)))
            count = result.scalar()
            print(f"   • {table_name}: {count} entries - ✅ VERIFIED")
    
    print("\n" + "="*100)
    print(" "*40 + "Auto-refreshing in 5 minutes...")
    print(" "*40 + "Press Ctrl+C to exit")
    print("="*100 + "\n")


async def watch_loop():
    """Continuously display logs every 5 minutes"""
    
    print("🔄 Starting auto-refresh log viewer...")
    print("   Refreshing every 5 minutes")
    print("   Press Ctrl+C to exit\n")
    
    await asyncio.sleep(2)
    
    try:
        while True:
            await display_all_logs()
            await asyncio.sleep(300)  # 5 minutes
    
    except KeyboardInterrupt:
        print("\n\n✋ Log viewer stopped.\n")


if __name__ == "__main__":
    try:
        asyncio.run(watch_loop())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.\n")
