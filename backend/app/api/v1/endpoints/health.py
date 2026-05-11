import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.rate_limit import limiter

router = APIRouter()


@router.get("")
@limiter.exempt
async def health_check(db: AsyncSession = Depends(get_db)):
    """Basic health endpoint — onbeperkt aanroepbaar (exempt van rate limiting).

    Load balancers, monitoring en orchestrators (Kubernetes liveness probes,
    Caddy healthchecks) pollen dit endpoint frequent. Rate-limiting hierop
    zou tot vals-positieve 'unhealthy' meldingen leiden.
    """
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@router.get("/details")
@limiter.exempt
async def health_details(db: AsyncSession = Depends(get_db)):
    """Uitgebreide health-check voor monitoring tools.

    Rapporteert: database-latency, AI-provider configuratie, observability-
    status en environment. Bevat géén secrets (alleen booleans en URLs
    zonder API-keys).

    Status-veld: 'ok' als alle checks slagen, 'degraded' als de database
    bereikbaar is maar trager dan 1000ms (configurable threshold in toekomst).
    """
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_latency_ms = int((time.perf_counter() - db_start) * 1000)
        db_connected = True
    except Exception:
        db_latency_ms = -1
        db_connected = False

    status = "ok"
    if not db_connected:
        status = "unhealthy"
    elif db_latency_ms > 1000:
        status = "degraded"

    return {
        "status": status,
        "environment": settings.ENVIRONMENT,
        "database": {
            "connected": db_connected,
            "latency_ms": db_latency_ms,
        },
        "ai_provider": {
            "configured": bool(settings.AI_API_KEY),
            "base_url": settings.AI_API_BASE,
            "model": settings.AI_MODEL_NAME,
        },
        "observability": {
            "langfuse_configured": bool(
                settings.LANGFUSE_SECRET_KEY
                and settings.LANGFUSE_PUBLIC_KEY
                and settings.LANGFUSE_HOST
            ),
        },
        "rate_limit": {
            "enabled": settings.RATE_LIMIT_ENABLED,
            "default": settings.RATE_LIMIT_DEFAULT,
            "auth": settings.RATE_LIMIT_AUTH,
        },
    }
