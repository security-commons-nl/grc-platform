"""Validator-service voor extensible attributes (RFC 0001).

Functies:
- `validate_custom_attributes`: bouwt een compound JSON-Schema uit de actieve
  veld-definities per (tenant, entity_type) en valideert de payload daartegen.
- `is_reserved_field_name`: weigert veldnamen die botsen met core-schema
  kolommen van de doel-entiteit.

Errors worden geraised als HTTPException (422) zodat endpoints geen
extra translation hoeven te doen.
"""

from typing import Iterable
from uuid import UUID

from fastapi import HTTPException
from jsonschema import Draft202012Validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core_models import (
    IMSAssessment,
    IMSControl,
    IMSCustomFieldDefinition,
    IMSFinding,
    IMSRisk,
)


# Aliases die we naar buiten brengen — mapping naar SQLAlchemy-modellen voor
# de reserved-namespace-check.
ENTITY_TYPES = ("risk", "control", "assessment", "finding")

_ENTITY_MODEL = {
    "risk": IMSRisk,
    "control": IMSControl,
    "assessment": IMSAssessment,
    "finding": IMSFinding,
}


def _reserved_field_names(entity_type: str) -> set[str]:
    """Alle kolomnamen die het core-schema al gebruikt voor deze entiteit."""
    model = _ENTITY_MODEL[entity_type]
    return {col.name for col in model.__table__.columns}


def is_reserved_field_name(entity_type: str, field_name: str) -> bool:
    """True als `field_name` botst met een bestaande core-kolom."""
    if entity_type not in _ENTITY_MODEL:
        raise ValueError(f"Unknown entity_type: {entity_type}")
    return field_name in _reserved_field_names(entity_type)


async def _load_definitions(
    db: AsyncSession,
    tenant_id: UUID,
    entity_type: str,
) -> list[IMSCustomFieldDefinition]:
    if entity_type not in _ENTITY_MODEL:
        raise ValueError(f"Unknown entity_type: {entity_type}")

    result = await db.execute(
        select(IMSCustomFieldDefinition).where(
            IMSCustomFieldDefinition.tenant_id == tenant_id,
            IMSCustomFieldDefinition.entity_type == entity_type,
        )
    )
    return list(result.scalars().all())


def _compound_schema(definitions: Iterable[IMSCustomFieldDefinition]) -> dict:
    """Combineert per-veld JSON-Schemas tot één object-schema."""
    defs = list(definitions)
    return {
        "type": "object",
        "properties": {d.field_name: d.json_schema for d in defs},
        "required": [d.field_name for d in defs if d.is_required],
        # Sluit onbekende velden uit — anders sluip onverwerkte data binnen
        # waar standaardrapportages niets van weten.
        "additionalProperties": False,
    }


async def validate_custom_attributes(
    db: AsyncSession,
    tenant_id: UUID,
    entity_type: str,
    attributes: dict | None,
) -> None:
    """Valideer `attributes` tegen de actieve veld-definities.

    None of {} → mag mits er geen verplichte velden zijn. Bij error raised
    HTTPException(422) met een lijst per veld.
    """
    if entity_type not in _ENTITY_MODEL:
        raise ValueError(f"Unknown entity_type: {entity_type}")

    defs = await _load_definitions(db, tenant_id, entity_type)
    if not defs:
        # Geen definities → alleen `{}` of leeg toegestaan.
        if attributes:
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["custom_attributes"],
                        "msg": (
                            "Tenant heeft geen custom-veld-definities; "
                            "custom_attributes moet leeg zijn."
                        ),
                        "type": "value_error.no_definitions",
                    }
                ],
            )
        return

    schema = _compound_schema(defs)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(attributes or {}), key=lambda e: list(e.absolute_path))
    if errors:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["custom_attributes"] + list(err.absolute_path),
                    "msg": err.message,
                    "type": "value_error.json_schema",
                }
                for err in errors
            ],
        )
