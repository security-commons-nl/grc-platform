"""Extensible attributes — custom_attributes JSONB + ims_custom_field_definitions

Implementeert RFC 0001. Hybride model: kernvelden blijven vast in schema,
tenant-specifieke uitbreidingen via JSONB met JSON-Schema-validatie per
tenant. Workflows blijven code-gedefinieerd.

- Voegt `custom_attributes JSONB DEFAULT '{}'` toe aan ims_risks,
  ims_controls, ims_assessments, ims_findings (GIN-index voor filtering).
- Maakt `ims_custom_field_definitions` aan met RLS-policy en
  uniqueness-constraint per (tenant, entity_type, field_name).

Revision ID: 016
Revises: 015
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CORE_ENTITIES = ("ims_risks", "ims_controls", "ims_assessments", "ims_findings")


def upgrade() -> None:
    # 1. custom_attributes JSONB op vier kern-entiteiten
    for table in CORE_ENTITIES:
        op.add_column(
            table,
            sa.Column(
                "custom_attributes",
                JSONB(),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
        )
        op.create_index(
            f"ix_{table}_custom_attributes_gin",
            table,
            ["custom_attributes"],
            postgresql_using="gin",
            postgresql_ops={"custom_attributes": "jsonb_path_ops"},
        )

    # 2. Tabel voor veld-definities per tenant + entiteit
    op.create_table(
        "ims_custom_field_definitions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("field_name", sa.String(64), nullable=False),
        sa.Column("display_label", sa.Text(), nullable=False),
        sa.Column("help_text", sa.Text(), nullable=True),
        sa.Column("json_schema", JSONB(), nullable=False),
        sa.Column(
            "is_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
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
            "tenant_id",
            "entity_type",
            "field_name",
            name="uq_custom_field_per_tenant_entity",
        ),
    )
    op.create_index(
        "ix_custom_field_definitions_tenant_entity",
        "ims_custom_field_definitions",
        ["tenant_id", "entity_type"],
    )

    # CHECK: entity_type beperkt tot bekende waarden (matcht service-laag)
    op.execute(
        """
        ALTER TABLE ims_custom_field_definitions
        ADD CONSTRAINT ims_custom_field_definitions_entity_type_check
        CHECK (entity_type IN ('risk', 'control', 'assessment', 'finding'));
        """
    )

    # CHECK: field_name moet voldoen aan ^[a-z][a-z0-9_]{0,63}$
    op.execute(
        r"""
        ALTER TABLE ims_custom_field_definitions
        ADD CONSTRAINT ims_custom_field_definitions_field_name_format_check
        CHECK (field_name ~ '^[a-z][a-z0-9_]{0,63}$');
        """
    )

    # RLS — tenant-isolatie conform pattern in migration 002
    op.execute("ALTER TABLE ims_custom_field_definitions ENABLE ROW LEVEL SECURITY;")
    op.execute(
        "ALTER TABLE ims_custom_field_definitions FORCE ROW LEVEL SECURITY;"
    )
    op.execute(
        """
        CREATE POLICY ims_custom_field_definitions_tenant_isolation
        ON ims_custom_field_definitions
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP POLICY IF EXISTS ims_custom_field_definitions_tenant_isolation "
        "ON ims_custom_field_definitions;"
    )
    op.execute(
        "ALTER TABLE ims_custom_field_definitions DISABLE ROW LEVEL SECURITY;"
    )
    op.drop_index(
        "ix_custom_field_definitions_tenant_entity",
        table_name="ims_custom_field_definitions",
    )
    op.drop_table("ims_custom_field_definitions")

    for table in CORE_ENTITIES:
        op.drop_index(f"ix_{table}_custom_attributes_gin", table_name=table)
        op.drop_column(table, "custom_attributes")
