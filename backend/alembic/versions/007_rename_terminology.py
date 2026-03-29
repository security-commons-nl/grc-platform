"""Rename SIMS/TIMS to strategisch/tactisch gremium

Revision ID: 007
Revises: 006
Create Date: 2026-03-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename gremium values in ims_steps
    op.execute(sa.text(
        "UPDATE ims_steps SET required_gremium = 'strategisch' WHERE required_gremium = 'sims'"
    ))
    op.execute(sa.text(
        "UPDATE ims_steps SET required_gremium = 'tactisch' WHERE required_gremium = 'tims'"
    ))

    # Rename gremium values in ims_decisions
    op.execute(sa.text(
        "UPDATE ims_decisions SET gremium = 'strategisch' WHERE gremium = 'sims'"
    ))
    op.execute(sa.text(
        "UPDATE ims_decisions SET gremium = 'tactisch' WHERE gremium = 'tims'"
    ))

    # Rename role values in user_tenant_roles
    op.execute(sa.text(
        "UPDATE user_tenant_roles SET role = 'strategisch_lid' WHERE role = 'sims_lid'"
    ))
    op.execute(sa.text(
        "UPDATE user_tenant_roles SET role = 'tactisch_lid' WHERE role = 'tims_lid'"
    ))

    # Rename TIMS/SIMS in waarom_nu free-text fields
    op.execute(sa.text(
        "UPDATE ims_steps SET waarom_nu = REPLACE(waarom_nu, 'het TIMS', 'het tactisch gremium') WHERE waarom_nu LIKE '%het TIMS%'"
    ))
    op.execute(sa.text(
        "UPDATE ims_steps SET waarom_nu = REPLACE(waarom_nu, 'Het SIMS', 'Het strategisch gremium') WHERE waarom_nu LIKE '%Het SIMS%'"
    ))
    op.execute(sa.text(
        "UPDATE ims_steps SET waarom_nu = REPLACE(waarom_nu, 'het SIMS', 'het strategisch gremium') WHERE waarom_nu LIKE '%het SIMS%'"
    ))

    # Rename tenant and region (if Leiden defaults exist)
    op.execute(sa.text(
        "UPDATE tenants SET name = 'Voorbeeldgemeente' WHERE name = 'Gemeente Leiden'"
    ))
    op.execute(sa.text(
        "UPDATE regions SET name = 'Voorbeeldregio' WHERE name = 'Leidse Regio'"
    ))


def downgrade() -> None:
    op.execute(sa.text(
        "UPDATE ims_steps SET required_gremium = 'sims' WHERE required_gremium = 'strategisch'"
    ))
    op.execute(sa.text(
        "UPDATE ims_steps SET required_gremium = 'tims' WHERE required_gremium = 'tactisch'"
    ))
    op.execute(sa.text(
        "UPDATE ims_decisions SET gremium = 'sims' WHERE gremium = 'strategisch'"
    ))
    op.execute(sa.text(
        "UPDATE ims_decisions SET gremium = 'tims' WHERE gremium = 'tactisch'"
    ))
    op.execute(sa.text(
        "UPDATE user_tenant_roles SET role = 'sims_lid' WHERE role = 'strategisch_lid'"
    ))
    op.execute(sa.text(
        "UPDATE user_tenant_roles SET role = 'tims_lid' WHERE role = 'tactisch_lid'"
    ))
    op.execute(sa.text(
        "UPDATE tenants SET name = 'Gemeente Leiden' WHERE name = 'Voorbeeldgemeente'"
    ))
    op.execute(sa.text(
        "UPDATE regions SET name = 'Leidse Regio' WHERE name = 'Voorbeeldregio'"
    ))
