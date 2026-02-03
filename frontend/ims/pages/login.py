"""
Login Page
"""
import reflex as rx
from ims.state.auth import AuthState


def login_page() -> rx.Component:
    """Login page component."""
    return rx.center(
        rx.card(
            rx.vstack(
                # Logo
                rx.hstack(
                    rx.icon("shield-check", size=32, color="var(--accent-9)"),
                    rx.heading("IMS", size="7"),
                    spacing="2",
                    justify="center",
                ),
                rx.text(
                    "Integrated Management System",
                    size="2",
                    color="gray",
                    text_align="center",
                ),

                rx.divider(margin_y="16px"),

                # Login form
                rx.form(
                    rx.vstack(
                        rx.text("Gebruikersnaam", size="2", weight="medium"),
                        rx.input(
                            placeholder="Voer gebruikersnaam in",
                            value=AuthState.username,
                            on_change=AuthState.set_username,
                            width="100%",
                            size="3",
                        ),

                        rx.text("Wachtwoord", size="2", weight="medium", margin_top="12px"),
                        rx.input(
                            placeholder="Voer wachtwoord in",
                            type="password",
                            value=AuthState.password,
                            on_change=AuthState.set_password,
                            width="100%",
                            size="3",
                        ),

                        rx.cond(
                            AuthState.login_error != "",
                            rx.callout(
                                AuthState.login_error,
                                icon="circle-alert",
                                color="red",
                                margin_top="12px",
                            ),
                        ),

                        rx.button(
                            rx.cond(
                                AuthState.is_logging_in,
                                rx.hstack(
                                    rx.spinner(size="1"),
                                    rx.text("Inloggen..."),
                                    spacing="2",
                                ),
                                rx.text("Inloggen"),
                            ),
                            type="submit",
                            width="100%",
                            size="3",
                            margin_top="16px",
                            disabled=AuthState.is_logging_in,
                        ),

                        spacing="1",
                        width="100%",
                    ),
                    on_submit=lambda _: AuthState.login(),
                    width="100%",
                ),

                rx.divider(margin_y="16px"),

                rx.text(
                    "Demo: voer een willekeurige gebruikersnaam in",
                    size="1",
                    color="gray",
                    text_align="center",
                ),

                spacing="2",
                width="100%",
                padding="24px",
            ),
            width="100%",
            max_width="400px",
        ),
        height="100vh",
        background="var(--gray-a2)",
    )
