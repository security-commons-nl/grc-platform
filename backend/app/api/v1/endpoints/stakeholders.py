from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from app.api import deps
from app.models.core_models import (
    Stakeholder,
    User,
)

router = APIRouter()


@router.get("/", response_model=List[Stakeholder])
def read_stakeholders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve stakeholders.
    """
    query = select(Stakeholder).where(Stakeholder.tenant_id == current_user.tenant_memberships[0].tenant_id)
    return db.exec(query.offset(skip).limit(limit)).all()


@router.post("/", response_model=Stakeholder)
def create_stakeholder(
    *,
    db: Session = Depends(deps.get_db),
    stakeholder_in: Stakeholder,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new stakeholder.
    """
    stakeholder = Stakeholder.from_orm(stakeholder_in)
    stakeholder.tenant_id = current_user.tenant_memberships[0].tenant_id
    db.add(stakeholder)
    db.commit()
    db.refresh(stakeholder)
    return stakeholder


@router.put("/{stakeholder_id}", response_model=Stakeholder)
def update_stakeholder(
    *,
    db: Session = Depends(deps.get_db),
    stakeholder_id: int,
    stakeholder_in: Stakeholder,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a stakeholder.
    """
    stakeholder = db.get(Stakeholder, stakeholder_id)
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    if stakeholder.tenant_id != current_user.tenant_memberships[0].tenant_id:
         raise HTTPException(status_code=400, detail="Not enough permissions")

    stakeholder_data = stakeholder_in.dict(exclude_unset=True)
    for key, value in stakeholder_data.items():
        setattr(stakeholder, key, value)
    
    db.add(stakeholder)
    db.commit()
    db.refresh(stakeholder)
    return stakeholder


@router.delete("/{stakeholder_id}", response_model=Stakeholder)
def delete_stakeholder(
    *,
    db: Session = Depends(deps.get_db),
    stakeholder_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a stakeholder.
    """
    stakeholder = db.get(Stakeholder, stakeholder_id)
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    if stakeholder.tenant_id != current_user.tenant_memberships[0].tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    db.delete(stakeholder)
    db.commit()
    return stakeholder
