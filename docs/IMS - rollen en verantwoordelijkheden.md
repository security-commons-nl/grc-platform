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

---

## 3. Drielijnenmodel (Three Lines of Defense)

Het platform ondersteunt het drielijnenmodel voor governance. Dit bepaalt welke functionaliteiten beschikbaar zijn per lijn.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DERDELIJN - Audit & Toezicht                                               │
│  Interne audit, externe auditors, toezichthouders                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  TWEEDELIJN - GRC Specialisten                                              │
│  CISO, Privacy Officer, Security Officers, Compliance Officers              │
├─────────────────────────────────────────────────────────────────────────────┤
│  EERSTELIJN - Operatie                                                      │
│  Proceseigenaren, lijnmanagers, teamleads, uitvoerenden                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Eerstelijn (Operatie)
**Wie**: Proceseigenaren, lijnmanagers, medewerkers

**Toegang tot:**
| Module | Rechten |
|--------|---------|
| Dashboard | Eigen scope(s) bekijken |
| Risico's | Eigen risico's beheren, kans/impact inschatten |
| Maatregelen | Eigen maatregelen beheren, evidence uploaden |
| Assessments | Self-assessments invullen |
| Incidenten | Melden en eigen incidenten volgen |
| Scopes | Eigen scope informatie bijwerken (BIA, eigenaar) |

**Geen toegang tot:**
- Framework beheer
- Requirement mappings
- Organisatie-breed beleid opstellen
- Andere scopes (tenzij gedeeld)

---

### Tweedelijn (GRC Specialisten)
**Wie**: CISO, Privacy Officer, Security Officers, Risk Managers, Compliance Officers

**Toegang tot:**
| Module | Rechten |
|--------|---------|
| **Frameworks** | Standaarden beheren (ISO 27001, BIO, AVG) |
| **Requirements** | Eisen per framework beheren |
| **Mappings** | Rosetta Stone - cross-framework mappings beheren |
| **Beleid** | Organisatie-breed beleid opstellen en publiceren |
| **Templates** | Risico- en maatregelentemplates beheren |
| Dashboard | Organisatie-breed overzicht |
| Risico's | Alle risico's inzien, templates toewijzen |
| Maatregelen | Alle maatregelen inzien, effectiviteit monitoren |
| Assessments | Assessments plannen en toewijzen |
| Rapportages | Management rapportages genereren |

**Kernverantwoordelijkheden:**
- Normenkaders up-to-date houden
- Mappings tussen frameworks onderhouden (evt. met AI-ondersteuning)
- Risicoregister bewaken
- Compliance status monitoren
- Eerstelijn ondersteunen en adviseren

---

### Derdelijn (Audit & Toezicht)
**Wie**: Interne auditors, externe auditors, toezichthouders

**Toegang tot:**
| Module | Rechten |
|--------|---------|
| Dashboard | Volledige read-only toegang |
| Risico's | Inzien (geen wijzigingen) |
| Maatregelen | Inzien incl. evidence |
| Assessments | Audits uitvoeren, findings vastleggen |
| Rapportages | Audit trails, compliance rapportages |
| Traceability | Click-through: Norm → Risico → Maatregel → Bewijs |

**Geen toegang tot:**
- Wijzigen van data (read-only)
- Framework beheer (wel inzien)
- Beleid wijzigen (wel inzien)

**Kernverantwoordelijkheden:**
- Onafhankelijke toetsing
- Findings rapporteren
- Aanbevelingen doen (via Corrective Actions)

---

## 4. Platform Modules per Lijn

| Module | Eerstelijn | Tweedelijn | Derdelijn |
|--------|:----------:|:----------:|:---------:|
| Dashboard | ✓ (eigen) | ✓ (alles) | ✓ (read) |
| Risico's | ✓ (eigen) | ✓ (alles) | 👁 (read) |
| Maatregelen | ✓ (eigen) | ✓ (alles) | 👁 (read) |
| Scopes | ✓ (eigen) | ✓ (alles) | 👁 (read) |
| Assessments | ✓ (invullen) | ✓ (plannen) | ✓ (auditen) |
| Incidenten | ✓ (melden) | ✓ (beheren) | 👁 (read) |
| Beleid | 👁 (lezen) | ✓ (beheren) | 👁 (read) |
| **Frameworks** | ❌ | ✓ | 👁 (read) |
| **Requirements** | ❌ | ✓ | 👁 (read) |
| **Mappings** | ❌ | ✓ | 👁 (read) |
| **Templates** | ❌ | ✓ | 👁 (read) |
| Rapportages | ✓ (eigen) | ✓ (alles) | ✓ (audit) |
| Gebruikersbeheer | ❌ | ✓ (Admin) | ❌ |

**Legenda:** ✓ = Volledige toegang | 👁 = Read-only | ❌ = Geen toegang