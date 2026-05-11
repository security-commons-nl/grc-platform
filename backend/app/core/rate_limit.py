"""Rate limiting via SlowAPI.

In-memory storage — geschikt voor single-instance deployments. Voor
multi-instance (load-balanced) deployments: configureer Redis als
storage backend via SLOWAPI_STORAGE_URI (toekomstige uitbreiding).

Achter Caddy reverse proxy: zorg dat uvicorn met --forwarded-allow-ips
draait of dat Starlette's ProxyHeadersMiddleware actief is, zodat
X-Forwarded-For correct doorkomt en rate limits per echte client-IP
worden toegepast (niet per Caddy-IP).
"""

from fastapi import Request
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_ENABLED else [],
    enabled=settings.RATE_LIMIT_ENABLED,
    # headers_enabled=True injects X-RateLimit-* on every 200 response, but
    # slowapi 0.1.9 + FastAPI/Starlette ASGI middleware order causes an
    # "parameter `response` must be an instance of starlette.responses.Response"
    # error when the route doesn't take an explicit response parameter.
    # We compensate by setting Retry-After in our own exception handler below.
    headers_enabled=False,
)


def _parse_retry_after_seconds(detail: str) -> int:
    """Parse a slowapi limit string like '10 per 1 minute' into a Retry-After
    value in seconds. Fallback to 60 if parsing fails."""
    parts = detail.lower().split()
    try:
        idx = parts.index("per")
        amount = int(parts[idx + 1])
        unit = parts[idx + 2]
        if unit.startswith("second"):
            return amount
        if unit.startswith("minute"):
            return amount * 60
        if unit.startswith("hour"):
            return amount * 3600
        if unit.startswith("day"):
            return amount * 86400
    except (ValueError, IndexError):
        pass
    return 60


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom 429 handler that always sets Retry-After.

    Required because we disabled slowapi's automatic header injection
    (see headers_enabled=False above). Without this, clients have no
    machine-readable hint when to retry.
    """
    retry_after = _parse_retry_after_seconds(str(exc.detail))
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )
    response.headers["Retry-After"] = str(retry_after)
    return response
