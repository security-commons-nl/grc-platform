from datetime import timedelta
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_token, CurrentUser, get_current_user, require_role
from app.core.config import settings
from app.core.db import get_db
from app.core.rate_limit import limiter
from app.models.core_models import IMSAISystem

router = APIRouter()


# Maximum lifetime for an agent token (NHI): 24 hours.
# Shorter tokens = smaller blast radius if leaked. For long-lived
# automation, rotate tokens via a scheduled job rather than minting
# year-long credentials.
AGENT_TOKEN_MAX_TTL_MINUTES = 24 * 60
AGENT_TOKEN_DEFAULT_TTL_MINUTES = 60


class DevTokenRequest(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str = "admin"
    domain: Optional[str] = None


class AgentTokenRequest(BaseModel):
    tenant_id: UUID
    agent_name: str
    role: str = "viewer"  # agents get minimal permissions by default
    scope: list[str] = Field(
        default_factory=lambda: ["read"],
        description="Fine-grained capabilities granted to this agent token. "
                    "Examples: 'risks:read', 'risks:write', 'controls:read'.",
    )
    ttl_minutes: int = Field(
        default=AGENT_TOKEN_DEFAULT_TTL_MINUTES,
        ge=1,
        le=AGENT_TOKEN_MAX_TTL_MINUTES,
        description=f"Token lifetime in minutes (max {AGENT_TOKEN_MAX_TTL_MINUTES} = 24h).",
    )
    ai_system_id: Optional[UUID] = Field(
        default=None,
        description="Optional link to an entry in ims_ai_systems for traceability.",
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: Optional[list[str]] = None
    ai_system_id: Optional[UUID] = None


@router.post("/dev-token", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def create_dev_token(request: Request, data: DevTokenRequest):
    """Generate a development JWT token. Only available when ENVIRONMENT=development."""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev tokens are only available in development mode",
        )

    expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_token(
        {
            "sub": str(data.user_id),
            "tenant_id": str(data.tenant_id),
            "role": data.role,
            "domain": data.domain,
            "token_type": "user",
        },
        expires_delta=expires,
    )
    return TokenResponse(
        access_token=token,
        expires_in=int(expires.total_seconds()),
    )


@router.post("/agent-token", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def create_agent_token(
    request: Request,
    data: AgentTokenRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Issue a Non-Human Identity (NHI) token for an AI agent or automation.

    Tokens are short-lived (default 60 min, max 24 h) and scoped to specific
    capabilities. Optionally linked to an entry in the AI-systemenregister
    (`ims_ai_systems`) so every agent action can be traced back to a
    registered AI system. Admin only.
    """
    # If linked to an AI system, verify it exists in the same tenant.
    # Prevents an admin of tenant A from minting tokens that claim to
    # represent an AI system of tenant B.
    if data.ai_system_id is not None:
        result = await db.execute(
            select(IMSAISystem).where(
                IMSAISystem.id == data.ai_system_id,
                IMSAISystem.tenant_id == data.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ai_system_id not found in this tenant",
            )

    expires = timedelta(minutes=data.ttl_minutes)
    payload = {
        "sub": str(current_user.id),  # issuing user
        "tenant_id": str(data.tenant_id),
        "role": data.role,
        "token_type": "agent",
        "agent_name": data.agent_name,
        "scope": data.scope,
    }
    if data.ai_system_id is not None:
        payload["ai_system_id"] = str(data.ai_system_id)

    token = create_token(payload, expires_delta=expires)
    return TokenResponse(
        access_token=token,
        expires_in=int(expires.total_seconds()),
        scope=data.scope,
        ai_system_id=data.ai_system_id,
    )


@router.get("/me", response_model=dict)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Return the current user's token claims."""
    return {
        "id": str(current_user.id),
        "tenant_id": str(current_user.tenant_id),
        "role": current_user.role,
        "domain": current_user.domain,
        "token_type": current_user.token_type,
        "agent_name": current_user.agent_name,
        "scope": current_user.scope,
        "ai_system_id": str(current_user.ai_system_id) if current_user.ai_system_id else None,
    }
