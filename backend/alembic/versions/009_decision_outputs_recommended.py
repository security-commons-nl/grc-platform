"""Decision outputs: V → A + skip_warning teksten

Revision ID: 009
Revises: 008
Create Date: 2026-03-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add skip_warning column
    op.add_column("ims_step_outputs", sa.Column("skip_warning", sa.Text(), nullable=True))

    # Change all decision outputs from V (verplicht) to A (aanbevolen)
    op.execute(sa.text(
        "UPDATE ims_step_outputs SET requirement = 'A' WHERE output_type = 'decision'"
    ))

    # Set skip_warning per decision output
    warnings = [
        ("1", "Besluitmemo",
         "U gaat verder zonder formeel akkoord van het bestuur. Uw team heeft geen mandaat om middelen in te zetten of beslissingen te nemen. Als er later discussie ontstaat over budget of prioriteit, heeft u geen besluit om naar te verwijzen."),
        ("1", "Besluitlog #001",
         "Het eerste besluit is niet vastgelegd in de besluitlog. De besluitlog is de formele audit trail van uw IMS — zonder deze eerste entry mist de basis."),
        ("2b", "Formeel scopebesluit",
         "U gaat verder zonder vastgestelde scope. Het is onduidelijk welke afdelingen en domeinen meedoen. In de gap-analyse (stap 4) weet u niet wat u moet meten."),
        ("3b", "Formeel governance-besluit",
         "De governance-structuur is niet formeel vastgesteld. Lijnmanagement kan niet worden aangesproken op hun rol, omdat die rol niet officieel is bekrachtigd."),
        ("3b", "Besluitlog",
         "Het governance-besluit is niet vastgelegd in de besluitlog. Er is geen traceerbaar bewijs dat het strategisch gremium de structuur heeft goedgekeurd."),
        ("6", "Besluitlog",
         "Het normenkader is niet formeel besloten. Lijnmanagement gaat in Fase 1 aan de slag, maar kan later zeggen: 'dit was nooit besloten.'"),
        ("14", "Verbeterbeslissingen",
         "De verbeterbeslissingen van het strategisch gremium zijn niet vastgelegd. De PDCA-cyclus sluit niet — er is geen bewijs dat de resultaten zijn beoordeeld en dat verbeteracties zijn afgesproken."),
    ]

    for step_number, output_name, warning in warnings:
        op.execute(sa.text(
            "UPDATE ims_step_outputs SET skip_warning = :warning "
            "WHERE name = :name AND step_id IN (SELECT id FROM ims_steps WHERE number = :number)"
        ).bindparams(warning=warning, name=output_name, number=step_number))


def downgrade() -> None:
    # Revert decision outputs back to V
    op.execute(sa.text(
        "UPDATE ims_step_outputs SET requirement = 'V' WHERE output_type = 'decision'"
    ))
    op.drop_column("ims_step_outputs", "skip_warning")
