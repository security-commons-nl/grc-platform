"""Add impact_correlation and financial_threshold_value to RiskAppetite

Extends RiskAppetite model with fields needed for the dynamic
risk tolerance / heatmap calculation engine.

Revision ID: 014_appetite_fields
Revises: 013_add_riskscope
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "014_appetite_fields"
down_revision: Union[str, None] = "013_add_riskscope"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "riskappetite",
        sa.Column("impact_correlation", sa.String(), nullable=True),
    )
    op.add_column(
        "riskappetite",
        sa.Column("financial_threshold_value", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("riskappetite", "financial_threshold_value")
    op.drop_column("riskappetite", "impact_correlation")
