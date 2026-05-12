"""CRUD voor organisatie-eenheden (RFC 0002).

Hiërarchische units onder een tenant met cycle- en depth-prevention.
Tenant-isolatie via RLS én expliciete tenant_id-filter (defense-in-depth).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSOrganizationalUnit
from app.schemas.organizational_units import (
    OrganizationalUnitCreate,
    OrganizationalUnitResponse,
    OrganizationalUnitTreeNode,
    OrganizationalUnitUpdate,
)
from app.services.org_units import (
    MAX_DEPTH,
    depth_of,
    descendants,
    validate_unit_in_tenant,
    would_create_cycle,
)

router = APIRouter()


def _build_tree(
    units: list[IMSOrganizationalUnit],
) -> list[OrganizationalUnitTreeNode]:
    """Bouw boom uit vlakke lijst (root-units zonder parent als top-niveau)."""
    nodes: dict[UUID, OrganizationalUnitTreeNode] = {
        u.id: OrganizationalUnitTreeNode.model_validate(u) for u in units
    }
    roots: list[OrganizationalUnitTreeNode] = []
    for u in units:
        node = nodes[u.id]
        if u.parent_id and u.parent_id in nodes:
            nodes[u.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


@router.get("/", response_model=list[OrganizationalUnitResponse])
async def list_units(
    is_active: bool | None = Query(None, description="Filter op actieve units."),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSOrganizationalUnit).where(
        IMSOrganizationalUnit.tenant_id == current_user.tenant_id
    )
    if is_active is not None:
        query = query.where(IMSOrganizationalUnit.is_active == is_active)
    query = query.order_by(
        IMSOrganizationalUnit.parent_id.nulls_first(),
        IMSOrganizationalUnit.name,
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tree", response_model=list[OrganizationalUnitTreeNode])
async def list_units_tree(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Geneste boom-representatie van alle (actieve én inactieve) units."""
    result = await db.execute(
        select(IMSOrganizationalUnit)
        .where(IMSOrganizationalUnit.tenant_id == current_user.tenant_id)
        .order_by(IMSOrganizationalUnit.name)
    )
    return _build_tree(list(result.scalars().all()))


@router.get(
    "/{unit_id}/descendants",
    response_model=list[UUID],
    description="IDs van de unit zelf plus alle descendants. Lege lijst bij 404.",
)
async def list_descendants(
    unit_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    unit = await validate_unit_in_tenant(db, current_user.tenant_id, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Organisatie-eenheid niet gevonden")
    return await descendants(db, current_user.tenant_id, unit_id)


@router.get("/{unit_id}", response_model=OrganizationalUnitResponse)
async def get_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    unit = await validate_unit_in_tenant(db, current_user.tenant_id, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Organisatie-eenheid niet gevonden")
    return unit


@router.post("/", response_model=OrganizationalUnitResponse, status_code=201)
async def create_unit(
    data: OrganizationalUnitCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    # Parent moet binnen dezelfde tenant vallen + diepte-limiet checken.
    if data.parent_id is not None:
        parent = await validate_unit_in_tenant(
            db, current_user.tenant_id, data.parent_id
        )
        if not parent:
            raise HTTPException(
                status_code=422,
                detail="parent_id verwijst niet naar een unit binnen deze tenant",
            )
        parent_depth = await depth_of(db, current_user.tenant_id, data.parent_id)
        if parent_depth + 1 > MAX_DEPTH:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Boomdiepte zou {parent_depth + 1} worden; maximum is {MAX_DEPTH}."
                ),
            )

    unit = IMSOrganizationalUnit(
        tenant_id=current_user.tenant_id,
        **data.model_dump(),
    )
    db.add(unit)
    await db.flush()
    await db.refresh(unit)
    return unit


@router.patch("/{unit_id}", response_model=OrganizationalUnitResponse)
async def update_unit(
    unit_id: UUID,
    data: OrganizationalUnitUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    unit = await validate_unit_in_tenant(db, current_user.tenant_id, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Organisatie-eenheid niet gevonden")

    update_data = data.model_dump(exclude_unset=True)

    if "parent_id" in update_data and update_data["parent_id"] is not None:
        new_parent_id = update_data["parent_id"]
        # 1. parent moet bestaan binnen tenant
        parent = await validate_unit_in_tenant(
            db, current_user.tenant_id, new_parent_id
        )
        if not parent:
            raise HTTPException(
                status_code=422,
                detail="parent_id verwijst niet naar een unit binnen deze tenant",
            )
        # 2. nieuwe parent mag geen descendant zijn (cyclus voorkomen)
        if await would_create_cycle(
            db, current_user.tenant_id, unit_id, new_parent_id
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Nieuwe parent is een descendant van deze unit; dat zou "
                    "een cyclus introduceren."
                ),
            )
        # 3. nieuwe diepte ≤ MAX_DEPTH (parent_depth + 1)
        parent_depth = await depth_of(db, current_user.tenant_id, new_parent_id)
        if parent_depth + 1 > MAX_DEPTH:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Boomdiepte zou {parent_depth + 1} worden; maximum is {MAX_DEPTH}."
                ),
            )

    for field, value in update_data.items():
        setattr(unit, field, value)

    await db.flush()
    await db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=204)
async def delete_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    unit = await validate_unit_in_tenant(db, current_user.tenant_id, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Organisatie-eenheid niet gevonden")
    # Kinderen of FK-referenties → 409 (geen cascade om datacorruptie te voorkomen).
    children_result = await db.execute(
        select(IMSOrganizationalUnit).where(
            IMSOrganizationalUnit.parent_id == unit_id,
            IMSOrganizationalUnit.tenant_id == current_user.tenant_id,
        )
    )
    if children_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Unit heeft sub-units; verwijder of verplaats die eerst. "
                "Soft-delete via is_active=false als alternatief."
            ),
        )
    await db.delete(unit)
    await db.flush()
    return None
