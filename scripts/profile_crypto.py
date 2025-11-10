import statistics
import time
import sys
import hashlib
import json
from pathlib import Path

# Add backend to path without triggering circular imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Direct imports to avoid circular dependency
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Create standalone verification engine for profiling
class StandaloneVerificationEngine:
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self._sign = self.private_key.sign
    
    def create_envelope(self, action_id: str, actor: str, action_type: str, resource: str, input_data: dict):
        """Simplified version of create_envelope for profiling"""
        input_str = json.dumps(input_data, sort_keys=True, separators=(",", ":"))
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        message = f"{action_id}:{actor}:{action_type}:{resource}:{input_hash}"
        signature = self._sign(message.encode())
        signature_hex = signature.hex()
        return signature_hex, input_hash

# Global instance
verification_engine = StandaloneVerificationEngine()


def run_once(i: int):
    # Exercise the hot path used in production: create_envelope signs a message
    action_id = f"test_{i}"
    actor = "profile"
    action_type = "benchmark"
    resource = "profiling"
    input_data = {"i": i, "fixed": True}
    # Returns (signature_hex, input_hash); ignore values
    verification_engine.create_envelope(action_id, actor, action_type, resource, input_data)


def bench(n: int = 5000):
    times = []
    for i in range(n):
        t0 = time.perf_counter_ns()
        run_once(i)
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1e6)
    median = statistics.median(times)
    # Approximate p95
    p95 = sorted(times)[int(0.95 * len(times)) - 1]
    print(f"n={n} median={median:.3f}ms p95={p95:.3f}ms min={min(times):.3f} max={max(times):.3f}")


if __name__ == "__main__":
    bench(10000)
