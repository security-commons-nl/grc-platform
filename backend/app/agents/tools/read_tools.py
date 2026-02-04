"""
Read Tools for AI Agents.

These tools allow agents to retrieve information from the database.
All tools are async and use the database session properly.
"""
from typing import Optional, List
from langchain_core.tools import tool
from sqlmodel import select
from app.core.db import get_session
from app.models.core_models import (
    Risk,
    Measure,
    Policy,
    Scope,
    Assessment,
    Incident,
    Requirement,
    Standard,
)


# =============================================================================
# RISK TOOLS
# =============================================================================

@tool
async def get_risk(risk_id: int) -> str:
    """
    Get detailed information about a specific risk by its ID.
    Returns risk details including title, description, impact, likelihood, and quadrant.
    """
    async for session in get_session():
        result = await session.execute(select(Risk).where(Risk.id == risk_id))
        risk = result.scalars().first()
        if not risk:
            return f"Risk with ID {risk_id} not found."

        return f"""
Risk #{risk.id}: {risk.title}
Description: {risk.description or 'N/A'}
Cause: {risk.cause or 'N/A'}
Consequence: {risk.consequence or 'N/A'}
Inherent: Impact={risk.inherent_impact}, Likelihood={risk.inherent_likelihood}
Residual: Impact={risk.residual_impact}, Likelihood={risk.residual_likelihood}
Quadrant: {risk.attention_quadrant or 'Not classified'}
Risk Accepted: {risk.risk_accepted}
Status: {risk.status}
"""


@tool
async def list_risks(
    tenant_id: Optional[int] = None,
    scope_id: Optional[int] = None,
    limit: int = 10
) -> str:
    """
    List risks with optional filtering by tenant and scope.
    Returns a summary of risks including their titles and risk levels.
    """
    async for session in get_session():
        query = select(Risk)
        if tenant_id:
            query = query.where(Risk.tenant_id == tenant_id)
        if scope_id:
            query = query.where(Risk.scope_id == scope_id)
        query = query.limit(limit)

        result = await session.execute(query)
        risks = result.scalars().all()

        if not risks:
            return "No risks found matching the criteria."

        output = f"Found {len(risks)} risks:\n\n"
        for risk in risks:
            output += f"- #{risk.id}: {risk.title} | Impact: {risk.inherent_impact} | Quadrant: {risk.attention_quadrant or 'N/A'}\n"

        return output


@tool
async def search_risks(query: str, limit: int = 5) -> str:
    """
    Search risks by title or description containing the query text.
    Use this to find risks related to specific topics.
    """
    async for session in get_session():
        result = await session.execute(
            select(Risk).where(
                Risk.title.ilike(f"%{query}%") | Risk.description.ilike(f"%{query}%")
            ).limit(limit)
        )
        risks = result.scalars().all()

        if not risks:
            return f"No risks found matching '{query}'."

        output = f"Found {len(risks)} risks matching '{query}':\n\n"
        for risk in risks:
            output += f"- #{risk.id}: {risk.title}\n  {risk.description[:100] if risk.description else 'No description'}...\n"

        return output


# =============================================================================
# MEASURE TOOLS
# =============================================================================

@tool
async def get_measure(measure_id: int) -> str:
    """
    Get detailed information about a specific measure (control) by its ID.
    """
    async for session in get_session():
        result = await session.execute(select(Measure).where(Measure.id == measure_id))
        measure = result.scalars().first()
        if not measure:
            return f"Measure with ID {measure_id} not found."

        return f"""
Measure #{measure.id}: {measure.title}
Description: {measure.description or 'N/A'}
Status: {measure.status}
"""


@tool
async def list_measures(
    tenant_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List measures with optional filtering.
    """
    async for session in get_session():
        query = select(Measure)
        if tenant_id:
            query = query.where(Measure.tenant_id == tenant_id)
        if status:
            query = query.where(Measure.status == status)
        query = query.limit(limit)

        result = await session.execute(query)
        measures = result.scalars().all()

        if not measures:
            return "No measures found."

        output = f"Found {len(measures)} measures:\n\n"
        for m in measures:
            output += f"- #{m.id}: {m.title} | Status: {m.status} | Effectiveness: {m.effectiveness_score or 'N/A'}%\n"

        return output


# =============================================================================
# POLICY TOOLS
# =============================================================================

@tool
async def get_policy(policy_id: int) -> str:
    """
    Get detailed information about a specific policy by its ID.
    """
    async for session in get_session():
        result = await session.execute(select(Policy).where(Policy.id == policy_id))
        policy = result.scalars().first()
        if not policy:
            return f"Policy with ID {policy_id} not found."

        return f"""
Policy #{policy.id}: {policy.title}
Version: {policy.version}
State: {policy.state}
Content preview: {policy.content[:200] if policy.content else 'N/A'}...
Effective date: {policy.effective_date or 'Not yet effective'}
Review date: {policy.review_date or 'Not set'}
"""


@tool
async def list_policies(
    tenant_id: Optional[int] = None,
    state: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List policies with optional filtering by tenant and state.
    """
    async for session in get_session():
        query = select(Policy)
        if tenant_id:
            query = query.where(Policy.tenant_id == tenant_id)
        if state:
            query = query.where(Policy.state == state)
        query = query.limit(limit)

        result = await session.execute(query)
        policies = result.scalars().all()

        if not policies:
            return "No policies found."

        output = f"Found {len(policies)} policies:\n\n"
        for p in policies:
            output += f"- #{p.id}: {p.title} | Version: {p.version} | State: {p.state}\n"

        return output


# =============================================================================
# SCOPE TOOLS
# =============================================================================

@tool
async def get_scope(scope_id: int) -> str:
    """
    Get detailed information about a scope (organization unit, process, asset).
    """
    async for session in get_session():
        result = await session.execute(select(Scope).where(Scope.id == scope_id))
        scope = result.scalars().first()
        if not scope:
            return f"Scope with ID {scope_id} not found."

        return f"""
Scope #{scope.id}: {scope.name}
Type: {scope.scope_type}
Description: {scope.description or 'N/A'}
Parent scope: {scope.parent_id or 'None (top-level)'}
Classification: {scope.classification or 'N/A'}
BIA Rating: Confidentiality={scope.bia_confidentiality}, Integrity={scope.bia_integrity}, Availability={scope.bia_availability}
"""


@tool
async def list_scopes(
    tenant_id: Optional[int] = None,
    scope_type: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List scopes with optional filtering.
    """
    async for session in get_session():
        query = select(Scope)
        if tenant_id:
            query = query.where(Scope.tenant_id == tenant_id)
        if scope_type:
            query = query.where(Scope.scope_type == scope_type)
        query = query.limit(limit)

        result = await session.execute(query)
        scopes = result.scalars().all()

        if not scopes:
            return "No scopes found."

        output = f"Found {len(scopes)} scopes:\n\n"
        for s in scopes:
            output += f"- #{s.id}: {s.name} | Type: {s.scope_type}\n"

        return output


# =============================================================================
# ASSESSMENT TOOLS
# =============================================================================

@tool
async def get_assessment(assessment_id: int) -> str:
    """
    Get detailed information about an assessment (audit, DPIA, pentest, etc.).
    """
    async for session in get_session():
        result = await session.execute(select(Assessment).where(Assessment.id == assessment_id))
        assessment = result.scalars().first()
        if not assessment:
            return f"Assessment with ID {assessment_id} not found."

        return f"""
Assessment #{assessment.id}: {assessment.title}
Type: {assessment.assessment_type}
Status: {assessment.status}
Start date: {assessment.start_date or 'Not started'}
End date: {assessment.end_date or 'Not completed'}
Lead assessor: {assessment.lead_assessor_id or 'Not assigned'}
Conclusion: {assessment.conclusion or 'No conclusion yet'}
"""


# =============================================================================
# INCIDENT TOOLS
# =============================================================================

@tool
async def get_incident(incident_id: int) -> str:
    """
    Get detailed information about a security or privacy incident.
    """
    async for session in get_session():
        result = await session.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalars().first()
        if not incident:
            return f"Incident with ID {incident_id} not found."

        return f"""
Incident #{incident.id}: {incident.title}
Status: {incident.status}
Severity: {incident.severity}
Reported at: {incident.reported_at}
Description: {incident.description or 'N/A'}
Root cause: {incident.root_cause or 'Not determined'}
Data breach: {incident.is_data_breach}
"""


# =============================================================================
# REQUIREMENT TOOLS
# =============================================================================

@tool
async def get_requirement(requirement_id: int) -> str:
    """
    Get detailed information about a requirement (control from a standard/framework).
    """
    async for session in get_session():
        result = await session.execute(select(Requirement).where(Requirement.id == requirement_id))
        req = result.scalars().first()
        if not req:
            return f"Requirement with ID {requirement_id} not found."

        # Get standard name
        std_result = await session.execute(select(Standard).where(Standard.id == req.standard_id))
        standard = std_result.scalars().first()

        return f"""
Requirement #{req.id}: {req.code} - {req.title}
Framework: {standard.name if standard else 'Unknown'}
Description: {req.description or 'N/A'}
Guidance: {req.guidance or 'N/A'}
Control type: {req.control_type or 'N/A'}
"""
