# IMS (Integrated Management System)

> **The Model leads. The API guards. Tools execute. AI supports.**

The **IMS** is a next-generation Governance, Risk, and Compliance (GRC) platform designed for **ISMS**, **PIMS**, and **BCMS**. It enforces strict separation of concerns and leverages **Local AI** to reduce administrative overhead without compromising data sovereignty.

---

## 🏗 Architecture
The system is built on 4 strict layers (detailed in `DESIGN.md`):

1.  **Layer 1: The Model (Data)**
    *   **Single Source of Truth** for Norms, Risks, and Controls.
    *   **Shared Core**: Assets, Processes, and Suppliers are shared across domains.
    *   **Tech**: Python SQLModel (PostgreSQL).

2.  **Layer 2: The API (logic)**
    *   **Gatekeeper**: Enforces RBAC, Validation, and Workflow states.
    *   **Tech**: FastAPI (Async/Await).

3.  **Layer 3: The Tools (UI)**
    *   **React/Vue Frontend**: A "dumb" glass pane for interaction.
    *   **Generative UI**: Dashboards created on-the-fly by AI.

4.  **Layer 4: The AI (Intelligence)**
    *   **Local-First**: Defaults to Ollama/Mistral. No cloud data leakage.
    *   **Capabilities**: Policy Drafting, Audit Execution, Evidence Analysis, Generative Dashboards.

---

## 🚀 Quick Start (Docker)

The easiest way to run the backend (API + DB) is via Docker Compose.

### Prerequisites
*   Docker & Docker Compose
*   (Optional) Ollama running locally for AI features

### Run
```bash
# 1. Start Database & API
docker-compose up -d

# 2. Access API Docs (Swagger)
# Open http://localhost:8000/docs

# 3. Access Database (PGAdmin)
# Open http://localhost:5050 (User: admin@ims.local / Pass: admin)
```

---

## 📚 Documentation
*   [**System Design (DESIGN.md)**](DESIGN.md): The technical specification and data model.
*   [**Architecture Layers**](docs/IMS%20-%20architectuurlagen.md): Conceptual breakdown of the 4 layers.
*   [**Roles & Responsibilities**](docs/IMS%20-%20rollen%20en%20verantwoordelijkheden.md): Who does what (and how it maps to RBAC).

---

## 🛡 Security & Compliance
*   **EU Data Sovereignty**: AI defaults to `localhost`. No external API calls by default.
*   **RBAC**: Granular access control per Scope (Process Owner vs Viewer).
*   **Audit Trail**: All changes to the Model are tracked.