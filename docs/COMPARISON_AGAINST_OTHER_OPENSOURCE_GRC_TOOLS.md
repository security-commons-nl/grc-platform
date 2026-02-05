# Vergelijking Open Source GRC Tools

Dit document biedt een high-level vergelijking tussen het **IMS** (Integrated Management System - deze repository) en twee prominente open-source alternatieven: **Gapps** en **CISO Assistant Community**.

De vergelijking richt zich op functionaliteit, architectuur, AI-integratie en inzetbaarheid.

## 1. Executive Summary

| Tool | Kernfilosofie | Tech Stack | AI Integratie | Geschikt voor |
| :--- | :--- | :--- | :--- | :--- |
| **IMS (Deze Repo)** | **"AI First" & Data Souvereiniteit.** Volledige integratie van lokale AI in elk proces. Strikte scheiding van lagen. | Python, FastAPI, SQLModel (Async) | **Diepgaand:** AI-velden in datamodel, RAG-kennisbank, Local LLM focus (Mistral). | Organisaties die controle, AI-automatisering en Shared Services nodig hebben (bv. Overheid/SSC's). |
| **CISO Assistant** | **"Decoupling & Content".** Enorme bibliotheek aan frameworks (100+). Compliance losgekoppeld van controls. | Python, Django | **Assistent:** AI als hulpmiddel/chatbot, minder diep verankerd in het datamodel. | Brede groep gebruikers die snel willen starten met specifieke frameworks. |
| **Gapps** | **"Audit Ready".** Focus op het behalen van certificeringen (SOC2, ISO) en samenwerking met auditors. | Python, Flask | **Beperkt:** Focus ligt meer op traditionele registratie en workflow. | Bedrijven die zich voorbereiden op audits zoals SOC2/ISO27001. |

---

## 2. Diepte-analyse

### A. IMS (Integrated Management System)
*Deze repository.*

**Sterke Punten (USP's):**
*   **AI in de kern:** AI is geen "add-on" maar zit in het DNA. Het datamodel bevat velden als `ai_confidence`, `ai_generated`, en `ai_suggested_quadrant`. Dit maakt autonome verwerking (bv. risico-analyse, beleid schrijven) mogelijk.
*   **Lokale AI (Privacy):** Ontworpen voor Local AI (Ollama/Mistral), waardoor gevoelige data de organisatie niet verlaat. Essentieel voor BIO/AVG-compliance.
*   **Shared Services (Multi-tenancy):** Unieke ondersteuning voor 'Providers' en 'Consumers' (bijv. een SSC die IT levert aan gemeenten). Controls en Scopes kunnen gedeeld worden.
*   **Volledige Scope:** Ondersteunt expliciet ISMS (Security), PIMS (Privacy/AVG) en BCMS (Bedrijfscontinuïteit) in één model.

**Overwegingen:**
*   **Complexiteit:** De architectuur (4 lagen) en het uitgebreide datamodel vragen om een investering in begrip bij developers.
*   **Maturiteit:** Is in actieve ontwikkeling met focus op architecturale zuiverheid.

### B. CISO Assistant (Intuitem)
*Community Edition.*

**Sterke Punten (USP's):**
*   **Enorme Content Library:** Ondersteunt out-of-the-box 100+ frameworks (NIST, ISO, CIS, etc.).
*   **Decoupling Concept:** Slimme scheiding tussen "Wat moet ik doen?" (Compliance) en "Hoe doe ik het?" (Controls). Hierdoor kun je één control mappen op meerdere normen (test 1x, voldoe aan velen).
*   **Community:** Grote userbase en actieve community.

**Overwegingen:**
*   **Django Monolith:** Gebruikt een meer traditionele Django-architectuur. Bewezen, maar minder flexibel voor moderne async/AI-toepassingen dan FastAPI.
*   **AI als Feature:** AI wordt toegevoegd, maar is minder fundamenteel onderdeel van de datastructuur dan bij IMS.

### C. Gapps (Bmarsh9)
*Compliance platform.*

**Sterke Punten (USP's):**
*   **Focus op Certificering:** Sterk gericht op het proces van auditen (SOC2, ISO27001).
*   **Eenvoud:** Flask-gebaseerd, lichter van opzet. Makkelijk te begrijpen voor Python developers.
*   **Auditor Portal:** Specifieke features om auditors toegang te geven.

**Overwegingen:**
*   **Feature Set:** Minder breed dan IMS (minder focus op PIMS/BCMS of Shared Services).
*   **Architectuur:** Eenvoudiger, maar minder schaalbaar voor complexe enterprise-scenario's (zoals multi-layer tenancy).

---

## 3. Functionele Vergelijking Matrix

| Feature | IMS | CISO Assistant | Gapps |
| :--- | :---: | :---: | :---: |
| **ISMS (Security)** | ✅ | ✅ | ✅ |
| **PIMS (Privacy/AVG)** | ✅ (Diepgaand: Verwerkingsreg., DSR) | ✅ (Via frameworks) | ⚠️ (Beperkter) |
| **BCMS (Continuïteit)** | ✅ (Plannen & Tests) | ✅ (Via frameworks) | ❌ |
| **Multi-tenancy** | ✅ (Incl. Shared Services) | ✅ | ✅ |
| **Framework Mapping** | ✅ (AI-ondersteund) | ✅ (Smart Mapping) | ✅ |
| **Risico Management** | ✅ (In Control Model) | ✅ | ✅ |
| **AI Automatisering** | ✅✅ (Core Design) | ✅ (Assistant) | ❌ |
| **Tech Stack** | Modern (FastAPI, SQLModel) | Bewezen (Django) | Lichtgewicht (Flask) |

## 4. Conclusie

*   Kies voor **CISO Assistant** als je **direct** aan de slag wilt met een breed scala aan internationale frameworks en steunt op een grote community.
*   Kies voor **Gapps** als je een **lichtgewicht** tool zoekt puur om een SOC2/ISO audit te managen.
*   Kies voor **IMS** als je:
    *   Gelooft in **AI als kern** van je administratie (minder handwerk).
    *   **Data Souvereiniteit** eist (Lokale AI).
    *   Werkt in een complexe structuur (bijv. Overheid, Holding, SSC) waar **Shared Services** cruciaal zijn.
    *   Een moderne, toekomstbestendige architectuur zoekt (FastAPI/Async).
