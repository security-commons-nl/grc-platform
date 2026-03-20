from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSEvidence
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate, EvidenceResponse

router = APIRouter()


@router.get("/", response_model=list[EvidenceResponse])
async def list_evidence(
    tenant_id: UUID = Query(...),
    control_id: UUID | None = None,
    evidence_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSEvidence).where(IMSEvidence.tenant_id == tenant_id)
    if control_id:
        query = query.where(IMSEvidence.control_id == control_id)
    if evidence_type:
        query = query.where(IMSEvidence.evidence_type == evidence_type)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSEvidence).where(IMSEvidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.post("/", response_model=EvidenceResponse, status_code=201)
async def create_evidence(
    data: EvidenceCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    evidence = IMSEvidence(tenant_id=tenant_id, **data.model_dump())
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.patch("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(evidence_id: UUID, data: EvidenceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSEvidence).where(IMSEvidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(evidence, field, value)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=204)
async def delete_evidence(evidence_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSEvidence).where(IMSEvidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    await db.delete(evidence)
    await db.commit()
