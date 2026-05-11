# Roadmap

> Het platform is opgebouwd uit zeven modules (M0–M6). Zie [`docs/modules.md`](docs/modules.md) voor de modulaire opbouw. Deze roadmap beschrijft wat per module gepland staat.

## Huidige staat

Het GRC-platform is functioneel voor de inrichtingsmodus én dagelijks GRC-gebruik.

**Operationeel (M0 + M1 + M2 + M3):**
- **M0** Platform — multi-tenant met RBAC en Row Level Security
- **M1** Normen & Mapping — BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG, RAG-pipeline op normatieve documenten
- **M2** GRC-engine — risico's, controls, assessments, evidence, incidenten
- **M3** IMS-inrichtingswizard — 22 stappen door 4 fasen, 7 AI-domeinagenten, AIAuditLog
- Docker-gebaseerde installatie

---

## Actieve sporen

Twee modules zijn nu in actieve ontwikkeling. Andere modules zijn bewust geparkeerd tot een van deze twee is afgerond.

### Spoor 1 — Productie-readiness (M0)

Klaar voor productie-gebruik bij gemeenten. **Module-focus: M0 productie-hard maken.**

- [x] Klikbaar likelihood-impact matrix-grid in risicoregister (vervangt dropdowns; heatmap boven tabel) — M2
- [x] HTTPS via Caddy reverse proxy (documentatie) — M0 — zie [`docs/deployment-caddy.md`](docs/deployment-caddy.md)
- [x] Rate limiting op API-endpoints — M0 — `slowapi` met instelbare limits per `.env` (`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`); auth-endpoints strenger; `/health` exempt
- [x] Geautomatiseerde backup-strategie PostgreSQL — M0 — zie [`docs/backup.md`](docs/backup.md), `scripts/backup-postgres.sh` + restore + end-to-end pipeline-test
- [x] Monitoring en observability — M0 — zie [`docs/monitoring.md`](docs/monitoring.md): `/health/details` endpoint, structured JSON logging in productie, Langfuse-config-detectie, alerting-drempels
- [ ] Deployment-documentatie voor IT-beheerders — M0
- [ ] Security hardening checklist — M0

### Spoor 2 — AI Governance Module (M4)

Uitbreiding met AI-governance functionaliteit. Aansluiting op EU AI Act (verordening 2024/1689) en NIST AI RMF. **Module-focus: M4 bouwen.**

- [ ] AI-systemenregister — catalogiseer alle AI-toepassingen per organisatie — M4
- [ ] EU AI Act risicoclassificatie per AI-systeem (verboden / hoog-risico / beperkt / minimaal) — M4
- [ ] NIST AI RMF als normenkader naast BIO 2.0 en ISO 27001 — M1 / M4
- [ ] AI Conformiteitsbeoordeling als assessment-type — M2 / M4
- [ ] Non-Human Identity (NHI) support — agent-tokens met beperkte scope en TTL — M0 / M4
- [ ] AI-audit log uitbreiding — HITL-checkpoints en menselijk toezicht registratie — M0 / M4

Detailvoorstel: [`docs/ai-governance-uitbreiding.md`](docs/ai-governance-uitbreiding.md).

---

## Geparkeerde sporen

Gepland, maar bewust uitgesteld tot de actieve sporen zijn afgerond. Niet geschrapt — wel niet *nu*.

### M6 — Inter-organisatorische samenwerking (geparkeerd)

Schaalbaar naar meerdere organisaties en regio's.

- [ ] Regionaal dashboard — compliance-scores delen tussen gemeenten — M6
- [ ] Governance-tooling voor centrumgemeente-constructies — M6
- [ ] Uitgebreide rapportage-module — M6 / M2
- [ ] Community-bijdragen: templates, aanpakken, best practices — M3

---

## Open scope-beslissing — M5 Risicokwantificatie

**Status: scope-keuze in voorbereiding, geen bouw-werk.**

Functionaliteit voor kwantitatief risicomanagement (financiële ranges, kansverdelingen, Monte Carlo, koppeling aan P&C-cyclus en organisatiedoelen, organisatie-units onder tenant) is **niet gepland**. Twee redenen:

1. **Andere persona** dan de huidige doelgroep — controller / concernadviseur risicomanagement i.p.v. CISO / ISO / TIMS-lid.
2. **Architectuurspanning** — sommige bijhorende eisen (configureerbaarheid zonder maatwerk, kwantitatieve modellering) wijken af van het huidige ontwerpprincipe "Database leading, schema vast".

Voordat hier ontwikkelwerk op start moet er een keuze liggen: past M5 binnen de scope van dit platform, of is dit een ander product? Zie [`docs/modules.md`](docs/modules.md) sectie M5. Discussie via [Discussions](../../discussions).

---

## Werkwijze parallelle sporen

De twee actieve sporen lopen parallel maar onafhankelijk:
- Spoor 1 raakt vooral `backend/app/core/*`, deployment-docs en infrastructuur. Weinig schemawijziging.
- Spoor 2 raakt nieuwe tabellen, nieuwe endpoints, nieuwe UI-routes. Bouwt voort op M0/M1/M2.

Beide sporen zijn af-bare eenheden — elk levert zelfstandig waarde op.

---

## Bijdragen

Heb je ideeën, wil je een feature aanvragen of zelf bijdragen? Zie [CONTRIBUTING.md](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md) of open een [issue](https://github.com/security-commons-nl/grc-platform/issues).
