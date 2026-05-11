"""NIST AI RMF 1.0 als zesde normenkader (M4 — AI Governance)

Voegt het NIST AI Risk Management Framework (versie 1.0, januari 2023)
toe aan ims_standards naast BIO, ISO 27001, ISO 27701, ISO 22301 en AVG.

Het NIST AI RMF heeft vier kernfuncties (GOVERN, MAP, MEASURE, MANAGE).
We voegen elke kernfunctie toe als top-level requirement zodat
organisaties hier controls aan kunnen koppelen.

Voor fijnmazigere categorieën (GV.PO, MP.IM, etc.) kan een latere
migratie sub-requirements toevoegen — voor MVP volstaan de vier
kernfuncties.

Revision ID: 011
Revises: 010
Create Date: 2026-05-12
"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NIST_RMF_STANDARD_NAME = "NIST AI RMF"
NIST_RMF_VERSION = "1.0"

CORE_FUNCTIONS = [
    (
        "GOVERN",
        "GOVERN — AI-risicobeheer governance",
        "Vestig en handhaaf processen, procedures en organisatorische structuren die "
        "AI-risicobeheer mogelijk maken. Bestrijkt beleid, rolverdeling, accountability, "
        "skills, transparantie en cultuur rondom AI-systemen.",
    ),
    (
        "MAP",
        "MAP — Context en risico's identificeren",
        "Identificeer en breng de context, beoogde gebruikers, doelen en mogelijke "
        "risico's van AI-systemen in kaart. Inclusief impact-assessment, "
        "stakeholderanalyse en grenzen van het systeem.",
    ),
    (
        "MEASURE",
        "MEASURE — Risico's beoordelen en meten",
        "Analyseer, beoordeel, benchmark en monitor AI-risico's met kwantitatieve "
        "en kwalitatieve methoden. Bestrijkt bias, robuustheid, uitlegbaarheid, "
        "privacy en performance over de tijd.",
    ),
    (
        "MANAGE",
        "MANAGE — Risico's beheersen en mitigeren",
        "Beheer geïdentificeerde risico's via mitigatie, monitoring, communicatie "
        "en incident-respons. Bestrijkt prioritering, risico-respons, communicatie "
        "naar stakeholders en periodieke heroverweging.",
    ),
]


def upgrade() -> None:
    bind = op.get_bind()

    # Insert het normenkader-record
    standard_id = uuid.uuid4()
    bind.execute(
        sa.text(
            "INSERT INTO ims_standards "
            "(id, name, version, published_at, status, domain, created_at, updated_at) "
            "VALUES (:id, :name, :version, :published, :status, :domain, now(), now())"
        ),
        {
            "id": standard_id,
            "name": NIST_RMF_STANDARD_NAME,
            "version": NIST_RMF_VERSION,
            "published": "2023-01-26",
            "status": "actief",
            "domain": "AIMS",
        },
    )

    # Insert de vier kernfunctie-requirements
    for code, title, description in CORE_FUNCTIONS:
        bind.execute(
            sa.text(
                "INSERT INTO ims_requirements "
                "(id, standard_id, code, title, description, domain, is_mandatory, "
                "created_at, updated_at) "
                "VALUES (:id, :standard_id, :code, :title, :description, :domain, "
                ":is_mandatory, now(), now())"
            ),
            {
                "id": uuid.uuid4(),
                "standard_id": standard_id,
                "code": code,
                "title": title,
                "description": description,
                "domain": "ISMS",  # NIST AI RMF requirements raken alle drie de IMS-domeinen
                "is_mandatory": True,
            },
        )


def downgrade() -> None:
    op.execute(
        f"DELETE FROM ims_requirements WHERE standard_id IN "
        f"(SELECT id FROM ims_standards WHERE name = '{NIST_RMF_STANDARD_NAME}' "
        f"AND version = '{NIST_RMF_VERSION}')"
    )
    op.execute(
        f"DELETE FROM ims_standards WHERE name = '{NIST_RMF_STANDARD_NAME}' "
        f"AND version = '{NIST_RMF_VERSION}'"
    )
