from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import re

from app.core.db import get_session
from app.core.security import verify_password, get_password_hash
from app.core.crud import CRUDBase
from app.core.rbac import require_admin, get_user_roles, get_current_user
from app.core.jwt import create_access_token
from app.models.core_models import User, UserRead, UserScopeRole, Role, Tenant, TenantUser

router = APIRouter()
crud_user = CRUDBase(User)
limiter = Limiter(key_func=get_remote_address)


# =============================================================================
# REQUEST MODELS
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


def _validate_password_strength(password: str) -> str:
    """Enforce password complexity: min 8 chars, 1 uppercase, 1 digit."""
    if len(password) < 8:
        raise ValueError("Wachtwoord moet minimaal 8 tekens zijn")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Wachtwoord moet minimaal 1 hoofdletter bevatten")
    if not re.search(r"\d", password):
        raise ValueError("Wachtwoord moet minimaal 1 cijfer bevatten")
    return password


class ChangePasswordRequest(BaseModel):
    """Admin changes another user's password."""
    user_id: int
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password_strength(v)


class ResetMyPasswordRequest(BaseModel):
    """User changes own password."""
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password_strength(v)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Validate credentials and return JWT access token + user data."""
    user = await crud_user.get_by_field(session, "username", credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is gedeactiveerd")

    if not user.password_hash:
        raise HTTPException(status_code=401, detail="Geen wachtwoord ingesteld voor dit account")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")

    # Update last_login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Fetch all tenant memberships for this user
    # TenantUser is NOT RLS-protected in the same way (or we access it via superuser/direct filtering if needed, 
    # but here we just need to know which tenants the user BELONGS to).
    # Note: TenantUser table does not have RLS policy dependent on app.current_tenant in the same way 
    # (it is a join table).
    tu_result = await session.execute(
        select(TenantUser, Tenant)
        .join(Tenant, TenantUser.tenant_id == Tenant.id)
        .where(
            TenantUser.user_id == user.id,
            TenantUser.is_active == True,
            Tenant.is_active == True,
        )
        .order_by(TenantUser.is_default.desc(), TenantUser.id.asc())
    )
    memberships = tu_result.all()

    tenants = []
    default_tenant_id = None
    tenant_name = ""
    for tu, tenant in memberships:
        t_info = {
            "id": tenant.id,
            "name": tenant.display_name or tenant.name,
            "slug": tenant.slug,
            "is_default": tu.is_default,
        }
        tenants.append(t_info)
        if tu.is_default:
            default_tenant_id = tenant.id
            tenant_name = tenant.display_name or tenant.name

    # Fallback: if no default set, use first membership
    if not default_tenant_id and tenants:
        default_tenant_id = tenants[0]["id"]
        tenant_name = tenants[0]["name"]
        tenants[0]["is_default"] = True

    # -------------------------------------------------------------------------
    # RLS CONTEXT SETUP
    # -------------------------------------------------------------------------
    # CRITICAL: We MUST set app.current_tenant before accessing RLS-protected tables
    # like UserScopeRole or Scope.
    if default_tenant_id:
        from sqlalchemy import text
        # Use set_config because SET command does not support bind parameters in asyncpg
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tenant_id, false)"), 
            {"tenant_id": str(default_tenant_id)}
        )

    # -------------------------------------------------------------------------
    # FETCH ROLES (RLS Protected)
    # -------------------------------------------------------------------------
    # Fetch user roles across all scopes (now safe because tenant is set)
    # Note: get_user_roles might inherently filter by the *current* tenant if it uses RLS,
    # or we might want to pass the tenant_id explicitly if the function supports it.
    roles = await get_user_roles(user, session, tenant_id=default_tenant_id)
    role_names = sorted({r.value for r in roles})

    # Build permissions map
    is_admin = user.is_superuser or Role.BEHEERDER in roles
    permissions = {
        "is_admin": is_admin,
        "can_edit": is_admin or bool(roles.intersection({
            Role.COORDINATOR, Role.EIGENAAR, Role.MEDEWERKER,
        })),
        "can_configure": is_admin or bool(roles.intersection({
            Role.COORDINATOR, Role.EIGENAAR,
        })),
        "can_manage_users": is_admin or Role.COORDINATOR in roles,
        "can_write_findings": is_admin or bool(roles.intersection({
            Role.COORDINATOR, Role.TOEZICHTHOUDER,
        })),
    }

    # Create JWT token
    access_token = create_access_token(
        user_id=user.id,
        tenant_id=default_tenant_id,
    )

    # Return user data + RBAC info + JWT
    user_data = UserRead.model_validate(user).model_dump()
    user_data["access_token"] = access_token
    user_data["token_type"] = "bearer"
    user_data["global_roles"] = role_names
    user_data["permissions"] = permissions
    user_data["tenant_name"] = tenant_name
    user_data["tenants"] = tenants
    user_data["default_tenant_id"] = default_tenant_id

    return user_data


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Admin changes another user's password. Requires Beheerder role."""
    target = await crud_user.get_or_404(session, req.user_id)

    target.password_hash = get_password_hash(req.new_password)
    session.add(target)
    await session.commit()

    return {"message": f"Wachtwoord van {target.username} is gewijzigd"}


@router.post("/reset-my-password")
async def reset_my_password(
    req: ResetMyPasswordRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """User changes own password (must be authenticated, verifies old password)."""
    if not current_user.password_hash or not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Huidig wachtwoord is onjuist")

    current_user.password_hash = get_password_hash(req.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "Wachtwoord is gewijzigd"}
