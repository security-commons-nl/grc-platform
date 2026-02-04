# Technische Beslissingen & Richtlijnen

> **Versie:** 1.1
> **Datum:** Februari 2026
> **Status:** Vastgesteld (Frontend gewijzigd naar Reflex)

---

## Inhoudsopgave

1. [Frontend Stack](#1-frontend-stack)
2. [AI Governance Model](#2-ai-governance-model)
3. [AI Performance Optimalisatie](#3-ai-performance-optimalisatie)

---

## 1. Frontend Stack

### 1.1 Besluit

**Gekozen stack:** Reflex (Python full-stack framework)

### 1.2 Rationale

| Criterium | React+TS | HTMX | Reflex | Besluit |
|-----------|----------|------|--------|---------|
| **100% Python stack** | ❌ | ✅ | ✅ | Reflex ✓ |
| **Complexe UI mogelijk** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Reflex ✓ |
| **Real-time/WebSockets** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Reflex ✓ |
| **Geen JS kennis nodig** | ❌ | ✅ | ✅ | Reflex ✓ |
| **State management** | Extern (Zustand) | Server-side | Ingebouwd | Reflex ✓ |
| **Snelheid ontwikkeling** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Reflex ✓ |
| **Community/maturity** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Acceptabel |

**Waarom Reflex:**
- **Één taal**: Hele stack in Python, geen context-switching
- **React onder de hood**: Compileert naar React, dus moderne UI mogelijk
- **Ingebouwde state**: Geen aparte state management library nodig
- **WebSocket native**: Real-time updates en streaming out-of-the-box
- **FastAPI integratie**: Backend API kan direct gekoppeld worden

### 1.3 Dependencies

```
# requirements.txt (frontend)
reflex>=0.4.0
reflex-chakra              # UI componenten (optioneel, Radix is default)
plotly                     # Grafieken en heatmaps
python-multipart           # File uploads
httpx                      # Async API calls naar backend
```

### 1.4 Project Structuur

```
frontend/
├── ims/                        # Reflex app package
│   ├── __init__.py
│   ├── ims.py                  # Main app entry point
│   │
│   ├── state/                  # Application state
│   │   ├── __init__.py
│   │   ├── base.py             # Base state (loading, errors, toasts)
│   │   ├── auth.py             # Auth state
│   │   ├── risk.py             # Risk state
│   │   ├── measure.py          # Measure state
│   │   ├── assessment.py       # Assessment state
│   │   ├── incident.py         # Incident state
│   │   ├── policy.py           # Policy state
│   │   ├── compliance.py       # Compliance state
│   │   ├── scope.py            # Scope state
│   │   ├── asset.py            # Asset state
│   │   ├── supplier.py         # Supplier state
│   │   └── backlog.py          # Backlog state
│   │
│   ├── pages/                  # Route pages (12 pages)
│   │   ├── __init__.py
│   │   ├── index.py            # Dashboard
│   │   ├── login.py            # Login page
│   │   ├── risks.py            # Risk management
│   │   ├── measures.py         # Measures/controls
│   │   ├── assessments.py      # Assessments
│   │   ├── incidents.py        # Incident management
│   │   ├── policies.py         # Policy management
│   │   ├── compliance.py       # Compliance overview
│   │   ├── scopes.py           # Scope/hierarchy
│   │   ├── assets.py           # Asset inventory
│   │   ├── suppliers.py        # Supplier management
│   │   └── backlog.py          # Backlog/planning
│   │
│   ├── components/             # Reusable components
│   │   ├── __init__.py
│   │   ├── layout.py           # Sidebar, page layout, auth guard
│   │   ├── heatmap.py          # Risk heatmap (In Control model)
│   │   └── deadline.py         # Deadline visualization
│   │
│   └── api/                    # Backend API client
│       ├── __init__.py
│       └── client.py           # httpx async client
│
├── rxconfig.py                 # Reflex configuratie
└── requirements.txt
```

### 1.5 Key UI Componenten

#### AI Chat Island
Altijd zichtbaar onderaan het scherm, context-aware:

```python
# ims/components/chat_island.py
import reflex as rx
from ims.state.chat import ChatState

def chat_message(message: dict) -> rx.Component:
    """Render een chat bericht."""
    is_user = message["role"] == "user"
    return rx.box(
        rx.box(
            rx.text(message["content"]),
            class_name=f"{'bg-blue-100' if is_user else 'bg-gray-100'} rounded-lg p-3",
        ),
        rx.cond(
            message.get("suggestions"),
            suggestion_cards(message["suggestions"]),
        ),
        class_name=f"{'ml-auto' if is_user else 'mr-auto'} max-w-[80%]",
    )

def chat_island() -> rx.Component:
    """AI Chat Island - altijd zichtbaar onderaan scherm."""
    return rx.box(
        # Header
        rx.hstack(
            rx.avatar(src=ChatState.current_agent_avatar, size="sm"),
            rx.vstack(
                rx.text(ChatState.current_agent_name, font_weight="bold"),
                rx.badge(ChatState.current_context, color_scheme="blue"),
                align_items="start",
                spacing="0",
            ),
            rx.spacer(),
            rx.icon_button(rx.icon("settings"), variant="ghost"),
            width="100%",
            padding="3",
            border_bottom="1px solid #eee",
        ),

        # Messages
        rx.scroll_area(
            rx.vstack(
                rx.foreach(ChatState.messages, chat_message),
                spacing="3",
                width="100%",
            ),
            height="300px",
            padding="3",
        ),

        # Input
        rx.hstack(
            rx.input(
                placeholder="Stel een vraag...",
                value=ChatState.input_value,
                on_change=ChatState.set_input_value,
                on_key_down=ChatState.handle_key_down,
                flex="1",
            ),
            rx.icon_button(
                rx.icon("send"),
                on_click=ChatState.send_message,
                is_loading=ChatState.is_streaming,
            ),
            padding="3",
            border_top="1px solid #eee",
        ),

        # Styling
        position="fixed",
        bottom="0",
        right="20px",
        width="400px",
        background="white",
        border_radius="lg",
        box_shadow="xl",
        border="1px solid #ddd",
        z_index="1000",
    )
```

#### Chat State met Streaming

```python
# ims/state/chat.py
import reflex as rx
import httpx
from typing import List, Dict, Any

class ChatState(rx.State):
    """State voor AI Chat Island."""

    messages: List[Dict[str, Any]] = []
    input_value: str = ""
    is_streaming: bool = False

    current_agent_name: str = "Risk Expert"
    current_agent_avatar: str = "/agents/risk.png"
    current_context: str = "Dashboard"

    # Context van huidige pagina
    current_entity_type: str = ""
    current_entity_id: int = 0

    async def send_message(self):
        """Verstuur bericht en stream response."""
        if not self.input_value.strip():
            return

        # Voeg user message toe
        user_message = {"role": "user", "content": self.input_value}
        self.messages = self.messages + [user_message]
        self.input_value = ""
        self.is_streaming = True

        # Start streaming response
        assistant_message = {"role": "assistant", "content": "", "suggestions": []}
        self.messages = self.messages + [assistant_message]

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/chat/stream",
                json={
                    "message": user_message["content"],
                    "context": {
                        "entity_type": self.current_entity_type,
                        "entity_id": self.current_entity_id,
                    }
                },
            ) as response:
                async for chunk in response.aiter_text():
                    if chunk.startswith("data: "):
                        data = chunk[6:].strip()
                        if data == "[DONE]":
                            break

                        import json
                        parsed = json.loads(data)

                        if "content" in parsed:
                            # Update laatste bericht met nieuwe content
                            self.messages[-1]["content"] += parsed["content"]
                            yield  # Trigger UI update

                        if "suggestions" in parsed:
                            self.messages[-1]["suggestions"] = parsed["suggestions"]
                            yield

        self.is_streaming = False

    def handle_key_down(self, key: str):
        """Handle Enter key."""
        if key == "Enter":
            return ChatState.send_message

    def set_context(self, entity_type: str, entity_id: int, context_name: str):
        """Update context wanneer gebruiker navigeert."""
        self.current_entity_type = entity_type
        self.current_entity_id = entity_id
        self.current_context = context_name
```

#### Suggestion Cards

```python
# ims/components/chat_island.py (vervolg)

def suggestion_card(suggestion: dict) -> rx.Component:
    """Render een AI suggestie kaart."""
    return rx.box(
        rx.hstack(
            rx.icon("lightbulb", color="yellow.500"),
            rx.vstack(
                rx.text(suggestion["title"], font_weight="bold"),
                rx.text(suggestion["reasoning"], font_size="sm", color="gray.600"),
                rx.hstack(
                    rx.badge(
                        f"{int(suggestion['confidence'] * 100)}% confidence",
                        color_scheme="green" if suggestion["confidence"] > 0.8 else "yellow",
                    ),
                ),
                align_items="start",
            ),
            align_items="start",
        ),
        rx.hstack(
            rx.button(
                "Accepteren",
                color_scheme="green",
                size="sm",
                on_click=lambda: ChatState.accept_suggestion(suggestion["id"]),
            ),
            rx.button(
                "Aanpassen",
                variant="outline",
                size="sm",
                on_click=lambda: ChatState.modify_suggestion(suggestion["id"]),
            ),
            rx.button(
                "Afwijzen",
                variant="ghost",
                size="sm",
                on_click=lambda: ChatState.reject_suggestion(suggestion["id"]),
            ),
            spacing="2",
            margin_top="2",
        ),
        padding="3",
        border="1px solid #e2e8f0",
        border_radius="md",
        background="white",
        margin_top="2",
    )

def suggestion_cards(suggestions: list) -> rx.Component:
    """Render meerdere suggestie kaarten."""
    return rx.vstack(
        rx.foreach(suggestions, suggestion_card),
        spacing="2",
        width="100%",
    )
```

#### Risk Heatmap (In Control Model)

```python
# ims/components/heatmap.py
import reflex as rx
from ims.state.risk import RiskState

def quadrant_cell(
    quadrant: str,
    label: str,
    risks: list,
    color: str,
    position: str,
) -> rx.Component:
    """Een kwadrant in de heatmap."""
    return rx.box(
        rx.vstack(
            rx.text(label, font_weight="bold", color="gray.700"),
            rx.text(f"{len(risks)} risico's", font_size="sm", color="gray.500"),
            rx.vstack(
                rx.foreach(
                    risks[:5],  # Toon max 5
                    lambda r: rx.tooltip(
                        rx.box(
                            rx.text(r["title"][:30], font_size="xs"),
                            padding="1",
                            background="white",
                            border_radius="sm",
                            cursor="pointer",
                            on_click=lambda: rx.redirect(f"/risks/{r['id']}"),
                        ),
                        label=r["title"],
                    ),
                ),
                spacing="1",
            ),
            rx.cond(
                len(risks) > 5,
                rx.text(f"+{len(risks) - 5} meer...", font_size="xs", color="gray.400"),
            ),
            align_items="start",
            spacing="2",
        ),
        background=color,
        padding="4",
        border_radius="md",
        min_height="200px",
        width="100%",
    )

def risk_heatmap() -> rx.Component:
    """'In Control' model heatmap for risk management."""
    return rx.box(
        # Y-as label
        rx.box(
            rx.text("Kwetsbaarheid →",
                    transform="rotate(-90deg)",
                    font_weight="bold",
                    color="gray.600"),
            position="absolute",
            left="-60px",
            top="50%",
        ),

        # Grid
        rx.grid(
            # Top row: MONITOR | MITIGATE
            quadrant_cell(
                "MONITOR", "Monitoren",
                RiskState.monitor_risks,
                "orange.50",
                "top-left",
            ),
            quadrant_cell(
                "MITIGATE", "Mitigeren",
                RiskState.mitigate_risks,
                "red.50",
                "top-right",
            ),

            # Bottom row: ACCEPT | ASSURANCE
            quadrant_cell(
                "ACCEPT", "Accepteren",
                RiskState.accept_risks,
                "green.50",
                "bottom-left",
            ),
            quadrant_cell(
                "ASSURANCE", "Zekerheid verkrijgen",
                RiskState.assurance_risks,
                "blue.50",
                "bottom-right",
            ),

            columns="2",
            spacing="4",
            width="100%",
        ),

        # X-as label
        rx.box(
            rx.text("Impact →", font_weight="bold", color="gray.600"),
            text_align="center",
            margin_top="4",
        ),

        position="relative",
        padding="8",
        padding_left="80px",
    )
```

#### Layout Component

```python
# ims/components/layout.py
import reflex as rx
from ims.components.chat_island import chat_island

def sidebar() -> rx.Component:
    """Navigatie sidebar."""
    return rx.box(
        rx.vstack(
            rx.image(src="/logo.png", height="40px"),
            rx.divider(),

            sidebar_link("Dashboard", "/", "layout-dashboard"),
            sidebar_link("Risico's", "/risks", "alert-triangle"),
            sidebar_link("Maatregelen", "/measures", "shield-check"),
            sidebar_link("Assessments", "/assessments", "clipboard-check"),
            sidebar_link("Incidenten", "/incidents", "alert-circle"),
            sidebar_link("Beleid", "/policies", "file-text"),

            rx.spacer(),
            rx.divider(),

            sidebar_link("Instellingen", "/settings", "settings"),

            height="100vh",
            padding="4",
            spacing="2",
        ),
        width="250px",
        background="gray.50",
        border_right="1px solid #eee",
    )

def sidebar_link(label: str, href: str, icon: str) -> rx.Component:
    """Sidebar navigatie link."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(label),
            width="100%",
            padding="2",
            border_radius="md",
            _hover={"background": "gray.100"},
        ),
        href=href,
        width="100%",
    )

def layout(content: rx.Component) -> rx.Component:
    """Hoofd layout met sidebar en chat island."""
    return rx.hstack(
        sidebar(),
        rx.box(
            content,
            flex="1",
            padding="6",
            overflow_y="auto",
            height="100vh",
        ),
        chat_island(),  # Altijd zichtbaar
        width="100%",
    )
```

### 1.6 Reflex Configuratie

```python
# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="ims",
    title="IMS - Integrated Management System",
    description="Governance, Risk & Compliance Platform",

    # Backend API (aparte FastAPI service)
    api_url="http://localhost:8000",

    # Database (shared met backend)
    db_url="postgresql://postgres:password@localhost:5432/ims",

    # Styling
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "brand": {
                        "50": "#eff6ff",
                        "500": "#3b82f6",
                        "900": "#1e3a8a",
                    }
                }
            }
        }
    },
)
```

### 1.7 Main App Entry

```python
# ims/ims.py
import reflex as rx

# Import pages
from ims.pages.login import login_page
from ims.pages.index import dashboard_page
from ims.pages.risks import risks_page
from ims.pages.measures import measures_page
from ims.pages.assessments import assessments_page
from ims.pages.incidents import incidents_page
from ims.pages.policies import policies_page
from ims.pages.scopes import scopes_page
from ims.pages.compliance import compliance_page
from ims.pages.assets import assets_page
from ims.pages.suppliers import suppliers_page
from ims.pages.backlog import backlog_page

# Create app
app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="medium",
        scaling="95%",
    ),
)

# Add pages (auth guard is in layout component)
app.add_page(login_page, route="/login", title="Login - IMS")
app.add_page(dashboard_page, route="/", title="Dashboard - IMS")
app.add_page(risks_page, route="/risks", title="Risico's - IMS")
app.add_page(measures_page, route="/measures", title="Maatregelen - IMS")
app.add_page(assessments_page, route="/assessments", title="Assessments - IMS")
app.add_page(incidents_page, route="/incidents", title="Incidenten - IMS")
app.add_page(policies_page, route="/policies", title="Beleid - IMS")
app.add_page(scopes_page, route="/scopes", title="Scopes - IMS")
app.add_page(compliance_page, route="/compliance", title="Compliance - IMS")
app.add_page(assets_page, route="/assets", title="Assets - IMS")
app.add_page(suppliers_page, route="/suppliers", title="Leveranciers - IMS")
app.add_page(backlog_page, route="/backlog", title="Backlog - IMS")
```

---

## 2. AI Governance Model

### 2.1 Principe

> **"AI adviseert, mens beslist."**

Geen enkele AI-gegenereerde waarde mag in productie-status komen zonder expliciete menselijke goedkeuring. Dit is zowel een governance-eis als een wettelijke noodzaak (AVG Art. 22 - recht om niet onderworpen te worden aan geautomatiseerde besluitvorming).

### 2.2 Suggestion Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI SUGGESTION LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ CREATED  │───►│ PENDING  │───►│ REVIEWED │───►│ APPLIED  │          │
│  └──────────┘    └──────────┘    └────┬─────┘    └──────────┘          │
│       │                               │                                  │
│       │                               ▼                                  │
│       │                         ┌──────────┐                            │
│       │                         │ REJECTED │                            │
│       │                         └──────────┘                            │
│       │                               │                                  │
│       ▼                               ▼                                  │
│  ┌──────────┐                  ┌──────────┐                             │
│  │ EXPIRED  │                  │ MODIFIED │───► (nieuwe suggestion)     │
│  └──────────┘                  └──────────┘                             │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Status definities:                                                      │
│  • CREATED   - AI heeft suggestie gegenereerd                           │
│  • PENDING   - Wacht op menselijke review                               │
│  • REVIEWED  - Mens heeft bekeken, nog niet besloten                    │
│  • APPLIED   - Mens heeft geaccepteerd, waarde is overgenomen           │
│  • REJECTED  - Mens heeft afgewezen met reden                           │
│  • MODIFIED  - Mens heeft aangepast (creëert nieuwe suggestion)         │
│  • EXPIRED   - Niet binnen 7 dagen behandeld                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Datamodel Uitbreidingen

#### AISuggestion Entity (uitgebreid)

```python
class SuggestionStatus(str, Enum):
    CREATED = "Created"
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    APPLIED = "Applied"
    REJECTED = "Rejected"
    MODIFIED = "Modified"
    EXPIRED = "Expired"


class AISuggestion(SQLModel, table=True):
    """
    AI-gegenereerde suggestie die menselijke goedkeuring vereist.

    GOVERNANCE REGEL: Geen AISuggestion mag APPLIED worden zonder
    dat reviewed_by_id en reviewed_at zijn ingevuld.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Conversatie context
    conversation_id: Optional[int] = Field(foreign_key="aiconversation.id")
    agent_id: Optional[int] = Field(foreign_key="aiagent.id")

    # Wat wordt gesuggereerd
    suggestion_type: str  # "field_update", "create_entity", "classification", "workflow_transition"
    target_entity_type: str  # "Risk", "Measure", etc.
    target_entity_id: Optional[int]  # Bestaande entity, NULL bij create

    # De suggestie zelf
    field_name: Optional[str]  # Welk veld (bijv. "attention_quadrant")
    suggested_value: str  # JSON-encoded waarde
    previous_value: Optional[str]  # JSON-encoded vorige waarde (voor audit)

    # AI reasoning
    reasoning: str  # Uitleg waarom AI dit suggereert
    confidence: float = Field(ge=0, le=1)  # 0.0 - 1.0

    # Knowledge sources gebruikt
    knowledge_sources_used: Optional[str]  # JSON array van AIKnowledgeBase IDs

    # =========================================================================
    # GOVERNANCE VELDEN
    # =========================================================================

    status: SuggestionStatus = SuggestionStatus.PENDING

    # Review tracking
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id")
    reviewed_at: Optional[datetime]
    review_duration_seconds: Optional[int]  # Hoe lang keek reviewer ernaar

    # Decision tracking
    decision: Optional[str]  # "accepted", "rejected", "modified"
    decision_by_id: Optional[int] = Field(foreign_key="user.id")
    decision_at: Optional[datetime]
    decision_justification: Optional[str]  # Verplicht bij reject/modify

    # Als gemodificeerd: wat was de aangepaste waarde?
    modified_value: Optional[str]  # JSON-encoded
    modification_reason: Optional[str]

    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # default: created_at + 7 dagen

    # Relationships
    conversation: Optional["AIConversation"] = Relationship()
    agent: Optional["AIAgent"] = Relationship()
```

#### Uitbreiding op Target Entities

Voeg aan Risk, Measure, en andere AI-beïnvloede entities toe:

```python
class Risk(SQLModel, table=True):
    # ... bestaande velden ...

    # =========================================================================
    # AI GOVERNANCE TRACKING
    # =========================================================================

    # Laatste AI suggestie die tot deze waarde leidde
    last_ai_suggestion_id: Optional[int] = Field(foreign_key="aisuggestion.id")

    # Is de huidige waarde gebaseerd op AI suggestie?
    value_source: str = "manual"  # "manual", "ai_accepted", "ai_modified"

    # Als AI suggestie niet gevolgd: waarom?
    ai_override_reason: Optional[str]

    # Tracking per veld (voor audit)
    # JSON: {"attention_quadrant": {"source": "ai_accepted", "suggestion_id": 123}, ...}
    field_sources: Optional[str]
```

### 2.4 Governance Regels

#### Regel 1: Verplichte Review voor High-Impact Velden

```python
HIGH_IMPACT_FIELDS = {
    "Risk": ["attention_quadrant", "risk_accepted", "inherent_impact", "residual_likelihood"],
    "Measure": ["status", "effectiveness_percentage"],
    "Incident": ["is_data_breach", "severity"],
    "Exception": ["status", "expiration_date"],
}

# Bij APPLIED status voor deze velden:
# - decision_justification is VERPLICHT (niet NULL, niet leeg)
# - review_duration_seconds moet > 10 seconden (anti-rubber-stamping)
```

#### Regel 2: Vier-Ogen Principe voor Kritieke Beslissingen

```python
FOUR_EYES_REQUIRED = {
    "Risk": {
        "fields": ["risk_accepted"],
        "condition": "residual_risk_score >= 12"  # Hoog risico
    },
    "Exception": {
        "fields": ["status"],
        "condition": "status == 'Active' AND accepted_risk_level in ['HIGH', 'CRITICAL']"
    },
}

# Bij deze condities:
# - decision_by_id mag NIET gelijk zijn aan target_entity.owner_id
# - OF: aparte approval workflow vereist
```

#### Regel 3: Confidence Threshold

```python
CONFIDENCE_THRESHOLDS = {
    "auto_suggest": 0.7,      # Onder 0.7: AI toont suggestie niet proactief
    "highlight_uncertainty": 0.85,  # Onder 0.85: UI toont waarschuwing
    "require_justification": 0.6,   # Onder 0.6: gebruiker MOET reden geven bij accept
}
```

### 2.5 Audit Trail Requirements

Elke AISuggestion transactie moet loggen:

```python
class AISuggestionAuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    suggestion_id: int = Field(foreign_key="aisuggestion.id")

    action: str  # "created", "viewed", "accepted", "rejected", "modified", "expired"
    actor_id: Optional[int] = Field(foreign_key="user.id")  # NULL bij system actions
    actor_type: str  # "user", "system", "ai"

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Context
    ip_address: Optional[str]
    user_agent: Optional[str]

    # Details
    details: Optional[str]  # JSON met actie-specifieke data
```

### 2.6 Rapportage KPIs

Dashboard metrics voor AI governance:

| KPI | Beschrijving | Target |
|-----|--------------|--------|
| **Suggestion Acceptance Rate** | % suggesties geaccepteerd | 60-80% |
| **Modification Rate** | % suggesties aangepast | 10-25% |
| **Rejection Rate** | % suggesties afgewezen | 10-20% |
| **Avg Review Time** | Gemiddelde review tijd | > 15 sec |
| **Rubber Stamp Rate** | % accepted in < 5 sec | < 5% |
| **Override Rate** | % waar mens AI niet volgde bij high-impact | Tracking |
| **Confidence Calibration** | Correlatie confidence vs acceptance | > 0.7 |

---

## 3. AI Performance Optimalisatie

### 3.1 Performance Targets

| Metric | Target | Maximum |
|--------|--------|---------|
| **Time to First Token** | < 500ms | 1000ms |
| **Full Response (simple)** | < 2 sec | 4 sec |
| **Full Response (complex)** | < 4 sec | 8 sec |
| **Tool Execution** | < 500ms per tool | 1000ms |
| **RAG Retrieval** | < 200ms | 500ms |

### 3.2 Hardware Configuratie

#### Minimum (Development)
```
CPU: 8 cores
RAM: 16 GB
GPU: Geen (CPU inference)
Storage: SSD 256GB

Expected performance:
- Mistral 7B: ~5 tokens/sec
- Simple response: 6-10 sec
```

#### Aanbevolen (Productie)
```
CPU: 16 cores
RAM: 32 GB
GPU: NVIDIA RTX 3060 12GB of beter
Storage: NVMe SSD 512GB

Expected performance:
- Mistral 7B: ~25 tokens/sec
- Simple response: 2-3 sec
```

#### Enterprise (High Volume)
```
CPU: 32 cores
RAM: 64 GB
GPU: NVIDIA RTX 4090 24GB of A100
Storage: NVMe SSD 1TB

Expected performance:
- Mistral 7B: ~50 tokens/sec
- Simple response: 1-2 sec
- Parallel requests: 4-8 concurrent
```

### 3.3 Ollama Configuratie

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_GPU_OVERHEAD=0"
Environment="OLLAMA_MAX_QUEUE=512"
```

```bash
# Model configuratie voor snelheid
ollama pull mistral:7b-instruct-v0.2-q4_K_M  # Quantized voor snelheid

# Modelfile optimalisaties
FROM mistral:7b-instruct-v0.2-q4_K_M

PARAMETER num_ctx 4096        # Kleinere context = sneller
PARAMETER num_batch 512       # Batch size
PARAMETER num_gpu 99          # Alle layers op GPU
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
```

### 3.4 Context Window Optimalisatie

Het documenteerde context budget (8000 tokens) is te groot. Geoptimaliseerde verdeling:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  GEOPTIMALISEERD CONTEXT BUDGET: 4096 tokens                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────┐                                    │
│  │ System Prompt          400 tok  │  Fixed per agent                   │
│  ├─────────────────────────────────┤                                    │
│  │ Methodology Knowledge   600 tok │  Top 2-3 meest relevante items     │
│  ├─────────────────────────────────┤                                    │
│  │ Organization Context    200 tok │  Alleen key facts                  │
│  ├─────────────────────────────────┤                                    │
│  │ Current Entity          300 tok │  Huidige risk/measure data         │
│  ├─────────────────────────────────┤                                    │
│  │ Conversation History   1000 tok │  Laatste 4-6 berichten             │
│  ├─────────────────────────────────┤                                    │
│  │ User Input              300 tok │  Huidige vraag                     │
│  ├─────────────────────────────────┤                                    │
│  │ Response Buffer        1296 tok │  Ruimte voor antwoord              │
│  └─────────────────────────────────┘                                    │
│                                                                          │
│  TOTAAL: 4096 tokens                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.5 Streaming Implementatie

Backend en Reflex frontend voor streaming responses:

```python
# Backend: FastAPI streaming endpoint
# backend/app/api/v1/endpoints/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: dict = {}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream AI response via Server-Sent Events."""

    async def generate():
        async for chunk in llm_service.stream_generate(
            prompt=request.message,
            context=request.context,
            tools=get_agent_tools(request.context.get("entity_type"))
        ):
            if chunk.get("type") == "content":
                yield f"data: {json.dumps({'content': chunk['text']})}\n\n"
            elif chunk.get("type") == "suggestion":
                yield f"data: {json.dumps({'suggestions': chunk['suggestions']})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

```python
# Frontend: Reflex state met streaming
# ims/state/chat.py
import reflex as rx
import httpx
import json
from typing import List, Dict, Any

class ChatState(rx.State):
    """State voor AI Chat Island met streaming support."""

    messages: List[Dict[str, Any]] = []
    input_value: str = ""
    is_streaming: bool = False
    error_message: str = ""

    current_agent_name: str = "Risk Expert"
    current_context: str = "Dashboard"
    current_entity_type: str = ""
    current_entity_id: int = 0

    async def send_message(self):
        """Verstuur bericht en stream response."""
        if not self.input_value.strip() or self.is_streaming:
            return

        user_message = {"role": "user", "content": self.input_value}
        self.messages = self.messages + [user_message]
        prompt = self.input_value
        self.input_value = ""
        self.is_streaming = True
        self.error_message = ""

        # Lege assistant message voor streaming
        self.messages = self.messages + [{"role": "assistant", "content": "", "suggestions": []}]
        yield  # Update UI

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    "http://localhost:8000/api/v1/chat/stream",
                    json={
                        "message": prompt,
                        "context": {
                            "entity_type": self.current_entity_type,
                            "entity_id": self.current_entity_id,
                        }
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:].strip()
                            if data == "[DONE]":
                                break

                            parsed = json.loads(data)

                            # Update content incrementeel
                            if "content" in parsed:
                                current_content = self.messages[-1]["content"]
                                self.messages[-1]["content"] = current_content + parsed["content"]
                                yield  # Trigger UI update voor elke chunk

                            # Voeg suggestions toe
                            if "suggestions" in parsed:
                                self.messages[-1]["suggestions"] = parsed["suggestions"]
                                yield

        except httpx.TimeoutException:
            self.error_message = "AI response timeout - probeer opnieuw"
            self.messages[-1]["content"] = "[Response timeout]"
        except Exception as e:
            self.error_message = f"Fout: {str(e)}"
            self.messages[-1]["content"] = f"[Fout: {str(e)}]"
        finally:
            self.is_streaming = False
            yield

    async def accept_suggestion(self, suggestion_id: int):
        """Accepteer een AI suggestie."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/api/v1/suggestions/{suggestion_id}/accept",
                json={"justification": "Geaccepteerd via chat"}
            )
            if response.status_code == 200:
                # Refresh huidige entity data
                yield ChatState.refresh_context

    async def reject_suggestion(self, suggestion_id: int):
        """Wijs een AI suggestie af."""
        # Open modal voor rejection reason
        self.rejection_modal_open = True
        self.rejecting_suggestion_id = suggestion_id
```

### 3.6 Caching Strategie

#### Knowledge Base Caching

```python
from functools import lru_cache
from redis import Redis

redis = Redis(host='localhost', port=6379, db=0)

# In-memory cache voor hot knowledge items
@lru_cache(maxsize=100)
def get_methodology_knowledge(key: str) -> str:
    """Cache methodology items die vaak gebruikt worden."""
    return db.query(AIKnowledgeBase).filter_by(key=key).first().content

# Redis cache voor tenant-specifieke context
def get_org_context_cached(tenant_id: int) -> dict:
    cache_key = f"org_context:{tenant_id}"

    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    context = fetch_org_context_from_db(tenant_id)
    redis.setex(cache_key, 3600, json.dumps(context))  # 1 uur TTL

    return context
```

#### Embedding Cache

```python
# Pre-compute embeddings voor alle knowledge base items
class EmbeddingCache:
    def __init__(self):
        self.embeddings = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def warm_cache(self):
        """Run bij startup: laad alle embeddings in memory."""
        items = db.query(AIKnowledgeBase).filter_by(is_embedded=True).all()
        for item in items:
            self.embeddings[item.id] = np.frombuffer(item.embedding, dtype=np.float32)

    def search(self, query: str, top_k: int = 5) -> List[int]:
        """Zoek in memory cache, niet in database."""
        query_embedding = self.model.encode(query)

        scores = {}
        for item_id, embedding in self.embeddings.items():
            scores[item_id] = np.dot(query_embedding, embedding)

        return sorted(scores, key=scores.get, reverse=True)[:top_k]
```

### 3.7 Async Tool Execution

Parallelliseer onafhankelijke tool calls:

```python
import asyncio

async def execute_tools_parallel(tool_calls: List[ToolCall]) -> List[ToolResult]:
    """Execute onafhankelijke tools parallel."""

    # Groepeer tools op dependencies
    independent_tools = []
    dependent_tools = []

    for tool in tool_calls:
        if tool.depends_on:
            dependent_tools.append(tool)
        else:
            independent_tools.append(tool)

    # Execute independent tools parallel
    results = {}
    if independent_tools:
        tasks = [execute_tool(tool) for tool in independent_tools]
        independent_results = await asyncio.gather(*tasks)
        for tool, result in zip(independent_tools, independent_results):
            results[tool.id] = result

    # Execute dependent tools sequentially
    for tool in dependent_tools:
        # Wacht op dependencies
        dep_results = {dep: results[dep] for dep in tool.depends_on}
        result = await execute_tool(tool, context=dep_results)
        results[tool.id] = result

    return list(results.values())
```

### 3.8 Tiered Model Approach

Gebruik verschillende models voor verschillende taken:

```python
class ModelRouter:
    """Route requests naar optimaal model op basis van task type."""

    MODELS = {
        "fast": "phi3:mini",           # 3B params, ~50 tok/sec
        "balanced": "mistral:7b",       # 7B params, ~25 tok/sec
        "quality": "mixtral:8x7b",      # 47B params, ~10 tok/sec
    }

    TASK_ROUTING = {
        # Snelle taken -> klein model
        "classification": "fast",
        "yes_no_question": "fast",
        "entity_extraction": "fast",
        "summarization_short": "fast",

        # Balanced taken -> medium model
        "risk_assessment": "balanced",
        "measure_suggestion": "balanced",
        "compliance_check": "balanced",
        "conversation": "balanced",

        # Complexe taken -> groot model
        "policy_drafting": "quality",
        "gap_analysis": "quality",
        "incident_analysis": "quality",
        "report_generation": "quality",
    }

    def select_model(self, task_type: str, urgency: str = "normal") -> str:
        if urgency == "high":
            # Bij urgentie altijd snelste model
            return self.MODELS["fast"]

        tier = self.TASK_ROUTING.get(task_type, "balanced")
        return self.MODELS[tier]
```

### 3.9 Performance Monitoring

```python
from prometheus_client import Histogram, Counter

# Metrics
llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'Time spent on LLM requests',
    ['model', 'task_type'],
    buckets=[0.5, 1, 2, 4, 8, 16, 32]
)

llm_tokens_generated = Counter(
    'llm_tokens_generated_total',
    'Total tokens generated',
    ['model']
)

tool_execution_duration = Histogram(
    'tool_execution_duration_seconds',
    'Time spent executing tools',
    ['tool_name'],
    buckets=[0.1, 0.25, 0.5, 1, 2, 5]
)

# Usage
@llm_request_duration.labels(model='mistral:7b', task_type='conversation').time()
async def generate_response(prompt: str):
    ...
```

### 3.10 Graceful Degradation

Als AI traag of onbeschikbaar is:

```python
class AIService:
    async def get_suggestion(self, context: dict, timeout: float = 5.0) -> Optional[Suggestion]:
        try:
            async with asyncio.timeout(timeout):
                return await self._generate_suggestion(context)
        except asyncio.TimeoutError:
            # Log maar blokkeer gebruiker niet
            logger.warning("AI suggestion timed out, continuing without AI")
            return None
        except ConnectionError:
            # Ollama niet bereikbaar
            logger.error("Ollama not available")
            return None

    def is_available(self) -> bool:
        """Health check voor UI om AI features te tonen/verbergen."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False
```

Frontend UI past zich aan:

```python
# ims/state/ai_health.py
import reflex as rx
import httpx

class AIHealthState(rx.State):
    """State voor AI beschikbaarheid check."""

    is_available: bool = True
    is_loading: bool = True

    async def check_health(self):
        """Check of Ollama bereikbaar is."""
        self.is_loading = True
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                self.is_available = response.status_code == 200
        except Exception:
            self.is_available = False
        finally:
            self.is_loading = False

# ims/components/ai_guard.py
import reflex as rx
from ims.state.ai_health import AIHealthState

def ai_feature_guard(content: rx.Component) -> rx.Component:
    """Verberg AI features als Ollama niet beschikbaar is."""
    return rx.cond(
        AIHealthState.is_loading,
        rx.skeleton(height="100px"),
        rx.cond(
            AIHealthState.is_available,
            content,
            rx.fragment(),  # Lege fragment, verbergt silently
        ),
    )

# Gebruik in layout
def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(content, flex="1", padding="6"),
        ai_feature_guard(chat_island()),  # Alleen tonen als AI beschikbaar
        on_mount=AIHealthState.check_health,
    )
```

---

## Appendix A: Checklist voor Go-Live

### Frontend (Reflex)
- [ ] Reflex project opgezet (`reflex init`)
- [ ] rxconfig.py geconfigureerd (app_name, api_url, db_url)
- [ ] State modules aangemaakt (auth, risk, measure, chat)
- [ ] Pages aangemaakt (dashboard, risks, measures, assessments)
- [ ] Layout component met sidebar werkend
- [ ] httpx API client voor backend communicatie
- [ ] Auth state met login/logout flow
- [ ] AI Chat Island component gebouwd met streaming
- [ ] Suggestion cards met accept/reject/modify
- [ ] Risk heatmap (In Control model) werkend
- [ ] AI health check voor graceful degradation

### AI Governance
- [ ] AISuggestion entity geïmplementeerd
- [ ] Audit logging actief
- [ ] Confidence thresholds geconfigureerd
- [ ] Four-eyes check geïmplementeerd voor kritieke beslissingen
- [ ] Governance dashboard met KPIs

### Performance
- [ ] Ollama draait met GPU acceleration
- [ ] Streaming responses werkend
- [ ] Knowledge base cache warm
- [ ] Response time < 4 sec (P95)
- [ ] Graceful degradation getest

---

*Einde document*
