"""
Backend Startup Probe (backend.main)
- Imports backend.main.app
- Runs startup events to initialize DBs and services
- Then runs shutdown to clean up

Windows: py scripts\test_backend_startup_backend.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def run_startup_shutdown():
    print("=" * 80)
    print("BACKEND.STARTUP: backend.main")
    print("=" * 80)
    tests_passed = 0
    tests_failed = 0

    try:
        import backend.main as m
        app = m.app
        print("[1/4] Import backend.main: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"[1/4] Import backend.main: FAIL -> {e}")
        return 1

    # Run startup events
    try:
        if app.router.on_startup:
            print("[2/4] Running startup events...")
            for handler in app.router.on_startup:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            print("        Startup: PASS")
            tests_passed += 1
        else:
            print("[2/4] No startup handlers registered (OK)")
            tests_passed += 1
    except Exception as e:
        print(f"[2/4] Startup failed: {e}")
        tests_failed += 1

    # Basic checks after startup
    try:
        # Metrics engine/session should be present
        me = getattr(app.state, 'metrics_engine', None)
        ms = getattr(app.state, 'metrics_session', None)
        assert me is not None, "metrics_engine missing"
        assert ms is not None, "metrics_session missing"
        print("[3/4] Metrics DB initialized: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"[3/4] Metrics DB check: FAIL -> {e}")
        tests_failed += 1

    # Run shutdown events
    try:
        if app.router.on_shutdown:
            print("[4/4] Running shutdown events...")
            for handler in app.router.on_shutdown:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            print("        Shutdown: PASS")
            tests_passed += 1
        else:
            print("[4/4] No shutdown handlers registered (OK)")
            tests_passed += 1
    except Exception as e:
        print(f"[4/4] Shutdown failed: {e}")
        tests_failed += 1

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print("=" * 80)

    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    try:
        code = asyncio.run(run_startup_shutdown())
    except RuntimeError as e:
        # In case of nested event loop (e.g., if run in certain environments)
        loop = asyncio.get_event_loop()
        code = loop.run_until_complete(run_startup_shutdown())
    sys.exit(code)
