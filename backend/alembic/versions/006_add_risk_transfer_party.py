"""Add transfer_party column to risk table

Revision ID: 006_add_risk_transfer_party
Revises: 005_role_simplification
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_add_risk_transfer_party'
down_revision: Union[str, None] = '005_role_simplification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risk', sa.Column('transfer_party', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('risk', 'transfer_party')
