"""Add OrganizationProfile table

Revision ID: 008_add_organization_profile
Revises: 007_add_assessment_phase_and_bia
Create Date: 2026-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_add_organization_profile'
down_revision: Union[str, None] = '007_add_assessment_phase_and_bia'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organizationprofile',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenant.id'), nullable=False, unique=True),

        # Blok 1: Identiteit
        sa.Column('org_type', sa.String(), nullable=True),
        sa.Column('sector', sa.String(), nullable=True),
        sa.Column('employee_count', sa.String(), nullable=True),
        sa.Column('location_count', sa.Integer(), nullable=True),
        sa.Column('geographic_scope', sa.String(), nullable=True),
        sa.Column('parent_organization', sa.String(), nullable=True),
        sa.Column('core_services', sa.Text(), nullable=True),

        # Blok 2: Governance
        sa.Column('existing_certifications', sa.Text(), nullable=True),
        sa.Column('applicable_frameworks', sa.Text(), nullable=True),
        sa.Column('has_security_officer', sa.Boolean(), nullable=True),
        sa.Column('has_dpo', sa.Boolean(), nullable=True),
        sa.Column('governance_maturity', sa.String(), nullable=True),
        sa.Column('risk_appetite_availability', sa.String(), nullable=True),
        sa.Column('risk_appetite_integrity', sa.String(), nullable=True),
        sa.Column('risk_appetite_confidentiality', sa.String(), nullable=True),

        # Blok 3: IT-Landschap
        sa.Column('cloud_strategy', sa.String(), nullable=True),
        sa.Column('cloud_providers', sa.Text(), nullable=True),
        sa.Column('workstation_count', sa.String(), nullable=True),
        sa.Column('has_remote_work', sa.Boolean(), nullable=True),
        sa.Column('has_byod', sa.Boolean(), nullable=True),
        sa.Column('critical_systems', sa.Text(), nullable=True),
        sa.Column('outsourced_it', sa.Boolean(), nullable=True),
        sa.Column('primary_it_supplier', sa.String(), nullable=True),

        # Blok 4: Privacy
        sa.Column('processes_personal_data', sa.Boolean(), nullable=True),
        sa.Column('data_subject_types', sa.Text(), nullable=True),
        sa.Column('has_special_categories', sa.Boolean(), nullable=True),
        sa.Column('international_transfers', sa.Boolean(), nullable=True),
        sa.Column('processing_count_estimate', sa.String(), nullable=True),

        # Blok 5: Continuiteit
        sa.Column('has_bcp', sa.Boolean(), nullable=True),
        sa.Column('has_incident_response_plan', sa.Boolean(), nullable=True),
        sa.Column('max_tolerable_downtime', sa.String(), nullable=True),
        sa.Column('critical_process_count', sa.Integer(), nullable=True),
        sa.Column('key_dependencies', sa.Text(), nullable=True),

        # Blok 6: Mensen
        sa.Column('has_awareness_program', sa.Boolean(), nullable=True),
        sa.Column('has_background_checks', sa.Boolean(), nullable=True),
        sa.Column('training_frequency', sa.String(), nullable=True),

        # Meta
        sa.Column('wizard_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('wizard_current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
    )
    op.create_index('ix_organizationprofile_tenant_id', 'organizationprofile', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('ix_organizationprofile_tenant_id')
    op.drop_table('organizationprofile')
