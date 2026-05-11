# IMS-proces — Backlog

Ideeën en toekomstig werk dat nu bewust wordt geparkeerd. Geen prioritering — dat volgt later.

Module-tags verwijzen naar [`docs/modules.md`](../docs/modules.md).

---

## Inhoud

| # | Module | Item | Context |
|---|--------|------|---------|
| 1 | **M3** | **Standaard awareness-materiaal** | Generieke templates voor onboarding lijnmanagement (stap 7). Per domein: ISMS (BIO-bewustzijn), PIMS (AVG-bewustzijn), BCMS (gedrag bij verstoring). Pas uitwerken als de stap-structuur en doelgroepen definitief zijn. |
| 2 | **M2** | **Informatiepositie burgemeester bij incidenten** | VNG-brief (maart 2026) signaleert dat de burgemeester wettelijk geïnformeerd moet worden bij digitale crises. Verwerken in de incidentmanagementprocedure (niveau 2, stap 15). Wachten op definitieve Wwke-tekst. |
| 3 | **M0 / M2 / M3** | **Platform architectuur & datamodel** | Geïntegreerd platform (inrichtingsmodus + beheermodus) vereist zorgvuldig datamodel. Apart uitwerken. Kernprincipe: simpel voor de gebruiker. |
| 4 | **M0** | **Export als platform-breed principe** | Besluitlog, handboek, risicoregister, SoA, auditrapportages — alles moet exporteerbaar zijn als PDF/Word. Dit is geen feature per module maar een platform-brede eis. Uitwerken bij architectuur. |
| 5 | **M1** | **Normversioning (Standard + RequirementMapping)** | BIO 2.0 → BIO 3.0 en ISO-revisies zullen komen. Voeg `norm_version` toe aan Standard/Requirement-entiteiten. RequirementMapping moet verwijzen naar specifieke normversie. Migratiewizard voor normupdate. Architectuurkeuze vastleggen vóór bouw datamodel. |
| 6 | **M3** | **IP-adres verwijderen uit besluitlog** | IP-adres is persoonsgegeven (AVG). Opslaan vereist grondslag + retentiebeleid. Shared IP's (NAT/VPN) maken het ook onbetrouwbaar als identificator. Vervangen door interne session_id of weglaten. Onderzoek ook of hoge-drempel risicobesluiten formele mandatering/eHerkenning vereisen. |
| 7 | **M3** | **Fase-overgangscriteriadefiniëren** | Wanneer gaat een gemeente van Fase 0 → 1 → 2 → 3? Per overgang: welke stappen afgerond (status = vastgesteld), welk gremium accordeert, welke besluitlog-entry. Voorkomt dat "IMS is ingericht" te vaag blijft. |
| 8 | **M0** | **eHerkenning-integratie voor formele risicobesluiten** | Sommige gemeentelijke procuratiereglementen vereisen meer dan naam+functie bij hoge-drempel besluiten. Onderzoek of en wanneer digitale handtekening (PKI of eHerkenning) noodzakelijk is. |
| 9 | **M2** | **Berekeningsmodel GRC-score** | De GRC-score (Fase 2+) is data-gedreven maar vereist een wegingsmodel: hoeveel telt een afgeronde audit mee vs. actuele evidence vs. open bevindingen vs. managementreview? Inhoudelijk werk — moet gereed zijn vóór Fase 2-bouw. |
