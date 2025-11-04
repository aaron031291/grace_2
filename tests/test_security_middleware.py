from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.security import setup_security_middleware


app = FastAPI()
setup_security_middleware(app, rate_limit=3, window_seconds=1)


@app.post("/echo")
async def echo(payload: dict):
    return payload


def test_suspicious_payload_rejected():
    client = TestClient(app)
    response = client.post("/echo", json={"message": "<script>alert('x')</script>"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Request blocked by security filters."


def test_rate_limiter():
    client = TestClient(app)
    for _ in range(3):
        resp = client.post("/echo", json={"message": "ok"})
        assert resp.status_code == 200
    throttled = client.post("/echo", json={"message": "ok"})
    assert throttled.status_code == 429
