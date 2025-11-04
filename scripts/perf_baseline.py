#!/usr/bin/env python3
"""
Run a simple performance baseline against the backend to produce initial reference numbers.

This script performs:
- Cold start import timing of backend app
- In-memory compute micro-benchmarks
- Optional HTTP latency checks if BACKEND_URL is provided (e.g., http://localhost:8000)

Usage:
  py scripts/perf_baseline.py --iterations 20 --out docs/PERFORMANCE_PLAN.md

Results are appended to PERFORMANCE_PLAN.md in a structured block.
"""
from __future__ import annotations
import argparse
import time
import statistics as stats
import os
from pathlib import Path

try:
    import httpx  # type: ignore
except Exception:
    httpx = None


def time_import() -> float:
    start = time.perf_counter()
    __import__('backend.main')
    return time.perf_counter() - start


def cpu_loop_work(n: int = 1_000_00) -> float:
    s = 0
    for i in range(n):
        s += (i % 7) * (i % 13)
    return s


def bench_cpu(iterations: int) -> dict:
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        cpu_loop_work()
        times.append(time.perf_counter() - t0)
    return {
        'avg_s': sum(times) / len(times),
        'p50_s': stats.median(times),
        'p95_s': sorted(times)[int(0.95 * len(times)) - 1],
        'iterations': iterations,
    }


def bench_http(url: str, iterations: int) -> dict | None:
    if httpx is None:
        return None
    times = []
    with httpx.Client(timeout=10.0) as client:
        for _ in range(iterations):
            t0 = time.perf_counter()
            r = client.get(f"{url.rstrip('/')}/docs")
            r.raise_for_status()
            times.append(time.perf_counter() - t0)
    return {
        'endpoint': '/docs',
        'avg_s': sum(times) / len(times),
        'p50_s': stats.median(times),
        'p95_s': sorted(times)[int(0.95 * len(times)) - 1],
        'iterations': iterations,
    }


def append_results(path: Path, results: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    lines = [
        "\n",
        "### Performance Baseline Run\n",
        f"Timestamp: {ts}\n",
        "\n",
        "- Import cold-start (backend.main): {:.3f}s\n".format(results['import_s']),
        "- CPU loop avg: {:.3f}s (p50 {:.3f}s, p95 {:.3f}s) over {} iters\n".format(
            results['cpu']['avg_s'], results['cpu']['p50_s'], results['cpu']['p95_s'], results['cpu']['iterations']
        ),
    ]
    if results.get('http'):
        http = results['http']
        lines.append("- HTTP {} avg: {:.3f}s (p50 {:.3f}s, p95 {:.3f}s) over {} iters\n".format(
            http['endpoint'], http['avg_s'], http['p50_s'], http['p95_s'], http['iterations']
        ))
    with path.open('a', encoding='utf-8') as f:
        f.writelines(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--iterations', type=int, default=20)
    ap.add_argument('--out', type=str, default='docs/PERFORMANCE_PLAN.md')
    ap.add_argument('--backend-url', type=str, default=os.getenv('BACKEND_URL', ''))
    args = ap.parse_args()

    import_time_s = time_import()
    cpu = bench_cpu(args.iterations)

    http_res = None
    if args.backend_url:
        try:
            http_res = bench_http(args.backend_url, args.iterations)
        except Exception as e:
            http_res = None

    results = {
        'import_s': import_time_s,
        'cpu': cpu,
        'http': http_res,
    }
    append_results(Path(args.out), results)
    print(f"Perf baseline appended to {args.out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
