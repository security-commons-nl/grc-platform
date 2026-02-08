"""
Organization Profile API — CRUD for onboarding wizard / organization profile.

One profile per tenant. Upsert pattern (create-or-update).
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.rbac import get_current_user, require_configurer
from app.models.core_models import OrganizationProfile, User

router = APIRouter()

# Fields per wizard step (for partial updates and completion calculation)
STEP_FIELDS: Dict[int, List[str]] = {
    0: [  # Blok 1: Identiteit
        "org_type", "sector", "employee_count", "location_count",
        "geographic_scope", "parent_organization", "core_services",
    ],
    1: [  # Blok 2: Governance
        "existing_certifications", "applicable_frameworks", "has_security_officer",
        "has_dpo", "governance_maturity", "risk_appetite_availability",
        "risk_appetite_integrity", "risk_appetite_confidentiality",
    ],
    2: [  # Blok 3: IT-Landschap
        "cloud_strategy", "cloud_providers", "workstation_count", "has_remote_work",
        "has_byod", "critical_systems", "outsourced_it", "primary_it_supplier",
    ],
    3: [  # Blok 4: Privacy
        "processes_personal_data", "data_subject_types", "has_special_categories",
        "international_transfers", "processing_count_estimate",
    ],
    4: [  # Blok 5: Continuiteit
        "has_bcp", "has_incident_response_plan", "max_tolerable_downtime",
        "critical_process_count", "key_dependencies",
    ],
    5: [  # Blok 6: Mensen
        "has_awareness_program", "has_background_checks", "training_frequency",
    ],
}

ALL_PROFILE_FIELDS = [f for fields in STEP_FIELDS.values() for f in fields]


def _calc_completion(profile: OrganizationProfile) -> int:
    """Calculate percentage of filled fields."""
    total = len(ALL_PROFILE_FIELDS)
    filled = sum(1 for f in ALL_PROFILE_FIELDS if getattr(profile, f, None) is not None)
    return round((filled / total) * 100) if total else 0


@router.get("/")
async def get_organization_profile(
    x_tenant_id: int = Header(1, alias="X-Tenant-ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get organization profile for the current tenant."""
    result = await session.execute(
        select(OrganizationProfile).where(OrganizationProfile.tenant_id == x_tenant_id)
    )
    profile = result.scalars().first()
    if not profile:
        # Return empty profile structure (not yet created)
        return {
            "tenant_id": x_tenant_id,
            "wizard_completed": False,
            "wizard_current_step": 0,
            "completion_pct": 0,
        }

    data = {c: getattr(profile, c) for c in profile.__fields__}
    data["completion_pct"] = _calc_completion(profile)
    return data


@router.put("/")
async def upsert_organization_profile(
    payload: Dict[str, Any],
    x_tenant_id: int = Header(1, alias="X-Tenant-ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_configurer),
):
    """Create or fully update organization profile."""
    result = await session.execute(
        select(OrganizationProfile).where(OrganizationProfile.tenant_id == x_tenant_id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = OrganizationProfile(tenant_id=x_tenant_id)
        session.add(profile)

    # Update all provided fields
    for key, value in payload.items():
        if hasattr(profile, key) and key not in ("id", "tenant_id"):
            setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    profile.updated_by_id = current_user.id

    await session.commit()
    await session.refresh(profile)

    data = {c: getattr(profile, c) for c in profile.__fields__}
    data["completion_pct"] = _calc_completion(profile)
    return data


@router.patch("/")
async def patch_organization_profile(
    payload: Dict[str, Any],
    x_tenant_id: int = Header(1, alias="X-Tenant-ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_configurer),
):
    """Partial update (e.g., per wizard step)."""
    result = await session.execute(
        select(OrganizationProfile).where(OrganizationProfile.tenant_id == x_tenant_id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = OrganizationProfile(tenant_id=x_tenant_id)
        session.add(profile)

    for key, value in payload.items():
        if hasattr(profile, key) and key not in ("id", "tenant_id"):
            setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    profile.updated_by_id = current_user.id

    await session.commit()
    await session.refresh(profile)

    data = {c: getattr(profile, c) for c in profile.__fields__}
    data["completion_pct"] = _calc_completion(profile)
    return data


@router.get("/completion")
async def get_profile_completion(
    x_tenant_id: int = Header(1, alias="X-Tenant-ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get completion percentage for the organization profile."""
    result = await session.execute(
        select(OrganizationProfile).where(OrganizationProfile.tenant_id == x_tenant_id)
    )
    profile = result.scalars().first()
    if not profile:
        return {"completion_pct": 0, "wizard_completed": False}
    return {
        "completion_pct": _calc_completion(profile),
        "wizard_completed": profile.wizard_completed,
    }
