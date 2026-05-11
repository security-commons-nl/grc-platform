"""AI Conformiteitsbeoordeling als assessment-type (M4)

Voegt:
  - kolom `ai_system_id` op `ims_assessments` (FK -> ims_ai_systems)
  - index voor filtering op AI-systeem

Het nieuwe assessment_type 'ai_conformity' wordt op applicatieniveau
gevalideerd (AssessmentTypeEnum in core_models.py); de database-kolom
is een vrije String(30), geen check-constraint.

Revision ID: 012
Revises: 011
Create Date: 2026-05-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ims_assessments",
        sa.Column("ai_system_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "ims_assessments_ai_system_id_fkey",
        "ims_assessments",
        "ims_ai_systems",
        ["ai_system_id"],
        ["id"],
    )
    op.create_index(
        "ix_ims_assessments_ai_system_id",
        "ims_assessments",
        ["ai_system_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ims_assessments_ai_system_id", table_name="ims_assessments")
    op.drop_constraint("ims_assessments_ai_system_id_fkey", "ims_assessments", type_="foreignkey")
    op.drop_column("ims_assessments", "ai_system_id")
