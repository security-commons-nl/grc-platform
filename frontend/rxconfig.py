import reflex as rx

config = rx.Config(
    app_name="ims",
    title="IMS - Integrated Management System",
    description="Governance, Risk & Compliance Platform",

    # Tailwind configuration
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "brand": {
                        "50": "#eff6ff",
                        "100": "#dbeafe",
                        "500": "#3b82f6",
                        "600": "#2563eb",
                        "700": "#1d4ed8",
                        "900": "#1e3a8a",
                    },
                    "risk": {
                        "low": "#22c55e",
                        "medium": "#eab308",
                        "high": "#f97316",
                        "critical": "#ef4444",
                    },
                    "quadrant": {
                        "mitigate": "#fee2e2",
                        "assurance": "#dbeafe",
                        "monitor": "#fef3c7",
                        "accept": "#dcfce7",
                    }
                }
            }
        }
    },
)
