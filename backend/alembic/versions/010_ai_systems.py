"""AI-systemenregister (M4 — AI Governance)

Eerste bouwsteen van de AI Governance Module: catalogus van AI-toepassingen
per organisatie, met EU AI Act-risicoclassificatie en NIST AI RMF-status.

Revision ID: 010
Revises: 009
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ims_ai_systems",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("vendor", sa.String(200), nullable=True),
        sa.Column("system_type", sa.String(30), nullable=False, server_default="other"),
        sa.Column("eu_ai_act_risk", sa.String(20), nullable=False, server_default="not_classified"),
        sa.Column("nist_ai_rmf_status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("deployment_status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("responsible_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_ims_ai_systems_tenant_id", "ims_ai_systems", ["tenant_id"])
    op.create_index("ix_ims_ai_systems_eu_ai_act_risk", "ims_ai_systems", ["eu_ai_act_risk"])
    op.create_index("ix_ims_ai_systems_deployment_status", "ims_ai_systems", ["deployment_status"])

    # CHECK-constraints op enum-achtige velden — voorkomen vrije-tekstwaarden
    op.execute("""
        ALTER TABLE ims_ai_systems ADD CONSTRAINT ims_ai_systems_system_type_check
        CHECK (system_type IN (
            'chatbot', 'decision_support', 'content_generation',
            'classification', 'monitoring', 'automation', 'other'
        ));
    """)
    op.execute("""
        ALTER TABLE ims_ai_systems ADD CONSTRAINT ims_ai_systems_eu_ai_act_risk_check
        CHECK (eu_ai_act_risk IN (
            'unacceptable', 'high', 'limited', 'minimal', 'not_classified'
        ));
    """)
    op.execute("""
        ALTER TABLE ims_ai_systems ADD CONSTRAINT ims_ai_systems_nist_rmf_status_check
        CHECK (nist_ai_rmf_status IN (
            'govern', 'map', 'measure', 'manage', 'not_started'
        ));
    """)
    op.execute("""
        ALTER TABLE ims_ai_systems ADD CONSTRAINT ims_ai_systems_deployment_status_check
        CHECK (deployment_status IN (
            'planned', 'building', 'deployed', 'retired'
        ));
    """)

    # RLS — multi-tenant isolatie, conform pattern in migration 002
    op.execute("ALTER TABLE ims_ai_systems ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ims_ai_systems FORCE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY ims_ai_systems_tenant_isolation ON ims_ai_systems
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS ims_ai_systems_tenant_isolation ON ims_ai_systems;")
    op.execute("ALTER TABLE ims_ai_systems DISABLE ROW LEVEL SECURITY;")
    op.drop_index("ix_ims_ai_systems_deployment_status", table_name="ims_ai_systems")
    op.drop_index("ix_ims_ai_systems_eu_ai_act_risk", table_name="ims_ai_systems")
    op.drop_index("ix_ims_ai_systems_tenant_id", table_name="ims_ai_systems")
    op.drop_table("ims_ai_systems")
