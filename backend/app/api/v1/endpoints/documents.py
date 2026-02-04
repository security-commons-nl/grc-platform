"""
Document Management Endpoints
Handles Documents with versioning and approval workflows.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Document,
    Status,
    VerificationStatus,
)

router = APIRouter()
crud_document = CRUDBase(Document)


# =============================================================================
# DOCUMENT CRUD
# =============================================================================

@router.get("/", response_model=List[Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None),
    scope_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    status: Optional[Status] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List documents with optional filters."""
    query = select(Document)

    if tenant_id:
        query = query.where(Document.tenant_id == tenant_id)
    if scope_id:
        query = query.where(Document.scope_id == scope_id)
    if document_type:
        query = query.where(Document.document_type == document_type)
    if status:
        query = query.where(Document.status == status)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=Document)
async def create_document(
    document: Document,
    session: AsyncSession = Depends(get_session),
):
    """Create a new document."""
    document.version = 1
    document.status = Status.DRAFT
    return await crud_document.create(session, obj_in=document)


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a document by ID."""
    return await crud_document.get_or_404(session, document_id)


@router.patch("/{document_id}", response_model=Document)
async def update_document(
    document_id: int,
    document_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a document."""
    db_document = await crud_document.get_or_404(session, document_id)

    # Only allow content updates in draft status
    if db_document.status != Status.DRAFT:
        content_fields = ["title", "content", "file_path"]
        for field in content_fields:
            if field in document_update:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot update {field} when document is not in Draft status"
                )

    document_update["updated_at"] = datetime.utcnow()
    return await crud_document.update(session, db_obj=db_document, obj_in=document_update)


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a document (only drafts)."""
    db_document = await crud_document.get_or_404(session, document_id)

    if db_document.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft documents can be deleted"
        )

    deleted = await crud_document.delete(session, id=document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}


# =============================================================================
# DOCUMENT LIFECYCLE
# =============================================================================

@router.post("/{document_id}/submit-for-review", response_model=Document)
async def submit_for_review(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Submit a document for review."""
    db_document = await crud_document.get_or_404(session, document_id)

    if db_document.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft documents can be submitted for review"
        )

    return await crud_document.update(session, db_obj=db_document, obj_in={
        "verification_status": VerificationStatus.PENDING_APPROVAL,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{document_id}/approve", response_model=Document)
async def approve_document(
    document_id: int,
    approved_by_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Approve a document."""
    db_document = await crud_document.get_or_404(session, document_id)

    if db_document.verification_status != VerificationStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail="Document must be pending approval"
        )

    return await crud_document.update(session, db_obj=db_document, obj_in={
        "status": Status.ACTIVE,
        "verification_status": VerificationStatus.VERIFIED,
        "approved_by_id": approved_by_id,
        "approved_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })


@router.post("/{document_id}/reject", response_model=Document)
async def reject_document(
    document_id: int,
    rejection_reason: str,
    session: AsyncSession = Depends(get_session),
):
    """Reject a document, returns to draft."""
    db_document = await crud_document.get_or_404(session, document_id)

    if db_document.verification_status != VerificationStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail="Document must be pending approval"
        )

    return await crud_document.update(session, db_obj=db_document, obj_in={
        "verification_status": VerificationStatus.REJECTED,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{document_id}/archive", response_model=Document)
async def archive_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Archive a document."""
    db_document = await crud_document.get_or_404(session, document_id)

    return await crud_document.update(session, db_obj=db_document, obj_in={
        "status": Status.DEPRECATED,
        "updated_at": datetime.utcnow(),
    })


# =============================================================================
# DOCUMENT VERSIONING
# =============================================================================

@router.post("/{document_id}/new-version", response_model=Document)
async def create_new_version(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Create a new version of a document."""
    db_document = await crud_document.get_or_404(session, document_id)

    if db_document.status != Status.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Can only create new versions from active documents"
        )

    # Create new version
    new_document = Document(
        tenant_id=db_document.tenant_id,
        scope_id=db_document.scope_id,
        title=db_document.title,
        content=db_document.content,
        document_type=db_document.document_type,
        file_path=db_document.file_path,
        version=db_document.version + 1,
        status=Status.DRAFT,
        verification_status=VerificationStatus.UNVERIFIED,
        created_by_id=db_document.created_by_id,
    )

    return await crud_document.create(session, obj_in=new_document)


@router.get("/{document_id}/versions", response_model=List[Document])
async def get_document_versions(
    document_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all versions of a document (by matching title and tenant)."""
    db_document = await crud_document.get_or_404(session, document_id)

    result = await session.execute(
        select(Document).where(
            Document.tenant_id == db_document.tenant_id,
            Document.title == db_document.title,
        ).order_by(Document.version.desc())
    )
    return result.scalars().all()


# =============================================================================
# DOCUMENT REVIEW
# =============================================================================

@router.get("/due-for-review", response_model=List[Document])
async def get_documents_due_for_review(
    tenant_id: Optional[int] = None,
    days_ahead: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Get documents due for review within specified days."""
    from datetime import timedelta

    deadline = datetime.utcnow() + timedelta(days=days_ahead)

    query = select(Document).where(
        Document.status == Status.ACTIVE,
        Document.review_date != None,
        Document.review_date <= deadline,
    )

    if tenant_id:
        query = query.where(Document.tenant_id == tenant_id)

    result = await session.execute(query)
    return result.scalars().all()


@router.patch("/{document_id}/set-review-date", response_model=Document)
async def set_review_date(
    document_id: int,
    review_date: datetime,
    session: AsyncSession = Depends(get_session),
):
    """Set or update the review date for a document."""
    db_document = await crud_document.get_or_404(session, document_id)

    return await crud_document.update(session, db_obj=db_document, obj_in={
        "review_date": review_date,
        "updated_at": datetime.utcnow(),
    })
