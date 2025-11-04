import pytest

from backend.security.sanitization import sanitize_text_value, SuspiciousInputError


def test_sanitize_text_value_allows_plain_text():
    assert sanitize_text_value("hello-world", field="username") == "hello-world"


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert('xss')</script>",
        "DROP TABLE users;",
        "SELECT * FROM accounts",
    ],
)
def test_sanitize_text_value_rejects_malicious_payload(payload: str):
    with pytest.raises(SuspiciousInputError):
        sanitize_text_value(payload, field="username")
