# RFC 0003 — Frontend Test-strategie

> **Status:** V1 actief — ratchet op V1 (20/50/40/20) · **Datum:** 2026-05-12 (status bijgewerkt 2026-05-13)
> **Type:** Tooling + CI · **Module-impact:** alle modules met UI (M2, M3, M4, M5)
> **Beslissing nodig vóór:** uitbreiding e2e-suite naar M4/M5 + activatie van eslint in CI
>
> **Implementatie-stand (2026-05-13)**
> - **Vitest 3 + RTL 16 + MSW 2** geconfigureerd; `src/test/setup.ts` start MSW met `onUnhandledRequest='error'`. SWR-isolatie per test via `<SWRConfig provider={() => new Map()}>` zodat caches niet over tests heen lekken.
> - **51 unit-tests over 11 spec-files** (was 20 / 4): `lib/constants`, `lib/format-error`, `lib/api-client`, `components/shared/org-unit-select`, `components/shared/custom-fields-form`, `components/beheer/simulation-interpretation`, plus page-tests voor `/beheer/ai-systemen`, `/beheer/hitl-checkpoints`, `/admin/agent-tokens`, `/beheer/controls`, `/beheer/assessments`.
> - **Coverage-ratchet**: thresholds in `vitest.config.ts` van 1/1/1/1 → 20/50/40/20. Actuals ~27/76/49/27. Volgende stop: V2 (50/40/50/50) na hook- en `auth-provider`-tests.
> - **17 Playwright e2e-specs** met UI → API → DB-verificatie via `docker compose exec psql`-helper (`frontend/e2e/helpers/db.ts`). Cached dev-token-helper (`frontend/e2e/helpers/auth.ts`) omzeilt `RATE_LIMIT_AUTH=10/min` door één JWT te delen over de hele suite.
> - CI groen op alle 3 jobs (Backend pytest, Frontend lint+typecheck+test+build, Playwright e2e); twee opeenvolgende full-runs zonder retries of container-restarts.

---

## 1. Probleem

Frontend-test-coverage is asymmetrisch t.o.v. backend:

| Laag | Aanwezig | Gat |
|------|----------|-----|
| Backend unit/integration | 207 pytest-tests over 27 bestanden, CI groen, pgvector-service in workflow | Coverage-rapportage niet aan |
| Frontend unit | **Geen** | Geen jest/vitest, geen `*.test.tsx`, geen RTL-setup |
| Frontend e2e | 3 Playwright-spec-bestanden (~160 regels) — auth, navigatie, inrichting-flow | M2 (GRC-engine), M4 (AI Governance, aanstaande UI), M5 (Monte Carlo) volledig niet gedekt |
| Frontend lint | **Uit in CI** door eslint 10.3 + eslint-config-next-incompatibiliteit | Subtiele fouten glippen door |

Concrete risico's:

- Bij refactoring van form-componenten (bv. `simulation-results.tsx`) breekt UX zonder dat CI dat ziet.
- Naderende RFC's 0004 (M4-UI) en 0005 (M5-UI) introduceren nieuwe componenten — zonder testbasis ontstaat technische schuld direct.
- Lint-uit-stand maskeert mogelijk al fouten in productie-code; we weten niet hoeveel.

---

## 2. Niet-doelen

Dit RFC behandelt **niet**:

- **Visuele regressie-testing** (Percy, Chromatic). Mooi-om-te-hebben, niet kritisch voor demo-readiness.
- **Performance-budget enforcement** in CI (Lighthouse-thresholds). Apart RFC.
- **Storybook**. Component-isolation is nuttig maar voegt build-tijd toe; we wachten op concrete vraag.
- **Cross-browser e2e** (Firefox, Webkit). Chromium-only blijft V1.
- **End-to-end-tests over docker-compose vanaf de developer-laptop**. CI doet dit; lokaal blijft optioneel.

---

## 3. Voorstel

### 3.1 Frontend unit-tests: Vitest + React Testing Library + MSW

**Stack-keuze:**

| Tool | Versie | Rol |
|------|--------|-----|
| `vitest` | ^3 | Test-runner (snel, ESM-native, jest-API-compatibel) |
| `@vitest/coverage-v8` | ^3 | Coverage-rapportage via V8 |
| `@testing-library/react` | ^16 | Component-render + interactie |
| `@testing-library/jest-dom` | ^6 | Matchers `toBeInTheDocument` etc. |
| `@testing-library/user-event` | ^14 | User-input-simulatie |
| `msw` | ^2 | Network mocking via service worker / Node |
| `jsdom` | ^25 | DOM-emulatie voor Vitest |

**Waarom Vitest boven Jest:**
- Native ESM (Next 16 + React 19 zijn ESM-first)
- Snellere watch-mode dankzij Vite
- Jest-compatibele API (kennis-overdracht eenvoudig)
- Geen Babel-config nodig

**Waarom RTL:**
- Test gedrag, niet implementatie (huidige standaard in React-ecosysteem)
- Goede a11y-defaults — leest queries zoals een screenreader doet

**Waarom MSW:**
- Mock op netwerk-niveau, niet op fetch-functie-niveau
- Zelfde mocks bruikbaar in unit-tests én Playwright-e2e (bonus: deduplicatie)
- Geen aanpassingen aan productie-code nodig

### 3.2 Directory-structuur

```
frontend/
├── src/
│   ├── components/
│   │   ├── beheer/
│   │   │   ├── simulation-results.tsx
│   │   │   └── simulation-results.test.tsx       ← unit-test naast component
│   │   └── ...
│   ├── lib/
│   │   ├── hooks/
│   │   │   ├── use-risks.ts
│   │   │   └── use-risks.test.ts                  ← hook-test naast hook
│   │   └── api-client.test.ts
│   └── test/
│       ├── setup.ts                                ← Vitest setup: RTL matchers, MSW
│       ├── msw-handlers.ts                         ← centrale handler-lijst
│       └── factories.ts                            ← test-data-factories (faker.js optioneel)
├── vitest.config.ts
└── e2e/                                            ← bestaand
```

**Convention:** test-bestand naast bron-bestand met `.test.ts(x)`-suffix. Geen aparte `__tests__/`-directory — dat verhoogt zoek-overhead.

### 3.3 Coverage-drempels

| Doel | Drempel V1 | Drempel V2 (na 3 maanden) |
|------|------------|---------------------------|
| Statements | 50% | 70% |
| Branches | 40% | 60% |
| Functions | 50% | 70% |
| Lines | 50% | 70% |

CI faalt onder V1-drempels. Bewust laag startpunt — niet-realistisch om vandaag op 80% te willen zijn met nul tests. Drempel groeit mee met groei van suite.

**Exclusies:**
- `*.config.ts`, `*.d.ts`
- `src/app/**/loading.tsx`, `error.tsx`, `not-found.tsx` (Next.js conventies, geen logica)
- `src/test/**`

### 3.4 ESLint herstellen

**Probleem:** `eslint@10.3.0` + `eslint-config-next` crashen op `contextOrFilename.getFilename is not a function`. Documentatie noemt dit (zie `.github/workflows/frontend.yml` regels 28-31).

**Drie opties:**

| Optie | Wat | Trade-off |
|-------|-----|-----------|
| **A — Downgrade naar eslint 10.2** | `npm install eslint@10.2.0` | Snel, weinig risico. Hoort tijdelijk te zijn maar werkt direct. |
| **B — Wachten op eslint-config-next patch** | Open issue tracken, intussen lint uit | Geen actie nu; ongedekt. |
| **C — Migreren naar Biome** | Vervang eslint + prettier door biome (Rust-tool, sneller, één-config) | Veel werk, maar grote winst. Apart RFC verdient eigenlijk. |

**Voorstel V1:** Optie A (downgrade). Activeer lint in CI. Optie C in vervolg-RFC overwegen wanneer Biome eslint-config-next-equivalent goed dekt.

### 3.5 E2E-uitbreiding

Huidige specs (`auth.spec.ts`, `navigation.spec.ts`, `inrichting-flow.spec.ts`) dekken M3 + auth. Toevoegen:

| Spec | Module | Flow |
|------|--------|------|
| `beheer-risicos.spec.ts` | M2 | Create risico → set likelihood/impact → save → verify in lijst → verwijder |
| `beheer-controls.spec.ts` | M2 | Create control → koppel aan risico → koppel aan norm → save → verify |
| `beheer-assessments.spec.ts` | M2 | Create assessment → scope → uitvoeren → finding aanmaken → corrective-action |
| `m5-simulatie.spec.ts` | M5 | Create risico met triangular distributie → simuleer → zie percentielen-staaf → simuleer opnieuw met seed → verifiëer identieke output (na RFC 0005: ook historie en compare) |
| `m4-ai-systemen.spec.ts` | M4 | Na RFC 0004 implementatie: register AI-systeem → classifier-advies → save → HITL-checkpoint → review |

**Conventies:**
- Page-Object-Model **niet** afdwingen (overhead voor kleine suite). Gewone helper-functies in `e2e/helpers/`.
- Test-data per spec genereert eigen tenant via `/auth/dev-token` met unieke tenant_slug — voorkomt parallel-test-interferentie. Wijziging op `e2e.yml`: `workers: 1` mag dan naar `workers: 2`.
- Geen tests tegen externe APIs (Mistral, Ollama) in e2e. MSW gateway op API-laag tijdens e2e parkeren voor V2.

### 3.6 CI-workflow-aanpassingen

**`.github/workflows/frontend.yml`** krijgt nieuwe stap vóór `build`:

```yaml
- name: Lint
  run: npm run lint                  # nu uncomment

- name: Type check
  run: npm run typecheck

- name: Unit tests
  run: npm run test -- --coverage

- name: Upload coverage
  uses: actions/upload-artifact@v7
  with:
    name: frontend-coverage
    path: frontend/coverage/
    if-no-files-found: ignore
```

**Drempels** worden in `vitest.config.ts` afgedwongen — `coverage.thresholds`. Geen aparte tool nodig.

**`.github/workflows/tests.yml`** (backend) krijgt coverage-rapportage:

```yaml
- name: Run tests
  run: pytest --tb=short -q --cov=app --cov-report=xml --cov-report=term

- name: Upload coverage
  uses: actions/upload-artifact@v7
  with:
    name: backend-coverage
    path: backend/coverage.xml
    if-no-files-found: ignore
```

Drempel start op 70% (backend is al goed gedekt; ondergrens om regressies te zien).

### 3.7 Lokale ontwikkelaar-experience

Nieuwe npm-scripts in `frontend/package.json`:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "typecheck": "tsc --noEmit",
    "lint": "next lint",
    "lint:fix": "next lint --fix"
  }
}
```

Pre-commit hook (optioneel) via `husky` + `lint-staged` — buiten scope dit RFC; ontwikkelaars kiezen zelf.

---

## 4. Alternatieven (afgewezen of geparkeerd)

| Alternatief | Status |
|-------------|--------|
| **Jest i.p.v. Vitest** | Afgewezen. Vitest is sneller en ESM-native; Next 16 + React 19 zijn ESM-first. Migratie van Jest naar Vitest is later duur. |
| **Cypress i.p.v. Playwright** | N.v.t. — Playwright zit al; geen reden te wisselen. |
| **Storybook + visual regression** | Geparkeerd. Voegt waarde maar build-tijd + onderhoud. Wacht op concrete vraag. |
| **Biome direct (vervang ESLint + Prettier)** | Geparkeerd. Apart RFC. V1 herstelt eerst eslint. |
| **POM (Page-Object-Model) voor e2e** | Afgewezen. Helper-functies volstaan tot suite >20 specs. |
| **Mock-Service-Worker in productie-build** | Afgewezen. MSW alleen in tests; productie blijft schoon. |
| **Snapshot-tests (Jest-snapshots)** | Afgewezen. Brittle voor UI; RTL-queries zijn beter. |

---

## 5. Risico's en mitigaties

| Risico | Mitigatie |
|--------|-----------|
| Vitest + Next 16 + React 19 compatibiliteits-quirks | Pin versies; smoke-test bij major upgrades. Documenteer in `frontend/CONTRIBUTING.md`. |
| Coverage-drempel blokkeert legitieme PRs vroeg | Start laag (50%) en groei geleidelijk. Tijdelijke uitzondering via `nyc-config`-override per PR mogelijk. |
| MSW-handlers raken out-of-sync met echte API | Genereer handlers uit OpenAPI-spec (apart issue). V1 handmatig; bewaak via e2e (die wel tegen echte API loopt). |
| E2E-suite wordt te traag (>10 min) | Splits in shards via Playwright `--shard`-flag wanneer >5 specs. |
| Lint-fixes leiden tot grote eerste-keer-PR | Eén losse "lint-cleanup"-PR, niet meegescoped met feature-werk. |
| ESLint downgrade introduceert security-issue | Onwaarschijnlijk voor 10.2 vs 10.3 patch. Dependabot pakt vervolg-bumps op. |
| Test-tenant-creatie via dev-token-flow lekt | Dev-token is alleen actief bij `ENVIRONMENT=development` in `.env`. Productie heeft `RATE_LIMIT` + JWT-secret-rotatie. |

---

## 6. Acceptatie-criteria

Dit RFC is "geïmplementeerd" wanneer:

- [ ] `frontend/vitest.config.ts` + `frontend/src/test/setup.ts` + `frontend/src/test/msw-handlers.ts` aanwezig
- [ ] Tenminste vijf voorbeeld-tests aanwezig in suite (per directory: `components`, `lib/hooks`, `lib/api-client`)
- [ ] Coverage-drempels in `vitest.config.ts` op V1-niveau (50/40/50/50)
- [ ] ESLint actief (Optie A — downgrade naar 10.2) en `npm run lint` slaagt
- [ ] `frontend.yml` CI-workflow draait lint + typecheck + unit tests + build; faalt bij niet-naleven drempels
- [ ] `tests.yml` CI-workflow rapporteert backend-coverage
- [ ] Drie nieuwe e2e-specs (`beheer-risicos`, `beheer-controls`, `m5-simulatie`) aanwezig en groen
- [ ] `playwright.config.ts` `workers: 2` (mits test-tenant-isolatie werkt)
- [ ] `frontend/CONTRIBUTING.md` of `frontend/README.md` bevat testing-sectie
- [ ] Bij implementatie M4-UI (RFC 0004): `m4-ai-systemen.spec.ts` toegevoegd

---

## 7. Open vragen voor discussie

1. **Coverage-drempel: harde fail of waarschuwing?** Voorstel: harde fail in V1, omdat suite klein is en gemakkelijk te onderhouden. Bij grotere suite mogelijk soft-fail per directory.
2. **Test-isolatie: tenant-per-spec of tenant-per-test?** Per-spec is goedkoper; per-test puurder. Voorstel: per-spec met `beforeAll`-creatie en `afterAll`-cleanup; tests binnen spec delen tenant.
3. **MSW handlers in een aparte package**: deelbaar tussen unit en e2e, of duplicate? Voorstel: gedeeld in `src/test/msw-handlers.ts`; e2e-laag wel "echte" API houden (tegen docker compose), unit-laag MSW.
4. **Pre-commit hook**: project-breed verplicht via husky, of optioneel via documentatie? Voorstel: documenteren, niet afdwingen — community-contributors moeten niet door extra installatie-stap moeten.
5. **Visuele regressie**: doen of niet doen voor M5-charts (na RFC 0005)? Voorstel: niet doen tot we klantvraag zien — charts veranderen vaak in vroege fase, snapshots zijn pijn.
6. **Test-data-factories**: handmatig schrijven of `faker.js`/`@faker-js/faker`? Voorstel: handmatig — minder dependency, voorspelbare data.

---

## 8. Beslismomenten

- **Goedkeuring RFC** vóór Vitest-installatie
- **Optie A vs C voor lint**: V1 = A (downgrade); RFC voor C (Biome) op losse track
- **Acceptatie van V1-coverage-drempels** (50/40/50/50) als realistisch startpunt
- **Volgorde van e2e-uitbreiding**: M5 + M2 vóór M4 (M4-UI bestaat nog niet)

---

## 9. Referenties

- `.github/workflows/frontend.yml` — huidige (incomplete) frontend-CI
- `.github/workflows/e2e.yml` — huidige Playwright-config
- `frontend/playwright.config.ts` — bestaande e2e-instellingen
- RFC 0004 (M4-frontend-UI) — produceert componenten die test-dekking nodig hebben
- RFC 0005 (M5-UI-uitbreiding) — produceert chart-componenten die test-dekking nodig hebben
- Vitest: https://vitest.dev/
- React Testing Library: https://testing-library.com/
- MSW: https://mswjs.io/
- Playwright: https://playwright.dev/

---

## Changelog

| Datum | Wijziging | Door |
|-------|-----------|------|
| 2026-05-12 | Initieel concept | open-source projectteam |
