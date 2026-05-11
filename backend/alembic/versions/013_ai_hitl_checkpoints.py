"""AI HITL checkpoints — menselijk toezicht audit-trail (M4)

EU AI Act art. 14 vereist menselijk toezicht op hoog-risico AI-systemen.
Deze tabel legt elke menselijke review-beslissing op een AI-uitvoer
vast: goedkeuring, afwijzing of aanpassing. Append-only.

Revision ID: 013
Revises: 012
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_hitl_checkpoints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("audit_log_id", UUID(as_uuid=True), sa.ForeignKey("ai_audit_logs.id"), nullable=False),
        sa.Column("reviewer_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_ai_hitl_checkpoints_tenant_id", "ai_hitl_checkpoints", ["tenant_id"])
    op.create_index("ix_ai_hitl_checkpoints_audit_log_id", "ai_hitl_checkpoints", ["audit_log_id"])

    op.execute("""
        ALTER TABLE ai_hitl_checkpoints ADD CONSTRAINT ai_hitl_checkpoints_decision_check
        CHECK (decision IN ('approved', 'rejected', 'modified', 'pending'));
    """)

    # RLS — tenant isolation conform pattern in migration 002
    op.execute("ALTER TABLE ai_hitl_checkpoints ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ai_hitl_checkpoints FORCE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY ai_hitl_checkpoints_tenant_isolation ON ai_hitl_checkpoints
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
    """)

    # Append-only: drop UPDATE en DELETE rechten zodra de tabel bestaat.
    # Inserts blijven toegestaan; de tabel is daarmee een echte audit-trail
    # die niet achteraf kan worden gemanipuleerd.
    op.execute("REVOKE UPDATE, DELETE ON ai_hitl_checkpoints FROM ims_app;")


def downgrade() -> None:
    op.execute("GRANT UPDATE, DELETE ON ai_hitl_checkpoints TO ims_app;")
    op.execute("DROP POLICY IF EXISTS ai_hitl_checkpoints_tenant_isolation ON ai_hitl_checkpoints;")
    op.execute("ALTER TABLE ai_hitl_checkpoints DISABLE ROW LEVEL SECURITY;")
    op.drop_index("ix_ai_hitl_checkpoints_audit_log_id", table_name="ai_hitl_checkpoints")
    op.drop_index("ix_ai_hitl_checkpoints_tenant_id", table_name="ai_hitl_checkpoints")
    op.drop_table("ai_hitl_checkpoints")
