"""Initial schema - all IMS models

Revision ID: 001_initial
Revises:
Create Date: 2025-02-04

This migration represents the initial database schema with all 85+ entities.
It should be run on a fresh database or used as baseline for existing databases.

To stamp an existing database as having this migration applied:
    alembic stamp 001_initial
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create all tables for IMS.

    Note: This migration is intentionally left as a marker.
    The actual schema is managed by SQLModel.metadata.create_all() in db.py.

    For new installations:
    1. Run the application once to create tables via SQLModel
    2. Run: alembic stamp 001_initial

    Future migrations will use autogenerate to detect changes.
    """
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # The tables are created by SQLModel.metadata.create_all()
    # This migration serves as the baseline marker
    pass


def downgrade() -> None:
    """
    Drop all tables.

    WARNING: This will delete all data!
    """
    # In a real downgrade, we would drop all tables
    # But this is dangerous, so we just pass
    pass
