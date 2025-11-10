import statistics
import time

# TODO: Replace with real import once the crypto hot path is identified
# from backend.security.crypto_assignments import assign_crypto

def run_once(i: int):
    # Placeholder: simulate a no-op call; update with real function
    # assign_crypto(component_id=i % 100)
    return None


def bench(n: int = 1000):
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
    bench(2000)
