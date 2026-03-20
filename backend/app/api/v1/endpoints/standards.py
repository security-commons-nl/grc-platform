from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import (
    IMSStandard, IMSRequirement, IMSRequirementMapping,
    IMSTenantNormenkader, IMSStandardIngestion,
)
from app.schemas.standards import (
    StandardCreate, StandardUpdate, StandardResponse,
    RequirementCreate, RequirementUpdate, RequirementResponse,
    RequirementMappingCreate, RequirementMappingUpdate, RequirementMappingResponse,
    TenantNormenkaderCreate, TenantNormenkaderUpdate, TenantNormenkaderResponse,
    StandardIngestionCreate, StandardIngestionUpdate, StandardIngestionResponse,
)

router = APIRouter()


# ── Standards ──────────────────────────────────────────────────────────────


@router.get("/", response_model=list[StandardResponse])
async def list_standards(
    domain: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStandard)
    if domain:
        query = query.where(IMSStandard.domain == domain)
    if status:
        query = query.where(IMSStandard.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{standard_id}", response_model=StandardResponse)
async def get_standard(standard_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSStandard).where(IMSStandard.id == standard_id))
    standard = result.scalar_one_or_none()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard


@router.post("/", response_model=StandardResponse, status_code=201)
async def create_standard(data: StandardCreate, db: AsyncSession = Depends(get_db)):
    standard = IMSStandard(**data.model_dump())
    db.add(standard)
    await db.commit()
    await db.refresh(standard)
    return standard


@router.patch("/{standard_id}", response_model=StandardResponse)
async def update_standard(standard_id: UUID, data: StandardUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSStandard).where(IMSStandard.id == standard_id))
    standard = result.scalar_one_or_none()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(standard, field, value)
    await db.commit()
    await db.refresh(standard)
    return standard


@router.delete("/{standard_id}", status_code=204)
async def delete_standard(standard_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSStandard).where(IMSStandard.id == standard_id))
    standard = result.scalar_one_or_none()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    await db.delete(standard)
    await db.commit()


# ── Requirements ───────────────────────────────────────────────────────────


@router.get("/requirements/", response_model=list[RequirementResponse])
async def list_requirements(
    standard_id: UUID | None = None,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRequirement)
    if standard_id:
        query = query.where(IMSRequirement.standard_id == standard_id)
    if domain:
        query = query.where(IMSRequirement.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRequirement).where(IMSRequirement.id == requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.post("/requirements/", response_model=RequirementResponse, status_code=201)
async def create_requirement(data: RequirementCreate, db: AsyncSession = Depends(get_db)):
    req = IMSRequirement(**data.model_dump())
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


@router.patch("/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(requirement_id: UUID, data: RequirementUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRequirement).where(IMSRequirement.id == requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(req, field, value)
    await db.commit()
    await db.refresh(req)
    return req


@router.delete("/requirements/{requirement_id}", status_code=204)
async def delete_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSRequirement).where(IMSRequirement.id == requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    await db.delete(req)
    await db.commit()


# ── Requirement Mappings ───────────────────────────────────────────────────


@router.get("/mappings/", response_model=list[RequirementMappingResponse])
async def list_requirement_mappings(
    source_requirement_id: UUID | None = None,
    target_requirement_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRequirementMapping)
    if source_requirement_id:
        query = query.where(IMSRequirementMapping.source_requirement_id == source_requirement_id)
    if target_requirement_id:
        query = query.where(IMSRequirementMapping.target_requirement_id == target_requirement_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/mappings/{mapping_id}", response_model=RequirementMappingResponse)
async def get_requirement_mapping(mapping_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSRequirementMapping).where(IMSRequirementMapping.id == mapping_id)
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="RequirementMapping not found")
    return mapping


@router.post("/mappings/", response_model=RequirementMappingResponse, status_code=201)
async def create_requirement_mapping(data: RequirementMappingCreate, db: AsyncSession = Depends(get_db)):
    mapping = IMSRequirementMapping(**data.model_dump())
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


@router.patch("/mappings/{mapping_id}", response_model=RequirementMappingResponse)
async def update_requirement_mapping(
    mapping_id: UUID, data: RequirementMappingUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IMSRequirementMapping).where(IMSRequirementMapping.id == mapping_id)
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="RequirementMapping not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mapping, field, value)
    await db.commit()
    await db.refresh(mapping)
    return mapping


@router.delete("/mappings/{mapping_id}", status_code=204)
async def delete_requirement_mapping(mapping_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSRequirementMapping).where(IMSRequirementMapping.id == mapping_id)
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="RequirementMapping not found")
    await db.delete(mapping)
    await db.commit()


# ── Tenant Normenkader ─────────────────────────────────────────────────────


@router.get("/normenkader/", response_model=list[TenantNormenkaderResponse])
async def list_tenant_normenkader(
    tenant_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(IMSTenantNormenkader)
        .where(IMSTenantNormenkader.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/normenkader/", response_model=TenantNormenkaderResponse, status_code=201)
async def create_tenant_normenkader(
    data: TenantNormenkaderCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    nk = IMSTenantNormenkader(tenant_id=tenant_id, **data.model_dump())
    db.add(nk)
    await db.commit()
    await db.refresh(nk)
    return nk


@router.patch("/normenkader/{nk_id}", response_model=TenantNormenkaderResponse)
async def update_tenant_normenkader(
    nk_id: UUID, data: TenantNormenkaderUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IMSTenantNormenkader).where(IMSTenantNormenkader.id == nk_id)
    )
    nk = result.scalar_one_or_none()
    if not nk:
        raise HTTPException(status_code=404, detail="TenantNormenkader not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(nk, field, value)
    await db.commit()
    await db.refresh(nk)
    return nk


@router.delete("/normenkader/{nk_id}", status_code=204)
async def delete_tenant_normenkader(nk_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSTenantNormenkader).where(IMSTenantNormenkader.id == nk_id)
    )
    nk = result.scalar_one_or_none()
    if not nk:
        raise HTTPException(status_code=404, detail="TenantNormenkader not found")
    await db.delete(nk)
    await db.commit()


# ── Standard Ingestions ────────────────────────────────────────────────────


@router.get("/ingestions/", response_model=list[StandardIngestionResponse])
async def list_standard_ingestions(
    tenant_id: UUID = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStandardIngestion).where(IMSStandardIngestion.tenant_id == tenant_id)
    if status_filter:
        query = query.where(IMSStandardIngestion.status == status_filter)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/ingestions/{ingestion_id}", response_model=StandardIngestionResponse)
async def get_standard_ingestion(ingestion_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSStandardIngestion).where(IMSStandardIngestion.id == ingestion_id)
    )
    ingestion = result.scalar_one_or_none()
    if not ingestion:
        raise HTTPException(status_code=404, detail="StandardIngestion not found")
    return ingestion


@router.post("/ingestions/", response_model=StandardIngestionResponse, status_code=201)
async def create_standard_ingestion(
    data: StandardIngestionCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    ingestion = IMSStandardIngestion(tenant_id=tenant_id, **data.model_dump())
    db.add(ingestion)
    await db.commit()
    await db.refresh(ingestion)
    return ingestion


@router.patch("/ingestions/{ingestion_id}", response_model=StandardIngestionResponse)
async def update_standard_ingestion(
    ingestion_id: UUID, data: StandardIngestionUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IMSStandardIngestion).where(IMSStandardIngestion.id == ingestion_id)
    )
    ingestion = result.scalar_one_or_none()
    if not ingestion:
        raise HTTPException(status_code=404, detail="StandardIngestion not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ingestion, field, value)
    await db.commit()
    await db.refresh(ingestion)
    return ingestion


@router.delete("/ingestions/{ingestion_id}", status_code=204)
async def delete_standard_ingestion(ingestion_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSStandardIngestion).where(IMSStandardIngestion.id == ingestion_id)
    )
    ingestion = result.scalar_one_or_none()
    if not ingestion:
        raise HTTPException(status_code=404, detail="StandardIngestion not found")
    await db.delete(ingestion)
    await db.commit()
