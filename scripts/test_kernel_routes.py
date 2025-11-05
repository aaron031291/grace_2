"""
Kernel Routes Probe
- Imports backend.main.app
- Runs startup handlers
- Calls a set of key kernel endpoints to ensure 2xx + sane shapes
- Runs shutdown handlers

Windows: py scripts\test_kernel_routes.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def run_probe() -> int:
    import backend.main as m

    app = m.app
    tests_passed = 0
    tests_failed = 0

    # Run startup events
    try:
        if app.router.on_startup:
            for handler in app.router.on_startup:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
        tests_passed += 1
        print("[1/3] Startup handlers: PASS")
    except Exception as e:
        print(f"[1/3] Startup handlers: FAIL -> {e}")
        tests_failed += 1

    # In-process HTTP client using ASGI transport
    try:
        import httpx
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            endpoints = [
                ("GET", "/health"),
                ("GET", "/api/core/heartbeat"),
                ("GET", "/api/core/governance"),
                ("GET", "/api/core/verify?limit=10&hours_back=1"),
                ("GET", "/api/core/metrics"),
                ("GET", "/api/cognition/status"),
                ("GET", "/api/cognition/readiness"),
                ("GET", "/api/cognition/alerts"),
                # Security domain (GET-only endpoints for probe)
                ("GET", "/api/security/rules"),
                ("GET", "/api/security/alerts"),
                ("GET", "/api/security/quarantined"),
                ("GET", "/api/security/constitutional"),
                ("GET", "/api/security/metrics"),
                # ML domain (public list)
                ("GET", "/api/ml/models"),
                # Trust API (public)
                ("GET", "/api/trust/sources"),
            ]
            failures = 0
            for method, path in endpoints:
                try:
                    resp = await client.request(method, path, timeout=15)
                    if resp.status_code >= 200 and resp.status_code < 300:
                        print(f"    200 OK: {path}")
                    else:
                        print(f"    FAIL {resp.status_code}: {path} -> {resp.text[:200]}")
                        failures += 1
                except Exception as e:
                    print(f"    EXC: {path} -> {e}")
                    failures += 1
            if failures == 0:
                tests_passed += 1
                print("[2/3] Endpoint checks: PASS")
            else:
                tests_failed += 1
                print(f"[2/3] Endpoint checks: FAIL ({failures} failing endpoint(s))")
    except Exception as e:
        tests_failed += 1
        print(f"[2/3] HTTP client setup failed: {e}")

    # Shutdown handlers
    try:
        if app.router.on_shutdown:
            for handler in app.router.on_shutdown:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
        tests_passed += 1
        print("[3/3] Shutdown handlers: PASS")
    except Exception as e:
        print(f"[3/3] Shutdown handlers: FAIL -> {e}")
        tests_failed += 1

    print("\nSUMMARY: {} passed, {} failed".format(tests_passed, tests_failed))
    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    try:
        code = asyncio.run(run_probe())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        code = loop.run_until_complete(run_probe())
    sys.exit(code)
