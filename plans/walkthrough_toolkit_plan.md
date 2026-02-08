# Walkthrough Toolkit MVP — Implementatieplan

## Context

Het IMS is een GRC-platform dat momenteel functioneert als passief archief. Gebruikers openen schermen (Risico's, Controls, Scopes), maar krijgen geen begeleiding over wat ze moeten doen of in welke volgorde. De MS Hub toont al PDCA-fasekaarten met metrics, maar geeft geen actionable guidance.

Dit plan transformeert de app van archief naar coach: de gebruiker wordt stap voor stap door het PDCA-inrichtingsproces geleid.

---

## Fase 1 (MVP): "MS Hub wordt de Coach"

### Wat wordt gebouwd

| Component | Beschrijving |
|-----------|--------------|
| **Journey Stepper** | 7-stappen voortgangsindicator op MS Hub met status/blockers/actieknoppen |
| **PDCA Ring Widget** | Compacte voortgangsbalk op Dashboard ("Stap 3 van 7") |
| **Next Best Step Hints** | Contextuele callouts op 4 domeinpagina's |

### De 7 journey-stappen

| Stap | Titel | Klaar-conditie | Blocker-tekst |
|------|-------|-----------------|---------------|
| 1 | Scopes definiëren | `len(scopes) > 0` | "Geen scopes gedefinieerd" |
| 2 | BIA uitvoeren | Minstens 1 scope met BIA-rating | "X scopes missen BIA-classificatie" |
| 3 | Risico's identificeren | `len(risks) >= 3` | "Slechts X risico's geregistreerd" |
| 4 | Behandeling bepalen | Alle risico's hebben treatment_strategy | "X risico's zonder behandelstrategie" |
| 5 | Controls implementeren | Minstens 1 control gekoppeld aan risico | "Controls niet gekoppeld aan risico's" |
| 6 | Besluiten vastleggen | `len(decisions) > 0` | "Geen formele besluiten vastgelegd" |
| 7 | Review uitvoeren | Minstens 1 afgerond assessment | "Nog geen assessments afgerond" |

---

## Implementatiestappen

### Stap 1: JourneyState aanmaken

**Nieuw bestand:** `frontend/ims/state/journey.py` (~120 regels)

`JourneyState(rx.State)` met:
- Backend-only data vars (`_` prefix): `_scopes`, `_risks`, `_controls`, `_decisions`, `_assessments`
- 7x `stepN_ok: bool` — computed vars op basis van klaar-condities
- 7x `stepN_blocker: str` — computed vars met blocker-tekst
- `overall_progress_pct: int` (0-100)
- `current_step: int` (eerste onvoltooide stap, 1-indexed)
- `current_step_label: str` (titel van huidige stap)
- Per-pagina hint vars: `risks_hint`, `controls_hint`, `scopes_hint`, `policies_hint`
- `load_journey_data()` — 5 parallelle GET-requests met `asyncio.gather`

Data-loading gebruikt bestaande endpoints (geen backend changes):
```
GET /scopes/        → _scopes
GET /risks/         → _risks
GET /controls/      → _controls
GET /decisions/     → _decisions
GET /assessments/   → _assessments
```

**Let op:**
- Gebruik `httpx.Timeout(connect=2.0)` i.p.v. `asyncio.wait_for` (Windows-compatibiliteit)
- `_` prefix op raw data vars is bewust: alleen computed vars zijn zichtbaar in de UI
- `return_exceptions=True` in `asyncio.gather` voor resilience

### Stap 2: Guidance componenten bouwen

**Nieuw bestand:** `frontend/ims/components/guidance.py` (~150 regels)

Vier herbruikbare componenten:

1. **`journey_step_card(step_num, title, icon, is_ok, blocker_text, link_href, link_label)`**
   - Genummerde cirkel (groen+vinkje = klaar, grijs = te doen)
   - Titel + badge ("Klaar" / "Te doen")
   - Oranje callout met blocker-tekst (alleen als niet klaar)
   - Actieknop met link naar relevante pagina

2. **`journey_stepper()`**
   - Alle 7 step_cards in een vstack
   - Handmatig opgebouwd (elke stap heeft unieke computed var-referentie)

3. **`pdca_ring_widget()`**
   - Voortgangsbalk (0-100%) met animatie
   - "Stap X van 7: [titel]" of "Alle stappen afgerond!"
   - Link naar MS Hub

4. **`next_step_hint(page: str)`**
   - `rx.match` op pagina-key → juiste hint var
   - `rx.callout` met lightbulb-icoon, alleen zichtbaar als hint niet leeg
   - Auto-hide zodra conditie opgelost

**Let op:**
- Geen `rx.tooltip` rond `rx.icon_button` (breekt on_click)
- Gebruik `rx.cond` met 2 args (geen else-branch) voor conditionele rendering
- Progress bar width via `JourneyState.overall_progress_pct.to(str) + "%"`

### Stap 3: BaseState uitbreiden

**Wijzig:** `frontend/ims/state/base.py`

Toevoegen:
```python
journey_expanded: bool = True

def toggle_journey_expanded(self):
    self.journey_expanded = not self.journey_expanded
```

**Wijzig:** `frontend/ims/state/__init__.py`

Toevoegen:
```python
from ims.state.journey import JourneyState
```

### Stap 4: MS Hub integreren

**Wijzig:** `frontend/ims/pages/ms_hub.py`

- Import: `BaseState`, `JourneyState`, `journey_stepper`
- Nieuwe functie `journey_section()`: card met inklapbare stepper
  - Header met kompas-icoon, "Inrichtingspad", percentage, chevron-toggle
  - Progress bar (altijd zichtbaar)
  - `rx.cond(BaseState.journey_expanded, journey_stepper())` voor inklapbaar deel
- Invoegen: `journey_section()` als eerste element in `ms_hub_content()`
- `on_mount` uitbreiden: `[MsHubState.load_all, JourneyState.load_journey_data]`
- Vernieuwen-knop uitbreiden: `on_click=[MsHubState.load_all, JourneyState.load_journey_data]`

### Stap 5: Dashboard integreren

**Wijzig:** `frontend/ims/pages/index.py`

- Import: `JourneyState`, `pdca_ring_widget`
- `pdca_ring_widget()` invoegen na welkomstbericht, voor ACT-warning
- `on_mount` uitbreiden met `JourneyState.load_journey_data`

### Stap 6: Domeinpagina's hints toevoegen

**Wijzig per pagina:**

| Bestand | Import toevoegen | Hint invoegen | on_mount uitbreiden |
|---------|-----------------|---------------|---------------------|
| `pages/risks.py` | `JourneyState`, `next_step_hint` | `next_step_hint("risks")` voor filter_bar | `[RiskState.load_risks, JourneyState.load_journey_data]` |
| `pages/controls.py` | `JourneyState`, `next_step_hint` | `next_step_hint("controls")` voor stat_cards | `[ControlState.load_controls, JourneyState.load_journey_data]` |
| `pages/scopes.py` | `JourneyState`, `next_step_hint` | `next_step_hint("scopes")` voor stat_cards | `[ScopeState.load_scopes, JourneyState.load_journey_data]` |
| `pages/policies.py` | `JourneyState`, `next_step_hint` | `next_step_hint("policies")` voor stat_cards | `[PolicyState.load_policies, JourneyState.load_journey_data]` |

---

## Geen backend-wijzigingen nodig

Alle data wordt client-side berekend uit bestaande endpoints. De 5 parallelle requests laden in <1s dankzij `asyncio.gather` met korte timeout.

---

## Bestandsoverzicht

### Nieuwe bestanden (2)

| Bestand | Regels | Inhoud |
|---------|--------|--------|
| `frontend/ims/state/journey.py` | ~120 | JourneyState: data + computed vars |
| `frontend/ims/components/guidance.py` | ~150 | 4 UI-componenten |

### Gewijzigde bestanden (8)

| Bestand | Wijziging |
|---------|-----------|
| `frontend/ims/state/base.py` | +`journey_expanded` bool + toggle |
| `frontend/ims/state/__init__.py` | +JourneyState export |
| `frontend/ims/pages/ms_hub.py` | +journey_section() + dual on_mount/refresh |
| `frontend/ims/pages/index.py` | +pdca_ring_widget() + on_mount |
| `frontend/ims/pages/risks.py` | +next_step_hint("risks") + on_mount |
| `frontend/ims/pages/controls.py` | +next_step_hint("controls") + on_mount |
| `frontend/ims/pages/scopes.py` | +next_step_hint("scopes") + on_mount |
| `frontend/ims/pages/policies.py` | +next_step_hint("policies") + on_mount |

---

## UX na implementatie

### MS Hub
```
┌─────────────────────────────────────┐
│ 🗺️ Inrichtingspad           [71%] │
│ ████████████████░░░░░░░            │
│                                     │
│ ① Scopes definiëren          ✅    │
│ ② BIA uitvoeren              ✅    │
│ ③ Risico's identificeren     ✅    │
│ ④ Behandeling bepalen        ✅    │
│ ⑤ Controls implementeren     ✅    │
│ ⑥ Besluiten vastleggen       🟡    │
│   ⚠ Geen formele besluiten...      │
│   [Documenteer besluiten →]        │
│ ⑦ Review uitvoeren           ❌    │
│   ⚠ Nog geen assessments...        │
│   [Start assessment →]             │
│                                     │
│ ──── PDCA Fasekaarten ────         │
│ [Context] [Plan] [Do] [Check] [Act]│
└─────────────────────────────────────┘
```

### Dashboard
```
┌──────────────────────┐
│ 🎯 IMS Voortgang     │
│ ████████░░░░  71%    │
│ Stap 6 van 7         │
│ [Bekijk voortgang →] │
└──────────────────────┘
```

### Domeinpagina's (bijv. Risico's)
```
┌─────────────────────────────────────────┐
│ 💡 3 risico's zonder behandelstrategie  │
│    — kies Vermijden/Reduceren/          │
│    Overdragen/Accepteren                │
└─────────────────────────────────────────┘
```

---

## Verificatie

| # | Test | Verwacht resultaat |
|---|------|-------------------|
| 1 | Lege database | Alle 7 stappen ❌, 0% voortgang |
| 2 | Scope toevoegen | Stap 1 → ✅, progress stijgt naar 14% |
| 3 | Alle stappen doorlopen | 100%, "Alle stappen afgerond!" |
| 4 | Hints verschijnen | Risico-pagina toont hint als treatment ontbreekt |
| 5 | Hints verdwijnen | Na behandelstrategie kiezen → hint weg |
| 6 | Dashboard ring | Toont correcte % en huidige stap |
| 7 | Inklapbaar | Journey stepper op MS Hub in/uitklappen |
| 8 | Vernieuwen-knop | Refresht zowel PDCA-kaarten als journey stepper |
| 9 | Deploy | Push naar VPS, test op productie |

---

## Fase 2 (toekomst, NIET nu)

- Framework Toolkits: templates/suggesties bij create-dialogen
- "Why am I stuck?" uitleg bij disabled knoppen
- Rolafhankelijke guidance (CISO/Eigenaar/DT)
- Visuele PDCA-ring (circulair diagram)

---

## Status: ✅ Geimplementeerd

Implementatie afgerond op 2026-02-08. Alle bestanden aangemaakt/gewijzigd, gepusht naar origin + server, gedocumenteerd in `docs/WALKTHROUGH_TOOLKIT.md`.
