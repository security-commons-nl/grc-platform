# Plan: Mijn Organisatie — Tooltips + AI-Prefill

## Doel

Twee verbeteringen aan de onboarding wizard op `/organization`:

1. **Tooltips bij vakjargon** — uitleg van termen én gradaties (laag/midden/hoog)
2. **AI-prefill na stap 1** — op basis van Identiteit automatisch voorzet doen voor stap 2–6

---

## Huidige architectuur (referentie)

| Laag | Bestand | Beschrijving |
|------|---------|--------------|
| **Database model** | `backend/app/models/core_models.py` (r.3639-3699) | `OrganizationProfile` SQLModel met 36 velden + meta |
| **Enums** | `backend/app/models/core_models.py` (r.585-652) | `OrgType`, `Sector`, `EmployeeRange`, `GovernanceMaturity`, `ProfileRiskAppetite`, etc. |
| **API endpoints** | `backend/app/api/v1/endpoints/organization_profile.py` | GET/PUT/PATCH `/organization-profile/` + `/completion` |
| **Router** | `backend/app/api/v1/api.py` (r.272-277) | Registreert `organization_profile.router` op prefix `/organization-profile` |
| **API client** | `frontend/ims/api/client.py` (r.1747-1773) | `get_organization_profile()`, `upsert_*`, `patch_*`, `get_profile_completion()` |
| **State** | `frontend/ims/state/organization_profile.py` | `OrganizationProfileState` — 36 string-vars, wizard-meta, event handlers |
| **Page** | `frontend/ims/pages/organization.py` | Wizard (6 stappen) + profielweergave (accordeons) |

---

## Wijziging 1: Tooltips bij velden

### Welke velden krijgen tooltips?

| Stap | Veld | Tooltip-inhoud |
|------|------|----------------|
| Governance | Governance volwassenheid | Uitleg CMM-niveaus: Startend (ad hoc, geen formeel beleid) → Basis (basale processen) → Gedefinieerd (gedocumenteerd) → Beheerst (gemeten & gestuurd) → Geoptimaliseerd (continu verbeterend) |
| Governance | Risicobereidheid — Beschikbaarheid | "Hoeveel uitval accepteert uw organisatie?" Laag = minimaal risico acceptabel, systemen moeten altijd beschikbaar zijn. Midden = beperkte uitval acceptabel (uren). Hoog = langere uitval acceptabel (dagen). |
| Governance | Risicobereidheid — Integriteit | "Hoeveel risico op onjuiste data accepteert uw organisatie?" Laag = data moet altijd 100% correct zijn. Midden = incidentele fouten acceptabel mits herstelbaar. Hoog = fouten acceptabel, geen directe impact. |
| Governance | Risicobereidheid — Vertrouwelijkheid | "Hoeveel risico op ongeautoriseerde toegang accepteert uw organisatie?" Laag = nultolerantie op datalekken. Midden = beperkt risico acceptabel met maatregelen. Hoog = openbare data, weinig gevoeligheid. |
| IT-Landschap | Cloud strategie | On-premises = alles in eigen beheer. Hybrid = mix van eigen infra en cloud. Cloud-first = cloud tenzij er een reden is voor on-prem. Full-cloud = alles in de cloud. |
| IT-Landschap | BYOD | "Bring Your Own Device — mogen medewerkers eigen laptops/telefoons gebruiken voor werk?" |
| Privacy | Bijzondere categorieën | "Verwerkt u gezondheidsgegevens, biometrische data, strafrechtelijke gegevens, politieke voorkeur, religie, etnische afkomst of seksuele geaardheid? (Art. 9 AVG)" |
| Privacy | Internationale doorgifte | "Worden persoonsgegevens buiten de EER verwerkt of opgeslagen? Denk aan cloud-diensten met US-datacenters." |
| Continuïteit | BCP | "Bedrijfscontinuïteitsplan — een gedocumenteerd plan om kritieke processen draaiend te houden bij een calamiteit." |
| Continuïteit | Max toelaatbare downtime | "Hoe lang mag uw primaire dienstverlening maximaal stilliggen? Uren = zeer kritisch. Dag = belangrijk. Week = niet tijdkritisch." |
| Mensen | Bewustwordingsprogramma | "Een structureel programma om medewerkers bewust te maken van informatiebeveiliging en privacy, bijv. phishing-simulaties, e-learning." |

### Technisch implementatieplan

#### Database: GEEN WIJZIGINGEN

Tooltips zijn puur UI-teksten. Het model `OrganizationProfile` en de enums blijven ongewijzigd.

#### API: GEEN WIJZIGINGEN

Geen nieuwe endpoints of response-wijzigingen nodig.

#### Frontend: 1 bestand wijzigt

**`frontend/ims/pages/organization.py`**

**Stap 1 — Tooltip-dictionary toevoegen (bovenaan, bij de opties-constanten r.17-33)**

```python
FIELD_TOOLTIPS = {
    "governance_maturity": (
        "Governance volwassenheid (CMM-niveaus):\n"
        "• Startend — Ad hoc, geen formeel beleid\n"
        "• Basis — Basale processen ingericht\n"
        "• Gedefinieerd — Gedocumenteerd en gestandaardiseerd\n"
        "• Beheerst — Gemeten en actief gestuurd\n"
        "• Geoptimaliseerd — Continu verbeterend"
    ),
    "risk_appetite_availability": (
        "Hoeveel uitval accepteert uw organisatie?\n"
        "• Laag — Systemen moeten (vrijwel) altijd beschikbaar zijn\n"
        "• Midden — Beperkte uitval acceptabel (uren)\n"
        "• Hoog — Langere uitval acceptabel (dagen)"
    ),
    "risk_appetite_integrity": (
        "Hoeveel risico op onjuiste data accepteert uw organisatie?\n"
        "• Laag — Data moet altijd 100% correct zijn\n"
        "• Midden — Incidentele fouten acceptabel mits herstelbaar\n"
        "• Hoog — Fouten acceptabel, geen directe impact"
    ),
    "risk_appetite_confidentiality": (
        "Hoeveel risico op ongeautoriseerde toegang accepteert uw organisatie?\n"
        "• Laag — Nultolerantie op datalekken\n"
        "• Midden — Beperkt risico acceptabel met maatregelen\n"
        "• Hoog — Overwegend openbare data, weinig gevoeligheid"
    ),
    "cloud_strategy": (
        "• On-premises — Alles op eigen infrastructuur\n"
        "• Hybrid — Mix van eigen infra en cloud\n"
        "• Cloud-first — Cloud tenzij er een reden is voor on-prem\n"
        "• Full-cloud — Alles in de cloud"
    ),
    "has_byod": "Bring Your Own Device — mogen medewerkers eigen laptops/telefoons gebruiken voor werk?",
    "has_special_categories": (
        "Bijzondere persoonsgegevens (Art. 9 AVG): gezondheidsgegevens, biometrische data, "
        "strafrechtelijke gegevens, politieke voorkeur, religie, etnische afkomst, seksuele geaardheid."
    ),
    "international_transfers": (
        "Worden persoonsgegevens buiten de EER verwerkt of opgeslagen? "
        "Denk aan cloud-diensten met datacenters in de VS."
    ),
    "has_bcp": (
        "Bedrijfscontinuïteitsplan — een gedocumenteerd plan om kritieke processen "
        "draaiend te houden bij een calamiteit (brand, cyberaanval, stroomuitval)."
    ),
    "max_tolerable_downtime": (
        "Hoe lang mag uw primaire dienstverlening maximaal stilliggen?\n"
        "• Uren — Zeer kritisch (bijv. 112-meldkamer)\n"
        "• Dag — Belangrijk maar kort herstelbaar\n"
        "• Week — Niet tijdkritisch"
    ),
    "has_awareness_program": (
        "Een structureel programma om medewerkers bewust te maken van informatiebeveiliging "
        "en privacy. Bijv. phishing-simulaties, e-learning, escape rooms."
    ),
}
```

**Stap 2 — Form helpers uitbreiden met optionele `tooltip` parameter (r.58-114)**

De bestaande `form_select()`, `form_bool_select()`, `form_input()` en `form_textarea()` krijgen een optionele `tooltip: str = ""` parameter. De label wordt gewrapped in een `rx.hstack` met een `rx.tooltip(rx.icon("info"))` als de tooltip niet leeg is:

```python
def form_select(label, value, on_change, options, placeholder="Selecteer...", tooltip=""):
    label_el = rx.hstack(
        rx.text(label, size="2", weight="medium"),
        rx.tooltip(
            rx.icon("info", size=14, color="var(--gray-a9)", cursor="help"),
            content=rx.text(tooltip, size="1", white_space="pre-line"),
            max_width="320px",
            side="top",
        ) if tooltip else rx.fragment(),
        spacing="1", align="center",
    ) if tooltip else rx.text(label, size="2", weight="medium")
    return rx.vstack(
        label_el,
        rx.select(options, value=value, on_change=on_change, placeholder=placeholder, width="100%"),
        spacing="1", width="100%",
    )
```

Idem voor `form_bool_select()`.

**Stap 3 — Stap-functies aanpassen (r.121-208)**

De 11 velden die een tooltip krijgen worden aangepast. Voorbeeld `step_governance()`:

```python
# Was:
form_select("Governance volwassenheid", S.governance_maturity, S.set_governance_maturity, MATURITY_OPTIONS),

# Wordt:
form_select("Governance volwassenheid", S.governance_maturity, S.set_governance_maturity, MATURITY_OPTIONS,
            tooltip=FIELD_TOOLTIPS["governance_maturity"]),
```

#### Samenvatting wijziging 1

| Component | Bestand | Actie |
|-----------|---------|-------|
| Database | — | Geen wijziging |
| API | — | Geen wijziging |
| Frontend page | `frontend/ims/pages/organization.py` | `FIELD_TOOLTIPS` dict + tooltip param in form helpers + 11 veldaanroepen |

---

## Wijziging 2: AI-Prefill na stap 1 (Identiteit)

### Concept

Na het opslaan van stap 1 (Identiteit) roept de frontend een nieuw endpoint aan dat op basis van organisatietype, sector en omvang een voorzet genereert voor alle velden van stap 2–6. Alleen **lege** velden worden ingevuld — eerder ingevulde waarden worden nooit overschreven.

### Voorbeeldlogica (Gemeente, Overheid, 500+)

| Veld | Voorgestelde waarde | Rationale |
|------|-------------------|-----------|
| **Governance** | | |
| Frameworks | BIO, AVG | Verplicht voor gemeenten |
| Security Officer | Ja | Verplicht bij BIO |
| FG / DPO | Ja | Verplicht bij gemeenten (AVG art. 37) |
| Volwassenheid | Basis | Conservatieve schatting |
| Risico beschikbaarheid | Laag | Publieke dienstverlening = hoge beschikbaarheidseis |
| Risico integriteit | Laag | Basisregistraties moeten accuraat zijn |
| Risico vertrouwelijkheid | Laag | Gevoelige burgerdata |
| **IT-Landschap** | | |
| Cloud strategie | Hybrid | Typisch voor gemeenten |
| Thuiswerken | Ja | Post-COVID standaard |
| BYOD | Nee | Gemeenten gebruiken managed devices |
| IT uitbesteed | Ja | Veel gemeenten besteden IT uit |
| **Privacy** | | |
| Persoonsgegevens | Ja | Gemeenten verwerken altijd persoonsgegevens |
| Betrokkenen | Burgers, Medewerkers | Kernbetrokkenen |
| Bijzondere categorieën | Ja | WMO, Jeugdzorg = gezondheidsgegevens |
| Internationale doorgifte | Nee | Overheid blijft doorgaans in EU |
| Verwerkingen | 100+ | Grote gemeente = veel verwerkingen |
| **Continuïteit** | | |
| BCP | Nee | Veel gemeenten hebben dit nog niet |
| Incident Response | Nee | Idem |
| Max downtime | Dag | Kritiek maar niet uren-kritisch |
| **Mensen** | | |
| Bewustwording | Ja | BIO vereist dit |
| Screening | Ja | Overheidsfunctie = VOG |
| Training | Jaarlijks | Minimumeis BIO |

### Gekozen aanpak: Rule-based (deterministisch)

Reden: de meeste IMS-gebruikers zijn overheidsorganisaties (gemeenten, waterschappen, provincies, ZBO's). De combinaties zijn voorspelbaar. LLM-based prefill kan later als upgrade.

### Technisch implementatieplan

#### Database: GEEN WIJZIGINGEN

De prefill-logica gebruikt de bestaande `OrganizationProfile`-velden. Er worden geen nieuwe kolommen toegevoegd. De rules leven puur in code.

#### API: 1 nieuw endpoint toevoegen

**Nieuw bestand: `backend/app/api/v1/endpoints/org_prefill.py`**

```python
"""
Organization profile prefill — rule-based suggestions based on identity block.
"""
from fastapi import APIRouter, Depends
from typing import Any, Dict
from app.core.rbac import require_configurer
from app.models.core_models import User

router = APIRouter()

# ──────────────────────────────────────────────────────────
# Prefill-regels per (org_type, sector) combinatie
# Waarden komen overeen met de enums in core_models.py
# ──────────────────────────────────────────────────────────
PREFILL_RULES: Dict[tuple, Dict[str, Any]] = {
    ("Gemeente", "Overheid"): {
        # Governance
        "applicable_frameworks": "BIO, AVG",
        "has_security_officer": True,
        "has_dpo": True,
        "governance_maturity": "Basis",
        "risk_appetite_availability": "Laag",
        "risk_appetite_integrity": "Laag",
        "risk_appetite_confidentiality": "Laag",
        # IT-Landschap
        "cloud_strategy": "Hybrid",
        "has_remote_work": True,
        "has_byod": False,
        "outsourced_it": True,
        # Privacy
        "processes_personal_data": True,
        "data_subject_types": "Burgers, Medewerkers",
        "has_special_categories": True,
        "international_transfers": False,
        "processing_count_estimate": "100+",
        # Continuïteit
        "has_bcp": False,
        "has_incident_response_plan": False,
        "max_tolerable_downtime": "Dag",
        # Mensen
        "has_awareness_program": True,
        "has_background_checks": True,
        "training_frequency": "Jaarlijks",
    },
    ("Waterschap", "Overheid"): {
        # Vergelijkbaar met gemeente, maar specifieke nuances
        "applicable_frameworks": "BIO, AVG",
        "has_security_officer": True,
        "has_dpo": True,
        "governance_maturity": "Basis",
        "risk_appetite_availability": "Laag",  # Waterbeheersing = kritiek
        "risk_appetite_integrity": "Laag",
        "risk_appetite_confidentiality": "Midden",
        "cloud_strategy": "Hybrid",
        "has_remote_work": True,
        "has_byod": False,
        "outsourced_it": True,
        "processes_personal_data": True,
        "data_subject_types": "Burgers, Medewerkers",
        "has_special_categories": False,
        "international_transfers": False,
        "processing_count_estimate": "11-50",
        "has_bcp": False,
        "has_incident_response_plan": False,
        "max_tolerable_downtime": "Uren",  # Waterbeheer = uren-kritisch
        "has_awareness_program": True,
        "has_background_checks": True,
        "training_frequency": "Jaarlijks",
    },
    ("Provincie", "Overheid"): {
        # Vergelijkbaar met gemeente
        "applicable_frameworks": "BIO, AVG",
        "has_security_officer": True,
        "has_dpo": True,
        "governance_maturity": "Basis",
        "risk_appetite_availability": "Midden",
        "risk_appetite_integrity": "Laag",
        "risk_appetite_confidentiality": "Laag",
        "cloud_strategy": "Hybrid",
        "has_remote_work": True,
        "has_byod": False,
        "outsourced_it": True,
        "processes_personal_data": True,
        "data_subject_types": "Burgers, Medewerkers",
        "has_special_categories": False,
        "international_transfers": False,
        "processing_count_estimate": "51-100",
        "has_bcp": False,
        "has_incident_response_plan": False,
        "max_tolerable_downtime": "Dag",
        "has_awareness_program": True,
        "has_background_checks": True,
        "training_frequency": "Jaarlijks",
    },
    ("Zorginstelling", "Zorg"): {
        "applicable_frameworks": "NEN 7510, AVG",
        "has_security_officer": True,
        "has_dpo": True,
        "governance_maturity": "Basis",
        "risk_appetite_availability": "Laag",  # Patiëntenzorg
        "risk_appetite_integrity": "Laag",     # Medische data
        "risk_appetite_confidentiality": "Laag",  # Gezondheidsgegevens
        "cloud_strategy": "Hybrid",
        "has_remote_work": False,
        "has_byod": False,
        "outsourced_it": True,
        "processes_personal_data": True,
        "data_subject_types": "Patiënten, Medewerkers",
        "has_special_categories": True,  # Gezondheidsgegevens
        "international_transfers": False,
        "processing_count_estimate": "100+",
        "has_bcp": False,
        "has_incident_response_plan": False,
        "max_tolerable_downtime": "Uren",
        "has_awareness_program": True,
        "has_background_checks": True,
        "training_frequency": "Jaarlijks",
    },
    ("Onderwijsinstelling", "Onderwijs"): {
        "applicable_frameworks": "AVG",
        "has_security_officer": False,
        "has_dpo": True,
        "governance_maturity": "Startend",
        "risk_appetite_availability": "Midden",
        "risk_appetite_integrity": "Midden",
        "risk_appetite_confidentiality": "Laag",  # Leerlinggegevens
        "cloud_strategy": "Cloud-first",
        "has_remote_work": True,
        "has_byod": True,
        "outsourced_it": True,
        "processes_personal_data": True,
        "data_subject_types": "Leerlingen, Medewerkers, Ouders",
        "has_special_categories": True,  # Leerlingdossiers
        "international_transfers": False,
        "processing_count_estimate": "51-100",
        "has_bcp": False,
        "has_incident_response_plan": False,
        "max_tolerable_downtime": "Dag",
        "has_awareness_program": False,
        "has_background_checks": True,  # VOG verplicht
        "training_frequency": "Jaarlijks",
    },
    # Fallback-combinaties worden later toegevoegd voor:
    # ZBO, SSC, Ministerie, Bedrijf + Financieel/IT/Transport/Energie
}

# ──────────────────────────────────────────────────────────
# Scaling modifiers op basis van omvang
# Overschrijft specifieke velden bij grote/kleine organisaties
# ──────────────────────────────────────────────────────────
SIZE_MODIFIERS: Dict[str, Dict[str, Any]] = {
    "500+": {
        "has_security_officer": True,    # Altijd bij grote organisaties
        "has_awareness_program": True,
    },
    "1-50": {
        "outsourced_it": True,           # Kleine org besteedt alles uit
        "governance_maturity": "Startend",
        "has_bcp": False,
    },
}


@router.post("/prefill")
async def prefill_from_identity(
    payload: Dict[str, Any],
    current_user: User = Depends(require_configurer),
) -> Dict[str, Any]:
    """
    Return suggested prefill values for wizard steps 2-6
    based on the identity block (step 1).

    Only returns fields that have a rule-based suggestion.
    The frontend decides whether to apply them (only to empty fields).
    """
    org_type = payload.get("org_type", "")
    sector = payload.get("sector", "")
    employee_count = payload.get("employee_count", "")

    # 1. Lookup exact (org_type, sector) match
    suggestions = dict(PREFILL_RULES.get((org_type, sector), {}))

    # 2. Apply size modifiers (override specific fields)
    size_mods = SIZE_MODIFIERS.get(employee_count, {})
    suggestions.update(size_mods)

    return {"suggestions": suggestions, "source": "rule-based"}
```

**Router registratie: `backend/app/api/v1/api.py`**

Toevoegen na de bestaande organization-profile router (r.277):

```python
from app.api.v1.endpoints import org_prefill

api_router.include_router(
    org_prefill.router,
    prefix="/organization-profile",
    tags=["Organization Profile"],
)
```

Het endpoint wordt dus: `POST /api/v1/organization-profile/prefill`

**RBAC:** Zelfde als bestaande PATCH — `require_configurer` (Admin/Coordinator/Eigenaar).

#### Frontend: 3 bestanden wijzigen

**Bestand 1: `frontend/ims/api/client.py`**

Nieuwe method toevoegen (na r.1773):

```python
async def prefill_organization_profile(self, identity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get prefill suggestions based on identity block."""
    async with self._get_client() as client:
        response = await client.post(
            "/organization-profile/prefill",
            json=identity_data,
        )
        response.raise_for_status()
        return response.json()
```

**Bestand 2: `frontend/ims/state/organization_profile.py`**

Nieuwe state variabelen (bij r.24):

```python
# --- Prefill tracking ---
prefilled_fields: list[str] = []    # Lijst van veld-namen die door prefill zijn ingevuld
prefill_applied: bool = False        # Heeft de gebruiker een prefill ontvangen?
is_prefilling: bool = False          # Loading state voor prefill-call
```

Nieuwe event handler (na `next_step()` r.199):

```python
async def prefill_from_identity(self):
    """Fetch prefill suggestions after step 0 and apply to empty fields only."""
    self.is_prefilling = True
    try:
        identity_data = self._build_step_payload(0)  # Stap 0 = Identiteit
        result = await api_client.prefill_organization_profile(identity_data)
        suggestions = result.get("suggestions", {})

        newly_filled = []
        for field, value in suggestions.items():
            current = getattr(self, field, "")
            # Alleen lege velden invullen
            if current == "" or current is None:
                if field in self._BOOL_FIELDS:
                    setattr(self, field, self._bool_to_str(value))
                elif field in self._INT_FIELDS:
                    setattr(self, field, str(value) if value is not None else "")
                else:
                    setattr(self, field, str(value) if value is not None else "")
                newly_filled.append(field)

        self.prefilled_fields = newly_filled
        self.prefill_applied = len(newly_filled) > 0
        self.error = ""
    except Exception as e:
        # Prefill is optioneel — bij fout gewoon doorgaan
        self.error = ""
        self.prefill_applied = False
    finally:
        self.is_prefilling = False
```

Aanpassing `next_step()` (r.195-199) — prefill triggeren na stap 0:

```python
async def next_step(self):
    """Save current step and advance. After step 0: trigger prefill."""
    await self.save_step()
    if self.active_step == 0 and not self.prefill_applied:
        await self.prefill_from_identity()
    if self.active_step < 5:
        self.active_step += 1
```

Reset bij `start_wizard()` (r.210-213):

```python
def start_wizard(self):
    self.show_wizard = True
    self.active_step = 0
    self.prefilled_fields = []
    self.prefill_applied = False
```

**Bestand 3: `frontend/ims/pages/organization.py`**

Visuele feedback — info-banner tonen in wizard wanneer prefill is toegepast.

Na de step-header in `wizard_view()` (r.341, na `rx.separator()`):

```python
# Prefill banner — alleen tonen als er suggesties zijn toegepast
rx.cond(
    S.prefill_applied & (S.active_step > 0),
    rx.callout(
        "Op basis van uw organisatieprofiel hebben we een voorzet gedaan. "
        "Controleer de ingevulde waarden en pas aan waar nodig.",
        icon="sparkles",
        color_scheme="blue",
        variant="soft",
        width="100%",
    ),
),
```

Optioneel: visuele markering van prefilled velden. Dit kan door de form helpers uit te breiden met een `is_prefilled` parameter die een subtiele `outline` toevoegt:

```python
def form_select(label, value, on_change, options, placeholder="Selecteer...",
                tooltip="", is_prefilled=False):
    # ... bestaande logica ...
    select_el = rx.select(
        options, value=value, on_change=on_change,
        placeholder=placeholder, width="100%",
        # Blauwe outline als prefilled
        **({
            "outline": "1.5px solid var(--blue-a6)",
            "border_radius": "var(--radius-2)",
        } if is_prefilled else {}),
    )
    # ...
```

In de stap-functies wordt dit dan:

```python
form_select("Cloud strategie", S.cloud_strategy, S.set_cloud_strategy, CLOUD_OPTIONS,
            tooltip=FIELD_TOOLTIPS["cloud_strategy"],
            is_prefilled=S.prefilled_fields.contains("cloud_strategy")),
```

> **Let op:** `rx.Var.contains()` werkt op lists in Reflex. Als dit niet direct werkt, alternatief: een computed var per veld, of simpelweg de banner als enige indicator.

#### AI: GEEN WIJZIGINGEN (nu)

De prefill is rule-based. Geen LLM-calls. De AI-laag (Ollama/Mistral) wordt niet aangesproken.

**Toekomstige upgrade:** als rule-based niet volstaat (bijv. voor onbekende org_type/sector-combinaties), kan het endpoint uitgebreid worden met een LLM-fallback:

```python
@router.post("/prefill")
async def prefill_from_identity(payload, ...):
    suggestions = PREFILL_RULES.get((org_type, sector), None)
    if suggestions is None:
        # Fallback naar LLM
        suggestions = await llm_generate_prefill(payload)
    return {"suggestions": suggestions, "source": "rule-based" | "llm"}
```

Dit valt buiten de huidige scope.

---

## Overzicht alle wijzigingen per component

### Database (0 wijzigingen)

Geen model- of migratiewijzigingen nodig.

### API / Backend (2 bestanden)

| Bestand | Actie | Details |
|---------|-------|---------|
| `backend/app/api/v1/endpoints/org_prefill.py` | **NIEUW** | Prefill-rules dict + POST `/prefill` endpoint |
| `backend/app/api/v1/api.py` | **EDIT** r.277 | Router toevoegen voor `org_prefill` |

### Frontend (3 bestanden)

| Bestand | Actie | Details |
|---------|-------|---------|
| `frontend/ims/pages/organization.py` | **EDIT** | `FIELD_TOOLTIPS` dict, tooltip-param in form helpers, 11 tooltip-aanroepen, prefill-banner, optionele prefill-markering |
| `frontend/ims/state/organization_profile.py` | **EDIT** | `prefilled_fields`, `prefill_applied`, `is_prefilling` vars + `prefill_from_identity()` handler + `next_step()` aanpassing |
| `frontend/ims/api/client.py` | **EDIT** | Nieuwe method `prefill_organization_profile()` |

### AI (0 wijzigingen)

Geen LLM-integratie in deze fase.

---

## Volgorde van implementatie

| Stap | Wat | Risico | Afhankelijkheid |
|------|-----|--------|-----------------|
| 1 | Tooltips in `organization.py` | Laag — puur UI | Geen |
| 2 | Prefill-rules endpoint (`org_prefill.py` + router) | Laag — nieuw endpoint, raakt niets bestaands | Geen |
| 3 | API client method (`client.py`) | Laag | Stap 2 |
| 4 | State: prefill handler + next_step aanpassing | Midden — wijzigt bestaande flow | Stap 3 |
| 5 | UI: prefill banner + optionele veldmarkering | Laag — visueel | Stap 4 |

---

## Niet in scope

- LLM-based prefill (kan later als upgrade op stap 2)
- Inline editing in profielweergave (apart verhaal)
- Wijzigingen aan het databasemodel `OrganizationProfile`
- Prefill-regels voor alle org_type/sector-combinaties (initieel: 5 combinaties, rest later)
