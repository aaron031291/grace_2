"""
CLI Test - Simple command line interface for Grace
Works with minimal_backend.py running on port 8000
"""

import sys
from typing import Dict, Any

sys.path.insert(0, '.')

try:
    import httpx
except Exception as e:
    print("ERROR: httpx is required. Install with: pip install httpx")
    sys.exit(1)

BASE_URL = 'http://localhost:8000'


def show_status() -> int:
    """Display cognition status from /api/status"""
    try:
        print("\n" + "=" * 60)
        print("GRACE COGNITION STATUS")
        print("=" * 60)

        response = httpx.get(f'{BASE_URL}/api/status', timeout=5)
        if response.status_code != 200:
            print(f"ERROR: /api/status returned {response.status_code}: {response.text}")
            return 1

        data: Dict[str, Any] = response.json()

        required_keys = {"overall_health", "overall_trust", "overall_confidence", "saas_ready", "domains"}
        missing = required_keys - set(data.keys())
        if missing:
            print(f"ERROR: /api/status missing keys: {sorted(missing)}")
            return 1

        print(f"\nOverall Metrics:")
        print(f"  Health:     {data['overall_health']:.1%}")
        print(f"  Trust:      {data['overall_trust']:.1%}")
        print(f"  Confidence: {data['overall_confidence']:.1%}")
        print(f"  SaaS Ready: {'YES' if data['saas_ready'] else 'NO'}")

        print(f"\nDomain Status ({len(data['domains'])} domains):")
        for name, domain in list(data['domains'].items())[:8]:
            try:
                print(f"  {name:15} {domain['health']:.1f}%")
            except Exception:
                print(f"  {name:15} (health: n/a)")

        print("\n" + "=" * 60)
        return 0

    except httpx.ConnectError:
        print("\nERROR: Backend not running")
        print("Start with: py minimal_backend.py")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


def smoke() -> int:
    """Run a smoke test across key endpoints and validate shapes"""
    failures = 0

    # /health
    try:
        r = httpx.get(f'{BASE_URL}/health', timeout=5)
        if r.status_code != 200 or r.json().get("status") != "ok":
            print(f"SMOKE FAIL: /health -> {r.status_code} {r.text}")
            failures += 1
        else:
            print("SMOKE OK: /health")
    except Exception as e:
        print(f"SMOKE FAIL: /health exception: {e}")
        failures += 1

    # /api/status
    try:
        r = httpx.get(f'{BASE_URL}/api/status', timeout=5)
        if r.status_code != 200:
            print(f"SMOKE FAIL: /api/status -> {r.status_code} {r.text}")
            failures += 1
        else:
            data = r.json()
            required = {"overall_health", "overall_trust", "overall_confidence", "saas_ready", "domains"}
            if required - set(data.keys()):
                print("SMOKE FAIL: /api/status missing required keys")
                failures += 1
            else:
                print("SMOKE OK: /api/status")
    except Exception as e:
        print(f"SMOKE FAIL: /api/status exception: {e}")
        failures += 1

    # /api/cognition/status
    try:
        r = httpx.get(f'{BASE_URL}/api/cognition/status', timeout=5)
        if r.status_code != 200:
            print(f"SMOKE FAIL: /api/cognition/status -> {r.status_code} {r.text}")
            failures += 1
        else:
            data = r.json()
            if not isinstance(data, dict) or not data:
                print("SMOKE FAIL: /api/cognition/status returned empty/invalid body")
                failures += 1
            else:
                print("SMOKE OK: /api/cognition/status")
    except Exception as e:
        print(f"SMOKE FAIL: /api/cognition/status exception: {e}")
        failures += 1

    if failures:
        print(f"\nSmoke test completed: {failures} failure(s)")
        return 1
    else:
        print("\nSmoke test passed: all checks OK")
        return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            code = show_status()
            sys.exit(code)
        elif cmd == "smoke":
            code = smoke()
            sys.exit(code)

    print("Grace CLI")
    print("\nUsage:")
    print("  py scripts\\cli_test.py status   - Show cognition status")
    print("  py scripts\\cli_test.py smoke    - Run smoke tests (/health, /api/status, /api/cognition/status)")
    print("\nMake sure backend is running:")
    print("  py minimal_backend.py")
    sys.exit(0)
