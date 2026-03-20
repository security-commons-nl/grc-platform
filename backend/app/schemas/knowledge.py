from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class KnowledgeChunkCreate(BaseModel):
    layer: str
    tenant_id: Optional[UUID] = None
    source_type: str
    source_id: Optional[UUID] = None
    chunk_index: int
    content: str
    model_used: str


class KnowledgeChunkUpdate(BaseModel):
    content: Optional[str] = None
    model_used: Optional[str] = None


class KnowledgeChunkResponse(BaseModel):
    id: UUID
    layer: str
    tenant_id: Optional[UUID]
    source_type: str
    source_id: Optional[UUID]
    chunk_index: int
    content: str
    model_used: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
