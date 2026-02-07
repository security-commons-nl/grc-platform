"""
Suppliers Page - Vendor/Supplier Management
Displays and manages Scopes of type SUPPLIER
"""
import reflex as rx
from ims.state.supplier import SupplierState
from ims.state.auth import AuthState
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


def supplier_form_dialog() -> rx.Component:
    """Dialog for creating/editing a supplier."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    SupplierState.is_editing,
                    "Leverancier Bewerken",
                    "Nieuwe Leverancier",
                ),
            ),
            rx.dialog.description(
                "Beheer leveranciers en hun contactgegevens.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                SupplierState.error != "",
                rx.callout(
                    SupplierState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Basic info
                rx.text("Leverancier Informatie", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Bedrijfsnaam *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. Microsoft, Salesforce",
                        value=SupplierState.form_name,
                        on_change=SupplierState.set_form_name,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Beschrijving", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Welke diensten levert deze leverancier?",
                        value=SupplierState.form_description,
                        on_change=SupplierState.set_form_description,
                        width="100%",
                        rows="2",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.flex(
                    rx.vstack(
                        rx.text("Interne Eigenaar *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Contracteigenaar intern",
                            value=SupplierState.form_owner,
                            on_change=SupplierState.set_form_owner,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Gekoppeld aan", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer scope"),
                            rx.select.content(
                                rx.select.item("Geen koppeling", value="0"),
                                rx.foreach(
                                    SupplierState.available_parents,
                                    lambda p: rx.select.item(
                                        rx.fragment(p["name"], " (", p["type"], ")"),
                                        value=p["id"],
                                    ),
                                ),
                            ),
                            value=SupplierState.form_parent_id,
                            on_change=SupplierState.set_form_parent_id,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                ),

                rx.divider(),

                # Contact info
                rx.text("Contactpersoon Leverancier", weight="bold", size="3"),

                rx.flex(
                    rx.vstack(
                        rx.text("Contactpersoon", size="2", weight="medium"),
                        rx.input(
                            placeholder="Naam contactpersoon",
                            value=SupplierState.form_vendor_contact_name,
                            on_change=SupplierState.set_form_vendor_contact_name,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("E-mail", size="2", weight="medium"),
                        rx.input(
                            placeholder="contact@leverancier.nl",
                            value=SupplierState.form_vendor_contact_email,
                            on_change=SupplierState.set_form_vendor_contact_email,
                            type="email",
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                ),

                spacing="3",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=SupplierState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(SupplierState.is_editing, "Opslaan", "Toevoegen"),
                    on_click=SupplierState.save_supplier,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="550px"),
        ),
        open=SupplierState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming supplier deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Leverancier Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze leverancier wilt verwijderen?"),
                    rx.text(SupplierState.deleting_supplier_name, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=SupplierState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=SupplierState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=SupplierState.show_delete_dialog,
    )


def supplier_row(supplier: dict) -> rx.Component:
    """Single row in suppliers table."""
    return rx.table.row(
        rx.table.cell(rx.text(supplier["id"], size="2", color="gray")),
        rx.table.cell(
            rx.vstack(
                rx.text(supplier["name"], weight="medium", size="2"),
                rx.cond(
                    supplier["description"],
                    rx.text(supplier["description"], size="1", color="gray", no_of_lines=1),
                    rx.text("Geen beschrijving", size="1", color="gray"),
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.vstack(
                rx.cond(
                    supplier["vendor_contact_name"],
                    rx.text(supplier["vendor_contact_name"], size="2"),
                    rx.text("-", size="2"),
                ),
                rx.cond(
                    supplier["vendor_contact_email"],
                    rx.text(supplier["vendor_contact_email"], size="1", color="blue"),
                    rx.text("-", size="1", color="gray"),
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.cond(
                supplier["owner"],
                rx.text(supplier["owner"], size="2"),
                rx.text("-", size="2"),
            ),
        ),
        rx.table.cell(
            rx.badge("Actief", color_scheme="green", variant="soft"),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: SupplierState.open_edit_dialog(supplier["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: SupplierState.open_delete_dialog(supplier["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def supplier_mobile_card(supplier: dict) -> rx.Component:
    """Mobile card view for a single supplier."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(supplier["name"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: SupplierState.open_edit_dialog(supplier["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: SupplierState.open_delete_dialog(supplier["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                supplier["vendor_contact_name"],
                rx.text(supplier["vendor_contact_name"], size="1", color="gray"),
                rx.text("-", size="1", color="gray"),
            ),
            rx.hstack(
                rx.badge("Actief", color_scheme="green", variant="soft", size="1"),
                rx.cond(
                    supplier["owner"],
                    rx.text(supplier["owner"], size="1", color="gray"),
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def suppliers_table() -> rx.Component:
    """Suppliers data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Leverancier"),
                rx.table.column_header_cell("Contact", width="180px"),
                rx.table.column_header_cell("Eigenaar", width="120px"),
                rx.table.column_header_cell("Status", width="100px"),
                rx.table.column_header_cell("Acties", width="80px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                SupplierState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(rx.spinner(size="2"), width="100%", padding="40px"),
                        col_span=6,
                    ),
                ),
                rx.cond(
                    SupplierState.suppliers.length() > 0,
                    rx.foreach(SupplierState.suppliers, supplier_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("building-2", size=32, color="gray"),
                                    rx.text("Geen leveranciers gevonden", color="gray"),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Voeg eerste leverancier toe",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=SupplierState.open_create_dialog,
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
    """Filter bar for suppliers."""
    return rx.flex(
        rx.input(
            placeholder="Zoek leverancier...",
            width=rx.breakpoints(initial="100%", md="auto"),
            style={"min_width": "200px"},
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuwe Leverancier",
            size="2",
            on_click=SupplierState.open_create_dialog,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def suppliers_content() -> rx.Component:
    """Suppliers page content."""
    return rx.vstack(
        rx.cond(
            SupplierState.success_message != "",
            rx.callout(
                SupplierState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),

        rx.cond(
            SupplierState.error != "",
            rx.callout(
                SupplierState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        # Stats
        rx.grid(
            stat_card("Totaal Leveranciers", SupplierState.total_suppliers, "building-2", "blue"),
            stat_card("Actieve Contracten", SupplierState.active_contracts, "file-check", "green"),
            stat_card("Binnenkort Verlopend", SupplierState.expiring_soon, "clock", "orange"),
            columns=rx.breakpoints(initial="1", sm="2", md="3"),
            spacing="4",
            width="100%",
        ),

        # Filter bar
        rx.box(
            rx.card(filter_bar(), padding="16px"),
            width="100%",
            margin_top="16px",
        ),

        # Table (desktop)
        rx.box(
            rx.card(suppliers_table(), padding="0"),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="none", md="block"),
        ),
        # Mobile cards
        rx.box(
            rx.vstack(
                rx.cond(
                    SupplierState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        SupplierState.suppliers.length() > 0,
                        rx.foreach(SupplierState.suppliers, supplier_mobile_card),
                        rx.center(rx.text("Geen leveranciers gevonden", color="gray"), padding="40px"),
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
        supplier_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        on_mount=SupplierState.load_suppliers,
    )


def suppliers_page() -> rx.Component:
    """Suppliers page with layout."""
    return layout(
        rx.cond(
            AuthState.can_configure,
            suppliers_content(),
            rx.callout(
                "Je hebt onvoldoende rechten om deze pagina te bekijken.",
                icon="shield-alert",
                color_scheme="red",
                size="3",
            ),
        ),
        title="Leveranciers",
        subtitle="Beheer leveranciers en externe partijen",
    )
