"""
Generic CRUD utilities for FastAPI endpoints.
Reduces boilerplate across endpoint files.

Includes:
- CRUDBase: Standard CRUD without tenant filtering
- TenantCRUDBase: CRUD with automatic tenant_id filtering (recommended)
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


class TenantCRUDBase(CRUDBase[ModelType]):
    """
    Tenant-aware CRUD operations.

    Automatically filters all queries by tenant_id to enforce data isolation.
    Use this for all multi-tenant models.

    Usage:
        crud_risk = TenantCRUDBase(Risk)
        risks = await crud_risk.get_multi(session, tenant_id=1)
    """

    def _apply_tenant_filter(self, query, tenant_id: int):
        """Apply tenant filter to query."""
        if not hasattr(self.model, "tenant_id"):
            raise ValueError(f"{self.model.__name__} does not have tenant_id field")
        return query.where(self.model.tenant_id == tenant_id)

    async def get(
        self,
        session: AsyncSession,
        id: int,
        tenant_id: int
    ) -> Optional[ModelType]:
        """Get single record by ID within tenant."""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_tenant_filter(query, tenant_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_or_404(
        self,
        session: AsyncSession,
        id: int,
        tenant_id: int
    ) -> ModelType:
        """Get single record by ID within tenant or raise 404."""
        obj = await self.get(session, id, tenant_id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return obj

    async def get_multi(
        self,
        session: AsyncSession,
        tenant_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get multiple records within tenant with pagination."""
        query = select(self.model)
        query = self._apply_tenant_filter(query, tenant_id)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: ModelType,
        tenant_id: int
    ) -> ModelType:
        """Create new record with tenant_id enforced."""
        if hasattr(obj_in, "tenant_id"):
            obj_in.tenant_id = tenant_id
        session.add(obj_in)
        await session.commit()
        await session.refresh(obj_in)
        return obj_in

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: dict,
        tenant_id: int
    ) -> ModelType:
        """Update existing record (verifies tenant ownership)."""
        # Verify the object belongs to the tenant
        if hasattr(db_obj, "tenant_id") and db_obj.tenant_id != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: object belongs to different tenant"
            )

        # Prevent changing tenant_id
        obj_in.pop("tenant_id", None)

        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        session: AsyncSession,
        *,
        id: int,
        tenant_id: int
    ) -> bool:
        """Delete record by ID (verifies tenant ownership)."""
        obj = await self.get(session, id, tenant_id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False

    async def count(
        self,
        session: AsyncSession,
        tenant_id: int,
        filters: Optional[dict] = None
    ) -> int:
        """Count records within tenant."""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        query = self._apply_tenant_filter(query, tenant_id)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        result = await session.execute(query)
        return result.scalar() or 0
