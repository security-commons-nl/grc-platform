"""
Guidance Components - Journey stepper, PDCA ring widget, and next-step hints.
Transforms the IMS from passive archive to active coach.
"""
import reflex as rx
from ims.state.journey import JourneyState, STEP_TITLES, STEP_ICONS, STEP_LINKS, STEP_LINK_LABELS


def journey_step_card(
    step_num: int,
    title: str,
    icon: str,
    is_ok: rx.Var,
    blocker_text: rx.Var,
    link_href: str,
    link_label: str,
) -> rx.Component:
    """Single step card in the journey stepper."""
    return rx.hstack(
        # Step number circle
        rx.cond(
            is_ok,
            rx.box(
                rx.icon("check", size=14, color="white"),
                width="28px",
                height="28px",
                min_width="28px",
                background="var(--green-9)",
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.box(
                rx.text(str(step_num), size="2", weight="bold", color="var(--gray-11)"),
                width="28px",
                height="28px",
                min_width="28px",
                background="var(--gray-a4)",
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
        ),
        # Content
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=14, color=rx.cond(is_ok, "var(--green-9)", "var(--gray-9)")),
                rx.text(title, size="2", weight="medium"),
                rx.cond(
                    is_ok,
                    rx.badge("Klaar", color_scheme="green", variant="soft", size="1"),
                    rx.badge("Te doen", color_scheme="gray", variant="outline", size="1"),
                ),
                spacing="2",
                align="center",
            ),
            # Blocker callout (only when not ok)
            rx.cond(
                is_ok,
                rx.fragment(),
                rx.cond(
                    blocker_text != "",
                    rx.vstack(
                        rx.hstack(
                            rx.icon("alert-triangle", size=12, color="var(--orange-9)"),
                            rx.text(blocker_text, size="1", color="var(--orange-11)"),
                            spacing="1",
                            align="center",
                        ),
                        rx.link(
                            rx.button(
                                link_label,
                                variant="soft",
                                size="1",
                                color_scheme="blue",
                            ),
                            href=link_href,
                            text_decoration="none",
                        ),
                        spacing="1",
                    ),
                ),
            ),
            spacing="1",
            align_items="start",
            flex="1",
        ),
        width="100%",
        align="start",
        padding="8px 4px",
        border_bottom="1px solid var(--gray-a4)",
    )


def journey_stepper() -> rx.Component:
    """All 7 journey steps in a vertical list."""
    return rx.vstack(
        journey_step_card(
            1, STEP_TITLES[0], STEP_ICONS[0],
            JourneyState.step1_ok, JourneyState.step1_blocker,
            STEP_LINKS[0], STEP_LINK_LABELS[0],
        ),
        journey_step_card(
            2, STEP_TITLES[1], STEP_ICONS[1],
            JourneyState.step2_ok, JourneyState.step2_blocker,
            STEP_LINKS[1], STEP_LINK_LABELS[1],
        ),
        journey_step_card(
            3, STEP_TITLES[2], STEP_ICONS[2],
            JourneyState.step3_ok, JourneyState.step3_blocker,
            STEP_LINKS[2], STEP_LINK_LABELS[2],
        ),
        journey_step_card(
            4, STEP_TITLES[3], STEP_ICONS[3],
            JourneyState.step4_ok, JourneyState.step4_blocker,
            STEP_LINKS[3], STEP_LINK_LABELS[3],
        ),
        journey_step_card(
            5, STEP_TITLES[4], STEP_ICONS[4],
            JourneyState.step5_ok, JourneyState.step5_blocker,
            STEP_LINKS[4], STEP_LINK_LABELS[4],
        ),
        journey_step_card(
            6, STEP_TITLES[5], STEP_ICONS[5],
            JourneyState.step6_ok, JourneyState.step6_blocker,
            STEP_LINKS[5], STEP_LINK_LABELS[5],
        ),
        journey_step_card(
            7, STEP_TITLES[6], STEP_ICONS[6],
            JourneyState.step7_ok, JourneyState.step7_blocker,
            STEP_LINKS[6], STEP_LINK_LABELS[6],
        ),
        spacing="0",
        width="100%",
    )


def pdca_ring_widget() -> rx.Component:
    """Compact progress card for the dashboard."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("compass", size=20, color="var(--accent-9)"),
                rx.text("IMS Voortgang", size="3", weight="bold"),
                rx.spacer(),
                rx.text(
                    rx.fragment(JourneyState.overall_progress_pct, "%"),
                    size="3",
                    weight="bold",
                    color="var(--accent-9)",
                ),
                width="100%",
                align="center",
            ),
            # Progress bar
            rx.box(
                rx.box(
                    width=rx.cond(
                        JourneyState.overall_progress_pct > 0,
                        JourneyState.overall_progress_pct.to(str) + "%",
                        "0%",
                    ),
                    height="100%",
                    background="var(--accent-9)",
                    border_radius="4px",
                    transition="width 0.5s ease",
                ),
                width="100%",
                height="8px",
                background="var(--gray-a4)",
                border_radius="4px",
                overflow="hidden",
            ),
            rx.hstack(
                rx.cond(
                    JourneyState.current_step <= 7,
                    rx.text(
                        rx.fragment(
                            "Stap ", JourneyState.current_step, " van 7: ",
                            JourneyState.current_step_label,
                        ),
                        size="1",
                        color="gray",
                    ),
                    rx.text(
                        "Alle stappen afgerond!",
                        size="1",
                        color="var(--green-9)",
                        weight="medium",
                    ),
                ),
                rx.spacer(),
                rx.link(
                    rx.button(
                        "Bekijk voortgang",
                        variant="ghost",
                        size="1",
                        color_scheme="blue",
                    ),
                    href="/ms-hub",
                    text_decoration="none",
                ),
                width="100%",
                align="center",
            ),
            spacing="2",
            width="100%",
        ),
        padding="16px",
        width="100%",
    )


def next_step_hint(page: str) -> rx.Component:
    """Contextual hint callout for domain pages. Returns empty fragment if no hint."""
    hint_var = rx.match(
        page,
        ("risks", JourneyState.risks_hint),
        ("controls", JourneyState.controls_hint),
        ("scopes", JourneyState.scopes_hint),
        ("policies", JourneyState.policies_hint),
        "",
    )

    return rx.cond(
        hint_var != "",
        rx.callout(
            rx.text(hint_var, size="2"),
            icon="lightbulb",
            color_scheme="blue",
            width="100%",
            margin_bottom="8px",
        ),
    )
