# Plan: Superadmin (Platform Admin) Dashboard

Dit document beschrijft het ontwerp voor de speciale **Platform Admin** omgeving. Deze omgeving is alleen toegankelijk voor users met `is_superuser=True` (Layer 0) en staat los van de reguliere Tenant interface.

## 1. Scope & Doel
De Superadmin omgeving dient voor het technisch en commercieel beheer van het SaaS-platform. Hier worden **geen** functionele risico's of maatregelen beheerd (dat gebeurt in de Tenants), maar wel de omgevingen waarin dat gebeurt.

## 2. Navigatie Structuur

De Superadmin krijgt een eigen layout (bijv. donkerpaarse sidebar) om duidelijk onderscheid te maken met de reguliere app.

*   **Overzicht (Dashboard)**: High-level metrics van het platform.
*   **Tenants**: Beheer van organisaties.
*   **Users**: Global user lookup en support.
*   **Instellingen**: Systeem-brede configuratie.
*   **Logs**: Audit logs van het platform zelf (niet de tenants).

---

## 3. Pagina Details

### 3.1 Dashboard (Overzicht)
Een "Mission Control" scherm.
*   **Metrics:**
    *   Totaal aantal Tenants (Active / Trial / Suspended).
    *   Totaal aantal Users (Active Now / Monthly Active).
    *   Systeem Health (Database connecties, AI Service status, Disk usage).
    *   Recente Error logs (500s).

### 3.2 Tenant Management (`/admin/tenants`)
De core business van de Superadmin.
*   **Lijstweergave:** Tabel met alle tenants.
    *   Kolommen: Naam, Type (Gemeente/SSC), Plan, Users, Status, Created At.
    *   Acties: Login As Tenant Admin (Impersonation), Suspend, Delete.
*   **Create Tenant Wizard:**
    *   Stap 1: Organisatie details (Naam, Slug, KvK).
    *   Stap 2: Type (Gemeente, Zorg, SSC) -> bepaalt template settings.
    *   Stap 3: Subscription (Free, Pro, Enterprise) + Limieten (Max Users).
    *   Stap 4: Admin User aanmaken (Invite sturen).
*   **Detail Pagina:**
    *   Tab: **Info** (NAW, Contact).
    *   Tab: **Subscription** (Looptijd, Licentie check).
    *   Tab: **Modules** (Welke features staan aan/uit voor deze tenant? bv. "AI Module", "Shared Services").
    *   Tab: **Usage** (Storage gebruik, API calls).

### 3.3 System Settings (`/admin/settings`)
Beheer van de `SystemSetting` tabel.
*   **AI Configuratie:**
    *   Global Model Selection (bv. "Mistral-Large" vs "Llama-3-70b").
    *   Ollama/vLLM Endpoint URL.
*   **Security:**
    *   Password Policy defaults.
    *   2FA enforcement global switch.
*   **Email (SMTP):**
    *   Mailgun/Sendgrid API keys.
    *   Template beheer.

### 3.4 Shared Services Hub (`/admin/market`)
Een overzicht van wie wat deelt.
*   **Service Matrix:** Welke SSC levert aan welke Gemeenten?
*   **Visualisatie:** Graaf-weergave van tenant relaties.

---

## 4. Technische Implementatie

### 4.1 Backend
*   **Endpoint:** `/api/v1/admin/*`
*   **Security:** `Depends(get_current_active_superuser)`.
*   **Queries:** `db.query(Tenant)` zonder tenant-filter! (Superadmin overstijgt tenant-level filtering).

### 4.2 Frontend (Reflex)
*   **Layout:** Nieuwe `AdminLayout` component (distinctive look).
*   **State:** `AdminState` voor het ophalen van global stats.
*   **Pages:**
    *   `admin_dashboard.py`
    *   `admin_tenants.py`
    *   `admin_settings.py`

## 5. Roadmap
1.  **Fase 1 (MVP):** Tenant Lijst + Create Tenant + System Health.
2.  **Fase 2:** System Settings editor + User Impersonation ("Login as...").
3.  **Fase 3:** Billing integratie (Stripe/Facturatie) + Usage metering.
