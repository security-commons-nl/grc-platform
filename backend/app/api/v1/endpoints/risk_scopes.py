"""
Risk-Scope Contextualisatie Endpoints
CRUD for RiskScope: scope-specific risk scores, treatment, and acceptance.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import ScopedTenantCRUDBase
from app.core.rbac import require_editor, require_configurer, get_tenant_id, get_scope_access
from app.models.core_models import (
    Risk,
    RiskAppetite,
    RiskScope,
    Scope,
    Control,
    Decision,
    ControlRiskScopeLink,
    DecisionRiskScopeLink,
    User,
)
from app.core.risk_appetite_engine import evaluate_risk_scope
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
crud_risk = ScopedTenantCRUDBase(Risk)
crud_scope = ScopedTenantCRUDBase(Scope)


async def _check_appetite_warning(
    session: AsyncSession,
    risk_scope: RiskScope,
    tenant_id: int,
) -> Optional[dict]:
    """Check RiskScope against active appetite; return warning dict if outside tolerance."""
    result = await session.execute(
        select(RiskAppetite).where(
            RiskAppetite.tenant_id == tenant_id,
            RiskAppetite.is_current == True,
        )
    )
    appetite = result.scalars().first()
    if not appetite:
        return None

    # Get risk category
    result = await session.execute(
        select(Risk.risk_category).where(Risk.id == risk_scope.risk_id)
    )
    category = result.scalar_one_or_none()

    evaluation = evaluate_risk_scope(risk_scope, appetite, category)
    if evaluation.get("is_acceptable") is False:
        return {
            "appetite_warning": evaluation["reason"],
            "zone": evaluation["zone"],
            "requires_decision": evaluation["requires_decision"],
            "requires_escalation": evaluation["requires_escalation"],
        }
    return None


# =============================================================================
# RISKSCOPE CRUD
# =============================================================================

@router.get("/", response_model=List[RiskScope])
async def list_risk_scopes(
    skip: int = 0,
    limit: int = 100,
    risk_id: Optional[int] = Query(None, description="Filter by risk"),
    scope_id: Optional[int] = Query(None, description="Filter by scope"),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """List all risk-scope contextualizations, optionally filtered."""
    query = select(RiskScope).where(RiskScope.tenant_id == tenant_id)

    if risk_id is not None:
        query = query.where(RiskScope.risk_id == risk_id)
    if scope_id is not None:
        query = query.where(RiskScope.scope_id == scope_id)

    # Scope-based access control
    if accessible_scopes is not None:
        query = query.where(RiskScope.scope_id.in_(accessible_scopes))

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{risk_scope_id}", response_model=RiskScope)
async def get_risk_scope(
    risk_scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific risk-scope contextualization."""
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

    return rs


@router.post("/", response_model=RiskScope, status_code=201)
async def create_risk_scope(
    risk_scope: RiskScope,
    response: Response,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Create a new risk-scope contextualization (link a risk to a scope with scores)."""
    # Verify risk exists in tenant
    await crud_risk.get_scoped_or_404(session, risk_scope.risk_id, tenant_id, accessible_scopes)
    # Verify scope exists in tenant
    await crud_scope.get_scoped_or_404(session, risk_scope.scope_id, tenant_id, accessible_scopes)

    # Check for duplicate
    result = await session.execute(
        select(RiskScope).where(
            RiskScope.tenant_id == tenant_id,
            RiskScope.risk_id == risk_scope.risk_id,
            RiskScope.scope_id == risk_scope.scope_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Risk is already linked to this scope")

    risk_scope.tenant_id = tenant_id
    risk_scope.id = None
    session.add(risk_scope)
    await session.commit()
    await session.refresh(risk_scope)

    # Check appetite and add warning header if outside tolerance
    warning = await _check_appetite_warning(session, risk_scope, tenant_id)
    if warning:
        response.headers["X-Appetite-Warning"] = warning["appetite_warning"]
        response.headers["X-Appetite-Zone"] = warning["zone"]

    return risk_scope


@router.put("/{risk_scope_id}", response_model=RiskScope)
async def update_risk_scope(
    risk_scope_id: int,
    risk_scope_update: RiskScope,
    response: Response,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Update scores, treatment, acceptance on a risk-scope contextualization."""
    result = await session.execute(
        select(RiskScope).where(
            RiskScope.id == risk_scope_id,
            RiskScope.tenant_id == tenant_id,
        )
    )
    db_rs = result.scalars().first()
    if not db_rs:
        raise HTTPException(status_code=404, detail="RiskScope not found")

    if accessible_scopes is not None and db_rs.scope_id not in accessible_scopes:
        raise HTTPException(status_code=403, detail="No access to this scope")

    # Update all provided fields (exclude id, tenant_id, risk_id, scope_id)
    update_data = risk_scope_update.model_dump(
        exclude_unset=True,
        exclude={"id", "tenant_id", "risk_id", "scope_id"},
    )
    for key, value in update_data.items():
        setattr(db_rs, key, value)

    db_rs.updated_at = datetime.utcnow()
    session.add(db_rs)
    await session.commit()
    await session.refresh(db_rs)

    # Check appetite and add warning header if outside tolerance
    warning = await _check_appetite_warning(session, db_rs, tenant_id)
    if warning:
        response.headers["X-Appetite-Warning"] = warning["appetite_warning"]
        response.headers["X-Appetite-Zone"] = warning["zone"]

    return db_rs


@router.delete("/{risk_scope_id}")
async def delete_risk_scope(
    risk_scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_configurer),
):
    """Delete a risk-scope contextualization."""
    result = await session.execute(
        select(RiskScope).where(
            RiskScope.id == risk_scope_id,
            RiskScope.tenant_id == tenant_id,
        )
    )
    db_rs = result.scalars().first()
    if not db_rs:
        raise HTTPException(status_code=404, detail="RiskScope not found")

    if accessible_scopes is not None and db_rs.scope_id not in accessible_scopes:
        raise HTTPException(status_code=403, detail="No access to this scope")

    await session.delete(db_rs)
    await session.commit()
    return {"message": "RiskScope deleted"}


# =============================================================================
# CONVENIENCE: SCOPE -> RISKS and RISK -> SCOPES
# =============================================================================

@router.get("/by-scope/{scope_id}", response_model=List[RiskScope])
async def get_risks_for_scope(
    scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all risk contextualizations for a specific scope."""
    await crud_scope.get_scoped_or_404(session, scope_id, tenant_id, accessible_scopes)

    result = await session.execute(
        select(RiskScope).where(
            RiskScope.scope_id == scope_id,
            RiskScope.tenant_id == tenant_id,
        )
    )
    return result.scalars().all()


@router.get("/by-risk/{risk_id}", response_model=List[RiskScope])
async def get_scopes_for_risk(
    risk_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all scope contextualizations for a specific risk."""
    await crud_risk.get_scoped_or_404(session, risk_id, tenant_id, accessible_scopes)

    query = select(RiskScope).where(
        RiskScope.risk_id == risk_id,
        RiskScope.tenant_id == tenant_id,
    )

    if accessible_scopes is not None:
        query = query.where(RiskScope.scope_id.in_(accessible_scopes))

    result = await session.execute(query)
    return result.scalars().all()


# =============================================================================
# CONTROL-RISKSCOPE LINKING
# =============================================================================

@router.post("/{risk_scope_id}/controls/{control_id}")
async def link_control_to_risk_scope(
    risk_scope_id: int,
    control_id: int,
    mitigation_percent: int = Query(50, ge=0, le=100),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Link a control to a scope-contextualized risk."""
    # Verify risk_scope exists
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

    # Check duplicate
    result = await session.execute(
        select(ControlRiskScopeLink).where(
            ControlRiskScopeLink.control_id == control_id,
            ControlRiskScopeLink.risk_scope_id == risk_scope_id,
            ControlRiskScopeLink.tenant_id == tenant_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = ControlRiskScopeLink(
        tenant_id=tenant_id,
        control_id=control_id,
        risk_scope_id=risk_scope_id,
        mitigation_percent=mitigation_percent,
    )
    session.add(link)
    await session.commit()
    return {"message": "Control linked to risk scope"}


@router.delete("/{risk_scope_id}/controls/{control_id}")
async def unlink_control_from_risk_scope(
    risk_scope_id: int,
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Remove link between control and scope-contextualized risk."""
    result = await session.execute(
        select(ControlRiskScopeLink).where(
            ControlRiskScopeLink.control_id == control_id,
            ControlRiskScopeLink.risk_scope_id == risk_scope_id,
            ControlRiskScopeLink.tenant_id == tenant_id,
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()
    return {"message": "Control unlinked from risk scope"}


@router.get("/{risk_scope_id}/controls", response_model=List[Control])
async def get_risk_scope_controls(
    risk_scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all controls linked to a scope-contextualized risk."""
    # Verify access
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

    result = await session.execute(
        select(Control)
        .join(ControlRiskScopeLink, Control.id == ControlRiskScopeLink.control_id)
        .where(ControlRiskScopeLink.risk_scope_id == risk_scope_id)
    )
    return result.scalars().all()


# =============================================================================
# DECISION-RISKSCOPE LINKING
# =============================================================================

@router.post("/{risk_scope_id}/decisions/{decision_id}")
async def link_decision_to_risk_scope(
    risk_scope_id: int,
    decision_id: int,
    notes: Optional[str] = None,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_configurer),
):
    """Link a decision to a scope-contextualized risk."""
    # Verify risk_scope exists
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

    # Check duplicate
    result = await session.execute(
        select(DecisionRiskScopeLink).where(
            DecisionRiskScopeLink.decision_id == decision_id,
            DecisionRiskScopeLink.risk_scope_id == risk_scope_id,
            DecisionRiskScopeLink.tenant_id == tenant_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = DecisionRiskScopeLink(
        tenant_id=tenant_id,
        decision_id=decision_id,
        risk_scope_id=risk_scope_id,
        notes=notes,
    )
    session.add(link)
    await session.commit()
    return {"message": "Decision linked to risk scope"}


@router.delete("/{risk_scope_id}/decisions/{decision_id}")
async def unlink_decision_from_risk_scope(
    risk_scope_id: int,
    decision_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_configurer),
):
    """Remove link between decision and scope-contextualized risk."""
    result = await session.execute(
        select(DecisionRiskScopeLink).where(
            DecisionRiskScopeLink.decision_id == decision_id,
            DecisionRiskScopeLink.risk_scope_id == risk_scope_id,
            DecisionRiskScopeLink.tenant_id == tenant_id,
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()
    return {"message": "Decision unlinked from risk scope"}


@router.get("/{risk_scope_id}/decisions", response_model=List[Decision])
async def get_risk_scope_decisions(
    risk_scope_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all decisions linked to a scope-contextualized risk."""
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

    result = await session.execute(
        select(Decision)
        .join(DecisionRiskScopeLink, Decision.id == DecisionRiskScopeLink.decision_id)
        .where(DecisionRiskScopeLink.risk_scope_id == risk_scope_id)
    )
    return result.scalars().all()
