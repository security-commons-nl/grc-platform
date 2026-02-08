"""
Mijn Organisatie — Organization profile page with onboarding wizard.

Two modes:
A) Wizard mode: step-by-step form (6 blocks)
B) Profile mode: accordion cards showing filled data
"""
import reflex as rx
from ims.state.organization_profile import OrganizationProfileState
from ims.components.layout import layout


# ---------------------------------------------------------------------------
# Enum options for dropdowns
# ---------------------------------------------------------------------------

ORG_TYPE_OPTIONS = [
    "Gemeente", "Provincie", "Waterschap", "ZBO", "Shared Service Center",
    "Ministerie", "Zorginstelling", "Onderwijsinstelling", "Bedrijf", "Overig",
]
SECTOR_OPTIONS = [
    "Overheid", "Zorg", "Onderwijs", "Financieel",
    "IT-dienstverlening", "Transport", "Energie", "Overig",
]
EMPLOYEE_OPTIONS = ["1-50", "51-200", "201-500", "500+"]
GEO_OPTIONS = ["Lokaal", "Regionaal", "Nationaal", "Internationaal"]
CLOUD_OPTIONS = ["On-premises", "Hybrid", "Cloud-first", "Full-cloud"]
MATURITY_OPTIONS = ["Startend", "Basis", "Gedefinieerd", "Beheerst", "Geoptimaliseerd"]
RISK_OPTIONS = ["Laag", "Midden", "Hoog"]
TRAINING_OPTIONS = ["Geen", "Jaarlijks", "Halfjaarlijks", "Doorlopend"]
DOWNTIME_OPTIONS = ["Uren", "Dag", "Week"]
PROCESSING_COUNT_OPTIONS = ["1-10", "11-50", "51-100", "100+"]
BOOL_OPTIONS = ["true", "false"]

STEP_TITLES = [
    "Identiteit",
    "Governance",
    "IT-Landschap",
    "Privacy",
    "Continuiteit",
    "Mensen & Bewustzijn",
]

STEP_DESCRIPTIONS = [
    "Vertel over je organisatie — type, sector en omvang.",
    "Bestaande certificeringen, frameworks en risicobereidheid.",
    "Hoe ziet je IT-landschap eruit?",
    "Verwerkt je organisatie persoonsgegevens?",
    "Hoe veerkrachtig is je organisatie?",
    "Bewustzijn, training en personeelsbeleid.",
]


# ---------------------------------------------------------------------------
# Form helpers
# ---------------------------------------------------------------------------

def form_select(label: str, value: rx.Var, on_change, options: list, placeholder: str = "Selecteer...") -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.select(
            options,
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def form_bool_select(label: str, value: rx.Var, on_change) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.select(
            ["true", "false"],
            value=value,
            on_change=on_change,
            placeholder="Selecteer...",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def form_input(label: str, value: rx.Var, on_change, placeholder: str = "") -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.input(
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def form_textarea(label: str, value: rx.Var, on_change, placeholder: str = "") -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.text_area(
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            width="100%",
            rows="3",
        ),
        spacing="1",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Wizard steps
# ---------------------------------------------------------------------------

def step_identiteit() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_select("Type organisatie", S.org_type, S.set_org_type, ORG_TYPE_OPTIONS),
        form_select("Sector", S.sector, S.set_sector, SECTOR_OPTIONS),
        form_select("Aantal medewerkers", S.employee_count, S.set_employee_count, EMPLOYEE_OPTIONS),
        form_input("Aantal locaties", S.location_count, S.set_location_count, "bijv. 3"),
        form_select("Geografische scope", S.geographic_scope, S.set_geographic_scope, GEO_OPTIONS),
        form_input("Moederorganisatie", S.parent_organization, S.set_parent_organization, "Optioneel"),
        form_textarea("Kernactiviteiten / diensten", S.core_services, S.set_core_services, "Beschrijf de belangrijkste diensten..."),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def step_governance() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_input("Bestaande certificeringen", S.existing_certifications, S.set_existing_certifications, "bijv. ISO 27001, NEN 7510"),
        form_input("Toepasselijke frameworks", S.applicable_frameworks, S.set_applicable_frameworks, "bijv. BIO, AVG, ISO 27001"),
        form_bool_select("Security Officer aangesteld?", S.has_security_officer, S.set_has_security_officer),
        form_bool_select("Functionaris Gegevensbescherming (FG)?", S.has_dpo, S.set_has_dpo),
        form_select("Governance volwassenheid", S.governance_maturity, S.set_governance_maturity, MATURITY_OPTIONS),
        form_select("Risicobereidheid — Beschikbaarheid", S.risk_appetite_availability, S.set_risk_appetite_availability, RISK_OPTIONS),
        form_select("Risicobereidheid — Integriteit", S.risk_appetite_integrity, S.set_risk_appetite_integrity, RISK_OPTIONS),
        form_select("Risicobereidheid — Vertrouwelijkheid", S.risk_appetite_confidentiality, S.set_risk_appetite_confidentiality, RISK_OPTIONS),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def step_it_landschap() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_select("Cloud strategie", S.cloud_strategy, S.set_cloud_strategy, CLOUD_OPTIONS),
        form_input("Cloud providers", S.cloud_providers, S.set_cloud_providers, "bijv. Azure, AWS, Google"),
        form_select("Aantal werkstations", S.workstation_count, S.set_workstation_count, EMPLOYEE_OPTIONS),
        form_bool_select("Thuiswerken?", S.has_remote_work, S.set_has_remote_work),
        form_bool_select("BYOD (eigen apparaten)?", S.has_byod, S.set_has_byod),
        form_textarea("Kritieke systemen", S.critical_systems, S.set_critical_systems, "Welke systemen zijn bedrijfskritisch?"),
        form_bool_select("IT uitbesteed?", S.outsourced_it, S.set_outsourced_it),
        form_input("Primaire IT-leverancier", S.primary_it_supplier, S.set_primary_it_supplier, "Optioneel"),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def step_privacy() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_bool_select("Verwerkt persoonsgegevens?", S.processes_personal_data, S.set_processes_personal_data),
        form_input("Type betrokkenen", S.data_subject_types, S.set_data_subject_types, "bijv. Burgers, Medewerkers, Cliënten"),
        form_bool_select("Bijzondere categorieën?", S.has_special_categories, S.set_has_special_categories),
        form_bool_select("Internationale doorgifte?", S.international_transfers, S.set_international_transfers),
        form_select("Geschat aantal verwerkingen", S.processing_count_estimate, S.set_processing_count_estimate, PROCESSING_COUNT_OPTIONS),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def step_continuiteit() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_bool_select("Bedrijfscontinuïteitsplan (BCP)?", S.has_bcp, S.set_has_bcp),
        form_bool_select("Incident Response Plan?", S.has_incident_response_plan, S.set_has_incident_response_plan),
        form_select("Maximale toelaatbare downtime", S.max_tolerable_downtime, S.set_max_tolerable_downtime, DOWNTIME_OPTIONS),
        form_input("Aantal kritieke processen", S.critical_process_count, S.set_critical_process_count, "bijv. 5"),
        form_textarea("Belangrijkste afhankelijkheden", S.key_dependencies, S.set_key_dependencies, "Externe diensten, leveranciers..."),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def step_mensen() -> rx.Component:
    S = OrganizationProfileState
    return rx.grid(
        form_bool_select("Bewustwordingsprogramma?", S.has_awareness_program, S.set_has_awareness_program),
        form_bool_select("Screening bij indiensttreding?", S.has_background_checks, S.set_has_background_checks),
        form_select("Trainingsfrequentie", S.training_frequency, S.set_training_frequency, TRAINING_OPTIONS),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


STEP_COMPONENTS = [
    step_identiteit,
    step_governance,
    step_it_landschap,
    step_privacy,
    step_continuiteit,
    step_mensen,
]


# ---------------------------------------------------------------------------
# Wizard stepper
# ---------------------------------------------------------------------------

def wizard_step_indicator(index: int, title: str) -> rx.Component:
    S = OrganizationProfileState
    return rx.hstack(
        rx.cond(
            S.active_step == index,
            rx.box(
                rx.text(str(index + 1), size="2", weight="bold", color="white"),
                width="28px", height="28px", border_radius="full",
                background="var(--accent-9)",
                display="flex", align_items="center", justify_content="center",
            ),
            rx.cond(
                S.active_step > index,
                rx.box(
                    rx.icon("check", size=14, color="white"),
                    width="28px", height="28px", border_radius="full",
                    background="var(--green-9)",
                    display="flex", align_items="center", justify_content="center",
                ),
                rx.box(
                    rx.text(str(index + 1), size="2", color="gray"),
                    width="28px", height="28px", border_radius="full",
                    border="2px solid var(--gray-a6)",
                    display="flex", align_items="center", justify_content="center",
                ),
            ),
        ),
        rx.text(
            title, size="2",
            weight=rx.cond(S.active_step == index, "bold", "regular"),
            color=rx.cond(S.active_step == index, "inherit", "gray"),
            display=rx.breakpoints(initial="none", md="block"),
        ),
        spacing="2",
        align="center",
        cursor="pointer",
        on_click=S.go_to_step(index),
    )


def wizard_stepper() -> rx.Component:
    return rx.hstack(
        *[
            rx.fragment(
                wizard_step_indicator(i, STEP_TITLES[i]),
                rx.cond(
                    i < 5,
                    rx.box(
                        width="24px",
                        height="2px",
                        background="var(--gray-a5)",
                        display=rx.breakpoints(initial="none", md="block"),
                    ),
                ),
            )
            for i in range(6)
        ],
        spacing="1",
        width="100%",
        justify="center",
        flex_wrap="wrap",
        padding="8px 0",
    )


# ---------------------------------------------------------------------------
# Wizard view
# ---------------------------------------------------------------------------

def wizard_view() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        wizard_stepper(),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            rx.match(
                                S.active_step,
                                (0, STEP_TITLES[0]),
                                (1, STEP_TITLES[1]),
                                (2, STEP_TITLES[2]),
                                (3, STEP_TITLES[3]),
                                (4, STEP_TITLES[4]),
                                (5, STEP_TITLES[5]),
                                STEP_TITLES[0],
                            ),
                            size="4",
                        ),
                        rx.text(
                            rx.match(
                                S.active_step,
                                (0, STEP_DESCRIPTIONS[0]),
                                (1, STEP_DESCRIPTIONS[1]),
                                (2, STEP_DESCRIPTIONS[2]),
                                (3, STEP_DESCRIPTIONS[3]),
                                (4, STEP_DESCRIPTIONS[4]),
                                (5, STEP_DESCRIPTIONS[5]),
                                STEP_DESCRIPTIONS[0],
                            ),
                            size="2", color="gray",
                        ),
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.cond(
                        S.wizard_completed,
                        rx.button(
                            "Annuleren",
                            variant="ghost",
                            on_click=S.cancel_wizard,
                        ),
                    ),
                    width="100%",
                ),
                rx.separator(),
                # Step content — use rx.match for step switching
                rx.match(
                    S.active_step,
                    (0, step_identiteit()),
                    (1, step_governance()),
                    (2, step_it_landschap()),
                    (3, step_privacy()),
                    (4, step_continuiteit()),
                    (5, step_mensen()),
                    step_identiteit(),
                ),
                rx.separator(),
                # Navigation buttons
                rx.hstack(
                    rx.cond(
                        S.active_step > 0,
                        rx.button(
                            rx.icon("chevron-left", size=16),
                            "Vorige",
                            variant="outline",
                            on_click=S.prev_step,
                        ),
                        rx.box(),
                    ),
                    rx.spacer(),
                    rx.cond(
                        S.active_step < 5,
                        rx.button(
                            "Opslaan & volgende",
                            rx.icon("chevron-right", size=16),
                            on_click=S.next_step,
                            loading=S.is_saving,
                        ),
                        rx.button(
                            rx.icon("check", size=16),
                            "Profiel opslaan",
                            color_scheme="green",
                            on_click=S.save_all,
                            loading=S.is_saving,
                        ),
                    ),
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Profile view (accordion cards)
# ---------------------------------------------------------------------------

def profile_section(title: str, icon: str, content_fn) -> rx.Component:
    return rx.accordion.item(
        header=rx.hstack(
            rx.icon(icon, size=18),
            rx.text(title, weight="medium"),
            spacing="2",
        ),
        content=rx.box(content_fn(), padding="8px 0"),
    )


def display_field(label: str, value: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="2", color="gray", min_width="180px"),
        rx.cond(
            value != "",
            rx.text(value, size="2"),
            rx.text("—", size="2", color="gray"),
        ),
        spacing="2",
        width="100%",
    )


def bool_display(label: str, value: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="2", color="gray", min_width="180px"),
        rx.cond(
            value == "true",
            rx.badge("Ja", color_scheme="green", variant="soft"),
            rx.cond(
                value == "false",
                rx.badge("Nee", color_scheme="red", variant="soft"),
                rx.text("—", size="2", color="gray"),
            ),
        ),
        spacing="2",
        width="100%",
    )


def profile_identiteit() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        display_field("Type", S.org_type),
        display_field("Sector", S.sector),
        display_field("Medewerkers", S.employee_count),
        display_field("Locaties", S.location_count),
        display_field("Scope", S.geographic_scope),
        display_field("Moederorganisatie", S.parent_organization),
        display_field("Kernactiviteiten", S.core_services),
        spacing="2", width="100%",
    )


def profile_governance() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        display_field("Certificeringen", S.existing_certifications),
        display_field("Frameworks", S.applicable_frameworks),
        bool_display("Security Officer", S.has_security_officer),
        bool_display("FG / DPO", S.has_dpo),
        display_field("Volwassenheid", S.governance_maturity),
        display_field("Risico — Beschikbaarheid", S.risk_appetite_availability),
        display_field("Risico — Integriteit", S.risk_appetite_integrity),
        display_field("Risico — Vertrouwelijkheid", S.risk_appetite_confidentiality),
        spacing="2", width="100%",
    )


def profile_it() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        display_field("Cloud strategie", S.cloud_strategy),
        display_field("Cloud providers", S.cloud_providers),
        display_field("Werkstations", S.workstation_count),
        bool_display("Thuiswerken", S.has_remote_work),
        bool_display("BYOD", S.has_byod),
        display_field("Kritieke systemen", S.critical_systems),
        bool_display("IT uitbesteed", S.outsourced_it),
        display_field("IT-leverancier", S.primary_it_supplier),
        spacing="2", width="100%",
    )


def profile_privacy() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        bool_display("Persoonsgegevens", S.processes_personal_data),
        display_field("Betrokkenen", S.data_subject_types),
        bool_display("Bijzondere categorieën", S.has_special_categories),
        bool_display("Internationale doorgifte", S.international_transfers),
        display_field("Verwerkingen", S.processing_count_estimate),
        spacing="2", width="100%",
    )


def profile_continuity() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        bool_display("BCP", S.has_bcp),
        bool_display("Incident Response", S.has_incident_response_plan),
        display_field("Max downtime", S.max_tolerable_downtime),
        display_field("Kritieke processen", S.critical_process_count),
        display_field("Afhankelijkheden", S.key_dependencies),
        spacing="2", width="100%",
    )


def profile_people() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        bool_display("Bewustwording", S.has_awareness_program),
        bool_display("Screening", S.has_background_checks),
        display_field("Training", S.training_frequency),
        spacing="2", width="100%",
    )


def profile_view() -> rx.Component:
    S = OrganizationProfileState
    return rx.vstack(
        # Completion bar
        rx.hstack(
            rx.text("Profiel compleetheid", size="2", weight="medium"),
            rx.spacer(),
            rx.text(rx.fragment(S.completion_pct, "%"), size="2", weight="bold"),
            width="100%",
        ),
        rx.progress(value=S.completion_pct, width="100%"),

        # Action buttons
        rx.hstack(
            rx.button(
                rx.icon("pencil", size=16),
                "Wizard opnieuw doorlopen",
                variant="outline",
                on_click=S.start_wizard,
            ),
            rx.spacer(),
            width="100%",
        ),

        # Accordion sections
        rx.accordion.root(
            profile_section("Identiteit", "building-2", profile_identiteit),
            profile_section("Governance", "shield", profile_governance),
            profile_section("IT-Landschap", "server", profile_it),
            profile_section("Privacy", "lock", profile_privacy),
            profile_section("Continuïteit", "activity", profile_continuity),
            profile_section("Mensen & Bewustzijn", "users", profile_people),
            type="multiple",
            default_value=["Identiteit"],
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def organization_content() -> rx.Component:
    S = OrganizationProfileState
    return rx.cond(
        S.profile_loaded,
        rx.cond(
            S.show_wizard,
            wizard_view(),
            profile_view(),
        ),
        rx.center(rx.spinner(size="3"), padding="48px"),
    )


def organization_page() -> rx.Component:
    return layout(
        organization_content(),
        title="Mijn Organisatie",
        subtitle="Organisatieprofiel en onboarding wizard",
    )
