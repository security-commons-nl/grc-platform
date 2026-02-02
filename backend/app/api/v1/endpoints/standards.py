from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.core_models import Standard, Requirement

router = APIRouter()

# --- Standards (Frameworks) ---

@router.get("/standards/", response_model=List[Standard])
async def read_standards(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Standard).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/standards/", response_model=Standard)
async def create_standard(standard: Standard, session: AsyncSession = Depends(get_session)):
    session.add(standard)
    await session.commit()
    await session.refresh(standard)
    return standard

@router.get("/standards/{standard_id}", response_model=Standard)
async def read_standard(standard_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Standard).where(Standard.id == standard_id))
    standard = result.scalars().first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard

# --- Requirements (Controls within Frameworks) ---

@router.post("/standards/{standard_id}/requirements/", response_model=Requirement)
async def create_requirement(standard_id: int, requirement: Requirement, session: AsyncSession = Depends(get_session)):
    # Verify standard exists
    result = await session.execute(select(Standard).where(Standard.id == standard_id))
    standard = result.scalars().first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    requirement.standard_id = standard_id
    session.add(requirement)
    await session.commit()
    await session.refresh(requirement)
    return requirement

@router.get("/standards/{standard_id}/requirements/", response_model=List[Requirement])
async def read_requirements_for_standard(standard_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Requirement).where(Requirement.standard_id == standard_id))
    return result.scalars().all()
