from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.core_models import Standard, Requirement
from app.services.knowledge_service import knowledge_service

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Standards (Frameworks) ---

@router.get("/", response_model=List[Standard])
async def read_standards(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Standard).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=Standard)
async def create_standard(standard: Standard, session: AsyncSession = Depends(get_session)):
    """Create a new standard/framework. Also indexes in knowledge base for AI RAG."""
    session.add(standard)
    await session.commit()
    await session.refresh(standard)

    # Index in knowledge base for AI RAG
    try:
        content = f"Framework/Standaard: {standard.name}\n\nVersie: {standard.version or ''}\n\nBeschrijving: {standard.description or ''}"
        await knowledge_service.add_knowledge(
            session=session,
            key=f"standard_{standard.id}",
            title=standard.name,
            content=content,
            category="standard"
        )
    except Exception as e:
        logger.warning(f"Failed to index standard {standard.id} in knowledge base: {e}")

    return standard

@router.get("/{standard_id}", response_model=Standard)
async def read_standard(standard_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Standard).where(Standard.id == standard_id))
    standard = result.scalars().first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard

# --- Requirements (Controls within Frameworks) ---

@router.post("/{standard_id}/requirements/", response_model=Requirement)
async def create_requirement(standard_id: int, requirement: Requirement, session: AsyncSession = Depends(get_session)):
    """Create a new requirement/control. Also indexes in knowledge base for AI RAG."""
    # Verify standard exists
    result = await session.execute(select(Standard).where(Standard.id == standard_id))
    standard = result.scalars().first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")

    requirement.standard_id = standard_id
    session.add(requirement)
    await session.commit()
    await session.refresh(requirement)

    # Index in knowledge base for AI RAG
    try:
        content = f"Requirement/Control: {requirement.code} - {requirement.title}\n\nFramework: {standard.name}\n\nBeschrijving: {requirement.description or ''}\n\nGuidance: {requirement.guidance or ''}"
        await knowledge_service.add_knowledge(
            session=session,
            key=f"requirement_{requirement.id}",
            title=f"{requirement.code}: {requirement.title}",
            content=content,
            category="requirement"
        )
    except Exception as e:
        logger.warning(f"Failed to index requirement {requirement.id} in knowledge base: {e}")

    return requirement

@router.get("/{standard_id}/requirements/", response_model=List[Requirement])
async def read_requirements_for_standard(standard_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Requirement).where(Requirement.standard_id == standard_id))
    return result.scalars().all()
