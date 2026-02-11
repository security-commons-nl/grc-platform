# Plan: Vereenvoudigen Scope-Entiteiten (Route A+)

> **Besluit**: De Scope-tabel blijft het fundament (27 FK-referenties intact), maar we herstructureren de hiërarchie en ontkoppelen Assets/Suppliers naar een M2M-pool.

---

## 1. Probleemstelling

| Probleem | Impact |
|----------|--------|
| `ScopeType.ORGANIZATION` dupliceert `Tenant` | Verwarrend voor gebruikers |
| `ScopeType.VIRTUAL` wordt nergens gebruikt | Dode code |
| `ScopeType.CLUSTER` is alleen nodig voor grote orgs | Onnodige complexiteit voor MKB |
| Asset is een **kind** van Process via `parent_id` (1-op-N) | Één MS365-licentie moet 20x aangemaakt worden |
| 7 ScopeTypes in één vlak model | Te flexibel, geen structuur |

## 2. Doelarchitectuur

```
Tenant (= de Organisatie, al bestaand)
  └── [Cluster]          ← optioneel, achter tenant-setting
       └── Department    ← de eigenaar/afdeling (verplicht tussenniveau)
            └── Process  ← wat de afdeling doet (1-op-N strict)

Asset-pool     ←→ Process (N-op-N via ScopeLink)
Supplier-pool  ←→ Process/Asset (N-op-N via ScopeLink)
```

**Strikte bovenkant** (parent_id, 1-op-N): `[Cluster] → Department → Process`
- RBAC vloeit hiërarchisch door
- Governance-status op elk niveau

**Flexibele onderkant** (ScopeLink, N-op-N): `Process ↔ Asset`, `Process ↔ Supplier`
- Geen dubbele invoer van assets
- Eén asset kan meerdere processen bedienen

---

## 3. Wijzigingen per laag

### 3.1 Backend: Enum opschonen

**Bestand**: `backend/app/models/core_models.py` regel 59-66

```python
# VOOR:
class ScopeType(str, Enum):
    ORGANIZATION = "Organization"
    CLUSTER = "Cluster"
    DEPARTMENT = "Department"
    PROCESS = "Process"
    ASSET = "Asset"
    SUPPLIER = "Supplier"
    VIRTUAL = "Virtual"

# NA:
class ScopeType(str, Enum):
    CLUSTER = "Cluster"        # Optioneel — alleen als tenant.enable_clusters=True
    DEPARTMENT = "Department"  # Afdeling — de eigenaar
    PROCESS = "Process"        # Wat de afdeling doet
    ASSET = "Asset"            # Middel — leeft in pool, M2M met Process
    SUPPLIER = "Supplier"      # Leverancier — leeft in pool, M2M met Process/Asset
```

**Geschrapt**: `ORGANIZATION` (= Tenant), `VIRTUAL` (nooit gebruikt)

### 3.2 Backend: Nieuwe koppeltabel `ScopeLink`

**Nieuw bestand/toevoeging in**: `backend/app/models/core_models.py`

```python
class ScopeLinkType(str, Enum):
    """Type relatie tussen pool-scopes en hiërarchische scopes"""
    USES = "uses"              # Process gebruikt Asset
    SUPPLIED_BY = "supplied_by"  # Process/Asset wordt geleverd door Supplier
    SUPPORTS = "supports"      # Asset ondersteunt Process (inverse view)

class ScopeLink(SQLModel, table=True):
    """
    Many-to-Many koppeling tussen hiërarchische scopes (Process) en
    pool-scopes (Asset, Supplier). Vervangt parent_id voor Assets/Suppliers.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    source_scope_id: int = Field(foreign_key="scope.id", index=True)  # Bijv. Process
    target_scope_id: int = Field(foreign_key="scope.id", index=True)  # Bijv. Asset

    link_type: ScopeLinkType = ScopeLinkType.USES
    description: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Unique constraint: geen dubbele links
    __table_args__ = (
        UniqueConstraint("source_scope_id", "target_scope_id", "link_type"),
    )
```

> **Opmerking**: `ScopeDependency` (bestaand) blijft bestaan voor infrastructure-/service-dependencies tussen scopes. `ScopeLink` is specifiek voor de M2M "gebruikt"/"geleverd door"-relatie.

### 3.3 Backend: Scope model aanpassen

**Bestand**: `backend/app/models/core_models.py` — `class Scope`

Wijzigingen:
1. **parent_id gedrag wijzigen**: `parent_id` is alleen geldig voor CLUSTER, DEPARTMENT, PROCESS. Voor ASSET en SUPPLIER wordt `parent_id` altijd `NULL` (afgedwongen in business logic).

2. **Nieuwe relationships toevoegen**:
```python
# Op het Scope model:
linked_targets: List["Scope"] = Relationship(
    link_model=ScopeLink,
    sa_relationship_kwargs={
        "primaryjoin": "Scope.id==ScopeLink.source_scope_id",
        "secondaryjoin": "Scope.id==ScopeLink.target_scope_id"
    }
)
linked_sources: List["Scope"] = Relationship(
    link_model=ScopeLink,
    sa_relationship_kwargs={
        "primaryjoin": "Scope.id==ScopeLink.target_scope_id",
        "secondaryjoin": "Scope.id==ScopeLink.source_scope_id"
    }
)
```

3. **Bestaande velden**: Alle conditionele velden (asset_type, vendor_contact_*, BIA ratings, etc.) blijven **ongewijzigd**. Geen JSONB. Typed fields behouden.

### 3.4 Backend: Tenant settings uitbreiden

**Bestand**: `backend/app/models/core_models.py` — `class Tenant`

```python
# Nieuw veld op Tenant:
enable_clusters: bool = False  # MKB=False, Gemeente=True
```

Of opnemen in het bestaande `settings: Optional[str]` JSON-veld als `{"enable_clusters": true}`.

### 3.5 Backend: Hiërarchie-validatie aanpassen

**Bestand**: `backend/app/api/v1/endpoints/scopes.py` regel 64-72

```python
# VOOR:
hierarchy = [ScopeType.ORGANIZATION, ScopeType.CLUSTER, ScopeType.DEPARTMENT,
             ScopeType.PROCESS, ScopeType.ASSET]

# NA:
hierarchy = [ScopeType.CLUSTER, ScopeType.DEPARTMENT, ScopeType.PROCESS]
# Asset en Supplier zijn NIET in de hiërarchie — ze leven in de pool

# Extra validatie:
if scope.type in [ScopeType.ASSET, ScopeType.SUPPLIER]:
    if scope.parent_id is not None:
        raise HTTPException(400, "Assets en Suppliers mogen geen parent hebben")

if scope.type == ScopeType.CLUSTER:
    tenant = await get_tenant(session, tenant_id)
    if not tenant.enable_clusters:
        raise HTTPException(400, "Clusters zijn niet ingeschakeld voor deze organisatie")
```

### 3.6 Backend: Nieuwe API-endpoints voor ScopeLink

**Bestand**: `backend/app/api/v1/endpoints/scopes.py` (uitbreiden)

| Endpoint | Methode | Doel |
|----------|---------|------|
| `POST /{process_id}/assets/{asset_id}` | POST | Koppel asset aan process |
| `DELETE /{process_id}/assets/{asset_id}` | DELETE | Ontkoppel asset van process |
| `GET /{process_id}/assets` | GET | Alle assets van een process |
| `GET /{asset_id}/processes` | GET | Alle processen die een asset gebruiken |
| `POST /{scope_id}/suppliers/{supplier_id}` | POST | Koppel supplier |
| `DELETE /{scope_id}/suppliers/{supplier_id}` | DELETE | Ontkoppel supplier |
| `GET /{scope_id}/suppliers` | GET | Alle suppliers van een scope |

### 3.7 Backend: RBAC query aanpassen

**Impact**: `UserScopeRole` query moet nu ook via `ScopeLink` zoeken.

```
"Geef alles waar gebruiker X recht op heeft voor Afdeling ICT":
1. Zoek scope_id = ICT (Department)
2. Zoek alle children via parent_id (= Processen onder ICT)
3. Zoek alle linked Assets/Suppliers via ScopeLink voor die Processen
→ Dat is de volledige scope van de gebruiker
```

### 3.8 Frontend: Scopes-pagina herstructureren

**Bestanden**:
- `frontend/ims/pages/scopes.py` — Hoofd scope-overzicht
- `frontend/ims/pages/assets.py` — Asset-pool pagina
- `frontend/ims/pages/suppliers.py` — Supplier-pool pagina
- `frontend/ims/state/scope.py` — State management

**Wijzigingen**:

1. **Scopes-pagina** (`/scopes`):
   - Verwijder type-filter opties "Organisatie" en "Virtueel"
   - Verberg "Cluster" als tenant.enable_clusters=False
   - Toon hiërarchische boomweergave: [Cluster →] Department → Process
   - Statistiek-kaarten: Afdelingen, Processen, Assets, Leveranciers (geen "Organisaties" meer)

2. **Assets-pagina** (`/assets`):
   - Toont de asset-pool (alle assets van de tenant, niet hiërarchisch)
   - Nieuwe kolom/badge: "Gebruikt door X processen"
   - Actie: "Koppel aan proces" → opent selectie-dialog
   - Asset-detail toont gekoppelde processen

3. **Suppliers-pagina** (`/suppliers`):
   - Toont supplier-pool
   - Nieuwe kolom: "Levert aan X processen/assets"
   - Actie: "Koppel aan proces/asset"

4. **Scope State** (`scope.py`):
   - Verwijder `organization_count` computed property
   - Voeg `link_asset_to_process()`, `unlink_asset_from_process()` handlers toe
   - Voeg `get_linked_assets(process_id)`, `get_linked_processes(asset_id)` toe
   - Pas `show_parent_field` logica aan: alleen tonen voor Cluster/Department/Process

5. **UI Modus toggle** (nieuw):
   - "Compact" (MKB): Toon alleen Afdeling → Proces als platte lijst. Assets/Suppliers als losse pools.
   - "Uitgebreid" (Gemeente): Toon volle boom met Clusters.
   - Gestuurd door `tenant.enable_clusters`

### 3.9 Scope-pagina: Create/Edit dialog aanpassen

**Wijzigingen in het formulier**:

| Veld | Nu | Straks |
|------|----|--------|
| Type dropdown | 7 opties | 4-5 opties (Cluster verborgen tenzij enabled) |
| Parent selectie | Altijd zichtbaar | Alleen voor Cluster/Department/Process |
| "Koppel aan processen" | Niet beschikbaar | Nieuw veld voor Asset/Supplier (multi-select) |

---

## 4. Data-migratie

### 4.1 Alembic migratie stappen

**Stap 1**: Nieuwe tabel aanmaken
```sql
CREATE TABLE scopelink (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenant(id),
    source_scope_id INTEGER NOT NULL REFERENCES scope(id),
    target_scope_id INTEGER NOT NULL REFERENCES scope(id),
    link_type VARCHAR NOT NULL DEFAULT 'uses',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_scope_id, target_scope_id, link_type)
);
```

**Stap 2**: Bestaande Asset parent_id relaties migreren naar ScopeLink
```sql
-- Alle Assets die nu een Process als parent hebben → maak ScopeLink records
INSERT INTO scopelink (tenant_id, source_scope_id, target_scope_id, link_type)
SELECT s.tenant_id, s.parent_id, s.id, 'uses'
FROM scope s
WHERE s.type = 'Asset' AND s.parent_id IS NOT NULL;

-- Zet parent_id op NULL voor alle Assets
UPDATE scope SET parent_id = NULL WHERE type = 'Asset';
```

**Stap 3**: Idem voor Suppliers
```sql
INSERT INTO scopelink (tenant_id, source_scope_id, target_scope_id, link_type)
SELECT s.tenant_id, s.parent_id, s.id, 'supplied_by'
FROM scope s
WHERE s.type = 'Supplier' AND s.parent_id IS NOT NULL;

UPDATE scope SET parent_id = NULL WHERE type = 'Supplier';
```

**Stap 4**: Organization scopes migreren
```sql
-- Organization scopes: hun children moeten direct aan Tenant hangen
-- Stap 4a: Vind alle scopes met een Organization-parent
-- Stap 4b: Zet hun parent_id naar NULL (ze worden top-level onder Tenant)
UPDATE scope SET parent_id = NULL
WHERE parent_id IN (SELECT id FROM scope WHERE type = 'Organization');

-- Stap 4c: Verwijder of deactiveer Organization scopes
UPDATE scope SET is_active = FALSE WHERE type = 'Organization';
```

**Stap 5**: Virtual scopes opruimen
```sql
UPDATE scope SET is_active = FALSE WHERE type = 'Virtual';
```

**Stap 6**: Tenant veld toevoegen
```sql
ALTER TABLE tenant ADD COLUMN enable_clusters BOOLEAN DEFAULT FALSE;
```

### 4.2 Rollback strategie

Alle migratie-stappen zijn **reversibel**:
- ScopeLink records bevatten de originele parent-child relatie
- Organization scopes worden soft-deleted (is_active=False), niet hard-deleted
- Enum-waarden worden niet uit de DB verwijderd, alleen uit de Python code

---

## 5. Agent sync

**Agents die bijgewerkt moeten worden** na deze wijziging:

| Agent | Wijziging |
|-------|-----------|
| `scope_agent.py` | System prompt: nieuwe hiërarchie uitleggen, M2M asset-linking, geen Organization type meer |
| `risk_agent.py` | Tools: RBAC query via ScopeLink voor asset-risico's |
| `measure_agent.py` | Scope-contextduidelijkheid: maatregel op asset vs. op proces |
| `supplier_agent.py` | M2M relatie uitleggen, koppel-tooling |
| `admin_agent.py` | Tenant-instelling enable_clusters uitleggen |
| `assessment_agent.py` | Scope-selectie: assessments op pool-assets |

---

## 6. Volgorde van uitvoering

| Fase | Wat | Risico | Geschatte impact |
|------|-----|--------|------------------|
| **Fase 1** | Enum opschonen + ScopeLink model toevoegen + Alembic migratie | Laag (additief) | `core_models.py` |
| **Fase 2** | Hiërarchie-validatie aanpassen in API | Medium | `scopes.py` endpoint |
| **Fase 3** | Nieuwe ScopeLink API-endpoints | Laag (additief) | `scopes.py` endpoint |
| **Fase 4** | RBAC query uitbreiden met ScopeLink | Medium | Auth/permissions |
| **Fase 5** | Frontend: scopes-pagina + asset-pagina + supplier-pagina | Medium | 4 frontend bestanden |
| **Fase 6** | Tenant-setting enable_clusters + UI modus toggle | Laag | Tenant model + frontend |
| **Fase 7** | Agent sync (6 agents) | Laag | Agent prompts/tools |
| **Fase 8** | Data-migratie bestaande data | Hoog (destructief) | Alembic + SQL |

> **Fase 8 (migratie) pas uitvoeren als Fase 1-7 getest en stabiel zijn.** Tot die tijd werken oude en nieuwe structuur naast elkaar.

---

## 7. Wat NIET verandert

- **27 modellen met `scope_id` FK**: Geen wijziging. Risk, Assessment, Incident, Policy, etc. blijven gewoon naar `scope.id` wijzen.
- **ScopeDependency tabel**: Blijft bestaan voor infrastructure/service dependencies.
- **Conditionele velden op Scope**: `asset_type`, `vendor_contact_*`, BIA ratings, `rto_hours`, etc. blijven getypeerde velden. Geen JSONB.
- **Governance-velden**: `governance_status`, `scope_motivation`, `in_scope`, `validity_year` — blijven.
- **External integration velden**: `external_id`, `external_source`, `last_synced` — blijven.

---

## 8. Succeskriterium

- [ ] MKB-gebruiker kan processen en assets aanmaken zonder ooit "Organization", "Cluster" of "Virtual" te zien
- [ ] Eén asset (bijv. Microsoft 365) kan aan meerdere processen gekoppeld worden zonder duplicatie
- [ ] Gemeente-gebruiker kan Clusters inschakelen en een diepe boom maken
- [ ] RBAC werkt: rechten op een afdeling vloeien door naar processen EN gekoppelde assets
- [ ] Alle bestaande data is correct gemigreerd (geen orphaned records)
- [ ] Alle 13+ modellen die `scope_id` gebruiken werken ongewijzigd
