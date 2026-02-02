# IMS - Architectuurlagen

De architectuur van het IMS is opgebouwd uit 4 strikte lagen. Het basisprincipe is:
> **"Het Model stuurt. De API bewaakt. De Tools voeren uit. AI ondersteunt."**

---

## Laag 1: Het Model ("De Waarheid")
Dit is het hart van het systeem. Hier wordt de werkelijkheid gemodelleerd.
*   **Functie**: Single Source of Truth voor Normen, Risico's, Maatregelen en Scopes.
*   **Implementatie**: Python **SQLModel** (Pydantic + SQLAlchemy) op een **PostgreSQL** database.
*   **Kernconcepten**:
    *   **Shared Core**: Assets, Processen en Leveranciers zijn gedeelde objecten over ISMS/PIMS/BCMS heen.
    *   **Dependencies**: Scopes kunnen afhankelijkheden hebben (Supply Chain Modeling).
    *   **BIA**: Classificatie van objecten (B/I/V) bepaalt de zwaarte van maatregelen.

## Laag 2: De API ("De Poortwachter")
De enige weg naar het model. Niemand (ook de frontend niet) mag direct in de database schrijven.
*   **Functie**: Validatie, Autorisatie (RBAC), en Business Logic.
*   **Implementatie**: **FastAPI** (Async).
*   **Taken**:
    *   Bewaakt de "State Transitions" (bijv. Beleid: Draft -> Approved).
    *   Handhaaft Workflow regels ("Je kunt geen Incident sluiten zonder Corrective Action").

## Laag 3: De Tools ("De Uitvoer")
De interface voor de mens. Dit is "domme" software die de staat van de API toont.
*   **Functie**: Interactie, Rapportage, Dashboards.
*   **Implementatie**: Modern Web Framework (React/Vue).
*   **Nieuw**: **Generative UI**. Dashboards worden dynamisch gegenereerd op basis van gebruikersvraag ("Show me HR Risks") en opgeslagen als JSON config.

## Laag 4: De AI ("Het Brein")
De slimme assistent die **lokaal** draait.
*   **Functie**: Advies, Reductie van "Busywork", Generatie.
*   **Implementatie**: **Ollama / Local LLM** + **pgvector** (RAG).
*   **Taken**:
    *   **Mapping**: "Rosetta Stone" functionaliteit (ISO <-> BIO mappings voorstellen).
    *   **Audit**: Evidence (screenshots) analyseren.
    *   **Drafting**: Beleidsteksten schrijven o.b.v. Organisatie Context.
    *   **Operational**: Incident Root Cause analyse.

## Belangrijke Beslissingen
1.  **Strict Separation**: De API weet niets van de Frontend. De Frontend weet niets van de Database.
2.  **Model First**: We bouwen eerst het Datamodel, dan pas de schermen.
3.  **Local AI**: Geen data naar externe Amerikaanse clouds (OpenAI/Anthropic) tenzij expliciet toegestaan.
