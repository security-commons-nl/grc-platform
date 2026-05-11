"""AI-systemenregister endpoints (M4 — AI Governance).

CRUD voor `ims_ai_systems` met tenant-isolatie via RLS en RBAC via
require_role. Mapt naar EU AI Act-risicoclassificatie (art. 5-7) en
NIST AI RMF-kernfuncties.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSAISystem
from app.schemas.ai_systems import (
    AISystemCreate,
    AISystemResponse,
    AISystemUpdate,
)
from app.services.eu_ai_act_classifier import suggest_risk

router = APIRouter()


class ClassifyRequest(BaseModel):
    system_type: str
    description: str = ""
    use_case: str = ""


class ClassifySuggestion(BaseModel):
    suggested_risk: str
    reasoning: str
    triggered_by: list[str]


@router.post("/classify-suggestion", response_model=ClassifySuggestion)
async def classify_suggestion(
    data: ClassifyRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Suggereer een EU AI Act-risicocategorie op basis van beschrijving.

    **Advies-only.** De suggestie moet door een menselijke beoordelaar
    worden bevestigd en handmatig op het AI-systeem gezet worden.
    Het advies is deterministisch (keyword-based) zodat het zelf auditbaar
    is — geen LLM in de loop voor deze classificatie.
    """
    suggestion = suggest_risk(
        system_type=data.system_type,
        description=data.description,
        use_case=data.use_case,
    )
    return ClassifySuggestion(
        suggested_risk=suggestion.suggested_risk,
        reasoning=suggestion.reasoning,
        triggered_by=suggestion.triggered_by,
    )


@router.get("/", response_model=list[AISystemResponse])
async def list_ai_systems(
    eu_ai_act_risk: str | None = Query(None, description="Filter op EU AI Act risico-categorie"),
    deployment_status: str | None = Query(None, description="Filter op levenscyclus-status"),
    system_type: str | None = Query(None, description="Filter op systeem-type"),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSAISystem).where(IMSAISystem.tenant_id == current_user.tenant_id)
    if eu_ai_act_risk:
        query = query.where(IMSAISystem.eu_ai_act_risk == eu_ai_act_risk)
    if deployment_status:
        query = query.where(IMSAISystem.deployment_status == deployment_status)
    if system_type:
        query = query.where(IMSAISystem.system_type == system_type)
    query = query.order_by(IMSAISystem.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{ai_system_id}", response_model=AISystemResponse)
async def get_ai_system(
    ai_system_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSAISystem).where(
            IMSAISystem.id == ai_system_id,
            IMSAISystem.tenant_id == current_user.tenant_id,
        )
    )
    ai_system = result.scalar_one_or_none()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI-systeem niet gevonden")
    return ai_system


@router.post("/", response_model=AISystemResponse, status_code=201)
async def create_ai_system(
    data: AISystemCreate,
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
    db: AsyncSession = Depends(get_db),
):
    ai_system = IMSAISystem(
        tenant_id=current_user.tenant_id,
        **data.model_dump(),
    )
    db.add(ai_system)
    await db.flush()
    await db.refresh(ai_system)
    return ai_system


@router.patch("/{ai_system_id}", response_model=AISystemResponse)
async def update_ai_system(
    ai_system_id: UUID,
    data: AISystemUpdate,
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSAISystem).where(
            IMSAISystem.id == ai_system_id,
            IMSAISystem.tenant_id == current_user.tenant_id,
        )
    )
    ai_system = result.scalar_one_or_none()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI-systeem niet gevonden")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(ai_system, key, value)
    await db.flush()
    await db.refresh(ai_system)
    return ai_system


@router.delete("/{ai_system_id}", status_code=204)
async def delete_ai_system(
    ai_system_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSAISystem).where(
            IMSAISystem.id == ai_system_id,
            IMSAISystem.tenant_id == current_user.tenant_id,
        )
    )
    ai_system = result.scalar_one_or_none()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI-systeem niet gevonden")
    await db.delete(ai_system)
    await db.flush()
    return None
