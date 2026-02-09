# Rolgebaseerde Navigatie & Paginatoegang

Dit document beschrijft welke pagina's en menusecties zichtbaar zijn per rol in het IMS-platform. Het rollenmodel is gebaseerd op het **Drielijnenmodel** (Three Lines of Defense).

---

## 1. Rollenmodel

| Rol | Lijn | Scope | Omschrijving |
|-----|------|-------|--------------|
| **Beheerder** | — | Cross-tenant | Platformbeheerder, volledige toegang |
| **Coordinator** | 2e lijn | Cross-tenant | GRC-coördinator, gebruikersbeheer, kaders stellen |
| **Eigenaar** | 1e lijn | Scope-gebonden | Proceseigenaar, risicoacceptatie, configuratie |
| **Medewerker** | 1e lijn | Scope-gebonden | Uitvoerder, controls invullen, bewijs leveren |
| **Toezichthouder** | 3e lijn | Cross-tenant | Auditor, alles lezen + findings schrijven |

---

## 2. Permissiematrix

Permissies worden berekend bij login (`backend/app/api/v1/endpoints/auth.py`) en opgeslagen in `localStorage`.

| Permissie | Beheerder | Coordinator | Eigenaar | Medewerker | Toezichthouder |
|-----------|:---------:|:-----------:|:--------:|:----------:|:--------------:|
| `is_admin` | x | | | | |
| `can_manage_users` | x | x | | | |
| `can_configure` | x | x | x | | |
| `can_edit` | x | x | x | x | |
| `can_write_findings` | x | x | | | x |
| `can_discover` | x | x | x | | x |

### Afgeleide permissies (frontend)

| Var | Logica | Doel |
|-----|--------|------|
| `can_discover` | `can_configure OR can_write_findings` | Toegang tot ONTDEKKEN-sectie en MS Hub |

**Bronbestanden:**
- Backend: `backend/app/api/v1/endpoints/auth.py` (regel 71-83)
- Frontend: `frontend/ims/state/auth.py`
- RBAC middleware: `backend/app/core/rbac.py`

---

## 3. Navigatiestructuur per rol

### Medewerker (minimaal: 7 pagina's)

```
Dashboard

── DOEN
   ├─ Risico's
   ├─ Controls
   ├─ Compliance
   ├─ Assessments
   ├─ Incidenten
   └─ In-Control
```

### Eigenaar (14 pagina's)

```
MS Hub
Dashboard

── DOEN
   ├─ Risico's
   ├─ Controls
   ├─ Compliance
   ├─ Assessments
   ├─ Incidenten
   ├─ Besluiten          ← can_configure
   └─ In-Control

── ONTDEKKEN             ← can_discover
   ├─ Frameworks
   ├─ Maatregelen
   ├─ Uitgangspunten
   ├─ Risicokader
   ├─ Analyses
   ├─ Relaties
   ├─ Rapportage
   └─ Backlog

── INRICHTEN             ← can_configure
   ├─ Mijn Organisatie
   ├─ Beleid
   ├─ Scopes
   ├─ Assets
   └─ Leveranciers
```

### Toezichthouder (16 pagina's, alleen-lezen)

```
MS Hub
Dashboard

── DOEN
   ├─ Risico's
   ├─ Controls
   ├─ Compliance
   ├─ Assessments
   ├─ Incidenten
   └─ In-Control

── ONTDEKKEN             ← can_discover
   ├─ Frameworks
   ├─ Maatregelen
   ├─ Uitgangspunten
   ├─ Risicokader
   ├─ Analyses
   ├─ Relaties
   ├─ Rapportage
   └─ Backlog
```

> **Let op:** Toezichthouder ziet DOEN en ONTDEKKEN, maar NIET Besluiten (vereist `can_configure`) en NIET INRICHTEN of BEHEER.

### Coordinator (alle pagina's behalve Beheer-paneel)

```
MS Hub
Dashboard
── DOEN (alles incl. Besluiten)
── ONTDEKKEN (alles)
── INRICHTEN (alles)
── BEHEER
   └─ Gebruikers
```

### Beheerder (alles)

```
MS Hub
Dashboard
── DOEN (alles)
── ONTDEKKEN (alles)
── INRICHTEN (alles)
── BEHEER
   ├─ Gebruikers
   └─ Beheer              ← is_admin
```

---

## 4. Beveiligingslagen (Defense in Depth)

Toegangscontrole wordt op **drie niveaus** afgedwongen:

### Laag 1: Navigatie verbergen (UX)

**Bestand:** `frontend/ims/components/layout.py`

Menu-items worden conditioneel gerenderd op basis van `AuthState`-permissies:

| Navigatie-item | Conditie |
|----------------|----------|
| MS Hub | `AuthState.can_discover` |
| Besluiten (in DOEN) | `AuthState.can_configure` |
| ONTDEKKEN (hele sectie) | `AuthState.can_discover` |
| INRICHTEN (hele sectie) | `AuthState.can_configure` |
| BEHEER (hele sectie) | `AuthState.can_manage_users` |
| Beheer-paneel (in BEHEER) | `AuthState.is_admin` |

### Laag 2: Page-level guard (frontend)

Directe URL-navigatie (bv. `/decisions` intypen) wordt geblokkeerd met `rx.cond()` in de pagina-functie:

```python
def decisions_page() -> rx.Component:
    return layout(
        rx.cond(AuthState.can_configure, decisions_content(), _no_access()),
        ...
    )
```

| Pagina | Guard |
|--------|-------|
| `/ms-hub` | `can_discover` |
| `/decisions` | `can_configure` |
| `/frameworks` | `can_discover` |
| `/measures` | `can_discover` |
| `/simulation` | `can_discover` |
| `/relaties` | `can_discover` |
| `/reports` | `can_discover` |
| `/policy-principles` | `can_discover` |
| `/risk-framework` | `can_discover` |
| `/policies` | `can_configure` |
| `/scopes` | `can_configure` |
| `/assets` | `can_configure` |
| `/suppliers` | `can_configure` |
| `/users` | `can_manage_users` |
| `/admin` | `is_admin` |

### Laag 3: API-enforcement (backend)

Elke schrijfoperatie controleert de rol via FastAPI-dependencies:

```python
# backend/app/core/rbac.py
require_admin = require_role(Role.BEHEERDER)
require_coordinator_or_admin = require_role(Role.BEHEERDER, Role.COORDINATOR)
require_editor = require_role(Role.BEHEERDER, Role.COORDINATOR, Role.EIGENAAR, Role.MEDEWERKER)
require_configurer = require_role(Role.BEHEERDER, Role.COORDINATOR, Role.EIGENAAR)
require_oversight = require_role(Role.BEHEERDER, Role.COORDINATOR, Role.TOEZICHTHOUDER)
```

Superusers (`is_superuser = True`) bypassen alle rolcontroles.

---

## 5. Paginaoverzicht met roltoegang

| # | Pagina | Route | Beheerder | Coordinator | Eigenaar | Medewerker | Toezichthouder |
|---|--------|-------|:---------:|:-----------:|:--------:|:----------:|:--------------:|
| 1 | Dashboard | `/` | x | x | x | x | x |
| 2 | MS Hub | `/ms-hub` | x | x | x | | x |
| 3 | Risico's | `/risks` | x | x | x | x | x |
| 4 | Controls | `/controls` | x | x | x | x | x |
| 5 | Compliance | `/compliance` | x | x | x | x | x |
| 6 | Assessments | `/assessments` | x | x | x | x | x |
| 7 | Incidenten | `/incidents` | x | x | x | x | x |
| 8 | Besluiten | `/decisions` | x | x | x | | |
| 9 | In-Control | `/in-control` | x | x | x | x | x |
| 10 | Frameworks | `/frameworks` | x | x | x | | x |
| 11 | Maatregelen | `/measures` | x | x | x | | x |
| 12 | Uitgangspunten | `/policy-principles` | x | x | x | | x |
| 13 | Risicokader | `/risk-framework` | x | x | x | | x |
| 14 | Analyses | `/simulation` | x | x | x | | x |
| 15 | Relaties | `/relaties` | x | x | x | | x |
| 16 | Rapportage | `/reports` | x | x | x | | x |
| 17 | Backlog | `/backlog` | x | x | x | | x |
| 18 | Mijn Organisatie | `/organization` | x | x | x | | |
| 19 | Beleid | `/policies` | x | x | x | | |
| 20 | Scopes | `/scopes` | x | x | x | | |
| 21 | Assets | `/assets` | x | x | x | | |
| 22 | Leveranciers | `/suppliers` | x | x | x | | |
| 23 | Gebruikers | `/users` | x | x | | | |
| 24 | Beheer | `/admin` | x | | | | |
| | **Totaal pagina's** | | **24** | **23** | **22** | **7** | **16** |
