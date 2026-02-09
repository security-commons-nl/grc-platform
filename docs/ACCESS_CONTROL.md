# IMS Toegangsmodel

> **Autoritatief document** — vervangt de voormalige `IMS ROLES AND RESPONSIBILITIES.md`,
> `IMS ACCESS CONTROL MODEL.md` en `IMS ACCESS CONTROL ANALYSIS.md`.
> Laatst bijgewerkt: 2026-02-09

---

## Drie lagen

Het IMS kent drie autorisatielagen. Een gebruiker moet door alle drie om iets te kunnen doen.

```
Laag 0: PLATFORM          User.is_superuser = true
                           ↓ ziet alle tenants, bypassed alle checks
Laag 1: ORGANISATIE        TenantUser.role (OWNER / ADMIN / MEMBER)
                           ↓ bepaalt of je lid bent + of je users mag beheren
Laag 2: SCOPE + ROL        UserScopeRole (Beheerder / Coordinator / Eigenaar / Medewerker / Toezichthouder)
                           ↓ bepaalt wat je mag DOEN met GRC-inhoud
```

### Waarom twee rollagen?

| Vraag | Antwoord komt van |
|-------|-------------------|
| "Mag deze user gebruikers uitnodigen?" | **TenantRole** (ADMIN/OWNER) |
| "Mag deze user risico's accepteren voor HR?" | **Role** via UserScopeRole (EIGENAAR op scope HR) |

TenantRole gaat over **de organisatie zelf** (users, billing, settings).
Role gaat over **de GRC-inhoud** (risico's, controls, assessments).

---

## Laag 0: Superuser (platform)

| Veld | `User.is_superuser` |
|------|---------------------|
| **Wie** | Jij als platformbeheerder |
| **Kan** | Alles in alle tenants, bypassed alle RBAC-checks |
| **Instellen** | Veld `is_superuser` in user-formulier (`/admin/users`) |

> Superuser is NIET hetzelfde als Beheerder. Beheerder is scope-gebonden binnen één tenant.
> Superuser opereert boven de tenants.

---

## Laag 1: Organisatie-lidmaatschap (TenantRole)

Een `User` wordt lid van een `Tenant` via de koppeltabel `TenantUser`.

| TenantRole | Wat mag je? | Typisch voor |
|------------|-------------|-------------|
| **OWNER** | Alles van ADMIN + billing, partnerships, tenant-instellingen | De oprichter / directie |
| **ADMIN** | Gebruikers uitnodigen, verwijderen, wachtwoorden resetten | CISO, IT-beheerder |
| **MEMBER** | Lid zijn van de organisatie — verdere rechten via Laag 2 | Iedereen |

### Waar beheer je dit?

| Actie | Backend endpoint | Frontend |
|-------|-----------------|----------|
| User toevoegen aan tenant | `POST /users/{id}/tenants/{tid}` | Nog niet in UI |
| User verwijderen uit tenant | `DELETE /users/{id}/tenants/{tid}` | Nog niet in UI |
| Tenant-lidmaatschappen bekijken | `GET /users/{id}/tenants` | Sidebar tenant-switcher |
| Tenant aanmaken | `POST /tenants/` | Nog niet in UI (alleen API) |
| Tenant bewerken | `PATCH /tenants/{id}` | Nog niet in UI |
| Tenant deactiveren | `DELETE /tenants/{id}` | Nog niet in UI |
| Tenant-users overzicht | `GET /tenants/{id}/users` | Nog niet in UI |

> **Let op:** TenantRole wordt bij `create_user` automatisch op MEMBER gezet.
> Wijzigen naar ADMIN/OWNER kan momenteel alleen via de database of API.

### Multi-tenant

Een user kan lid zijn van meerdere tenants. Eén daarvan is `is_default = true`.
In de frontend kies je je actieve tenant via de sidebar-switcher. Alle requests
sturen `X-Tenant-ID` mee als header.

---

## Laag 2: GRC-rollen per scope (Role via UserScopeRole)

Dit is het hart van het systeem. Gebaseerd op het **Drielijnenmodel**:

```
┌────────────────────────────────────────────────────────────┐
│  3e LIJN — Audit & Toezicht                                │
│  TOEZICHTHOUDER: lees alles + schrijf findings             │
├────────────────────────────────────────────────────────────┤
│  2e LIJN — GRC Specialisten                                │
│  BEHEERDER: volledige GRC-toegang, ziet alle scopes        │
│  COORDINATOR: gebruikersbeheer, ziet alle scopes           │
├────────────────────────────────────────────────────────────┤
│  1e LIJN — Operatie                                        │
│  EIGENAAR: risico-acceptatie, besluiten (per scope)        │
│  MEDEWERKER: controls invullen, taken uitvoeren (per scope)│
└────────────────────────────────────────────────────────────┘
```

### De 5 rollen in detail

| Role | Lijn | Scope-gebonden? | Rechten |
|------|------|-----------------|---------|
| **BEHEERDER** | 2e | Nee — ziet alle scopes | Volledige GRC-inhoud: risico's, controls, beleid, frameworks, rapportages. Vergelijkbaar met CISO. |
| **COORDINATOR** | 2e | Nee — ziet alle scopes | Gebruikers beheren + GRC-inhoud bewerken. Vergelijkbaar met Security Officer. |
| **EIGENAAR** | 1e | **Ja** — alleen eigen scope(s) | Risico's accepteren, BIA invullen, besluiten nemen voor zijn afdeling/proces. Vergelijkbaar met proceseigenaar/lijnmanager. |
| **MEDEWERKER** | 1e | **Ja** — alleen eigen scope(s) | Controls implementeren, evidence uploaden, taken afhandelen. Vergelijkbaar met uitvoerder. |
| **TOEZICHTHOUDER** | 3e | Nee — leest alle scopes | Alles lezen + findings en assessments schrijven. Vergelijkbaar met (interne) auditor. |

### Scope-hiërarchie

Rollen op een parent-scope **cascaderen** naar child-scopes:

```
Organisatie "Gemeente X"        ← EIGENAAR hier = eigenaar van alles eronder
  └─ Cluster "Bedrijfsvoering"
       ├─ Afdeling "IT"         ← MEDEWERKER hier = kan werken in IT + children
       │    ├─ Proces "Werkplekbeheer"
       │    └─ Asset "Firewall"
       └─ Afdeling "HR"
```

Dit wordt berekend in `rbac.py → get_scope_access()` die de scope-boom doorloopt.

### Waar beheer je dit?

| Actie | Backend endpoint | Frontend |
|-------|-----------------|----------|
| Rol toekennen | `POST /users/{id}/scopes/{scope_id}/roles/{role}` | `/admin/users` → sleutel-icoon → Rollen-dialoog |
| Rol intrekken | `DELETE /users/{id}/scopes/{scope_id}/roles/{role}` | `/admin/users` → sleutel-icoon → Rollen-dialoog |
| Rollen van user bekijken | `GET /users/{id}/scopes` | `/admin/users` → sleutel-icoon |
| Permissies checken | `GET /users/{id}/permissions/{scope_id}` | Intern (AuthState) |

### RBAC-guards in de backend

Elke endpoint gebruikt een guard als FastAPI dependency:

| Guard | Toegestane rollen | Gebruikt door |
|-------|-------------------|---------------|
| `require_admin` | BEHEERDER | Tenant aanmaken, deactiveren |
| `require_coordinator_or_admin` | BEHEERDER, COORDINATOR | Users CRUD, rollen toekennen |
| `require_editor` | BEHEERDER, COORDINATOR, EIGENAAR, MEDEWERKER | Risico's/controls/etc. aanmaken/bewerken |
| `require_configurer` | BEHEERDER, COORDINATOR, EIGENAAR | Scopes configureren, BIA invullen |
| `require_oversight` | BEHEERDER, COORDINATOR, TOEZICHTHOUDER | Assessments, findings |

Superusers bypassen **alle** guards.

Bron: `backend/app/core/rbac.py` regels 192-230.

---

## Gebruikersbeheer in de praktijk

### Een nieuwe gebruiker aanmaken

1. Ga naar `/admin/users` (vereist: BEHEERDER of COORDINATOR)
2. Klik "+ Nieuwe gebruiker"
3. Vul username, email, naam in
4. User wordt automatisch lid van je huidige tenant (TenantRole.MEMBER)
5. Ken rollen toe via het sleutel-icoon → kies scope + rol

Backend: `POST /users/` maakt atomair User + TenantUser aan.
Bron: `backend/app/api/v1/endpoints/users.py:66`

### Rollen toekennen

1. Ga naar `/admin/users`
2. Klik het sleutel-icoon bij de user
3. Kies een scope (dropdown) + rol (dropdown)
4. Klik "Toevoegen"

De beschikbare rollen worden getoond met kleurlabels:
- **BEHEERDER** (rood)
- **COORDINATOR** (blauw)
- **EIGENAAR** (paars)
- **MEDEWERKER** (groen)
- **TOEZICHTHOUDER** (oranje)

Bron: `frontend/ims/pages/users.py`, `frontend/ims/state/user.py`

### User deactiveren vs. permanent verwijderen

| Actie | Knop | Effect | Reversibel? |
|-------|------|--------|-------------|
| Deactiveren | Oranje (user-x icoon) | `is_active = false`, kan niet meer inloggen | Ja |
| Permanent verwijderen | Rood (prullenbak icoon) | User + alle TenantUser + alle UserScopeRole weg | **Nee** |

### Wachtwoord resetten

1. Ga naar `/admin` → tab "Wachtwoorden"
2. Klik "Reset" bij de user
3. Voer nieuw wachtwoord in (min. 8 tekens)

Vereist: BEHEERDER rol.
Bron: `POST /auth/change-password`

---

## Veelgestelde vragen

### "Wat is het verschil tussen BEHEERDER en TenantRole.ADMIN?"

| | TenantRole.ADMIN | Role.BEHEERDER |
|---|---|---|
| **Laag** | Organisatie (Laag 1) | Scope/inhoud (Laag 2) |
| **Scope** | Hele tenant | Alle scopes binnen tenant |
| **Beheert** | Gebruikersaccounts | GRC-inhoud (risico's, controls, etc.) |
| **Voorbeeld** | IT-beheerder die accounts aanmaakt | CISO die het hele risicoregister beheert |

### "Wat als een MEMBER geen UserScopeRole heeft?"

Dan kan die user niks — alleen inloggen en een leeg dashboard zien. Dit is bewust: je moet
expliciet rechten toekennen per scope.

### "Kan een user meerdere rollen hebben?"

Ja. Per scope kun je meerdere rollen toekennen. Bijv. EIGENAAR van "IT" én MEDEWERKER van "HR".

### "Hoe werkt de tenant-switcher?"

Bij inloggen stuurt de API alle tenant-lidmaatschappen terug. De sidebar toont een dropdown
als je lid bent van >1 tenant. Switchen wijzigt de `X-Tenant-ID` header op alle requests.

---

## Bekende beperkingen

| Beperking | Impact | Oplossing |
|-----------|--------|-----------|
| TenantRole kan alleen via API gewijzigd worden | Admin/Owner toekennen vereist API-call | UI bouwen in `/admin/users` |
| Tenant CRUD alleen via API | Organisaties aanmaken/bewerken kan niet in UI | Admin-pagina uitbreiden |
| Geen uitnodigings-workflow | `invited_at`/`accepted_at` velden bestaan maar worden niet gebruikt | Email-integratie bouwen |
| `valid_from`/`valid_until` op UserScopeRole niet afgedwongen | Tijdelijke rollen verlopen niet automatisch | Cron/scheduled check toevoegen |

---

## Technische referenties

| Onderdeel | Bestand |
|-----------|---------|
| Role + TenantRole enums | `backend/app/models/core_models.py:44-90` |
| User model | `backend/app/models/core_models.py:3504` |
| TenantUser model | `backend/app/models/core_models.py:735` |
| UserScopeRole model | `backend/app/models/core_models.py:3560` |
| RBAC guards | `backend/app/core/rbac.py:192-230` |
| Scope-hiërarchie cascade | `backend/app/core/rbac.py:109-160` |
| User endpoints | `backend/app/api/v1/endpoints/users.py` |
| Tenant endpoints | `backend/app/api/v1/endpoints/tenants.py` |
| Auth endpoints | `backend/app/api/v1/endpoints/auth.py` |
| System endpoints | `backend/app/api/v1/endpoints/system.py` |
| Frontend user state | `frontend/ims/state/user.py` |
| Frontend auth state | `frontend/ims/state/auth.py` |
| Frontend admin state | `frontend/ims/state/admin.py` |
| Frontend users page | `frontend/ims/pages/users.py` |
| Frontend admin page | `frontend/ims/pages/admin.py` |
