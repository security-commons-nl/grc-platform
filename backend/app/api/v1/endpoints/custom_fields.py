"""CRUD voor tenant-specifieke veld-definities (RFC 0001).

Beheert `ims_custom_field_definitions`. Reserved-namespace-check zorgt dat
veldnamen niet botsen met core-schema-kolommen. JSON-Schema-validatie van
het definitie-fragment is licht: we accepteren elk geldig JSON-object
(de runtime-validatie volgt bij entity-writes).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSCustomFieldDefinition
from app.schemas.custom_fields import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionResponse,
    CustomFieldDefinitionUpdate,
    EntityType,
)
from app.services.custom_fields import is_reserved_field_name

router = APIRouter()


@router.get("/", response_model=list[CustomFieldDefinitionResponse])
async def list_custom_fields(
    entity_type: EntityType | None = Query(
        None, description="Filter op entiteit (risk | control | assessment | finding)."
    ),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSCustomFieldDefinition).where(
        IMSCustomFieldDefinition.tenant_id == current_user.tenant_id
    )
    if entity_type:
        query = query.where(IMSCustomFieldDefinition.entity_type == entity_type)
    query = query.order_by(
        IMSCustomFieldDefinition.entity_type,
        IMSCustomFieldDefinition.display_order,
        IMSCustomFieldDefinition.field_name,
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=CustomFieldDefinitionResponse,
    status_code=201,
)
async def create_custom_field(
    data: CustomFieldDefinitionCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    # Reserved-namespace check tegen core-kolommen van de doel-entiteit
    if is_reserved_field_name(data.entity_type, data.field_name):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Veldnaam '{data.field_name}' conflicteert met een kernveld "
                f"van entiteit '{data.entity_type}'."
            ),
        )

    # Uniqueness per (tenant, entity_type, field_name)
    existing = await db.execute(
        select(IMSCustomFieldDefinition).where(
            IMSCustomFieldDefinition.tenant_id == current_user.tenant_id,
            IMSCustomFieldDefinition.entity_type == data.entity_type,
            IMSCustomFieldDefinition.field_name == data.field_name,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Definitie voor '{data.entity_type}.{data.field_name}' bestaat "
                "al voor deze tenant."
            ),
        )

    definition = IMSCustomFieldDefinition(
        tenant_id=current_user.tenant_id,
        **data.model_dump(),
    )
    db.add(definition)
    await db.flush()
    await db.refresh(definition)
    return definition


@router.get("/{definition_id}", response_model=CustomFieldDefinitionResponse)
async def get_custom_field(
    definition_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCustomFieldDefinition).where(
            IMSCustomFieldDefinition.id == definition_id,
            IMSCustomFieldDefinition.tenant_id == current_user.tenant_id,
        )
    )
    definition = result.scalar_one_or_none()
    if not definition:
        raise HTTPException(status_code=404, detail="Veld-definitie niet gevonden")
    return definition


@router.patch(
    "/{definition_id}",
    response_model=CustomFieldDefinitionResponse,
)
async def update_custom_field(
    definition_id: UUID,
    data: CustomFieldDefinitionUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCustomFieldDefinition).where(
            IMSCustomFieldDefinition.id == definition_id,
            IMSCustomFieldDefinition.tenant_id == current_user.tenant_id,
        )
    )
    definition = result.scalar_one_or_none()
    if not definition:
        raise HTTPException(status_code=404, detail="Veld-definitie niet gevonden")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(definition, field, value)

    await db.flush()
    await db.refresh(definition)
    return definition


@router.delete("/{definition_id}", status_code=204)
async def delete_custom_field(
    definition_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCustomFieldDefinition).where(
            IMSCustomFieldDefinition.id == definition_id,
            IMSCustomFieldDefinition.tenant_id == current_user.tenant_id,
        )
    )
    definition = result.scalar_one_or_none()
    if not definition:
        raise HTTPException(status_code=404, detail="Veld-definitie niet gevonden")
    await db.delete(definition)
    await db.flush()
    return None
