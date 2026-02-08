"""
Domain-specific AI Agents for IMS.

Each agent is specialized for a specific GRC domain.
"""
from app.agents.domains.risk_agent import RiskAgent
from app.agents.domains.compliance_agent import ComplianceAgent
from app.agents.domains.measure_agent import MeasureAgent
from app.agents.domains.policy_agent import PolicyAgent
from app.agents.domains.scope_agent import ScopeAgent
from app.agents.domains.assessment_agent import AssessmentAgent
from app.agents.domains.incident_agent import IncidentAgent
from app.agents.domains.privacy_agent import PrivacyAgent
from app.agents.domains.bcm_agent import BCMAgent
from app.agents.domains.supplier_agent import SupplierAgent
from app.agents.domains.improvement_agent import ImprovementAgent
from app.agents.domains.workflow_agent import WorkflowAgent
from app.agents.domains.planning_agent import PlanningAgent
from app.agents.domains.report_agent import ReportAgent
from app.agents.domains.objectives_agent import ObjectivesAgent
from app.agents.domains.maturity_agent import MaturityAgent
from app.agents.domains.admin_agent import AdminAgent
from app.agents.domains.onboarding_agent import OnboardingAgent

# All available agents
ALL_AGENTS = {
    "risk": RiskAgent,
    "compliance": ComplianceAgent,
    "measure": MeasureAgent,
    "policy": PolicyAgent,
    "scope": ScopeAgent,
    "assessment": AssessmentAgent,
    "incident": IncidentAgent,
    "privacy": PrivacyAgent,
    "bcm": BCMAgent,
    "supplier": SupplierAgent,
    "improvement": ImprovementAgent,
    "workflow": WorkflowAgent,
    "planning": PlanningAgent,
    "report": ReportAgent,
    "objectives": ObjectivesAgent,
    "maturity": MaturityAgent,
    "admin": AdminAgent,
    "onboarding": OnboardingAgent,
}

__all__ = [
    "RiskAgent",
    "ComplianceAgent",
    "MeasureAgent",
    "PolicyAgent",
    "ScopeAgent",
    "AssessmentAgent",
    "IncidentAgent",
    "PrivacyAgent",
    "BCMAgent",
    "SupplierAgent",
    "ImprovementAgent",
    "WorkflowAgent",
    "PlanningAgent",
    "ReportAgent",
    "ObjectivesAgent",
    "MaturityAgent",
    "AdminAgent",
    "OnboardingAgent",
    "ALL_AGENTS",
]
