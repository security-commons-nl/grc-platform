# Plan: Risk-Scope Contextualisatie (RiskScope koppeltabel)

**Doel:** Risico's scope-gebonden maken via koppeltabel, zonder het generieke risico-concept te breken.
Eenzelfde Risk kan in meerdere Scopes voorkomen met eigen scores, owner, behandelstrategie en acceptatie.

**Bron:** E-mail Bas Stevens (09-02-2026)

---

## Huidige situatie (IST)

| Entiteit | PK type | Scope-relatie | Opmerkingen |
|---|---|---|---|
| `Risk` | `int` | `scope_id: Optional[int]` (single FK) | Bevat alle scores, treatment, acceptance inline |
| `Control` | `int` | `scope_id: Optional[int]` | Al scope-gebonden |
| `ControlRiskLink` | composite PK (`risk_id, control_id`) | Geen scope | `mitigation_percent: int` |
| `DecisionRiskLink` | `id: int` PK | Geen scope | `notes, created_at` |
| `Decision` | `int` | `scope_id: Optional[int]` | Heeft al een scope-link |
| Scores | `RiskLevel` enum (Low/Med/High/Critical) | Op Risk zelf | `inherent_*`, `residual_*`, `vulnerability_score`, etc. |
| `InControlAssessment` | `int` | `scope_id: int` | Leest risico's per scope |

**Probleem:** Risk.scope_id is 1:1 -- hetzelfde risico kan niet in meerdere scopes met eigen context bestaan.

---

## Doelsituatie (SOLL)

```
Risk (generiek)          Scope
  │  1                      │ 1
  └────── RiskScope ────────┘
           │ 1:N                ← per-scope scores, owner, treatment, acceptance
           │
     ControlRiskScopeLink    DecisionRiskScopeLink
           │                       │
        Control              Decision
```

---

## Stap 0: Voorbereiding

### 0.1 Nieuwe Enums

Toevoegen aan `core_models.py` (boven de model-klassen):

```python
class AcceptanceStatus(str, Enum):
    PROPOSED = "Voorgesteld"
    ACCEPTED = "Geaccepteerd"
    REJECTED = "Afgewezen"
    EXPIRED = "Verlopen"
```

> `TreatmentStrategy` bestaat al (Vermijden/Reduceren/Overdragen/Accepteren).

### 0.2 Validatie bestaande data

Voor backfill moeten we weten:
- Hoeveel risico's hebben `scope_id IS NULL`? → die gaan naar "Onbekend/Unassigned" scope
- Hoeveel risico's zijn al gekoppeld via `ControlRiskLink` aan een control met scope? → primaire backfill-bron

Query (handmatig draaien voor de migratie):
```sql
-- Risico's met scope
SELECT COUNT(*) FROM risk WHERE scope_id IS NOT NULL;
-- Risico's zonder scope
SELECT COUNT(*) FROM risk WHERE scope_id IS NULL;
-- Risico's die via control-link een scope kunnen afleiden
SELECT DISTINCT r.id
FROM risk r
JOIN controlrisklink crl ON crl.risk_id = r.id
JOIN control c ON c.id = crl.control_id
WHERE c.scope_id IS NOT NULL AND r.scope_id IS NULL;
```

---

## Stap 1: Nieuwe tabel `RiskScope` aanmaken

### 1.1 SQLModel definitie

Toevoegen aan `core_models.py` (sectie RISK MANAGEMENT, na class Risk):

```python
class RiskScope(SQLModel, table=True):
    """
    Contextualisatie van een generiek Risk binnen een specifieke Scope.
    Bevat scope-specifieke scores, eigenaar, behandelstrategie en acceptatie.
    Eenzelfde Risk kan in meerdere Scopes voorkomen.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    risk_id: int = Field(foreign_key="risk.id", index=True)
    scope_id: int = Field(foreign_key="scope.id", index=True)

    # --- Inherent Risk (per scope) ---
    inherent_likelihood: Optional[RiskLevel] = None
    inherent_impact: Optional[RiskLevel] = None
    inherent_risk_score: Optional[int] = None  # 1-16

    # --- Residual Risk (per scope, after controls) ---
    residual_likelihood: Optional[RiskLevel] = None
    residual_impact: Optional[RiskLevel] = None
    residual_risk_score: Optional[int] = None  # 1-16

    # --- Vulnerability & Control Effectiveness ---
    vulnerability_score: Optional[int] = None  # 0-100
    control_effectiveness_pct: Optional[int] = None  # 0-100%

    # --- Attention Strategy (In Control Quadrant) ---
    attention_quadrant: Optional[AttentionQuadrant] = None
    ai_suggested_quadrant: Optional[AttentionQuadrant] = None

    # --- Treatment ---
    mitigation_approach: Optional[MitigationApproach] = None
    treatment_strategy: Optional[TreatmentStrategy] = None
    treatment_justification: Optional[str] = None
    transfer_party: Optional[str] = None

    # --- Governance per scope ---
    owner_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # --- Acceptance ---
    acceptance_status: AcceptanceStatus = AcceptanceStatus.PROPOSED
    accepted_by_decision_id: Optional[int] = Field(default=None, foreign_key="decision.id")
    risk_accepted: bool = False
    accepted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    acceptance_date: Optional[datetime] = None
    acceptance_justification: Optional[str] = None
    risk_appetite_threshold: Optional[RiskLevel] = None

    # --- Review ---
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    review_frequency_months: Optional[int] = None
    is_critical: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    risk: Optional[Risk] = Relationship(back_populates="risk_scopes")
    scope: Optional[Scope] = Relationship(back_populates="risk_scopes")
    control_links: List["ControlRiskScopeLink"] = Relationship(back_populates="risk_scope")
    decision_links: List["DecisionRiskScopeLink"] = Relationship(back_populates="risk_scope")
```

### 1.2 Relationships toevoegen aan Risk en Scope

**Risk** (behoud `scope` relatie tijdelijk voor backward compat):
```python
# Bestaand (DEPRECATED, behouden tot stap 5):
scope: Optional[Scope] = Relationship(back_populates="risks")
control_links: List["ControlRiskLink"] = Relationship(back_populates="risk")

# Nieuw:
risk_scopes: List["RiskScope"] = Relationship(back_populates="risk")
```

**Scope** (toevoegen):
```python
# Bestaand (DEPRECATED):
risks: List["Risk"] = Relationship(back_populates="scope")

# Nieuw:
risk_scopes: List["RiskScope"] = Relationship(back_populates="scope")
```

### 1.3 Alembic migratie (013)

```
backend/alembic/versions/013_add_riskscope_contextualisatie.py
```

Inhoud: `op.create_table("riskscope", ...)` met:
- Alle kolommen uit 1.1
- `UniqueConstraint("tenant_id", "risk_id", "scope_id")`
- `Index("ix_riskscope_tenant_scope", "tenant_id", "scope_id")`
- `Index("ix_riskscope_tenant_risk", "tenant_id", "risk_id")`
- `CheckConstraint` op scores (1-16 range)

---

## Stap 2: Backfill RiskScope records

### 2.1 Primaire bron: Risk.scope_id (directe link)

```sql
INSERT INTO riskscope (
    tenant_id, risk_id, scope_id,
    inherent_likelihood, inherent_impact, inherent_risk_score,
    residual_likelihood, residual_impact, residual_risk_score,
    vulnerability_score, control_effectiveness_pct,
    attention_quadrant, ai_suggested_quadrant,
    mitigation_approach, treatment_strategy, treatment_justification, transfer_party,
    owner_user_id,
    acceptance_status,
    risk_accepted, accepted_by_id, acceptance_date, acceptance_justification,
    risk_appetite_threshold,
    last_review_date, next_review_date, review_frequency_months, is_critical,
    created_at, updated_at
)
SELECT
    r.tenant_id, r.id, r.scope_id,
    r.inherent_likelihood, r.inherent_impact, r.inherent_risk_score,
    r.residual_likelihood, r.residual_impact, r.residual_risk_score,
    r.vulnerability_score, r.control_effectiveness_pct,
    r.attention_quadrant, r.ai_suggested_quadrant,
    r.mitigation_approach, r.treatment_strategy, r.treatment_justification, r.transfer_party,
    NULL,  -- owner_user_id (kan later ingevuld)
    CASE WHEN r.risk_accepted THEN 'Geaccepteerd' ELSE 'Voorgesteld' END,
    r.risk_accepted, r.accepted_by_id, r.acceptance_date, r.acceptance_justification,
    r.risk_appetite_threshold,
    r.last_review_date, r.next_review_date, r.review_frequency_months, r.is_critical,
    now(), now()
FROM risk r
WHERE r.scope_id IS NOT NULL
ON CONFLICT DO NOTHING;
```

### 2.2 Secundaire bron: via ControlRiskLink

Voor risico's zonder `scope_id` maar wél met controls die een scope hebben:

```sql
INSERT INTO riskscope (
    tenant_id, risk_id, scope_id,
    inherent_likelihood, inherent_impact, inherent_risk_score,
    residual_likelihood, residual_impact, residual_risk_score,
    vulnerability_score, control_effectiveness_pct,
    attention_quadrant, treatment_strategy,
    acceptance_status, risk_accepted,
    created_at, updated_at
)
SELECT DISTINCT ON (r.tenant_id, r.id, c.scope_id)
    r.tenant_id, r.id, c.scope_id,
    r.inherent_likelihood, r.inherent_impact, r.inherent_risk_score,
    r.residual_likelihood, r.residual_impact, r.residual_risk_score,
    r.vulnerability_score, r.control_effectiveness_pct,
    r.attention_quadrant, r.treatment_strategy,
    CASE WHEN r.risk_accepted THEN 'Geaccepteerd' ELSE 'Voorgesteld' END,
    r.risk_accepted,
    now(), now()
FROM risk r
JOIN controlrisklink crl ON crl.risk_id = r.id
JOIN control c ON c.id = crl.control_id
WHERE r.scope_id IS NULL
  AND c.scope_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM riskscope rs
      WHERE rs.risk_id = r.id AND rs.scope_id = c.scope_id AND rs.tenant_id = r.tenant_id
  )
ON CONFLICT DO NOTHING;
```

### 2.3 Fallback: Onbekende scope

Per tenant een "Niet-toegewezen" scope aanmaken (of bestaande hergebruiken):

```sql
-- Maak per tenant een fallback scope (als die nog niet bestaat)
INSERT INTO scope (tenant_id, name, type, description, is_active, created_at, updated_at)
SELECT DISTINCT t.id, 'Niet-toegewezen', 'Organization', 'Automatisch aangemaakt voor risicos zonder scope', true, now(), now()
FROM tenant t
WHERE NOT EXISTS (
    SELECT 1 FROM scope s WHERE s.tenant_id = t.id AND s.name = 'Niet-toegewezen'
);

-- Koppel overgebleven risico's
INSERT INTO riskscope (tenant_id, risk_id, scope_id, ..., created_at, updated_at)
SELECT r.tenant_id, r.id, fallback.id, ..., now(), now()
FROM risk r
JOIN scope fallback ON fallback.tenant_id = r.tenant_id AND fallback.name = 'Niet-toegewezen'
WHERE NOT EXISTS (
    SELECT 1 FROM riskscope rs WHERE rs.risk_id = r.id AND rs.tenant_id = r.tenant_id
);
```

### 2.4 Verificatie

```sql
-- Geen orphan risks (elke risk moet minstens 1 riskscope hebben)
SELECT r.id, r.title
FROM risk r
WHERE NOT EXISTS (SELECT 1 FROM riskscope rs WHERE rs.risk_id = r.id);
-- Verwacht: 0 rijen
```

---

## Stap 3: Nieuwe linktabellen

### 3.1 ControlRiskScopeLink

```python
class ControlRiskScopeLink(SQLModel, table=True):
    """Links a Control to a scope-contextualized Risk (RiskScope)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    control_id: int = Field(foreign_key="control.id", index=True)
    risk_scope_id: int = Field(foreign_key="riskscope.id", index=True)

    mitigation_percent: int = 100  # Behoud bestaande semantiek

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    control: Optional[Control] = Relationship(back_populates="risk_scope_links")
    risk_scope: Optional[RiskScope] = Relationship(back_populates="control_links")
```

**Constraint:** `UNIQUE(tenant_id, control_id, risk_scope_id)`

**Backfill:**
```sql
INSERT INTO controlriskscopelink (tenant_id, control_id, risk_scope_id, mitigation_percent, created_at)
SELECT
    c.tenant_id,
    crl.control_id,
    rs.id,
    crl.mitigation_percent,
    now()
FROM controlrisklink crl
JOIN control c ON c.id = crl.control_id
JOIN riskscope rs ON rs.risk_id = crl.risk_id
    AND rs.scope_id = COALESCE(c.scope_id, (
        SELECT s.id FROM scope s WHERE s.tenant_id = c.tenant_id AND s.name = 'Niet-toegewezen' LIMIT 1
    ))
    AND rs.tenant_id = c.tenant_id
ON CONFLICT DO NOTHING;
```

### 3.2 DecisionRiskScopeLink

```python
class DecisionRiskScopeLink(SQLModel, table=True):
    """Links a Decision to a scope-contextualized Risk (RiskScope)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    decision_id: int = Field(foreign_key="decision.id", index=True)
    risk_scope_id: int = Field(foreign_key="riskscope.id", index=True)

    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    decision: Optional[Decision] = Relationship(back_populates="risk_scope_links")
    risk_scope: Optional[RiskScope] = Relationship(back_populates="decision_links")
```

**Constraint:** `UNIQUE(tenant_id, decision_id, risk_scope_id)`

**Backfill:**
```sql
INSERT INTO decisionriskscopelink (tenant_id, decision_id, risk_scope_id, notes, created_at)
SELECT
    d.tenant_id,
    drl.decision_id,
    rs.id,
    drl.notes,
    now()
FROM decisionrisklink drl
JOIN decision d ON d.id = drl.decision_id
JOIN riskscope rs ON rs.risk_id = drl.risk_id
    AND rs.scope_id = COALESCE(d.scope_id, (
        SELECT s.id FROM scope s WHERE s.tenant_id = d.tenant_id AND s.name = 'Niet-toegewezen' LIMIT 1
    ))
    AND rs.tenant_id = d.tenant_id
ON CONFLICT DO NOTHING;
```

### 3.3 Relationships toevoegen aan Control en Decision

**Control** (toevoegen):
```python
# Bestaand (DEPRECATED):
risk_links: List["ControlRiskLink"] = Relationship(back_populates="control")

# Nieuw:
risk_scope_links: List["ControlRiskScopeLink"] = Relationship(back_populates="control")
```

**Decision** (toevoegen):
```python
# Bestaand (DEPRECATED):
risk_links: List["DecisionRiskLink"] = Relationship(back_populates="decision")

# Nieuw:
risk_scope_links: List["DecisionRiskScopeLink"] = Relationship(back_populates="decision")
```

---

## Stap 4: API-wijzigingen

### 4.1 Nieuwe endpoints

**File:** `backend/app/api/v1/endpoints/risk_scopes.py` (nieuw)

| Method | Path | Beschrijving |
|---|---|---|
| `GET` | `/risk-scopes/` | Lijst alle RiskScopes (filter op tenant) |
| `GET` | `/risk-scopes/{id}` | Detail van een RiskScope |
| `POST` | `/risk-scopes/` | Koppel risk aan scope met scores |
| `PUT` | `/risk-scopes/{id}` | Update scores/treatment/acceptance |
| `DELETE` | `/risk-scopes/{id}` | Verwijder koppeling |
| `GET` | `/scopes/{scope_id}/risks` | Alle risico's in een scope (via RiskScope) |
| `GET` | `/risks/{risk_id}/scopes` | Alle scopes van een risk (via RiskScope) |

### 4.2 Aanpassingen bestaande endpoints

**`risks.py`:**
- `GET /risks/` behouden (generieke risk-lijst), maar response verrijken met `risk_scopes` count
- `POST /risks/` aanpassen: als `scope_id` wordt meegegeven, automatisch een RiskScope aanmaken
- **Deprecation notice** op score-velden in Risk zelf (ze worden read-only, data komt uit RiskScope)

**`decisions.py`:**
- Accept-endpoint accepteert `risk_scope_id` i.p.v. `risk_id`
- Backward compat: als `risk_id` wordt gestuurd, zoek de RiskScope op (of error als ambigue)

### 4.3 Router registratie

In `backend/app/api/v1/api.py`:
```python
from app.api.v1.endpoints import risk_scopes
api_router.include_router(risk_scopes.router, prefix="/risk-scopes", tags=["Risk Scopes"])
```

---

## Stap 5: Frontend-wijzigingen

### 5.1 Risk detail pagina (`frontend/ims/pages/risks.py`)

- Toon lijst van scopes (RiskScopes) als primaire context
- Per scope: eigen heatmap scores, owner, treatment, acceptance status
- "Toevoegen aan scope" button → modal met scope-picker + score-invoer

### 5.2 Scope detail pagina

- Tab/sectie "Risico's" toont RiskScopes voor deze scope
- In-Control berekening gebruikt RiskScope queries

### 5.3 Risk state (`frontend/ims/state/risk.py`)

- Nieuwe state-variabelen voor `risk_scopes`
- API calls naar `/risk-scopes/` endpoints
- Backward compat: als er maar 1 RiskScope is, toon inline

---

## Stap 6: InControlAssessment aanpassen

`InControlAssessment` (regel 1498) telt nu risico's via `Risk.scope_id`. Aanpassen:

```python
# OUD:
open_risks = select(Risk).where(Risk.scope_id == scope_id, Risk.status == Status.ACTIVE)

# NIEUW:
open_risks = (
    select(RiskScope)
    .where(RiskScope.scope_id == scope_id, RiskScope.tenant_id == tenant_id)
    .join(Risk)
    .where(Risk.status == Status.ACTIVE)
)
```

---

## Stap 7: Agent sync

Volgens CLAUDE.md agent-sync-regel: update de relevante domain agents.

| Agent | Wijziging |
|---|---|
| `risk_agent.py` | System prompt: vermeld RiskScope, multi-scope risico's. Tools: CRUD risk-scopes |
| `scope_agent.py` | System prompt: vermeld dat scopes nu RiskScopes bevatten |
| `improvement_agent.py` | Vermeld dat acceptatie nu per RiskScope gaat |
| `measure_agent.py` | ControlRiskScopeLink i.p.v. ControlRiskLink |

---

## Stap 8: Deprecatie oude structuur (later, na 1-2 releases)

### 8.1 Na release 1 (soft deprecation)

- `Risk.scope_id` markeren als deprecated in docstring
- `Risk.inherent_*`, `Risk.residual_*`, etc. markeren als deprecated
- `ControlRiskLink` en `DecisionRiskLink` markeren als deprecated
- API geeft deprecation warning header bij gebruik oude velden

### 8.2 Na release 2 (hard removal)

- Drop `Risk.scope_id` kolom
- Drop score-velden van Risk (bewaar alleen title/description/category/template/MAPGOOD)
- Drop `ControlRiskLink` tabel
- Drop `DecisionRiskLink` tabel
- Drop fallback code in API

---

## Impact op bestaande businessregels

| Regel | Oud | Nieuw |
|---|---|---|
| "Score >= 9 vereist DT-besluit" | `Risk.residual_risk_score` | `RiskScope.residual_risk_score` |
| In-Control berekening | `Risk WHERE scope_id = X` | `RiskScope WHERE scope_id = X` |
| Risk appetite per scope | Niet mogelijk | `RiskScope.risk_appetite_threshold` per scope |
| Acceptatie | Per risk (globaal) | Per RiskScope (scope-gebonden) |
| Control-risk koppeling | Scope-onafhankelijk | Scope-correct via `ControlRiskScopeLink` |

---

## Migratie-checklist

- [ ] `AcceptanceStatus` enum toegevoegd
- [ ] `RiskScope` model in `core_models.py`
- [ ] `ControlRiskScopeLink` model in `core_models.py`
- [ ] `DecisionRiskScopeLink` model in `core_models.py`
- [ ] Relationships toegevoegd aan Risk, Scope, Control, Decision
- [ ] Alembic migratie 013: create tables + indexes + constraints
- [ ] Alembic migratie 013: backfill RiskScope van Risk.scope_id
- [ ] Alembic migratie 013: backfill via ControlRiskLink
- [ ] Alembic migratie 013: fallback "Niet-toegewezen" scope
- [ ] Alembic migratie 013: backfill ControlRiskScopeLink
- [ ] Alembic migratie 013: backfill DecisionRiskScopeLink
- [ ] Verificatie: geen orphan risks
- [ ] API: `/risk-scopes/` endpoints
- [ ] API: `/scopes/{id}/risks` endpoint
- [ ] API: `/risks/{id}/scopes` endpoint
- [ ] Frontend: risk detail toont scopes
- [ ] Frontend: scope detail toont risico's
- [ ] InControlAssessment queries aangepast
- [ ] Domain agents bijgewerkt (risk, scope, measure, improvement)
- [ ] Tests: tenant isolation + scope filtering
- [ ] Tests: backfill correctheid
- [ ] Tests: CRUD RiskScope
- [ ] Tests: In-Control met RiskScope

---

## Volgorde van uitvoering

1. **Models** (core_models.py) — enums + 3 nieuwe tabellen + relationships
2. **Alembic migratie** — DDL + backfill (alles in 1 migratie, maar met duidelijke stappen)
3. **API endpoints** — risk_scopes.py + aanpassingen risks.py/decisions.py
4. **Frontend** — state + pages
5. **InControl** — query-aanpassingen
6. **Agents** — system prompts + tools
7. **Tests** — unit + integration
8. **Deprecatie** — soft → hard (apart release-traject)
