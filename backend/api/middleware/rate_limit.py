import time
from collections import defaultdict, deque
from typing import Deque

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = structlog.get_logger(__name__)

# In-memory sliding window rate limiter.
# For production deploy, replace with Redis-backed storage.
_request_log: dict[str, Deque[float]] = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self._max = max_requests
        self._window = window_seconds

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        # Skip rate limiting for health/docs endpoints
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self._window
        log = _request_log[client]

        # Evict expired timestamps
        while log and log[0] < window_start:
            log.popleft()

        if len(log) >= self._max:
            logger.warning("rate_limit_exceeded", client=client, path=request.url.path)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {self._max} requests per {self._window}s."
                },
                headers={"Retry-After": str(self._window)},
            )

        log.append(now)
        return await call_next(request)
