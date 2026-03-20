from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSRisk, IMSRiskControlLink
from app.schemas.risks import (
    RiskCreate, RiskUpdate, RiskResponse,
    RiskControlLinkCreate, RiskControlLinkResponse,
)

router = APIRouter()


def calculate_risk_level(score: int) -> str:
    if score <= 4:
        return "groen"
    if score <= 9:
        return "geel"
    if score <= 14:
        return "oranje"
    return "rood"


# ── Risks ──────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[RiskResponse])
async def list_risks(
    tenant_id: UUID = Query(...),
    domain: str | None = None,
    status: str | None = None,
    scope_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRisk).where(IMSRisk.tenant_id == tenant_id)
    if domain:
        query = query.where(IMSRisk.domain == domain)
    if status:
        query = query.where(IMSRisk.status == status)
    if scope_id:
        query = query.where(IMSRisk.scope_id == scope_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(risk_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.post("/", response_model=RiskResponse, status_code=201)
async def create_risk(
    data: RiskCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    risk_score = data.likelihood * data.impact
    risk_level = calculate_risk_level(risk_score)

    risk_data = data.model_dump()
    risk_data.pop("likelihood", None)
    risk_data.pop("impact", None)

    risk = IMSRisk(
        tenant_id=tenant_id,
        likelihood=data.likelihood,
        impact=data.impact,
        risk_level=risk_level,
        **risk_data,
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return risk


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(risk_id: UUID, data: RiskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(risk, field, value)

    # Recalculate risk_level if likelihood or impact changed
    likelihood = update_data.get("likelihood", risk.likelihood)
    impact = update_data.get("impact", risk.impact)
    if "likelihood" in update_data or "impact" in update_data:
        risk_score = likelihood * impact
        risk.risk_level = calculate_risk_level(risk_score)

    await db.commit()
    await db.refresh(risk)
    return risk


@router.delete("/{risk_id}", status_code=204)
async def delete_risk(risk_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    # Delete associated risk-control links first
    links_result = await db.execute(
        select(IMSRiskControlLink).where(IMSRiskControlLink.risk_id == risk_id)
    )
    for link in links_result.scalars().all():
        await db.delete(link)
    await db.delete(risk)
    await db.commit()


# ── Risk-Control Links ─────────────────────────────────────────────────────


@router.get("/links/", response_model=list[RiskControlLinkResponse])
async def list_risk_control_links(
    risk_id: UUID | None = None,
    control_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRiskControlLink)
    if risk_id:
        query = query.where(IMSRiskControlLink.risk_id == risk_id)
    if control_id:
        query = query.where(IMSRiskControlLink.control_id == control_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/links/", response_model=RiskControlLinkResponse, status_code=201)
async def create_risk_control_link(data: RiskControlLinkCreate, db: AsyncSession = Depends(get_db)):
    link = IMSRiskControlLink(**data.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


@router.delete("/links/{risk_id}/{control_id}", status_code=204)
async def delete_risk_control_link(risk_id: UUID, control_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSRiskControlLink).where(
            and_(
                IMSRiskControlLink.risk_id == risk_id,
                IMSRiskControlLink.control_id == control_id,
            )
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="RiskControlLink not found")
    await db.delete(link)
    await db.commit()
