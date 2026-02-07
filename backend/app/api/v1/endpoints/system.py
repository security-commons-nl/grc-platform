"""
System Administration Endpoints
Health checks, stats, and audit log for admin panel.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
import httpx

from app.core.db import get_session
from app.core.config import settings
from app.models.core_models import User

router = APIRouter()


@router.get("/health")
async def system_health(
    session: AsyncSession = Depends(get_session),
):
    """System health check: DB, Ollama, API version."""
    health = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": {"status": "unknown"},
        "ollama": {"status": "unknown"},
    }

    # DB check
    try:
        result = await session.execute(select(func.count()).select_from(User))
        count = result.scalar()
        health["database"] = {"status": "ok", "user_count": count}
    except Exception as e:
        health["database"] = {"status": "error", "detail": str(e)}

    # Ollama check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                health["ollama"] = {
                    "status": "ok",
                    "models": len(models),
                    "url": settings.OLLAMA_BASE_URL,
                }
            else:
                health["ollama"] = {"status": "error", "detail": f"HTTP {resp.status_code}"}
    except Exception:
        health["ollama"] = {"status": "offline", "url": settings.OLLAMA_BASE_URL}

    return health


@router.get("/stats")
async def system_stats(
    session: AsyncSession = Depends(get_session),
):
    """System statistics for admin overview."""
    # Total users
    total_result = await session.execute(select(func.count()).select_from(User))
    total_users = total_result.scalar() or 0

    # Active users
    active_result = await session.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_result.scalar() or 0

    # Superusers (beheerders)
    admin_result = await session.execute(
        select(func.count()).select_from(User).where(User.is_superuser == True)
    )
    admin_users = admin_result.scalar() or 0

    # Inactive users
    inactive_users = total_users - active_users

    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "inactive_users": inactive_users,
    }


@router.get("/audit-log")
async def audit_log(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    """Recent login activity (based on last_login field)."""
    result = await session.execute(
        select(User)
        .where(User.last_login != None)
        .order_by(User.last_login.desc())
        .limit(limit)
    )
    users = result.scalars().all()

    return [
        {
            "user_id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "is_active": u.is_active,
        }
        for u in users
    ]
