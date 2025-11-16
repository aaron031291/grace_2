import os
import sys
import json
import time
from urllib import request, parse, error

"""
Health smoke script (observe-only, safe):
- Posts a degraded latency signal for service 'backend_api'
- Fetches health state
- Calls triage/diagnose
- Requests a dry-run playbook plan

Usage (Windows):
  py scripts\health_smoke.py [base_url]
Default base_url: http://localhost:8000

Requires:
- API running
- Auth token in env AUTH_TOKEN (Bearer <token>) or unauthenticated if your dev server allows it.
"""

def _hdrs():
    token = os.getenv("AUTH_TOKEN")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _post(url: str, payload: dict) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=_hdrs(), method="POST")
    try:
        with request.urlopen(req, timeout=10) as resp:
            return resp.getcode(), resp.read().decode("utf-8")
    except error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


def _get(url: str) -> tuple[int, str]:
    req = request.Request(url, headers=_hdrs(), method="GET")
    try:
        with request.urlopen(req, timeout=10) as resp:
            return resp.getcode(), resp.read().decode("utf-8")
    except error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BASE_URL", "http://localhost:8000")
    service = os.getenv("SMOKE_SERVICE", "backend_api")

    print(f"Health smoke against {base} (service={service})")

    # 1) Ingest a degraded latency signal
    code, body = _post(
        f"{base}/api/health/ingest_signal",
        {
            "service": service,
            "signal_type": "http",
            "metric_key": "latency_ms",
            "value": 1200,
            "status": "degraded",
            "severity": "high",
        },
    )
    print("ingest_signal:", code, body)
    if code not in (200, 201):
        print("Smoke failed at ingest_signal")
        sys.exit(1)

    time.sleep(0.2)

    # 2) Get health state
    code, body = _get(f"{base}/api/health/state?service={parse.quote(service)}")
    print("health/state:", code, body)
    if code != 200:
        print("Smoke failed at health/state")
        sys.exit(1)

    time.sleep(0.2)

    # 3) Diagnose
    code, body = _post(f"{base}/api/triage/diagnose", {"service": service})
    print("triage/diagnose:", code, body)
    if code != 200:
        print("Smoke failed at triage/diagnose")
        sys.exit(1)

    # 4) Request a dry-run plan (use latency_spike diagnosis by default)
    code, body = _post(
        f"{base}/api/playbooks/plan",
        {"service": service, "diagnosis": "latency_spike", "severity": "high"},
    )
    print("playbooks/plan:", code, body)
    if code != 200:
        print("Smoke failed at playbooks/plan")
        sys.exit(1)

    print("Health smoke: OK")


if __name__ == "__main__":
    main()
