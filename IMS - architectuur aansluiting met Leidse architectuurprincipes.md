# IMS – architectuur aansluiting met Leidse architectuurprincipes

Dit document geeft een **helder en bestuurlijk bruikbaar overzicht** van hoe het ontwerp van het  
**Integrated Management System (IMS)** aansluit op de **Architectuurprincipes Gemeente Leiden (v0.99)**.

Doel:
- legitimeren van IMS-ontwerpkeuzes;
- expliciet maken welke principes **leidend**, **randvoorwaardelijk** of **niet van toepassing** zijn;
- houvast bieden aan DT, CIO, IV-architectuur, FG en audit.

---

## 1. Leidende architectuurprincipes (direct ondersteunend)

Deze principes **onderbouwen expliciet** de gekozen IMS-architectuur.

### C1 – We besturen de informatievoorziening  
**Relevantie: zeer hoog**

**Aansluiting IMS**
- IMS is het **sturings- en governancemodel** voor security, privacy en continuïteit.
- Risico’s, maatregelen, evidence en besluiten zijn expliciete bestuurlijke objecten.
- Eén canoniek IMS-model fungeert als **single source of truth**.

**IMS-keuze**
- Canoniek datamodel leidend
- Expliciete besluitlog (acceptatie restrisico’s, prioritering)
- PDCA als structureel besturingsmechanisme

:contentReference[oaicite:0]{index=0}

---

### C2 – We besturen en beheren de levenscyclus van IT-componenten  
**Relevantie: hoog**

**Aansluiting IMS**
- Lifecycle-sturing is niet beperkt tot IT-componenten, maar geldt ook voor:
  - risico’s
  - controls
  - evidence
  - besluiten

**IMS-keuze**
- Lifecycle-statussen (draft ? approved ? archived)
- Periodieke herbeoordeling (reviewdata verplicht)
- PDCA-cyclus over alle domeinen heen

:contentReference[oaicite:1]{index=1}

---

### D1 – Gegevens zijn een bedrijfsmiddel met waarde  
**Relevantie: zeer hoog**

**Aansluiting IMS**
- IMS is een **datagedreven sturingsinstrument**.
- Risico-, control- en evidencegegevens zijn strategische assets.
- Eigenaarschap, classificatie en kwaliteit zijn expliciet belegd.

**IMS-keuze**
- Canoniek datamodel
- Objecteigenaars per risico/control/proces
- Integratie ISMS (CIA), PIMS (rechten/vrijheden) en BCMS (uitval/herstel)

:contentReference[oaicite:2]{index=2}

---

### I2 – Informatievoorziening is een gemeenschappelijke verantwoordelijkheid  
**Relevantie: hoog**

**Aansluiting IMS**
- Eigenaarschap ligt in de lijn; CISO regisseert.
- FG en concerncontroller hebben expliciete toetsende rollen.
- IMS is geen IT- of securityproject, maar organisatiebreed.

**IMS-keuze**
- Rolverdeling vastgelegd in IMS
- Geen parallelle registers per domein
- Lijnmanagement eigenaar van risico’s en maatregelen

:contentReference[oaicite:3]{index=3}

---

## 2. Randvoorwaardelijke architectuurprincipes (conditionerend)

Deze principes vormen **kaders**, maar zijn **niet inhoudelijk leidend** voor het IMS.

### T1 – Gemeentebrede IT-voorzieningen  
**Relevantie: conditioneel**

**Aansluiting IMS**
- Gebruik van gemeentelijke IAM-, netwerk- en loggingvoorzieningen.
- Identity via Entra ID mogelijk.

**Bewuste afbakening**
- Autorisatiemodel ligt in IMS (object- en rolniveau), niet in Azure.
- Gemeentelijke voorzieningen ondersteunen, maar sturen het IMS niet.

:contentReference[oaicite:4]{index=4}

---

### T2 – Moderne maar bewezen technologie  
**Relevantie: middel-hoog**

**Aansluiting IMS**
- API-first, modulair en container-based ontwerp.
- Azure als huidige landingszone.

**Bewuste keuze**
- Geen vendor lock-in in kernlagen.
- Open standaarden (SQL, OpenAPI, OAuth2/OIDC).
- Ontwerp is verplaatsbaar naar on-prem of EU-cloud.

:contentReference[oaicite:5]{index=5}

---

### T3 – Platform past bij het bedrijfsproces  
**Relevantie: conditioneel**

**Aansluiting IMS**
- IMS ondersteunt een **besturingsproces** met hoog risicoprofiel.
- Stabiliteit, traceerbaarheid en auditability zijn belangrijker dan UX.

**IMS-keuze**
- Azure nu (organisatiebesluit)
- Techniek- en tool-agnostisch ontwerp voor latere migratie

:contentReference[oaicite:6]{index=6}

---

## 3. Niet-leidende architectuurprincipes voor het IMS

Deze principes zijn **bewust niet richtinggevend** voor de IMS-architectuur.

### Bedrijfsarchitectuurprincipes (B1–B5)
- Gericht op dienstverlening, klantinteractie en frontoffice.
- Niet van toepassing op een intern besturings- en governancesysteem.

### D2 – Gegevens zijn open, tenzij
- IMS-gegevens zijn vertrouwelijk en vaak geclassificeerd.
- Openbaarheid is alleen van toepassing op afgeleide rapportages, niet op kernregisters.

---

## 4. Samenvattende conclusie

> Het IMS-ontwerp sluit **volledig en expliciet aan** op de Leidse architectuurprincipes  
> voor **besturing, datagedreven werken, lifecycle-management en gezamenlijke verantwoordelijkheid**.  
> Principes gericht op dienstverlening en open data zijn **niet leidend**, omdat het IMS een  
> **intern bestuurlijk sturingsinstrument** is en geen dienstverleningsapplicatie.

---

## 5. Next steps

Mogelijke vervolgstappen:
1. Mappingtabel *IMS-ontwerpkeuzes ? architectuurprincipes* (compact overzicht)
2. 1-pager voor IV-architectuur en CIO
3. Tekstblok voor DT-besluit: formele verankering in C1, D1 en I2

