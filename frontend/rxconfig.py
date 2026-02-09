import os
import reflex as rx

config = rx.Config(
    app_name="ims",
    title="IMS - Integrated Management System",
    description="Governance, Risk & Compliance Platform",

    # Production: browser connects WebSocket to this URL
    # Without this, the frontend tries localhost:8002 which fails for remote users
    # Local dev: set REFLEX_API_URL=http://localhost:8002 in shell
    api_url=os.getenv("REFLEX_API_URL") or "https://i-m-s.nl",

    # Use port 8002 for Reflex backend (8001 is used by FastAPI)
    backend_port=8002,
    frontend_port=3000,

    # Disable telemetry and branding
    telemetry_enabled=False,

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
