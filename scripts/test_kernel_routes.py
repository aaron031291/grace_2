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
            # Endpoint tuples: (method, path, json_payload_or_None)
            endpoints = [
                ("GET", "/health", None),
                ("GET", "/api/core/heartbeat", None),
                ("GET", "/api/core/governance", None),
                ("GET", "/api/core/verify?limit=10&hours_back=1", None),
                ("GET", "/api/core/metrics", None),
                ("GET", "/api/cognition/status", None),
                ("GET", "/api/cognition/readiness", None),
                ("GET", "/api/cognition/alerts", None),
                # Security domain (GET-only endpoints for probe)
                ("GET", "/api/security/rules", None),
                ("GET", "/api/security/alerts", None),
                ("GET", "/api/security/quarantined", None),
                ("GET", "/api/security/constitutional", None),
                ("GET", "/api/security/metrics", None),
                # ML domain (public list)
                ("GET", "/api/ml/models", None),
                # Trust API (public)
                ("GET", "/api/trust/sources", None),
                # Transcendence domain (basic POSTs with minimal bodies)
                ("POST", "/api/transcendence/plan", {"task_description": "probe task", "context": {}}),
                ("POST", "/api/transcendence/generate", {"specification": "print('hello')", "language": "python"}),
                ("POST", "/api/transcendence/memory/search", {"query": "probe", "limit": 1}),
                # Temporal domain
                ("GET", "/api/temporal/patterns", None),
            ]
            failures = 0
            for method, path, payload in endpoints:
                try:
                    kwargs = {"timeout": 20}
                    if payload is not None:
                        kwargs["json"] = payload
                    resp = await client.request(method, path, **kwargs)
                    if 200 <= resp.status_code < 300:
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
