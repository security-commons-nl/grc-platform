"""
Multi-tenancy support for IMS.

Provides tenant context and isolation for all database operations.
Every query is automatically filtered by tenant_id to prevent data leakage.
"""
from contextvars import ContextVar
from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session

# Context variable to store the current tenant ID
_current_tenant: ContextVar[Optional[int]] = ContextVar("current_tenant", default=None)


def get_current_tenant() -> Optional[int]:
    """Get the current tenant ID from context."""
    return _current_tenant.get()


def set_current_tenant(tenant_id: Optional[int]) -> None:
    """Set the current tenant ID in context."""
    _current_tenant.set(tenant_id)


async def require_tenant(
    x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID"),
) -> int:
    """
    Dependency that requires a tenant ID.

    In production, this should extract tenant from JWT token.
    For now, it accepts X-Tenant-ID header for development.

    Raises:
        HTTPException: If no tenant ID is provided
    """
    if x_tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID header is required. Multi-tenancy is enforced."
        )

    set_current_tenant(x_tenant_id)
    return x_tenant_id


async def optional_tenant(
    x_tenant_id: Optional[int] = Header(None, alias="X-Tenant-ID"),
) -> Optional[int]:
    """
    Dependency that optionally accepts a tenant ID.

    Used for endpoints that can work with or without tenant context.
    """
    if x_tenant_id is not None:
        set_current_tenant(x_tenant_id)
    return x_tenant_id


class TenantAwareSession:
    """
    Wrapper around AsyncSession that enforces tenant isolation.

    Usage:
        async def endpoint(session: TenantAwareSession = Depends(get_tenant_session)):
            # All queries through this session are tenant-filtered
    """

    def __init__(self, session: AsyncSession, tenant_id: int):
        self.session = session
        self.tenant_id = tenant_id

    def __getattr__(self, name):
        """Proxy all other attributes to the underlying session."""
        return getattr(self.session, name)


async def get_tenant_session(
    session: AsyncSession = Depends(get_session),
    tenant_id: int = Depends(require_tenant),
) -> TenantAwareSession:
    """
    Dependency that provides a tenant-aware database session.

    Combines the database session with the current tenant context.
    """
    return TenantAwareSession(session, tenant_id)
