"""
Scopes Page - Organization hierarchy management with CRUD
"""
import reflex as rx
from ims.state.scope import ScopeState
from ims.state.auth import AuthState
from ims.components.layout import layout


def scope_form_dialog() -> rx.Component:
    """Dialog for creating/editing a scope with conditional fields."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    ScopeState.is_editing,
                    "Scope Bewerken",
                    "Nieuwe Scope",
                ),
            ),
            rx.dialog.description(
                "Velden met * zijn verplicht. Extra velden verschijnen op basis van het type.",
                size="2",
                margin_bottom="16px",
            ),

            # Error message
            rx.cond(
                ScopeState.error != "",
                rx.callout(
                    ScopeState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            # Scrollable form content
            rx.scroll_area(
                rx.vstack(
                    # === BASIC FIELDS (always shown) ===
                    rx.text("Basis Informatie", weight="bold", size="3", margin_bottom="8px"),

                    # Type (important to show first as it affects other fields)
                    rx.vstack(
                        rx.text("Type *", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer type"),
                            rx.select.content(
                                rx.select.item("Organisatie", value="Organization"),
                                rx.select.item("Cluster", value="Cluster"),
                                rx.select.item("Afdeling", value="Department"),
                                rx.select.item("Proces", value="Process"),
                                rx.select.item("Asset", value="Asset"),
                                rx.select.item("Leverancier", value="Supplier"),
                            ),
                            value=ScopeState.form_type,
                            on_change=ScopeState.set_form_type,
                            default_value="Process",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    # Name
                    rx.vstack(
                        rx.text("Naam *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Bijv. HR Afdeling, Salarisadministratie",
                            value=ScopeState.form_name,
                            on_change=ScopeState.set_form_name,
                            width="100%",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    # Description
                    rx.vstack(
                        rx.text("Beschrijving", size="2", weight="medium"),
                        rx.text_area(
                            placeholder="Korte omschrijving van de scope...",
                            value=ScopeState.form_description,
                            on_change=ScopeState.set_form_description,
                            width="100%",
                            rows="2",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    # Owner
                    rx.vstack(
                        rx.text("Eigenaar *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Naam van de verantwoordelijke",
                            value=ScopeState.form_owner,
                            on_change=ScopeState.set_form_owner,
                            width="100%",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    # Parent scope
                    rx.vstack(
                        rx.text("Bovenliggende Scope", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer parent (optioneel)"),
                            rx.select.content(
                                rx.select.item("Geen (root level)", value="NONE"),
                                rx.foreach(
                                    ScopeState.available_parents,
                                    lambda p: rx.select.item(
                                        p["name"],
                                        value=p["id"],
                                    ),
                                ),
                            ),
                            value=ScopeState.form_parent_id,
                            on_change=ScopeState.set_form_parent_id,
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    rx.divider(margin_y="16px"),

                    # === ASSET SPECIFIC FIELDS ===
                    rx.cond(
                        ScopeState.show_asset_fields,
                        rx.vstack(
                            rx.text("Asset Informatie", weight="bold", size="3", margin_bottom="8px"),

                            rx.hstack(
                                rx.vstack(
                                    rx.text("Asset Type", size="2", weight="medium"),
                                    rx.select.root(
                                        rx.select.trigger(placeholder="Selecteer"),
                                        rx.select.content(
                                            rx.select.item("Geen", value="NONE"),
                                            rx.select.item("Hardware", value="Hardware"),
                                            rx.select.item("Software", value="Software"),
                                            rx.select.item("Data", value="Data"),
                                            rx.select.item("Mensen", value="People"),
                                            rx.select.item("Faciliteit", value="Facility"),
                                            rx.select.item("Service", value="Service"),
                                            rx.select.item("Netwerk", value="Network"),
                                        ),
                                        value=ScopeState.form_asset_type,
                                        on_change=ScopeState.set_form_asset_type,
                                    ),
                                    align_items="start",
                                    flex="1",
                                ),
                                rx.vstack(
                                    rx.text("Data Classificatie", size="2", weight="medium"),
                                    rx.select.root(
                                        rx.select.trigger(placeholder="Selecteer"),
                                        rx.select.content(
                                            rx.select.item("Openbaar", value="Public"),
                                            rx.select.item("Intern", value="Internal"),
                                            rx.select.item("Vertrouwelijk", value="Confidential"),
                                            rx.select.item("Geheim", value="Secret"),
                                        ),
                                        value=ScopeState.form_data_classification,
                                        on_change=ScopeState.set_form_data_classification,
                                        default_value="Internal",
                                    ),
                                    align_items="start",
                                    flex="1",
                                ),
                                width="100%",
                                spacing="4",
                            ),

                            rx.vstack(
                                rx.text("Locatie", size="2", weight="medium"),
                                rx.input(
                                    placeholder="Fysieke of logische locatie",
                                    value=ScopeState.form_location,
                                    on_change=ScopeState.set_form_location,
                                    width="100%",
                                ),
                                align_items="start",
                                width="100%",
                            ),

                            rx.divider(margin_y="16px"),
                            align_items="start",
                            width="100%",
                        ),
                    ),

                    # === SUPPLIER SPECIFIC FIELDS ===
                    rx.cond(
                        ScopeState.show_supplier_fields,
                        rx.vstack(
                            rx.text("Leverancier Informatie", weight="bold", size="3", margin_bottom="8px"),

                            rx.vstack(
                                rx.text("Contactpersoon", size="2", weight="medium"),
                                rx.input(
                                    placeholder="Naam contactpersoon leverancier",
                                    value=ScopeState.form_vendor_contact_name,
                                    on_change=ScopeState.set_form_vendor_contact_name,
                                    width="100%",
                                ),
                                align_items="start",
                                width="100%",
                            ),

                            rx.vstack(
                                rx.text("Contact E-mail", size="2", weight="medium"),
                                rx.input(
                                    placeholder="email@leverancier.nl",
                                    value=ScopeState.form_vendor_contact_email,
                                    on_change=ScopeState.set_form_vendor_contact_email,
                                    width="100%",
                                    type="email",
                                ),
                                align_items="start",
                                width="100%",
                            ),

                            rx.divider(margin_y="16px"),
                            align_items="start",
                            width="100%",
                        ),
                    ),

                    # === BIA FIELDS (Process, Asset, Department) ===
                    rx.cond(
                        ScopeState.show_bia_fields,
                        rx.vstack(
                            rx.text("BIA / BIV Classificatie", weight="bold", size="3", margin_bottom="8px"),
                            rx.text(
                                "Business Impact Analysis - classificeer beschikbaarheid, integriteit en vertrouwelijkheid",
                                size="1",
                                color="gray",
                                margin_bottom="8px",
                            ),

                            rx.flex(
                                rx.vstack(
                                    rx.text("Beschikbaarheid", size="2", weight="medium"),
                                    rx.select.root(
                                        rx.select.trigger(),
                                        rx.select.content(
                                            rx.select.item("Openbaar", value="Public"),
                                            rx.select.item("Intern", value="Internal"),
                                            rx.select.item("Vertrouwelijk", value="Confidential"),
                                            rx.select.item("Geheim", value="Secret"),
                                        ),
                                        value=ScopeState.form_availability_rating,
                                        on_change=ScopeState.set_form_availability_rating,
                                        default_value="Internal",
                                    ),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                rx.vstack(
                                    rx.text("Integriteit", size="2", weight="medium"),
                                    rx.select.root(
                                        rx.select.trigger(),
                                        rx.select.content(
                                            rx.select.item("Openbaar", value="Public"),
                                            rx.select.item("Intern", value="Internal"),
                                            rx.select.item("Vertrouwelijk", value="Confidential"),
                                            rx.select.item("Geheim", value="Secret"),
                                        ),
                                        value=ScopeState.form_integrity_rating,
                                        on_change=ScopeState.set_form_integrity_rating,
                                        default_value="Internal",
                                    ),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                rx.vstack(
                                    rx.text("Vertrouwelijkheid", size="2", weight="medium"),
                                    rx.select.root(
                                        rx.select.trigger(),
                                        rx.select.content(
                                            rx.select.item("Openbaar", value="Public"),
                                            rx.select.item("Intern", value="Internal"),
                                            rx.select.item("Vertrouwelijk", value="Confidential"),
                                            rx.select.item("Geheim", value="Secret"),
                                        ),
                                        value=ScopeState.form_confidentiality_rating,
                                        on_change=ScopeState.set_form_confidentiality_rating,
                                        default_value="Internal",
                                    ),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                width="100%",
                                wrap="wrap",
                                gap="2",
                            ),

                            rx.divider(margin_y="12px"),
                            rx.text("BCM Recovery Doelen", weight="bold", size="3", margin_bottom="8px"),

                            rx.flex(
                                rx.vstack(
                                    rx.text("RTO (uren)", size="2", weight="medium"),
                                    rx.input(
                                        placeholder="Bijv. 4",
                                        value=ScopeState.form_rto_hours,
                                        on_change=ScopeState.set_form_rto_hours,
                                        type="number",
                                    ),
                                    rx.text("Recovery Time Objective", size="1", color="gray"),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                rx.vstack(
                                    rx.text("RPO (uren)", size="2", weight="medium"),
                                    rx.input(
                                        placeholder="Bijv. 1",
                                        value=ScopeState.form_rpo_hours,
                                        on_change=ScopeState.set_form_rpo_hours,
                                        type="number",
                                    ),
                                    rx.text("Recovery Point Objective", size="1", color="gray"),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                rx.vstack(
                                    rx.text("MTPD (uren)", size="2", weight="medium"),
                                    rx.input(
                                        placeholder="Bijv. 24",
                                        value=ScopeState.form_mtpd_hours,
                                        on_change=ScopeState.set_form_mtpd_hours,
                                        type="number",
                                    ),
                                    rx.text("Max Tolerable Downtime", size="1", color="gray"),
                                    align_items="start",
                                    flex="1",
                                    min_width="140px",
                                ),
                                width="100%",
                                wrap="wrap",
                                gap="2",
                            ),

                            align_items="start",
                            width="100%",
                        ),
                    ),

                    spacing="3",
                    width="100%",
                    padding_right="8px",
                ),
                max_height="60vh",
                scrollbars="vertical",
            ),

            # Action buttons
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ScopeState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(
                        ScopeState.is_editing,
                        "Opslaan",
                        "Toevoegen",
                    ),
                    on_click=ScopeState.save_scope,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=ScopeState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming scope deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Scope Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze scope wilt verwijderen?"),
                    rx.text(
                        ScopeState.deleting_scope_name,
                        weight="bold",
                        color="red",
                    ),
                    rx.text(
                        "Gekoppelde items (risico's, maatregelen) kunnen hierdoor beïnvloed worden.",
                        size="2",
                        color="gray",
                    ),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ScopeState.close_delete_dialog,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Verwijderen",
                        color_scheme="red",
                        on_click=ScopeState.confirm_delete,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=ScopeState.show_delete_dialog,
    )


def type_badge(scope_type: str) -> rx.Component:
    """Badge for scope type."""
    return rx.match(
        scope_type,
        ("ORGANIZATION", rx.badge(
            rx.hstack(rx.icon("building-2", size=12), rx.text("Organisatie"), spacing="1"),
            color_scheme="purple", variant="soft"
        )),
        ("CLUSTER", rx.badge(
            rx.hstack(rx.icon("boxes", size=12), rx.text("Cluster"), spacing="1"),
            color_scheme="blue", variant="soft"
        )),
        ("DEPARTMENT", rx.badge(
            rx.hstack(rx.icon("users", size=12), rx.text("Afdeling"), spacing="1"),
            color_scheme="cyan", variant="soft"
        )),
        ("PROCESS", rx.badge(
            rx.hstack(rx.icon("workflow", size=12), rx.text("Proces"), spacing="1"),
            color_scheme="green", variant="soft"
        )),
        ("ASSET", rx.badge(
            rx.hstack(rx.icon("server", size=12), rx.text("Asset"), spacing="1"),
            color_scheme="orange", variant="soft"
        )),
        ("SUPPLIER", rx.badge(
            rx.hstack(rx.icon("truck", size=12), rx.text("Leverancier"), spacing="1"),
            color_scheme="yellow", variant="soft"
        )),
        rx.badge(scope_type, color_scheme="gray", variant="outline"),
    )


def scope_row(scope: dict) -> rx.Component:
    """Single row in scopes table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(scope["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(scope["name"], weight="medium", size="2"),
                rx.text(
                    scope["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(type_badge(scope["type"])),
        rx.table.cell(
            rx.text(scope["owner"], size="2"),
        ),
        rx.table.cell(
            rx.match(
                scope["governance_status"],
                ("Vastgesteld", rx.badge("Vastgesteld", color_scheme="green", variant="soft")),
                ("Concept", rx.badge("Concept", color_scheme="yellow", variant="soft")),
                ("Verlopen", rx.badge("Verlopen", color_scheme="red", variant="soft")),
                rx.cond(
                    scope["is_active"],
                    rx.badge("Actief", color_scheme="green", variant="soft"),
                    rx.badge("Inactief", color_scheme="gray", variant="soft"),
                ),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: ScopeState.open_edit_dialog(scope["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: ScopeState.open_delete_dialog(scope["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def scope_mobile_card(scope: dict) -> rx.Component:
    """Mobile card view for a single scope."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(scope["name"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: ScopeState.open_edit_dialog(scope["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: ScopeState.open_delete_dialog(scope["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.text(scope["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                type_badge(scope["type"]),
                rx.text(scope["owner"], size="1", color="gray"),
                rx.match(
                    scope["governance_status"],
                    ("Vastgesteld", rx.badge("Vastgesteld", color_scheme="green", variant="soft", size="1")),
                    ("Concept", rx.badge("Concept", color_scheme="yellow", variant="soft", size="1")),
                    ("Verlopen", rx.badge("Verlopen", color_scheme="red", variant="soft", size="1")),
                    rx.cond(
                        scope["is_active"],
                        rx.badge("Actief", color_scheme="green", variant="soft", size="1"),
                        rx.badge("Inactief", color_scheme="gray", variant="soft", size="1"),
                    ),
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def scopes_table() -> rx.Component:
    """Scopes data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Scope"),
                rx.table.column_header_cell("Type", width="140px"),
                rx.table.column_header_cell("Eigenaar", width="150px"),
                rx.table.column_header_cell("Bestuurlijk", width="120px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                ScopeState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=6,
                    ),
                ),
                rx.cond(
                    ScopeState.scopes.length() > 0,
                    rx.foreach(ScopeState.scopes, scope_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("git-branch", size=32, color="gray"),
                                    rx.text("Geen scopes gevonden", color="gray"),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Voeg eerste scope toe",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=ScopeState.open_create_dialog,
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=6,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def filter_bar() -> rx.Component:
    """Filter bar for scopes."""
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op type"),
            rx.select.content(
                rx.select.item("Alle types", value="ALLE"),
                rx.select.item("Organisatie", value="Organization"),
                rx.select.item("Cluster", value="Cluster"),
                rx.select.item("Afdeling", value="Department"),
                rx.select.item("Proces", value="Process"),
                rx.select.item("Asset", value="Asset"),
                rx.select.item("Leverancier", value="Supplier"),
            ),
            value=ScopeState.filter_type,
            on_change=ScopeState.set_filter_type,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=ScopeState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuwe Scope",
            size="2",
            on_click=ScopeState.open_create_dialog,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.grid(
        rx.card(
            rx.hstack(
                rx.icon("building-2", size=20, color="var(--purple-9)"),
                rx.vstack(
                    rx.text("Organisaties", size="1", color="gray"),
                    rx.text(ScopeState.organization_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("users", size=20, color="var(--cyan-9)"),
                rx.vstack(
                    rx.text("Afdelingen", size="1", color="gray"),
                    rx.text(ScopeState.department_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("workflow", size=20, color="var(--green-9)"),
                rx.vstack(
                    rx.text("Processen", size="1", color="gray"),
                    rx.text(ScopeState.process_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("server", size=20, color="var(--orange-9)"),
                rx.vstack(
                    rx.text("Assets", size="1", color="gray"),
                    rx.text(ScopeState.asset_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("truck", size=20, color="var(--yellow-9)"),
                rx.vstack(
                    rx.text("Leveranciers", size="1", color="gray"),
                    rx.text(ScopeState.supplier_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        columns=rx.breakpoints(initial="2", sm="3", md="5"),
        spacing="3",
        width="100%",
    )


def scopes_content() -> rx.Component:
    """Scopes page content."""
    return rx.vstack(
        # Success message
        rx.cond(
            ScopeState.success_message != "",
            rx.callout(
                ScopeState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),

        # Error message
        rx.cond(
            ScopeState.error != "",
            rx.callout(
                ScopeState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        stat_cards(),
        filter_bar(),

        # Table (desktop)
        rx.box(
            rx.card(
                scopes_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="none", md="block"),
        ),
        # Mobile cards
        rx.box(
            rx.vstack(
                rx.cond(
                    ScopeState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        ScopeState.scopes.length() > 0,
                        rx.foreach(ScopeState.scopes, scope_mobile_card),
                        rx.center(rx.text("Geen scopes gevonden", color="gray"), padding="40px"),
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="block", md="none"),
        ),

        # Dialogs
        scope_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        spacing="4",
        on_mount=ScopeState.load_scopes,
    )


def scopes_page() -> rx.Component:
    """Scopes page with layout."""
    return layout(
        rx.cond(
            AuthState.can_configure,
            scopes_content(),
            rx.callout(
                "Je hebt onvoldoende rechten om deze pagina te bekijken.",
                icon="shield-alert",
                color_scheme="red",
                size="3",
            ),
        ),
        title="Scopes",
        subtitle="Organisatie, processen en assets beheren",
    )
