# Analyse: Access Control Model vs. System Design & Context

## 1. Conclusie
Het voorgestelde **Access Control Model** is **volledig in lijn** met zowel de `README.md` (Design Principles) als de `COMPLETE_DESIGN_OVERVIEW.md` (Visie & Architectuur). Sterker nog: de recente wijziging van het datamodel (`Measure` vs `Control`) versterkt dit model aanzienlijk door een heldere scheiding tussen "Norm" en "Uitvoering" aan te brengen.

## 2. Alignment Check: Design Principles

| Design Principe | Access Control Model Implementatie | Status |
| :--- | :--- | :--- |
| **"The Model leads"** | Toegang wordt niet bepaald door UI, maar door harde data-relaties: `Tenant` -> `Scope` -> `Role`. | ✅ |
| **Strict Separation** | RBAC zit in Laag 2 (API) en werkt o.b.v. Scopes. Een gebruiker ziet *niets* buiten zijn toegewezen Scope. | ✅ |
| **Separation of Concerns** | De scheiding tussen **1e Lijn** (Uitvoering) en **2e Lijn** (Kaderstelling) wordt 1-op-1 vertaald naar **Scope Roles** (Process Owner) vs. **Global Roles** (Risk Owner/Admin). | ✅ |
| **Multi-Tenancy** | Het model erkent expliciet dat gebruikers in meerdere tenants kunnen zitten (via `TenantUser`), essentieel voor Shared Services. | ✅ |

## 3. Impact Analyse: Datamodel Refactor (`Measure` -> `Control`)

Je hebt recent het datamodel aangepast:
*   **Oud:** `MeasureTemplate` (Catalogus) en `Measure` (Implementatie).
*   **Nieuw:** `Measure` (De Norm/Eis) en `Control` (De daadwerkelijke Implementatie).

### Waarom dit cruciaal is voor het Toegangsmodel:
Deze wijziging maakt de **Governance** veel scherper:

1.  **2e Lijn (CISO/Policy):**
    *   **Beheert de `Measure` (De Norm).**
    *   *Rol:* `Editor` of `Admin` op Global niveau.
    *   *Actie:* "Wij stellen vast dat *MFA verplicht is* (Measure)."
    *   *Toegang:* Schrijfrechten op `Measures`, leesrechten op `Controls`.

2.  **1e Lijn (DevOps/ beheer):**
    *   **Beheert de `Control` (De Implementatie).**
    *   *Rol:* `Process Owner` of `Editor` op Scope niveau.
    *   *Actie:* "Wij implementeren *YubiKeys* (Control) om aan de MFA-eis te voldoen."
    *   *Toegang:* Schrijfrechten op `Controls`, alleen leesrechten op `Measures`.

**Conclusie**: De naamswijziging lost een vorig conflict op waarbij onduidelijk was wie de "Measure" mocht aanpassen. Nu is het helder: CISO beheert de Eis (`Measure`), Operatie beheert de Oplossing (`Control`).

## 4. Aandachtspunten & Risico's

### 4.1 "Shared Services" Complexiteit
Het model beschrijft Shared Services (SSC), waarbij een SSC-tenant diensten levert aan afnemers.
*   **Risico**: Als een SSC een `Control` deelt (bv. "Centrale Firewall"), wie is dan verantwoordelijk voor het *testen* (effectiveness)?
*   **Oplossing in Model**: De SSC (Provider) blijft eigenaar van de `Control` en voert de tests uit. De Afnemer (Consumer) "linkt" naar deze `Control` en erft de effectiviteit, maar kan deze niet wijzigen (Read-only via `SharedMeasure`/`SharedScope`).

### 4.2 De "Viewer" Rol (3e Lijn Audit)
Het model definieert een `Viewer` rol.
*   **Check**: De `COMPLETE_DESIGN_OVERVIEW.md` stelt dat Auditors ook "Findings" moeten kunnen loggen.
*   **Correctie**: Een pure `Viewer` (alleen lezen) is voor een Auditor soms te beperkt.
*   **Advies**: Introduceer een specifieke **`Auditor`** rol (of scope-specifieke permissie) die *wel* Findings en AssessmentResponses mag schrijven, maar *geen* aanpassingen mag doen aan Risks of Controls.

## 5. Eindoordeel

Het Access Control Model is robuust, schaalbaar en juridisch/compliance-technisch correct (functiescheiding). De datamodel-wijziging was de "missing link" om de scheiding tussen Kaders (2e lijn) en Uitvoering (1e lijn) ook technisch af te dwingen.

**Implementatie Advies:**
Focus nu op de technische migratie (`measures` -> `controls` rename) in de backend en frontend, want de conceptuele basis staat als een huis.
