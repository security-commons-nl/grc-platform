from datetime import timedelta
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import create_token, CurrentUser, get_current_user, require_role
from app.core.config import settings

router = APIRouter()


class DevTokenRequest(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str = "admin"
    domain: Optional[str] = None


class AgentTokenRequest(BaseModel):
    tenant_id: UUID
    agent_name: str
    role: str = "viewer"  # agents get minimal permissions by default


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/dev-token", response_model=TokenResponse)
async def create_dev_token(data: DevTokenRequest):
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
async def create_agent_token(
    data: AgentTokenRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Generate a service token for an AI agent. Admin only."""
    expires = timedelta(days=30)  # Agent tokens live longer
    token = create_token(
        {
            "sub": str(current_user.id),  # issuing user
            "tenant_id": str(data.tenant_id),
            "role": data.role,
            "token_type": "agent",
            "agent_name": data.agent_name,
        },
        expires_delta=expires,
    )
    return TokenResponse(
        access_token=token,
        expires_in=int(expires.total_seconds()),
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
    }
