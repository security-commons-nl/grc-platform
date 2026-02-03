from fastapi import APIRouter
from app.api.v1.endpoints import (
    standards,
    scopes,
    risks,
    users,
    assessments,
    incidents,
    policies,
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
