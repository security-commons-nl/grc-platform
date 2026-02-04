# IMS - Architectuurprincipes

Dit document beschrijft hoe het **Integrated Management System (IMS)** aansluit op gangbare enterprise architectuurprincipes voor overheidsorganisaties.

---

## 1. Leidende principes (direct ondersteunend)

### Governance van informatievoorziening

**Aansluiting IMS**
- IMS is het **sturings- en governancemodel** voor security, privacy en continuïteit
- Risico's, maatregelen, evidence en besluiten zijn expliciete bestuurlijke objecten
- Eén canoniek IMS-model fungeert als **single source of truth**

**IMS-keuzes**
- Canoniek datamodel leidend
- Expliciete besluitlog (acceptatie restrisico's, prioritering)
- PDCA als structureel besturingsmechanisme

---

### Lifecycle management

**Aansluiting IMS**
- Lifecycle-sturing geldt voor:
  - risico's
  - controls
  - evidence
  - besluiten

**IMS-keuzes**
- Lifecycle-statussen: Draft → Approved → Archived
- Periodieke herbeoordeling (reviewdata verplicht)
- PDCA-cyclus over alle domeinen heen

---

### Data als bedrijfsmiddel

**Aansluiting IMS**
- IMS is een **datagedreven sturingsinstrument**
- Risico-, control- en evidencegegevens zijn strategische assets
- Eigenaarschap, classificatie en kwaliteit zijn expliciet belegd

**IMS-keuzes**
- Canoniek datamodel
- Objecteigenaars per risico/control/proces
- Integratie ISMS (CIA), PIMS (rechten/vrijheden) en BCMS (uitval/herstel)

---

### Gedeelde verantwoordelijkheid

**Aansluiting IMS**
- Eigenaarschap ligt in de lijn; CISO regisseert
- FG en concerncontroller hebben expliciete toetsende rollen
- IMS is geen IT- of securityproject, maar organisatiebreed

**IMS-keuzes**
- Rolverdeling vastgelegd in IMS
- Geen parallelle registers per domein
- Lijnmanagement eigenaar van risico's en maatregelen

---

## 2. Randvoorwaardelijke principes

### IT-voorzieningen integratie

**Aansluiting IMS**
- Gebruik van organisatie IAM-, netwerk- en loggingvoorzieningen
- Identity via Entra ID / Azure AD mogelijk

**Bewuste afbakening**
- Autorisatiemodel ligt in IMS (object- en rolniveau), niet in externe IAM
- Organisatievoorzieningen ondersteunen, maar sturen het IMS niet

---

### Technologiekeuzes

**Aansluiting IMS**
- API-first, modulair en container-based ontwerp
- Cloud-ready (Azure, AWS, of on-premise)

**Bewuste keuzes**
- Geen vendor lock-in in kernlagen
- Open standaarden (SQL, OpenAPI, OAuth2/OIDC)
- Ontwerp is verplaatsbaar naar on-prem of EU-cloud

---

### Platform past bij proces

**Aansluiting IMS**
- IMS ondersteunt een **besturingsproces** met hoog risicoprofiel
- Stabiliteit, traceerbaarheid en auditability zijn belangrijker dan UX

**IMS-keuzes**
- Techniek- en tool-agnostisch ontwerp voor latere migratie
- Audit trail op alle kritieke operaties

---

## 3. Niet-leidende principes

### Dienstverlening & frontoffice principes
- Niet van toepassing op een intern besturings- en governancesysteem

### Open data principes
- IMS-gegevens zijn vertrouwelijk en vaak geclassificeerd
- Openbaarheid is alleen van toepassing op afgeleide rapportages, niet op kernregisters

---

## 4. Samenvatting

> Het IMS-ontwerp sluit aan op architectuurprincipes voor **besturing, datagedreven werken,
> lifecycle-management en gezamenlijke verantwoordelijkheid**. Principes gericht op
> dienstverlening en open data zijn **niet leidend**, omdat het IMS een **intern bestuurlijk
> sturingsinstrument** is en geen dienstverleningsapplicatie.
