"""
Assets Page - Asset Register Management
Displays and manages Scopes of type ASSET
"""
import reflex as rx
from ims.state.asset import AssetState
from ims.components.layout import layout


def stat_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Statistics card."""
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color=f"var(--{color}-9)"),
                padding="12px",
                background=f"var(--{color}-a3)",
                border_radius="lg",
            ),
            rx.vstack(
                rx.text(title, size="2", color="gray"),
                rx.text(value, size="5", weight="bold"),
                align_items="start",
                spacing="0",
            ),
            spacing="3",
        ),
        padding="16px",
    )


def asset_type_badge(asset_type: str) -> rx.Component:
    """Badge for asset type."""
    return rx.match(
        asset_type,
        ("Hardware", rx.badge("Hardware", color_scheme="blue", variant="soft")),
        ("Software", rx.badge("Software", color_scheme="purple", variant="soft")),
        ("Data", rx.badge("Data", color_scheme="green", variant="soft")),
        ("People", rx.badge("Mensen", color_scheme="orange", variant="soft")),
        ("Facility", rx.badge("Faciliteit", color_scheme="brown", variant="soft")),
        ("Service", rx.badge("Service", color_scheme="cyan", variant="soft")),
        ("Network", rx.badge("Netwerk", color_scheme="indigo", variant="soft")),
        rx.badge("Onbekend", color_scheme="gray", variant="outline"),
    )


def classification_badge(classification: str) -> rx.Component:
    """Badge for data classification."""
    return rx.match(
        classification,
        ("Public", rx.badge("Openbaar", color_scheme="green", variant="soft")),
        ("Internal", rx.badge("Intern", color_scheme="blue", variant="soft")),
        ("Confidential", rx.badge("Vertrouwelijk", color_scheme="orange", variant="soft")),
        ("Secret", rx.badge("Geheim", color_scheme="red", variant="soft")),
        rx.badge("N.v.t.", color_scheme="gray", variant="outline"),
    )


def asset_form_dialog() -> rx.Component:
    """Dialog for creating/editing an asset."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    AssetState.is_editing,
                    "Asset Bewerken",
                    "Nieuw Asset",
                ),
            ),
            rx.dialog.description(
                "Beheer hardware, software, data en andere bedrijfsmiddelen.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                AssetState.error != "",
                rx.callout(
                    AssetState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.scroll_area(
                rx.vstack(
                    # Basic info
                    rx.text("Basis Informatie", weight="bold", size="3"),

                    rx.vstack(
                        rx.text("Naam *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Bijv. Salarisapplicatie, Fileserver HR",
                            value=AssetState.form_name,
                            on_change=AssetState.set_form_name,
                            width="100%",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    rx.vstack(
                        rx.text("Beschrijving", size="2", weight="medium"),
                        rx.text_area(
                            placeholder="Korte omschrijving van het asset...",
                            value=AssetState.form_description,
                            on_change=AssetState.set_form_description,
                            width="100%",
                            rows="2",
                        ),
                        align_items="start",
                        width="100%",
                    ),

                    rx.hstack(
                        rx.vstack(
                            rx.text("Eigenaar *", size="2", weight="medium"),
                            rx.input(
                                placeholder="Asset eigenaar",
                                value=AssetState.form_owner,
                                on_change=AssetState.set_form_owner,
                                width="100%",
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Onderdeel van", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Selecteer parent"),
                                rx.select.content(
                                    rx.select.item("Geen parent", value="none"),
                                    rx.foreach(
                                        AssetState.available_parents,
                                        lambda p: rx.select.item(
                                            rx.fragment(p["name"], " (", p["type"], ")"),
                                            value=p["id"],
                                        ),
                                    ),
                                ),
                                value=AssetState.form_parent_id,
                                on_change=AssetState.set_form_parent_id,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    rx.divider(),

                    # Asset specific
                    rx.text("Asset Details", weight="bold", size="3"),

                    rx.hstack(
                        rx.vstack(
                            rx.text("Asset Type *", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Type"),
                                rx.select.content(
                                    rx.select.item("Hardware", value="Hardware"),
                                    rx.select.item("Software", value="Software"),
                                    rx.select.item("Data", value="Data"),
                                    rx.select.item("Mensen", value="People"),
                                    rx.select.item("Faciliteit", value="Facility"),
                                    rx.select.item("Service", value="Service"),
                                    rx.select.item("Netwerk", value="Network"),
                                ),
                                value=AssetState.form_asset_type,
                                on_change=AssetState.set_form_asset_type,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Locatie", size="2", weight="medium"),
                            rx.input(
                                placeholder="Bijv. Datacenter A",
                                value=AssetState.form_location,
                                on_change=AssetState.set_form_location,
                                width="100%",
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    rx.divider(),

                    # Classification
                    rx.text("Classificatie (BIV)", weight="bold", size="3"),

                    rx.hstack(
                        rx.vstack(
                            rx.text("Data Classificatie", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Classificatie"),
                                rx.select.content(
                                    rx.select.item("Openbaar", value="Public"),
                                    rx.select.item("Intern", value="Internal"),
                                    rx.select.item("Vertrouwelijk", value="Confidential"),
                                    rx.select.item("Geheim", value="Secret"),
                                ),
                                value=AssetState.form_data_classification,
                                on_change=AssetState.set_form_data_classification,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Beschikbaarheid", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Rating"),
                                rx.select.content(
                                    rx.select.item("Laag", value="Public"),
                                    rx.select.item("Gemiddeld", value="Internal"),
                                    rx.select.item("Hoog", value="Confidential"),
                                    rx.select.item("Kritiek", value="Secret"),
                                ),
                                value=AssetState.form_availability_rating,
                                on_change=AssetState.set_form_availability_rating,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    rx.hstack(
                        rx.vstack(
                            rx.text("Integriteit", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Rating"),
                                rx.select.content(
                                    rx.select.item("Laag", value="Public"),
                                    rx.select.item("Gemiddeld", value="Internal"),
                                    rx.select.item("Hoog", value="Confidential"),
                                    rx.select.item("Kritiek", value="Secret"),
                                ),
                                value=AssetState.form_integrity_rating,
                                on_change=AssetState.set_form_integrity_rating,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Vertrouwelijkheid", size="2", weight="medium"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Rating"),
                                rx.select.content(
                                    rx.select.item("Laag", value="Public"),
                                    rx.select.item("Gemiddeld", value="Internal"),
                                    rx.select.item("Hoog", value="Confidential"),
                                    rx.select.item("Kritiek", value="Secret"),
                                ),
                                value=AssetState.form_confidentiality_rating,
                                on_change=AssetState.set_form_confidentiality_rating,
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    rx.divider(),

                    # Recovery objectives
                    rx.text("Recovery Doelen (BCM)", weight="bold", size="3"),

                    rx.hstack(
                        rx.vstack(
                            rx.text("RTO (uren)", size="2", weight="medium"),
                            rx.input(
                                placeholder="Recovery Time",
                                value=AssetState.form_rto_hours,
                                on_change=AssetState.set_form_rto_hours,
                                type="number",
                                width="100%",
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("RPO (uren)", size="2", weight="medium"),
                            rx.input(
                                placeholder="Recovery Point",
                                value=AssetState.form_rpo_hours,
                                on_change=AssetState.set_form_rpo_hours,
                                type="number",
                                width="100%",
                            ),
                            align_items="start",
                            flex="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    spacing="3",
                    width="100%",
                ),
                type="auto",
                scrollbars="vertical",
                max_height="60vh",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=AssetState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(AssetState.is_editing, "Opslaan", "Toevoegen"),
                    on_click=AssetState.save_asset,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width="600px",
        ),
        open=AssetState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming asset deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Asset Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit asset wilt verwijderen?"),
                    rx.text(AssetState.deleting_asset_name, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=AssetState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=AssetState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=AssetState.show_delete_dialog,
    )


def asset_row(asset: dict) -> rx.Component:
    """Single row in assets table."""
    return rx.table.row(
        rx.table.cell(rx.text(asset["id"], size="2", color="gray")),
        rx.table.cell(
            rx.vstack(
                rx.text(asset["name"], weight="medium", size="2"),
                rx.cond(
                    asset.get("location"),
                    rx.text(asset["location"], size="1", color="gray"),
                    rx.text("Geen locatie", size="1", color="gray"),
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(asset_type_badge(asset.get("asset_type", ""))),
        rx.table.cell(classification_badge(asset.get("data_classification", ""))),
        rx.table.cell(
            rx.cond(
                asset.get("owner"),
                rx.text(asset["owner"], size="2"),
                rx.text("-", size="2"),
            ),
        ),
        rx.table.cell(
            rx.cond(
                asset.get("rto_hours"),
                rx.badge(rx.fragment("RTO: ", asset["rto_hours"], "h"), variant="outline", size="1"),
                rx.text("-", size="2", color="gray"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: AssetState.open_edit_dialog(asset["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: AssetState.open_delete_dialog(asset["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def assets_table() -> rx.Component:
    """Assets data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Asset"),
                rx.table.column_header_cell("Type", width="100px"),
                rx.table.column_header_cell("Classificatie", width="120px"),
                rx.table.column_header_cell("Eigenaar", width="120px"),
                rx.table.column_header_cell("RTO", width="80px"),
                rx.table.column_header_cell("Acties", width="80px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                AssetState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(rx.spinner(size="2"), width="100%", padding="40px"),
                        col_span=7,
                    ),
                ),
                rx.cond(
                    AssetState.filtered_assets.length() > 0,
                    rx.foreach(AssetState.filtered_assets, asset_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("server", size=32, color="gray"),
                                    rx.text("Geen assets gevonden", color="gray"),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Voeg eerste asset toe",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=AssetState.open_create_dialog,
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=7,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def filter_bar() -> rx.Component:
    """Filter bar for assets."""
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(placeholder="Asset Type"),
            rx.select.content(
                rx.select.item("Alle types", value="ALLE"),
                rx.select.item("Hardware", value="Hardware"),
                rx.select.item("Software", value="Software"),
                rx.select.item("Data", value="Data"),
                rx.select.item("Mensen", value="People"),
                rx.select.item("Service", value="Service"),
                rx.select.item("Netwerk", value="Network"),
            ),
            value=AssetState.filter_asset_type,
            on_change=AssetState.set_filter_asset_type,
            size="2",
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Classificatie"),
            rx.select.content(
                rx.select.item("Alle classificaties", value="ALLE"),
                rx.select.item("Openbaar", value="Public"),
                rx.select.item("Intern", value="Internal"),
                rx.select.item("Vertrouwelijk", value="Confidential"),
                rx.select.item("Geheim", value="Secret"),
            ),
            value=AssetState.filter_classification,
            on_change=AssetState.set_filter_classification,
            size="2",
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=AssetState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuw Asset",
            size="2",
            on_click=AssetState.open_create_dialog,
        ),
        width="100%",
        spacing="2",
    )


def assets_content() -> rx.Component:
    """Assets page content."""
    return rx.vstack(
        rx.cond(
            AssetState.success_message != "",
            rx.callout(
                AssetState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),

        rx.cond(
            AssetState.error != "",
            rx.callout(
                AssetState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        # Stats
        rx.grid(
            stat_card("Totaal Assets", AssetState.total_assets, "server", "blue"),
            stat_card("Hardware", AssetState.hardware_count, "hard-drive", "indigo"),
            stat_card("Software", AssetState.software_count, "app-window", "purple"),
            stat_card("Data", AssetState.data_count, "database", "green"),
            columns="4",
            spacing="4",
            width="100%",
        ),

        # Filter bar
        rx.box(
            rx.card(filter_bar(), padding="16px"),
            width="100%",
            margin_top="16px",
        ),

        # Table
        rx.box(
            rx.card(assets_table(), padding="0"),
            width="100%",
            margin_top="16px",
        ),

        # Dialogs
        asset_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        on_mount=AssetState.load_assets,
    )


def assets_page() -> rx.Component:
    """Assets page with layout."""
    return layout(
        assets_content(),
        title="Asset Register",
        subtitle="Beheer hardware, software en andere bedrijfsmiddelen",
    )
