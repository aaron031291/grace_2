"""
Real-Time Healing Monitor
Live display of Grace's autonomous healing activity
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models import async_session
from sqlalchemy import select, desc
from governance_models import ImmutableLogEntry


async def display_healing_status():
    """Display real-time healing status"""
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*80)
    print(" "*20 + "🔧 GRACE AUTONOMOUS HEALING MONITOR")
    print(" "*25 + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80 + "\n")
    
    try:
        async with async_session() as session:
            # Get recent healing activity
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(
                    ImmutableLogEntry.subsystem.in_([
                        'autonomous_code_healer',
                        'log_based_healer',
                        'resilient_startup',
                        'ml_healing'
                    ])
                )
                .order_by(desc(ImmutableLogEntry.timestamp))
                .limit(20)
            )
            
            entries = result.scalars().all()
            
            if not entries:
                print("⚠️  No healing activity yet")
                return
            
            print(f"📊 Recent Healing Activity ({len(entries)} actions):\n")
            
            for i, entry in enumerate(reversed(entries), 1):
                # Format timestamp
                ts = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "unknown"
                
                # Icon based on result
                icon = "✅" if entry.result == "success" else "⚠️" if entry.result == "pending" else "❌"
                
                # Subsystem color
                subsystem_short = entry.subsystem.replace('_', ' ').title()
                
                print(f"{icon} [{ts}] {subsystem_short}")
                print(f"   Action: {entry.action}")
                print(f"   Resource: {entry.resource}")
                print(f"   Actor: {entry.actor}")
                print(f"   Result: {entry.result}")
                print()
            
            # Get statistics
            print("="*80)
            print("📈 STATISTICS:\n")
            
            # Count by subsystem
            subsystem_counts = {}
            success_counts = {}
            
            for entry in entries:
                subsystem = entry.subsystem
                subsystem_counts[subsystem] = subsystem_counts.get(subsystem, 0) + 1
                
                if entry.result == 'success':
                    success_counts[subsystem] = success_counts.get(subsystem, 0) + 1
            
            for subsystem, count in subsystem_counts.items():
                successes = success_counts.get(subsystem, 0)
                success_rate = (successes / count * 100) if count > 0 else 0
                
                print(f"   {subsystem}:")
                print(f"      Total: {count} | Success: {successes} ({success_rate:.1f}%)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def watch_loop():
    """Continuously monitor healing activity"""
    
    print("🔄 Starting real-time monitor (Press Ctrl+C to exit)...\n")
    await asyncio.sleep(2)
    
    try:
        while True:
            await display_healing_status()
            
            print("\n" + "="*80)
            print("🔄 Refreshing in 10 seconds... (Ctrl+C to exit)")
            print("="*80)
            
            await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\n✋ Monitor stopped.\n")


if __name__ == "__main__":
    try:
        asyncio.run(watch_loop())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.\n")
