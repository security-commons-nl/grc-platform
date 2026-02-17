import reflex as rx
from ims.state.isms_implementer import IsmsImplementerState
from ims.components.layout import layout


def step_header(step_number: int, title: str, description: str = "") -> rx.Component:
    """Header for each implementation step."""
    heading_text = f"Stap {step_number}: {title}" if step_number >= 1 else title
    children = [rx.heading(heading_text, size="5")]
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


def phase_dashboard(
    accent: str,
    progress_var: rx.Var,
    activities: list,
) -> rx.Component:
    """Generic phase progress dashboard. Used on every step."""
    return rx.box(
        rx.vstack(
            rx.box(
                width="100%",
                height="3px",
                background=f"var(--{accent}-9)",
                border_radius="var(--radius-3) var(--radius-3) 0 0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("gauge", size=20, color="white"),
                        background=f"var(--{accent}-9)",
                        padding="8px",
                        border_radius="var(--radius-2)",
                    ),
                    rx.text("Fase Voortgang", size="3", weight="bold"),
                    rx.spacer(),
                    rx.badge(
                        rx.fragment(progress_var.to(str), "%"),
                        color_scheme=rx.cond(
                            progress_var >= 100,
                            "green",
                            rx.cond(progress_var > 0, "blue", "gray"),
                        ),
                        variant="soft",
                        size="2",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(
                    rx.box(
                        width=rx.cond(
                            progress_var > 0,
                            progress_var.to(str) + "%",
                            "0%",
                        ),
                        height="100%",
                        background=f"var(--{accent}-9)",
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
                rx.text("Activiteiten", size="2", weight="bold", color="var(--gray-11)"),
                *[_activity_check(label, var) for label, var in activities],
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
        on_open_change=IsmsImplementerState.handle_swot_dialog_change,
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
        phase_dashboard(
            "indigo",
            IsmsImplementerState.context_progress,
            [
                ("1. Interne en externe analyse", IsmsImplementerState.has_context_issues),
                ("2. Stakeholders identificeren, analyseren en adresseren", IsmsImplementerState.has_stakeholders),
                ("3. Vaststellen toepassingsgebied (scope)", IsmsImplementerState.has_scope),
            ],
        ),

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


def _bmc_block(
    title: str, icon: str, content: rx.Var, color: str, on_click_handler, min_h: str = "200px",
) -> rx.Component:
    """Single clickable BMC block."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=14, color=f"var(--{color}-9)"),
                rx.text(title, size="1", weight="bold", color=f"var(--{color}-11)"),
                spacing="1",
                align="center",
            ),
            rx.text(
                content, size="1", color="var(--gray-11)", white_space="pre-wrap", line_height="1.5",
            ),
            spacing="2",
            width="100%",
        ),
        background=f"var(--{color}-a2)",
        border=f"1px solid var(--{color}-a4)",
        border_radius="var(--radius-2)",
        padding="12px",
        min_height=min_h,
        cursor="pointer",
        _hover={"border_color": f"var(--{color}-a7)", "background": f"var(--{color}-a3)"},
        transition="all 0.15s ease",
        on_click=on_click_handler,
        overflow="hidden",
    )


def bmc_canvas() -> rx.Component:
    """Visual Business Model Canvas grid."""
    return rx.box(
        rx.vstack(
            rx.box(width="100%", height="3px", background="var(--indigo-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
            rx.vstack(
                # Header
                rx.hstack(
                    rx.box(
                        rx.icon("layout-grid", size=18, color="white"),
                        background="var(--indigo-9)",
                        padding="8px",
                        border_radius="var(--radius-2)",
                    ),
                    rx.vstack(
                        rx.text("Business Model Canvas", size="3", weight="bold"),
                        rx.text("ISMS-proces — Gemeente", size="1", color="var(--gray-10)"),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.text("Klik op een blok om te bewerken", size="1", color="var(--gray-9)"),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.divider(),
                # Row 1: Partners | Activities + Resources | Value Prop | Relations + Channels | Segments
                rx.grid(
                    # Kern partners (spans 2 rows)
                    rx.box(
                        _bmc_block(
                            "Kern partners", "handshake", IsmsImplementerState.bmc_partners,
                            "slate", IsmsImplementerState.open_bmc_edit("partners"), "100%",
                        ),
                        grid_row="1 / 3",
                        grid_column="1",
                    ),
                    # Kern activiteiten (top of col 2)
                    rx.box(
                        _bmc_block(
                            "Kern activiteiten", "settings", IsmsImplementerState.bmc_activiteiten,
                            "blue", IsmsImplementerState.open_bmc_edit("activiteiten"), "100%",
                        ),
                        grid_row="1",
                        grid_column="2",
                    ),
                    # Waarde propositie (spans 2 rows, center)
                    rx.box(
                        _bmc_block(
                            "Waarde propositie", "gem", IsmsImplementerState.bmc_waarde,
                            "amber", IsmsImplementerState.open_bmc_edit("waarde"), "100%",
                        ),
                        grid_row="1 / 3",
                        grid_column="3",
                    ),
                    # Klant relaties (top of col 4)
                    rx.box(
                        _bmc_block(
                            "Klant relaties", "heart-handshake", IsmsImplementerState.bmc_relaties,
                            "violet", IsmsImplementerState.open_bmc_edit("relaties"), "100%",
                        ),
                        grid_row="1",
                        grid_column="4",
                    ),
                    # Klant segmenten (spans 2 rows)
                    rx.box(
                        _bmc_block(
                            "Klant segmenten", "users", IsmsImplementerState.bmc_segmenten,
                            "green", IsmsImplementerState.open_bmc_edit("segmenten"), "100%",
                        ),
                        grid_row="1 / 3",
                        grid_column="5",
                    ),
                    # Kern middelen (bottom of col 2)
                    rx.box(
                        _bmc_block(
                            "Kern middelen", "database", IsmsImplementerState.bmc_middelen,
                            "blue", IsmsImplementerState.open_bmc_edit("middelen"), "100%",
                        ),
                        grid_row="2",
                        grid_column="2",
                    ),
                    # Kanalen (bottom of col 4)
                    rx.box(
                        _bmc_block(
                            "Kanalen", "send", IsmsImplementerState.bmc_kanalen,
                            "violet", IsmsImplementerState.open_bmc_edit("kanalen"), "100%",
                        ),
                        grid_row="2",
                        grid_column="4",
                    ),
                    display="grid",
                    grid_template_columns="1fr 1fr 1fr 1fr 1fr",
                    grid_template_rows="1fr 1fr",
                    gap="8px",
                    width="100%",
                ),
                # Row 2: Cost Structure | Kern aspecten | Revenue Streams
                rx.grid(
                    _bmc_block(
                        "Kosten structuur", "receipt", IsmsImplementerState.bmc_kosten,
                        "red", IsmsImplementerState.open_bmc_edit("kosten"), "160px",
                    ),
                    _bmc_block(
                        "Kern aspecten", "star", IsmsImplementerState.bmc_aspecten,
                        "indigo", IsmsImplementerState.open_bmc_edit("aspecten"), "160px",
                    ),
                    _bmc_block(
                        "Inkomstenbronnen", "trending-up", IsmsImplementerState.bmc_inkomsten,
                        "green", IsmsImplementerState.open_bmc_edit("inkomsten"), "160px",
                    ),
                    columns="3",
                    spacing="2",
                    width="100%",
                ),
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


def bmc_edit_dialog() -> rx.Component:
    """Dialog for editing a BMC block."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.match(
                    IsmsImplementerState.bmc_editing,
                    ("partners", "Kern partners bewerken"),
                    ("activiteiten", "Kern activiteiten bewerken"),
                    ("waarde", "Waarde propositie bewerken"),
                    ("relaties", "Klant relaties bewerken"),
                    ("segmenten", "Klant segmenten bewerken"),
                    ("middelen", "Kern middelen bewerken"),
                    ("kanalen", "Kanalen bewerken"),
                    ("kosten", "Kosten structuur bewerken"),
                    ("inkomsten", "Inkomstenbronnen bewerken"),
                    ("aspecten", "Kern aspecten bewerken"),
                    "BMC bewerken",
                ),
            ),
            rx.dialog.description("Pas de inhoud aan. Gebruik bullet points (•) voor opsommingen."),
            rx.text_area(
                value=IsmsImplementerState.bmc_edit_text,
                on_change=IsmsImplementerState.set_bmc_edit_text,
                min_height="250px",
                width="100%",
                auto_focus=True,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=IsmsImplementerState.close_bmc_edit),
                ),
                rx.dialog.close(
                    rx.button("Opslaan", on_click=IsmsImplementerState.save_bmc_edit),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="550px",
        ),
        open=IsmsImplementerState.bmc_editing != "",
        on_open_change=IsmsImplementerState.handle_bmc_dialog_change,
    )


def _bc_section(icon: str, title: str, content: rx.Var, on_click_handler) -> rx.Component:
    """Single clickable Business Case section card."""
    return rx.hstack(
        rx.box(
            rx.icon(icon, size=16, color="var(--amber-9)"),
            padding="8px",
            background="var(--amber-a3)",
            border_radius="var(--radius-2)",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, size="2", weight="bold"),
            rx.text(content, size="2", color="var(--gray-10)", line_height="1.6", white_space="pre-wrap"),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        width="100%",
        align="start",
        spacing="3",
        padding="12px",
        background="var(--gray-a2)",
        border_radius="var(--radius-2)",
        cursor="pointer",
        _hover={"background": "var(--amber-a3)", "border_color": "var(--amber-a5)"},
        border="1px solid transparent",
        transition="all 0.15s ease",
        on_click=on_click_handler,
    )


def bc_edit_dialog() -> rx.Component:
    """Dialog for editing a Business Case element."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.match(
                    IsmsImplementerState.bc_editing,
                    ("omgeving", "Omgeving bewerken"),
                    ("doelen", "Doel en doelstellingen bewerken"),
                    ("samenvatting", "Projectsamenvatting bewerken"),
                    ("voordelen", "Verwachte voordelen bewerken"),
                    ("scope", "Voorlopige scope bewerken"),
                    ("succesfactoren", "Kritische succesfactoren bewerken"),
                    ("projectplan", "Projectplan bewerken"),
                    ("deadlines", "Deadlines en mijlpalen bewerken"),
                    ("rollen", "Rollen en verantwoordelijkheden bewerken"),
                    ("middelen", "Middelen bewerken"),
                    ("budget", "Budget bewerken"),
                    ("beperkingen", "Beperkingen bewerken"),
                    "Element bewerken",
                ),
            ),
            rx.dialog.description("Pas de inhoud aan. Gebruik bullet points (•) voor opsommingen."),
            rx.text_area(
                placeholder="Voer hier de inhoud in...",
                value=IsmsImplementerState.bc_edit_text,
                on_change=IsmsImplementerState.set_bc_edit_text,
                min_height="250px",
                width="100%",
                auto_focus=True,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=IsmsImplementerState.close_bc_edit),
                ),
                rx.dialog.close(
                    rx.button("Opslaan", on_click=IsmsImplementerState.save_bc_edit),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="550px",
        ),
        open=IsmsImplementerState.bc_editing != "",
        on_open_change=IsmsImplementerState.handle_bc_dialog_change,
    )


def step_bc_content() -> rx.Component:
    """Content for preparation step: Business Case."""
    return rx.vstack(
        step_header(0, "Business Case"),
        # Dashboard
        phase_dashboard(
            "amber",
            IsmsImplementerState.bc_progress,
            [
                ("1. Business Model Canvas invullen", IsmsImplementerState.has_bmc),
                ("2. Elementen van de Business Case invullen", IsmsImplementerState.has_bc_elements),
            ],
        ),
        # Banner
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
        # Business Model Canvas
        bmc_canvas(),
        bmc_edit_dialog(),
        # Elementen card
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
                        rx.text("Elementen van de Business Case", size="3", weight="bold"),
                        rx.spacer(),
                        rx.text("Klik op een element om te bewerken", size="1", color="var(--gray-9)"),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(),
                    _bc_section("globe", "Omgeving", IsmsImplementerState.bc_omgeving, IsmsImplementerState.open_bc_edit("omgeving")),
                    _bc_section("target", "Doel en doelstellingen", IsmsImplementerState.bc_doelen, IsmsImplementerState.open_bc_edit("doelen")),
                    _bc_section("file-text", "Projectsamenvatting", IsmsImplementerState.bc_samenvatting, IsmsImplementerState.open_bc_edit("samenvatting")),
                    _bc_section("trophy", "Verwachte voordelen", IsmsImplementerState.bc_voordelen, IsmsImplementerState.open_bc_edit("voordelen")),
                    _bc_section("scan", "Voorlopige scope", IsmsImplementerState.bc_scope, IsmsImplementerState.open_bc_edit("scope")),
                    _bc_section("circle-check", "Kritische succesfactoren", IsmsImplementerState.bc_succesfactoren, IsmsImplementerState.open_bc_edit("succesfactoren")),
                    _bc_section("gantt-chart", "Projectplan", IsmsImplementerState.bc_projectplan, IsmsImplementerState.open_bc_edit("projectplan")),
                    _bc_section("calendar", "Deadlines en mijlpalen", IsmsImplementerState.bc_deadlines, IsmsImplementerState.open_bc_edit("deadlines")),
                    _bc_section("users", "Rollen en verantwoordelijkheden", IsmsImplementerState.bc_rollen, IsmsImplementerState.open_bc_edit("rollen")),
                    _bc_section("cpu", "Middelen", IsmsImplementerState.bc_middelen, IsmsImplementerState.open_bc_edit("middelen")),
                    _bc_section("wallet", "Budget", IsmsImplementerState.bc_budget, IsmsImplementerState.open_bc_edit("budget")),
                    _bc_section("triangle-alert", "Beperkingen", IsmsImplementerState.bc_beperkingen, IsmsImplementerState.open_bc_edit("beperkingen")),
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
        ),
        bc_edit_dialog(),
        align_items="start",
        width="100%",
        spacing="5",
    )



def step_pp_content() -> rx.Component:
    """Content for preparation step: Projectplan."""
    return rx.vstack(
        step_header(0, "Projectplan"),
        # Dashboard
        phase_dashboard(
            "amber",
            IsmsImplementerState.pp_progress,
            [
                ("1. Work Breakdown Structure opstellen", IsmsImplementerState.has_wbs),
                ("2. Planning en mijlpalen vastleggen", IsmsImplementerState.has_planning),
            ],
        ),
        # Banner
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color="var(--amber-4)", flex_shrink="0"),
                rx.text(
                    "Dit Projectplan is opgesteld aan de hand van het instrument Work Breakdown "
                    "Structure, zodat uitsluitend de benodigde en relevante onderdelen binnen het "
                    "plan zijn opgenomen. Daarnaast is het plan ingericht conform de PDCA-cyclus. "
                    "Het doel van dit project is het realiseren van een effectief ISMS dat voldoet "
                    "aan normatieve eisen, wettelijke kaders en bijdraagt aan het behalen van de "
                    "informatiebeveiligingsdoelstellingen van de gemeente.",
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
        # Projectplan tabel
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
                        rx.text("Work Breakdown Structure", size="3", weight="bold"),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Fase"),
                                rx.table.column_header_cell("Stap"),
                                rx.table.column_header_cell("Activiteit"),
                                rx.table.column_header_cell("Output"),
                                rx.table.column_header_cell("Verantwoordelijke"),
                                rx.table.column_header_cell("Planning & Deadline"),
                                rx.table.column_header_cell(""),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                IsmsImplementerState.wbs_rows,
                                lambda row, idx: rx.table.row(
                                    rx.table.cell(rx.text(row["fase"], size="2")),
                                    rx.table.cell(rx.text(row["stap"], size="2")),
                                    rx.table.cell(rx.text(row["activiteit"], size="2")),
                                    rx.table.cell(rx.text(row["output"], size="2")),
                                    rx.table.cell(rx.text(row["verantwoordelijke"], size="2")),
                                    rx.table.cell(rx.text(row["planning"], size="2")),
                                    rx.table.cell(
                                        rx.icon_button(
                                            rx.icon("trash-2", size=14),
                                            variant="ghost",
                                            color_scheme="red",
                                            size="1",
                                            on_click=IsmsImplementerState.delete_wbs_row(idx),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        variant="surface",
                        width="100%",
                    ),
                    # Toevoegen knop
                    rx.button(
                        rx.icon("plus", size=14),
                        "Toevoegen",
                        variant="soft",
                        color_scheme="amber",
                        size="2",
                        on_click=IsmsImplementerState.open_wbs_dialog,
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
        # Visie-callout
        rx.box(
            rx.hstack(
                rx.icon("sparkles", size=20, color="var(--amber-9)", flex_shrink="0"),
                rx.text(
                    "Dit implementatietraject transformeert informatiebeveiliging van een "
                    "reactieve taak naar een proactief proces dat integraal onderdeel is van "
                    "de gemeentelijke identiteit. Door de focus op leiderschap, objectieve "
                    "meting en continue verbetering bouwen we aan een weerbare gemeente.",
                    size="2",
                    color="var(--gray-11)",
                    line_height="1.7",
                ),
                spacing="3",
                align="start",
            ),
            background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
            border="1px solid var(--amber-a4)",
            border_radius="var(--radius-3)",
            padding="20px 24px",
            width="100%",
        ),
        # WBS toevoeg-dialog
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Activiteit Toevoegen"),
                rx.dialog.description("Voeg een nieuwe rij toe aan het projectplan."),
                rx.flex(
                    rx.text("Fase", size="2", weight="bold"),
                    rx.select(
                        ["Plan", "Do", "Check", "Act"],
                        placeholder="Selecteer fase...",
                        value=IsmsImplementerState.wbs_fase,
                        on_change=IsmsImplementerState.set_wbs_fase,
                    ),
                    rx.text("Stap", size="2", weight="bold", margin_top="12px"),
                    rx.input(
                        placeholder="Bijv. 1. Context",
                        value=IsmsImplementerState.wbs_stap,
                        on_change=IsmsImplementerState.set_wbs_stap,
                    ),
                    rx.text("Activiteit", size="2", weight="bold", margin_top="12px"),
                    rx.input(
                        placeholder="Bijv. Interne en externe analyse (SWOT)",
                        value=IsmsImplementerState.wbs_activiteit,
                        on_change=IsmsImplementerState.set_wbs_activiteit,
                    ),
                    rx.text("Output", size="2", weight="bold", margin_top="12px"),
                    rx.input(
                        placeholder="Bijv. SWOT-analyse",
                        value=IsmsImplementerState.wbs_output,
                        on_change=IsmsImplementerState.set_wbs_output,
                    ),
                    rx.text("Verantwoordelijke", size="2", weight="bold", margin_top="12px"),
                    rx.input(
                        placeholder="Bijv. CISO",
                        value=IsmsImplementerState.wbs_verantwoordelijke,
                        on_change=IsmsImplementerState.set_wbs_verantwoordelijke,
                    ),
                    rx.text("Planning & Deadline", size="2", weight="bold", margin_top="12px"),
                    rx.input(
                        placeholder="Bijv. Q1 2026",
                        value=IsmsImplementerState.wbs_planning,
                        on_change=IsmsImplementerState.set_wbs_planning,
                    ),
                    direction="column",
                    spacing="2",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=IsmsImplementerState.close_wbs_dialog),
                    ),
                    rx.dialog.close(
                        rx.button("Toevoegen", on_click=IsmsImplementerState.add_wbs_row),
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                max_width="500px",
            ),
            open=IsmsImplementerState.show_wbs_dialog,
        ),
        align_items="start",
        width="100%",
        spacing="5",
    )


def step_gap_content() -> rx.Component:
    """Content for Step 2: Gap-Analysis."""
    return _step_page(
        2, "Gap-Analysis",
        "De gap-analyse brengt het verschil in kaart tussen de huidige situatie "
        "en de gewenste situatie conform de eisen van ISO 27001 en BIO 2.0. "
        "Op basis van de geïdentificeerde hiaten worden prioriteiten gesteld "
        "en een actieplan opgesteld om de organisatie naar het gewenste "
        "volwassenheidsniveau te brengen.",
        "git-compare", "indigo",
        "De gap-analyse is nog in ontwikkeling. Hier komt een overzicht van "
        "de huidige status per ISO 27001-hoofdstuk, geïdentificeerde hiaten "
        "en het bijbehorende actieplan.",
        progress_var=IsmsImplementerState.gap_progress,
        activities=[
            ("1. Gap-analyse uitvoeren", IsmsImplementerState.has_gap_analysis),
            ("2. Actieplan opstellen", IsmsImplementerState.has_action_plan),
        ],
    )


def _step_page(
    step_number: int,
    title: str,
    banner_text: str,
    icon_name: str,
    accent: str,
    placeholder: str,
    progress_var: rx.Var = None,
    activities: list = None,
) -> rx.Component:
    """Reusable step page layout: header + dashboard + banner + card."""
    children = [step_header(step_number, title)]

    # Phase dashboard
    if progress_var is not None and activities is not None:
        children.append(
            phase_dashboard(accent, progress_var, activities)
        )

    # Banner
    children.append(
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color=f"var(--{accent}-4)", flex_shrink="0"),
                rx.text(
                    banner_text,
                    size="2",
                    color=f"var(--{accent}-3)",
                    line_height="1.7",
                ),
                spacing="3",
                align="start",
            ),
            background=f"linear-gradient(135deg, var(--{accent}-9), var(--{accent}-11))",
            border_radius="var(--radius-3)",
            padding="20px 24px",
            width="100%",
        )
    )

    # Content card
    children.append(
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background=f"var(--{accent}-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon(icon_name, size=18, color="white"),
                            background=f"var(--{accent}-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.text(title, size="3", weight="bold"),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(),
                    rx.text(
                        placeholder,
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
        )
    )

    return rx.vstack(
        *children,
        align_items="start",
        width="100%",
        spacing="5",
    )


def _beleid_section(icon: str, title: str, content: rx.Var, key: str, accent: str = "indigo") -> rx.Component:
    """Clickable policy section card."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=16, color="white"),
                background=f"var(--{accent}-9)",
                padding="6px",
                border_radius="var(--radius-2)",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(title, size="2", weight="bold"),
                rx.text(content, size="2", color="var(--gray-10)", line_height="1.6", white_space="pre-wrap"),
                spacing="1",
                align_items="start",
                width="100%",
            ),
            width="100%",
            align="start",
            spacing="3",
        ),
        padding="14px",
        background="var(--gray-a2)",
        border_radius="var(--radius-2)",
        cursor="pointer",
        _hover={"background": f"var(--{accent}-a3)", "border_color": f"var(--{accent}-a5)"},
        border="1px solid transparent",
        transition="all 0.15s ease",
        on_click=IsmsImplementerState.open_beleid_edit(key),
        width="100%",
    )


def _role_card(icon: str, title: str, content: rx.Var, key: str, line: str = "1") -> rx.Component:
    """Role card for Three Lines of Defence view."""
    line_colors = {"1": "blue", "2": "amber", "3": "red"}
    accent = line_colors.get(line, "gray")
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=16, color="white"),
                    background=f"var(--{accent}-9)",
                    padding="6px",
                    border_radius="var(--radius-2)",
                    flex_shrink="0",
                ),
                rx.text(title, size="2", weight="bold"),
                rx.spacer(),
                rx.badge(
                    f"Lijn {line}",
                    color_scheme=accent,
                    variant="soft",
                    size="1",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.text(content, size="1", color="var(--gray-10)", line_height="1.5", white_space="pre-wrap"),
            spacing="2",
            width="100%",
        ),
        padding="14px",
        background="var(--gray-a2)",
        border_radius="var(--radius-2)",
        cursor="pointer",
        _hover={"background": f"var(--{accent}-a3)", "border_color": f"var(--{accent}-a5)"},
        border="1px solid transparent",
        transition="all 0.15s ease",
        on_click=IsmsImplementerState.open_beleid_edit(key),
        width="100%",
    )


def beleid_edit_dialog() -> rx.Component:
    """Dialog for editing a policy section."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.match(
                    IsmsImplementerState.beleid_editing,
                    ("inleiding", "Inleiding bewerken"),
                    ("reikwijdte", "Reikwijdte bewerken"),
                    ("strategie", "Strategie & Doelen bewerken"),
                    ("risicomanagement", "Risicomanagement bewerken"),
                    ("rol_college", "College van B&W bewerken"),
                    ("rol_directeuren", "Directeuren bewerken"),
                    ("rol_afdelingsmanagers", "Afdelingsmanagers bewerken"),
                    ("rol_ciso", "CISO bewerken"),
                    ("rol_ibteam", "IB-team bewerken"),
                    ("rol_proceseigenaren", "Proceseigenaren bewerken"),
                    ("rol_medewerkers", "Alle medewerkers bewerken"),
                    ("naleving", "Naleving bewerken"),
                    ("versie", "Versie bewerken"),
                    ("datum", "Datum bewerken"),
                    ("status", "Status bewerken"),
                    ("gemeenten", "Gemeenten bewerken"),
                    "Beleid bewerken",
                ),
            ),
            rx.dialog.description("Pas de inhoud aan. Gebruik bullet points (•) voor opsommingen."),
            rx.text_area(
                value=IsmsImplementerState.beleid_edit_text,
                on_change=IsmsImplementerState.set_beleid_edit_text,
                min_height="250px",
                width="100%",
                auto_focus=True,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=IsmsImplementerState.close_beleid_edit),
                ),
                rx.dialog.close(
                    rx.button("Opslaan", on_click=IsmsImplementerState.save_beleid_edit),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="600px",
        ),
        open=IsmsImplementerState.beleid_editing != "",
        on_open_change=IsmsImplementerState.handle_beleid_dialog_change,
    )


def _mindmap_node(
    key: str, label: str, icon: str,
    left: str, top: str, accent: str,
) -> rx.Component:
    """A single mindmap branch node that scrolls to the matching beleid section."""
    scroll_js = (
        f"var el = document.getElementById('beleid-{key}');"
        "if(el){"
        "el.scrollIntoView({behavior:'smooth',block:'start'});"
        "el.style.transition='background-color 0.4s ease';"
        f"el.style.backgroundColor='var(--{accent}-a4)';"
        "setTimeout(function(){el.style.backgroundColor='';},2000);"
        "}"
    )
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=18, color="white"),
                width="44px",
                height="44px",
                background=f"var(--{accent}-a8)",
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
                transition="all 0.3s ease",
            ),
            rx.text(
                label,
                size="1",
                weight="medium",
                color="var(--gray-11)",
                text_align="center",
                white_space="pre-wrap",
            ),
            align="center",
            spacing="1",
        ),
        position="absolute",
        left=left,
        top=top,
        transform="translate(-50%, -50%)",
        cursor="pointer",
        z_index="2",
        _hover={"transform": "translate(-50%, -50%) scale(1.12)"},
        transition="transform 0.2s ease",
        on_click=rx.call_script(scroll_js),
    )


def _mindmap_text_content(content_var: rx.Var, key: str) -> rx.Component:
    """Expanded text content for a mindmap section."""
    return rx.vstack(
        rx.text(
            content_var,
            size="2",
            color="var(--gray-11)",
            line_height="1.7",
            white_space="pre-wrap",
        ),
        rx.button(
            rx.icon("pencil", size=14),
            "Bewerken",
            variant="soft",
            size="2",
            on_click=IsmsImplementerState.open_beleid_edit(key),
        ),
        spacing="3",
        width="100%",
    )


def _mindmap_role_row(
    icon: str, title: str, key: str, line_num: str, accent: str,
) -> rx.Component:
    """A single clickable role row in the mindmap roles view."""
    return rx.hstack(
        rx.badge(f"L{line_num}", color_scheme=accent, variant="soft", size="1"),
        rx.icon(icon, size=14, color=f"var(--{accent}-9)", flex_shrink="0"),
        rx.text(title, size="2", weight="medium"),
        rx.spacer(),
        rx.icon("pencil", size=12, color="var(--gray-9)"),
        width="100%",
        align="center",
        spacing="2",
        padding="8px 12px",
        background="var(--gray-a2)",
        border_radius="var(--radius-2)",
        cursor="pointer",
        _hover={"background": f"var(--{accent}-a3)"},
        transition="all 0.15s ease",
        on_click=IsmsImplementerState.open_beleid_edit(key),
    )


def _mindmap_roles_content() -> rx.Component:
    """Expanded roles content for the mindmap."""
    return rx.vstack(
        rx.hstack(
            rx.badge("Lijn 1", color_scheme="blue", variant="soft", size="1"),
            rx.text("Uitvoering", size="1", color="var(--gray-10)"),
            rx.badge("Lijn 2", color_scheme="amber", variant="soft", size="1"),
            rx.text("Ondersteuning", size="1", color="var(--gray-10)"),
            spacing="2",
            align="center",
            flex_wrap="wrap",
        ),
        _mindmap_role_row("landmark", "College van B&W", "rol_college", "1", "blue"),
        _mindmap_role_row("crown", "Directeuren", "rol_directeuren", "1", "blue"),
        _mindmap_role_row("briefcase", "Afdelingsmanagers", "rol_afdelingsmanagers", "1", "blue"),
        _mindmap_role_row("shield", "CISO", "rol_ciso", "2", "amber"),
        _mindmap_role_row("users", "IB-team", "rol_ibteam", "2", "amber"),
        _mindmap_role_row("database", "Proceseigenaren", "rol_proceseigenaren", "1", "blue"),
        _mindmap_role_row("user", "Alle medewerkers", "rol_medewerkers", "1", "blue"),
        spacing="2",
        width="100%",
    )


def beleid_mindmap() -> rx.Component:
    """Interactive mindmap visualization of the Informatiebeveiligingsbeleid."""
    S = IsmsImplementerState

    # SVG connecting lines from center (50%, 48%) to each node
    # Wrapped in rx.box so CSS properties (position, pointer_events) apply correctly
    svg_lines = rx.box(
        rx.el.svg(
            rx.el.line(x1="50%", y1="48%", x2="50%", y2="10%", stroke="var(--indigo-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            rx.el.line(x1="50%", y1="48%", x2="82%", y2="26%", stroke="var(--blue-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            rx.el.line(x1="50%", y1="48%", x2="82%", y2="72%", stroke="var(--violet-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            rx.el.line(x1="50%", y1="48%", x2="50%", y2="90%", stroke="var(--red-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            rx.el.line(x1="50%", y1="48%", x2="18%", y2="72%", stroke="var(--amber-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            rx.el.line(x1="50%", y1="48%", x2="18%", y2="26%", stroke="var(--green-6)", stroke_width="2", stroke_dasharray="6,4", opacity="0.5"),
            width="100%",
            height="100%",
        ),
        position="absolute",
        top="0",
        left="0",
        width="100%",
        height="100%",
        pointer_events="none",
        z_index="1",
    )

    # Center node
    center_node = rx.box(
        rx.vstack(
            rx.icon("shield", size=24, color="white"),
            rx.text("Informatie-", size="1", weight="bold", color="white", line_height="1.1", text_align="center"),
            rx.text("beveiligings-", size="1", weight="bold", color="white", line_height="1.1", text_align="center"),
            rx.text("beleid", size="1", weight="bold", color="white", line_height="1.1", text_align="center"),
            align="center",
            spacing="0",
        ),
        background="linear-gradient(135deg, var(--indigo-9), var(--indigo-11))",
        border_radius="50%",
        width="130px",
        height="130px",
        display="flex",
        align_items="center",
        justify_content="center",
        position="absolute",
        left="50%",
        top="48%",
        transform="translate(-50%, -50%)",
        z_index="2",
        box_shadow="0 4px 24px var(--indigo-a5)",
    )

    # Branch nodes (hexagonal layout)
    branch_nodes = [
        _mindmap_node("inleiding", "Inleiding", "book-open", "50%", "10%", "indigo"),
        _mindmap_node("reikwijdte", "Reikwijdte", "scan", "82%", "26%", "blue"),
        _mindmap_node("strategie", "Strategie\n& Doelen", "target", "82%", "72%", "violet"),
        _mindmap_node("risicomanagement", "Risico-\nmanagement", "shield-alert", "50%", "90%", "red"),
        _mindmap_node("rollen", "Rollen", "users", "18%", "72%", "amber"),
        _mindmap_node("naleving", "Naleving", "clipboard-check", "18%", "26%", "green"),
    ]

    # Visual mindmap area
    visual_area = rx.box(
        svg_lines,
        center_node,
        *branch_nodes,
        position="relative",
        width="100%",
        height="420px",
        min_height="420px",
    )

    return rx.box(
        rx.vstack(
            rx.box(
                width="100%",
                height="3px",
                background="linear-gradient(90deg, var(--indigo-9), var(--blue-9), var(--violet-9), var(--red-9), var(--amber-9), var(--green-9))",
                border_radius="var(--radius-3) var(--radius-3) 0 0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("brain", size=18, color="white"),
                        background="var(--indigo-9)",
                        padding="8px",
                        border_radius="var(--radius-2)",
                    ),
                    rx.text("Mindmap Informatiebeveiligingsbeleid", size="3", weight="bold"),
                    rx.spacer(),
                    rx.text("Klik op een onderdeel om ernaartoe te scrollen", size="1", color="var(--gray-9)"),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.divider(),
                visual_area,
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
    )


def step_3_content() -> rx.Component:
    S = IsmsImplementerState
    return rx.vstack(
        step_header(3, "Leiderschap & Beleid"),

        # Dashboard
        phase_dashboard(
            "indigo",
            S.leadership_progress,
            [
                ("1. Informatiebeveiligingsbeleid vaststellen", S.has_policy),
                ("2. Rollen en verantwoordelijkheden toewijzen", S.has_roles_assigned),
                ("3. Doelstellingen definiëren", S.has_objectives),
            ],
        ),

        # Banner
        rx.box(
            rx.hstack(
                rx.icon("info", size=20, color="var(--indigo-4)", flex_shrink="0"),
                rx.text(
                    "De fase 'leiderschap' omvat het tonen van commitment door het topmanagement via het "
                    "vaststellen van een informatiebeveiligingsbeleid en meetbare doelstellingen die aansluiten "
                    "bij de organisatiestrategie. Tevens worden binnen deze fase rollen en verantwoordelijkheden "
                    "toegewezen, de benodigde middelen beschikbaar gesteld en de integratie van ISMS-eisen in "
                    "de bedrijfsprocessen geborgd.",
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

        # ── Mindmap ──
        beleid_mindmap(),

        # ── Beleid metadata ──
        rx.box(
            rx.vstack(
                rx.box(width="100%", height="3px", background="var(--indigo-9)", border_radius="var(--radius-3) var(--radius-3) 0 0"),
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("file-badge", size=18, color="white"),
                            background="var(--indigo-9)",
                            padding="8px",
                            border_radius="var(--radius-2)",
                        ),
                        rx.text("Informatiebeveiligingsbeleid", size="3", weight="bold"),
                        rx.spacer(),
                        rx.hstack(
                            rx.badge(
                                rx.fragment("v", S.beleid_versie),
                                color_scheme="indigo", variant="soft", size="1",
                                cursor="pointer",
                                on_click=S.open_beleid_edit("versie"),
                            ),
                            rx.badge(
                                S.beleid_status,
                                color_scheme="green", variant="soft", size="1",
                                cursor="pointer",
                                on_click=S.open_beleid_edit("status"),
                            ),
                            rx.badge(
                                S.beleid_datum,
                                color_scheme="gray", variant="soft", size="1",
                                cursor="pointer",
                                on_click=S.open_beleid_edit("datum"),
                            ),
                            spacing="2",
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.text(
                        S.beleid_gemeenten,
                        size="2",
                        color="var(--gray-10)",
                        cursor="pointer",
                        _hover={"color": "var(--indigo-11)"},
                        on_click=S.open_beleid_edit("gemeenten"),
                    ),
                    rx.divider(),

                    # Hoofdstuk 1: Inleiding
                    rx.text("Hoofdstuk 1 — Inleiding", size="2", weight="bold", color="var(--indigo-11)", id="beleid-inleiding", scroll_margin_top="20px"),
                    _beleid_section("book-open", "Inleiding & Context", S.beleid_inleiding, "inleiding"),
                    rx.box(_beleid_section("scan", "Reikwijdte", S.beleid_reikwijdte, "reikwijdte"), id="beleid-reikwijdte", scroll_margin_top="20px", width="100%"),

                    rx.divider(),

                    # Hoofdstuk 2: Strategie & Doelen
                    rx.text("Hoofdstuk 2 — Strategie & Doelen", size="2", weight="bold", color="var(--indigo-11)", id="beleid-strategie", scroll_margin_top="20px"),
                    _beleid_section("target", "Doelstellingen informatiebeveiliging", S.beleid_strategie, "strategie"),

                    rx.divider(),

                    # Hoofdstuk 3: Risicomanagement
                    rx.text("Hoofdstuk 3 — Risicomanagement", size="2", weight="bold", color="var(--indigo-11)", id="beleid-risicomanagement", scroll_margin_top="20px"),
                    _beleid_section("shield-alert", "Risicobeheer", S.beleid_risicomanagement, "risicomanagement"),

                    rx.divider(),

                    # Hoofdstuk 4: Rollen & Verantwoordelijkheden
                    rx.text("Hoofdstuk 4 — Rollen & Verantwoordelijkheden", size="2", weight="bold", color="var(--indigo-11)", id="beleid-rollen", scroll_margin_top="20px"),
                    rx.hstack(
                        rx.badge("Lijn 1", color_scheme="blue", variant="soft", size="1"),
                        rx.text("Uitvoering", size="1", color="var(--gray-10)"),
                        rx.badge("Lijn 2", color_scheme="amber", variant="soft", size="1"),
                        rx.text("Ondersteuning & Controle", size="1", color="var(--gray-10)"),
                        rx.badge("Lijn 3", color_scheme="red", variant="soft", size="1"),
                        rx.text("Onafhankelijke toetsing", size="1", color="var(--gray-10)"),
                        spacing="2",
                        align="center",
                        flex_wrap="wrap",
                    ),
                    rx.grid(
                        _role_card("landmark", "College van B&W", S.beleid_rol_college, "rol_college", "1"),
                        _role_card("crown", "Directeuren", S.beleid_rol_directeuren, "rol_directeuren", "1"),
                        _role_card("briefcase", "Afdelingsmanagers", S.beleid_rol_afdelingsmanagers, "rol_afdelingsmanagers", "1"),
                        _role_card("shield", "CISO", S.beleid_rol_ciso, "rol_ciso", "2"),
                        _role_card("users", "IB-team", S.beleid_rol_ibteam, "rol_ibteam", "2"),
                        _role_card("database", "Proceseigenaren", S.beleid_rol_proceseigenaren, "rol_proceseigenaren", "1"),
                        _role_card("user", "Alle medewerkers", S.beleid_rol_medewerkers, "rol_medewerkers", "1"),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),

                    rx.divider(),

                    # Hoofdstuk 5: Naleving
                    rx.text("Hoofdstuk 5 — Naleving", size="2", weight="bold", color="var(--indigo-11)", id="beleid-naleving", scroll_margin_top="20px"),
                    _beleid_section("clipboard-check", "Borging, controle & handhaving", S.beleid_naleving, "naleving"),

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

        # Edit dialog
        beleid_edit_dialog(),

        align_items="start",
        width="100%",
        spacing="5",
    )


def step_4_content() -> rx.Component:
    return _step_page(
        4, "Risicomanagement",
        "Het risicomanagementproces omvat het identificeren, analyseren en evalueren van "
        "informatiebeveiligingsrisico's. Op basis van de risicoanalyse worden passende "
        "beheersmaatregelen geselecteerd om risico's te mitigeren tot een acceptabel niveau.",
        "triangle-alert", "red",
        "Hier komt de content voor Stap 4 (Risico's, Bedreigingen).",
        progress_var=IsmsImplementerState.risk_progress,
        activities=[
            ("1. Risicoanalyse uitvoeren", IsmsImplementerState.has_risk_analysis),
            ("2. Risicobehandelingsplan opstellen", IsmsImplementerState.has_risk_treatment),
        ],
    )


def step_5_content() -> rx.Component:
    return _step_page(
        5, "Middelen & Bewustzijn",
        "De organisatie moet voldoende middelen beschikbaar stellen voor het ISMS, "
        "waaronder competent personeel, bewustwordingsprogramma's en communicatie. "
        "Medewerkers moeten zich bewust zijn van het informatiebeveiligingsbeleid "
        "en hun rol daarin.",
        "graduation-cap", "blue",
        "Hier komt de content voor Stap 5 (Middelen, Training, Bewustzijn).",
        progress_var=IsmsImplementerState.support_progress,
        activities=[
            ("1. Middelen beschikbaar stellen", IsmsImplementerState.has_resources),
            ("2. Competenties vaststellen", IsmsImplementerState.has_competences),
            ("3. Bewustwordingsprogramma opzetten", IsmsImplementerState.has_awareness),
        ],
    )


def step_6_content() -> rx.Component:
    return _step_page(
        6, "Beheersing & SoA",
        "In deze fase worden de beheersmaatregelen uit Annex A van ISO 27001 beoordeeld "
        "en geïmplementeerd. De Verklaring van Toepasselijkheid (SoA) documenteert welke "
        "maatregelen van toepassing zijn, waarom, en hoe ze zijn geïmplementeerd.",
        "shield-check", "green",
        "Hier komt de content voor Stap 6 (Beheersmaatregelen, SoA).",
        progress_var=IsmsImplementerState.controls_progress,
        activities=[
            ("1. Verklaring van Toepasselijkheid (SoA) opstellen", IsmsImplementerState.has_soa),
            ("2. Beheersmaatregelen implementeren", IsmsImplementerState.has_controls_implemented),
        ],
    )


def step_7_content() -> rx.Component:
    return _step_page(
        7, "Evaluatie & Audit",
        "De prestaties van het ISMS worden gemonitord, gemeten, geanalyseerd en "
        "geëvalueerd. Interne audits en directiebeoordelingen worden uitgevoerd om "
        "vast te stellen of het ISMS effectief is en voldoet aan de gestelde eisen.",
        "clipboard-check", "orange",
        "Hier komt de content voor Stap 7 (Monitoring, Interne Audits, Directiebeoordeling).",
        progress_var=IsmsImplementerState.evaluation_progress,
        activities=[
            ("1. Interne audit uitvoeren", IsmsImplementerState.has_internal_audit),
            ("2. Directiebeoordeling uitvoeren", IsmsImplementerState.has_management_review),
        ],
    )


def step_8_content() -> rx.Component:
    return _step_page(
        8, "Verbetering (CAPA)",
        "Op basis van de bevindingen uit audits, incidenten en evaluaties worden "
        "corrigerende maatregelen genomen en verbeteringen doorgevoerd. Het ISMS "
        "wordt continu verbeterd om de effectiviteit en geschiktheid te waarborgen.",
        "refresh-cw", "red",
        "Hier komt de content voor Stap 8 (Corrigerende Acties, Continue Verbetering).",
        progress_var=IsmsImplementerState.improvement_progress,
        activities=[
            ("1. Corrigerende acties definiëren", IsmsImplementerState.has_corrective_actions),
            ("2. Verbeterplannen opstellen", IsmsImplementerState.has_improvement_plans),
        ],
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
                    stepper_item(2, "Gap-Analysis"),
                    stepper_connector(2),
                    stepper_item(3, "Leiderschap"),
                    stepper_connector(3),
                    stepper_item(4, "Planning"),
                    stepper_connector(4),
                    stepper_item(5, "Ondersteuning"),
                    stepper_connector(5),
                    stepper_item(6, "Uitvoering"),
                    stepper_connector(6),
                    stepper_item(7, "Evaluatie"),
                    stepper_connector(7),
                    stepper_item(8, "Verbetering"),
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
                rx.cond(IsmsImplementerState.active_step == 2, step_gap_content()),
                rx.cond(IsmsImplementerState.active_step == 3, step_3_content()),
                rx.cond(IsmsImplementerState.active_step == 4, step_4_content()),
                rx.cond(IsmsImplementerState.active_step == 5, step_5_content()),
                rx.cond(IsmsImplementerState.active_step == 6, step_6_content()),
                rx.cond(IsmsImplementerState.active_step == 7, step_7_content()),
                rx.cond(IsmsImplementerState.active_step == 8, step_8_content()),
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
