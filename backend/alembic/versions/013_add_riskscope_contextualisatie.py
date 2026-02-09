"""Add RiskScope contextualisatie

Introduces RiskScope as a many-to-many between Risk and Scope with
per-scope scores, treatment, and acceptance. Replaces direct
ControlRiskLink / DecisionRiskLink with scope-aware variants.

Backfills existing data so every Risk gets at least one RiskScope record.

Revision ID: 013_add_riskscope
Revises: 012_relax_not_null
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "013_add_riskscope"
down_revision: Union[str, None] = "012_relax_not_null"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # 1. Create AcceptanceStatus enum type (if not already created by SQLModel)
    # =========================================================================
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE acceptancestatus AS ENUM ('Voorgesteld', 'Geaccepteerd', 'Afgewezen', 'Verlopen');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # =========================================================================
    # 2. Create RiskScope table
    # =========================================================================
    op.create_table(
        "riskscope",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("risk_id", sa.Integer(), sa.ForeignKey("risk.id"), nullable=False),
        sa.Column("scope_id", sa.Integer(), sa.ForeignKey("scope.id"), nullable=False),

        # Inherent Risk
        sa.Column("inherent_likelihood", sa.String(), nullable=True),
        sa.Column("inherent_impact", sa.String(), nullable=True),
        sa.Column("inherent_risk_score", sa.Integer(), nullable=True),

        # Residual Risk
        sa.Column("residual_likelihood", sa.String(), nullable=True),
        sa.Column("residual_impact", sa.String(), nullable=True),
        sa.Column("residual_risk_score", sa.Integer(), nullable=True),

        # Vulnerability & Control Effectiveness
        sa.Column("vulnerability_score", sa.Integer(), nullable=True),
        sa.Column("control_effectiveness_pct", sa.Integer(), nullable=True),

        # Attention Strategy
        sa.Column("attention_quadrant", sa.String(), nullable=True),
        sa.Column("ai_suggested_quadrant", sa.String(), nullable=True),

        # Treatment
        sa.Column("mitigation_approach", sa.String(), nullable=True),
        sa.Column("treatment_strategy", sa.String(), nullable=True),
        sa.Column("treatment_justification", sa.Text(), nullable=True),
        sa.Column("transfer_party", sa.String(), nullable=True),

        # Governance
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True),

        # Acceptance
        sa.Column("acceptance_status", sa.VARCHAR(), nullable=False, server_default="Voorgesteld"),
        sa.Column("accepted_by_decision_id", sa.Integer(), sa.ForeignKey("decision.id"), nullable=True),
        sa.Column("risk_accepted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("accepted_by_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("acceptance_date", sa.DateTime(), nullable=True),
        sa.Column("acceptance_justification", sa.Text(), nullable=True),
        sa.Column("risk_appetite_threshold", sa.String(), nullable=True),

        # Review
        sa.Column("last_review_date", sa.DateTime(), nullable=True),
        sa.Column("next_review_date", sa.DateTime(), nullable=True),
        sa.Column("review_frequency_months", sa.Integer(), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default="false"),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),

        # Constraints
        sa.UniqueConstraint("tenant_id", "risk_id", "scope_id", name="uq_riskscope_tenant_risk_scope"),
    )

    op.create_index("ix_riskscope_tenant_id", "riskscope", ["tenant_id"])
    op.create_index("ix_riskscope_risk_id", "riskscope", ["risk_id"])
    op.create_index("ix_riskscope_scope_id", "riskscope", ["scope_id"])
    op.create_index("ix_riskscope_tenant_scope", "riskscope", ["tenant_id", "scope_id"])
    op.create_index("ix_riskscope_tenant_risk", "riskscope", ["tenant_id", "risk_id"])

    # =========================================================================
    # 3. Create ControlRiskScopeLink table
    # =========================================================================
    op.create_table(
        "controlriskscopelink",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("control_id", sa.Integer(), sa.ForeignKey("control.id"), nullable=False),
        sa.Column("risk_scope_id", sa.Integer(), sa.ForeignKey("riskscope.id"), nullable=False),
        sa.Column("mitigation_percent", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),

        sa.UniqueConstraint("tenant_id", "control_id", "risk_scope_id", name="uq_controlriskscopelink_tenant_ctrl_rs"),
    )

    op.create_index("ix_controlriskscopelink_tenant_id", "controlriskscopelink", ["tenant_id"])
    op.create_index("ix_controlriskscopelink_control_id", "controlriskscopelink", ["control_id"])
    op.create_index("ix_controlriskscopelink_risk_scope_id", "controlriskscopelink", ["risk_scope_id"])

    # =========================================================================
    # 4. Create DecisionRiskScopeLink table
    # =========================================================================
    op.create_table(
        "decisionriskscopelink",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("decision_id", sa.Integer(), sa.ForeignKey("decision.id"), nullable=False),
        sa.Column("risk_scope_id", sa.Integer(), sa.ForeignKey("riskscope.id"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),

        sa.UniqueConstraint("tenant_id", "decision_id", "risk_scope_id", name="uq_decisionriskscopelink_tenant_dec_rs"),
    )

    op.create_index("ix_decisionriskscopelink_tenant_id", "decisionriskscopelink", ["tenant_id"])
    op.create_index("ix_decisionriskscopelink_decision_id", "decisionriskscopelink", ["decision_id"])
    op.create_index("ix_decisionriskscopelink_risk_scope_id", "decisionriskscopelink", ["risk_scope_id"])

    # =========================================================================
    # 5. Backfill RiskScope from Risk.scope_id (primary source)
    # =========================================================================
    op.execute("""
        INSERT INTO riskscope (
            tenant_id, risk_id, scope_id,
            inherent_likelihood, inherent_impact, inherent_risk_score,
            residual_likelihood, residual_impact, residual_risk_score,
            vulnerability_score, control_effectiveness_pct,
            attention_quadrant, ai_suggested_quadrant,
            mitigation_approach, treatment_strategy, treatment_justification, transfer_party,
            acceptance_status,
            risk_accepted, accepted_by_id, acceptance_date, acceptance_justification,
            risk_appetite_threshold,
            last_review_date, next_review_date, review_frequency_months, is_critical,
            created_at, updated_at
        )
        SELECT
            r.tenant_id, r.id, r.scope_id,
            r.inherent_likelihood, r.inherent_impact, r.inherent_risk_score,
            r.residual_likelihood, r.residual_impact, r.residual_risk_score,
            r.vulnerability_score, r.control_effectiveness_pct,
            r.attention_quadrant, r.ai_suggested_quadrant,
            r.mitigation_approach, r.treatment_strategy, r.treatment_justification, r.transfer_party,
            CASE WHEN r.risk_accepted THEN 'Geaccepteerd' ELSE 'Voorgesteld' END,
            r.risk_accepted, r.accepted_by_id, r.acceptance_date, r.acceptance_justification,
            r.risk_appetite_threshold,
            r.last_review_date, r.next_review_date, r.review_frequency_months, r.is_critical,
            now(), now()
        FROM risk r
        WHERE r.scope_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)

    # =========================================================================
    # 6. Backfill RiskScope via ControlRiskLink (secondary: risks without scope)
    # =========================================================================
    op.execute("""
        INSERT INTO riskscope (
            tenant_id, risk_id, scope_id,
            inherent_likelihood, inherent_impact, inherent_risk_score,
            residual_likelihood, residual_impact, residual_risk_score,
            vulnerability_score, control_effectiveness_pct,
            attention_quadrant, treatment_strategy,
            acceptance_status, risk_accepted,
            created_at, updated_at
        )
        SELECT DISTINCT ON (r.tenant_id, r.id, c.scope_id)
            r.tenant_id, r.id, c.scope_id,
            r.inherent_likelihood, r.inherent_impact, r.inherent_risk_score,
            r.residual_likelihood, r.residual_impact, r.residual_risk_score,
            r.vulnerability_score, r.control_effectiveness_pct,
            r.attention_quadrant, r.treatment_strategy,
            CASE WHEN r.risk_accepted THEN 'Geaccepteerd' ELSE 'Voorgesteld' END,
            r.risk_accepted,
            now(), now()
        FROM risk r
        JOIN controlrisklink crl ON crl.risk_id = r.id
        JOIN control c ON c.id = crl.control_id
        WHERE r.scope_id IS NULL
          AND c.scope_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM riskscope rs
              WHERE rs.risk_id = r.id AND rs.scope_id = c.scope_id AND rs.tenant_id = r.tenant_id
          )
        ON CONFLICT DO NOTHING
    """)

    # =========================================================================
    # 7. Fallback: create "Niet-toegewezen" scope per tenant for orphan risks
    # =========================================================================
    op.execute("""
        INSERT INTO scope (tenant_id, name, type, description, is_active, created_at, updated_at)
        SELECT DISTINCT t.id, 'Niet-toegewezen', 'Organization',
               'Automatisch aangemaakt voor risicos zonder scope', true, now(), now()
        FROM tenant t
        WHERE NOT EXISTS (
            SELECT 1 FROM scope s WHERE s.tenant_id = t.id AND s.name = 'Niet-toegewezen'
        )
    """)

    # Backfill remaining orphan risks into fallback scope
    op.execute("""
        INSERT INTO riskscope (
            tenant_id, risk_id, scope_id,
            inherent_likelihood, inherent_impact, inherent_risk_score,
            residual_likelihood, residual_impact, residual_risk_score,
            vulnerability_score, control_effectiveness_pct,
            attention_quadrant, treatment_strategy,
            acceptance_status, risk_accepted,
            created_at, updated_at
        )
        SELECT
            r.tenant_id, r.id, fallback.id,
            r.inherent_likelihood, r.inherent_impact, r.inherent_risk_score,
            r.residual_likelihood, r.residual_impact, r.residual_risk_score,
            r.vulnerability_score, r.control_effectiveness_pct,
            r.attention_quadrant, r.treatment_strategy,
            CASE WHEN r.risk_accepted THEN 'Geaccepteerd' ELSE 'Voorgesteld' END,
            r.risk_accepted,
            now(), now()
        FROM risk r
        JOIN scope fallback ON fallback.tenant_id = r.tenant_id AND fallback.name = 'Niet-toegewezen'
        WHERE NOT EXISTS (
            SELECT 1 FROM riskscope rs WHERE rs.risk_id = r.id AND rs.tenant_id = r.tenant_id
        )
        ON CONFLICT DO NOTHING
    """)

    # =========================================================================
    # 8. Backfill ControlRiskScopeLink from ControlRiskLink
    # =========================================================================
    op.execute("""
        INSERT INTO controlriskscopelink (tenant_id, control_id, risk_scope_id, mitigation_percent, created_at)
        SELECT
            c.tenant_id,
            crl.control_id,
            rs.id,
            crl.mitigation_percent,
            now()
        FROM controlrisklink crl
        JOIN control c ON c.id = crl.control_id
        JOIN riskscope rs ON rs.risk_id = crl.risk_id
            AND rs.scope_id = COALESCE(c.scope_id, (
                SELECT s.id FROM scope s WHERE s.tenant_id = c.tenant_id AND s.name = 'Niet-toegewezen' LIMIT 1
            ))
            AND rs.tenant_id = c.tenant_id
        ON CONFLICT DO NOTHING
    """)

    # =========================================================================
    # 9. Backfill DecisionRiskScopeLink from DecisionRiskLink
    # =========================================================================
    op.execute("""
        INSERT INTO decisionriskscopelink (tenant_id, decision_id, risk_scope_id, notes, created_at)
        SELECT
            d.tenant_id,
            drl.decision_id,
            rs.id,
            drl.notes,
            now()
        FROM decisionrisklink drl
        JOIN decision d ON d.id = drl.decision_id
        JOIN riskscope rs ON rs.risk_id = drl.risk_id
            AND rs.scope_id = COALESCE(d.scope_id, (
                SELECT s.id FROM scope s WHERE s.tenant_id = d.tenant_id AND s.name = 'Niet-toegewezen' LIMIT 1
            ))
            AND rs.tenant_id = d.tenant_id
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table("decisionriskscopelink")
    op.drop_table("controlriskscopelink")
    op.drop_table("riskscope")

    op.execute("DROP TYPE IF EXISTS acceptancestatus")
