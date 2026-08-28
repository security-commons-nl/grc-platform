# RFC 0001 — Extensible Attributes (custom fields per tenant)

> **Status:** V1 geïmplementeerd · **Datum:** 2026-05-12 (status bijgewerkt 2026-05-13)
> **Type:** Architectuur · **Module-impact:** M0 (platform), M2 (GRC-engine), M5 (risicokwantificatie)
> **Beslissing nodig vóór:** commitment aan klanten dat tenant-specifieke velden zonder code-wijziging mogelijk zijn
>
> **Implementatie-stand (2026-05-13)**
> - Backend: `custom_attributes` JSONB-kolom op `ims_risks`, `ims_controls`, `ims_assessments`, `ims_findings` (Alembic 016). `ims_custom_field_definitions`-tabel met RLS, GIN-index en CHECK op snake_case `field_name`. JSON-Schema-validatie via compound-schema (`additionalProperties=false`) + reserved-namespace-check tegen kernkolommen.
> - API: CRUD `/api/v1/custom-fields/` (admin-only). POST/PATCH op risk/control/assessment/finding valideren payload tegen tenant-definities.
> - UI: form-builder `/admin/velden` met 4 veldtypes (string / number / boolean / enum). Herbruikbare `CustomFieldsForm`-component rendert dynamische inputs in create-forms voor risk, control en assessment.
> - Tests: backend pytest in `tests/test_custom_fields.py`; 7 vitest-tests op `CustomFieldsForm`; e2e via `admin-velden`, `beheer-risicos-ui`, `beheer-controls-extensies`, `beheer-assessments-extensies` met directe DB-verificatie van `custom_attributes->>'field_name'`.

---

## 1. Probleem

Het platform werkt vandaag onder het architectuurprincipe **"Database leading, schema vast"** (zie [`docs/development.md`](../development.md)). Velden op `ims_risks`, `ims_controls`, `ims_assessments` en `ims_findings` liggen vast in code en in Alembic-migraties. Nieuwe velden vereisen een release.

Klanten — concreet: de eerste pilot-gemeente — vragen om **tenant-specifieke velden zonder code-wijziging**. Voorbeelden uit de praktijk:

- "Wij willen een veld 'kadernota-programma' op risico's, om aan te sluiten op de P&C-cyclus"
- "Wij gebruiken een eigen impactschaal '1-7' in plaats van '1-5'"
- "Wij willen een dropdown 'cluster' op controls voor onze interne rapportages"

Deze vragen leiden vandaag tot één van twee uitkomsten — geen van beide gewenst:

1. **Maatwerk per tenant** — patch op `core_models.py`, nieuwe Alembic-migratie, deployment-coördinatie. Onhoudbaar bij >1 tenant met andere wensen.
2. **Niet beantwoorden** — klant gebruikt vrije tekstvelden (`description`) als opslag, met verlies van structuur, validatie en filterbaarheid.

Dit RFC stelt een **derde route** voor: extensible attributes binnen een audit-veilig kader.

---

## 2. Niet-doelen

Dit RFC behandelt **niet**:

- Configureerbare workflows (status-transities). Audit-trail vereist dat statuslogica code-gedefinieerd blijft. Afzonderlijk RFC zou nodig zijn.
- Volledige form-builder UI. Dit RFC dekt schema-flexibiliteit; UI-rendering volgt in een vervolg-issue.
- Cross-tenant rapportage met custom velden. Custom velden zijn per-tenant; standaard-rapportages over meerdere tenants (M6 regio-dashboard) blijven op vaste kernvelden.
- EU AI Act / audit-log uitbreidingen. Standaard `AIAuditLog` registreert alle wijzigingen aan custom field-definities én aan custom-waarden zonder extra werk.

---

## 3. Voorstel — Hybride model

### 3.1 Wat blijft vast

Kernvelden op alle entiteiten blijven exact zoals nu:

- Identiteit: `id`, `tenant_id`, `created_at`, `updated_at`
- Workflow-velden: `status`, `risk_level`, eventuele `*_state` velden
- Koppelingen (FK's) naar andere kerntabellen
- Audit-relevante velden: `owner_user_id`, `treatment_decision_id`, etc.
- Velden waarop M5/M6/M4 rekenen: `likelihood`, `impact`, `financial_impact_*`, `impact_distribution`, `eu_ai_act_risk`, etc.

Standaard-rapportages, RLS-policies, Monte Carlo-simulatie en cross-framework mapping blijven gegarandeerd werken.

### 3.2 Wat erbij komt

**(a) JSONB-kolom op vier kern-entiteiten**

```python
# in IMSRisk, IMSControl, IMSAssessment, IMSFinding
custom_attributes: Mapped[dict] = mapped_column(
    JSONB, nullable=False, server_default=text("'{}'::jsonb")
)
```

**(b) Nieuwe tabel `ims_custom_field_definitions`**

Per tenant + entiteit een set veld-definities met JSON-Schema-validatie.

```python
class IMSCustomFieldDefinition(Base):
    __tablename__ = "ims_custom_field_definitions"

    id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # Enum: 'risk' | 'control' | 'assessment' | 'finding'

    field_name: Mapped[str] = mapped_column(String(64), nullable=False)
    # Pattern: ^[a-z][a-z0-9_]{0,63}$ — geen reserved namespace
    # Reserved: alles wat al in core-schema bestaat; valideer in service-laag.

    display_label: Mapped[str] = mapped_column(Text, nullable=False)
    help_text:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    json_schema: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Bijvoorbeeld: {"type": "string", "maxLength": 64, "enum": ["A","B","C"]}
    # Of: {"type": "number", "minimum": 0, "maximum": 100}

    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "entity_type", "field_name", name="uq_custom_field_per_tenant_entity"),
        Index("ix_custom_field_definitions_tenant_entity", "tenant_id", "entity_type"),
    )
```

**(c) GIN-index op `custom_attributes` per entiteit**

```sql
CREATE INDEX ix_ims_risks_custom_attributes_gin
  ON ims_risks USING GIN (custom_attributes jsonb_path_ops);
```

Hetzelfde voor `ims_controls`, `ims_assessments`, `ims_findings`. Maakt filteren op `custom_attributes @> '{"cluster": "X"}'` snel.

**(d) RLS-policy op `ims_custom_field_definitions`**

Standaard tenant-isolatie patroon (zoals andere `ims_*` tabellen):

```sql
ALTER TABLE ims_custom_field_definitions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ims_custom_field_definitions
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

### 3.3 Validator-middleware

Bij elke POST/PATCH op een entiteit met `custom_attributes`:

1. Laad de actieve `ims_custom_field_definitions` voor `(tenant_id, entity_type)`.
2. Combineer alle `json_schema`-fragmenten tot één compound schema:
   ```python
   schema = {
       "type": "object",
       "properties": {d.field_name: d.json_schema for d in defs},
       "required":   [d.field_name for d in defs if d.is_required],
       "additionalProperties": False,
   }
   ```
3. Valideer `custom_attributes` met `jsonschema.validate()`.
4. Bij fout: HTTP 422 met `{"detail": [{"loc": ["custom_attributes", field], "msg": ...}]}` zodat Pydantic-stijl error-handling consistent blijft.

Plaatsing: nieuwe service `app/services/custom_fields.py` met functie `validate_custom_attributes(db, tenant_id, entity_type, attributes)`. Endpoints roepen deze aan vóór `db.commit()`.

### 3.4 Reserved-namespace bewaking

Veld-definities kunnen geen veldnamen krijgen die al bestaan in het kernschema. Bij `POST /api/v1/custom-fields`:

```python
RESERVED_FIELDS_PER_ENTITY = {
    "risk":       {c.name for c in IMSRisk.__table__.columns},
    "control":    {c.name for c in IMSControl.__table__.columns},
    "assessment": {c.name for c in IMSAssessment.__table__.columns},
    "finding":    {c.name for c in IMSFinding.__table__.columns},
}

if field_name in RESERVED_FIELDS_PER_ENTITY[entity_type]:
    raise HTTPException(409, f"Veldnaam '{field_name}' conflicteert met kernveld")
```

### 3.5 API-impact

**Bestaande endpoints (bv. `POST /api/v1/risks`):**

```json
{
  "title": "...",
  "scope_id": "...",
  "likelihood": 3,
  "impact": 4,
  "custom_attributes": {
    "kadernota_programma": "Programma 7 — Veiligheid",
    "cluster": "Bedrijfsvoering"
  }
}
```

Backward-compatible: clients die `custom_attributes` weglaten zien geen verandering. Default `{}` voldoet aan een leeg schema (geen required custom fields).

**Nieuwe endpoints:**

| Methode | Pad | Doel |
|---------|-----|------|
| `GET`    | `/api/v1/custom-fields?entity_type=risk` | Alle veld-definities voor tenant |
| `POST`   | `/api/v1/custom-fields` | Nieuw veld definiëren (admin-only) |
| `PATCH`  | `/api/v1/custom-fields/{id}` | Veld aanpassen (label, help, schema, required) |
| `DELETE` | `/api/v1/custom-fields/{id}` | Veld verwijderen — waarden blijven in JSONB, alleen definitie weg |

RBAC: alleen `admin` van de tenant mag definities CRUD-en. Alle rollen lezen en schrijven custom-waarden volgens normale entity-permissions.

### 3.6 UI-impact (out of scope voor dit RFC, hier alleen schets)

- Tenant-admin krijgt route `/beheer/admin/velden` met form-builder per entity_type.
- Entity-pagina's (bv. risico-detail) tonen een "Aanvullende velden"-sectie waar definities voor deze tenant worden gerenderd op basis van `json_schema` (string → text, number → numeric, enum → dropdown, boolean → checkbox).
- Lijst-views (`/beheer/risicos`) krijgen optionele kolomkiezer voor custom-velden (filter/sort via JSONB-query).

### 3.7 Verwijdering / migratie van definities

Bij wijzigen van een veld-`json_schema` (bv. `enum` aanpassen) **geen retroactieve validatie**: bestaande waarden blijven staan. Tenant-admin krijgt waarschuwing.

Bij verwijderen van een definitie: waarden in JSONB blijven (audit-traceerbaarheid), maar verschijnen niet meer in UI of validator. Een afzonderlijke `POST /api/v1/custom-fields/{id}/purge` purgt waarden (admin-only, met expliciete confirmatie).

---

## 4. Alternatieven (afgewezen)

| Alternatief | Waarom afgewezen |
|-------------|------------------|
| **EAV (entity-attribute-value)** met aparte `custom_values`-tabel met (`entity_id`, `field_id`, `value_text`, `value_number`, …) | Verliest type-safety in SQL, maakt joins onleesbaar, RLS-policies vermenigvuldigen. Klassiek anti-pattern in audit-systemen. |
| **Volledige schema-flexibiliteit** (per tenant aparte tabellen of dynamic ALTER TABLE) | Onhoudbaar bij N tenants, breekt migratie-discipline, ondergraaft "Database leading"-principe volledig. |
| **UI-only form-builder** zonder schema-extensie | Lost niet op dat klanten *data* willen opslaan die nu nergens past — werkt alleen voor verbergen/herordenen van kernvelden. |
| **Configurable workflows in dezelfde tabel** | Verworpen voor dit RFC. Status-transities en audit-log integriteit vereisen code-discipline. Apart RFC zou nodig zijn. |

---

## 5. Risico's en mitigaties

| Risico | Mitigatie |
|--------|-----------|
| Custom velden lekken in cross-tenant rapportage | Standaard-rapportages renderen alléén kernvelden. Cross-tenant features (M6) krijgen expliciete allow-list voor custom velden. |
| Tenant-admin breekt validatie door schema-wijziging | Wijzigingen worden niet retroactief afgedwongen. Bij volgende write valideert nieuw schema; oude data blijft inspecteerbaar via audit-log. |
| Performance-degradatie door GIN-indices | Acceptabel: JSONB GIN-indices zijn in PostgreSQL 16 efficiënt voor `@>`-containment queries die we hier verwachten. Benchmarken bij >100k risico's. |
| Klanten verwarren custom velden met workflow-customization | Documentatie expliciet: "custom velden ≠ custom workflow". UI-tooltips in form-builder. |
| AVG: PII in custom velden | Tenant-admin verantwoordelijk; documentatie verwijst naar AVG-richtsnoer. Geen aanvullende encryptie nodig (RLS dekt confidentialiteit). |

---

## 6. Acceptatie-criteria

Dit RFC is "geïmplementeerd" wanneer:

- [ ] Alembic-migratie voegt `custom_attributes JSONB` + GIN-index toe aan `ims_risks`, `ims_controls`, `ims_assessments`, `ims_findings`
- [ ] Alembic-migratie maakt tabel `ims_custom_field_definitions` aan met RLS-policy
- [ ] Service `app/services/custom_fields.py` valideert custom_attributes tegen actieve definities; reserved-namespace check werkt
- [ ] CRUD-endpoints onder `/api/v1/custom-fields` werken; admin-only via `require_role()` op `admin`
- [ ] Bestaande tests blijven groen; nieuwe tests dekken: (1) valide definitie + valide waarde = 200, (2) verplicht veld missend = 422, (3) reserved naam = 409, (4) cross-tenant RLS-isolatie van definities
- [ ] `docs/extensible-attributes.md` geschreven (gebruiks-handleiding voor tenant-admins en clients)

UI (form-builder, custom field-rendering) volgt in een vervolg-issue na dit RFC-werk.

---

## 7. Open vragen voor discussie

1. **Reserved naming**: kiezen we een prefix-conventie voor custom velden (bv. `x_`-prefix) om kerncollisie a priori uit te sluiten, of houden we de runtime reserved-check? Voor- en nadeel: prefix maakt veldnamen lelijker maar voorkomt subtiele fouten bij toekomstig hernoemen van core-velden.
2. **Versionering van json_schema**: bij schema-wijziging geen retroactieve validatie. Moet er een `schema_version`-veld bij om te zien onder welke schema-versie een waarde is geschreven? (Argument vóór: audit-trail; argument tegen: extra complexiteit voor weinig praktisch nut.)
3. **Maximum aantal custom velden per tenant/entity**: hardlimit of soft? Praktisch is iets als 50 redelijk; UI wordt onbruikbaar boven dat aantal.
4. **Indexering op specifieke custom velden**: GIN op hele JSONB is generiek. Voor frequent gefilterde velden kan een expression-index sneller zijn — maar dan moet tenant-admin dat triggeren. Voorlopig parkeren tot we performance-issues zien.
5. **Export/import van veld-definities** tussen tenants (template-deling): nuttig voor regio-adoptie maar buiten scope dit RFC.

---

## 8. Beslismomenten

- **Goedkeuring van dit RFC** door projectteam vóór implementatie-werk start
- **Per-tenant beslissing** door klant zelf: welke custom velden activeren ze (geen platform-keuze)
- **Acceptatie van trade-off** "configureerbaar binnen audit-veilig kader" i.p.v. "alles configureerbaar" — expliciet communiceren in `README.md` onder positionering

---

## 9. Referenties

- Beslispunt 2 in intern document `grc-platform-beslispunten.md` — voorkeur voor Optie B (hybride)
- `docs/development.md` — "Database leading, schema vast" als oorspronkelijk principe
- `docs/modules.md` — M0 Platform architectuurprincipes
- PostgreSQL 16 docs — JSONB en GIN-indices
- IETF RFC 7159 (JSON), JSON Schema draft 2020-12

---

## Changelog

| Datum | Wijziging | Door |
|-------|-----------|------|
| 2026-05-12 | Initieel concept | open-source projectteam |
