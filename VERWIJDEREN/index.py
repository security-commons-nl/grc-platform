"""
Dashboard Page - Main landing page after login
"""
import reflex as rx
from ims.state.auth import AuthState
from ims.state.risk import RiskState
from ims.components.layout import layout
from ims.components.heatmap import leiden_heatmap


def stat_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Statistics card for dashboard."""
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


def dashboard_content() -> rx.Component:
    """Dashboard main content."""
    return rx.vstack(
        # Welcome message
        rx.hstack(
            rx.vstack(
                rx.heading(
                    rx.fragment("Welkom, ", AuthState.user_display_name),
                    size="6",
                ),
                rx.text(
                    "Hier is een overzicht van uw GRC status.",
                    size="2",
                    color="gray",
                ),
                align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=16),
                "Vernieuwen",
                variant="soft",
                on_click=RiskState.load_heatmap,
            ),
            width="100%",
            padding_bottom="24px",
        ),

        # Stats row
        rx.grid(
            stat_card("Totaal Risico's", RiskState.total_risks, "triangle-alert", "orange"),
            stat_card("Te Mitigeren", RiskState.mitigate_risks.length(), "shield-alert", "red"),
            stat_card("Zekerheid", RiskState.assurance_risks.length(), "shield-check", "blue"),
            stat_card("Geaccepteerd", RiskState.accept_risks.length(), "circle-check", "green"),
            columns="4",
            spacing="4",
            width="100%",
        ),

        # Heatmap
        rx.box(
            rx.card(
                leiden_heatmap(),
                padding="20px",
            ),
            width="100%",
            margin_top="24px",
        ),

        # Quick actions
        rx.box(
            rx.card(
                rx.vstack(
                    rx.heading("Snelle Acties", size="4"),
                    rx.hstack(
                        rx.button(
                            rx.icon("plus", size=16),
                            "Nieuw Risico",
                            variant="soft",
                        ),
                        rx.button(
                            rx.icon("clipboard-check", size=16),
                            "Start Assessment",
                            variant="soft",
                        ),
                        rx.button(
                            rx.icon("circle-alert", size=16),
                            "Meld Incident",
                            variant="soft",
                            color_scheme="red",
                        ),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="3",
                ),
                padding="20px",
            ),
            width="100%",
            margin_top="24px",
        ),

        width="100%",
        spacing="0",
        on_mount=RiskState.load_heatmap,
    )


def dashboard_page() -> rx.Component:
    """Dashboard page with layout."""
    return layout(
        dashboard_content(),
        title="Dashboard",
        subtitle="Governance, Risk & Compliance overzicht",
    )
