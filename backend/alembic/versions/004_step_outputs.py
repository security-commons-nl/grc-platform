"""Add step output definitions and fulfillment tracking

Revision ID: 004
Revises: 003
Create Date: 2026-03-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # ims_step_outputs — global reference data (no tenant_id)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_step_outputs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "step_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_steps.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("output_type", sa.String(20), nullable=False),
        sa.Column("requirement", sa.String(1), nullable=False, server_default="V"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_step_outputs_step_id", "ims_step_outputs", ["step_id"])

    # ------------------------------------------------------------------
    # ims_step_output_fulfillments — tenant-scoped
    # ------------------------------------------------------------------
    op.create_table(
        "ims_step_output_fulfillments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "step_output_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_step_outputs.id"),
            nullable=False,
        ),
        sa.Column(
            "step_execution_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_step_executions.id"),
            nullable=False,
        ),
        sa.Column(
            "decision_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_decisions.id"),
            nullable=True,
        ),
        sa.Column(
            "document_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_documents.id"),
            nullable=True,
        ),
        sa.Column(
            "fulfilled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("fulfilled_by", sa.String(200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "(CASE WHEN decision_id IS NOT NULL THEN 1 ELSE 0 END"
            " + CASE WHEN document_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_fulfillment_one_link",
        ),
        sa.UniqueConstraint(
            "step_output_id",
            "step_execution_id",
            name="uq_fulfillment_output_execution",
        ),
    )
    op.create_index(
        "ix_fulfillments_execution_id",
        "ims_step_output_fulfillments",
        ["step_execution_id"],
    )
    op.create_index(
        "ix_fulfillments_output_id",
        "ims_step_output_fulfillments",
        ["step_output_id"],
    )

    # ------------------------------------------------------------------
    # RLS on fulfillments (same pattern as 002)
    # ------------------------------------------------------------------
    op.execute(
        "ALTER TABLE ims_step_output_fulfillments ENABLE ROW LEVEL SECURITY;"
    )
    op.execute(
        "ALTER TABLE ims_step_output_fulfillments FORCE ROW LEVEL SECURITY;"
    )
    op.execute("""
        CREATE POLICY ims_step_output_fulfillments_tenant_isolation
            ON ims_step_output_fulfillments
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
    """)

    # Grant permissions to ims_app role
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ims_step_outputs TO ims_app;"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ims_step_output_fulfillments TO ims_app;"
    )


def downgrade() -> None:
    op.execute(
        "DROP POLICY IF EXISTS ims_step_output_fulfillments_tenant_isolation "
        "ON ims_step_output_fulfillments;"
    )
    op.execute(
        "ALTER TABLE ims_step_output_fulfillments DISABLE ROW LEVEL SECURITY;"
    )
    op.drop_table("ims_step_output_fulfillments")
    op.drop_table("ims_step_outputs")
