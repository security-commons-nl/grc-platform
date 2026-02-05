"""
Statement of Applicability (SoA) Endpoints
Manages requirement applicability and compliance tracking per scope.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import func

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    ApplicabilityStatement,
    Requirement,
    Standard,
    Scope,
    Measure,
    CoverageType,
    ImplementationStatus,
)

router = APIRouter()
crud_soa = CRUDBase(ApplicabilityStatement)
crud_requirement = CRUDBase(Requirement)
crud_standard = CRUDBase(Standard)
crud_scope = CRUDBase(Scope)
crud_measure = CRUDBase(Measure)


# =============================================================================
# STATEMENT OF APPLICABILITY CRUD
# =============================================================================

@router.get("/", response_model=List[ApplicabilityStatement])
async def list_applicability_statements(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    scope_id: Optional[int] = Query(None, description="Filter by scope"),
    standard_id: Optional[int] = Query(None, description="Filter by standard"),
    is_applicable: Optional[bool] = Query(None, description="Filter by applicability"),
    coverage_type: Optional[CoverageType] = Query(None, description="Filter by coverage"),
    implementation_status: Optional[ImplementationStatus] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_session),
):
    """List applicability statements with optional filters."""
    query = select(ApplicabilityStatement)

    if tenant_id:
        query = query.where(ApplicabilityStatement.tenant_id == tenant_id)
    if scope_id:
        query = query.where(ApplicabilityStatement.scope_id == scope_id)
    if is_applicable is not None:
        query = query.where(ApplicabilityStatement.is_applicable == is_applicable)
    if coverage_type:
        query = query.where(ApplicabilityStatement.coverage_type == coverage_type)
    if implementation_status:
        query = query.where(ApplicabilityStatement.implementation_status == implementation_status)

    # Join with Requirement to filter by standard
    if standard_id:
        query = query.join(Requirement).where(Requirement.standard_id == standard_id)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ApplicabilityStatement)
async def create_applicability_statement(
    soa: ApplicabilityStatement,
    session: AsyncSession = Depends(get_session),
):
    """Create a new applicability statement."""
    # Verify requirement exists
    await crud_requirement.get_or_404(session, soa.requirement_id)

    # Verify scope exists
    await crud_scope.get_or_404(session, soa.scope_id)

    # Check for duplicate
    existing = await session.execute(
        select(ApplicabilityStatement)
        .where(ApplicabilityStatement.tenant_id == soa.tenant_id)
        .where(ApplicabilityStatement.scope_id == soa.scope_id)
        .where(ApplicabilityStatement.requirement_id == soa.requirement_id)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Applicability statement already exists for this scope/requirement"
        )

    # Set coverage type based on measure links
    if soa.local_measure_id and soa.shared_measure_id:
        soa.coverage_type = CoverageType.COMBINED
    elif soa.local_measure_id:
        soa.coverage_type = CoverageType.LOCAL
    elif soa.shared_measure_id:
        soa.coverage_type = CoverageType.SHARED
    elif not soa.is_applicable:
        soa.coverage_type = CoverageType.NOT_APPLICABLE
    else:
        soa.coverage_type = CoverageType.NOT_COVERED

    return await crud_soa.create(session, obj_in=soa)


@router.get("/{soa_id}", response_model=ApplicabilityStatement)
async def get_applicability_statement(
    soa_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get an applicability statement by ID."""
    return await crud_soa.get_or_404(session, soa_id)


@router.patch("/{soa_id}", response_model=ApplicabilityStatement)
async def update_applicability_statement(
    soa_id: int,
    soa_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update an applicability statement."""
    db_soa = await crud_soa.get_or_404(session, soa_id)

    # Update coverage type based on measure changes
    local_measure = soa_update.get("local_measure_id", db_soa.local_measure_id)
    shared_measure = soa_update.get("shared_measure_id", db_soa.shared_measure_id)
    is_applicable = soa_update.get("is_applicable", db_soa.is_applicable)

    if local_measure and shared_measure:
        soa_update["coverage_type"] = CoverageType.COMBINED
    elif local_measure:
        soa_update["coverage_type"] = CoverageType.LOCAL
    elif shared_measure:
        soa_update["coverage_type"] = CoverageType.SHARED
    elif not is_applicable:
        soa_update["coverage_type"] = CoverageType.NOT_APPLICABLE
    else:
        soa_update["coverage_type"] = CoverageType.NOT_COVERED

    soa_update["updated_at"] = datetime.utcnow()
    return await crud_soa.update(session, db_obj=db_soa, obj_in=soa_update)


@router.delete("/{soa_id}")
async def delete_applicability_statement(
    soa_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an applicability statement."""
    deleted = await crud_soa.delete(session, id=soa_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Applicability statement not found")
    return {"message": "Applicability statement deleted"}


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post("/scope/{scope_id}/initialize-from-standard/{standard_id}")
async def initialize_soa_from_standard(
    scope_id: int,
    standard_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    Initialize SoA entries for all requirements in a standard for a given scope.
    Creates applicability statements with default values.
    """
    # Verify scope exists
    scope = await crud_scope.get_or_404(session, scope_id)

    # Verify standard exists
    standard = await crud_standard.get_or_404(session, standard_id)

    # Get all requirements for this standard
    requirements_result = await session.execute(
        select(Requirement).where(Requirement.standard_id == standard_id)
    )
    requirements = requirements_result.scalars().all()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Standard has no requirements"
        )

    created_count = 0
    skipped_count = 0

    # Optimize: Fetch all existing SoA entries for this scope and standard in one query
    req_ids = [r.id for r in requirements]
    existing_result = await session.execute(
        select(ApplicabilityStatement.requirement_id)
        .where(ApplicabilityStatement.tenant_id == tenant_id)
        .where(ApplicabilityStatement.scope_id == scope_id)
        .where(ApplicabilityStatement.requirement_id.in_(req_ids))
    )
    existing_req_ids = set(existing_result.scalars().all())

    for req in requirements:
        # Check if already exists
        if req.id in existing_req_ids:
            skipped_count += 1
            continue

        # Create new SoA entry
        soa = ApplicabilityStatement(
            tenant_id=tenant_id,
            scope_id=scope_id,
            requirement_id=req.id,
            is_applicable=True,
            justification="Initialized from standard - needs review",
            implementation_status=ImplementationStatus.NOT_STARTED,
            coverage_type=CoverageType.NOT_COVERED,
        )
        session.add(soa)
        created_count += 1

    await session.commit()

    return {
        "message": f"SoA initialized for {standard.name}",
        "created": created_count,
        "skipped": skipped_count,
        "total_requirements": len(requirements),
    }


@router.post("/scope/{scope_id}/link-measure/{measure_id}")
async def link_measure_to_requirements(
    scope_id: int,
    measure_id: int,
    requirement_ids: List[int],
    tenant_id: int = Query(..., description="Tenant ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    Link a measure to multiple requirements in the SoA.
    Updates existing applicability statements or creates new ones.
    """
    # Verify measure exists
    measure = await crud_measure.get_or_404(session, measure_id)

    # Verify scope exists
    await crud_scope.get_or_404(session, scope_id)

    updated_count = 0
    created_count = 0

    for req_id in requirement_ids:
        # Check if SoA entry exists
        existing_result = await session.execute(
            select(ApplicabilityStatement)
            .where(ApplicabilityStatement.tenant_id == tenant_id)
            .where(ApplicabilityStatement.scope_id == scope_id)
            .where(ApplicabilityStatement.requirement_id == req_id)
        )
        existing = existing_result.scalars().first()

        if existing:
            # Update existing
            existing.local_measure_id = measure_id
            if existing.shared_measure_id:
                existing.coverage_type = CoverageType.COMBINED
            else:
                existing.coverage_type = CoverageType.LOCAL
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            updated_count += 1
        else:
            # Create new
            soa = ApplicabilityStatement(
                tenant_id=tenant_id,
                scope_id=scope_id,
                requirement_id=req_id,
                is_applicable=True,
                justification="Linked via measure",
                local_measure_id=measure_id,
                coverage_type=CoverageType.LOCAL,
                implementation_status=ImplementationStatus.IN_PROGRESS,
            )
            session.add(soa)
            created_count += 1

    await session.commit()

    return {
        "message": f"Measure linked to {updated_count + created_count} requirements",
        "updated": updated_count,
        "created": created_count,
    }


# =============================================================================
# SOA REPORTING & STATISTICS
# =============================================================================

@router.get("/scope/{scope_id}/summary", response_model=dict)
async def get_soa_summary(
    scope_id: int,
    tenant_id: Optional[int] = None,
    standard_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get SoA compliance summary for a scope.
    Returns statistics on applicability and implementation status.
    """
    await crud_scope.get_or_404(session, scope_id)

    # Base query
    query = select(ApplicabilityStatement).where(ApplicabilityStatement.scope_id == scope_id)
    if tenant_id:
        query = query.where(ApplicabilityStatement.tenant_id == tenant_id)

    # Filter by standard if specified
    if standard_id:
        query = query.join(Requirement).where(Requirement.standard_id == standard_id)

    result = await session.execute(query)
    statements = result.scalars().all()

    # Calculate statistics
    total = len(statements)
    applicable = sum(1 for s in statements if s.is_applicable)
    not_applicable = total - applicable

    # Coverage breakdown
    coverage_stats = {
        "local": sum(1 for s in statements if s.coverage_type == CoverageType.LOCAL),
        "shared": sum(1 for s in statements if s.coverage_type == CoverageType.SHARED),
        "combined": sum(1 for s in statements if s.coverage_type == CoverageType.COMBINED),
        "not_covered": sum(1 for s in statements if s.coverage_type == CoverageType.NOT_COVERED),
        "not_applicable": sum(1 for s in statements if s.coverage_type == CoverageType.NOT_APPLICABLE),
    }

    # Implementation status breakdown
    implementation_stats = {
        "not_started": sum(1 for s in statements if s.implementation_status == ImplementationStatus.NOT_STARTED),
        "in_progress": sum(1 for s in statements if s.implementation_status == ImplementationStatus.IN_PROGRESS),
        "implemented": sum(1 for s in statements if s.implementation_status == ImplementationStatus.IMPLEMENTED),
        "not_applicable": sum(1 for s in statements if s.implementation_status == ImplementationStatus.NOT_APPLICABLE),
    }

    # Calculate compliance percentage (implemented / applicable)
    if applicable > 0:
        compliance_pct = round(implementation_stats["implemented"] / applicable * 100, 1)
    else:
        compliance_pct = 100.0

    return {
        "scope_id": scope_id,
        "total_requirements": total,
        "applicable": applicable,
        "not_applicable": not_applicable,
        "coverage": coverage_stats,
        "implementation": implementation_stats,
        "compliance_percentage": compliance_pct,
    }


@router.get("/scope/{scope_id}/gaps", response_model=List[dict])
async def get_soa_gaps(
    scope_id: int,
    tenant_id: Optional[int] = None,
    standard_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get list of gaps (applicable requirements not yet covered).
    """
    await crud_scope.get_or_404(session, scope_id)

    query = (
        select(ApplicabilityStatement, Requirement)
        .join(Requirement)
        .where(ApplicabilityStatement.scope_id == scope_id)
        .where(ApplicabilityStatement.is_applicable == True)
        .where(ApplicabilityStatement.coverage_type == CoverageType.NOT_COVERED)
    )

    if tenant_id:
        query = query.where(ApplicabilityStatement.tenant_id == tenant_id)
    if standard_id:
        query = query.where(Requirement.standard_id == standard_id)

    result = await session.execute(query)
    rows = result.all()

    gaps = []
    for soa, req in rows:
        gaps.append({
            "soa_id": soa.id,
            "requirement_id": req.id,
            "requirement_code": req.code,
            "requirement_title": req.title,
            "category": req.category,
            "justification": soa.justification,
            "target_date": soa.target_date.isoformat() if soa.target_date else None,
        })

    return gaps


@router.get("/scope/{scope_id}/by-standard", response_model=dict)
async def get_soa_by_standard(
    scope_id: int,
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get SoA entries grouped by standard.
    """
    await crud_scope.get_or_404(session, scope_id)

    query = (
        select(ApplicabilityStatement, Requirement, Standard)
        .join(Requirement)
        .join(Standard)
        .where(ApplicabilityStatement.scope_id == scope_id)
    )

    if tenant_id:
        query = query.where(ApplicabilityStatement.tenant_id == tenant_id)

    result = await session.execute(query)
    rows = result.all()

    # Group by standard
    by_standard = {}
    for soa, req, std in rows:
        std_key = f"{std.name} {std.version}"
        if std_key not in by_standard:
            by_standard[std_key] = {
                "standard_id": std.id,
                "standard_name": std.name,
                "standard_version": std.version,
                "requirements": [],
                "stats": {
                    "total": 0,
                    "implemented": 0,
                    "in_progress": 0,
                    "not_started": 0,
                }
            }

        by_standard[std_key]["requirements"].append({
            "soa_id": soa.id,
            "requirement_code": req.code,
            "requirement_title": req.title,
            "is_applicable": soa.is_applicable,
            "coverage_type": soa.coverage_type.value if soa.coverage_type else None,
            "implementation_status": soa.implementation_status.value if soa.implementation_status else None,
        })

        by_standard[std_key]["stats"]["total"] += 1
        if soa.implementation_status == ImplementationStatus.IMPLEMENTED:
            by_standard[std_key]["stats"]["implemented"] += 1
        elif soa.implementation_status == ImplementationStatus.IN_PROGRESS:
            by_standard[std_key]["stats"]["in_progress"] += 1
        elif soa.implementation_status == ImplementationStatus.NOT_STARTED:
            by_standard[std_key]["stats"]["not_started"] += 1

    return by_standard


# =============================================================================
# REVIEW & SIGN-OFF
# =============================================================================

@router.post("/{soa_id}/review", response_model=ApplicabilityStatement)
async def review_applicability_statement(
    soa_id: int,
    reviewer_id: int = Query(..., description="ID of the reviewing user"),
    notes: Optional[str] = Query(None, description="Review notes"),
    session: AsyncSession = Depends(get_session),
):
    """Mark an applicability statement as reviewed."""
    db_soa = await crud_soa.get_or_404(session, soa_id)

    update_data = {
        "last_reviewed_at": datetime.utcnow(),
        "reviewed_by_id": reviewer_id,
        "updated_at": datetime.utcnow(),
    }

    if notes:
        update_data["implementation_notes"] = (db_soa.implementation_notes or "") + f"\n[Review] {notes}"

    return await crud_soa.update(session, db_obj=db_soa, obj_in=update_data)


@router.post("/scope/{scope_id}/bulk-review")
async def bulk_review_soa(
    scope_id: int,
    reviewer_id: int = Query(..., description="ID of the reviewing user"),
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Mark all applicability statements for a scope as reviewed."""
    await crud_scope.get_or_404(session, scope_id)

    query = (
        select(ApplicabilityStatement)
        .where(ApplicabilityStatement.scope_id == scope_id)
    )
    if tenant_id:
        query = query.where(ApplicabilityStatement.tenant_id == tenant_id)

    result = await session.execute(query)
    statements = result.scalars().all()

    now = datetime.utcnow()
    for soa in statements:
        soa.last_reviewed_at = now
        soa.reviewed_by_id = reviewer_id
        soa.updated_at = now
        session.add(soa)

    await session.commit()

    return {
        "message": f"Reviewed {len(statements)} applicability statements",
        "count": len(statements),
        "reviewed_at": now.isoformat(),
    }
