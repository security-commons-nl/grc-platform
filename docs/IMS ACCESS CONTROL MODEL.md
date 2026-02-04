# IMS Access Control Model & Governance

Dit document beschrijft het toegangsmodel van het IMS, gebaseerd op het **Drielijnenmodel (Three Lines of Defense)** en ontworpen voor **Multi-Tenant (Meerdere Organisaties)** gebruik.

## 1. Governance Structuur: 3 Lines of Defense

Het model vertaalt organisatorische verantwoordelijkheden direct naar systeemrollen.

| Lijn | Organisatie Functie | Verantwoordelijkheid | Systeem Rol & Scope |
| :--- | :--- | :--- | :--- |
| **1e Lijn** | **Operatie**<br>(Proceseigenaar, Lijnmanager) | Eigenaar van risico's en beheersmaatregelen. Voert uit. | **Process Owner**<br>*Op specifieke Scopes (bv. "HR", "Inkoop")* |
| **2e Lijn** | **Control / GRC**<br>(CISO, PO, Security Officer) | Stelt kaders, ondersteunt, monitort en daagt uit. Beheert het beleid. | **Admin** / **Editor** / **Risk Owner**<br>*Organisatiebreed (Global Scope)* |
| **3e Lijn** | **Audit**<br>(Interne/Externe Audit) | Geeft onafhankelijke zekerheid (Assurance). Toetst werking. | **Viewer** (Read-only)<br>*Organisatiebreed, incl. audit trails* |

---

## 2. Multi-Tenant Structuur (Meerdere Organisaties)

Het systeem ondersteunt meerdere organisaties (Tenants) die volledig van elkaar gescheiden zijn, maar wel kunnen samenwerken (bijv. in een Shared Service Center constructie).

### Hiërarchie
1.  **Platform**: De gehele applicatie instance (SaaS niveau).
2.  **Tenant**: Een logische organisatie (bijv. "Gemeente Amsterdam", "Zorginstelling X"). Data is hier strikt gescheiden.
3.  **Scope**: Een functioneel gebied binnen een Tenant (bijv. "Afdeling Financiën", "Systeem Y").

### Samenwerking (Cross-Tenant)
Via **Tenant Relationships** kunnen organisaties samenwerken:
*   **Shared Service Center (SSC)**: Een SSC-tenant levert diensten (bv. "Werkplekbeheer") aan afnemende tenants.
*   **Federatie**: Organisaties delen specifieke Kennis of Benchmarks zonder dat ze bij elkaars operationele data kunnen.

---

## 3. Toegangsmodel (Technisch)

Toegang wordt bepaald door drie lagen. Een gebruiker moet door alle lagen heen om een actie uit te voeren.

### Laag 0: Platform Admin (Superuser)
Boven de tenants staat de **Platform Admin**.
*   **Rol:** `is_superuser = True` (in User model).
*   **Verantwoordelijkheid:**
    *   Aanmaken van nieuwe Tenants.
    *   Systeem-brede configuratie (bv. AI model selectie).
    *   Technische monitoring van het platform.
*   **Beperking:** Heeft *geen* toegang tot functionele data binnen tenants, tenzij expliciet toegevoegd als lid.

### Laag 1: Tenant Membership ("Het Gebouw")
Bepaalt of een gebruiker überhaupt lid is van de organisatie.
*   **Tenant Owner**: Eigenaar van de 'omgeving'. Kan billing en partnerships beheren.
*   **Tenant Admin**: Kan gebruikers uitnodigen en accounts beheren.
*   **Tenant Member**: Gewone gebruiker.

### Laag 2: Scope Assignment ("De Kamer")
Bepaalt bij welk proces of afdeling een gebruiker hoort. Een gebruiker heeft **geen** toegang tot data tenzij expliciet toegewezen aan een Scope (of Global Admin is).
*   *Voorbeeld*: Jan is lid van "Gemeente X" (Layer 1) en toegewezen aan scope "Burgerzaken" (Layer 2). Hij ziet **niets** van "Openbare Orde".

### Laag 3: Functional Role ("De Rol")
Bepaalt wat de gebruiker mag *doen*.

**Principe: Vertrouwen vs. Segmentatie**
*   **2e Lijn (Vertrouwen):** Krijgt een **Global Role** (op Tenant niveau, geen specifieke Scope). Zij zien *alles* binnen de organisatie. Dit houdt het beheer simpel.
*   **1e Lijn (Segmentatie):** Krijgt een **Scoped Role** (gekoppeld aan specifieke Scopes zoals "Cluster Bedrijfsvoering"). Zij zien *alleen* hun eigen gebied.

| Rol | Type | Rechten Profiel |
| :--- | :--- | :--- |
| **Viewer** | Global (vaak) | Alleen lezen. Kan niets wijzigen. (Voor Stakeholders/Management) |
| **Auditor** | Global | Kan "Findings" en "Assessment Responses" schrijven, verder read-only. (Voor 3e lijn) |
| **Editor** | **Scoped** | Kan bewijs uploaden, **Control** status bijwerken binnen eigen Scope. (1e lijn Uitvoerders) |
| **Risk Owner** | Global | Kan risico's accepteren, mitigeren. Ziet hele organisatie. (2e lijn Risk Officers) |
| **Process Owner** | **Scoped** | Volledig beheer over de eigen Scope/Afdeling. Eigenaar van de **Controls**. (1e lijn Managers) |
| **Admin** | Global | God-mode binnen de Tenant. Beheert de **Measures** (Normen). |

---

## 4. Scenario's uit de Praktijk

### Scenario A: De CISO (2e Lijn)
*   **Rol**: Tenant Admin & Risk Owner (Global).
*   **Bevoegdheid**: Kan alle risico's zien, framework beheren, beleid publiceren.
*   **Beperking**: Kan *meestal* geen operationele taken (zoals bewijs uploaden) "faken", dit moet de 1e lijn doen (functiescheiding).

### Scenario B: De Afdelingsmanager (1e Lijn)
*   **Rol**: Process Owner op Scope "Financiën".
*   **Bevoegdheid**: Ziet alleen Financiën. Kan risico's accepteren voor zijn afdeling.
*   **Beperking**: Ziet niets van HR of IT. Kan geen beleid aanpassen.

### Scenario C: De Externe Auditor (3e Lijn)
*   **Rol**: Viewer (Global).
*   **Bevoegdheid**: Kan alles inzien, incl. "deleted" items (audit trail).
*   **Beperking**: Read-only. Krijgt een account met einddatum.

### Scenario D: Shared Service Provider (SSC)
*   **Situatie**: ICT-leverancier levert "Hosting" aan "Gemeente A".
*   **Inrichting**:
    1.  SSC heeft eigen Tenant met scope "Hosting Dienst".
    2.  SSC "deelt" deze scope met Gemeente A (via SharedScope).
    3.  Gemeente A ziet "Hosting Dienst" als black-box (of white-box, afhankelijk van contract).
    4.  Gemeente A koppelt hun risico's aan de gedeelde scope van het SSC.

## 5. Functionele Domein Rollen (Specialisten)

Naast de generieke lijnen, kent het model specifieke invullingen voor vakgebieden. Deze vallen technisch meestal in de **2e Lijn** (Global Scope).

### 5.1 Privacy Team (Privacy Officer / FG)
*   **Rol:** Global **Risk Owner** + Global **Auditor**.
*   **Verantwoordelijkheid:**
    *   Beheert het **Privacy Framework** (AVG Normenkader).
    *   Monitort de **Verwerkingsregisters** (die door Process Owners worden gevuld).
    *   Voert de regie op **DPIA's** en **Datalekken**.
*   **Toegangsbehoefte:** Moet *alles* kunnen zien (ook gevoelige data in verwerkingen), maar mag operationele processen niet verstoren.

### 5.2 BCM Manager (Business Continuity)
*   **Rol:** Global **Viewer** + **Editor** op "BCM Scope".
*   **Verantwoordelijkheid:**
    *   Faciliteert **BIA's** (Business Impact Analyses) voor Scopes.
    *   Beheert de centrale **Continuïteitsplannen** (Calamiteitenplan, Crisisplan).
    *   Organiseert en logt **Oefeningen/Tests**.
*   **Toegangsbehoefte:** Inzicht in de kritiekheid (BIA) van alle assets/scopes.
