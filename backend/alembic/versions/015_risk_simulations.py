"""Simulatie-historie — ims_risk_simulations (M5)

Voegt tabel toe voor reproduceerbare en vergelijkbare Monte Carlo-runs per
risico. Bevat input-snapshot (distribution, parameters, iterations, seed) en
output-samenvatting (expected_loss, var_95/99, percentielen, statistics).

Ruwe samples worden bewust **niet** opgeslagen — bij 10k iteraties is dat
~80kB per row en bloeit DB onnodig op. Reproductie via opgeslagen seed.

Revision ID: 015
Revises: 014
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ims_risk_simulations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column(
            "risk_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ims_risks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        # user_id nullable: tokens met fictieve sub (dev/agent) hebben geen
        # bijbehorende users-row. FK blijft voor productie-traceability.
        # Input-snapshot — risico kan na deze run worden aangepast; snapshot
        # bewaart wat er werd gesimuleerd, niet wat er nu in ims_risks staat.
        sa.Column("distribution", sa.String(20), nullable=False),
        sa.Column("parameters", JSONB(), nullable=False),
        sa.Column("iterations", sa.Integer(), nullable=False),
        sa.Column("seed", sa.BigInteger(), nullable=True),
        # Output-samenvatting — voldoende voor lijstweergave en vergelijken
        # zonder de ruwe samples-array te hoeven persisteren.
        sa.Column("expected_loss", sa.Numeric(15, 2), nullable=False),
        sa.Column("var_95", sa.Numeric(15, 2), nullable=False),
        sa.Column("var_99", sa.Numeric(15, 2), nullable=False),
        sa.Column("percentiles", JSONB(), nullable=False),
        sa.Column("statistics", JSONB(), nullable=False),
        # Optionele annotaties — "Scenario na mitigatie X", losse notitie
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_ims_risk_simulations_tenant_risk_created",
        "ims_risk_simulations",
        ["tenant_id", "risk_id", "created_at"],
    )

    # CHECK-constraint conform supported distributies (matcht service-laag).
    op.execute(
        """
        ALTER TABLE ims_risk_simulations
        ADD CONSTRAINT ims_risk_simulations_distribution_check
        CHECK (distribution IN ('uniform', 'triangular'));
        """
    )

    # RLS — multi-tenant isolatie, conform pattern in migration 002
    op.execute("ALTER TABLE ims_risk_simulations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ims_risk_simulations FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY ims_risk_simulations_tenant_isolation ON ims_risk_simulations
            USING (tenant_id::text = current_setting('app.current_tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true));
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP POLICY IF EXISTS ims_risk_simulations_tenant_isolation ON ims_risk_simulations;"
    )
    op.execute("ALTER TABLE ims_risk_simulations DISABLE ROW LEVEL SECURITY;")
    op.drop_index(
        "ix_ims_risk_simulations_tenant_risk_created",
        table_name="ims_risk_simulations",
    )
    op.drop_table("ims_risk_simulations")
