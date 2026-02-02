from fastapi import APIRouter
from app.api.v1.endpoints import standards

api_router = APIRouter()
api_router.include_router(standards.router, tags=["Layer 1: Standards"])
