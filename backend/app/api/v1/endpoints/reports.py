"""
Reporting Endpoints
Provides aggregated statistics and compliance reports for dashboards.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import func

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.core.rbac import get_tenant_id
from app.models.core_models import (
    Risk,
    Measure,
    Assessment,
    Incident,
    Policy,
    Scope,
    ApplicabilityStatement,
    Finding,
    CorrectiveAction,
    AttentionQuadrant,
    RiskLevel,
    Status,
    PolicyState,
    ImplementationStatus,
    CoverageType,
    FindingSeverity,
)

router = APIRouter()


# =============================================================================
# EXECUTIVE DASHBOARD
# =============================================================================

@router.get("/dashboard/executive", response_model=dict)
async def get_executive_dashboard(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get executive dashboard summary.
    High-level KPIs for management review.
    """
    # Risk counts by quadrant
    risk_query = select(Risk).where(Risk.tenant_id == tenant_id)
    risks_result = await session.execute(risk_query)
    risks = risks_result.scalars().all()

    risk_by_quadrant = {
        "mitigate": sum(1 for r in risks if r.attention_quadrant == AttentionQuadrant.MITIGATE),
        "assurance": sum(1 for r in risks if r.attention_quadrant == AttentionQuadrant.ASSURANCE),
        "monitor": sum(1 for r in risks if r.attention_quadrant == AttentionQuadrant.MONITOR),
        "accept": sum(1 for r in risks if r.attention_quadrant == AttentionQuadrant.ACCEPT),
        "unclassified": sum(1 for r in risks if r.attention_quadrant is None),
    }

    high_critical_risks = sum(
        1 for r in risks
        if r.inherent_impact in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    )

    # Policy status
    policy_query = select(Policy).where(Policy.tenant_id == tenant_id)
    policies_result = await session.execute(policy_query)
    policies = policies_result.scalars().all()

    policy_stats = {
        "draft": sum(1 for p in policies if p.state == PolicyState.DRAFT),
        "review": sum(1 for p in policies if p.state == PolicyState.REVIEW),
        "approved": sum(1 for p in policies if p.state == PolicyState.APPROVED),
        "published": sum(1 for p in policies if p.state == PolicyState.PUBLISHED),
        "total": len(policies),
    }

    # Measure effectiveness
    measure_query = select(Measure).where(Measure.tenant_id == tenant_id)
    measures_result = await session.execute(measure_query)
    measures = measures_result.scalars().all()

    active_measures = [m for m in measures if m.status == Status.ACTIVE]
    avg_effectiveness = 0
    if active_measures:
        effectiveness_values = [m.effectiveness_percentage for m in active_measures if m.effectiveness_percentage]
        if effectiveness_values:
            avg_effectiveness = round(sum(effectiveness_values) / len(effectiveness_values), 1)

    # Open incidents
    incident_query = select(Incident).where(Incident.tenant_id == tenant_id)
    incidents_result = await session.execute(incident_query)
    incidents = incidents_result.scalars().all()

    open_incidents = sum(1 for i in incidents if i.status in [Status.DRAFT, Status.ACTIVE])

    # Compliance (SoA)
    soa_query = select(ApplicabilityStatement).where(ApplicabilityStatement.tenant_id == tenant_id)
    soa_result = await session.execute(soa_query)
    soa_entries = soa_result.scalars().all()

    applicable_entries = [s for s in soa_entries if s.is_applicable]
    implemented = sum(1 for s in applicable_entries if s.implementation_status == ImplementationStatus.IMPLEMENTED)
    compliance_pct = round(implemented / len(applicable_entries) * 100, 1) if applicable_entries else 100

    return {
        "risks": {
            "total": len(risks),
            "by_quadrant": risk_by_quadrant,
            "high_critical": high_critical_risks,
        },
        "policies": policy_stats,
        "measures": {
            "total": len(measures),
            "active": len(active_measures),
            "avg_effectiveness": avg_effectiveness,
        },
        "incidents": {
            "total": len(incidents),
            "open": open_incidents,
        },
        "compliance": {
            "overall_percentage": compliance_pct,
            "total_requirements": len(soa_entries),
            "implemented": implemented,
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# RISK REPORTS
# =============================================================================

@router.get("/risks/summary", response_model=dict)
async def get_risk_summary(
    tenant_id: int = Depends(get_tenant_id),
    scope_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get comprehensive risk summary report.
    """
    query = select(Risk).where(Risk.tenant_id == tenant_id)
    if scope_id:
        query = query.where(Risk.scope_id == scope_id)

    result = await session.execute(query)
    risks = result.scalars().all()

    # By quadrant
    by_quadrant = {}
    for quadrant in AttentionQuadrant:
        by_quadrant[quadrant.name.lower()] = sum(
            1 for r in risks if r.attention_quadrant == quadrant
        )
    by_quadrant["unclassified"] = sum(1 for r in risks if r.attention_quadrant is None)

    # By impact level
    by_impact = {}
    for level in RiskLevel:
        by_impact[level.name.lower()] = sum(
            1 for r in risks if r.inherent_impact == level
        )

    # By likelihood level
    by_likelihood = {}
    for level in RiskLevel:
        by_likelihood[level.name.lower()] = sum(
            1 for r in risks if r.inherent_likelihood == level
        )

    # Risk acceptance stats
    accepted = sum(1 for r in risks if r.risk_accepted)
    pending_acceptance = sum(
        1 for r in risks
        if r.attention_quadrant == AttentionQuadrant.ACCEPT and not r.risk_accepted
    )

    # Average scores
    inherent_scores = [r.inherent_risk_score for r in risks if r.inherent_risk_score]
    residual_scores = [r.residual_risk_score for r in risks if r.residual_risk_score]

    return {
        "total": len(risks),
        "by_quadrant": by_quadrant,
        "by_impact": by_impact,
        "by_likelihood": by_likelihood,
        "acceptance": {
            "accepted": accepted,
            "pending": pending_acceptance,
        },
        "scores": {
            "avg_inherent": round(sum(inherent_scores) / len(inherent_scores), 2) if inherent_scores else 0,
            "avg_residual": round(sum(residual_scores) / len(residual_scores), 2) if residual_scores else 0,
        },
    }


@router.get("/risks/heatmap-matrix", response_model=dict)
async def get_risk_heatmap_matrix(
    tenant_id: int = Depends(get_tenant_id),
    scope_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get 4x4 risk matrix data for heatmap visualization.
    Returns count of risks at each likelihood/impact intersection.
    """
    query = select(Risk).where(Risk.tenant_id == tenant_id)
    if scope_id:
        query = query.where(Risk.scope_id == scope_id)

    result = await session.execute(query)
    risks = result.scalars().all()

    # Initialize matrix
    levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    matrix = {
        likelihood: {impact: {"count": 0, "risks": []} for impact in levels}
        for likelihood in levels
    }

    for risk in risks:
        if risk.inherent_likelihood and risk.inherent_impact:
            likelihood = risk.inherent_likelihood.name
            impact = risk.inherent_impact.name
            matrix[likelihood][impact]["count"] += 1
            matrix[likelihood][impact]["risks"].append({
                "id": risk.id,
                "title": risk.title,
                "score": risk.inherent_risk_score,
            })

    return {
        "matrix": matrix,
        "levels": levels,
        "total_risks": len(risks),
    }


# =============================================================================
# COMPLIANCE REPORTS
# =============================================================================

@router.get("/compliance/overview", response_model=dict)
async def get_compliance_overview(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get overall compliance status across all standards and scopes.
    """
    query = select(ApplicabilityStatement).where(
        ApplicabilityStatement.tenant_id == tenant_id,
    )

    result = await session.execute(query)
    entries = result.scalars().all()

    applicable = [e for e in entries if e.is_applicable]

    # Implementation status breakdown
    impl_status = {
        "not_started": sum(1 for e in applicable if e.implementation_status == ImplementationStatus.NOT_STARTED),
        "in_progress": sum(1 for e in applicable if e.implementation_status == ImplementationStatus.IN_PROGRESS),
        "implemented": sum(1 for e in applicable if e.implementation_status == ImplementationStatus.IMPLEMENTED),
    }

    # Coverage breakdown
    coverage = {
        "local": sum(1 for e in entries if e.coverage_type == CoverageType.LOCAL),
        "shared": sum(1 for e in entries if e.coverage_type == CoverageType.SHARED),
        "combined": sum(1 for e in entries if e.coverage_type == CoverageType.COMBINED),
        "not_covered": sum(1 for e in entries if e.coverage_type == CoverageType.NOT_COVERED),
        "not_applicable": sum(1 for e in entries if e.coverage_type == CoverageType.NOT_APPLICABLE),
    }

    # Overall compliance
    total_applicable = len(applicable)
    implemented = impl_status["implemented"]
    compliance_pct = round(implemented / total_applicable * 100, 1) if total_applicable > 0 else 100

    return {
        "total_requirements": len(entries),
        "applicable": total_applicable,
        "not_applicable": len(entries) - total_applicable,
        "implementation_status": impl_status,
        "coverage": coverage,
        "compliance_percentage": compliance_pct,
        "gaps_count": impl_status["not_started"] + coverage["not_covered"],
    }


# =============================================================================
# ASSESSMENT REPORTS
# =============================================================================

@router.get("/assessments/summary", response_model=dict)
async def get_assessment_summary(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get assessment and finding summary.
    """
    # Get assessments
    assessment_query = select(Assessment).where(Assessment.tenant_id == tenant_id)
    assessments_result = await session.execute(assessment_query)
    assessments = assessments_result.scalars().all()

    # Get findings
    finding_query = select(Finding).where(Finding.tenant_id == tenant_id)
    findings_result = await session.execute(finding_query)
    findings = findings_result.scalars().all()

    # Assessment stats
    active = sum(1 for a in assessments if a.status == Status.ACTIVE)
    completed = sum(1 for a in assessments if a.status == Status.CLOSED)

    # By type
    by_type = {}
    for assessment in assessments:
        if assessment.type:
            type_name = assessment.type.name.lower()
            by_type[type_name] = by_type.get(type_name, 0) + 1

    # Finding severity breakdown
    finding_severity = {}
    for severity in FindingSeverity:
        finding_severity[severity.name.lower()] = sum(
            1 for f in findings if f.severity == severity
        )

    # Open findings
    open_findings = sum(1 for f in findings if f.status in [Status.DRAFT, Status.ACTIVE])

    return {
        "assessments": {
            "total": len(assessments),
            "active": active,
            "completed": completed,
            "by_type": by_type,
        },
        "findings": {
            "total": len(findings),
            "open": open_findings,
            "by_severity": finding_severity,
        },
    }


# =============================================================================
# INCIDENT REPORTS
# =============================================================================

@router.get("/incidents/summary", response_model=dict)
async def get_incident_summary(
    tenant_id: int = Depends(get_tenant_id),
    days: int = Query(30, description="Number of days to look back"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get incident summary and trends.
    """
    query = select(Incident).where(Incident.tenant_id == tenant_id)

    result = await session.execute(query)
    incidents = result.scalars().all()

    # Recent incidents (last N days)
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent = [i for i in incidents if i.created_at and i.created_at >= cutoff]

    # Status breakdown
    open_incidents = sum(1 for i in incidents if i.status in [Status.DRAFT, Status.ACTIVE])
    closed_incidents = sum(1 for i in incidents if i.status == Status.CLOSED)

    # Severity (using impact field if available)
    severity_breakdown = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    # Note: This would need to be adjusted based on actual Incident model fields

    return {
        "total": len(incidents),
        "open": open_incidents,
        "closed": closed_incidents,
        "recent_count": len(recent),
        "period_days": days,
    }


# =============================================================================
# CORRECTIVE ACTIONS
# =============================================================================

@router.get("/actions/summary", response_model=dict)
async def get_corrective_actions_summary(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Get corrective actions summary.
    """
    query = select(CorrectiveAction).where(CorrectiveAction.tenant_id == tenant_id)

    result = await session.execute(query)
    actions = result.scalars().all()

    open_actions = sum(1 for a in actions if not a.completed)
    closed_actions = sum(1 for a in actions if a.completed)

    # Overdue actions (due_date in the past and not completed)
    now = datetime.utcnow()
    overdue = sum(
        1 for a in actions
        if a.due_date and a.due_date < now and not a.completed
    )

    return {
        "total": len(actions),
        "open": open_actions,
        "closed": closed_actions,
        "overdue": overdue,
        "completion_rate": round(closed_actions / len(actions) * 100, 1) if actions else 100,
    }


# =============================================================================
# TREND REPORTS
# =============================================================================

@router.get("/trends/monthly", response_model=dict)
async def get_monthly_trends(
    tenant_id: int = Depends(get_tenant_id),
    months: int = Query(6, description="Number of months to include"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get monthly trend data for key metrics.
    """
    # This is a simplified version - a production version would use
    # proper date aggregation queries

    now = datetime.utcnow()
    trends = {
        "months": [],
        "risks_created": [],
        "incidents_created": [],
        "assessments_completed": [],
    }

    for i in range(months - 1, -1, -1):
        # Calculate month start/end
        month_start = now.replace(day=1) - timedelta(days=i * 30)
        month_label = month_start.strftime("%Y-%m")
        trends["months"].append(month_label)

        # Placeholder values - in production, these would be actual queries
        trends["risks_created"].append(0)
        trends["incidents_created"].append(0)
        trends["assessments_completed"].append(0)

    return trends
