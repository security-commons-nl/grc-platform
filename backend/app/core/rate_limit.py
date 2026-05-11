"""Rate limiting via SlowAPI.

In-memory storage — geschikt voor single-instance deployments. Voor
multi-instance (load-balanced) deployments: configureer Redis als
storage backend via SLOWAPI_STORAGE_URI (toekomstige uitbreiding).

Achter Caddy reverse proxy: zorg dat uvicorn met --forwarded-allow-ips
draait of dat Starlette's ProxyHeadersMiddleware actief is, zodat
X-Forwarded-For correct doorkomt en rate limits per echte client-IP
worden toegepast (niet per Caddy-IP).
"""

from slowapi import Limiter
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
    # 429 responses still get Retry-After via the default exception handler.
    headers_enabled=False,
)
