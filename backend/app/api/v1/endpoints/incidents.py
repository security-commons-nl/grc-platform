from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSIncident
from app.schemas.incidents import IncidentCreate, IncidentUpdate, IncidentResponse

router = APIRouter()


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    incident_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSIncident).where(IMSIncident.tenant_id == current_user.tenant_id)
    if incident_type:
        query = query.where(IMSIncident.incident_type == incident_type)
    if severity:
        query = query.where(IMSIncident.severity == severity)
    if status:
        query = query.where(IMSIncident.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSIncident).where(IMSIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    current_user: CurrentUser = Depends(require_role("lijnmanager")),
    db: AsyncSession = Depends(get_db),
):
    incident = IMSIncident(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(incident)
    await db.flush()
    await db.refresh(incident)
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    data: IncidentUpdate,
    current_user: CurrentUser = Depends(require_role("lijnmanager")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSIncident).where(IMSIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    await db.flush()
    await db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(
    incident_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSIncident).where(IMSIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await db.delete(incident)
    await db.flush()
