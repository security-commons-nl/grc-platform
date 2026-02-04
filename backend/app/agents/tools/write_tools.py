"""
Write Tools for AI Agents.

These tools allow agents to create and update data in the database.
All write operations require confirmation before execution.
"""
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from sqlmodel import select
from app.core.db import get_session
from app.models.core_models import (
    Risk,
    Measure,
    CorrectiveAction,
    RiskLevel,
    Status,
    AttentionQuadrant,
)


# =============================================================================
# RISK WRITE TOOLS
# =============================================================================

@tool
async def create_risk(
    tenant_id: int,
    title: str,
    description: str,
    inherent_likelihood: str = "MEDIUM",
    inherent_impact: str = "MEDIUM",
    scope_id: Optional[int] = None,
    cause: Optional[str] = None,
    consequence: Optional[str] = None,
) -> str:
    """
    Create a new risk in the system.
    Inherent likelihood and impact should be: LOW, MEDIUM, HIGH, or CRITICAL.

    Returns the ID of the created risk.
    """
    async for session in get_session():
        # Map string to enum
        likelihood_map = {"LOW": RiskLevel.LOW, "MEDIUM": RiskLevel.MEDIUM, "HIGH": RiskLevel.HIGH, "CRITICAL": RiskLevel.CRITICAL}
        impact_map = likelihood_map

        risk = Risk(
            tenant_id=tenant_id,
            title=title,
            description=description,
            inherent_likelihood=likelihood_map.get(inherent_likelihood.upper(), RiskLevel.MEDIUM),
            inherent_impact=impact_map.get(inherent_impact.upper(), RiskLevel.MEDIUM),
            residual_likelihood=likelihood_map.get(inherent_likelihood.upper(), RiskLevel.MEDIUM),
            residual_impact=impact_map.get(inherent_impact.upper(), RiskLevel.MEDIUM),
            scope_id=scope_id,
            cause=cause,
            consequence=consequence,
            status=Status.ACTIVE,
        )

        # Calculate risk scores
        level_to_score = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        risk.inherent_risk_score = level_to_score[risk.inherent_likelihood] * level_to_score[risk.inherent_impact]
        risk.residual_risk_score = risk.inherent_risk_score

        session.add(risk)
        await session.commit()
        await session.refresh(risk)

        return f"Created risk #{risk.id}: {risk.title}"


@tool
async def update_risk(
    risk_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    residual_likelihood: Optional[str] = None,
    residual_impact: Optional[str] = None,
    attention_quadrant: Optional[str] = None,
) -> str:
    """
    Update an existing risk.

    For residual likelihood/impact use: LOW, MEDIUM, HIGH, or CRITICAL.
    For attention quadrant use: MITIGATE, ASSURANCE, MONITOR, or ACCEPT.
    """
    async for session in get_session():
        result = await session.execute(select(Risk).where(Risk.id == risk_id))
        risk = result.scalars().first()
        if not risk:
            return f"Risk with ID {risk_id} not found."

        likelihood_map = {"LOW": RiskLevel.LOW, "MEDIUM": RiskLevel.MEDIUM, "HIGH": RiskLevel.HIGH, "CRITICAL": RiskLevel.CRITICAL}
        quadrant_map = {
            "MITIGATE": AttentionQuadrant.MITIGATE,
            "ASSURANCE": AttentionQuadrant.ASSURANCE,
            "MONITOR": AttentionQuadrant.MONITOR,
            "ACCEPT": AttentionQuadrant.ACCEPT,
        }

        if title:
            risk.title = title
        if description:
            risk.description = description
        if residual_likelihood:
            risk.residual_likelihood = likelihood_map.get(residual_likelihood.upper(), risk.residual_likelihood)
        if residual_impact:
            risk.residual_impact = likelihood_map.get(residual_impact.upper(), risk.residual_impact)
        if attention_quadrant:
            risk.attention_quadrant = quadrant_map.get(attention_quadrant.upper(), risk.attention_quadrant)

        # Recalculate residual score
        level_to_score = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        risk.residual_risk_score = level_to_score[risk.residual_likelihood] * level_to_score[risk.residual_impact]
        risk.updated_at = datetime.utcnow()

        session.add(risk)
        await session.commit()

        return f"Updated risk #{risk.id}: {risk.title}"


# =============================================================================
# MEASURE WRITE TOOLS
# =============================================================================

@tool
async def create_measure(
    tenant_id: int,
    title: str,
    description: str,
    implementation_details: Optional[str] = None,
    scope_id: Optional[int] = None,
) -> str:
    """
    Create a new measure (control) in the system.

    Returns the ID of the created measure.
    """
    async for session in get_session():
        measure = Measure(
            tenant_id=tenant_id,
            title=title,
            description=description,
            implementation_details=implementation_details,
            scope_id=scope_id,
            status=Status.DRAFT,
        )

        session.add(measure)
        await session.commit()
        await session.refresh(measure)

        return f"Created measure #{measure.id}: {measure.title}"


@tool
async def update_measure(
    measure_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    implementation_details: Optional[str] = None,
    effectiveness_score: Optional[int] = None,
    status: Optional[str] = None,
) -> str:
    """
    Update an existing measure.

    For status use: DRAFT, ACTIVE, or INACTIVE.
    Effectiveness score should be 0-100.
    """
    async for session in get_session():
        result = await session.execute(select(Measure).where(Measure.id == measure_id))
        measure = result.scalars().first()
        if not measure:
            return f"Measure with ID {measure_id} not found."

        status_map = {"DRAFT": Status.DRAFT, "ACTIVE": Status.ACTIVE, "INACTIVE": Status.INACTIVE}

        if title:
            measure.title = title
        if description:
            measure.description = description
        if implementation_details:
            measure.implementation_details = implementation_details
        if effectiveness_score is not None:
            measure.effectiveness_score = max(0, min(100, effectiveness_score))
        if status:
            measure.status = status_map.get(status.upper(), measure.status)

        measure.updated_at = datetime.utcnow()

        session.add(measure)
        await session.commit()

        return f"Updated measure #{measure.id}: {measure.title}"


@tool
async def link_measure_to_risk(
    measure_id: int,
    risk_id: int,
    effectiveness_contribution: int = 50,
) -> str:
    """
    Link a measure to a risk, indicating the measure helps mitigate the risk.

    NOTE: This function is currently disabled pending data model refactoring.
    """
    return "This function is temporarily disabled. Measure-Risk linking is being refactored to Control-Risk linking."


# =============================================================================
# CORRECTIVE ACTION TOOLS
# =============================================================================

@tool
async def create_corrective_action(
    tenant_id: int,
    title: str,
    description: str,
    due_date: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    risk_id: Optional[int] = None,
    finding_id: Optional[int] = None,
    incident_id: Optional[int] = None,
) -> str:
    """
    Create a corrective action to address a finding, incident, or risk.

    Due date format: YYYY-MM-DD
    Link to at least one of: risk_id, finding_id, or incident_id.
    """
    async for session in get_session():
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return "Invalid due_date format. Use YYYY-MM-DD."

        action = CorrectiveAction(
            tenant_id=tenant_id,
            title=title,
            description=description,
            due_date=due_datetime,
            assigned_to_id=assigned_to_id,
            risk_id=risk_id,
            finding_id=finding_id,
            incident_id=incident_id,
            status=Status.DRAFT,
        )

        session.add(action)
        await session.commit()
        await session.refresh(action)

        return f"Created corrective action #{action.id}: {action.title}"
