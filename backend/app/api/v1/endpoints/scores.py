from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSMaturityProfile, IMSSetupScore, IMSGRCScore
from app.schemas.scores import (
    MaturityProfileCreate, MaturityProfileUpdate, MaturityProfileResponse,
    SetupScoreCreate, SetupScoreUpdate, SetupScoreResponse,
    GRCScoreCreate, GRCScoreUpdate, GRCScoreResponse,
)

router = APIRouter()


# ── Maturity Profiles ──────────────────────────────────────────────────────


@router.get("/maturity-profiles/", response_model=list[MaturityProfileResponse])
async def list_maturity_profiles(
    domain: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSMaturityProfile).where(IMSMaturityProfile.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(IMSMaturityProfile.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/maturity-profiles/{profile_id}", response_model=MaturityProfileResponse)
async def get_maturity_profile(
    profile_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSMaturityProfile).where(IMSMaturityProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="MaturityProfile not found")
    return profile


@router.post("/maturity-profiles/", response_model=MaturityProfileResponse, status_code=201)
async def create_maturity_profile(
    data: MaturityProfileCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    profile = IMSMaturityProfile(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.patch("/maturity-profiles/{profile_id}", response_model=MaturityProfileResponse)
async def update_maturity_profile(
    profile_id: UUID,
    data: MaturityProfileUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSMaturityProfile).where(IMSMaturityProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="MaturityProfile not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.delete("/maturity-profiles/{profile_id}", status_code=204)
async def delete_maturity_profile(
    profile_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSMaturityProfile).where(IMSMaturityProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="MaturityProfile not found")
    await db.delete(profile)
    await db.flush()


# ── Setup Scores ───────────────────────────────────────────────────────────


@router.get("/setup-scores/", response_model=list[SetupScoreResponse])
async def list_setup_scores(
    domain: str | None = None,
    cyclus_year: int | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSSetupScore).where(IMSSetupScore.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(IMSSetupScore.domain == domain)
    if cyclus_year:
        query = query.where(IMSSetupScore.cyclus_year == cyclus_year)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/setup-scores/{score_id}", response_model=SetupScoreResponse)
async def get_setup_score(
    score_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSSetupScore).where(IMSSetupScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="SetupScore not found")
    return score


@router.post("/setup-scores/", response_model=SetupScoreResponse, status_code=201)
async def create_setup_score(
    data: SetupScoreCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    score = IMSSetupScore(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(score)
    await db.flush()
    await db.refresh(score)
    return score


@router.patch("/setup-scores/{score_id}", response_model=SetupScoreResponse)
async def update_setup_score(
    score_id: UUID,
    data: SetupScoreUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSSetupScore).where(IMSSetupScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="SetupScore not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(score, field, value)
    await db.flush()
    await db.refresh(score)
    return score


@router.delete("/setup-scores/{score_id}", status_code=204)
async def delete_setup_score(
    score_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSSetupScore).where(IMSSetupScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="SetupScore not found")
    await db.delete(score)
    await db.flush()


# ── GRC Scores ─────────────────────────────────────────────────────────────


@router.get("/grc-scores/", response_model=list[GRCScoreResponse])
async def list_grc_scores(
    domain: str | None = None,
    cyclus_year: int | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSGRCScore).where(IMSGRCScore.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(IMSGRCScore.domain == domain)
    if cyclus_year:
        query = query.where(IMSGRCScore.cyclus_year == cyclus_year)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/grc-scores/{score_id}", response_model=GRCScoreResponse)
async def get_grc_score(
    score_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSGRCScore).where(IMSGRCScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="GRCScore not found")
    return score


@router.post("/grc-scores/", response_model=GRCScoreResponse, status_code=201)
async def create_grc_score(
    data: GRCScoreCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    score = IMSGRCScore(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(score)
    await db.flush()
    await db.refresh(score)
    return score


@router.patch("/grc-scores/{score_id}", response_model=GRCScoreResponse)
async def update_grc_score(
    score_id: UUID,
    data: GRCScoreUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSGRCScore).where(IMSGRCScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="GRCScore not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(score, field, value)
    await db.flush()
    await db.refresh(score)
    return score


@router.delete("/grc-scores/{score_id}", status_code=204)
async def delete_grc_score(
    score_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSGRCScore).where(IMSGRCScore.id == score_id))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="GRCScore not found")
    await db.delete(score)
    await db.flush()
