# IMS (Integrated Management System) - System Design & Architecture

## 1. Introduction
The IMS is a **Governance, Risk, and Compliance (GRC)** platform designed to enforce a strict separation between **Architecture/Policy** (The Model) and **Execution** (The Tools). It implements the Plan-Do-Check-Act (PDCA) cycle for Security (ISMS), Privacy (PIMS), and Business Continuity (BCMS).

### Core Philosophy
> "The Model leads, the API guards, Tools execute, AI supports."

*   **Layer 1 (The Model)**: The single source of truth for Norms, Risks, and Controls.
*   **Layer 2 (The API)**: The gatekeeper ensuring data integrity and policy enforcement.
*   **Layer 3 (The Tools)**: User interfaces and external connectors (React/Vue Frontend).
*   **Layer 4 (The AI)**: Local/Private AI for advisory and "smart" suggestions.

---

## 2. Technology Stack & Rationale

### Backend: Python (FastAPI + SQLModel)
*   **Why**: Python is the native language of AI and Data Science. **SQLModel** (Pydantic + SQLAlchemy) allows us to define rigorous data models that serve as both the Database Schema and the API Validator. This directly supports the "Model is King" philosophy.
*   **vs Mastra/Node**: While frameworks like Mastra are excellent for orchestrating Agents (Layer 4), a dedicated backend framework like FastAPI is superior for building the foundational **Core System of Record** (Layers 1 & 2) requiring strict ACID transactions, complex relational queries, and deep schema validation. Mastra can be integrated later as the "Brain" of Layer 4, communicating with this Core API.

### Frontend: React / Vue
*   **Choice**: To be decided (likely React for broad ecosystem support).
*   **Role**: A "dumb" glass pane. It contains no business logic; it simply displays the Model's state and submits actions to the API.

### Database: PostgreSQL
*   **Role**: Centralized storage for all data, including Audit Logs.

---

## 3. Data Model (Layer 1)

### A. Governance & Strategy
1.  **Scope**: The target of governance (Asset, Process, Organization, Supplier).
    *   **Multi-Tenancy**: Hierarchical model (Municipality -> Cluster -> Dept -> Asset).
    *   *Features*: **Dependencies** (Supply Chain), **BIA Ratings** (Confidentiality/Integrity/Availability).
    *   *Accountability*: **Accountable User** (Head of Dept / Internal Contract Owner) + **Vendor Contact** (if Supplier).
    *   *Roles*: **RBAC** enforced via `UserScopeRole` (Process Owner, Editor, Viewer).
2.  **Standard (Norm)**: External frameworks (BIO, ISO 27001, NIST).
    *   *Features*: **Multilingual** (NL/EN), **Versioning**.
3.  **Requirement (Control)**: The specific rule/control text.
    *   *Rosetta Stone*: **RequirementMapping** table allows many-to-many mapping between frameworks (e.g. ISO <-> BIO) with AI confidence scores.
4.  **Policy**: Internal documents (e.g. "Access Control Policy").
    *   *Workflow*: Draft -> Review -> Approved -> Published.

### B. Risk Management (The "Plan" & "Do")
5.  **Risk**: Potential negative events linked to Scopes.
    *   *Methodology*: Heatmap (Impact vs Likelihood).
6.  **Measure (Implementation)**: Verification that a Requirement is met.
    *   *Exceptions*: Formal **Waivers** (`Exception` object) can be granted for temporary non-compliance (with expiration date).
7.  **Dashboard**: AI-Generated UI views persisted for users.

### C. Verification & Improvement (The "Check" & "Act")
8.  **Assessment (Traject)**: A generic compliance project (Start Date -> Deadline).
    *   **Types**: Self-Assessment (ENSIA), Audit (BIO), Pentest, DPIA, Compliance Journey.
    *   **Features**: Timeline Planning, "Requirement Set" selection (via Standard), Team Assignment.
    *   *Structure*: Assessment -> Findings -> Evidence.
    *   *AI Support*: Generates timelines, suggests Controls based on Traject Type.
9.  **Evidence**: Proof of compliance (Documents, Screenshots).
10. **Incident**: Real-world security failures.
    *   *Traceability*: Incident -> Root Cause -> Corrective Action.
11. **Unified Improvement Backlog**:
    *   **Finding** (Audit Gap) or **Incident** (Breach) -> **Corrective Action**.
    *   *Goal*: One single list of "Things to Fix."

---

## 4. Artificial Intelligence Strategy (Layer 4)

*   **Deployment**: **Local/Private Only**. No Risk data leaves the perimeter.
*   **Mode**:
    1.  **Reactive**: Responds only when asked (Chat interface).
    2.  **Advisory**: Suggests Measures based on selected Risks ("Others typically use MFA here").
    3.  **Busywork Reduction**: Auto-mapping new Regulations to existing Controls; Summarizing Incident Reports.
    4.  **Generative (Drafting)**: Writes Policy text based on `OrganizationContext` and `KnowledgeArtifacts`.
    5.  **Audit Execution**: Analyzes `Evidence` (images/PDFs) against Control requirements to recommend Pass/Fail.
    6.  **Generative UI**: Creates custom **Dashboards** (JSON Config) on-the-fly based on user prompts (e.g., "Show me a heatmap for HR System").

---

## 5. Security & Isolation
*   **Day 1**: The system runs isolated (air-gapped or internal network). No active scanning of the wider network.
*   **Future**: Permitted "Automated Checks" (e.g., verify MFA status via Azure Graph API).

---

## 6. AI Content Delivery & RAG (The "Brain" Expansion)
To support policy writing and context-aware advice, the system uses **Retrieval-Augmented Generation (RAG)** backed by `pgvector`.

### Data Ingestion (Input Agents)
1.  **Document Agents**: Process PDF/Word uploads (Policies, Reports) -> Text Chunks -> Vector Store.
2.  **Voice Agents**: Conduct interviews (Speech-to-Text) with Process Owners -> Transcripts -> Vector Store.
    *   *Example*: "Interview the HR Manager about the Offboarding Process."

### Knowledge Store
*   **OrganizationContext**: High-level structured keys (Mission, Vision, Risk Appetite).
*   **KnowledgeArtifacts**: Unstructured data (Interview transcripts, raw dumps) available for RAG. 
    *   *Constraint*: All artifacts are stored locally in Postgres.


