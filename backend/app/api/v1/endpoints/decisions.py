from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSDecision
from app.schemas.decisions import DecisionCreate, DecisionResponse

router = APIRouter()


@router.get("/", response_model=list[DecisionResponse])
async def list_decisions(
    tenant_id: UUID = Query(...),
    decision_type: str | None = None,
    gremium: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSDecision).where(IMSDecision.tenant_id == tenant_id)
    if decision_type:
        query = query.where(IMSDecision.decision_type == decision_type)
    if gremium:
        query = query.where(IMSDecision.gremium == gremium)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(decision_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSDecision).where(IMSDecision.id == decision_id))
    decision = result.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.post("/", response_model=DecisionResponse, status_code=201)
async def create_decision(
    data: DecisionCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    # Mandatering validation
    if data.decision_type in ("restrisico_acceptatie", "beleidsafwijking"):
        if data.gremium != "sims":
            raise HTTPException(
                status_code=422,
                detail="Restrisico/beleidsafwijking vereist SIMS-accordering",
            )

    decision = IMSDecision(tenant_id=tenant_id, **data.model_dump())
    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    return decision
