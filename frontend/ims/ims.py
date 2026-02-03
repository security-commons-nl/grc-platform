"""
IMS - Integrated Management System
Main Reflex Application Entry Point
"""
import reflex as rx

# Import pages
from ims.pages.login import login_page
from ims.pages.index import dashboard_page
from ims.pages.risks import risks_page

# Import state (to ensure it's registered)
from ims.state.auth import AuthState
from ims.state.risk import RiskState


# Create app
app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="medium",
        scaling="95%",
    ),
)

# Add pages
app.add_page(login_page, route="/login", title="Login - IMS")
app.add_page(dashboard_page, route="/", title="Dashboard - IMS")
app.add_page(risks_page, route="/risks", title="Risico's - IMS")

# Placeholder pages for navigation links
def placeholder_page(title: str):
    """Placeholder page for routes not yet implemented."""
    from ims.components.layout import layout
    return layout(
        rx.center(
            rx.vstack(
                rx.icon("construction", size=48, color="gray"),
                rx.heading(f"{title}", size="5"),
                rx.text("Deze pagina is nog in ontwikkeling.", color="gray"),
                spacing="3",
            ),
            height="400px",
        ),
        title=title,
        subtitle="Binnenkort beschikbaar",
    )

app.add_page(lambda: placeholder_page("Maatregelen"), route="/measures", title="Maatregelen - IMS")
app.add_page(lambda: placeholder_page("Assessments"), route="/assessments", title="Assessments - IMS")
app.add_page(lambda: placeholder_page("Incidenten"), route="/incidents", title="Incidenten - IMS")
app.add_page(lambda: placeholder_page("Beleid"), route="/policies", title="Beleid - IMS")
app.add_page(lambda: placeholder_page("Scopes"), route="/scopes", title="Scopes - IMS")
