# IMS - Rollen en Verantwoordelijkheden

Dit document beschrijft de rollen binnen het IMS en hoe deze technisch vertaald worden naar **Role Based Access Control (RBAC)** in de applicatie.

## 1. Technisch RBAC Model (UserScopeRole)
In het systeem wordt autorisatie geregeld op **Scope** niveau. Iemand kan "Process Owner" zijn van "HR" maar "Viewer" van "IT Infra".

| Implementatie Rol | Rechten | Typische Functie |
| :--- | :--- | :--- |
| **Admin** | Full Control (Create Scopes, Delete data, Manage Users) | CISO, Lead Architect |
| **Process Owner** | **Risk Acceptance**, Update Measures, Approve Exceptions | Lijnmanager, Proceseigenaar |
| **Editor** | Upload Evidence, Edit Controls, manage Incidents | Security Officer, Uitvoerder |
| **Viewer** | Read Only (Dashboard, Reports) | Auditor, Management, Medewerkers |

---

## 2. Functionele Rollen & Taken

### CISO / Control Room
*   **Systeem Rol**: Admin
*   **Taken**:
    *   Beheren van het Model (nieuwe Frameworks/Normenkaders laden).
    *   Monitoren van de "Unified Improvement Backlog".
    *   Goedkeuren van organisatie-breed Beleid (Policy Approval Workflow).

### Proceseigenaar (Line of Business)
*   **Systeem Rol**: Process Owner (op eigen Scope)
*   **Taken**:
    *   **Accepteren** van Restrisico's.
    *   **Accorderen** van Exceptions (Waivers).
    *   Vaststellen van de BIA (Classificatie) van hun assets.

### Uitvoerder / Beheerder
*   **Systeem Rol**: Editor
*   **Taken**:
    *   Implementeren van Maatregelen (Controls).
    *   Aanleveren van Bewijslast (Evidence uploaden).
    *   Afhandelen van Corrective Actions uit Audits/Incidenten.

### Auditor (Intern/Extern)
*   **Systeem Rol**: Viewer
*   **Taken**:
    *   Inzien van de "Click-through Traceability" (Norm -> Risico -> Maatregel -> Bewijs).
    *   Uitvoeren van Audits (Findings loggen).

### AI Assistent
*   **Systeem Rol**: N/A (Tool)
*   **Taken**:
    *   Adviseert mappings tussen normenkaders.
    *   Analyseert bewijslast ("Pre-Audit").
    *   Draft beleidsteksten en incident samenvattingen.
    *   *Let op*: De AI neemt **nooit** besluiten (Risk Acceptance of Policy Approval is altijd menselijk).