# IMS-architectuur — 4 lagen

Dit is het **strakke, eenduidige architectuurmodel** van het Integrated Management System (IMS).  
Geschikt voor gebruik richting **DT, CIO, IV-architecten, FG en auditors**.

Geen tooling-discussie. Geen marketing.  
**Besturing ? regie ? uitvoering ? ondersteuning.**

---

## Laag 1 — Canoniek IMS-model (Besturingslaag)

**Dit ís het IMS.**  
Hier ligt de enige waarheid over risico’s, maatregelen en besluiten.

### Wat zit in deze laag
- **Risico’s (ISMS-kern)**
  - Impact op CIA
  - Kans, score, behandeling, restrisico
- **Maatregelen / controls**
  - Doel, type (prevent/detect/correct)
  - Eigenaar, status
- **Evidence**
  - Wat is “voldoende bewijs”
  - Actualiteit en kwaliteit
- **Besluiten**
  - Acceptatie van restrisico’s
  - Prioritering
  - Afwijkingen
- **Audit & assurance**
  - Bevindingen
  - Follow-up

### Waarom dit de kern is
- Dit is **ISO/BIO in werking**, niet op papier
- **Privacy (PIMS)** en **Continuïteit (BCMS)** zijn **dimensies binnen dit model**
- Er bestaat **geen tweede waarheid**

> Als dit model klopt, kan tooling wisselen zonder impact op governance.

---

## Laag 2 — IMS-logica & API (Regie- en validatielaag)

**Deze laag laat het IMS functioneren als systeem.**  
Zonder deze laag is er alleen registratie, geen sturing.

### Wat doet deze laag
- **Validatie**
  - Is een risico volledig?
  - Mag een control “groen” zijn zonder evidence?
- **Lifecycle**
  - Draft ? reviewed ? approved ? archived
- **Autorisatie**
  - Wie mag wat, op welk object?
- **Audittrail**
  - Wie wijzigde wat, wanneer, waarom?

### Technisch karakter
- Centrale API (REST / GraphQL)
- Rolgebaseerde autorisatie (objectniveau, niet toolniveau)
- Event logging en traceerbaarheid

> Alle tools — ook NARIS — praten via deze laag.

---

## Laag 3 — Executielaag (Tools & workflows)

**Hier gebeurt het werk.**  
Maar deze laag **stuurt niet** en **bepaalt geen waarheid**.

### Voorbeelden
- NARIS (of andere GRC-tool)
- Formulieren
- Workflows en taken
- Dashboards

### Harde randvoorwaarden
- Geen eigen risicomodel
- Geen eigen control-definities
- Geen besluitvorming

### Rol van deze laag
- Gebruiksvriendelijkheid (UX)
- Procesondersteuning
- Datainvoer en -weergave

> Deze laag is **pluggable en vervangbaar**.

---

## Laag 4 — AI & Analyse (Ondersteuningslaag)

**AI denkt mee, maar beslist nooit.**

### Wat AI mag doen
- Suggesties voor risico’s en maatregelen
- Mapping naar normen (BIO / ISO / AVG)
- Samenvatten van rapportages
- Signaleren van afwijkingen en trends

### Wat AI niet mag doen
- Zelfstandig risico’s accepteren
- Controls wijzigen zonder menselijk besluit
- Bestuurlijke besluiten nemen

### Technisch principe
- Overwegend leesrechten
- Beperkte schrijfrechten (conceptvoorstellen)
- Volledige traceerbaarheid en logging

> AI vergroot uitvoeringskracht, niet bestuurlijke macht.

---

## Samenvattend in één zin

> **Het IMS-model stuurt.**  
> **De API bewaakt.**  
> **Tools voeren uit.**  
> **AI ondersteunt.**

---

## Besluitpunten (bestuurlijk vastleggen)
1. Het canonieke IMS-model is de enige waarheid
2. Alle tooling communiceert via de IMS-API
3. De executielaag is vervangbaar
4. AI is adviserend, nooit beslissend

---

## Next steps
- Visuele praatplaat (1 pagina)
- Mapping ISMS–PIMS–BCMS per laag
- Azure-technische uitwerking per laag
