"""
AI Chat Island Component

Floating chat panel for interacting with AI agents.
Appears in the bottom-right corner of all pages.
"""
import reflex as rx
from ims.state.chat import ChatState


def chat_message(msg: dict) -> rx.Component:
    """Render a single chat message."""
    is_user = msg["role"] == "user"

    return rx.box(
        rx.hstack(
            rx.cond(
                is_user,
                rx.spacer(),
                rx.fragment(),
            ),
            rx.box(
                rx.markdown(msg["content"]),
                padding="12px 16px",
                border_radius="lg",
                max_width="80%",
                background=rx.cond(
                    is_user,
                    "var(--accent-9)",
                    "var(--gray-3)",
                ),
                color=rx.cond(
                    is_user,
                    "white",
                    "inherit",
                ),
            ),
            rx.cond(
                is_user,
                rx.fragment(),
                rx.spacer(),
            ),
            width="100%",
        ),
        width="100%",
        padding_y="4px",
    )


def chat_input() -> rx.Component:
    """Chat input field and send button."""
    return rx.hstack(
        rx.input(
            id="chat-input",
            placeholder="Stel een vraag...",
            value=ChatState.current_input,
            on_change=ChatState.set_input,
            on_key_down=lambda key: rx.cond(
                key == "Enter",
                ChatState.send_message(),
                None,
            ),
            flex="1",
            size="2",
            auto_focus=True,
        ),
        rx.icon_button(
            rx.icon("send", size=18),
            on_click=ChatState.send_message,
            disabled=ChatState.is_loading,
            size="2",
        ),
        width="100%",
        spacing="2",
    )


def agent_selector() -> rx.Component:
    """Dropdown to select current agent with auto-detect indicator."""
    return rx.vstack(
        # Auto-detected indicator
        rx.hstack(
            rx.icon("sparkles", size=14, color="var(--accent-9)"),
            rx.text(ChatState.agent_display_name, size="1", color="gray"),
            spacing="1",
            align="center",
        ),
        # Dropdown for manual override
        rx.select.root(
            rx.select.trigger(placeholder="Selecteer agent"),
            rx.select.content(
                rx.select.item("Risico Expert", value="risk"),
                rx.select.item("Maatregelen Expert", value="measure"),
                rx.select.item("Beleid Expert", value="policy"),
                rx.select.item("Compliance Expert", value="compliance"),
                rx.select.item("Assessment Expert", value="assessment"),
                rx.select.item("Incident Expert", value="incident"),
                rx.select.item("Privacy Expert", value="privacy"),
                rx.select.item("Continuïteit Expert", value="bcm"),
                rx.select.item("Leverancier Expert", value="supplier"),
                rx.select.item("Rapportage Expert", value="report"),
            ),
            value=ChatState.current_agent,
            on_change=ChatState.set_agent,
            size="1",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def chat_header() -> rx.Component:
    """Chat panel header with agent info and controls."""
    return rx.hstack(
        rx.hstack(
            rx.icon("bot", size=20, color="var(--accent-9)"),
            rx.text(ChatState.agent_display_name, size="2", weight="medium"),
            spacing="2",
        ),
        rx.spacer(),
        rx.hstack(
            rx.icon_button(
                rx.icon("trash-2", size=16),
                variant="ghost",
                size="1",
                on_click=ChatState.clear_chat,
            ),
            rx.icon_button(
                rx.icon("x", size=16),
                variant="ghost",
                size="1",
                on_click=ChatState.close_chat,
            ),
            spacing="1",
        ),
        width="100%",
        padding="12px 16px",
        border_bottom="1px solid var(--gray-5)",
    )


def chat_panel() -> rx.Component:
    """The main chat panel (shown when open)."""
    return rx.box(
        rx.vstack(
            # Header
            chat_header(),

            # Agent selector
            rx.box(
                agent_selector(),
                padding="8px 16px",
                border_bottom="1px solid var(--gray-5)",
                width="100%",
            ),

            # Messages area
            rx.box(
                rx.foreach(
                    ChatState.messages,
                    chat_message,
                ),
                rx.cond(
                    ChatState.is_loading,
                    rx.box(
                        rx.hstack(
                            rx.box(
                                rx.hstack(
                                    rx.spinner(size="1"),
                                    rx.el.span(
                                        "Bezig met denken",
                                        class_name="typing-dots",
                                        font_size="var(--font-size-2)",
                                        color="var(--gray-11)",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="12px 16px",
                                border_radius="lg",
                                max_width="80%",
                                background="var(--gray-3)",
                            ),
                            rx.spacer(),
                            width="100%",
                        ),
                        width="100%",
                        padding_y="4px",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    ~ChatState.has_messages & ~ChatState.is_loading,
                    rx.vstack(
                        rx.icon("message-circle", size=32, color="var(--gray-8)"),
                        rx.text(
                            "Stel een vraag aan de AI assistent",
                            size="2",
                            color="gray",
                            text_align="center",
                        ),
                        padding="24px",
                        align_items="center",
                        justify_content="center",
                        height="100%",
                    ),
                    rx.fragment(),
                ),
                flex="1",
                overflow_y="auto",
                padding="12px 16px",
                width="100%",
                id="chat-messages-container",
            ),

            # Input area
            rx.box(
                chat_input(),
                padding="12px 16px",
                border_top="1px solid var(--gray-5)",
                width="100%",
            ),

            height="100%",
            width="100%",
            spacing="0",
        ),
        position="fixed",
        bottom=rx.breakpoints(initial="70px", md="80px"),
        right=rx.breakpoints(initial="8px", md="20px"),
        width=rx.breakpoints(initial="calc(100vw - 16px)", md="380px"),
        height=rx.breakpoints(initial="60vh", md="500px"),
        background="var(--color-background)",
        border="1px solid var(--gray-5)",
        border_radius="lg",
        box_shadow="0 10px 40px rgba(0,0,0,0.15)",
        z_index="1000",
        display=rx.cond(ChatState.is_open, "flex", "none"),
    )


def chat_toggle_button() -> rx.Component:
    """Floating button to toggle chat panel."""
    return rx.box(
        rx.icon_button(
            rx.icon("message-circle", size=24),
            size="4",
            radius="full",
            on_click=ChatState.toggle_chat,
            variant="solid",
        ),
        position="fixed",
        bottom="20px",
        right="20px",
        z_index="1000",
    )


def chat_island() -> rx.Component:
    """
    Complete Chat Island component.

    Add this to your layout to enable AI chat on all pages:

        layout(
            your_content(),
            chat_island(),
        )
    """
    return rx.fragment(
        chat_panel(),
        chat_toggle_button(),
    )
