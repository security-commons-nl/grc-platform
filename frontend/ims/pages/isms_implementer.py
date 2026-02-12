import reflex as rx
from ims.state.isms_implementer import IsmsImplementerState
from ims.components.layout import layout


def step_header(step_number: int, title: str, description: str) -> rx.Component:
    """Header for each implementation step."""
    return rx.box(
        rx.heading(f"Stap {step_number}: {title}", size="5"),
        rx.text(description, color="gray", size="2", margin_top="4px"),
        border_bottom="1px solid var(--gray-a5)",
        padding_bottom="16px",
        margin_bottom="24px",
    )


def step_1_content() -> rx.Component:
    """Content for Step 1: Context & Organisatie."""
    return rx.vstack(
        step_header(1, "Context & Organisatie", "Bepaal de interne en externe context, stakeholders en scope van het ISMS."),

        # 1. Organization Profile
        rx.card(
            rx.vstack(
                rx.heading("Organisatie Profiel", size="4"),
                rx.text("Basisgegevens van de organisatie.", color="gray", size="2"),
                rx.separator(),
                rx.hstack(
                    rx.text("Sector:", weight="bold"),
                    rx.text(rx.cond(IsmsImplementerState.organization_profile, IsmsImplementerState.organization_profile["sector"], "-")),
                    rx.spacer(),
                    rx.text("Grootte:", weight="bold"),
                    rx.text(rx.cond(IsmsImplementerState.organization_profile, IsmsImplementerState.organization_profile["size"], "-")),
                    width="100%",
                ),
                align_items="start",
                width="100%",
                spacing="3",
            ),
            width="100%",
        ),

        # 2. Context (SWOT)
        rx.heading("Interne & Externe Context (SWOT)", size="4", margin_top="16px"),
        rx.text("Analyseer Sterktes, Zwaktes, Kansen en Bedreigingen (ISO 27001 \u00a74.1).", color="gray", size="2"),
        rx.button("Bewerk SWOT Analyse", variant="outline", on_click=rx.window_alert("SWOT editor coming soon!")),

        # 3. Stakeholders
        rx.heading("Belanghebbenden (Stakeholders)", size="4", margin_top="16px"),
        rx.text("Identificeer belanghebbenden en hun eisen (ISO 27001 \u00a74.2).", color="gray", size="2"),

        # Stakeholder List
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Naam"),
                    rx.table.column_header_cell("Type"),
                    rx.table.column_header_cell("Eisen & Verwachtingen"),
                    rx.table.column_header_cell("Relevantie"),
                    rx.table.column_header_cell("Acties"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    IsmsImplementerState.stakeholders,
                    lambda sh: rx.table.row(
                        rx.table.cell(sh["name"]),
                        rx.table.cell(sh["type"]),
                        rx.table.cell(sh["requirements"]),
                        rx.table.cell(
                            rx.badge(
                                sh["relevance_level"],
                                color_scheme=rx.cond(
                                    sh["relevance_level"] == "High",
                                    "red",
                                    rx.cond(sh["relevance_level"] == "Medium", "orange", "gray"),
                                ),
                            )
                        ),
                        rx.table.cell(
                            rx.icon_button(
                                rx.icon("trash-2", size=16),
                                variant="ghost",
                                color_scheme="red",
                                on_click=lambda: IsmsImplementerState.delete_stakeholder(sh["id"]),
                            )
                        ),
                    ),
                ),
            ),
            variant="surface",
            width="100%",
        ),

        # Add Stakeholder Form
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(rx.icon("plus"), "Stakeholder Toevoegen", margin_top="8px"),
            ),
            rx.dialog.content(
                rx.dialog.title("Nieuwe Stakeholder"),
                rx.dialog.description("Voeg een belanghebbende toe aan het ISMS."),
                rx.flex(
                    rx.text("Naam", size="2", weight="bold"),
                    rx.input(
                        placeholder="Bijv. Klanten, Directie...",
                        value=IsmsImplementerState.new_stakeholder_name,
                        on_change=IsmsImplementerState.set_new_stakeholder_name,
                    ),
                    rx.text("Type", size="2", weight="bold", margin_top="12px"),
                    rx.select(
                        ["Internal", "External", "Partner"],
                        default_value="Internal",
                        value=IsmsImplementerState.new_stakeholder_type,
                        on_change=IsmsImplementerState.set_new_stakeholder_type,
                    ),
                    rx.text("Eisen & Verwachtingen", size="2", weight="bold", margin_top="12px"),
                    rx.text_area(
                        placeholder="Wat verwachten zij van informatiebeveiliging?",
                        value=IsmsImplementerState.new_stakeholder_reqs,
                        on_change=IsmsImplementerState.set_new_stakeholder_reqs,
                    ),
                    rx.text("Relevantie", size="2", weight="bold", margin_top="12px"),
                    rx.select(
                        ["High", "Medium", "Low"],
                        default_value="High",
                        value=IsmsImplementerState.new_stakeholder_rel,
                        on_change=IsmsImplementerState.set_new_stakeholder_rel,
                    ),
                    direction="column",
                    spacing="2",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Annuleren", variant="soft", color_scheme="gray"),
                    ),
                    rx.dialog.close(
                        rx.button("Opslaan", on_click=IsmsImplementerState.add_stakeholder),
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
            ),
        ),

        align_items="start",
        width="100%",
        spacing="4",
    )


def step_2_content() -> rx.Component:
    return rx.vstack(
        step_header(2, "Leiderschap & Beleid", "Toon betrokkenheid van de directie en stel beleid vast."),
        rx.text("Hier komt de content voor Stap 2 (Beleid, Doelstellingen)"),
        align_items="start",
        width="100%",
    )


def step_3_content() -> rx.Component:
    return rx.vstack(
        step_header(3, "Risicomanagement", "Identificeer en analyseer risico's."),
        rx.text("Hier komt de content voor Stap 3 (Risico's, Bedreigingen)"),
        align_items="start",
        width="100%",
    )


def step_4_content() -> rx.Component:
    return rx.vstack(
        step_header(4, "Middelen & Bewustzijn", "Zorg voor voldoende middelen en bewustzijn."),
        rx.text("Hier komt de content voor Stap 4"),
        align_items="start",
        width="100%",
    )


def step_5_content() -> rx.Component:
    return rx.vstack(
        step_header(5, "Beheersing & SoA", "Selecteer en implementeer beheersmaatregelen."),
        rx.text("Hier komt de content voor Stap 5"),
        align_items="start",
        width="100%",
    )


def step_6_content() -> rx.Component:
    return rx.vstack(
        step_header(6, "Evaluatie & Audit", "Monitor en evalueer de prestaties van het ISMS."),
        rx.text("Hier komt de content voor Stap 6"),
        align_items="start",
        width="100%",
    )


def step_7_content() -> rx.Component:
    return rx.vstack(
        step_header(7, "Verbetering (CAPA)", "Corrigeer afwijkingen en verbeter continu."),
        rx.text("Hier komt de content voor Stap 7"),
        align_items="start",
        width="100%",
    )


def stepper_item(step: int, title: str) -> rx.Component:
    """A single item in the stepper navigation."""
    is_active = IsmsImplementerState.active_step == step
    is_completed = IsmsImplementerState.active_step > step

    return rx.vstack(
        rx.box(
            rx.cond(
                is_completed,
                rx.icon("check", color="white", size=16),
                rx.text(
                    str(step),
                    color=rx.cond(is_active, "white", "var(--gray-9)"),
                    weight="bold",
                    size="2",
                ),
            ),
            background=rx.cond(
                is_active,
                "var(--accent-9)",
                rx.cond(is_completed, "var(--green-9)", "var(--gray-a4)"),
            ),
            width="32px",
            height="32px",
            border_radius="50%",
            display="flex",
            align_items="center",
            justify_content="center",
            cursor="pointer",
            _hover={"opacity": "0.8"},
            on_click=lambda: IsmsImplementerState.set_step(step),
        ),
        rx.text(
            title,
            size="1",
            align="center",
            color=rx.cond(is_active, "var(--accent-11)", "var(--gray-11)"),
            weight=rx.cond(is_active, "bold", "regular"),
        ),
        align="center",
        spacing="1",
    )


def stepper_connector(step: int) -> rx.Component:
    """Line connecting stepper items."""
    is_completed = IsmsImplementerState.active_step > step
    return rx.box(
        height="2px",
        flex_grow="1",
        background=rx.cond(is_completed, "var(--green-9)", "var(--gray-a4)"),
        margin_x="4px",
        margin_top="-20px",
    )


def isms_implementer_page() -> rx.Component:
    return layout(
        rx.vstack(
            # Horizontal Stepper
            rx.hstack(
                stepper_item(1, "Context"),
                stepper_connector(1),
                stepper_item(2, "Leiderschap"),
                stepper_connector(2),
                stepper_item(3, "Planning"),
                stepper_connector(3),
                stepper_item(4, "Ondersteuning"),
                stepper_connector(4),
                stepper_item(5, "Uitvoering"),
                stepper_connector(5),
                stepper_item(6, "Evaluatie"),
                stepper_connector(6),
                stepper_item(7, "Verbetering"),
                width="100%",
                align="center",
                margin_bottom="32px",
            ),

            # Main Content Area
            rx.box(
                rx.cond(IsmsImplementerState.active_step == 1, step_1_content()),
                rx.cond(IsmsImplementerState.active_step == 2, step_2_content()),
                rx.cond(IsmsImplementerState.active_step == 3, step_3_content()),
                rx.cond(IsmsImplementerState.active_step == 4, step_4_content()),
                rx.cond(IsmsImplementerState.active_step == 5, step_5_content()),
                rx.cond(IsmsImplementerState.active_step == 6, step_6_content()),
                rx.cond(IsmsImplementerState.active_step == 7, step_7_content()),
                width="100%",
            ),

            width="100%",
            align_items="start",
            spacing="4",
            on_mount=IsmsImplementerState.load_data,
        ),
        title="ISMS Implementatie",
        subtitle="Stapsgewijze implementatiegids",
    )
