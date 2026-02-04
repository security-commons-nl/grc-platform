from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.core_models import (
    BacklogItem, 
    BacklogStatus, 
    BacklogType, 
    BacklogPriority
)

router = APIRouter()

@router.get("/", response_model=List[BacklogItem])
async def read_backlog_items(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = None,
    item_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> Any:
    """
    Retrieve backlog items.
    """
    query = select(BacklogItem)
    
    if tenant_id:
        query = query.where(BacklogItem.tenant_id == tenant_id)
    if item_type:
        query = query.where(BacklogItem.item_type == item_type)
    if status:
        query = query.where(BacklogItem.status == status)
    if priority:
        query = query.where(BacklogItem.priority == priority)
        
    # Order by priority (Critical first) and then date
    # In a real app we'd need a custom sort for the Enum, or integer values
    # For now, default sorting by created_at desc
    query = query.order_by(BacklogItem.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    items = result.scalars().all()
    return items


@router.post("/", response_model=BacklogItem)
async def create_backlog_item(
    *,
    session: AsyncSession = Depends(get_session),
    item_in: BacklogItem,
) -> Any:
    """
    Create new backlog item.
    """
    session.add(item_in)
    await session.commit()
    await session.refresh(item_in)
    return item_in


@router.get("/{id}", response_model=BacklogItem)
async def read_backlog_item(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
) -> Any:
    """
    Get backlog item by ID.
    """
    item = await session.get(BacklogItem, id)
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")
    return item


@router.patch("/{id}", response_model=BacklogItem)
async def update_backlog_item(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
    item_in: dict,
) -> Any:
    """
    Update backlog item.
    """
    item = await session.get(BacklogItem, id)
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")
        
    for key, value in item_in.items():
        if hasattr(item, key):
            setattr(item, key, value)
            
    await session.commit()
    await session.refresh(item)
    return item


@router.delete("/{id}", response_model=dict)
async def delete_backlog_item(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
) -> Any:
    """
    Delete backlog item.
    """
    item = await session.get(BacklogItem, id)
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")
        
    await session.delete(item)
    await session.commit()
    return {"ok": True}
