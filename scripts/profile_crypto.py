import statistics
import time
from backend.verification import verification_engine


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
