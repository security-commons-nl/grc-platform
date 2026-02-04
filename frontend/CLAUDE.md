# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is the **Reflex frontend** for IMS (Integrated Management System). See the parent `IMS/CLAUDE.md` for overall project architecture. The frontend is a "dumb glass pane" - all business logic resides in the FastAPI backend.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Reflex development server (starts both Python backend on 8001 and Vite dev server)
reflex run

# Requires backend running first:
docker-compose up -d    # From IMS root - starts FastAPI on 8000
```

**Access Points:**
- Frontend: http://localhost:3000 (Reflex default)
- Reflex backend: http://localhost:8001
- FastAPI backend: http://localhost:8000/api/v1

## Architecture

```
ims/
├── ims.py              # App entry point - registers all pages
├── api/client.py       # Async httpx client (singleton: api_client)
├── state/              # Reflex state classes
│   ├── base.py         # BaseState: tenant context, loading, toasts
│   ├── auth.py         # AuthState: localStorage-backed auth
│   └── [domain].py     # Domain states (risk, measure, policy, etc.)
├── pages/              # Page components wrapped in layout()
└── components/
    ├── layout.py       # Sidebar + page_header + auth guard
    └── heatmap.py      # "In Control" risk matrix (4 quadrants)
```

### State Pattern

Each domain state follows this pattern:
```python
class DomainState(rx.State):
    items: List[Dict[str, Any]] = []
    is_loading: bool = False
    error: str = ""
    show_form_dialog: bool = False
    is_editing: bool = False
    form_field: str = ""  # Form fields

    @rx.var
    def computed_property(self) -> int:  # Computed vars
        return len(self.items)

    async def load_items(self):      # Async API calls
    def open_create_dialog(self):    # UI handlers
    async def save_item(self):       # CRUD operations
```

### Page Pattern

Pages use the `layout()` wrapper which handles:
- Authentication guard (redirects to /login if not authenticated)
- Sidebar navigation
- Page header with title/subtitle

```python
def page() -> rx.Component:
    return layout(
        rx.vstack(...content...),
        title="Page Title",
        subtitle="Optional subtitle"
    )
```

### API Client

Use the singleton `api_client` from `ims/api/client.py`:
```python
from ims.api.client import api_client

async def load_data(self):
    self.items = await api_client.get_risks()
```

All API calls are async. Backend base URL: `http://localhost:8000/api/v1`

## Key Conventions

- **Dutch UI**: All labels, placeholders, and messages are in Dutch
- **Conditional rendering**: Use `rx.cond()` for if/else in components
- **Event binding**: Form inputs use `on_change` to update state
- **Dialog pattern**: Modal forms with `show_form_dialog` state toggle
- **On mount**: Pages call `on_mount=State.load_data` to fetch initial data

## Tailwind Colors (rxconfig.py)

- `brand-*`: Blue palette (50, 100, 500, 600, 700, 900)
- `risk-*`: low (green), medium (yellow), high (orange), critical (red)
- `quadrant-*`: mitigate (red), assurance (blue), monitor (yellow), accept (green)
