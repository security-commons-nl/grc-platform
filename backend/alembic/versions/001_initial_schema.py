"""Initial schema — all IMS v1 tables.

Revision ID: 001
Revises: None
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # pgvector extension
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------
    # regions  (no FK deps except self-ref to tenants added later)
    # ------------------------------------------------------------------
    op.create_table(
        "regions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("centrum_tenant_id", UUID(as_uuid=True), nullable=True),
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

    # ------------------------------------------------------------------
    # tenants  (FK to regions)
    # ------------------------------------------------------------------
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("region_id", UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
    )

    # ------------------------------------------------------------------
    # users  (FK to tenants)
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # user_tenant_roles
    # ------------------------------------------------------------------
    op.create_table(
        "user_tenant_roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("domain", sa.String(10), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # user_region_roles
    # ------------------------------------------------------------------
    op.create_table(
        "user_region_roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("region_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
    )

    # ------------------------------------------------------------------
    # ims_steps
    # ------------------------------------------------------------------
    op.create_table(
        "ims_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("number", sa.String(10), nullable=False),
        sa.Column("phase", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("waarom_nu", sa.Text(), nullable=False),
        sa.Column("required_gremium", sa.String(50), nullable=False),
        sa.Column("is_optional", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("domain", sa.String(10), nullable=True),
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

    # ------------------------------------------------------------------
    # ims_step_executions  (FK: tenants, ims_steps)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_step_executions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("step_id", UUID(as_uuid=True), nullable=False),
        sa.Column("cyclus_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("skipped", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("skip_reason", sa.Text(), nullable=True),
        sa.Column("skip_logged_by", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["step_id"], ["ims_steps.id"]),
    )

    # ------------------------------------------------------------------
    # ai_audit_logs  (FK: tenants, users, ims_step_executions)
    # ------------------------------------------------------------------
    op.create_table(
        "ai_audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("agent_name", sa.Text(), nullable=False),
        sa.Column("step_execution_id", UUID(as_uuid=True), nullable=True),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "completion_tokens", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("langfuse_trace_id", sa.Text(), nullable=True),
        sa.Column("feedback", sa.String(20), nullable=True),
        sa.Column("feedback_comment", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["step_execution_id"], ["ims_step_executions.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_decisions  (FK: tenants, ims_step_executions; self-ref added after)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.String(10), nullable=False),
        sa.Column("step_execution_id", UUID(as_uuid=True), nullable=True),
        sa.Column("decision_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("grondslag", sa.Text(), nullable=False),
        sa.Column("gremium", sa.String(50), nullable=False),
        sa.Column("decided_by_name", sa.String(200), nullable=False),
        sa.Column("decided_by_role", sa.String(200), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.Text(), nullable=True),
        sa.Column("motivation", sa.Text(), nullable=True),
        sa.Column("alternatives", sa.Text(), nullable=True),
        sa.Column("iso_clause", sa.String(20), nullable=True),
        sa.Column("supersedes_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(
            ["step_execution_id"], ["ims_step_executions.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_documents  (FK: tenants, ims_step_executions)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("step_execution_id", UUID(as_uuid=True), nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(10), nullable=True),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(
            ["step_execution_id"], ["ims_step_executions.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_document_versions  (FK: ims_documents, users, ims_decisions)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_document_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.String(20), nullable=False),
        sa.Column("content_json", JSONB(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("generated_by_agent", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("vastgesteld_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vastgesteld_by_name", sa.String(200), nullable=True),
        sa.Column("vastgesteld_by_role", sa.String(200), nullable=True),
        sa.Column("decision_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["document_id"], ["ims_documents.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["decision_id"], ["ims_decisions.id"]),
    )

    # ------------------------------------------------------------------
    # ims_step_input_documents  (FK: tenants, ims_step_executions, users)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_step_input_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("step_execution_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uploaded_by_user_id", UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(
            ["step_execution_id"], ["ims_step_executions.id"]
        ),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_gap_analysis_results  (FK: ims_step_input_documents, tenants, users)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_gap_analysis_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("input_document_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("field_reference", sa.Text(), nullable=False),
        sa.Column("ai_suggestion", sa.Text(), nullable=False),
        sa.Column(
            "uncertainty", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "validated", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_by_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["input_document_id"], ["ims_step_input_documents.id"]
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["validated_by_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_step_dependencies  (FK: ims_steps x2)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_step_dependencies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("step_id", UUID(as_uuid=True), nullable=False),
        sa.Column("depends_on_step_id", UUID(as_uuid=True), nullable=False),
        sa.Column("dependency_type", sa.String(1), nullable=False),
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
        sa.ForeignKeyConstraint(["step_id"], ["ims_steps.id"]),
        sa.ForeignKeyConstraint(["depends_on_step_id"], ["ims_steps.id"]),
    )

    # ------------------------------------------------------------------
    # ims_standards  (self-ref FK added after)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_standards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("published_at", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("superseded_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("domain", sa.String(10), nullable=False),
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

    # ------------------------------------------------------------------
    # ims_requirements  (FK: ims_standards)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_requirements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("standard_id", UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column(
            "is_mandatory", sa.Boolean(), nullable=False, server_default="true"
        ),
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
        sa.ForeignKeyConstraint(["standard_id"], ["ims_standards.id"]),
    )

    # ------------------------------------------------------------------
    # ims_requirement_mappings  (FK: ims_requirements x2)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_requirement_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_requirement_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_requirement_id", UUID(as_uuid=True), nullable=False),
        sa.Column("norm_version_source", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("created_by", sa.String(10), nullable=False),
        sa.Column(
            "verified", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "orphaned", sa.Boolean(), nullable=False, server_default="false"
        ),
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
        sa.ForeignKeyConstraint(
            ["source_requirement_id"], ["ims_requirements.id"]
        ),
        sa.ForeignKeyConstraint(
            ["target_requirement_id"], ["ims_requirements.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_tenant_normenkader  (FK: tenants, ims_standards, ims_decisions)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_tenant_normenkader",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("standard_id", UUID(as_uuid=True), nullable=False),
        sa.Column("adopted_at", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("decision_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["standard_id"], ["ims_standards.id"]),
        sa.ForeignKeyConstraint(["decision_id"], ["ims_decisions.id"]),
    )

    # ------------------------------------------------------------------
    # ims_standard_ingestions  (FK: tenants, users, ims_standards)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_standard_ingestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by_user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(10), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("detected_standard_id", UUID(as_uuid=True), nullable=True),
        sa.Column("detected_version", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("parsed_requirements_json", JSONB(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["detected_standard_id"], ["ims_standards.id"]
        ),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_scopes  (FK: tenants; self-ref)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_scopes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), nullable=True),
        sa.Column("domain", sa.String(10), nullable=True),
        sa.Column(
            "is_critical", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "verwerkt_pii", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("ext_verwerking_ref", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["ims_scopes.id"]),
    )

    # ------------------------------------------------------------------
    # ims_risks  (FK: tenants, ims_scopes, users, ims_decisions)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_risks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("likelihood", sa.Integer(), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("financial_impact_eur", sa.Numeric(15, 2), nullable=True),
        sa.Column("risk_level", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("owner_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("cyclus_id", sa.Integer(), nullable=True),
        sa.Column("treatment_decision_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["scope_id"], ["ims_scopes.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["treatment_decision_id"], ["ims_decisions.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_controls  (FK: tenants, ims_requirements, users)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_controls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("requirement_id", UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column("owner_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("implementation_status", sa.String(20), nullable=False),
        sa.Column("implementation_date", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["requirement_id"], ["ims_requirements.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_risk_control_links  (composite PK, no id, no timestamps)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_risk_control_links",
        sa.Column("risk_id", UUID(as_uuid=True), nullable=False),
        sa.Column("control_id", UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("risk_id", "control_id"),
        sa.ForeignKeyConstraint(["risk_id"], ["ims_risks.id"]),
        sa.ForeignKeyConstraint(["control_id"], ["ims_controls.id"]),
    )

    # ------------------------------------------------------------------
    # ims_assessments  (FK: tenants, ims_scopes, ims_documents)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("assessment_type", sa.String(30), nullable=False),
        sa.Column("scope_id", UUID(as_uuid=True), nullable=True),
        sa.Column("domain", sa.String(10), nullable=True),
        sa.Column("planned_at", sa.Date(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("cyclus_id", sa.Integer(), nullable=True),
        sa.Column("document_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["scope_id"], ["ims_scopes.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["ims_documents.id"]),
    )

    # ------------------------------------------------------------------
    # ims_findings  (FK: ims_assessments, tenants, ims_requirements)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_findings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("requirement_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["assessment_id"], ["ims_assessments.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["requirement_id"], ["ims_requirements.id"]),
    )

    # ------------------------------------------------------------------
    # ims_corrective_actions  (FK: tenants, ims_findings, ims_risks, users)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_corrective_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("finding_id", UUID(as_uuid=True), nullable=True),
        sa.Column("risk_id", UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["finding_id"], ["ims_findings.id"]),
        sa.ForeignKeyConstraint(["risk_id"], ["ims_risks.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_evidence  (FK: tenants, ims_controls, users)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_evidence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("control_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("evidence_type", sa.String(20), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("collected_at", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("collected_by_user_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["control_id"], ["ims_controls.id"]),
        sa.ForeignKeyConstraint(["collected_by_user_id"], ["users.id"]),
    )

    # ------------------------------------------------------------------
    # ims_incidents  (FK: tenants, ims_corrective_actions)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_incidents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("incident_type", sa.String(30), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_ticket_id", sa.Text(), nullable=True),
        sa.Column("corrective_action_id", UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(
            ["corrective_action_id"], ["ims_corrective_actions.id"]
        ),
    )

    # ------------------------------------------------------------------
    # ims_maturity_profiles  (FK: tenants)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_maturity_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column("existing_registers", sa.String(20), nullable=False),
        sa.Column("existing_analyses", sa.String(20), nullable=False),
        sa.Column("coordination_capacity", sa.String(20), nullable=False),
        sa.Column("linemanagement_structure", sa.String(20), nullable=False),
        sa.Column("recommended_option", sa.String(1), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # ims_setup_scores  (FK: tenants)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_setup_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column("cyclus_year", sa.Integer(), nullable=False),
        sa.Column("score_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("steps_completed", sa.Integer(), nullable=False),
        sa.Column("steps_total", sa.Integer(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # ims_grc_scores  (FK: tenants)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_grc_scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(10), nullable=False),
        sa.Column("cyclus_year", sa.Integer(), nullable=False),
        sa.Column("score_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("components_json", JSONB(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # ims_knowledge_chunks  (FK: tenants nullable)
    # ------------------------------------------------------------------
    op.create_table(
        "ims_knowledge_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("layer", sa.String(20), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("source_id", UUID(as_uuid=True), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("model_used", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    # ------------------------------------------------------------------
    # Deferred self-referential FKs
    # ------------------------------------------------------------------

    # regions.centrum_tenant_id → tenants.id
    op.create_foreign_key(
        "fk_regions_centrum_tenant_id",
        "regions",
        "tenants",
        ["centrum_tenant_id"],
        ["id"],
    )

    # ims_decisions.supersedes_id → ims_decisions.id
    op.create_foreign_key(
        "fk_ims_decisions_supersedes_id",
        "ims_decisions",
        "ims_decisions",
        ["supersedes_id"],
        ["id"],
    )

    # ims_standards.superseded_by_id → ims_standards.id
    op.create_foreign_key(
        "fk_ims_standards_superseded_by_id",
        "ims_standards",
        "ims_standards",
        ["superseded_by_id"],
        ["id"],
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------

    # --- tenant_id indexes (all tables with tenant_id) ---
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index(
        "ix_user_tenant_roles_tenant_id", "user_tenant_roles", ["tenant_id"]
    )
    op.create_index(
        "ix_user_tenant_roles_user_id", "user_tenant_roles", ["user_id"]
    )
    op.create_index(
        "ix_user_region_roles_user_id", "user_region_roles", ["user_id"]
    )
    op.create_index(
        "ix_user_region_roles_region_id", "user_region_roles", ["region_id"]
    )
    op.create_index("ix_ai_audit_logs_tenant_id", "ai_audit_logs", ["tenant_id"])
    op.create_index("ix_ai_audit_logs_user_id", "ai_audit_logs", ["user_id"])
    op.create_index(
        "ix_ai_audit_logs_step_execution_id",
        "ai_audit_logs",
        ["step_execution_id"],
    )
    op.create_index(
        "ix_ims_step_executions_tenant_id",
        "ims_step_executions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_step_executions_step_id", "ims_step_executions", ["step_id"]
    )
    op.create_index(
        "ix_ims_step_executions_status", "ims_step_executions", ["status"]
    )
    op.create_index(
        "ix_ims_decisions_tenant_id", "ims_decisions", ["tenant_id"]
    )
    op.create_index(
        "ix_ims_decisions_step_execution_id",
        "ims_decisions",
        ["step_execution_id"],
    )
    op.create_index(
        "ix_ims_documents_tenant_id", "ims_documents", ["tenant_id"]
    )
    op.create_index(
        "ix_ims_documents_step_execution_id",
        "ims_documents",
        ["step_execution_id"],
    )
    op.create_index(
        "ix_ims_document_versions_document_id",
        "ims_document_versions",
        ["document_id"],
    )
    op.create_index(
        "ix_ims_document_versions_status",
        "ims_document_versions",
        ["status"],
    )
    op.create_index(
        "ix_ims_step_input_documents_tenant_id",
        "ims_step_input_documents",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_step_input_documents_step_execution_id",
        "ims_step_input_documents",
        ["step_execution_id"],
    )
    op.create_index(
        "ix_ims_step_input_documents_status",
        "ims_step_input_documents",
        ["status"],
    )
    op.create_index(
        "ix_ims_gap_analysis_results_tenant_id",
        "ims_gap_analysis_results",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_gap_analysis_results_input_document_id",
        "ims_gap_analysis_results",
        ["input_document_id"],
    )
    op.create_index(
        "ix_ims_step_dependencies_step_id",
        "ims_step_dependencies",
        ["step_id"],
    )
    op.create_index(
        "ix_ims_requirements_standard_id",
        "ims_requirements",
        ["standard_id"],
    )
    op.create_index(
        "ix_ims_requirements_domain", "ims_requirements", ["domain"]
    )
    op.create_index(
        "ix_ims_requirement_mappings_source_requirement_id",
        "ims_requirement_mappings",
        ["source_requirement_id"],
    )
    op.create_index(
        "ix_ims_requirement_mappings_target_requirement_id",
        "ims_requirement_mappings",
        ["target_requirement_id"],
    )
    op.create_index(
        "ix_ims_tenant_normenkader_tenant_id",
        "ims_tenant_normenkader",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_tenant_normenkader_standard_id",
        "ims_tenant_normenkader",
        ["standard_id"],
    )
    op.create_index(
        "ix_ims_standard_ingestions_tenant_id",
        "ims_standard_ingestions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_standard_ingestions_status",
        "ims_standard_ingestions",
        ["status"],
    )
    op.create_index("ix_ims_scopes_tenant_id", "ims_scopes", ["tenant_id"])
    op.create_index("ix_ims_scopes_parent_id", "ims_scopes", ["parent_id"])
    op.create_index("ix_ims_scopes_type", "ims_scopes", ["type"])
    op.create_index("ix_ims_risks_tenant_id", "ims_risks", ["tenant_id"])
    op.create_index("ix_ims_risks_scope_id", "ims_risks", ["scope_id"])
    op.create_index("ix_ims_risks_status", "ims_risks", ["status"])
    op.create_index("ix_ims_risks_owner_user_id", "ims_risks", ["owner_user_id"])
    op.create_index("ix_ims_controls_tenant_id", "ims_controls", ["tenant_id"])
    op.create_index(
        "ix_ims_controls_requirement_id", "ims_controls", ["requirement_id"]
    )
    op.create_index(
        "ix_ims_controls_implementation_status",
        "ims_controls",
        ["implementation_status"],
    )
    op.create_index(
        "ix_ims_risk_control_links_risk_id",
        "ims_risk_control_links",
        ["risk_id"],
    )
    op.create_index(
        "ix_ims_risk_control_links_control_id",
        "ims_risk_control_links",
        ["control_id"],
    )
    op.create_index(
        "ix_ims_assessments_tenant_id", "ims_assessments", ["tenant_id"]
    )
    op.create_index(
        "ix_ims_assessments_scope_id", "ims_assessments", ["scope_id"]
    )
    op.create_index(
        "ix_ims_assessments_status", "ims_assessments", ["status"]
    )
    op.create_index(
        "ix_ims_findings_assessment_id", "ims_findings", ["assessment_id"]
    )
    op.create_index("ix_ims_findings_tenant_id", "ims_findings", ["tenant_id"])
    op.create_index("ix_ims_findings_status", "ims_findings", ["status"])
    op.create_index("ix_ims_findings_severity", "ims_findings", ["severity"])
    op.create_index(
        "ix_ims_corrective_actions_tenant_id",
        "ims_corrective_actions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_corrective_actions_finding_id",
        "ims_corrective_actions",
        ["finding_id"],
    )
    op.create_index(
        "ix_ims_corrective_actions_risk_id",
        "ims_corrective_actions",
        ["risk_id"],
    )
    op.create_index(
        "ix_ims_corrective_actions_status",
        "ims_corrective_actions",
        ["status"],
    )
    op.create_index("ix_ims_evidence_tenant_id", "ims_evidence", ["tenant_id"])
    op.create_index("ix_ims_evidence_control_id", "ims_evidence", ["control_id"])
    op.create_index("ix_ims_incidents_tenant_id", "ims_incidents", ["tenant_id"])
    op.create_index("ix_ims_incidents_status", "ims_incidents", ["status"])
    op.create_index(
        "ix_ims_maturity_profiles_tenant_id",
        "ims_maturity_profiles",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_setup_scores_tenant_id", "ims_setup_scores", ["tenant_id"]
    )
    op.create_index(
        "ix_ims_setup_scores_domain_year",
        "ims_setup_scores",
        ["tenant_id", "domain", "cyclus_year"],
    )
    op.create_index(
        "ix_ims_grc_scores_tenant_id", "ims_grc_scores", ["tenant_id"]
    )
    op.create_index(
        "ix_ims_grc_scores_domain_year",
        "ims_grc_scores",
        ["tenant_id", "domain", "cyclus_year"],
    )
    op.create_index(
        "ix_ims_knowledge_chunks_tenant_id",
        "ims_knowledge_chunks",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ims_knowledge_chunks_layer", "ims_knowledge_chunks", ["layer"]
    )
    op.create_index(
        "ix_ims_knowledge_chunks_source_type",
        "ims_knowledge_chunks",
        ["source_type"],
    )

    # pgvector HNSW index for ANN similarity search
    op.execute(
        """
        CREATE INDEX ix_ims_knowledge_chunks_embedding_hnsw
        ON ims_knowledge_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index(
        "ix_ims_knowledge_chunks_embedding_hnsw",
        table_name="ims_knowledge_chunks",
    )
    op.drop_index(
        "ix_ims_knowledge_chunks_source_type", table_name="ims_knowledge_chunks"
    )
    op.drop_index(
        "ix_ims_knowledge_chunks_layer", table_name="ims_knowledge_chunks"
    )
    op.drop_index(
        "ix_ims_knowledge_chunks_tenant_id", table_name="ims_knowledge_chunks"
    )
    op.drop_index(
        "ix_ims_grc_scores_domain_year", table_name="ims_grc_scores"
    )
    op.drop_index("ix_ims_grc_scores_tenant_id", table_name="ims_grc_scores")
    op.drop_index(
        "ix_ims_setup_scores_domain_year", table_name="ims_setup_scores"
    )
    op.drop_index(
        "ix_ims_setup_scores_tenant_id", table_name="ims_setup_scores"
    )
    op.drop_index(
        "ix_ims_maturity_profiles_tenant_id", table_name="ims_maturity_profiles"
    )
    op.drop_index("ix_ims_incidents_status", table_name="ims_incidents")
    op.drop_index("ix_ims_incidents_tenant_id", table_name="ims_incidents")
    op.drop_index("ix_ims_evidence_control_id", table_name="ims_evidence")
    op.drop_index("ix_ims_evidence_tenant_id", table_name="ims_evidence")
    op.drop_index(
        "ix_ims_corrective_actions_status", table_name="ims_corrective_actions"
    )
    op.drop_index(
        "ix_ims_corrective_actions_risk_id", table_name="ims_corrective_actions"
    )
    op.drop_index(
        "ix_ims_corrective_actions_finding_id",
        table_name="ims_corrective_actions",
    )
    op.drop_index(
        "ix_ims_corrective_actions_tenant_id",
        table_name="ims_corrective_actions",
    )
    op.drop_index("ix_ims_findings_severity", table_name="ims_findings")
    op.drop_index("ix_ims_findings_status", table_name="ims_findings")
    op.drop_index("ix_ims_findings_tenant_id", table_name="ims_findings")
    op.drop_index("ix_ims_findings_assessment_id", table_name="ims_findings")
    op.drop_index("ix_ims_assessments_status", table_name="ims_assessments")
    op.drop_index("ix_ims_assessments_scope_id", table_name="ims_assessments")
    op.drop_index(
        "ix_ims_assessments_tenant_id", table_name="ims_assessments"
    )
    op.drop_index(
        "ix_ims_risk_control_links_control_id",
        table_name="ims_risk_control_links",
    )
    op.drop_index(
        "ix_ims_risk_control_links_risk_id", table_name="ims_risk_control_links"
    )
    op.drop_index(
        "ix_ims_controls_implementation_status", table_name="ims_controls"
    )
    op.drop_index("ix_ims_controls_requirement_id", table_name="ims_controls")
    op.drop_index("ix_ims_controls_tenant_id", table_name="ims_controls")
    op.drop_index("ix_ims_risks_owner_user_id", table_name="ims_risks")
    op.drop_index("ix_ims_risks_status", table_name="ims_risks")
    op.drop_index("ix_ims_risks_scope_id", table_name="ims_risks")
    op.drop_index("ix_ims_risks_tenant_id", table_name="ims_risks")
    op.drop_index("ix_ims_scopes_type", table_name="ims_scopes")
    op.drop_index("ix_ims_scopes_parent_id", table_name="ims_scopes")
    op.drop_index("ix_ims_scopes_tenant_id", table_name="ims_scopes")
    op.drop_index(
        "ix_ims_standard_ingestions_status",
        table_name="ims_standard_ingestions",
    )
    op.drop_index(
        "ix_ims_standard_ingestions_tenant_id",
        table_name="ims_standard_ingestions",
    )
    op.drop_index(
        "ix_ims_tenant_normenkader_standard_id",
        table_name="ims_tenant_normenkader",
    )
    op.drop_index(
        "ix_ims_tenant_normenkader_tenant_id",
        table_name="ims_tenant_normenkader",
    )
    op.drop_index(
        "ix_ims_requirement_mappings_target_requirement_id",
        table_name="ims_requirement_mappings",
    )
    op.drop_index(
        "ix_ims_requirement_mappings_source_requirement_id",
        table_name="ims_requirement_mappings",
    )
    op.drop_index("ix_ims_requirements_domain", table_name="ims_requirements")
    op.drop_index(
        "ix_ims_requirements_standard_id", table_name="ims_requirements"
    )
    op.drop_index(
        "ix_ims_step_dependencies_step_id", table_name="ims_step_dependencies"
    )
    op.drop_index(
        "ix_ims_gap_analysis_results_input_document_id",
        table_name="ims_gap_analysis_results",
    )
    op.drop_index(
        "ix_ims_gap_analysis_results_tenant_id",
        table_name="ims_gap_analysis_results",
    )
    op.drop_index(
        "ix_ims_step_input_documents_status",
        table_name="ims_step_input_documents",
    )
    op.drop_index(
        "ix_ims_step_input_documents_step_execution_id",
        table_name="ims_step_input_documents",
    )
    op.drop_index(
        "ix_ims_step_input_documents_tenant_id",
        table_name="ims_step_input_documents",
    )
    op.drop_index(
        "ix_ims_document_versions_status", table_name="ims_document_versions"
    )
    op.drop_index(
        "ix_ims_document_versions_document_id",
        table_name="ims_document_versions",
    )
    op.drop_index(
        "ix_ims_documents_step_execution_id", table_name="ims_documents"
    )
    op.drop_index("ix_ims_documents_tenant_id", table_name="ims_documents")
    op.drop_index(
        "ix_ims_decisions_step_execution_id", table_name="ims_decisions"
    )
    op.drop_index("ix_ims_decisions_tenant_id", table_name="ims_decisions")
    op.drop_index(
        "ix_ims_step_executions_status", table_name="ims_step_executions"
    )
    op.drop_index(
        "ix_ims_step_executions_step_id", table_name="ims_step_executions"
    )
    op.drop_index(
        "ix_ims_step_executions_tenant_id", table_name="ims_step_executions"
    )
    op.drop_index(
        "ix_ai_audit_logs_step_execution_id", table_name="ai_audit_logs"
    )
    op.drop_index("ix_ai_audit_logs_user_id", table_name="ai_audit_logs")
    op.drop_index("ix_ai_audit_logs_tenant_id", table_name="ai_audit_logs")
    op.drop_index(
        "ix_user_region_roles_region_id", table_name="user_region_roles"
    )
    op.drop_index(
        "ix_user_region_roles_user_id", table_name="user_region_roles"
    )
    op.drop_index(
        "ix_user_tenant_roles_user_id", table_name="user_tenant_roles"
    )
    op.drop_index(
        "ix_user_tenant_roles_tenant_id", table_name="user_tenant_roles"
    )
    op.drop_index("ix_users_tenant_id", table_name="users")

    # Drop deferred FKs before dropping tables
    op.drop_constraint(
        "fk_ims_standards_superseded_by_id",
        "ims_standards",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ims_decisions_supersedes_id", "ims_decisions", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_regions_centrum_tenant_id", "regions", type_="foreignkey"
    )

    # Drop tables in reverse creation order
    op.drop_table("ims_knowledge_chunks")
    op.drop_table("ims_grc_scores")
    op.drop_table("ims_setup_scores")
    op.drop_table("ims_maturity_profiles")
    op.drop_table("ims_incidents")
    op.drop_table("ims_evidence")
    op.drop_table("ims_corrective_actions")
    op.drop_table("ims_findings")
    op.drop_table("ims_assessments")
    op.drop_table("ims_risk_control_links")
    op.drop_table("ims_controls")
    op.drop_table("ims_risks")
    op.drop_table("ims_scopes")
    op.drop_table("ims_standard_ingestions")
    op.drop_table("ims_tenant_normenkader")
    op.drop_table("ims_requirement_mappings")
    op.drop_table("ims_requirements")
    op.drop_table("ims_standards")
    op.drop_table("ims_step_dependencies")
    op.drop_table("ims_gap_analysis_results")
    op.drop_table("ims_step_input_documents")
    op.drop_table("ims_document_versions")
    op.drop_table("ims_documents")
    op.drop_table("ims_decisions")
    op.drop_table("ai_audit_logs")
    op.drop_table("ims_step_executions")
    op.drop_table("ims_steps")
    op.drop_table("user_region_roles")
    op.drop_table("user_tenant_roles")
    op.drop_table("users")
    op.drop_table("tenants")
    op.drop_table("regions")
