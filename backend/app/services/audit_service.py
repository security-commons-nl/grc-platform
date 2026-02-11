"""
Audit Service — lightweight helper to write AuditLog entries.
Fire-and-forget: logs warning on failure, never raises.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core_models import AuditLog, AuditAction

logger = logging.getLogger(__name__)


async def record_audit(
    session: AsyncSession,
    *,
    tenant_id: int,
    entity_type: str,
    entity_id: int,
    action: AuditAction,
    changed_by_id: int,
    field_name: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    """
    Write a single row to the AuditLog table.

    Fire-and-forget: catches all exceptions and logs a warning
    so that a broken audit trail never blocks the business operation.
    """
    try:
        entry = AuditLog(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changed_by_id=changed_by_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
        )
        session.add(entry)
        await session.flush()
    except Exception as e:
        logger.warning("Failed to write audit log: %s", e)
