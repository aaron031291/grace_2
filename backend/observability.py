import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


_REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
_LOGGING_CONFIGURED = False


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = _REQUEST_ID.get()
        if request_id:
            log["request_id"] = request_id

        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log.update(record.extra_fields)

        return json.dumps(log)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        token = _REQUEST_ID.set(request_id)

        logger = logging.getLogger("request")
        logger.info(
            "request.start",
            extra={"extra_fields": {"path": str(request.url.path), "method": request.method}},
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "request.complete",
                extra={
                    "extra_fields": {
                        "path": str(request.url.path),
                        "method": request.method,
                        "duration_ms": duration_ms,
                    }
                },
            )
            _REQUEST_ID.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response


def configure_logging() -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(level=level)
    root = logging.getLogger()
    for handler in root.handlers:
        handler.setFormatter(JSONFormatter())

    # Reduce noisy libraries
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)

    _LOGGING_CONFIGURED = True


def setup_observability(app) -> None:
    configure_logging()
    app.add_middleware(RequestContextMiddleware)
