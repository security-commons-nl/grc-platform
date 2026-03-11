"""
Generic CRUD utilities for FastAPI endpoints.
Reduces boilerplate across endpoint files.

Includes:
- CRUDBase: Standard CRUD without tenant filtering
- TenantCRUDBase: CRUD with automatic tenant_id filtering (recommended)
- ScopedTenantCRUDBase: Tenant + scope-level filtering (for models with scope_id)
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Set
from sqlmodel import SQLModel, select
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

ModelType = TypeVar("ModelType", bound=SQLModel)


def _integrity_error_detail(e: IntegrityError) -> str:
    """Extract a user-friendly message from an IntegrityError."""
    msg = str(e.orig) if e.orig else str(e)
    if "not-null" in msg.lower() or "notnullviolation" in msg.lower():
        # Extract column name from: null value in column "description" ...
        import re
        m = re.search(r'column "(\w+)"', msg)
        col = m.group(1) if m else "unknown"
        return f"Verplicht veld '{col}' ontbreekt of is leeg."
    if "unique" in msg.lower():
        return "Dit item bestaat al (unieke waarde duplicaat)."
    if "foreign" in msg.lower() or "foreignkey" in msg.lower():
        return "Ongeldige referentie — gekoppeld item bestaat niet."
    return f"Database constraint fout: {msg[:200]}"


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
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            detail = _integrity_error_detail(e)
            raise HTTPException(status_code=400, detail=detail)
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
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            detail = _integrity_error_detail(e)
            raise HTTPException(status_code=400, detail=detail)
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, *, id: int) -> bool:
        """Delete record by ID."""
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                detail = _integrity_error_detail(e)
                raise HTTPException(status_code=400, detail=detail)
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
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            detail = _integrity_error_detail(e)
            raise HTTPException(status_code=400, detail=detail)
        # Re-set app.current_tenant: after commit() SQLAlchemy may return the
        # connection to the pool and refresh() gets a new one without the setting.
        # Without it the RLS policy ((current_setting('app.current_tenant'))::integer)
        # fails with "invalid input syntax for type integer: """.
        # set_config is PostgreSQL-only; skip for SQLite (used in tests).
        from sqlalchemy import text
        if session.bind is None or "postgresql" in str(session.bind.url):
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid, false)"),
                {"tid": str(tenant_id)}
            )
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
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            detail = _integrity_error_detail(e)
            raise HTTPException(status_code=400, detail=detail)
        # Re-set app.current_tenant before refresh (same pool-recycle reason as create).
        # set_config is PostgreSQL-only; skip for SQLite (used in tests).
        from sqlalchemy import text
        if session.bind is None or "postgresql" in str(session.bind.url):
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid, false)"),
                {"tid": str(tenant_id)}
            )
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
            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                detail = _integrity_error_detail(e)
                raise HTTPException(status_code=400, detail=detail)
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


class ScopedTenantCRUDBase(TenantCRUDBase[ModelType]):
    """
    Tenant + scope-aware CRUD operations.

    Extends TenantCRUDBase with scope-level filtering for models that have
    a scope_id field. Resources with scope_id=NULL are visible to all tenant members.

    Usage:
        crud_risk = ScopedTenantCRUDBase(Risk)
        risks = await crud_risk.get_multi_scoped(
            session, tenant_id=1, accessible_scope_ids={1, 2, 3}
        )
    """

    def _apply_scope_filter(self, query, accessible_scope_ids: Optional[Set[int]]):
        """Apply scope filter to query.

        Args:
            accessible_scope_ids: Set of scope IDs the user can access.
                None means unrestricted (admin/coordinator/superuser).
        """
        if accessible_scope_ids is None:
            return query  # No restriction

        if not hasattr(self.model, "scope_id"):
            return query  # Model has no scope_id — no filtering

        # Show resources in accessible scopes OR with scope_id=NULL
        return query.where(
            or_(
                self.model.scope_id.in_(accessible_scope_ids),
                self.model.scope_id.is_(None),
            )
        )

    async def get_scoped(
        self,
        session: AsyncSession,
        id: int,
        tenant_id: int,
        accessible_scope_ids: Optional[Set[int]] = None,
    ) -> Optional[ModelType]:
        """Get single record by ID within tenant, with scope check."""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_tenant_filter(query, tenant_id)
        query = self._apply_scope_filter(query, accessible_scope_ids)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_scoped_or_404(
        self,
        session: AsyncSession,
        id: int,
        tenant_id: int,
        accessible_scope_ids: Optional[Set[int]] = None,
    ) -> ModelType:
        """Get single record by ID within tenant + scope, or raise 404."""
        obj = await self.get_scoped(session, id, tenant_id, accessible_scope_ids)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return obj

    async def get_multi_scoped(
        self,
        session: AsyncSession,
        tenant_id: int,
        accessible_scope_ids: Optional[Set[int]] = None,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[ModelType]:
        """Get multiple records within tenant + scope with pagination."""
        query = select(self.model)
        query = self._apply_tenant_filter(query, tenant_id)
        query = self._apply_scope_filter(query, accessible_scope_ids)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def count_scoped(
        self,
        session: AsyncSession,
        tenant_id: int,
        accessible_scope_ids: Optional[Set[int]] = None,
        filters: Optional[dict] = None,
    ) -> int:
        """Count records within tenant + scope."""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        query = self._apply_tenant_filter(query, tenant_id)
        query = self._apply_scope_filter(query, accessible_scope_ids)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        result = await session.execute(query)
        return result.scalar() or 0
