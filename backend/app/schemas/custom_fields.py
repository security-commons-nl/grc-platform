"""Pydantic schemas voor extensible attributes (RFC 0001)."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


EntityType = Literal["risk", "control", "assessment", "finding"]


class CustomFieldDefinitionCreate(BaseModel):
    entity_type: EntityType
    field_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-z][a-z0-9_]{0,63}$",
        description="Snake-case veldnaam; mag niet botsen met core-kolom-namen.",
    )
    display_label: str = Field(..., min_length=1, max_length=200)
    help_text: Optional[str] = None
    json_schema: dict[str, Any] = Field(
        ...,
        description="JSON-Schema fragment, bv. {'type': 'string', 'maxLength': 64}.",
    )
    is_required: bool = False
    display_order: int = 0


class CustomFieldDefinitionUpdate(BaseModel):
    display_label: Optional[str] = Field(None, min_length=1, max_length=200)
    help_text: Optional[str] = None
    json_schema: Optional[dict[str, Any]] = None
    is_required: Optional[bool] = None
    display_order: Optional[int] = None


class CustomFieldDefinitionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    entity_type: EntityType
    field_name: str
    display_label: str
    help_text: Optional[str]
    json_schema: dict[str, Any]
    is_required: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
