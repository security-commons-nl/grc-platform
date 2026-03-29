"""Seed reference data — 22 IMS steps + dependencies + base standards

Revision ID: 003
Revises: 002
Create Date: 2026-03-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def _uuid():
    return str(uuid.uuid4())


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 22 IMS Steps
    # ------------------------------------------------------------------
    steps = {}

    step_data = [
        # (number, phase, name, waarom_nu, required_gremium, is_optional, domain)
        ("1", 0, "Bestuurlijk commitment",
         "Zonder formeel mandaat van het bestuur heeft het tactisch gremium geen autoriteit om besluiten te nemen of middelen in te zetten. Dit is de juridische en bestuurlijke basis voor alles wat volgt.",
         "strategisch", False, None),
        ("2a", 0, "Organisatiecontext vaststellen",
         "De scope, de stakeholders en de PII-rol van de gemeente moeten bekend zijn voordat er iets wordt ingericht. Zonder context kiest iedereen zijn eigen referentiekader.",
         "tactisch", False, None),
        ("2b", 0, "Scope bepalen",
         "De scope bepaalt op welke organisatieonderdelen en domeinen het IMS van toepassing is. Zonder vastgestelde scope kun je geen gap-analyse uitvoeren — je weet niet wat je moet meten.",
         "strategisch", False, None),
        ("3a", 0, "Governance- en beleidsvoorstel opstellen",
         "Nu de context en scope bekend zijn, kan het tactisch gremium uitwerken hoe het IMS wordt bestuurd: wie zit waar, wie rapporteert aan wie, wat is het beleid. Dit is het ontwerp — nog geen besluit.",
         "tactisch", False, None),
        ("3b", 0, "Governance en beleid vaststellen",
         "Het strategisch gremium stelt het governance-voorstel van het tactisch gremium formeel vast. Pas na dit besluit is de structuur gezaghebbend en kan lijnmanagement straks worden aangesproken op hun rol.",
         "strategisch", False, None),
        ("4", 0, "Gap-analyse",
         "Met governance vastgesteld en scope duidelijk kan de nulmeting beginnen: waar staan we nu ten opzichte van de norm? Deze meting is de basis voor alles wat daarna geprioriteerd wordt.",
         "tactisch", False, None),
        ("5", 0, "Registers & risicobeoordeling",
         "De gap-analyse laat zien wat ontbreekt. Nu worden de basisregisters opgebouwd en de eerste risico's in kaart gebracht — zodat stap 6 controls kan selecteren op basis van echte risico's, niet op aannames.",
         "tactisch", False, None),
        ("6", 0, "Normenkader & kerncontrols",
         "Het normenkader en de minimale werkset controls zijn de randvoorwaarde voor Fase 1. Zonder dit weet lijnmanagement niet op basis van welke maatregelen ze moeten werken.",
         "tactisch", False, None),
        ("7", 1, "Onboarding & awareness lijnmanagement",
         "Het normenkader staat vast. Nu moet lijnmanagement weten wat er van hen verwacht wordt en in welke taal het IMS communiceert. Zonder awareness voeren ze stap 9 uit zonder te begrijpen waarom.",
         "tactisch", False, None),
        ("8", 1, "Koppeling processen, systemen & verwerkingen",
         "Risicoanalyse (stap 9) vereist inzicht in welke processen welke systemen gebruiken en welke persoonsgegevens daarin zitten. Dit register legt die koppeling — zonder deze basis is de risicoanalyse incompleet.",
         "tactisch", False, None),
        ("9", 1, "Risicoanalyse door lijnmanagement",
         "Het register is beschikbaar, de methodiek staat vast, lijnmanagement is onboarded. Nu kan de daadwerkelijke beoordeling plaatsvinden: wat zijn de risico's per afdeling/proces?",
         "lijnmanagement", False, None),
        ("10", 1, "Risicobehandeling & controls toewijzen",
         "De risico's zijn bekend. Nu wordt per risico bepaald: accepteren, mitigeren, overdragen of vermijden — en worden controls en eigenaren toegewezen. Zonder dit stap blijft het risicoregister een lijst zonder actie.",
         "tactisch", False, None),
        ("11", 1, "Statement of Applicability (SoA)",
         "Met de risicoanalyse en controls in kaart kan worden vastgesteld welke ISO-controls van toepassing zijn en waarom. De SoA is het formele bewijs van een weloverwogen norm-keuze — vereist voor certificering.",
         "tactisch", False, None),
        ("12", 1, "Monitoring & rapportage inrichten",
         "Het IMS is ingericht. Nu moet de infrastructuur staan om het ook te kunnen bewaken: KPI's, rapportagelijnen, dashboards. Zonder dit kan het strategisch gremium in Fase 2 niet sturen op resultaten.",
         "tactisch", False, None),
        ("13", 2, "Interne audit plannen & uitvoeren",
         "Het IMS draait. Nu moet onafhankelijk worden getoetst of de controls ook daadwerkelijk werken. De audit levert de input voor de management review en toont aan dat het systeem zichzelf bewaakt.",
         "tactisch", False, None),
        ("14", 2, "Management review",
         "De auditresultaten, risicostatussen en KPI's zijn beschikbaar. Het strategisch gremium beoordeelt het geheel en neemt verbeterbeslissingen. Dit is het moment waarop de PDCA-cirkel sluit op strategisch niveau.",
         "strategisch", False, None),
        ("15", 2, "Afwijkingen, incidenten & corrigerende maatregelen",
         "Afwijkingen en incidenten doen zich voor wanneer ze zich voordoen — niet op een gepland moment. Dit is de event-driven stap die ervoor zorgt dat problemen worden geregistreerd, geanalyseerd en opgevolgd.",
         "discipline_eigenaar", False, None),
        ("16", 2, "Evidence-verzameling & control-monitoring",
         "Controls zijn toegewezen en geimplementeerd. Nu moet worden bewezen dat ze ook werken: bewijs per control, continue monitoring, privacy-procedures actueel houden. Zonder evidence is een audit niet te doorstaan.",
         "discipline_eigenaar", False, None),
        ("17", 2, "PDCA-cyclus formaliseren",
         "Aan het einde van de cyclus wordt de volgende cyclus gepland. Stap 17 zorgt dat de PDCA niet stopt na een ronde maar structureel verankerd is in de jaarplanning.",
         "tactisch", False, None),
        ("18", 3, "Certificeringsgereedheid",
         "De organisatie wil externe validatie van het IMS. Een pre-audit brengt resterende gaps in beeld zodat de certificeringsaanvraag met vertrouwen kan worden ingediend.",
         "strategisch", True, None),
        ("19", 3, "Geavanceerde analytics & rapportage",
         "Het IMS heeft genoeg historische data opgebouwd om trends te zien. Predictive risk en geautomatiseerde rapportages maken het IMS proactief in plaats van reactief.",
         "tactisch", True, None),
        ("20", 3, "Externe integraties",
         "De organisatie werkt intensief samen met ketenpartners of leveranciers. Koppelingen maken data-uitwisseling gestructureerd en controleerbaar in plaats van handmatig.",
         "tactisch", True, None),
        ("21", 3, "Multi-framework optimalisatie",
         "De organisatie werkt met meerdere normen (BIO, AVG, BCM). Cross-mapping elimineert dubbel werk: een control dekt meerdere normeisen.",
         "tactisch", True, None),
        ("22", 3, "Benchmarking & kennisdeling",
         "Meerdere gemeenten gebruiken het platform. Vergelijking en kennisdeling versnellen volwassenheid in de regio en maken gezamenlijk leren mogelijk.",
         "strategisch", True, None),
    ]

    for number, phase, name, waarom_nu, gremium, is_optional, domain in step_data:
        step_id = _uuid()
        steps[number] = step_id
        op.execute(
            sa.text(
                "INSERT INTO ims_steps (id, number, phase, name, waarom_nu, required_gremium, is_optional, domain, created_at, updated_at) "
                "VALUES (:id, :number, :phase, :name, :waarom_nu, :gremium, :optional, :domain, now(), now())"
            ).bindparams(
                id=step_id, number=number, phase=phase, name=name,
                waarom_nu=waarom_nu, gremium=gremium, optional=is_optional, domain=domain,
            )
        )

    # ------------------------------------------------------------------
    # Step dependencies (B = blokkerend, W = waarschuwing)
    # ------------------------------------------------------------------
    dependencies = [
        # Fase 0 dependencies
        ("2a", "1", "B"),   # Context needs commitment
        ("2b", "1", "B"),   # Scope needs commitment
        ("2b", "2a", "B"),  # Scope needs context
        ("3a", "2b", "B"),  # Governance needs scope
        ("3b", "3a", "B"),  # Governance approval needs proposal
        ("4", "3b", "B"),   # Gap-analyse needs governance
        ("5", "4", "B"),    # Registers need gap-analyse
        ("6", "5", "B"),    # Normenkader needs registers
        # Fase 1 dependencies
        ("7", "6", "B"),    # Onboarding needs normenkader
        ("8", "7", "W"),    # Koppeling benefits from onboarding
        ("9", "8", "B"),    # Risicoanalyse needs registers
        ("9", "7", "B"),    # Risicoanalyse needs onboarding
        ("10", "9", "B"),   # Behandeling needs analyse
        ("11", "10", "B"),  # SoA needs behandeling
        ("12", "11", "W"),  # Monitoring benefits from SoA
        # Fase 2 dependencies
        ("13", "12", "W"),  # Audit benefits from monitoring
        ("13", "11", "B"),  # Audit needs SoA
        ("14", "13", "B"),  # Management review needs audit
        ("15", "11", "W"),  # Incidenten can start after SoA
        ("16", "10", "B"),  # Evidence needs controls assigned
        ("17", "14", "B"),  # PDCA formalisatie needs management review
        # Fase 3 dependencies
        ("18", "17", "B"),  # Certificering needs PDCA cycle done
        ("19", "17", "W"),  # Analytics benefits from full cycle
        ("20", "17", "W"),  # Integraties benefits from full cycle
        ("21", "17", "W"),  # Multi-framework benefits from full cycle
        ("22", "18", "W"),  # Benchmarking benefits from certification readiness
    ]

    for step_num, depends_on_num, dep_type in dependencies:
        dep_id = _uuid()
        op.execute(
            sa.text(
                "INSERT INTO ims_step_dependencies (id, step_id, depends_on_step_id, dependency_type, created_at, updated_at) "
                "VALUES (:id, :step_id, :depends_on, :dep_type, now(), now())"
            ).bindparams(
                id=dep_id, step_id=steps[step_num],
                depends_on=steps[depends_on_num], dep_type=dep_type,
            )
        )

    # ------------------------------------------------------------------
    # Default tenant + region + admin user (development)
    # ------------------------------------------------------------------
    default_id = "00000000-0000-0000-0000-000000000001"
    region_id = _uuid()
    admin_user_id = "00000000-0000-0000-0000-000000000002"

    op.execute(sa.text(
        "INSERT INTO regions (id, name, created_at, updated_at) "
        "VALUES (:id, 'Voorbeeldregio', now(), now())"
    ).bindparams(id=region_id))

    op.execute(sa.text(
        "INSERT INTO tenants (id, name, type, region_id, is_active, created_at, updated_at) "
        "VALUES (:id, 'Voorbeeldgemeente', 'centrum', :region_id, true, now(), now())"
    ).bindparams(id=default_id, region_id=region_id))

    op.execute(sa.text(
        "UPDATE regions SET centrum_tenant_id = :tenant_id WHERE id = :region_id"
    ).bindparams(tenant_id=default_id, region_id=region_id))

    op.execute(sa.text(
        "INSERT INTO users (id, tenant_id, external_id, name, email, is_active, created_at, updated_at) "
        "VALUES (:id, :tenant_id, 'dev-admin', 'Beheerder (dev)', 'admin@ims.dev', true, now(), now())"
    ).bindparams(id=admin_user_id, tenant_id=default_id))

    op.execute(sa.text(
        "INSERT INTO user_tenant_roles (id, user_id, tenant_id, role, created_at, updated_at) "
        "VALUES (:id, :user_id, :tenant_id, 'admin', now(), now())"
    ).bindparams(id=_uuid(), user_id=admin_user_id, tenant_id=default_id))

    # ------------------------------------------------------------------
    # Base standards (normenkaders)
    # ------------------------------------------------------------------
    standards = [
        ("BIO", "2.0", "2020-01-01", "actief", "ISMS"),
        ("ISO 27001", "2022", "2022-10-25", "actief", "ISMS"),
        ("ISO 27701", "2019", "2019-08-01", "actief", "PIMS"),
        ("ISO 22301", "2019", "2019-10-31", "actief", "BCMS"),
        ("AVG", "2016", "2016-04-27", "actief", "PIMS"),
    ]

    for name, version, published, status, domain in standards:
        std_id = _uuid()
        op.execute(
            sa.text(
                "INSERT INTO ims_standards (id, name, version, published_at, status, domain, created_at, updated_at) "
                "VALUES (:id, :name, :version, :published, :status, :domain, now(), now())"
            ).bindparams(
                id=std_id, name=name, version=version,
                published=published, status=status, domain=domain,
            )
        )


def downgrade() -> None:
    op.execute("DELETE FROM user_tenant_roles")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM tenants")
    op.execute("DELETE FROM regions")
    op.execute("DELETE FROM ims_step_dependencies")
    op.execute("DELETE FROM ims_steps")
    op.execute("DELETE FROM ims_standards")
