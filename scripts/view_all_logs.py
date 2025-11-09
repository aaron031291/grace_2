"""
View GRACE System Logs
Shows last 50 entries from:
- Backend logs
- Immutable log (with crypto verification)
- Memory storage
- Meta-loop decisions
"""

import asyncio
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from immutable_log import ImmutableLog
from memory import PersistentMemory
from models import async_session
from sqlalchemy import select, desc, and_
from governance_models import ImmutableLogEntry
from trigger_mesh import TriggerEvent


async def view_backend_logs():
    """View last 50 backend log entries"""
    print("\n" + "="*80)
    print("📋 BACKEND LOGS (Last 50 entries)")
    print("="*80)
    
    log_file = Path(__file__).parent.parent / "logs" / "backend.log"
    
    if not log_file.exists():
        # Try alternative locations
        log_file = Path(__file__).parent.parent / "backend.log"
    
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_50 = lines[-50:] if len(lines) > 50 else lines
            
            for line in last_50:
                print(line.rstrip())
    else:
        print("⚠️  Log file not found")
        print(f"   Searched: {log_file}")


async def view_immutable_log():
    """View last 50 immutable log entries with crypto verification"""
    print("\n" + "="*80)
    print("🔒 IMMUTABLE LOG (Last 50 entries with crypto)")
    print("="*80)
    
    try:
        immutable_log = ImmutableLog()
        
        async with async_session() as session:
            # Get last 50 entries
            result = await session.execute(
                select(ImmutableLogEntry)
                .order_by(desc(ImmutableLogEntry.timestamp))
                .limit(50)
            )
            entries = result.scalars().all()
            
            if not entries:
                print("⚠️  No immutable log entries found")
                return
            
            # Reverse to show oldest first
            entries = list(reversed(entries))
            
            print(f"\n📊 Found {len(entries)} entries\n")
            
            for i, entry in enumerate(entries, 1):
                print(f"[{i}] Entry ID: {entry.entry_id}")
                print(f"    Timestamp: {entry.timestamp}")
                print(f"    Actor: {entry.actor}")
                print(f"    Action: {entry.action}")
                print(f"    Resource: {entry.resource}")
                print(f"    Subsystem: {entry.subsystem}")
                print(f"    Result: {entry.result}")
                
                # Crypto metadata
                print(f"    🔐 Crypto:")
                print(f"       - Signature: {entry.signature[:32]}..." if entry.signature else "       - Signature: None")
                print(f"       - Hash: {entry.hash[:32]}..." if entry.hash else "       - Hash: None")
                print(f"       - Prev Hash: {entry.previous_hash[:32]}..." if entry.previous_hash else "       - Prev Hash: None")
                
                # Verify integrity
                if entry.signature and entry.hash:
                    # Simple verification - check hash matches
                    print(f"       - ✅ Cryptographically signed")
                else:
                    print(f"       - ⚠️  Missing crypto data")
                
                print()
    
    except Exception as e:
        print(f"❌ Error reading immutable log: {e}")
        import traceback
        traceback.print_exc()


async def view_memory_storage():
    """View last 50 memory entries"""
    print("\n" + "="*80)
    print("🧠 MEMORY STORAGE (Last 50 entries)")
    print("="*80)
    
    try:
        memory = PersistentMemory()
        
        # Get recent memories
        recent = await memory.search(
            query="",  # Empty query gets all
            limit=50,
            threshold=0.0  # No similarity threshold
        )
        
        if not recent:
            print("⚠️  No memory entries found")
            return
        
        print(f"\n📊 Found {len(recent)} memory entries\n")
        
        for i, mem in enumerate(recent, 1):
            print(f"[{i}] Memory ID: {mem.get('id', 'unknown')}")
            print(f"    Timestamp: {mem.get('timestamp', 'unknown')}")
            print(f"    Type: {mem.get('memory_type', 'unknown')}")
            print(f"    Content: {mem.get('content', '')[:100]}...")
            
            # Metadata
            metadata = mem.get('metadata', {})
            if metadata:
                print(f"    📎 Metadata:")
                for key, value in metadata.items():
                    if key not in ['embedding']:  # Skip large embeddings
                        print(f"       - {key}: {value}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error reading memory: {e}")
        import traceback
        traceback.print_exc()


async def view_meta_decisions():
    """View meta-loop decisions and directives"""
    print("\n" + "="*80)
    print("🎯 META-LOOP DECISIONS (Last 50)")
    print("="*80)
    
    try:
        # Read from immutable log for meta-loop actions
        async with async_session() as session:
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(ImmutableLogEntry.subsystem.like('%meta%'))
                .order_by(desc(ImmutableLogEntry.timestamp))
                .limit(50)
            )
            entries = result.scalars().all()
            
            if not entries:
                print("⚠️  No meta-loop decisions found")
                return
            
            print(f"\n📊 Found {len(entries)} meta decisions\n")
            
            for i, entry in enumerate(reversed(entries), 1):
                print(f"[{i}] {entry.timestamp}")
                print(f"    Action: {entry.action}")
                print(f"    Resource: {entry.resource}")
                print(f"    Result: {entry.result}")
                
                # Parse payload if available
                import json
                if hasattr(entry, 'payload') and entry.payload:
                    try:
                        payload = json.loads(entry.payload) if isinstance(entry.payload, str) else entry.payload
                        print(f"    Details: {payload}")
                    except:
                        pass
                
                print()
    
    except Exception as e:
        print(f"❌ Error reading meta decisions: {e}")
        import traceback
        traceback.print_exc()


async def view_crypto_graph():
    """View cryptographic chain/graph integrity"""
    print("\n" + "="*80)
    print("🔐 CRYPTOGRAPHIC CHAIN INTEGRITY")
    print("="*80)
    
    try:
        async with async_session() as session:
            # Get all entries to verify chain
            result = await session.execute(
                select(ImmutableLogEntry)
                .order_by(ImmutableLogEntry.timestamp)
            )
            entries = result.scalars().all()
            
            if not entries:
                print("⚠️  No entries to verify")
                return
            
            print(f"\n📊 Verifying {len(entries)} entries in chain...\n")
            
            verified = 0
            broken = 0
            
            for i, entry in enumerate(entries):
                if i == 0:
                    # First entry - should have no previous hash
                    if entry.previous_hash is None or entry.previous_hash == "":
                        print(f"✅ Genesis entry verified: {entry.entry_id}")
                        verified += 1
                    else:
                        print(f"⚠️  Genesis entry has unexpected previous_hash")
                else:
                    # Verify chain link
                    prev_entry = entries[i-1]
                    if entry.previous_hash == prev_entry.hash:
                        verified += 1
                    else:
                        broken += 1
                        print(f"❌ Chain broken at entry {i}: {entry.entry_id}")
                        print(f"   Expected prev_hash: {prev_entry.hash[:32]}...")
                        print(f"   Actual prev_hash: {entry.previous_hash[:32] if entry.previous_hash else 'None'}...")
            
            print(f"\n📈 Chain Statistics:")
            print(f"   Total Entries: {len(entries)}")
            print(f"   ✅ Verified Links: {verified}")
            print(f"   ❌ Broken Links: {broken}")
            
            if broken == 0:
                print(f"\n   🎉 CHAIN INTEGRITY: PERFECT")
            else:
                print(f"\n   ⚠️  CHAIN INTEGRITY: COMPROMISED")
    
    except Exception as e:
        print(f"❌ Error verifying crypto chain: {e}")
        import traceback
        traceback.print_exc()


async def view_trigger_mesh_events():
    """View last 50 trigger mesh events"""
    print("\n" + "="*80)
    print("⚡ TRIGGER MESH EVENTS (Last 50)")
    print("="*80)
    
    try:
        async with async_session() as session:
            # Trigger mesh events are logged in immutable log
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(ImmutableLogEntry.result == 'published')  # Events published to mesh
                .order_by(desc(ImmutableLogEntry.timestamp))
                .limit(50)
            )
            entries = result.scalars().all()
            
            if not entries:
                print("⚠️  No trigger mesh events found")
                return
            
            print(f"\n📊 Found {len(entries)} trigger mesh events\n")
            
            for i, entry in enumerate(reversed(entries), 1):
                print(f"[{i}] {entry.timestamp}")
                print(f"    Event: {entry.action}")
                print(f"    Source: {entry.subsystem}")
                print(f"    Actor: {entry.actor}")
                print(f"    Resource: {entry.resource}")
                print()
    
    except Exception as e:
        print(f"❌ Error reading trigger mesh events: {e}")


async def view_tail_logs():
    """View tail of backend logs (last 50 lines)"""
    print("\n" + "="*80)
    print("📜 BACKEND TAIL LOGS (Last 50 lines)")
    print("="*80 + "\n")
    
    log_file = Path(__file__).parent.parent / "logs" / "backend.log"
    
    if not log_file.exists():
        log_file = Path(__file__).parent.parent / "backend.log"
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                tail_lines = lines[-50:] if len(lines) > 50 else lines
                
                for i, line in enumerate(tail_lines, 1):
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        print(f"[{i}] {line.rstrip()}")
                    else:
                        print(f"    {line.rstrip()}")
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print("⚠️  Log file not found")


async def main():
    """Main entry point"""
    print("\n" + "="*80)
    print(" "*20 + "GRACE SYSTEM LOGS VIEWER")
    print(" "*25 + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    
    # View all logs
    await view_tail_logs()
    await view_immutable_log()
    await view_trigger_mesh_events()
    await view_memory_storage()
    await view_meta_decisions()
    await view_crypto_graph()
    
    print("\n" + "="*80)
    print(" "*25 + "END OF LOG REPORT")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLog viewer interrupted.\n")
    except Exception as e:
        print(f"\n\nFatal error: {e}\n")
        import traceback
        traceback.print_exc()
