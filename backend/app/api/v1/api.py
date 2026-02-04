from fastapi import APIRouter
from app.api.v1.endpoints import (
    standards,
    scopes,
    risks,
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
)

api_router = APIRouter()

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
