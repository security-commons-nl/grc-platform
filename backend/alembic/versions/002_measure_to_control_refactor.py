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
revision: str = '002_measure_control'
down_revision: Union[str, None] = '31de748cb282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Rename tables and columns for Measure/Control separation.

    IMPORTANT: Order matters to avoid FK constraint violations!
    1. Drop foreign keys first
    2. Rename tables
    3. Rename columns
    4. Recreate foreign keys
    """

    # =========================================================================
    # STEP 1: Drop Foreign Keys (to allow renaming)
    # =========================================================================

    # Drop FK from measurerisklink to measure
    op.drop_constraint('measurerisklink_measure_id_fkey', 'measurerisklink', type_='foreignkey')
    op.drop_constraint('measurerisklink_risk_id_fkey', 'measurerisklink', type_='foreignkey')

    # Drop FK from measurerequirementlink to measure
    op.drop_constraint('measurerequirementlink_measure_id_fkey', 'measurerequirementlink', type_='foreignkey')
    op.drop_constraint('measurerequirementlink_requirement_id_fkey', 'measurerequirementlink', type_='foreignkey')

    # Drop FK from sharedmeasure to measure
    op.drop_constraint('sharedmeasure_measure_id_fkey', 'sharedmeasure', type_='foreignkey')
    op.drop_constraint('sharedmeasure_provider_tenant_id_fkey', 'sharedmeasure', type_='foreignkey')

    # Drop FK from evidence to measure
    op.drop_constraint('evidence_measure_id_fkey', 'evidence', type_='foreignkey')

    # Drop FK from finding to measure
    op.drop_constraint('finding_measure_id_fkey', 'finding', type_='foreignkey')

    # Drop FK from gapanalysisitem to measure (existing_measure_id)
    op.drop_constraint('gapanalysisitem_existing_measure_id_fkey', 'gapanalysisitem', type_='foreignkey')

    # Drop FK from correctiveaction to measure (if exists)
    try:
        op.drop_constraint('correctiveaction_measure_id_fkey', 'correctiveaction', type_='foreignkey')
    except Exception:
        pass  # May not exist

    # Drop FK from applicabilitystatement to measure/sharedmeasure (if exists)
    try:
        op.drop_constraint('applicabilitystatement_local_measure_id_fkey', 'applicabilitystatement', type_='foreignkey')
        op.drop_constraint('applicabilitystatement_shared_measure_id_fkey', 'applicabilitystatement', type_='foreignkey')
    except Exception:
        pass  # May not exist or have different names

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

    # In evidence: measure_id -> control_id
    op.alter_column('evidence', 'measure_id', new_column_name='control_id')

    # In finding: measure_id -> control_id
    op.alter_column('finding', 'measure_id', new_column_name='control_id')

    # In gapanalysisitem: existing_measure_id -> existing_control_id
    op.alter_column('gapanalysisitem', 'existing_measure_id', new_column_name='existing_control_id')

    # In correctiveaction: measure_id -> control_id (if exists)
    try:
        op.alter_column('correctiveaction', 'measure_id', new_column_name='control_id')
    except Exception:
        pass  # Column may not exist

    # In applicabilitystatement: rename columns if they exist
    try:
        op.alter_column('applicabilitystatement', 'local_measure_id', new_column_name='local_control_id')
        op.alter_column('applicabilitystatement', 'shared_measure_id', new_column_name='shared_control_id')
    except Exception:
        pass  # Columns may not exist

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
        sa.ForeignKeyConstraint(['control_id'], ['control.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['measure_id'], ['measure.id'], ondelete='CASCADE'),
    )

    # =========================================================================
    # STEP 5: Recreate Foreign Keys
    # =========================================================================

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

    # sharedcontrol -> control
    op.create_foreign_key(
        'sharedcontrol_control_id_fkey', 'sharedcontrol', 'control',
        ['control_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'sharedcontrol_provider_tenant_id_fkey', 'sharedcontrol', 'tenant',
        ['provider_tenant_id'], ['id'], ondelete='CASCADE'
    )

    # evidence -> control
    op.create_foreign_key(
        'evidence_control_id_fkey', 'evidence', 'control',
        ['control_id'], ['id'], ondelete='SET NULL'
    )

    # finding -> control
    op.create_foreign_key(
        'finding_control_id_fkey', 'finding', 'control',
        ['control_id'], ['id'], ondelete='SET NULL'
    )

    # gapanalysisitem -> control (existing_control_id)
    op.create_foreign_key(
        'gapanalysisitem_existing_control_id_fkey', 'gapanalysisitem', 'control',
        ['existing_control_id'], ['id'], ondelete='SET NULL'
    )

    # correctiveaction -> control (if column exists)
    try:
        op.create_foreign_key(
            'correctiveaction_control_id_fkey', 'correctiveaction', 'control',
            ['control_id'], ['id'], ondelete='SET NULL'
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
        op.create_foreign_key(
            'applicabilitystatement_shared_control_id_fkey',
            'applicabilitystatement', 'sharedcontrol',
            ['shared_control_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        pass

    # =========================================================================
    # STEP 6: Update Indexes (if any named indexes need renaming)
    # =========================================================================
    # Most indexes will auto-update with table/column renames
    # Add explicit index recreation here if needed


def downgrade() -> None:
    """
    Reverse the migration - restore original table/column names.
    """

    # Drop new table
    op.drop_table('controlmeasurelink')

    # Drop foreign keys
    op.drop_constraint('controlrisklink_control_id_fkey', 'controlrisklink', type_='foreignkey')
    op.drop_constraint('controlrisklink_risk_id_fkey', 'controlrisklink', type_='foreignkey')
    op.drop_constraint('controlrequirementlink_control_id_fkey', 'controlrequirementlink', type_='foreignkey')
    op.drop_constraint('controlrequirementlink_requirement_id_fkey', 'controlrequirementlink', type_='foreignkey')
    op.drop_constraint('sharedcontrol_control_id_fkey', 'sharedcontrol', type_='foreignkey')
    op.drop_constraint('sharedcontrol_provider_tenant_id_fkey', 'sharedcontrol', type_='foreignkey')
    op.drop_constraint('evidence_control_id_fkey', 'evidence', type_='foreignkey')
    op.drop_constraint('finding_control_id_fkey', 'finding', type_='foreignkey')
    op.drop_constraint('gapanalysisitem_existing_control_id_fkey', 'gapanalysisitem', type_='foreignkey')

    try:
        op.drop_constraint('correctiveaction_control_id_fkey', 'correctiveaction', type_='foreignkey')
    except Exception:
        pass

    try:
        op.drop_constraint('applicabilitystatement_local_control_id_fkey', 'applicabilitystatement', type_='foreignkey')
        op.drop_constraint('applicabilitystatement_shared_control_id_fkey', 'applicabilitystatement', type_='foreignkey')
    except Exception:
        pass

    # Rename columns back
    op.alter_column('controlrisklink', 'control_id', new_column_name='measure_id')
    op.alter_column('controlrequirementlink', 'control_id', new_column_name='measure_id')
    op.alter_column('sharedcontrol', 'control_id', new_column_name='measure_id')
    op.alter_column('evidence', 'control_id', new_column_name='measure_id')
    op.alter_column('finding', 'control_id', new_column_name='measure_id')
    op.alter_column('gapanalysisitem', 'existing_control_id', new_column_name='existing_measure_id')

    try:
        op.alter_column('correctiveaction', 'control_id', new_column_name='measure_id')
    except Exception:
        pass

    try:
        op.alter_column('applicabilitystatement', 'local_control_id', new_column_name='local_measure_id')
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
    op.create_foreign_key('sharedmeasure_provider_tenant_id_fkey', 'sharedmeasure', 'tenant',
                          ['provider_tenant_id'], ['id'])
    op.create_foreign_key('evidence_measure_id_fkey', 'evidence', 'measure',
                          ['measure_id'], ['id'])
    op.create_foreign_key('finding_measure_id_fkey', 'finding', 'measure',
                          ['measure_id'], ['id'])
    op.create_foreign_key('gapanalysisitem_existing_measure_id_fkey', 'gapanalysisitem', 'measure',
                          ['existing_measure_id'], ['id'])
