"""
Read Tools for AI Agents.

These tools allow agents to retrieve information from the database.
All tools are async and use the database session properly.
"""
from typing import Optional, List
from datetime import datetime
from langchain_core.tools import tool
from sqlmodel import select, func
from app.core.db import get_session
from app.models.core_models import (
    Risk,
    RiskAppetite,
    RiskScope,
    Measure,
    Policy,
    Scope,
    Assessment,
    Incident,
    Requirement,
    Standard,
    Decision,
    DecisionType,
    DecisionStatus,
    DecisionRiskLink,
    RiskFramework,
    RiskFrameworkStatus,
    InControlAssessment,
    InControlLevel,
    PolicyPrinciple,
    Finding,
    CorrectiveAction,
    Status,
    Control,
    ControlRiskLink,
)
from app.core.risk_appetite_engine import (
    evaluate_risk_scope,
    evaluate_scope_risks_bulk,
    generate_heatmap_matrix,
    HeatmapZone,
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
In Scope: {scope.in_scope}
Governance Status: {scope.governance_status or 'N/A'}
Scope Motivation: {scope.scope_motivation or 'N/A'}
Validity Year: {scope.validity_year or 'N/A'}
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


# =============================================================================
# DECISION TOOLS (Hiaat 1: Besluitlog)
# =============================================================================

@tool
async def get_decision(decision_id: int) -> str:
    """
    Get detailed information about a formal management decision (managementbesluit).
    Returns decision type, text, maker, validity, and linked risks.
    """
    async for session in get_session():
        result = await session.execute(select(Decision).where(Decision.id == decision_id))
        decision = result.scalars().first()
        if not decision:
            return f"Decision with ID {decision_id} not found."

        # Get linked risks
        links_result = await session.execute(
            select(DecisionRiskLink).where(DecisionRiskLink.decision_id == decision_id)
        )
        links = links_result.scalars().all()
        risk_ids = [str(link.risk_id) for link in links]

        return f"""
Decision #{decision.id}
Type: {decision.decision_type.value}
Text: {decision.decision_text}
Decision maker: user #{decision.decision_maker_id}
Date: {decision.decision_date}
Valid until: {decision.valid_until or 'No expiry'}
Status: {decision.status.value}
Justification: {decision.justification or 'N/A'}
Conditions: {decision.conditions or 'N/A'}
Linked risks: {', '.join(risk_ids) if risk_ids else 'None'}
"""


@tool
async def list_decisions(
    tenant_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List formal management decisions with optional filtering.
    Status options: Actief, Verlopen, Ingetrokken, Vervangen.
    """
    async for session in get_session():
        query = select(Decision)
        if tenant_id:
            query = query.where(Decision.tenant_id == tenant_id)
        if status:
            try:
                query = query.where(Decision.status == DecisionStatus(status))
            except ValueError:
                pass
        query = query.order_by(Decision.decision_date.desc()).limit(limit)

        result = await session.execute(query)
        decisions = result.scalars().all()

        if not decisions:
            return "No decisions found matching the criteria."

        output = f"Found {len(decisions)} decisions:\n\n"
        for d in decisions:
            output += f"- #{d.id}: [{d.decision_type.value}] {d.decision_text[:80]}... | Status: {d.status.value} | Valid until: {d.valid_until or 'N/A'}\n"

        return output


@tool
async def check_decision_required(risk_id: int) -> str:
    """
    Check if a formal management decision is required for a risk.
    Hard rule: risk score >= 9 AND treatment=Accepteren requires a management decision.
    Returns whether a decision exists or is still needed.
    """
    async for session in get_session():
        result = await session.execute(select(Risk).where(Risk.id == risk_id))
        risk = result.scalars().first()
        if not risk:
            return f"Risk with ID {risk_id} not found."

        score = risk.residual_risk_score or risk.inherent_risk_score or 0
        strategy = risk.treatment_strategy

        needs_decision = score >= 9 and strategy and strategy.value == "Accepteren"

        # Check if decision already exists
        existing = await session.execute(
            select(DecisionRiskLink).where(DecisionRiskLink.risk_id == risk_id)
        )
        has_decision = existing.scalars().first() is not None

        if not needs_decision:
            return f"Risk #{risk_id} (score={score}, strategy={strategy}) does NOT require a management decision."

        if has_decision:
            return f"Risk #{risk_id} (score={score}, strategy=Accepteren) REQUIRES a management decision — and one already exists."

        return f"⚠ Risk #{risk_id} (score={score}, strategy=Accepteren) REQUIRES a management decision — NONE found! A formal decision must be recorded."


# =============================================================================
# RISK FRAMEWORK TOOLS (Hiaat 3: Risicokader)
# =============================================================================

@tool
async def get_risk_framework(tenant_id: int) -> str:
    """
    Get the active risk framework for a tenant, including impact/likelihood definitions,
    risk tolerance, and decision rules.
    """
    async for session in get_session():
        result = await session.execute(
            select(RiskFramework).where(
                RiskFramework.tenant_id == tenant_id,
                RiskFramework.status == RiskFrameworkStatus.ACTIVE,
            )
        )
        fw = result.scalars().first()
        if not fw:
            return f"No active risk framework found for tenant {tenant_id}."

        return f"""
Risk Framework #{fw.id}: {fw.name} (v{fw.version})
Status: {fw.status.value}

Impact Definitions:
{fw.impact_definitions}

Likelihood Definitions:
{fw.likelihood_definitions}

Risk Tolerance:
{fw.risk_tolerance}

Decision Rules:
{fw.decision_rules}

Established by: user #{fw.established_by_id or 'N/A'}
Established date: {fw.established_date or 'Not yet established'}
"""


# =============================================================================
# RISK APPETITE TOOLS
# =============================================================================

@tool
async def get_risk_appetite(tenant_id: int) -> str:
    """
    Get the current active risk appetite for a tenant.
    Shows overall and domain-specific appetite levels, thresholds, and acceptance criteria.
    """
    async for session in get_session():
        result = await session.execute(
            select(RiskAppetite).where(
                RiskAppetite.tenant_id == tenant_id,
                RiskAppetite.is_current == True,
            )
        )
        appetite = result.scalars().first()
        if not appetite:
            return "Geen actieve Risk Appetite geconfigureerd voor deze tenant."

        domains = []
        if appetite.isms_appetite:
            domains.append(f"  ISMS: {appetite.isms_appetite.value}")
        if appetite.pims_appetite:
            domains.append(f"  Privacy: {appetite.pims_appetite.value}")
        if appetite.bcms_appetite:
            domains.append(f"  BCM: {appetite.bcms_appetite.value}")
        if appetite.financial_appetite:
            domains.append(f"  Financieel: {appetite.financial_appetite.value}")
        if appetite.reputational_appetite:
            domains.append(f"  Reputatie: {appetite.reputational_appetite.value}")
        if appetite.compliance_appetite:
            domains.append(f"  Compliance: {appetite.compliance_appetite.value}")

        domain_text = "\n".join(domains) if domains else "  Geen domein-specifieke instellingen"

        return f"""
Risk Appetite #{appetite.id} (v{appetite.version})
Algehele appetite: {appetite.overall_appetite.value}

Domein-specifieke appetites:
{domain_text}

Drempels:
  Auto-acceptatie drempel: {appetite.auto_accept_threshold.value}
  Escalatiedrempel: {appetite.escalation_threshold.value}
  Max acceptabel risicoscore: {appetite.max_acceptable_risk_score}
  Financieel plafond: €{appetite.financial_threshold_value or 'Niet ingesteld'}

Statement: {appetite.appetite_statement or 'Geen statement'}
Geldig vanaf: {appetite.effective_date}
Volgende review: {appetite.next_review_date or 'Niet gepland'}
"""


@tool
async def evaluate_risk_against_appetite(risk_scope_id: int, tenant_id: int) -> str:
    """
    Evaluate a specific RiskScope against the current risk appetite.
    Returns whether the risk is acceptable, needs a decision, or must be escalated.
    """
    async for session in get_session():
        # Get appetite
        result = await session.execute(
            select(RiskAppetite).where(
                RiskAppetite.tenant_id == tenant_id,
                RiskAppetite.is_current == True,
            )
        )
        appetite = result.scalars().first()
        if not appetite:
            return "Geen actieve Risk Appetite — kan niet evalueren."

        # Get RiskScope
        result = await session.execute(
            select(RiskScope).where(
                RiskScope.id == risk_scope_id,
                RiskScope.tenant_id == tenant_id,
            )
        )
        rs = result.scalars().first()
        if not rs:
            return f"RiskScope #{risk_scope_id} niet gevonden."

        # Get risk category
        result = await session.execute(
            select(Risk.risk_category).where(Risk.id == rs.risk_id)
        )
        category = result.scalar_one_or_none()

        evaluation = evaluate_risk_scope(rs, appetite, category)

        zone_labels = {
            HeatmapZone.ACCEPTABLE: "ACCEPTABEL (groen)",
            HeatmapZone.CONDITIONAL: "VOORWAARDELIJK ACCEPTABEL (geel)",
            HeatmapZone.ESCALATION: "ESCALATIE VEREIST (oranje)",
            HeatmapZone.UNACCEPTABLE: "ONACCEPTABEL (rood)",
        }
        zone_label = zone_labels.get(evaluation.get("zone"), "Onbekend")

        return f"""
Evaluatie RiskScope #{risk_scope_id}:
Zone: {zone_label}
Acceptabel: {evaluation.get('is_acceptable')}
Besluit vereist: {evaluation.get('requires_decision')}
Escalatie vereist: {evaluation.get('requires_escalation')}
Residuele score: {evaluation.get('residual_score')}
Appetite niveau: {evaluation.get('appetite_level')}
Toelichting: {evaluation.get('reason')}
"""


# =============================================================================
# IN-CONTROL TOOLS (Hiaat 5: In-control status)
# =============================================================================

@tool
async def calculate_in_control(scope_id: int, tenant_id: int) -> str:
    """
    Calculate the in-control level for a scope based on open risks,
    high risks, open findings, and overdue corrective actions.

    Returns: In control / Beperkt in control / Niet in control.
    """
    async for session in get_session():
        # Count open high risks
        high_risks_q = await session.execute(
            select(func.count(Risk.id)).where(
                Risk.scope_id == scope_id,
                Risk.tenant_id == tenant_id,
                Risk.status == Status.ACTIVE,
                Risk.residual_risk_score >= 9,
            )
        )
        high_risks = high_risks_q.scalar() or 0

        # Count open findings
        open_findings_q = await session.execute(
            select(func.count(Finding.id)).where(
                Finding.tenant_id == tenant_id,
                Finding.status == Status.ACTIVE,
            )
        )
        open_findings = open_findings_q.scalar() or 0

        # Count overdue corrective actions
        now = datetime.utcnow()
        overdue_q = await session.execute(
            select(func.count(CorrectiveAction.id)).where(
                CorrectiveAction.tenant_id == tenant_id,
                CorrectiveAction.completed == False,
                CorrectiveAction.due_date < now,
            )
        )
        overdue_actions = overdue_q.scalar() or 0

        # Determine level
        if high_risks > 0 or overdue_actions > 3:
            level = InControlLevel.NOT_IN_CONTROL
        elif open_findings > 5 or overdue_actions > 0:
            level = InControlLevel.LIMITED_CONTROL
        else:
            level = InControlLevel.IN_CONTROL

        return f"""
In-Control Assessment for Scope #{scope_id}:
Level: {level.value}

Supporting data:
- High risks (score >= 9): {high_risks}
- Open findings: {open_findings}
- Overdue corrective actions: {overdue_actions}

Rules applied:
- Niet in control: high risks > 0 OR overdue actions > 3
- Beperkt in control: open findings > 5 OR overdue actions > 0
- In control: otherwise
"""


@tool
async def get_in_control_dashboard(tenant_id: int) -> str:
    """
    Get an in-control overview for all scopes within a tenant.
    Shows the calculated in-control level per scope.
    """
    async for session in get_session():
        scopes_result = await session.execute(
            select(Scope).where(Scope.tenant_id == tenant_id, Scope.in_scope == True)
        )
        scopes = scopes_result.scalars().all()

        if not scopes:
            return f"No in-scope scopes found for tenant {tenant_id}."

        output = f"In-Control Dashboard for Tenant {tenant_id}\n{'='*50}\n\n"

        for scope in scopes:
            # High risks
            hr_q = await session.execute(
                select(func.count(Risk.id)).where(
                    Risk.scope_id == scope.id,
                    Risk.tenant_id == tenant_id,
                    Risk.status == Status.ACTIVE,
                    Risk.residual_risk_score >= 9,
                )
            )
            high_risks = hr_q.scalar() or 0

            # Overdue actions (tenant-wide for now)
            now = datetime.utcnow()
            od_q = await session.execute(
                select(func.count(CorrectiveAction.id)).where(
                    CorrectiveAction.tenant_id == tenant_id,
                    CorrectiveAction.completed == False,
                    CorrectiveAction.due_date < now,
                )
            )
            overdue = od_q.scalar() or 0

            if high_risks > 0 or overdue > 3:
                level = "Niet in control"
            elif overdue > 0:
                level = "Beperkt in control"
            else:
                level = "In control"

            governance = scope.governance_status.value if scope.governance_status else "N/A"
            output += f"- {scope.name} ({scope.scope_type}): {level} | Governance: {governance} | High risks: {high_risks}\n"

        return output


# =============================================================================
# POLICY PRINCIPLE TOOLS (Hiaat 6: Beleid-trace)
# =============================================================================

@tool
async def get_policy_principle(principle_id: int) -> str:
    """
    Get a policy principle and its parent policy.
    Principles create the traceability chain: Policy → Principle → Risk → Control.
    """
    async for session in get_session():
        result = await session.execute(
            select(PolicyPrinciple).where(PolicyPrinciple.id == principle_id)
        )
        principle = result.scalars().first()
        if not principle:
            return f"PolicyPrinciple with ID {principle_id} not found."

        # Get parent policy
        policy_result = await session.execute(
            select(Policy).where(Policy.id == principle.policy_id)
        )
        policy = policy_result.scalars().first()

        return f"""
Principle #{principle.id}: {principle.code or 'No code'} — {principle.title}
Description: {principle.description or 'N/A'}
Order: {principle.order}

Parent Policy: #{policy.id} — {policy.title} (State: {policy.state})
"""


@tool
async def list_policy_principles(
    tenant_id: Optional[int] = None,
    policy_id: Optional[int] = None,
    limit: int = 20
) -> str:
    """
    List policy principles with optional filtering by tenant or policy.
    """
    async for session in get_session():
        query = select(PolicyPrinciple)
        if tenant_id:
            query = query.where(PolicyPrinciple.tenant_id == tenant_id)
        if policy_id:
            query = query.where(PolicyPrinciple.policy_id == policy_id)
        query = query.order_by(PolicyPrinciple.policy_id, PolicyPrinciple.order).limit(limit)

        result = await session.execute(query)
        principles = result.scalars().all()

        if not principles:
            return "No policy principles found."

        output = f"Found {len(principles)} principles:\n\n"
        for p in principles:
            output += f"- #{p.id}: [{p.code or '—'}] {p.title} (Policy #{p.policy_id})\n"

        return output


@tool
async def trace_control_origin(control_id: int) -> str:
    """
    Trace the full origin chain for a control:
    Control ← Risk(s) ← (implied) Principle ← Policy.
    Shows which risks a control mitigates and the policies behind them.
    """
    async for session in get_session():
        # Get control
        ctrl_result = await session.execute(select(Control).where(Control.id == control_id))
        control = ctrl_result.scalars().first()
        if not control:
            return f"Control with ID {control_id} not found."

        output = f"Trace for Control #{control.id}: {control.title}\n{'='*50}\n\n"

        # Get linked risks via ControlRiskLink
        link_result = await session.execute(
            select(ControlRiskLink).where(ControlRiskLink.control_id == control_id)
        )
        risk_links = link_result.scalars().all()

        if not risk_links:
            output += "No risks linked to this control.\n"
        else:
            for link in risk_links:
                risk_result = await session.execute(select(Risk).where(Risk.id == link.risk_id))
                risk = risk_result.scalars().first()
                if risk:
                    output += f"→ Risk #{risk.id}: {risk.title} (Score: {risk.residual_risk_score or 'N/A'}, Strategy: {risk.treatment_strategy or 'N/A'})\n"

        # Get linked requirement → standard
        if control.requirement_id:
            req_result = await session.execute(
                select(Requirement).where(Requirement.id == control.requirement_id)
            )
            req = req_result.scalars().first()
            if req:
                std_result = await session.execute(select(Standard).where(Standard.id == req.standard_id))
                std = std_result.scalars().first()
                output += f"\n→ Requirement: {req.code} — {req.title} (Framework: {std.name if std else 'N/A'})\n"

        # Get policy principles that share the same policy (if control has a requirement link)
        # This is a best-effort trace via tenant
        if control.tenant_id:
            principles_result = await session.execute(
                select(PolicyPrinciple).where(PolicyPrinciple.tenant_id == control.tenant_id).limit(5)
            )
            principles = principles_result.scalars().all()
            if principles:
                output += "\nRelated Policy Principles:\n"
                for p in principles:
                    policy_result = await session.execute(select(Policy).where(Policy.id == p.policy_id))
                    policy = policy_result.scalars().first()
                    output += f"  → Principle #{p.id}: {p.title} ← Policy: {policy.title if policy else 'N/A'}\n"

        return output


# =============================================================================
# ACT-OVERDUE TOOLS (Hiaat 7: ACT-feedbackloop)
# =============================================================================

@tool
async def get_act_overdue(tenant_id: int) -> str:
    """
    Get a summary of the ACT-feedbackloop health:
    - Findings that are blocked (status=ACTIVE but no corrective action linked)
    - Corrective actions that are overdue

    These represent gaps in the PDCA Act phase.
    """
    async for session in get_session():
        # Findings without corrective actions ("actionless")
        all_findings_q = await session.execute(
            select(Finding).where(
                Finding.tenant_id == tenant_id,
                Finding.status == Status.ACTIVE,
            )
        )
        active_findings = all_findings_q.scalars().all()

        actionless = []
        for f in active_findings:
            ca_q = await session.execute(
                select(func.count(CorrectiveAction.id)).where(
                    CorrectiveAction.finding_id == f.id
                )
            )
            ca_count = ca_q.scalar() or 0
            if ca_count == 0:
                actionless.append(f)

        # Overdue corrective actions
        now = datetime.utcnow()
        overdue_q = await session.execute(
            select(CorrectiveAction).where(
                CorrectiveAction.tenant_id == tenant_id,
                CorrectiveAction.completed == False,
                CorrectiveAction.due_date < now,
            )
        )
        overdue_actions = overdue_q.scalars().all()

        output = f"ACT-Feedbackloop Health for Tenant {tenant_id}\n{'='*50}\n\n"

        output += f"## Actionless Findings ({len(actionless)})\n"
        output += "These findings have no corrective action linked — the PDCA loop is broken.\n\n"
        for f in actionless[:10]:
            output += f"- Finding #{f.id}: {f.title} (Severity: {f.severity}, Since: {f.found_date.date() if f.found_date else 'N/A'})\n"
        if len(actionless) > 10:
            output += f"  ... and {len(actionless) - 10} more\n"

        output += f"\n## Overdue Corrective Actions ({len(overdue_actions)})\n"
        output += "These actions are past their due date.\n\n"
        for a in overdue_actions[:10]:
            output += f"- Action #{a.id}: {a.title} (Due: {a.due_date.date() if a.due_date else 'N/A'})\n"
        if len(overdue_actions) > 10:
            output += f"  ... and {len(overdue_actions) - 10} more\n"

        return output
