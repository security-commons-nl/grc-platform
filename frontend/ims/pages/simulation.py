"""
Simulation Page - Monte Carlo Simulation for Risk Analysis
"""
import reflex as rx
from ims.state.simulation import SimulationState
from ims.components.layout import layout
from ims.state.auth import AuthState
from typing import Any

def config_input(label: str, value: rx.Var, on_change: Any, unit: str = "") -> rx.Component:
    """Helper for config input fields."""
    return rx.vstack(
        rx.text(label, size="1", color="gray"),
        rx.input(
            value=value.to_string(),
            on_change=on_change,
            type="number",
            size="2",
        ),
        rx.cond(unit != "", rx.text(unit, size="1", color="gray")),
        spacing="1",
        width="100%",
    )

def config_row(level: str, freq_min: rx.Var, freq_max: rx.Var, imp_min: rx.Var, imp_max: rx.Var,
               set_freq_min: Any, set_freq_max: Any, set_imp_min: Any, set_imp_max: Any) -> rx.Component:
    """Row for configuration table."""
    return rx.table.row(
        rx.table.cell(rx.badge(level, variant="soft")),
        rx.table.cell(
            rx.hstack(
                config_input("Min", freq_min, set_freq_min),
                rx.text("-", padding_top="24px"),
                config_input("Max", freq_max, set_freq_max),
                spacing="2",
            )
        ),
        rx.table.cell(
            rx.hstack(
                config_input("Min (€)", imp_min, set_imp_min),
                rx.text("-", padding_top="24px"),
                config_input("Max (€)", imp_max, set_imp_max),
                spacing="2",
            )
        ),
    )

def configuration_tab() -> rx.Component:
    """Configuration tab content."""
    return rx.vstack(
        rx.heading("Parameters", size="4"),
        rx.text("Stel de kwantitatieve waardes in voor de kwalitatieve labels.", color="gray", size="2"),

        # Iterations & Currency
        rx.hstack(
            rx.vstack(
                rx.text("Aantal iteraties", weight="bold"),
                rx.input(
                    value=SimulationState.iterations.to_string(),
                    on_change=SimulationState.set_iterations,
                    type="number"
                ),
                align_items="start",
            ),
            rx.vstack(
                rx.text("Valuta", weight="bold"),
                rx.input(
                    value=SimulationState.currency,
                    on_change=SimulationState.set_currency,
                ),
                align_items="start",
            ),
            spacing="4",
            margin_bottom="16px",
        ),

        # Main Table
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Niveau"),
                    rx.table.column_header_cell("Frequentie (per jaar)"),
                    rx.table.column_header_cell("Financiële Impact"),
                ),
            ),
            rx.table.body(
                config_row("LOW", SimulationState.low_freq_min, SimulationState.low_freq_max, SimulationState.low_imp_min, SimulationState.low_imp_max,
                           SimulationState.set_low_freq_min, SimulationState.set_low_freq_max, SimulationState.set_low_imp_min, SimulationState.set_low_imp_max),
                config_row("MEDIUM", SimulationState.med_freq_min, SimulationState.med_freq_max, SimulationState.med_imp_min, SimulationState.med_imp_max,
                           SimulationState.set_med_freq_min, SimulationState.set_med_freq_max, SimulationState.set_med_imp_min, SimulationState.set_med_imp_max),
                config_row("HIGH", SimulationState.high_freq_min, SimulationState.high_freq_max, SimulationState.high_imp_min, SimulationState.high_imp_max,
                           SimulationState.set_high_freq_min, SimulationState.set_high_freq_max, SimulationState.set_high_imp_min, SimulationState.set_high_imp_max),
                config_row("CRITICAL", SimulationState.crit_freq_min, SimulationState.crit_freq_max, SimulationState.crit_imp_min, SimulationState.crit_imp_max,
                           SimulationState.set_crit_freq_min, SimulationState.set_crit_freq_max, SimulationState.set_crit_imp_min, SimulationState.set_crit_imp_max),
            ),
            variant="surface",
        ),

        # Category Overrides
        rx.heading("Categorie Overrides (JSON)", size="3", margin_top="24px"),
        rx.text("Specifieke instellingen per risicocategorie.", color="gray", size="2"),
        rx.text_area(
            value=SimulationState.category_configs_json,
            on_change=SimulationState.set_category_configs_json,
            rows="5",
            placeholder='{"Legal": {"CRITICAL": {"impact_min": 1000000}}}',
            width="100%",
            font_family="monospace",
        ),

        # Save Button
        rx.button(
            "Instellingen Opslaan",
            on_click=SimulationState.save_config,
            margin_top="16px",
        ),

        rx.cond(
            SimulationState.success_message != "",
            rx.callout(
                SimulationState.success_message,
                icon="check",
                color="green",
                margin_top="16px",
            ),
        ),
        rx.cond(
            SimulationState.error != "",
            rx.callout(
                SimulationState.error,
                icon="triangle-alert",
                color="red",
                margin_top="16px",
            ),
        ),

        padding="16px",
        width="100%",
    )

def stat_card(title: str, value: str, icon: str, color: str) -> rx.Component:
    """Result statistic card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, color=f"var(--{color}-10)"),
                rx.text(title, color="gray", size="2"),
                spacing="2",
            ),
            rx.text(value, size="6", weight="bold"),
            align_items="start",
        ),
        width="100%",
    )

def histogram_bar(bar_data: dict) -> rx.Component:
    """Single bar in histogram."""
    # We need max count to calculate height percentage.
    # But doing max in reflex vars inside loop is hard.
    # We will assume backend returns normalized data or handled via logic?
    # Actually, let's just use CSS height if we can compute max in state.
    # For now, let's assume 'count' is raw.
    # NOTE: Reflex looping makes `max` hard.
    # I'll rely on the backend or state to normalize?
    # Let's make bars flexible.

    return rx.vstack(
        rx.tooltip(
            rx.box(
                width="100%",
                height=f"{bar_data['count']}px", # Scaling might be an issue.
                # Better: Use a computed height in state or assume CSS handles relative?
                # Using fixed px height based on count is risky if count is 10000.
                # I'll stick to a simple vertical list of bars if I can't normalize easily.
                # Actually, I can use a flex row and set height via style.
                # But calculating percentage requires knowing the max.
                background="var(--accent-9)",
                border_radius="4px 4px 0 0",
                transition="height 0.5s",
                min_height="4px",
            ),
            content=f"Verlies: {bar_data['range']} | Aantal: {bar_data['count']}",
        ),
        rx.text(bar_data["range"], size="1", color="gray", style={"writing-mode": "vertical-rl"}),
        align_items="center",
        justify_content="end",
        height="300px", # Container height
        width="40px",
        spacing="2",
    )

def simulation_tab() -> rx.Component:
    """Simulation tab content."""
    return rx.vstack(
        rx.hstack(
            rx.heading("Kwantitatieve Risico Analyse (Monte Carlo)", size="4"),
            rx.spacer(),
            rx.button(
                rx.cond(
                    SimulationState.is_running,
                    rx.spinner(size="1"),
                    rx.icon("play", size=16),
                ),
                "Start Simulatie",
                on_click=SimulationState.run_simulation,
                disabled=SimulationState.is_running,
            ),
            width="100%",
            margin_bottom="16px",
        ),

        rx.cond(
            SimulationState.has_results,
            rx.vstack(
                # Stats
                rx.grid(
                    stat_card("Verwacht Jaarlijks Verlies", SimulationState.mean_loss_formatted, "trending-down", "blue"),
                    stat_card("VaR (95%)", SimulationState.var95_formatted, "shield-alert", "orange"),
                    stat_card("VaR (99%)", SimulationState.var99_formatted, "shield-alert", "red"),
                    stat_card("Iteraties", SimulationState.iterations.to_string(), "repeat", "gray"),
                    columns=rx.breakpoints(initial="1", sm="2", md="4"),
                    spacing="4",
                    width="100%",
                ),

                # Histogram
                rx.card(
                    rx.vstack(
                        rx.text("Verlies Distributie (Histogram)", weight="medium"),
                        rx.scroll_area(
                            rx.hstack(
                                rx.foreach(
                                    SimulationState.histogram_data_normalized,
                                    lambda bar: rx.vstack(
                                        rx.box(
                                            height=bar["height_pct"],
                                            min_height="2px",
                                            width="20px",
                                            background="var(--indigo-9)",
                                            border_radius="sm",
                                        ),
                                        rx.tooltip(
                                            rx.box(
                                                rx.text(bar["range"], size="1", style={"writing-mode": "vertical-rl", "font-size": "10px"}),
                                                cursor="help",
                                            ),
                                            content=f"Aantal: {bar['count']}",
                                        ),
                                        align_items="center",
                                        justify_content="end",
                                        height="250px",
                                        spacing="1",
                                    )
                                ),
                                align_items="end",
                                spacing="2",
                                padding="16px",
                                height="280px",
                            ),
                            type="always",
                            scrollbars="horizontal",
                        ),
                        align_items="start",
                        width="100%",
                    ),
                    margin_top="24px",
                    width="100%",
                ),
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("chart-bar", size=48, color="gray"),
                    rx.text("Druk op Start om de simulatie te draaien.", color="gray"),
                    spacing="2",
                    padding="40px",
                ),
                width="100%",
            ),
        ),

        width="100%",
    )

def simulation_content() -> rx.Component:
    # return rx.text("Debug Mode")
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Simulatie", value="sim"),
            rx.tabs.trigger("Instellingen", value="config"),
        ),
        rx.tabs.content(
            simulation_tab(),
            value="sim",
            padding="20px",
        ),
        rx.tabs.content(
             configuration_tab(), # Uncommented this
            # rx.text("Configuratie tijdelijk uitgeschakeld"),
            # configuration_tab(),
            value="config",
            padding="20px",
        ),
        default_value="sim",
        width="100%",
        on_mount=SimulationState.load_config,
    )

def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def simulation_page() -> rx.Component:
    return layout(
        rx.cond(AuthState.can_discover, simulation_content(), _no_access()),
        title="Kwantitatieve Analyse",
        subtitle="Monte Carlo simulatie en risicokwantificering",
    )
