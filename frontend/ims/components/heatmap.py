"""
Leiden Heatmap Component
Displays risks in the four quadrants: Mitigate, Assurance, Monitor, Accept
"""
import reflex as rx
from ims.state.risk import RiskState


def risk_chip(risk: dict) -> rx.Component:
    """Small chip showing a risk in the heatmap."""
    return rx.box(
        rx.text(
            risk["title"],
            size="1",
            truncate=True,
        ),
        padding="4px 8px",
        background="white",
        border_radius="sm",
        border="1px solid var(--gray-a5)",
        cursor="pointer",
        _hover={"background": "var(--gray-a3)"},
        max_width="150px",
    )


def quadrant_cell(
    title: str,
    subtitle: str,
    risks: rx.Var,
    count: rx.Var,
    bg_color: str,
    icon: str,
) -> rx.Component:
    """A single quadrant in the heatmap."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=18, color="var(--gray-11)"),
                rx.text(title, weight="bold", size="2"),
                rx.badge(
                    count,
                    variant="soft",
                    size="1",
                ),
                spacing="2",
            ),
            rx.text(subtitle, size="1", color="gray"),
            rx.box(
                rx.flex(
                    rx.foreach(
                        risks,
                        risk_chip,
                    ),
                    wrap="wrap",
                    gap="2",
                ),
                margin_top="12px",
            ),
            align_items="start",
            spacing="1",
            width="100%",
        ),
        padding="16px",
        background=bg_color,
        border_radius="lg",
        min_height="180px",
        border="1px solid var(--gray-a5)",
    )


def leiden_heatmap() -> rx.Component:
    """
    Leiden 'In Control' model heatmap.

    Layout:
                     IMPACT
                Laag          Hoog
         ┌────────────┬────────────┐
    Hoog │  MONITOR   │  MITIGATE  │
   Kwets-│            │            │
   baar- ├────────────┼────────────┤
   heid  │   ACCEPT   │ ASSURANCE  │
    Laag │            │            │
         └────────────┴────────────┘
    """
    return rx.box(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("Risico Heatmap", size="4"),
                rx.text("Leiden 'In Control' Model", size="2", color="gray"),
                align_items="start",
            ),
            rx.spacer(),
            rx.badge(
                rx.hstack(
                    rx.text("Totaal:"),
                    rx.text(RiskState.total_risks, weight="bold"),
                    spacing="1",
                ),
                size="2",
                variant="surface",
            ),
            width="100%",
            margin_bottom="16px",
        ),

        # Axis label - Impact (horizontal)
        rx.hstack(
            rx.box(width="60px"),  # Spacer for Y-axis label
            rx.hstack(
                rx.text("Laag impact", size="1", color="gray"),
                rx.spacer(),
                rx.text("Hoog impact", size="1", color="gray"),
                width="100%",
            ),
            width="100%",
            margin_bottom="4px",
        ),

        # Main grid with Y-axis label
        rx.hstack(
            # Y-axis label
            rx.box(
                rx.text(
                    "Kwetsbaarheid",
                    size="1",
                    color="gray",
                    style={"writing-mode": "vertical-rl", "transform": "rotate(180deg)"},
                ),
                width="60px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),

            # Grid
            rx.box(
                rx.grid(
                    # Top row: MONITOR | MITIGATE (high vulnerability)
                    quadrant_cell(
                        "Monitoren",
                        "Lage impact, hoge kwetsbaarheid",
                        RiskState.monitor_risks,
                        RiskState.monitor_risks.length(),
                        "var(--amber-a3)",
                        "eye",
                    ),
                    quadrant_cell(
                        "Mitigeren",
                        "Hoge impact, hoge kwetsbaarheid",
                        RiskState.mitigate_risks,
                        RiskState.mitigate_risks.length(),
                        "var(--red-a3)",
                        "shield-alert",
                    ),

                    # Bottom row: ACCEPT | ASSURANCE (low vulnerability)
                    quadrant_cell(
                        "Accepteren",
                        "Lage impact, lage kwetsbaarheid",
                        RiskState.accept_risks,
                        RiskState.accept_risks.length(),
                        "var(--green-a3)",
                        "circle-check",
                    ),
                    quadrant_cell(
                        "Zekerheid",
                        "Hoge impact, lage kwetsbaarheid",
                        RiskState.assurance_risks,
                        RiskState.assurance_risks.length(),
                        "var(--blue-a3)",
                        "shield-check",
                    ),

                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                flex="1",
            ),

            width="100%",
            align_items="stretch",
        ),

        # Unclassified risks warning
        rx.cond(
            RiskState.unclassified_risks.length() > 0,
            rx.callout(
                "Er zijn risico's zonder kwadrant.",
                icon="triangle-alert",
                color="orange",
                margin_top="16px",
            ),
        ),

        width="100%",
    )
