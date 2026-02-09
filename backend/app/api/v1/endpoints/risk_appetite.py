"""
Risk Appetite Endpoints — Organisatie-brede risicotolerantie.

CRUD for RiskAppetite + evaluation endpoints that check
RiskScopes against the active appetite thresholds.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import TenantCRUDBase
from app.core.rbac import require_admin, require_editor, get_tenant_id, get_scope_access
from app.core.risk_appetite_engine import (
    classify_cell,
    generate_heatmap_matrix,
    evaluate_risk_scope,
    evaluate_scope_risks_bulk,
    RISK_LEVEL_VALUE,
    HeatmapZone,
)
from app.models.core_models import (
    RiskAppetite,
    RiskAppetiteLevel,
    RiskLevel,
    RiskScope,
    Risk,
    User,
)

router = APIRouter()
crud_appetite = TenantCRUDBase(RiskAppetite)


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class HeatmapCell(BaseModel):
    likelihood: int
    impact: int
    score: int
    zone: str

class HeatmapResponse(BaseModel):
    appetite_level: str
    matrix: list[list[HeatmapCell]]

class RiskEvaluation(BaseModel):
    risk_scope_id: Optional[int]
    risk_id: Optional[int]
    scope_id: Optional[int]
    is_acceptable: Optional[bool]
    zone: Optional[str]
    requires_decision: bool
    requires_escalation: bool
    residual_score: Optional[int] = None
    appetite_level: Optional[str] = None
    reason: str

class BulkEvaluationResponse(BaseModel):
    total: int
    acceptable: int
    conditional: int
    escalation: int
    unacceptable: int
    not_assessed: int
    requires_decision_count: int
    details: list[RiskEvaluation]


# =============================================================================
# HELPERS
# =============================================================================

async def _get_current_appetite(
    session: AsyncSession, tenant_id: int
) -> RiskAppetite:
    """Get the current active appetite for a tenant, or 404."""
    result = await session.execute(
        select(RiskAppetite).where(
            RiskAppetite.tenant_id == tenant_id,
            RiskAppetite.is_current == True,
        )
    )
    appetite = result.scalars().first()
    if not appetite:
        raise HTTPException(
            status_code=404,
            detail="Geen actieve Risk Appetite geconfigureerd. Maak eerst een appetite-instelling aan.",
        )
    return appetite


# =============================================================================
# CRUD
# =============================================================================

@router.get("/", response_model=List[RiskAppetite])
async def list_risk_appetites(
    skip: int = 0,
    limit: int = 100,
    current_only: bool = Query(False, description="Only return current/active appetite"),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """List all risk appetite definitions (including historical versions)."""
    filters = {}
    if current_only:
        filters["is_current"] = True
    return await crud_appetite.get_multi(session, tenant_id, skip=skip, limit=limit, filters=filters)


@router.get("/current", response_model=RiskAppetite)
async def get_current_appetite(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get the currently active risk appetite."""
    return await _get_current_appetite(session, tenant_id)


@router.post("/", response_model=RiskAppetite, status_code=201)
async def create_risk_appetite(
    appetite: RiskAppetite,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """
    Create a new risk appetite definition.
    If is_current=True, deactivates any existing current appetite for this tenant.
    """
    appetite.tenant_id = tenant_id
    appetite.id = None

    if appetite.is_current:
        # Deactivate existing current appetites
        result = await session.execute(
            select(RiskAppetite).where(
                RiskAppetite.tenant_id == tenant_id,
                RiskAppetite.is_current == True,
            )
        )
        for existing in result.scalars().all():
            existing.is_current = False
            session.add(existing)

    session.add(appetite)
    await session.commit()
    await session.refresh(appetite)
    return appetite


@router.patch("/{appetite_id}", response_model=RiskAppetite)
async def update_risk_appetite(
    appetite_id: int,
    appetite_update: dict,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Update a risk appetite definition."""
    db_appetite = await crud_appetite.get_or_404(session, appetite_id, tenant_id)

    # If setting as current, deactivate others
    if appetite_update.get("is_current"):
        result = await session.execute(
            select(RiskAppetite).where(
                RiskAppetite.tenant_id == tenant_id,
                RiskAppetite.is_current == True,
                RiskAppetite.id != appetite_id,
            )
        )
        for existing in result.scalars().all():
            existing.is_current = False
            session.add(existing)

    appetite_update["updated_at"] = datetime.utcnow()
    return await crud_appetite.update(session, db_obj=db_appetite, obj_in=appetite_update, tenant_id=tenant_id)


@router.delete("/{appetite_id}")
async def delete_risk_appetite(
    appetite_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Delete a risk appetite (only non-current)."""
    db_appetite = await crud_appetite.get_or_404(session, appetite_id, tenant_id)
    if db_appetite.is_current:
        raise HTTPException(
            status_code=400,
            detail="Kan actieve appetite niet verwijderen. Maak eerst een nieuwe versie aan.",
        )
    deleted = await crud_appetite.delete(session, id=appetite_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Appetite not found")
    return {"message": "Risk appetite deleted"}


@router.post("/{appetite_id}/activate", response_model=RiskAppetite)
async def activate_risk_appetite(
    appetite_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Set a risk appetite as the current active one. Deactivates others."""
    db_appetite = await crud_appetite.get_or_404(session, appetite_id, tenant_id)

    # Deactivate all others
    result = await session.execute(
        select(RiskAppetite).where(
            RiskAppetite.tenant_id == tenant_id,
            RiskAppetite.is_current == True,
        )
    )
    for existing in result.scalars().all():
        existing.is_current = False
        session.add(existing)

    db_appetite.is_current = True
    db_appetite.updated_at = datetime.utcnow()
    session.add(db_appetite)
    await session.commit()
    await session.refresh(db_appetite)
    return db_appetite


# =============================================================================
# HEATMAP GENERATION
# =============================================================================

@router.get("/heatmap", response_model=HeatmapResponse)
async def get_appetite_heatmap(
    appetite_level: Optional[RiskAppetiteLevel] = Query(
        None, description="Override appetite level (uses current if not set)"
    ),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Generate the 4×4 heatmap matrix with zone classifications based on appetite.

    Zones:
    - acceptable: Within appetite (green)
    - conditional: Conditionally acceptable (yellow)
    - escalation: Needs management decision (orange)
    - unacceptable: Must mitigate (red)
    """
    if appetite_level is None:
        appetite = await _get_current_appetite(session, tenant_id)
        appetite_level = appetite.overall_appetite

    matrix = generate_heatmap_matrix(appetite_level)
    return HeatmapResponse(
        appetite_level=appetite_level.value,
        matrix=matrix,
    )


@router.get("/heatmap/{domain}", response_model=HeatmapResponse)
async def get_domain_heatmap(
    domain: str,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Generate a domain-specific heatmap (e.g., /heatmap/financial).
    Uses the domain-specific appetite level if configured, else overall.
    """
    appetite = await _get_current_appetite(session, tenant_id)

    domain_map = {
        "financial": appetite.financial_appetite,
        "financieel": appetite.financial_appetite,
        "isms": appetite.isms_appetite,
        "operational": appetite.isms_appetite,
        "privacy": appetite.pims_appetite,
        "pims": appetite.pims_appetite,
        "bcm": appetite.bcms_appetite,
        "continuity": appetite.bcms_appetite,
        "compliance": appetite.compliance_appetite,
        "legal": appetite.compliance_appetite,
        "reputation": appetite.reputational_appetite,
    }

    level = domain_map.get(domain.lower(), appetite.overall_appetite) or appetite.overall_appetite

    matrix = generate_heatmap_matrix(level)
    return HeatmapResponse(
        appetite_level=level.value,
        matrix=matrix,
    )


# =============================================================================
# RISK EVALUATION
# =============================================================================

@router.get("/evaluate/{risk_scope_id}", response_model=RiskEvaluation)
async def evaluate_single_risk(
    risk_scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Evaluate a single RiskScope against the current appetite."""
    appetite = await _get_current_appetite(session, tenant_id)

    # Get RiskScope
    result = await session.execute(
        select(RiskScope).where(
            RiskScope.id == risk_scope_id,
            RiskScope.tenant_id == tenant_id,
        )
    )
    rs = result.scalars().first()
    if not rs:
        raise HTTPException(status_code=404, detail="RiskScope not found")

    if accessible_scopes is not None and rs.scope_id not in accessible_scopes:
        raise HTTPException(status_code=403, detail="No access to this scope")

    # Get risk category for domain-specific appetite
    result = await session.execute(
        select(Risk.risk_category).where(Risk.id == rs.risk_id)
    )
    category = result.scalar_one_or_none()

    evaluation = evaluate_risk_scope(rs, appetite, category)
    return RiskEvaluation(
        risk_scope_id=rs.id,
        risk_id=rs.risk_id,
        scope_id=rs.scope_id,
        **evaluation,
    )


@router.get("/evaluate/scope/{scope_id}", response_model=BulkEvaluationResponse)
async def evaluate_scope_risks(
    scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Evaluate all risks in a scope against the current appetite."""
    if accessible_scopes is not None and scope_id not in accessible_scopes:
        raise HTTPException(status_code=403, detail="No access to this scope")

    appetite = await _get_current_appetite(session, tenant_id)

    result = await session.execute(
        select(RiskScope).where(
            RiskScope.scope_id == scope_id,
            RiskScope.tenant_id == tenant_id,
        )
    )
    risk_scopes = result.scalars().all()

    stats = evaluate_scope_risks_bulk(list(risk_scopes), appetite)
    return BulkEvaluationResponse(**stats)


@router.get("/evaluate/tenant", response_model=BulkEvaluationResponse)
async def evaluate_all_tenant_risks(
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Evaluate all risks across the tenant against the current appetite (dashboard)."""
    appetite = await _get_current_appetite(session, tenant_id)

    query = select(RiskScope).where(RiskScope.tenant_id == tenant_id)
    if accessible_scopes is not None:
        query = query.where(RiskScope.scope_id.in_(accessible_scopes))

    result = await session.execute(query)
    risk_scopes = result.scalars().all()

    stats = evaluate_scope_risks_bulk(list(risk_scopes), appetite)
    return BulkEvaluationResponse(**stats)
