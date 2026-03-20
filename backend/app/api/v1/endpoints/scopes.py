from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSScope
from app.schemas.scopes import ScopeCreate, ScopeUpdate, ScopeResponse

router = APIRouter()


@router.get("/", response_model=list[ScopeResponse])
async def list_scopes(
    tenant_id: UUID = Query(...),
    type: str | None = None,
    domain: str | None = None,
    parent_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSScope).where(IMSScope.tenant_id == tenant_id)
    if type:
        query = query.where(IMSScope.type == type)
    if domain:
        query = query.where(IMSScope.domain == domain)
    if parent_id:
        query = query.where(IMSScope.parent_id == parent_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{scope_id}", response_model=ScopeResponse)
async def get_scope(scope_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSScope).where(IMSScope.id == scope_id))
    scope = result.scalar_one_or_none()
    if not scope:
        raise HTTPException(status_code=404, detail="Scope not found")
    return scope


@router.post("/", response_model=ScopeResponse, status_code=201)
async def create_scope(
    data: ScopeCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    scope = IMSScope(tenant_id=tenant_id, **data.model_dump())
    db.add(scope)
    await db.commit()
    await db.refresh(scope)
    return scope


@router.patch("/{scope_id}", response_model=ScopeResponse)
async def update_scope(scope_id: UUID, data: ScopeUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSScope).where(IMSScope.id == scope_id))
    scope = result.scalar_one_or_none()
    if not scope:
        raise HTTPException(status_code=404, detail="Scope not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(scope, field, value)
    await db.commit()
    await db.refresh(scope)
    return scope


@router.delete("/{scope_id}", status_code=204)
async def delete_scope(scope_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSScope).where(IMSScope.id == scope_id))
    scope = result.scalar_one_or_none()
    if not scope:
        raise HTTPException(status_code=404, detail="Scope not found")
    await db.delete(scope)
    await db.commit()
