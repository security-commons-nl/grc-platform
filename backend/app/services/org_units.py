"""Service-functies voor organisatie-eenheden (RFC 0002).

- `descendants(db, tenant_id, unit_id)`: recursive CTE-walk; retourneert
  inclusief de unit zelf, of een lege lijst als de unit niet bestaat in
  deze tenant.
- `validate_unit_in_tenant(db, tenant_id, unit_id)`: verifieert dat de unit
  binnen de tenant valt — voorkomt cross-tenant FK-lekken via
  gemanipuleerde IDs in payloads.
- `depth_of(db, tenant_id, unit_id)` / `descendant_ids_with_depth`: helpers
  voor depth-check (max diepte 6) en cycle-prevention bij PATCH.
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core_models import IMSOrganizationalUnit
from sqlalchemy import select


MAX_DEPTH = 6


async def validate_unit_in_tenant(
    db: AsyncSession, tenant_id: UUID, unit_id: UUID
) -> IMSOrganizationalUnit | None:
    """Returnt de unit als hij binnen de tenant bestaat, anders None."""
    result = await db.execute(
        select(IMSOrganizationalUnit).where(
            IMSOrganizationalUnit.id == unit_id,
            IMSOrganizationalUnit.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def descendants(
    db: AsyncSession, tenant_id: UUID, unit_id: UUID
) -> list[UUID]:
    """Geef alle descendant-ids (inclusief unit_id zelf) terug.

    Lege lijst als de unit niet bestaat in deze tenant.
    """
    sql = text(
        """
        WITH RECURSIVE tree AS (
            SELECT id
              FROM ims_organizational_units
             WHERE id = :unit_id
               AND tenant_id = :tenant_id
            UNION ALL
            SELECT u.id
              FROM ims_organizational_units u
              JOIN tree t ON u.parent_id = t.id
             WHERE u.tenant_id = :tenant_id
        )
        SELECT id FROM tree;
        """
    )
    result = await db.execute(sql, {"unit_id": str(unit_id), "tenant_id": str(tenant_id)})
    return [row[0] for row in result.fetchall()]


async def depth_of(
    db: AsyncSession, tenant_id: UUID, unit_id: UUID | None
) -> int:
    """Diepte van de unit, met de tenant-root op 0.

    Lege parent_id → 1. Een unit met grandparent → 3. Etc.
    Returns 0 als unit_id None is (parent = tenant-root).
    """
    if unit_id is None:
        return 0
    sql = text(
        """
        WITH RECURSIVE chain AS (
            SELECT id, parent_id, 1 AS depth
              FROM ims_organizational_units
             WHERE id = :unit_id AND tenant_id = :tenant_id
            UNION ALL
            SELECT u.id, u.parent_id, c.depth + 1
              FROM ims_organizational_units u
              JOIN chain c ON c.parent_id = u.id
             WHERE u.tenant_id = :tenant_id
        )
        SELECT MAX(depth) FROM chain;
        """
    )
    result = await db.execute(
        sql, {"unit_id": str(unit_id), "tenant_id": str(tenant_id)}
    )
    row = result.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


async def would_create_cycle(
    db: AsyncSession,
    tenant_id: UUID,
    unit_id: UUID,
    new_parent_id: UUID,
) -> bool:
    """True als nieuwe parent een descendant van unit_id is (cyclus)."""
    if unit_id == new_parent_id:
        return True
    descendant_ids = await descendants(db, tenant_id, unit_id)
    return new_parent_id in descendant_ids
