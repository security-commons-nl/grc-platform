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
    headers_enabled=True,
)
