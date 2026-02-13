import reflex as rx
from ims.components.layout import layout


def leidse_ims_page() -> rx.Component:
    """Leidse IMS - Overzichtspagina."""
    return layout(
        rx.vstack(
            rx.text(
                "Het Leidse IMS overzicht is in ontwikkeling.",
                color="gray",
                size="2",
            ),
            spacing="4",
            width="100%",
        ),
        title="Leidse IMS",
        subtitle="Integrated Management System",
    )
