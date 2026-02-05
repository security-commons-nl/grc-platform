# IMS (Integrated Management System)

> **Model-gedreven GRC voor ISMS, PIMS en BCMS — met lokale AI als versneller.**

IMS is een Governance, Risk & Compliance-platform dat **normen, risico’s, controls en bewijs** centraal beheert. Het is ontworpen voor organisaties (o.a. publieke sector) die meerdere managementsystemen willen combineren in één consistente bron van waarheid, met **strikte scheiding van data, logica en UI** en optionele **local-first AI**.

---

## ✨ Wat IMS doet
- **Eén gedeeld kernmodel** voor assets, processen, leveranciers en controls over ISMS/PIMS/BCMS heen.
- **Workflow- en RBAC-gedreven governance** via een API die alle validatie en autorisatie bewaakt.
- **AI-ondersteuning** voor beleid, audit-activiteiten en bewijsanalyse met lokale modellen (Ollama) als default.

---

## 🧱 Architectuur (4 lagen)
1. **Model (Data)** – single source of truth voor normen, risico’s en controls.
2. **API (Logic)** – gatekeeper voor RBAC, validatie en workflow-states.
3. **Tools (UI)** – een dunne front-end laag voor interactie en dashboards.
4. **AI (Intelligence)** – lokale/regionale AI voor generatieve dashboards en content.

Zie ook: [Complete Design Overview](docs/COMPLETE_DESIGN_OVERVIEW.md) en [Architectuurprincipes](docs/ARCHITECTURE_PRINCIPLES.md).

---

## 🗂 Repo-indeling
- **`backend/`** – FastAPI + SQLModel + PostgreSQL (API, domeinlogica, migraties).
- **`frontend/`** – Reflex UI (Python) voor dashboards en interactie.
- **`docs/`** – ontwerp, rollen, AI-architectuur, gap analyses, testplannen.
- **`illustrations/`** – schema’s en visuals.

---

## 🚀 Quick Start (Docker)
### 1) Configureer environment
```bash
cp .env.example .env
```
Vul de waarden in je `.env` (Postgres/pgAdmin/AI).

### 2) Start de stack
```bash
docker-compose up -d
```

### 3) Toegang
- **API docs (Swagger):** http://localhost:8001/docs
- **Frontend:** http://localhost:3000
- **pgAdmin:** http://localhost:5050
- **Ollama API:** http://localhost:11434

---

## 📚 Documentatie
- [Complete Design Overview](docs/COMPLETE_DESIGN_OVERVIEW.md)
- [IMS Roles & Responsibilities](docs/IMS%20ROLES%20AND%20RESPONSIBILITIES.md)
- [AI Gateway Architecture](docs/AI_GATEWAY_ARCHITECTURE.md)
- [Audit Logging Implementation Plan](docs/AUDIT_LOGGING_IMPLEMENTATION_PLAN.md)
- [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)

---

## 🔐 Security & Compliance
- **EU data-soevereiniteit:** AI draait lokaal of via regionale providers.
- **RBAC-first:** toegang en workflow via API-afdwinging.
- **Audit trail:** wijzigingshistorie op modelniveau.

---

## ✅ Status
IMS is actief in ontwikkeling. Zie de documenten in `docs/` voor roadmap, ontwerpkeuzes en plannen.
