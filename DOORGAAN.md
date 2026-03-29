# DOORGAAN — Alle user-facing tekst naar gebruiksvriendelijk Nederlands

## Context

~80 backend foutmeldingen zijn in het Engels ("X not found"). Twee rol-labels zijn Engels ("Admin", "Viewer"). Eén troubleshoot-tekst is technisch. Alles moet Nederlands en gebruiksvriendelijk.

## 1. Backend: Engelse foutmeldingen vertalen

Alle `HTTPException(detail="...")` in `backend/app/api/v1/endpoints/*.py`:

| Engels | Nederlands |
|--------|-----------|
| `Assessment not found` | `Assessment niet gevonden` |
| `Finding not found` | `Bevinding niet gevonden` |
| `CorrectiveAction not found` | `Corrigerende maatregel niet gevonden` |
| `Control not found` | `Control niet gevonden` |
| `Decision not found` | `Besluit niet gevonden` |
| `Document not found` | `Document niet gevonden` |
| `DocumentVersion not found` | `Documentversie niet gevonden` |
| `StepInputDocument not found` | `Invoerdocument niet gevonden` |
| `GapAnalysisResult not found` | `Gap-analyse resultaat niet gevonden` |
| `Evidence not found` | `Bewijs niet gevonden` |
| `Incident not found` | `Incident niet gevonden` |
| `KnowledgeChunk not found` | `Kennisartikel niet gevonden` |
| `Risk not found` | `Risico niet gevonden` |
| `RiskControlLink not found` | `Risico-control koppeling niet gevonden` |
| `Scope not found` | `Scope niet gevonden` |
| `MaturityProfile not found` | `Volwassenheidsprofiel niet gevonden` |
| `SetupScore not found` | `Inrichtingsscore niet gevonden` |
| `GRCScore not found` | `GRC-score niet gevonden` |
| `Standard not found` | `Standaard niet gevonden` |
| `Requirement not found` | `Vereiste niet gevonden` |
| `RequirementMapping not found` | `Vereiste-mapping niet gevonden` |
| `TenantNormenkader not found` | `Tenant-normenkader niet gevonden` |
| `StandardIngestion not found` | `Standaard-ingestie niet gevonden` |
| `Step not found` | `Stap niet gevonden` |
| `StepDependency not found` | `Stapafhankelijkheid niet gevonden` |
| `StepExecution not found` | `Stapuitvoering niet gevonden` |
| `StepOutput not found` | `Stap-output niet gevonden` |
| `Fulfillment not found` | `Fulfillment niet gevonden` |
| `Tenant not found` | `Tenant niet gevonden` |
| `Region not found` | `Regio niet gevonden` |
| `User not found` | `Gebruiker niet gevonden` |
| `UserTenantRole not found` | `Gebruikersrol niet gevonden` |
| `UserRegionRole not found` | `Regionale gebruikersrol niet gevonden` |

**Bestanden:** assessments.py, controls.py, decisions.py, documents.py, evidence.py, incidents.py, knowledge.py, risks.py, scopes.py, scores.py, standards.py, steps.py, tenants.py

## 2. Frontend: rol-labels naar Nederlands

**Bestand:** `frontend/src/lib/constants.ts`

| Huidig | Nieuw |
|--------|-------|
| `admin: 'Admin'` | `admin: 'Beheerder'` |
| `viewer: 'Viewer'` | `viewer: 'Alleen-lezen'` |

**Bestand:** `frontend/src/app/login/page.tsx` — zelfde labels in ROLE_OPTIONS

## 3. Frontend: troubleshoot-tekst

**Bestand:** `frontend/src/app/(protected)/inrichten/page.tsx` (regel ~65)

| Huidig | Nieuw |
|--------|-------|
| `Controleer de API-verbinding` | `Vernieuw de pagina of neem contact op met de beheerder` |

## 4. Backend tests: assertions updaten

Tests die assertions doen op Engelse foutmeldingen (bijv. `assert "not found" in response`) moeten mee-updaten naar de Nederlandse tekst.

## Verificatie

1. `grep -r '".*not found"' backend/app/api/` → nul resultaten
2. `docker-compose exec api pytest --tb=short` → groen
3. `cd frontend && npx playwright test` → groen
4. `python generate-docs.py` → docs bijgewerkt
