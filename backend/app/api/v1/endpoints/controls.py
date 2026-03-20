from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSControl, IMSRiskControlLink
from app.schemas.controls import ControlCreate, ControlUpdate, ControlResponse

router = APIRouter()


@router.get("/", response_model=list[ControlResponse])
async def list_controls(
    tenant_id: UUID = Query(...),
    domain: str | None = None,
    implementation_status: str | None = None,
    requirement_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSControl).where(IMSControl.tenant_id == tenant_id)
    if domain:
        query = query.where(IMSControl.domain == domain)
    if implementation_status:
        query = query.where(IMSControl.implementation_status == implementation_status)
    if requirement_id:
        query = query.where(IMSControl.requirement_id == requirement_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(control_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control


@router.post("/", response_model=ControlResponse, status_code=201)
async def create_control(
    data: ControlCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    control = IMSControl(tenant_id=tenant_id, **data.model_dump())
    db.add(control)
    await db.commit()
    await db.refresh(control)
    return control


@router.patch("/{control_id}", response_model=ControlResponse)
async def update_control(control_id: UUID, data: ControlUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(control, field, value)
    await db.commit()
    await db.refresh(control)
    return control


@router.delete("/{control_id}", status_code=204)
async def delete_control(control_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSControl).where(IMSControl.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    # Delete associated risk-control links first
    links_result = await db.execute(
        select(IMSRiskControlLink).where(IMSRiskControlLink.control_id == control_id)
    )
    for link in links_result.scalars().all():
        await db.delete(link)
    await db.delete(control)
    await db.commit()
