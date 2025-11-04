from fastapi import Request

from backend.security.rate_limiter import rate_limit_key


class DummyScope(dict):
    def __init__(self, headers):
        super().__init__(type="http", headers=headers, client=("127.0.0.1", 12345))


def build_request(headers: dict) -> Request:
    header_items = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()]
    scope = DummyScope(header_items)
    return Request(scope)


def test_rate_limit_key_prefers_bearer_token():
    request = build_request({"Authorization": "Bearer secret-token"})
    assert rate_limit_key(request) == "secret-token"


def test_rate_limit_key_uses_api_key_header():
    request = build_request({"X-API-Key": "apikey123"})
    assert rate_limit_key(request) == "apikey123"


def test_rate_limit_key_falls_back_to_ip():
    request = build_request({})
    assert rate_limit_key(request) == "127.0.0.1"
