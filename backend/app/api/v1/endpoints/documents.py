from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import (
    IMSDocument, IMSDocumentVersion, IMSStepInputDocument, IMSGapAnalysisResult,
)
from app.schemas.documents import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentVersionCreate, DocumentVersionResponse,
    StepInputDocumentCreate, StepInputDocumentUpdate, StepInputDocumentResponse,
    GapAnalysisResultCreate, GapAnalysisResultValidate, GapAnalysisResultResponse,
)

router = APIRouter()


# ── Documents ──────────────────────────────────────────────────────────────


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    document_type: str | None = None,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSDocument).where(IMSDocument.tenant_id == current_user.tenant_id)
    if document_type:
        query = query.where(IMSDocument.document_type == document_type)
    if domain:
        query = query.where(IMSDocument.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSDocument).where(IMSDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    doc = IMSDocument(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSDocument).where(IMSDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSDocument).where(IMSDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.flush()


# ── Document Versions (immutable — POST and GET only) ──────────────────────


@router.get("/versions/", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(IMSDocumentVersion)
        .where(IMSDocumentVersion.document_id == document_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/versions/{version_id}", response_model=DocumentVersionResponse)
async def get_document_version(
    version_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSDocumentVersion).where(IMSDocumentVersion.id == version_id)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="DocumentVersion not found")
    return version


@router.post("/versions/", response_model=DocumentVersionResponse, status_code=201)
async def create_document_version(
    data: DocumentVersionCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    version = IMSDocumentVersion(**data.model_dump())
    db.add(version)
    await db.flush()
    await db.refresh(version)
    return version


# ── Step Input Documents ───────────────────────────────────────────────────


@router.get("/input-documents/", response_model=list[StepInputDocumentResponse])
async def list_step_input_documents(
    step_execution_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStepInputDocument).where(IMSStepInputDocument.tenant_id == current_user.tenant_id)
    if step_execution_id:
        query = query.where(IMSStepInputDocument.step_execution_id == step_execution_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/input-documents/{input_doc_id}", response_model=StepInputDocumentResponse)
async def get_step_input_document(
    input_doc_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSStepInputDocument).where(IMSStepInputDocument.id == input_doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="StepInputDocument not found")
    return doc


@router.post("/input-documents/", response_model=StepInputDocumentResponse, status_code=201)
async def create_step_input_document(
    data: StepInputDocumentCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    doc = IMSStepInputDocument(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.patch("/input-documents/{input_doc_id}", response_model=StepInputDocumentResponse)
async def update_step_input_document(
    input_doc_id: UUID,
    data: StepInputDocumentUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSStepInputDocument).where(IMSStepInputDocument.id == input_doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="StepInputDocument not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.flush()
    await db.refresh(doc)
    return doc


# ── Gap Analysis Results ───────────────────────────────────────────────────


@router.get("/gap-analysis/", response_model=list[GapAnalysisResultResponse])
async def list_gap_analysis_results(
    input_document_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSGapAnalysisResult).where(IMSGapAnalysisResult.tenant_id == current_user.tenant_id)
    if input_document_id:
        query = query.where(IMSGapAnalysisResult.input_document_id == input_document_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/gap-analysis/{gap_id}", response_model=GapAnalysisResultResponse)
async def get_gap_analysis_result(
    gap_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSGapAnalysisResult).where(IMSGapAnalysisResult.id == gap_id)
    )
    gap = result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="GapAnalysisResult not found")
    return gap


@router.post("/gap-analysis/", response_model=GapAnalysisResultResponse, status_code=201)
async def create_gap_analysis_result(
    data: GapAnalysisResultCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    gap = IMSGapAnalysisResult(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(gap)
    await db.flush()
    await db.refresh(gap)
    return gap


@router.patch("/gap-analysis/{gap_id}", response_model=GapAnalysisResultResponse)
async def validate_gap_analysis_result(
    gap_id: UUID,
    data: GapAnalysisResultValidate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSGapAnalysisResult).where(IMSGapAnalysisResult.id == gap_id)
    )
    gap = result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="GapAnalysisResult not found")

    gap.validated = data.validated
    if data.validated:
        gap.validated_at = datetime.utcnow()
    if data.validated_by_user_id:
        gap.validated_by_user_id = data.validated_by_user_id

    await db.flush()
    await db.refresh(gap)
    return gap
