from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, tenants, steps, decisions, documents,
    standards, scopes, risks, controls, assessments,
    evidence, incidents, scores, knowledge,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(steps.router, prefix="/steps", tags=["steps"])
api_router.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(standards.router, prefix="/standards", tags=["standards"])
api_router.include_router(scopes.router, prefix="/scopes", tags=["scopes"])
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(controls.router, prefix="/controls", tags=["controls"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(scores.router, prefix="/scores", tags=["scores"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
