from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSControl, IMSRiskControlLink
from app.schemas.controls import ControlCreate, ControlUpdate, ControlResponse
from app.services.custom_fields import validate_custom_attributes
from app.services.org_units import descendants, validate_unit_in_tenant

router = APIRouter()


@router.get("/", response_model=list[ControlResponse])
async def list_controls(
    domain: str | None = None,
    implementation_status: str | None = None,
    requirement_id: UUID | None = None,
    organizational_unit_id: UUID | None = None,
    include_descendants: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSControl).where(IMSControl.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(IMSControl.domain == domain)
    if implementation_status:
        query = query.where(IMSControl.implementation_status == implementation_status)
    if requirement_id:
        query = query.where(IMSControl.requirement_id == requirement_id)
    # RFC 0002 — filter op organisatie-eenheid, optioneel inclusief sub-units.
    if organizational_unit_id is not None:
        if include_descendants:
            ids = await descendants(
                db, current_user.tenant_id, organizational_unit_id
            )
            query = query.where(IMSControl.organizational_unit_id.in_(ids))
        else:
            query = query.where(
                IMSControl.organizational_unit_id == organizational_unit_id
            )
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(
    control_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control niet gevonden")
    return control


@router.post("/", response_model=ControlResponse, status_code=201)
async def create_control(
    data: ControlCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    await validate_custom_attributes(
        db, current_user.tenant_id, "control", data.custom_attributes,
    )
    # RFC 0002 — org-unit moet binnen dezelfde tenant zitten.
    if data.organizational_unit_id is not None:
        unit = await validate_unit_in_tenant(
            db, current_user.tenant_id, data.organizational_unit_id
        )
        if not unit:
            raise HTTPException(
                status_code=422,
                detail="organizational_unit_id verwijst niet naar een unit binnen deze tenant",
            )
    payload = data.model_dump()
    if payload.get("custom_attributes") is None:
        payload["custom_attributes"] = {}
    control = IMSControl(tenant_id=current_user.tenant_id, **payload)
    db.add(control)
    await db.flush()
    await db.refresh(control)
    return control


@router.patch("/{control_id}", response_model=ControlResponse)
async def update_control(
    control_id: UUID,
    data: ControlUpdate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control niet gevonden")
    update_data = data.model_dump(exclude_unset=True)
    if "custom_attributes" in update_data:
        await validate_custom_attributes(
            db, current_user.tenant_id, "control", update_data["custom_attributes"],
        )
        if update_data["custom_attributes"] is None:
            update_data["custom_attributes"] = {}
    if (
        "organizational_unit_id" in update_data
        and update_data["organizational_unit_id"] is not None
    ):
        unit = await validate_unit_in_tenant(
            db, current_user.tenant_id, update_data["organizational_unit_id"]
        )
        if not unit:
            raise HTTPException(
                status_code=422,
                detail="organizational_unit_id verwijst niet naar een unit binnen deze tenant",
            )
    for field, value in update_data.items():
        setattr(control, field, value)
    await db.flush()
    await db.refresh(control)
    return control


@router.delete("/{control_id}", status_code=204)
async def delete_control(
    control_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control niet gevonden")
    # Delete associated risk-control links first
    links_result = await db.execute(
        select(IMSRiskControlLink).where(IMSRiskControlLink.control_id == control_id)
    )
    for link in links_result.scalars().all():
        await db.delete(link)
    await db.delete(control)
    await db.flush()
