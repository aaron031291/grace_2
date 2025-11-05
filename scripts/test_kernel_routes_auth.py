"""
Kernel Routes Auth Probe
- Imports backend.main.app
- Runs startup handlers
- Registers/logs in a temp user and calls protected endpoints with JWT
- Runs shutdown handlers

Windows: py scripts\test_kernel_routes_auth.py
"""

import asyncio
import sys
from pathlib import Path
import time

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
        print("[1/4] Startup handlers: PASS")
    except Exception as e:
        print(f"[1/4] Startup handlers: FAIL -> {e}")
        tests_failed += 1

    # In-process HTTP client using ASGI transport
    token = None
    try:
        import httpx
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Register or login
            username = f"probe_user_{int(time.time())}"
            password = "Probing123!"
            try:
                r = await client.post("/api/auth/register", json={"username": username, "password": password})
                if r.status_code not in (200, 201):
                    # If already exists, try login
                    r = await client.post("/api/auth/login", json={"username": username, "password": password})
            except Exception as e:
                print(f"    Auth EXC: {e}")
                raise

            if r.status_code not in (200, 201):
                print(f"    FAIL auth: {r.status_code} {r.text}")
                raise RuntimeError("auth failed")

            data = r.json()
            token = data.get("access_token")
            if not token:
                raise RuntimeError("no access_token in response")

            headers = {"Authorization": f"Bearer {token}"}

            endpoints = [
                ("GET", "/api/verification/stats?hours_back=1"),
                ("GET", "/api/dashboard/cognitive/current"),
                ("GET", "/api/ingest/artifacts?limit=1"),
                # Added kernel coverage under auth
                ("GET", "/api/parliament/members"),
                ("GET", "/api/temporal/patterns"),
                # Federation (safe read-only)
                ("GET", "/api/external/secrets"),
            ]
            failures = 0
            for method, path in endpoints:
                try:
                    resp = await client.request(method, path, headers=headers, timeout=30)
                    if resp.status_code >= 200 and resp.status_code < 300:
                        print(f"    200 OK (auth): {path}")
                    else:
                        print(f"    FAIL {resp.status_code} (auth): {path} -> {resp.text[:200]}")
                        failures += 1
                except Exception as e:
                    print(f"    EXC (auth): {path} -> {e}")
                    failures += 1
            if failures == 0:
                tests_passed += 1
                print("[2/4] Protected endpoint checks: PASS")
            else:
                tests_failed += 1
                print(f"[2/4] Protected endpoint checks: FAIL ({failures} failing endpoint(s))")

            # Also test trust source listing (public) to ensure consistency
            r = await client.get("/api/trust/sources")
            if r.status_code == 200:
                tests_passed += 1
                print("[3/4] Trust sources list: PASS")
            else:
                tests_failed += 1
                print(f"[3/4] Trust sources list: FAIL -> {r.status_code}")
    except Exception as e:
        tests_failed += 1
        print(f"[2-3/4] HTTP client/auth failed: {e}")

    # Shutdown handlers
    try:
        if app.router.on_shutdown:
            for handler in app.router.on_shutdown:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
        tests_passed += 1
        print("[4/4] Shutdown handlers: PASS")
    except Exception as e:
        print(f"[4/4] Shutdown handlers: FAIL -> {e}")
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
