import reflex as rx
from ims.state.isms_implementer import IsmsImplementerState
from ims.components.layout import layout


def step_header(step_number: int, title: str, description: str = "") -> rx.Component:
    """Header for each implementation step."""
    children = [rx.heading(f"Stap {step_number}: {title}", size="5")]
    if description:
        children.append(rx.text(description, color="gray", size="2", margin_top="4px"))
    return rx.box(
        *children,
        border_bottom="1px solid var(--gray-a5)",
        padding_bottom="16px",
        margin_bottom="24px",
    )


def _activity_check(label: str, is_done: rx.Var) -> rx.Component:
    """Single activity check item."""
    return rx.hstack(
        rx.icon(
            "circle-check",
            color=rx.cond(is_done, "var(--green-9)", "var(--gray-a6)"),
            size=18,
        ),
        rx.text(
            label,
            size="2",
            color=rx.cond(is_done, "var(--gray-12)", "var(--gray-10)"),
            text_decoration=rx.cond(is_done, "line-through", "none"),
        ),
        align="center",
        spacing="2",
    )


def context_dashboard() -> rx.Component:
    """Dashboard showing progress for Context phase."""
    return rx.box(
        rx.vstack(
            # Accent bar
            rx.box(
                width="100%",
                height="3px",
                background="var(--indigo-9)",
                border_radius="var(--radius-3) var(--radius-3) 0 0",
            ),
            rx.vstack(
                # Header
                rx.hstack(
                    rx.box(
                        rx.icon("gauge", size=20, color="white"),
                        background="var(--indigo-9)",
                        padding="8px",
                        border_radius="var(--radius-2)",
                    ),
                    rx.text("Fase Voortgang", size="3", weight="bold"),
                    rx.spacer(),
                    rx.badge(
                        rx.fragment(IsmsImplementerState.context_progress.to(str), "%"),
                        color_scheme=rx.cond(
                            IsmsImplementerState.context_progress >= 100,
                            "green",
                            rx.cond(IsmsImplementerState.context_progress > 0, "blue", "gray"),
                        ),
                        variant="soft",
                        size="2",
                    ),
                    width="100%",
                    align="center",
                ),
                # Progress bar
                rx.box(
                    rx.box(
                        width=rx.cond(
                            IsmsImplementerState.context_progress > 0,
                            IsmsImplementerState.context_progress.to(str) + "%",
                            "0%",
                        ),
                        height="100%",
                        background="var(--indigo-9)",
                        border_radius="4px",
                        transition="width 0.5s ease",
                    ),
                    width="100%",
                    height="8px",
                    background="var(--gray-a4)",
                    border_radius="4px",
                    overflow="hidden",
                ),
                rx.divider(),
                # Activities checklist
                rx.text("Activiteiten", size="2", weight="bold", color="var(--gray-11)"),
                _activity_check("1. Interne en externe analyse", IsmsImplementerState.has_context_issues),
                _activity_check("2. Stakeholders identificeren, analyseren en adresseren", IsmsImplementerState.has_stakeholders),
                _activity_check("3. Vaststellen toepassingsgebied (scope)", IsmsImplementerState.has_scope),
                spacing="3",
                width="100%",
                padding="20px",
            ),
            spacing="0",
            width="100%",
        ),
        background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
        border="1px solid var(--gray-a4)",
        border_radius="var(--radius-3)",
        overflow="hidden",
        width="100%",
    )


def _swot_quadrant_box(
    letter: str,
    title: str,
    bg: str,
    text_color: str,
    content: rx.Var,
    on_click_handler,
) -> rx.Component:
    """Single clickable SWOT quadrant."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(title, size="3", weight="bold", color=text_color),
                rx.spacer(),
                rx.text(letter, size="7", weight="bold", color=text_color, opacity="0.25"),
                width="100%",
                align="start",
            ),
            rx.cond(
                content != "",
                rx.text(content, size="2", color=text_color, opacity="0.85", white_space="pre-wrap"),
                rx.text(
                    "Klik om in te vullen...",
                    size="2",
                    color=text_color,
                    opacity="0.4",
                    font_style="italic",
                ),
            ),
            spacing="2",
            width="100%",
            height="100%",
        ),
        background=bg,
        border_radius="var(--radius-3)",
        padding="20px",
        min_height="180px",
        cursor="pointer",
        _hover={"opacity": "0.85", "transform": "scale(1.01)"},
        transition="all 0.15s ease",
        on_click=on_click_handler,
    )


def swot_grid() -> rx.Component:
    """Visual 2×2 SWOT analysis grid."""
    return rx.vstack(
        rx.hstack(
            rx.icon("grid-2x2", size=20, color="var(--indigo-9)"),
            rx.text("SWOT Analyse", size="3", weight="bold"),
            rx.spacer(),
            rx.text("Klik op een vak om te bewerken", size="1", color="var(--gray-9)"),
            width="100%",
            align="center",
        ),
        rx.grid(
            _swot_quadrant_box(
                "S", "Strengths", "var(--blue-a3)", "var(--blue-11)",
                IsmsImplementerState.swot_strengths,
                IsmsImplementerState.open_swot_edit("strengths"),
            ),
            _swot_quadrant_box(
                "W", "Weaknesses", "var(--orange-a3)", "var(--orange-11)",
                IsmsImplementerState.swot_weaknesses,
                IsmsImplementerState.open_swot_edit("weaknesses"),
            ),
            _swot_quadrant_box(
                "O", "Opportunities", "var(--green-a3)", "var(--green-11)",
                IsmsImplementerState.swot_opportunities,
                IsmsImplementerState.open_swot_edit("opportunities"),
            ),
            _swot_quadrant_box(
                "T", "Threats", "var(--red-a3)", "var(--red-11)",
                IsmsImplementerState.swot_threats,
                IsmsImplementerState.open_swot_edit("threats"),
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def swot_edit_dialog() -> rx.Component:
    """Dialog for editing a SWOT quadrant."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.match(
                    IsmsImplementerState.swot_editing,
                    ("strengths", "Strengths bewerken"),
                    ("weaknesses", "Weaknesses bewerken"),
                    ("opportunities", "Opportunities bewerken"),
                    ("threats", "Threats bewerken"),
                    "SWOT bewerken",
                ),
            ),
            rx.dialog.description(
                "Voer de items in, één per regel.",
            ),
            rx.text_area(
                placeholder="Voer hier de items in...",
                value=IsmsImplementerState.swot_edit_text,
                on_change=IsmsImplementerState.set_swot_edit_text,
                min_height="200px",
                width="100%",
                auto_focus=True,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=IsmsImplementerState.close_swot_edit,
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Opslaan",
                        on_click=IsmsImplementerState.save_swot_edit,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="500px",
        ),
        open=IsmsImplementerState.swot_editing != "",
    )


def step_1_content() -> rx.Component:
    """Content for Step 1: Context & Organisatie."""
    return rx.vstack(
        step_header(1, "Context & Organisatie", ""),

        # Inleidende banner
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color="var(--indigo-4)", flex_shrink="0"),
                rx.text(
                    "De fase 'context van de organisatie' omvat het uitvoeren van een "
                    "interne en externe analyse, het identificeren en analyseren van de "
                    "behoeften, eisen en verwachtingen van relevante belanghebbenden en "
                    "het bepalen welke daarvan worden geadresseerd binnen het "
                    "managementsysteem. Op basis hiervan wordt het toepassingsgebied "
                    "(scope) van het ISMS vastgesteld.",
                    size="2",
                    color="var(--indigo-3)",
                    line_height="1.7",
                ),
                spacing="3",
                align="start",
            ),
            background="linear-gradient(135deg, var(--indigo-9), var(--indigo-11))",
            border_radius="var(--radius-3)",
            padding="20px 24px",
            width="100%",
        ),

        # Dashboard
        context_dashboard(),

        # ── Sectie 1: Interne en externe analyse ──────────────────
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--blue-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("search", size=18, color="white"),
                            background="var(--blue-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.vstack(
                            rx.text("1. Interne en externe analyse", size="3", weight="bold"),
                            rx.text(
                                "Het uitvoeren van een interne en externe analyse, waarbij het "
                                "SWOT-instrument wordt gebruikt. Om de SWOT kwalitatief en volledig "
                                "in te vullen kunnen aanvullende methodieken worden toegepast, zoals "
                                "een PEST-analyse voor externe ontwikkelingen en het McKinsey "
                                "7S-model voor de interne analyse.",
                                size="2",
                                color="var(--gray-10)",
                                line_height="1.6",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        width="100%",
                        align="start",
                        spacing="3",
                    ),
                    rx.divider(),
                    swot_grid(),
                    spacing="4",
                    width="100%",
                    padding="20px",
                ),
                spacing="0",
                width="100%",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--gray-a4)",
            border_radius="var(--radius-3)",
            overflow="hidden",
            width="100%",
        ),

        # SWOT edit dialog
        swot_edit_dialog(),

        # ── Sectie 2: Stakeholders ────────────────────────────────
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--violet-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("users", size=18, color="white"),
                            background="var(--violet-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.vstack(
                            rx.text("2. Stakeholders identificeren, analyseren en adresseren", size="3", weight="bold"),
                            rx.text(
                                "Het identificeren en analyseren van de behoeften, eisen en "
                                "verwachtingen van relevante belanghebbenden en het bepalen welke "
                                "daarvan binnen het managementsysteem worden geadresseerd. "
                                "Onderstaande tabel wordt gebruikt om in één oogopslag inzichtelijk "
                                "te maken hoe met de verschillende stakeholders wordt omgegaan.",
                                size="2",
                                color="var(--gray-10)",
                                line_height="1.6",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        width="100%",
                        align="start",
                        spacing="3",
                    ),
                    rx.divider(),
                    # Stakeholder table
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
                    # Add stakeholder button
                    rx.dialog.root(
                        rx.dialog.trigger(
                            rx.button(rx.icon("plus", size=14), "Stakeholder Toevoegen", variant="soft", size="2"),
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
                    spacing="4",
                    width="100%",
                    padding="20px",
                ),
                spacing="0",
                width="100%",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--gray-a4)",
            border_radius="var(--radius-3)",
            overflow="hidden",
            width="100%",
        ),

        # ── Sectie 3: Toepassingsgebied (scope) ──────────────────
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--green-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("target", size=18, color="white"),
                            background="var(--green-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.vstack(
                            rx.text("3. Vaststellen toepassingsgebied (scope)", size="3", weight="bold"),
                            rx.text(
                                "Het vaststellen van het toepassingsgebied (scope) van het ISMS. "
                                "Hoewel de scope door de organisatie zelf kan worden bepaald, stelt "
                                "de BIO2 aanvullend op ISO 27001 dat deze minimaal alle kritische "
                                "processen moet omvatten. Daarom worden de kritische processen als "
                                "uitgangspunt genomen. Hieronder vallen tevens alle onderliggende "
                                "taakspecifieke applicaties, bedrijfsmiddelen (assets), de gehele "
                                "IT-infrastructuur (van applicaties tot en met netwerkcomponenten "
                                "zoals routers) en de fysieke locaties en gebouwen waarvan deze "
                                "kritische processen afhankelijk zijn.",
                                size="2",
                                color="var(--gray-10)",
                                line_height="1.6",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        width="100%",
                        align="start",
                        spacing="3",
                    ),
                    rx.divider(),
                    # Kritische processen
                    rx.vstack(
                        rx.hstack(
                            rx.icon("list-checks", size=16, color="var(--green-9)"),
                            rx.text("Kritische processen binnen het toepassingsgebied", size="2", weight="bold"),
                            spacing="2",
                            align="center",
                        ),
                        rx.cond(
                            IsmsImplementerState.critical_processes.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    IsmsImplementerState.critical_processes,
                                    lambda p, idx: rx.hstack(
                                        rx.badge(
                                            (idx + 1).to(str),
                                            color_scheme="green",
                                            variant="soft",
                                            size="1",
                                        ),
                                        rx.text(p, size="2"),
                                        rx.spacer(),
                                        rx.icon_button(
                                            rx.icon("trash-2", size=14),
                                            variant="ghost",
                                            color_scheme="red",
                                            size="1",
                                            on_click=IsmsImplementerState.delete_critical_process(idx),
                                        ),
                                        width="100%",
                                        align="center",
                                        padding_y="4px",
                                    ),
                                ),
                                spacing="1",
                                width="100%",
                            ),
                            rx.text(
                                "Nog geen kritische processen toegevoegd.",
                                size="2",
                                color="var(--gray-9)",
                                font_style="italic",
                            ),
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="Naam van het kritische proces...",
                                value=IsmsImplementerState.new_critical_process,
                                on_change=IsmsImplementerState.set_new_critical_process,
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("plus", size=14),
                                "Toevoegen",
                                variant="soft",
                                color_scheme="green",
                                size="2",
                                on_click=IsmsImplementerState.add_critical_process,
                            ),
                            width="100%",
                            spacing="2",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.divider(),
                    # Uitsluitingen
                    rx.vstack(
                        rx.hstack(
                            rx.icon("shield-off", size=16, color="var(--orange-9)"),
                            rx.text("Buiten het toepassingsgebied", size="2", weight="bold"),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            "Beschrijf hier eventuele onderdelen die buiten het toepassingsgebied van het ISMS vallen.",
                            size="2",
                            color="var(--gray-10)",
                        ),
                        rx.text_area(
                            placeholder="Bijv. specifieke afdelingen, locaties of systemen die niet in scope zijn...",
                            value=IsmsImplementerState.scope_exclusions,
                            on_change=IsmsImplementerState.set_scope_exclusions,
                            min_height="100px",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                    padding="20px",
                ),
                spacing="0",
                width="100%",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--gray-a4)",
            border_radius="var(--radius-3)",
            overflow="hidden",
            width="100%",
        ),

        align_items="start",
        width="100%",
        spacing="5",
    )


def step_bc_content() -> rx.Component:
    """Content for preparation step: Business Case."""
    return rx.vstack(
        step_header(0, "Business Case", ""),
        # Inleidende banner
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color="var(--amber-4)", flex_shrink="0"),
                rx.text(
                    "De business case vormt de zakelijke rechtvaardiging voor het opzetten "
                    "van een ISMS. Hierin wordt beschreven waarom informatiebeveiliging "
                    "noodzakelijk is, welke kosten en baten worden verwacht, en hoe het "
                    "ISMS bijdraagt aan de strategische doelen van de organisatie.",
                    size="2",
                    color="var(--amber-3)",
                    line_height="1.7",
                ),
                spacing="3",
                align="start",
            ),
            background="linear-gradient(135deg, var(--amber-9), var(--amber-11))",
            border_radius="var(--radius-3)",
            padding="20px 24px",
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--amber-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("briefcase", size=18, color="white"),
                            background="var(--amber-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.text("Business Case", size="3", weight="bold"),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(),
                    rx.text(
                        "De business case is nog in ontwikkeling. Hier komt een gestructureerd "
                        "formulier voor de zakelijke rechtvaardiging van het ISMS.",
                        size="2",
                        color="var(--gray-10)",
                        font_style="italic",
                    ),
                    spacing="4",
                    width="100%",
                    padding="20px",
                ),
                spacing="0",
                width="100%",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--gray-a4)",
            border_radius="var(--radius-3)",
            overflow="hidden",
            width="100%",
        ),
        align_items="start",
        width="100%",
        spacing="5",
    )


def step_pp_content() -> rx.Component:
    """Content for preparation step: Projectplan / Implementatieplan."""
    return rx.vstack(
        step_header(0, "Projectplan / Implementatieplan", ""),
        # Inleidende banner
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color="var(--amber-4)", flex_shrink="0"),
                rx.text(
                    "Het projectplan beschrijft hoe het ISMS wordt geïmplementeerd: de scope "
                    "van het project, de planning, mijlpalen, benodigde resources, rollen en "
                    "verantwoordelijkheden, en de communicatiestrategie. Dit plan is de leidraad "
                    "voor het gehele implementatietraject.",
                    size="2",
                    color="var(--amber-3)",
                    line_height="1.7",
                ),
                spacing="3",
                align="start",
            ),
            background="linear-gradient(135deg, var(--amber-9), var(--amber-11))",
            border_radius="var(--radius-3)",
            padding="20px 24px",
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--amber-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("gantt-chart", size=18, color="white"),
                            background="var(--amber-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.text("Projectplan / Implementatieplan", size="3", weight="bold"),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(),
                    rx.text(
                        "Het projectplan is nog in ontwikkeling. Hier komt een overzicht van "
                        "de planning, mijlpalen, resources en verantwoordelijkheden.",
                        size="2",
                        color="var(--gray-10)",
                        font_style="italic",
                    ),
                    spacing="4",
                    width="100%",
                    padding="20px",
                ),
                spacing="0",
                width="100%",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--gray-a4)",
            border_radius="var(--radius-3)",
            overflow="hidden",
            width="100%",
        ),
        align_items="start",
        width="100%",
        spacing="5",
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


def stepper_item(step: int, title: str, label: str = "", color: str = "accent") -> rx.Component:
    """A single item in the stepper navigation."""
    is_active = IsmsImplementerState.active_step == step
    is_completed = IsmsImplementerState.active_step > step
    display_label = label if label else str(step)

    return rx.vstack(
        rx.box(
            rx.cond(
                is_completed,
                rx.icon("check", color="white", size=16),
                rx.text(
                    display_label,
                    color=rx.cond(is_active, "white", "var(--gray-9)"),
                    weight="bold",
                    size="2",
                ),
            ),
            background=rx.cond(
                is_active,
                f"var(--{color}-9)",
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
            on_click=IsmsImplementerState.set_step(step),
        ),
        rx.text(
            title,
            size="1",
            align="center",
            color=rx.cond(is_active, f"var(--{color}-11)", "var(--gray-11)"),
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


def stepper_divider() -> rx.Component:
    """Visual separator between preparation and ISMS steps."""
    return rx.box(
        width="2px",
        height="48px",
        background="var(--gray-a6)",
        margin_x="8px",
        border_radius="1px",
    )


def isms_implementer_page() -> rx.Component:
    return layout(
        rx.vstack(
            # Horizontal Stepper with preparation + ISMS sections
            rx.vstack(
                # Phase labels
                rx.hstack(
                    rx.badge("Voorbereiding", color_scheme="amber", variant="soft", size="1"),
                    rx.spacer(),
                    rx.badge("Implementatiestappen", color_scheme="indigo", variant="soft", size="1"),
                    width="100%",
                ),
                rx.hstack(
                    # Preparation steps (amber)
                    stepper_item(-1, "Business Case", "BC", "amber"),
                    stepper_connector(-1),
                    stepper_item(0, "Projectplan", "PP", "amber"),
                    # Visual divider
                    stepper_divider(),
                    # ISMS steps (accent/indigo)
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
                ),
                spacing="2",
                width="100%",
                margin_bottom="32px",
            ),

            # Main Content Area
            rx.box(
                rx.cond(IsmsImplementerState.active_step == -1, step_bc_content()),
                rx.cond(IsmsImplementerState.active_step == 0, step_pp_content()),
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
        title="ISMS Dashboard",
        subtitle="Stapsgewijze implementatiegids",
    )
