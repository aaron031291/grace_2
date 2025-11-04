# Observability Stack

## Logging

- JSON-formatted logs emitted via `backend/observability.py`.
- `LOG_LEVEL` environment variable controls verbosity.
- Request-scoped fields (`request_id`, path, duration) are appended automatically.
- Use `logger = logging.getLogger(__name__)` in modules instead of `print()`.

## Request tracing

- Middleware attaches `X-Request-ID` to every response; clients may pass their own header to correlate calls.
- Request start/finish events are logged under the `request` logger with durations in milliseconds.

## Usage

```bash
LOG_LEVEL=DEBUG py minimal_backend.py
```

## Next steps for AMP

- Hook the JSON stream into ELK/Loki.
- Add OpenTelemetry exporters once infrastructure is ready.
- Gradually replace remaining `print()` statements in edge modules with structured logs.
