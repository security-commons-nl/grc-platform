"""Add User Story fields to BacklogItem

Revision ID: 003_backlog_user_story
Revises: 002_measure_to_control_refactor
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_backlog_user_story'
down_revision = '002_measure_to_control_refactor'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add User Story fields to backlogitem table
    op.add_column('backlogitem', sa.Column('user_role', sa.String(), nullable=True))
    op.add_column('backlogitem', sa.Column('user_want', sa.String(), nullable=True))
    op.add_column('backlogitem', sa.Column('user_so_that', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove User Story fields
    op.drop_column('backlogitem', 'user_so_that')
    op.drop_column('backlogitem', 'user_want')
    op.drop_column('backlogitem', 'user_role')
