from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.rate_limit import limiter

router = APIRouter()


@router.get("")
@limiter.exempt
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health endpoint — onbeperkt aanroepbaar (exempt van rate limiting).

    Load balancers, monitoring en orchestrators (Kubernetes liveness probes,
    Caddy healthchecks) pollen dit endpoint frequent. Rate-limiting hierop
    zou tot vals-positieve 'unhealthy' meldingen leiden.
    """
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
