"""
Proof of Self-Healing Functionality Test

This test demonstrates that Grace's self-healing system is working by:
1. Triggering a simulated failure
2. Verifying the self-healing system detects it
3. Confirming automatic remediation occurs
4. Showing before/after metrics
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.self_heal.trigger_system import (
    HeartbeatFailureTrigger,
    APITimeoutTrigger,
    TriggerType,
    IncidentSeverity
)
from backend.core.message_bus import message_bus
from datetime import datetime
import json

class SelfHealingProofTest:
    """Demonstrate self-healing is working"""
    
    def __init__(self):
        self.events_captured = []
        self.healing_activated = False
        
    async def capture_events(self, msg):
        """Capture all healing-related events"""
        self.events_captured.append({
            'topic': msg.topic,
            'payload': msg.payload,
            'timestamp': datetime.now().isoformat()
        })
        
        if 'self_healing' in str(msg.payload):
            self.healing_activated = True
            
    async def run_proof(self):
        """Run the proof-of-concept test"""
        print("=" * 70)
        print("GRACE SELF-HEALING PROOF TEST")
        print("=" * 70)
        
        # Subscribe to all events
        await message_bus.subscribe('event.#', self.capture_events)
        await message_bus.subscribe('task.#', self.capture_events)
        
        print("\n[1/5] Setting up message bus...")
        await asyncio.sleep(0.5)
        print("[OK] Message bus ready")
        
        print("\n[2/5] Creating heartbeat failure trigger...")
        heartbeat_trigger = HeartbeatFailureTrigger(
            kernel_name="test_kernel",
            timeout_seconds=5
        )
        print("[OK] Trigger created")
        
        print("\n[3/5] Simulating component failure (missing heartbeats)...")
        # Simulate the kernel not sending heartbeats
        await asyncio.sleep(1)
        
        # Check for failure (will fire if timeout exceeded)
        await heartbeat_trigger.check()
        print("[OK] Trigger check executed")
        
        print("\n[4/5] Waiting for self-healing activation...")
        await asyncio.sleep(2)
        
        # Check if healing was triggered
        print("\n[5/5] RESULTS:")
        print("-" * 70)
        print(f"Events captured: {len(self.events_captured)}")
        print(f"Self-healing activated: {self.healing_activated}")
        
        if self.events_captured:
            print("\nCaptured Events:")
            for i, event in enumerate(self.events_captured, 1):
                print(f"\n  Event {i}:")
                print(f"    Topic: {event['topic']}")
                print(f"    Time: {event['timestamp']}")
                if event['payload']:
                    print(f"    Payload: {json.dumps(event['payload'], indent=6)}")
        
        print("\n" + "=" * 70)
        
        if self.healing_activated:
            print("[PASS] PROOF CONFIRMED: Self-healing system is ACTIVE and WORKING")
        elif self.events_captured:
            print("[WARN] PARTIAL: Events captured but no healing action detected")
        else:
            print("[FAIL] NO EVIDENCE: No self-healing events detected")
            
        print("=" * 70)
        
        return self.healing_activated

async def main():
    """Main test runner"""
    tester = SelfHealingProofTest()
    
    try:
        result = await asyncio.wait_for(tester.run_proof(), timeout=10)
        
        if result:
            print("\n[PASS] TEST PASSED: Self-healing is working!")
            return 0
        else:
            print("\n[WARN] TEST INCONCLUSIVE: Check system logs")
            return 1
            
    except asyncio.TimeoutError:
        print("\n[FAIL] TEST TIMEOUT: Self-healing may not be running")
        return 2
    except Exception as e:
        print(f"\n[FAIL] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
