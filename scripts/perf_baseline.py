"""Simple performance probe for key Grace endpoints."""

import argparse
import asyncio
import statistics
import time

import httpx


ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/api/status"),
    ("GET", "/api/cognition/status"),
]


async def probe(base_url: str, iterations: int) -> None:
    timings = {endpoint: [] for endpoint in ENDPOINTS}

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        for method, path in ENDPOINTS:
            for _ in range(iterations):
                start = time.perf_counter()
                response = await client.request(method, path)
                elapsed_ms = (time.perf_counter() - start) * 1000
                timings[(method, path)].append(elapsed_ms)
                response.raise_for_status()

    for (method, path), values in timings.items():
        pct95 = statistics.quantiles(values, n=100)[94]
        print(f"{method} {path} -> median {statistics.median(values):.1f}ms, p95 {pct95:.1f}ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight performance probes")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()

    asyncio.run(probe(args.base_url, args.iterations))


if __name__ == "__main__":
    main()
