from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db

security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    sub: UUID            # user_id
    tenant_id: UUID
    role: str            # admin, sims_lid, tims_lid, discipline_eigenaar, lijnmanager, viewer
    domain: Optional[str] = None  # ISMS, PIMS, BCMS, or None (all)
    token_type: str = "user"  # "user" or "agent"
    agent_name: Optional[str] = None  # only for agent tokens


class CurrentUser(BaseModel):
    id: UUID
    tenant_id: UUID
    role: str
    domain: Optional[str] = None
    token_type: str = "user"
    agent_name: Optional[str] = None


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Convert UUIDs to strings for JSON serialization
    for key in ("sub", "tenant_id"):
        if key in to_encode and not isinstance(to_encode[key], str):
            to_encode[key] = str(to_encode[key])
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.now(timezone.utc)
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenData(
            sub=UUID(payload["sub"]),
            tenant_id=UUID(payload["tenant_id"]),
            role=payload["role"],
            domain=payload.get("domain"),
            token_type=payload.get("token_type", "user"),
            agent_name=payload.get("agent_name"),
        )
    except (JWTError, KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Extract and validate JWT token. Sets tenant_id on the DB session for RLS."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(credentials.credentials)

    # Set tenant_id on the DB session for RLS
    await db.execute(text(f"SET LOCAL app.current_tenant_id = '{token_data.tenant_id}'"))

    return CurrentUser(
        id=token_data.sub,
        tenant_id=token_data.tenant_id,
        role=token_data.role,
        domain=token_data.domain,
        token_type=token_data.token_type,
        agent_name=token_data.agent_name,
    )


def require_role(*roles: str):
    """Dependency that checks if the current user has one of the required roles.

    Role hierarchy: admin > sims_lid > tims_lid > discipline_eigenaar > lijnmanager > viewer
    Higher roles inherit all permissions of lower roles.
    """
    ROLE_HIERARCHY = {
        "admin": 6,
        "sims_lid": 5,
        "tims_lid": 4,
        "discipline_eigenaar": 3,
        "lijnmanager": 2,
        "viewer": 1,
    }

    # Find the minimum required level
    min_required = min(ROLE_HIERARCHY.get(r, 99) for r in roles)

    async def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_level < min_required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {', '.join(roles)}. Your role: {current_user.role}",
            )
        return current_user

    return dependency
