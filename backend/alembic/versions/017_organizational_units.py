"""Organizational units — sub-tenant hiërarchie (RFC 0002).

Voegt `ims_organizational_units` toe (parent_id self-FK voor boomstructuur)
en `organizational_unit_id` (nullable FK) op `ims_risks`, `ims_controls`,
`ims_assessments` en `ims_grc_scores`. NULL = tenant-niveau,
backward-compatible.

Revision ID: 017
Revises: 016
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Entiteiten die een organizational_unit_id-FK krijgen (nullable, NULL = tenant-niveau).
_ENTITIES_WITH_UNIT_FK = (
    "ims_risks",
    "ims_controls",
    "ims_assessments",
    "ims_grc_scores",
)


def upgrade() -> None:
    op.create_table(
        "ims_organizational_units",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_organizational_units.id"),
            nullable=True,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("code", sa.String(32), nullable=True),
        sa.Column("unit_type", sa.String(32), nullable=False),
        # Vrije lijst — geen DB-enum want gemeente-jargon verschilt.
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id", "code", name="uq_org_unit_code_per_tenant"
        ),
        sa.CheckConstraint("id <> parent_id", name="ck_org_unit_no_self_parent"),
    )
    op.create_index(
        "ix_org_units_tenant_parent",
        "ims_organizational_units",
        ["tenant_id", "parent_id"],
    )

    # RLS — multi-tenant isolatie, conform pattern in migration 002.
    op.execute(
        "ALTER TABLE ims_organizational_units ENABLE ROW LEVEL SECURITY;"
    )
    op.execute("ALTER TABLE ims_organizational_units FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY ims_organizational_units_tenant_isolation
        ON ims_organizational_units
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
        """
    )

    # Nullable FK op kern-entiteiten — NULL = tenant-niveau, backward-compatible.
    for table in _ENTITIES_WITH_UNIT_FK:
        op.add_column(
            table,
            sa.Column(
                "organizational_unit_id",
                UUID(as_uuid=True),
                sa.ForeignKey("ims_organizational_units.id"),
                nullable=True,
            ),
        )
        op.create_index(
            f"ix_{table}_organizational_unit_id",
            table,
            ["organizational_unit_id"],
        )


def downgrade() -> None:
    for table in _ENTITIES_WITH_UNIT_FK:
        op.drop_index(f"ix_{table}_organizational_unit_id", table_name=table)
        op.drop_column(table, "organizational_unit_id")

    op.execute(
        "DROP POLICY IF EXISTS ims_organizational_units_tenant_isolation "
        "ON ims_organizational_units;"
    )
    op.execute(
        "ALTER TABLE ims_organizational_units DISABLE ROW LEVEL SECURITY;"
    )
    op.drop_index(
        "ix_org_units_tenant_parent", table_name="ims_organizational_units"
    )
    op.drop_table("ims_organizational_units")
