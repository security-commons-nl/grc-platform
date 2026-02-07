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
    Decision,
    DecisionType,
    DecisionStatus,
    DecisionRiskLink,
    TreatmentStrategy,
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


# =============================================================================
# DECISION WRITE TOOLS (Hiaat 1: Besluitlog)
# =============================================================================

@tool
async def create_decision(
    tenant_id: int,
    decision_type: str,
    decision_text: str,
    decision_maker_id: int,
    justification: Optional[str] = None,
    valid_until: Optional[str] = None,
    risk_ids: Optional[str] = None,
    scope_id: Optional[int] = None,
    conditions: Optional[str] = None,
) -> str:
    """
    Create a formal management decision (DT-besluit).

    Decision types: Restrisico-acceptatie, Prioritering, Afwijking, Scopewijziging, Beleidsgoedkeuring.
    Valid until format: YYYY-MM-DD.
    Risk IDs: comma-separated list of risk IDs to link (e.g. "1,2,3").
    """
    async for session in get_session():
        # Map decision type
        type_map = {
            "Restrisico-acceptatie": DecisionType.RISK_ACCEPTANCE,
            "Prioritering": DecisionType.PRIORITIZATION,
            "Afwijking": DecisionType.DEVIATION,
            "Scopewijziging": DecisionType.SCOPE_CHANGE,
            "Beleidsgoedkeuring": DecisionType.POLICY_APPROVAL,
        }
        dt = type_map.get(decision_type)
        if not dt:
            return f"Unknown decision type '{decision_type}'. Options: {', '.join(type_map.keys())}"

        valid_dt = None
        if valid_until:
            try:
                valid_dt = datetime.strptime(valid_until, "%Y-%m-%d")
            except ValueError:
                return "Invalid valid_until format. Use YYYY-MM-DD."

        decision = Decision(
            tenant_id=tenant_id,
            decision_type=dt,
            decision_text=decision_text,
            decision_maker_id=decision_maker_id,
            justification=justification,
            valid_until=valid_dt,
            scope_id=scope_id,
            conditions=conditions,
            status=DecisionStatus.ACTIVE,
        )

        session.add(decision)
        await session.commit()
        await session.refresh(decision)

        # Link risks if provided
        linked = []
        if risk_ids:
            for rid_str in risk_ids.split(","):
                rid = int(rid_str.strip())
                link = DecisionRiskLink(decision_id=decision.id, risk_id=rid)
                session.add(link)
                linked.append(rid)
            await session.commit()

        risk_info = f" | Linked risks: {linked}" if linked else ""
        return f"Created decision #{decision.id}: [{dt.value}] {decision_text[:80]}{risk_info}"


# =============================================================================
# RISK TREATMENT TOOLS (Hiaat 4: Behandelstrategie)
# =============================================================================

@tool
async def update_risk_treatment(
    risk_id: int,
    treatment_strategy: str,
    transfer_party: Optional[str] = None,
) -> str:
    """
    Set the treatment strategy for a risk.

    Strategies: Vermijden, Reduceren, Overdragen, Accepteren.
    If strategy is Overdragen, transfer_party is required (e.g. verzekeraar or leverancier).
    Hard rule: if Accepteren AND score >= 9, a DT decision is required.
    """
    async for session in get_session():
        result = await session.execute(select(Risk).where(Risk.id == risk_id))
        risk = result.scalars().first()
        if not risk:
            return f"Risk with ID {risk_id} not found."

        strategy_map = {
            "Vermijden": TreatmentStrategy.AVOID,
            "Reduceren": TreatmentStrategy.REDUCE,
            "Overdragen": TreatmentStrategy.TRANSFER,
            "Accepteren": TreatmentStrategy.ACCEPT,
        }
        strategy = strategy_map.get(treatment_strategy)
        if not strategy:
            return f"Unknown strategy '{treatment_strategy}'. Options: {', '.join(strategy_map.keys())}"

        if strategy == TreatmentStrategy.TRANSFER and not transfer_party:
            return "transfer_party is required when strategy is 'Overdragen'. Specify the party (e.g. verzekeraar, leverancier)."

        risk.treatment_strategy = strategy
        if transfer_party:
            risk.transfer_party = transfer_party
        risk.updated_at = datetime.utcnow()

        session.add(risk)
        await session.commit()

        # Warning if acceptance requires decision
        score = risk.residual_risk_score or risk.inherent_risk_score or 0
        warning = ""
        if strategy == TreatmentStrategy.ACCEPT and score >= 9:
            warning = "\n⚠ HARD RULE: Score >= 9 + Accepteren requires a formal DT decision. Use create_decision to record it."

        return f"Updated risk #{risk.id} treatment strategy to {strategy.value}.{warning}"
