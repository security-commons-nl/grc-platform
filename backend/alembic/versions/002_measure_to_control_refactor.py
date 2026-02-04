"""Refactor Measure/Control naming

Revision ID: 002_measure_control
Revises: 31de748cb282
Create Date: 2026-02-04

This migration implements the architectural separation between:
- Measure (generic, reusable policy building blocks from catalog)
- Control (context-specific, testable implementations)

Changes:
- Rename measuretemplate -> measure (the catalog)
- Rename measure -> control (the implementations)
- Rename link tables and columns accordingly
- Create new controlmeasurelink table for many-to-many
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_measure_to_control_refactor'
down_revision: Union[str, None] = '31de748cb282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Rename tables and columns for Measure/Control separation.
    Uses raw SQL for better control over constraint handling.
    """

    # =========================================================================
    # STEP 1: Drop Foreign Keys using raw SQL (safer with IF EXISTS pattern)
    # =========================================================================

    # Get connection for raw SQL
    connection = op.get_bind()

    # Helper to safely drop constraint
    def safe_drop_fk(table: str, constraint: str):
        connection.execute(sa.text(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"
        ))

    # Drop FKs from measurerisklink
    safe_drop_fk('measurerisklink', 'measurerisklink_measure_id_fkey')
    safe_drop_fk('measurerisklink', 'measurerisklink_risk_id_fkey')

    # Drop FKs from measurerequirementlink
    safe_drop_fk('measurerequirementlink', 'measurerequirementlink_measure_id_fkey')
    safe_drop_fk('measurerequirementlink', 'measurerequirementlink_requirement_id_fkey')

    # Drop FKs from sharedmeasure
    safe_drop_fk('sharedmeasure', 'sharedmeasure_measure_id_fkey')
    safe_drop_fk('sharedmeasure', 'sharedmeasure_consumer_tenant_id_fkey')
    safe_drop_fk('sharedmeasure', 'sharedmeasure_provider_tenant_id_fkey')
    safe_drop_fk('sharedmeasure', 'sharedmeasure_relationship_id_fkey')
    safe_drop_fk('sharedmeasure', 'sharedmeasure_local_contact_id_fkey')
    safe_drop_fk('sharedmeasure', 'sharedmeasure_acknowledged_by_id_fkey')

    # Drop FKs from evidence
    safe_drop_fk('evidence', 'evidence_measure_id_fkey')

    # Drop FKs from finding
    safe_drop_fk('finding', 'finding_measure_id_fkey')

    # Drop FKs from gapanalysisitem
    safe_drop_fk('gapanalysisitem', 'gapanalysisitem_existing_measure_id_fkey')

    # Drop FKs from correctiveaction (if exists)
    safe_drop_fk('correctiveaction', 'correctiveaction_measure_id_fkey')

    # Drop FKs from applicabilitystatement (if exists)
    safe_drop_fk('applicabilitystatement', 'applicabilitystatement_local_measure_id_fkey')
    safe_drop_fk('applicabilitystatement', 'applicabilitystatement_shared_measure_id_fkey')

    # =========================================================================
    # STEP 2: Rename Tables
    # NOTE: Order matters! We must free up 'measure' name before using it.
    # =========================================================================

    # FIRST: measure -> control (frees up the name 'measure')
    op.rename_table('measure', 'control')

    # THEN: measuretemplate -> measure (now we can use the freed name)
    op.rename_table('measuretemplate', 'measure')

    # measurerisklink -> controlrisklink
    op.rename_table('measurerisklink', 'controlrisklink')

    # measurerequirementlink -> controlrequirementlink
    op.rename_table('measurerequirementlink', 'controlrequirementlink')

    # sharedmeasure -> sharedcontrol
    op.rename_table('sharedmeasure', 'sharedcontrol')

    # =========================================================================
    # STEP 3: Rename Columns
    # =========================================================================

    # In controlrisklink: measure_id -> control_id
    op.alter_column('controlrisklink', 'measure_id', new_column_name='control_id')

    # In controlrequirementlink: measure_id -> control_id
    op.alter_column('controlrequirementlink', 'measure_id', new_column_name='control_id')

    # In sharedcontrol: measure_id -> control_id
    op.alter_column('sharedcontrol', 'measure_id', new_column_name='control_id')

    # In evidence: measure_id -> control_id (if column exists)
    try:
        op.alter_column('evidence', 'measure_id', new_column_name='control_id')
    except Exception:
        pass

    # In finding: measure_id -> control_id (if column exists)
    try:
        op.alter_column('finding', 'measure_id', new_column_name='control_id')
    except Exception:
        pass

    # In gapanalysisitem: existing_measure_id -> existing_control_id
    try:
        op.alter_column('gapanalysisitem', 'existing_measure_id', new_column_name='existing_control_id')
    except Exception:
        pass

    # In applicabilitystatement: rename columns if they exist
    try:
        op.alter_column('applicabilitystatement', 'local_measure_id', new_column_name='local_control_id')
    except Exception:
        pass
    try:
        op.alter_column('applicabilitystatement', 'shared_measure_id', new_column_name='shared_control_id')
    except Exception:
        pass

    # =========================================================================
    # STEP 4: Create New Tables
    # =========================================================================

    # Create controlmeasurelink (Control -> Measure many-to-many)
    op.create_table(
        'controlmeasurelink',
        sa.Column('control_id', sa.Integer(), nullable=False),
        sa.Column('measure_id', sa.Integer(), nullable=False),
        sa.Column('coverage_percentage', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('control_id', 'measure_id'),
    )

    # =========================================================================
    # STEP 5: Recreate Foreign Keys
    # =========================================================================

    # controlmeasurelink FKs
    op.create_foreign_key(
        'controlmeasurelink_control_id_fkey', 'controlmeasurelink', 'control',
        ['control_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'controlmeasurelink_measure_id_fkey', 'controlmeasurelink', 'measure',
        ['measure_id'], ['id'], ondelete='CASCADE'
    )

    # controlrisklink -> control
    op.create_foreign_key(
        'controlrisklink_control_id_fkey', 'controlrisklink', 'control',
        ['control_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'controlrisklink_risk_id_fkey', 'controlrisklink', 'risk',
        ['risk_id'], ['id'], ondelete='CASCADE'
    )

    # controlrequirementlink -> control
    op.create_foreign_key(
        'controlrequirementlink_control_id_fkey', 'controlrequirementlink', 'control',
        ['control_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'controlrequirementlink_requirement_id_fkey', 'controlrequirementlink', 'requirement',
        ['requirement_id'], ['id'], ondelete='CASCADE'
    )

    # sharedcontrol FKs
    op.create_foreign_key(
        'sharedcontrol_control_id_fkey', 'sharedcontrol', 'control',
        ['control_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'sharedcontrol_consumer_tenant_id_fkey', 'sharedcontrol', 'tenant',
        ['consumer_tenant_id'], ['id'], ondelete='CASCADE'
    )

    # Recreate other sharedcontrol FKs that existed
    try:
        op.create_foreign_key(
            'sharedcontrol_relationship_id_fkey', 'sharedcontrol', 'tenantrelationship',
            ['relationship_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass
    try:
        op.create_foreign_key(
            'sharedcontrol_local_contact_id_fkey', 'sharedcontrol', 'user',
            ['local_contact_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass
    try:
        op.create_foreign_key(
            'sharedcontrol_acknowledged_by_id_fkey', 'sharedcontrol', 'user',
            ['acknowledged_by_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass

    # evidence -> control
    try:
        op.create_foreign_key(
            'evidence_control_id_fkey', 'evidence', 'control',
            ['control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass

    # finding -> control
    try:
        op.create_foreign_key(
            'finding_control_id_fkey', 'finding', 'control',
            ['control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass

    # gapanalysisitem -> control (existing_control_id)
    try:
        op.create_foreign_key(
            'gapanalysisitem_existing_control_id_fkey', 'gapanalysisitem', 'control',
            ['existing_control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass

    # applicabilitystatement -> control and sharedcontrol
    try:
        op.create_foreign_key(
            'applicabilitystatement_local_control_id_fkey',
            'applicabilitystatement', 'control',
            ['local_control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass
    try:
        op.create_foreign_key(
            'applicabilitystatement_shared_control_id_fkey',
            'applicabilitystatement', 'sharedcontrol',
            ['shared_control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass


def downgrade() -> None:
    """
    Reverse the migration - restore original table/column names.
    """
    connection = op.get_bind()

    def safe_drop_fk(table: str, constraint: str):
        connection.execute(sa.text(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"
        ))

    # Drop new table
    op.drop_table('controlmeasurelink')

    # Drop foreign keys
    safe_drop_fk('controlrisklink', 'controlrisklink_control_id_fkey')
    safe_drop_fk('controlrisklink', 'controlrisklink_risk_id_fkey')
    safe_drop_fk('controlrequirementlink', 'controlrequirementlink_control_id_fkey')
    safe_drop_fk('controlrequirementlink', 'controlrequirementlink_requirement_id_fkey')
    safe_drop_fk('sharedcontrol', 'sharedcontrol_control_id_fkey')
    safe_drop_fk('sharedcontrol', 'sharedcontrol_consumer_tenant_id_fkey')
    safe_drop_fk('sharedcontrol', 'sharedcontrol_relationship_id_fkey')
    safe_drop_fk('sharedcontrol', 'sharedcontrol_local_contact_id_fkey')
    safe_drop_fk('sharedcontrol', 'sharedcontrol_acknowledged_by_id_fkey')
    safe_drop_fk('evidence', 'evidence_control_id_fkey')
    safe_drop_fk('finding', 'finding_control_id_fkey')
    safe_drop_fk('gapanalysisitem', 'gapanalysisitem_existing_control_id_fkey')
    safe_drop_fk('applicabilitystatement', 'applicabilitystatement_local_control_id_fkey')
    safe_drop_fk('applicabilitystatement', 'applicabilitystatement_shared_control_id_fkey')

    # Rename columns back
    op.alter_column('controlrisklink', 'control_id', new_column_name='measure_id')
    op.alter_column('controlrequirementlink', 'control_id', new_column_name='measure_id')
    op.alter_column('sharedcontrol', 'control_id', new_column_name='measure_id')

    try:
        op.alter_column('evidence', 'control_id', new_column_name='measure_id')
    except Exception:
        pass
    try:
        op.alter_column('finding', 'control_id', new_column_name='measure_id')
    except Exception:
        pass
    try:
        op.alter_column('gapanalysisitem', 'existing_control_id', new_column_name='existing_measure_id')
    except Exception:
        pass
    try:
        op.alter_column('applicabilitystatement', 'local_control_id', new_column_name='local_measure_id')
    except Exception:
        pass
    try:
        op.alter_column('applicabilitystatement', 'shared_control_id', new_column_name='shared_measure_id')
    except Exception:
        pass

    # Rename tables back (reverse order!)
    op.rename_table('controlrequirementlink', 'measurerequirementlink')
    op.rename_table('controlrisklink', 'measurerisklink')
    op.rename_table('sharedcontrol', 'sharedmeasure')
    # FIRST: measure -> measuretemplate (frees up 'measure' name)
    op.rename_table('measure', 'measuretemplate')
    # THEN: control -> measure (now we can use the freed name)
    op.rename_table('control', 'measure')

    # Recreate original foreign keys
    op.create_foreign_key('measurerisklink_measure_id_fkey', 'measurerisklink', 'measure',
                          ['measure_id'], ['id'])
    op.create_foreign_key('measurerisklink_risk_id_fkey', 'measurerisklink', 'risk',
                          ['risk_id'], ['id'])
    op.create_foreign_key('measurerequirementlink_measure_id_fkey', 'measurerequirementlink', 'measure',
                          ['measure_id'], ['id'])
    op.create_foreign_key('measurerequirementlink_requirement_id_fkey', 'measurerequirementlink', 'requirement',
                          ['requirement_id'], ['id'])
    op.create_foreign_key('sharedmeasure_measure_id_fkey', 'sharedmeasure', 'measure',
                          ['measure_id'], ['id'])
    op.create_foreign_key('sharedmeasure_consumer_tenant_id_fkey', 'sharedmeasure', 'tenant',
                          ['consumer_tenant_id'], ['id'])
