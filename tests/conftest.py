import os


# Ensure a deterministic secret key for test runs without exposing real credentials.
os.environ.setdefault("GRACE_JWT_SECRET", "test-suite-secret-key")
