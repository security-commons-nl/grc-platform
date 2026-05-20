# RFC 0002 — Organizational Units (sub-tenant hiërarchie)

> **Status:** V1 geïmplementeerd · **Auteur:** open-source projectteam · **Datum:** 2026-05-12 (status bijgewerkt 2026-05-13)
> **Type:** Schema-uitbreiding · **Module-impact:** M5 (risicokwantificatie), M2 (GRC-engine), raakt aggregatie M0
> **Beslissing nodig vóór:** commitment aan klanten dat decentrale risicosturing op team/cluster-niveau mogelijk is
>
> **Implementatie-stand (2026-05-13)**
> - Backend: `ims_organizational_units` met parent-self-FK (Alembic 017), `MAX_DEPTH=6`, CHECK `ck_org_unit_no_self_parent`, server-side cycle-detection via recursive CTE. Nullable FK-kolom `organizational_unit_id` op `ims_risks`, `ims_controls`, `ims_assessments` en `ims_grc_scores`.
> - API: CRUD `/api/v1/organizational-units/` + `/tree` + `/{id}/descendants`. POST/PATCH op risk/control/assessment valideren cross-tenant koppelingen (HTTP 422). GET op risico/control/assessment ondersteunt `?organizational_unit_id=&include_descendants=` met recursive descendants-walk.
> - UI: boom-editor `/admin/organisatie` met `OrgUnitSelect`-dropdown gedeeld over create-forms en filter-kaarten op `/beheer/risicos`, `/beheer/controls` en `/beheer/assessments`.
> - Tests: 12 pytest-tests in `tests/test_organizational_units.py` (CRUD, cycle-detection, depth-limit, cross-tenant-reject, filter incl. descendants op risk + control + assessment); 4 vitest-tests op `OrgUnitSelect`; e2e in `admin-organisatie`, `rfc-extensions`, `beheer-risicos-ui`, `beheer-controls-extensies`, `beheer-assessments-extensies` met directe DB-verificatie van `organizational_unit_id`-FK.

---

## 1. Probleem

Het platform kent vandaag exact één hiërarchische laag: `tenant`. Een gemeente of organisatie *is* een tenant, en al haar gebruikers, risico's, controls, assessments hangen direct onder die tenant.

De eerste pilot-gemeente (via de concernadviseur risicomanagement) vraagt expliciet om decentrale risicosturing **in de lijn**: clusters, teams en afdelingen moeten zelfstandig hun risico- en controlportefeuille kunnen beheren én aggregaten op cluster- of organisatie-niveau kunnen genereren voor MT-rapportage.

Concrete eisen uit de interne werkdocumenten van de pilot-gemeente:

- **N1.4** Geaggregeerde overzichten op team-, cluster- en organisatie-niveau
- **N1.5** Risicomanagement primair in de lijn (RBAC al passend; entiteit ontbreekt)
- **N1.3** (indirect) P&C-cyclus-koppeling — wordt pragmatisch opgelost zonder schema-uitbreiding (zie sectie 3.5)

Vandaag kun je hier alleen omheen werken via `ims_scopes`, maar scopes zijn flat (geen ouder/kind) en bedoeld voor scope-van-een-assessment, niet voor organisatie-structuur.

---

## 2. Niet-doelen

Dit RFC behandelt **niet**:

- **Matrix-organisaties** (één team rapporteert aan meerdere clusters). Eerste iteratie kiest bewust voor strikte boom (één parent per unit). Bij vraag escaleren naar M2M in vervolg-RFC.
- **Planning-en-control-cyclus als first-class entiteit** (`ims_planning_cycles`, `ims_business_objectives`). Wordt pragmatisch opgelost via scope-conventie (sectie 3.5). Promotie naar eerste-klas-entiteit pas bij tweede klantvraag.
- **Cross-tenant unit-sharing** (regio-dashboard, M6). Volledig binnen één tenant.
- **Per-unit RBAC** ("alleen Cluster X mag bij Cluster X-risico's"). Huidig RBAC blijft op tenant-niveau; unit is filter, geen permissie-grens. Apart RFC zou nodig zijn.
- **Hernoeming van `cyclus_id` op `ims_risks`** — bestaat al voor P&C-cyclus-jaar; valt buiten dit RFC.

---

## 3. Voorstel

### 3.1 Nieuwe tabel `ims_organizational_units`

```python
class IMSOrganizationalUnit(Base):
    __tablename__ = "ims_organizational_units"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_organizational_units.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    # Optionele unieke code per tenant (bv. "BV-FIN" voor cluster-bedrijfsvoering/financiën)

    unit_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # 'directie' | 'cluster' | 'afdeling' | 'team' | 'overig'
    # Vrije lijst; geen DB-enum want gemeente-jargon verschilt.

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_org_unit_code_per_tenant"),
        Index("ix_org_units_tenant_parent", "tenant_id", "parent_id"),
        CheckConstraint("id <> parent_id", name="ck_org_unit_no_self_parent"),
    )
```

### 3.2 FK-velden op kern-entiteiten

Op `ims_risks`, `ims_controls`, `ims_assessments` (en optioneel `ims_findings`):

```python
organizational_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID(as_uuid=True), ForeignKey("ims_organizational_units.id"), nullable=True
)
```

**Nullable bewust:** bestaande rows blijven `NULL`, betekenen "tenant-niveau, niet aan een specifieke unit gehangen". Backward-compatible. Nieuwe risico's mogen ook tenant-niveau blijven als unit-structuur (nog) niet relevant is.

### 3.3 RLS en cross-tenant validatie

Standaard tenant-isolatie:

```sql
ALTER TABLE ims_organizational_units ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ims_organizational_units
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Service-laag validatie** (kritisch: voorkomt FK-lekken via gemanipuleerde IDs):
- Bij elke POST/PATCH op risk/control/assessment met `organizational_unit_id`: verifieer dat de unit binnen dezelfde tenant valt (RLS dekt het, maar expliciete check geeft 422 i.p.v. 404).
- Bij `parent_id` op een nieuwe/aangepaste unit: idem.

### 3.4 Aggregatie via recursive CTE

Boom-traversal voor "alle risico's onder cluster X (inclusief sub-units)":

```sql
WITH RECURSIVE unit_tree AS (
    SELECT id FROM ims_organizational_units WHERE id = :unit_id
    UNION ALL
    SELECT u.id
      FROM ims_organizational_units u
      JOIN unit_tree t ON u.parent_id = t.id
)
SELECT * FROM ims_risks WHERE organizational_unit_id IN (SELECT id FROM unit_tree);
```

Geïmplementeerd als utility-functie `services/org_units.py::descendants(db, tenant_id, unit_id)` zodat endpoints schoon blijven.

**Diepte-limiet:** controleer in service-laag dat boomdiepte ≤ 6 niveaus bij INSERT/UPDATE (`parent_id`). Voorkomt run-aways; gemeente-organogrammen zijn zelden dieper. Hardlimiet, geen soft warning.

### 3.5 P&C-cyclus pragmatisch via `ims_scopes`

N1.3 (P&C / doelen) blijft buiten dit RFC. **Conventie** in plaats van schema:

- Bestaande `ims_scopes` krijgt documentatie-conventie: `scope_type='pc_object'` voor P&C-objecten (kadernota, programma, doelstelling)
- Risico's worden via `scope_id` aan een P&C-object gekoppeld (kan al)
- Vanaf de tweede gemeente met dezelfde vraag → vervolg-RFC voor promotie naar `ims_planning_cycles` + `ims_business_objectives`

Reden: te vroeg modelleren op gemeente-jargon ("kadernota", "programmabegroting") maakt platform gemeente-specifiek. Liever wachten op tweede vraag om abstractie-niveau goed te kiezen.

### 3.6 Aggregatie-views

`ims_grc_scores` (en `ims_setup_scores`) krijgen optioneel `organizational_unit_id`:

```python
organizational_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID(as_uuid=True), ForeignKey("ims_organizational_units.id"), nullable=True
)
```

`NULL` betekent tenant-totaal (huidige gedrag). Scoring-service berekent per (tenant, unit) tuple. Filter in dashboard-endpoint.

Indexering: bestaande `(tenant_id, *)` indices uitbreiden naar `(tenant_id, organizational_unit_id, *)` waar relevant.

### 3.7 API

| Methode | Pad | Doel |
|---------|-----|------|
| `GET`    | `/api/v1/organizational-units` | Vlakke lijst voor tenant |
| `GET`    | `/api/v1/organizational-units?tree=true` | Geneste boom als JSON |
| `GET`    | `/api/v1/organizational-units/{id}/descendants` | IDs van alle sub-units (utility voor filtering) |
| `POST`   | `/api/v1/organizational-units` | Nieuwe unit aanmaken (admin) |
| `PATCH`  | `/api/v1/organizational-units/{id}` | Aanpassen (admin) |
| `DELETE` | `/api/v1/organizational-units/{id}` | Verwijderen (admin). 409 als unit referenties heeft. |

Bestaande endpoints krijgen optionele query-parameter:

- `GET /api/v1/risks?organizational_unit_id={id}&include_descendants=true`
- Idem voor controls, assessments

RBAC:
- CRUD op units: `admin` van tenant
- Filteren in lijst-endpoints: alle rollen (geen permissie-grens)

### 3.8 UI-impact (out of scope; schets)

- Tenant-admin krijgt route `/beheer/admin/organisatie` met boom-editor
- Risk/control/assessment-forms krijgen dropdown "Organisatie-eenheid" (optioneel)
- Dashboard `/beheer` krijgt filter "Toon scope" met unit-selector (default: hele tenant)
- `ims_grc_scores`-12-cellenmatrix kan per unit getoond worden

---

## 4. Alternatieven (afgewezen of geparkeerd)

| Alternatief | Status |
|-------------|--------|
| **M2M parent-relatie** (matrix-organisatie) | Geparkeerd. Eerste klant heeft strikte boom; bij matrix-vraag escaleren via vervolg-RFC. Schema-impact in beide richtingen niet-trivial — eerst echte vraag afwachten. |
| **Materialized path** (`/cluster/team`) i.p.v. parent_id | Afgewezen. Sneller voor "alle descendants" maar duurder bij verplaatsen. Recursive CTE is in PostgreSQL 16 efficiënt genoeg. |
| **Nested set model** (left/right) | Afgewezen. Schrijfacties (insert/move) zijn O(N) — boom-mutaties zijn frequent in gemeente-context (reorganisaties). |
| **Tenant-tree** (tenant zelf hiërarchisch) | Afgewezen. Breekt multi-tenant-fundament; tenants moeten gescheiden blijven voor RLS-eenvoud. |
| **`ims_scopes` uitbreiden met parent_id** | Afgewezen. Scopes hebben semantiek "wat valt onder deze assessment"; organisatie-units hebben semantiek "wie is verantwoordelijk". Doelen vermengen geeft verwarring. |
| **First-class P&C-entiteiten nu meenemen** | Geparkeerd. Zie sectie 3.5 — wachten op tweede klantvraag. |

---

## 5. Risico's en mitigaties

| Risico | Mitigatie |
|--------|-----------|
| Cyclische `parent_id`-keten | DB-niveau check: `id <> parent_id`. Service-laag check: recursieve verificatie bij PATCH dat nieuwe parent geen descendant is. |
| Te diepe boom maakt queries traag | Diepte-limiet 6 in service-laag (zie 3.4). Toelichting in UI. |
| Verkeerde unit-koppeling bij grote re-organisaties | Audit-log standaard registreert wijzigingen via `AIAuditLog`-patroon. Geen bulk-rewrite-endpoint in deze iteratie (admin doet handmatig of via API-script). |
| Cross-tenant FK via gemanipuleerde unit_id | RLS dekt het bij read; service-laag valideert bij write (sectie 3.3). Beide nodig (defense-in-depth). |
| Nullable FK maskeert "vergeten unit" | Acceptabel. Tenant kiest zelf of unit-koppeling verplicht is via UI-validatie of via custom field (RFC 0001). |
| Performance bij `include_descendants=true` op grote boom | Recursive CTE met `LIMIT` op resultaat-pagina. Diepte-limiet 6 begrenst worst-case. Benchmarken bij >10 units en >10k risico's. |

---

## 6. Acceptatie-criteria

Dit RFC is "geïmplementeerd" wanneer:

- [ ] Alembic-migratie maakt `ims_organizational_units` aan met indices, constraints, RLS-policy
- [ ] Alembic-migratie voegt `organizational_unit_id` (nullable FK) toe aan `ims_risks`, `ims_controls`, `ims_assessments`, `ims_grc_scores`
- [ ] Service `services/org_units.py` met `descendants()` en `validate_unit_in_tenant()` utility-functies
- [ ] Endpoints onder `/api/v1/organizational-units` operationeel met admin-only CRUD
- [ ] Bestaande endpoints accepteren `organizational_unit_id` en `include_descendants=true` query
- [ ] Cycle-detection getest: PATCH die unit z'n eigen descendant als parent zou geven faalt met 422
- [ ] Diepte-limiet getest: 7e niveau aanmaken faalt met 422
- [ ] RLS-test: unit van tenant A is onbereikbaar voor tenant B (read én write)
- [ ] `docs/organizational-units.md` geschreven (gebruikshandleiding tenant-admin + API-clients)
- [ ] `docs/modules.md` M5-sectie bijgewerkt: "Organisatie-units" verschuift van "Bewust nog niet in deze iteratie" naar gebouwd

UI (boom-editor, dropdowns, dashboard-filter) volgt in vervolg-issues.

---

## 7. Open vragen voor discussie

1. **Verplichte `unit_type`-waarde**: laten we het volledig vrij of geven we een suggestie-set (`directie | cluster | afdeling | team`)? Vrij is flexibeler maar leidt tot inconsistente data tussen gemeenten. Voorstel: vrije string met UI-suggesties uit een config-lijst per tenant.
2. **`code`-uniciteit**: alleen per tenant uniek (huidig voorstel) of globaal? Per tenant is voldoende voor identificatie, globaal hindert nuttige use cases.
3. **Verwijderen vs. archiveren**: huidige DELETE faalt bij referenties (409). Moeten we soft-delete (`is_active=false`) als alternatief aanbieden? Voorstel: ja, en DELETE alleen toestaan bij `is_active=false` én geen referenties.
4. **`organizational_unit_id` op `ims_findings`**: voegt waarde toe voor MT-rapportage per unit, maar bevindingen zijn altijd afgeleid van assessment. Genoeg om assessment-koppeling te volgen? Voorstel: niet toevoegen aan `ims_findings`; afleiden via assessment.
5. **Eigenaar-rol per unit** (lijnmanager X is eigenaar van Cluster Y): nodig voor escalatie-flows. Buiten dit RFC. Volgende RFC `0003-unit-ownership.md`.

---

## 8. Beslismomenten

- **Goedkeuring van dit RFC** door projectteam vóór implementatie
- **Per-tenant beslissing**: gebruikt deze klant unit-structuur of blijft alles tenant-niveau? UI moet beide werkpaden aankunnen.
- **Acceptatie van pragmatische P&C-route** (sectie 3.5): expliciet documenteren in [`../risico-kwantificatie.md`](../risico-kwantificatie.md) zodat klanten weten dat P&C-objecten via scopes lopen tot er bredere vraag is.

---

## 9. Referenties

- Beslispunt 1 in intern document `grc-platform-beslispunten.md` — voorkeur voor Optie B (org-units bouwen, P&C-via-scope voorlopig)
- `docs/modules.md` sectie M5 — "Bewust niet in deze iteratie": organisatie-units, P&C
- `ROADMAP.md` sectie "M5 Risicokwantificatie — scope-beperkt" — uitbreidings-lijst
- PostgreSQL 16 docs — recursive CTE, RLS

---

## Changelog

| Datum | Wijziging | Door |
|-------|-----------|------|
| 2026-05-12 | Initieel concept | open-source projectteam |
