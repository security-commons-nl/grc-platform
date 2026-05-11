"""Risicokwantificatie — financiële range + distributie op ims_risks (M5)

Voegt drie kolommen toe aan ims_risks zodat Monte Carlo-simulatie
mogelijk is bovenop het bestaande point-estimate veld
`financial_impact_eur`.

Revision ID: 014
Revises: 013
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ims_risks",
        sa.Column("financial_impact_min_eur", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "ims_risks",
        sa.Column("financial_impact_max_eur", sa.Numeric(15, 2), nullable=True),
    )
    op.add_column(
        "ims_risks",
        sa.Column("impact_distribution", sa.String(20), nullable=True),
    )

    # CHECK constraint op enum-achtige waarden
    op.execute("""
        ALTER TABLE ims_risks ADD CONSTRAINT ims_risks_impact_distribution_check
        CHECK (impact_distribution IS NULL OR impact_distribution IN (
            'single', 'uniform', 'triangular'
        ));
    """)

    # Logical constraint: als min EN max gezet, dan max >= min
    op.execute("""
        ALTER TABLE ims_risks ADD CONSTRAINT ims_risks_impact_range_ordered
        CHECK (
            financial_impact_min_eur IS NULL OR
            financial_impact_max_eur IS NULL OR
            financial_impact_max_eur >= financial_impact_min_eur
        );
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE ims_risks DROP CONSTRAINT IF EXISTS ims_risks_impact_range_ordered;")
    op.execute("ALTER TABLE ims_risks DROP CONSTRAINT IF EXISTS ims_risks_impact_distribution_check;")
    op.drop_column("ims_risks", "impact_distribution")
    op.drop_column("ims_risks", "financial_impact_max_eur")
    op.drop_column("ims_risks", "financial_impact_min_eur")
