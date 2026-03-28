"""Seed step output definitions for all 22 steps

Revision ID: 005
Revises: 004
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _uuid():
    return str(uuid.uuid4())


def upgrade() -> None:
    # Lookup step IDs by number
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, number FROM ims_steps")).fetchall()
    steps = {row[1]: str(row[0]) for row in rows}

    # (step_number, name, output_type, requirement, sort_order)
    output_defs = [
        # ── Fase 0 ──────────────────────────────────────────────────
        # Stap 1: Bestuurlijk commitment
        ("1", "Besluitmemo", "decision", "V", 0),
        ("1", "Besluitlog #001", "decision", "V", 1),
        # Stap 2a: Organisatiecontext vaststellen
        ("2a", "Organisatiecontextdocument", "document", "V", 0),
        ("2a", "Stakeholderregister", "register", "V", 1),
        ("2a", "PII-rol", "document", "V", 2),
        # Stap 2b: Scope bepalen
        ("2b", "Formeel scopebesluit", "decision", "V", 0),
        # Stap 3a: Governance- en beleidsvoorstel opstellen
        ("3a", "Concept governance-document", "document", "V", 0),
        ("3a", "Concept IMS-beleid", "document", "V", 1),
        ("3a", "Communicatiematrix", "document", "V", 2),
        # Stap 3b: Governance en beleid vaststellen
        ("3b", "Formeel governance-besluit", "decision", "V", 0),
        ("3b", "IMS-beleid (definitief)", "document", "V", 1),
        ("3b", "Besluitlog", "decision", "V", 2),
        # Stap 4: Gap-analyse
        ("4", "Nulmeting per domein", "document", "V", 0),
        ("4", "Volwassenheidsprofiel v1", "document", "V", 1),
        # Stap 5: Registers & risicobeoordeling
        ("5", "Registerinventarisatie", "register", "V", 0),
        ("5", "Eerste risicobeeld", "document", "V", 1),
        ("5", "Risicobeoordelingsmethodiek", "document", "V", 2),
        # Stap 6: Normenkader & kerncontrols
        ("6", "Normenkader", "document", "V", 0),
        ("6", "Minimale werkset kerncontrols", "document", "V", 1),
        ("6", "Besluitlog", "decision", "V", 2),

        # ── Fase 1 ──────────────────────────────────────────────────
        # Stap 7: Onboarding & awareness lijnmanagement
        ("7", "Awareness-materiaal", "document", "V", 0),
        ("7", "Competentiebeoordeling", "document", "V", 1),
        ("7", "Documentbeheerprocedure", "document", "V", 2),
        # Stap 8: Koppeling processen, systemen & verwerkingen
        ("8", "Geintegreerd register", "register", "V", 0),
        ("8", "PII-doorgifte-inventarisatie", "register", "V", 1),
        ("8", "PbD-procedure", "document", "V", 2),
        # Stap 9: Risicoanalyse door lijnmanagement
        ("9", "Risicoregister per afdeling/proces", "register", "V", 0),
        ("9", "BIA (BCMS-track)", "document", "V", 1),
        # Stap 10: Risicobehandeling & controls toewijzen
        ("10", "Risicobehandelplan", "document", "V", 0),
        ("10", "Controls met eigenaren", "register", "V", 1),
        ("10", "Implementatieplan", "document", "V", 2),
        ("10", "BCPs", "document", "V", 3),
        # Stap 11: Statement of Applicability (SoA)
        ("11", "SoA-document incl. ISO 27701 Annex A/B", "document", "V", 0),
        # Stap 12: Monitoring & rapportage inrichten
        ("12", "KPIs", "document", "V", 0),
        ("12", "Rapportagelijnen", "document", "V", 1),
        ("12", "Dashboards", "document", "V", 2),

        # ── Fase 2 ──────────────────────────────────────────────────
        # Stap 13: Interne audit plannen & uitvoeren
        ("13", "Auditprogramma", "document", "V", 0),
        ("13", "Auditrapportages", "document", "V", 1),
        ("13", "BC-oefenrapportage", "document", "V", 2),
        # Stap 14: Management review
        ("14", "Review-rapportage", "document", "V", 0),
        ("14", "Verbeterbeslissingen", "decision", "V", 1),
        # Stap 15: Afwijkingen, incidenten & corrigerende maatregelen
        ("15", "Non-conformiteitenregister", "register", "V", 0),
        ("15", "Correctieve acties", "document", "V", 1),
        # Stap 16: Evidence-verzameling & control-monitoring
        ("16", "Bewijs per control", "document", "V", 0),
        ("16", "Continue monitoring", "document", "V", 1),
        ("16", "Privacy-procedures", "document", "V", 2),
        # Stap 17: PDCA-cyclus formaliseren
        ("17", "Jaarplanning", "document", "V", 0),
        ("17", "Risicoherbeoordeling", "document", "V", 1),
        ("17", "Communicatieprocedures", "document", "V", 2),

        # ── Fase 3 ──────────────────────────────────────────────────
        # Stap 18: Certificeringsgereedheid
        ("18", "Pre-audit rapport", "document", "V", 0),
        ("18", "Gap-remediatie", "document", "V", 1),
        ("18", "Certificeringsaanvraag", "document", "V", 2),
        # Stap 19: Geavanceerde analytics & rapportage
        ("19", "Trendanalyses", "document", "V", 0),
        ("19", "Predictive risk", "document", "V", 1),
        ("19", "Geautomatiseerde rapportages", "document", "V", 2),
        # Stap 20: Externe integraties
        ("20", "Ketenpartner-koppelingen", "document", "V", 0),
        ("20", "Leveranciersportaal", "document", "V", 1),
        # Stap 21: Multi-framework optimalisatie
        ("21", "Cross-mapping controls", "document", "V", 0),
        ("21", "Duplicatie-eliminatie", "document", "V", 1),
        # Stap 22: Benchmarking & kennisdeling
        ("22", "Benchmark-rapportage", "document", "V", 0),
        ("22", "Best practice bibliotheek", "document", "V", 1),
    ]

    for step_num, name, output_type, requirement, sort_order in output_defs:
        op.execute(
            sa.text(
                "INSERT INTO ims_step_outputs "
                "(id, step_id, name, output_type, requirement, sort_order, created_at, updated_at) "
                "VALUES (:id, :step_id, :name, :output_type, :requirement, :sort_order, now(), now())"
            ).bindparams(
                id=_uuid(),
                step_id=steps[step_num],
                name=name,
                output_type=output_type,
                requirement=requirement,
                sort_order=sort_order,
            )
        )


def downgrade() -> None:
    op.execute("DELETE FROM ims_step_outputs")
