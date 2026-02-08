# Walkthrough Toolkit

Het Walkthrough Toolkit transformeert het IMS van een passief archief naar een actieve coach. Gebruikers worden stap voor stap door het PDCA-inrichtingsproces geleid.

## Overzicht

| Component | Locatie | Functie |
|-----------|---------|---------|
| **JourneyState** | `frontend/ims/state/journey.py` | Data laden + 7-staps voortgangsberekening |
| **Guidance Components** | `frontend/ims/components/guidance.py` | UI-componenten (stepper, ring, hints) |
| **BaseState** | `frontend/ims/state/base.py` | `journey_expanded` toggle |

## De 7 journey-stappen

| Stap | Titel | Klaar-conditie | Blocker-tekst |
|------|-------|----------------|---------------|
| 1 | Scopes definieren | Minstens 1 scope | "Geen scopes gedefinieerd" |
| 2 | BIA uitvoeren | Minstens 1 scope met BIA-rating | "X scopes missen BIA-classificatie" |
| 3 | Risico's identificeren | Minstens 3 risico's | "Slechts X risico's geregistreerd" |
| 4 | Behandeling bepalen | Alle risico's hebben treatment_strategy | "X risico's zonder behandelstrategie" |
| 5 | Controls implementeren | Minstens 1 control gekoppeld aan risico | "Controls niet gekoppeld aan risico's" |
| 6 | Besluiten vastleggen | Minstens 1 besluit | "Geen formele besluiten vastgelegd" |
| 7 | Review uitvoeren | Minstens 1 afgerond assessment | "Nog geen assessments afgerond" |

## Architectuur

### Dataflow

```
Bestaande API endpoints          JourneyState              UI Components
─────────────────────     ──────────────────────     ─────────────────────
GET /scopes/         ──>  _scopes (backend-only) ──> step1_ok / step1_blocker
GET /risks/          ──>  _risks                 ──> step3_ok / risks_hint
GET /controls/       ──>  _controls              ──> step5_ok / controls_hint
GET /decisions/      ──>  _decisions             ──> step6_ok
GET /assessments/    ──>  _assessments           ──> step7_ok
                          │
                          ├─ overall_progress_pct ──> pdca_ring_widget()
                          ├─ current_step         ──> journey_stepper()
                          └─ *_hint vars          ──> next_step_hint()
```

### Geen backend-wijzigingen

Alle data komt uit bestaande endpoints. De 5 parallelle requests worden afgevuurd in `load_journey_data()` met `asyncio.gather` en een korte connect-timeout (2s) om de UI niet te blokkeren.

### State vars met `_` prefix

De ruwe API-data (`_scopes`, `_risks`, etc.) heeft een `_` prefix, wat ze backend-only maakt in Reflex. Dit is bewust: de computed `@rx.var` properties (`step1_ok`, `risks_hint`, etc.) zijn de publieke interface naar de UI.

## UI-componenten

### 1. Journey Stepper (`journey_stepper()`)

Verticale lijst van 7 stapkaarten. Elke kaart toont:
- Genummerde cirkel (groen met vinkje = klaar, grijs = te doen)
- Titel + status-badge
- Oranje blocker-tekst met actieknop (alleen als niet klaar)

Wordt getoond op de **MS Hub** pagina, inklapbaar via `BaseState.journey_expanded`.

### 2. PDCA Ring Widget (`pdca_ring_widget()`)

Compacte voortgangskaart met:
- Voortgangsbalk (0-100%)
- "Stap X van 7: [huidige stap titel]"
- Link naar MS Hub

Wordt getoond op het **Dashboard** (index pagina).

### 3. Next Step Hint (`next_step_hint(page)`)

Contextuele `rx.callout` die verschijnt bovenaan domeinpagina's wanneer er actie nodig is:

| Pagina | Hint verschijnt wanneer |
|--------|------------------------|
| `"risks"` | Risico's zonder behandelstrategie, of minder dan 3 risico's |
| `"controls"` | Geen controls gekoppeld aan risico's |
| `"scopes"` | Geen scopes, of scopes zonder BIA-classificatie |
| `"policies"` | (Gereserveerd voor toekomstige hints) |

De hint verdwijnt automatisch zodra de conditie is opgelost.

## Gewijzigde pagina's

| Pagina | Wat is toegevoegd |
|--------|-------------------|
| `pages/ms_hub.py` | `journey_section()` boven PDCA-kaarten (inklapbaar) |
| `pages/index.py` | `pdca_ring_widget()` na welkomstbericht |
| `pages/risks.py` | `next_step_hint("risks")` boven filter bar |
| `pages/controls.py` | `next_step_hint("controls")` boven stat cards |
| `pages/scopes.py` | `next_step_hint("scopes")` boven stat cards |
| `pages/policies.py` | `next_step_hint("policies")` boven stat cards |

Alle pagina's laden journey-data via `on_mount`:
```python
on_mount=[PageState.load_data, JourneyState.load_journey_data]
```

## Uitbreiden

### Nieuwe stap toevoegen

1. Voeg titel/icon/link toe aan de constanten in `journey.py` (bovenaan)
2. Voeg `stepN_ok` en `stepN_blocker` computed vars toe aan `JourneyState`
3. Voeg een `journey_step_card()` aanroep toe in `journey_stepper()` in `guidance.py`
4. Update `steps_done` en `current_step` om de nieuwe stap mee te tellen

### Nieuwe hint toevoegen

1. Voeg een `@rx.var` computed var toe aan `JourneyState` (bijv. `new_page_hint`)
2. Voeg de pagina-key toe aan de `rx.match` in `next_step_hint()` in `guidance.py`
3. Voeg `next_step_hint("new_page")` toe aan de betreffende pagina

## Toekomstige uitbreidingen (Fase 2)

- Framework Toolkits: templates/suggesties bij create-dialogen
- "Why am I stuck?" uitleg bij disabled knoppen
- Rolafhankelijke guidance (CISO/Eigenaar/DT)
- Visuele PDCA-ring (circulair diagram)
