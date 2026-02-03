"""
Generic CRUD utilities for FastAPI endpoints.
Reduces boilerplate across endpoint files.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

ModelType = TypeVar("ModelType", bound=SQLModel)


class CRUDBase(Generic[ModelType]):
    """
    Base class for CRUD operations.

    Usage:
        crud_risk = CRUDBase(Risk)
        risks = await crud_risk.get_multi(session, skip=0, limit=10)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """Get single record by ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def get_or_404(self, session: AsyncSession, id: int) -> ModelType:
        """Get single record by ID or raise 404."""
        obj = await self.get(session, id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return obj

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional filters."""
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_field(
        self,
        session: AsyncSession,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """Get single record by arbitrary field."""
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} has no field '{field}'")
        result = await session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalars().first()

    async def get_multi_by_field(
        self,
        session: AsyncSession,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by arbitrary field."""
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} has no field '{field}'")
        result = await session.execute(
            select(self.model)
            .where(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, session: AsyncSession, *, obj_in: ModelType) -> ModelType:
        """Create new record."""
        session.add(obj_in)
        await session.commit()
        await session.refresh(obj_in)
        return obj_in

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: dict
    ) -> ModelType:
        """Update existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, *, id: int) -> bool:
        """Delete record by ID."""
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False

    async def count(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None
    ) -> int:
        """Count records with optional filters."""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        result = await session.execute(query)
        return result.scalar() or 0
