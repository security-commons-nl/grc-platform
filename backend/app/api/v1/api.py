from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    standards,
    scopes,
    risks,
    measures,
    controls,
    users,
    assessments,
    incidents,
    policies,
    workflows,
    soa,
    reports,
    backlog,
    tenants,
    documents,
    privacy,
    continuity,
    agents,
    webhooks,
    sync,
    knowledge,
    dashboard,
    decisions,
    risk_framework,
    in_control,
    policy_principles,
    system,
    graph,
    organization_profile,
)

api_router = APIRouter()

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Layer 1: Governance (Standards & Requirements)
api_router.include_router(
    standards.router,
    prefix="/standards",
    tags=["Governance: Standards"]
)

# Layer 1: Governance (Policies)
api_router.include_router(
    policies.router,
    prefix="/policies",
    tags=["Governance: Policies"]
)

# Scope Management (Foundation for RBAC)
api_router.include_router(
    scopes.router,
    prefix="/scopes",
    tags=["Scope Management"]
)

# Risk Management (Core GRC)
api_router.include_router(
    risks.router,
    prefix="/risks",
    tags=["Risk Management"]
)

# Measure Catalog (Reusable building blocks)
api_router.include_router(
    measures.router,
    prefix="/measures",
    tags=["Measure Catalog"]
)

# Control Management (Context-specific implementations)
api_router.include_router(
    controls.router,
    prefix="/controls",
    tags=["Control Management"]
)

# User Management & RBAC
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users & RBAC"]
)

# Verification (PDCA Check)
api_router.include_router(
    assessments.router,
    prefix="/assessments",
    tags=["Verification: Assessments"]
)

# Improvement (PDCA Act)
api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["Improvement: Incidents"]
)

# Workflows
api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["Workflows"]
)

# Statement of Applicability (Compliance)
api_router.include_router(
    soa.router,
    prefix="/soa",
    tags=["Statement of Applicability"]
)

# Reports & Dashboard
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports & Dashboard"]
)

# Operational Dashboard
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

# Backlog
api_router.include_router(
    backlog.router,
    prefix="/backlog",
    tags=["Backlog"]
)

# Tenant Management
api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["Tenant Management"]
)

# Document Management
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Document Management"]
)

# Privacy (PIMS/AVG)
api_router.include_router(
    privacy.router,
    prefix="/privacy",
    tags=["Privacy: PIMS/AVG"]
)

# Business Continuity (BCMS)
api_router.include_router(
    continuity.router,
    prefix="/continuity",
    tags=["Business Continuity: BCMS"]
)

# AI Agents
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["AI Agents"]
)

# External Integrations - Webhooks
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Integrations: Webhooks"]
)

# External Integrations - Sync
api_router.include_router(
    sync.router,
    prefix="/sync",
    tags=["Integrations: Sync"]
)

# Knowledge Base
api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["Knowledge Base"]
)

# Simulation (Monte Carlo)
from app.api.v1.endpoints import simulation
api_router.include_router(
    simulation.router,
    prefix="/simulation",
    tags=["Simulation"]
)

# Hiaat 1: Besluitlog (Decision Log)
api_router.include_router(
    decisions.router,
    prefix="/decisions",
    tags=["Besluitlog: Decisions"]
)

# Hiaat 3: Risicokader (Risk Framework)
api_router.include_router(
    risk_framework.router,
    prefix="/risk-framework",
    tags=["Risk Framework"]
)

# Hiaat 5: In-Control Status
api_router.include_router(
    in_control.router,
    prefix="/in-control",
    tags=["In-Control Status"]
)

# Hiaat 6: Beleid-trace (Policy Principles)
api_router.include_router(
    policy_principles.router,
    prefix="/policy-principles",
    tags=["Policy Principles"]
)

# System Administration
api_router.include_router(
    system.router,
    prefix="/system",
    tags=["System Administration"]
)

# Relationship Graph
api_router.include_router(
    graph.router,
    prefix="/graph",
    tags=["Relationship Graph"]
)
