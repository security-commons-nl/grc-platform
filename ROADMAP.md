# Roadmap

## Huidige staat

Het GRC-platform is functioneel voor de inrichtingsmodus: een organisatie kan stap voor stap een Integrated Management System (IMS) inrichten via de web-interface, ondersteund door AI-agents.

**Beschikbaar:**
- Inrichtingsmodus — 22 stappen door 4 fasen
- GRC-engine — risico's, controls, assessments, evidence, incidenten
- Multi-tenant architectuur met RBAC en Row Level Security
- AI-assistentie tijdens inrichting
- Docker-gebaseerde installatie

## Fase 1 — AI-integratie

Contextual hints per processtap en een chat-interface voor directe AI-ondersteuning tijdens het IMS-traject.

- Contextual hints (subtiele uitleg per stap, op basis van normatief kader)
- Chat-island (floating knop, zijpaneel)
- RAG-store met normatieve laag (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG)
- Domain agents per discipline (informatiebeveiliging, privacy, BCM)

## Fase 2 — Productie-readiness

Klaar voor productie-gebruik bij gemeenten.

- HTTPS via Caddy reverse proxy
- Rate limiting
- Backup-strategie PostgreSQL
- Monitoring en observability
- Deployment-documentatie

## Fase 3 — Volwassen multi-tenant platform

Schaalbaar naar meerdere organisaties en regio's.

- Regionaal dashboard (compliance-scores delen tussen gemeenten)
- Governance-tooling voor centrumgemeente-constructies
- Uitgebreide rapportage-module
- Community-bijdragen: templates, aanpakken, best practices

## Bijdragen

Heb je ideeën, wil je een feature aanvragen of zelf bijdragen? Zie [CONTRIBUTING.md](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md) of open een [issue](https://github.com/security-commons-nl/grc-platform/issues).
