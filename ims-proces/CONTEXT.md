# IMS-proces — Gesprekscontext & Ontwerprichtingen

*Bijgehouden zodat een volgend LLM-gesprek direct kan doorpakken.*
*Laatst bijgewerkt: 2026-03-13*

---

## Wat is dit project?

`IMS-proces` is een **implementatiemethodologie + procesbegeleiding platform** voor het inrichten van een Integrated Management System (ISMS/PIMS/BCMS) bij gemeenten.

Het is een **zusterrepo** van `IMS-tooling` (de GRC-machine). Samen vormen ze één platform dat meegroeit met de gemeente.

---

## Het kernidee

Het platform heeft **twee modi die in elkaar overlopen**:

1. **Inrichtingsmodus** (IMS-proces) — begeleidt een gemeente stap voor stap door het IMS-implementatietraject. Elke stap levert een concreet document op (besluitlog, handboek, registers, domeinspecifieke docs). AI agents ondersteunen bij het opstellen van die documenten.

2. **Beheermodus** (IMS-tooling) — de GRC-machine draait: risico's, controls, assessments, PDCA-cyclus.

De inrichtingsmodus *is* de configuratie van de beheermodus. Data die tijdens onboarding wordt ingevoerd (governance, scope, registers) vloeit direct door naar de GRC-tool. Geen synchronisatie, één waarheid.

---

## Doelstelling

### Nu (Gemeente Leiden, 2026)
- Ondersteunt het TIMS en de discipline-eigenaren (Regiegroep) bij het inrichten van het IMS
- Nog geen risicobeheer voor lijnmanagement — dat komt in Fase 1

### Later (generiek product)
- Elke stap die Gemeente Leiden doorloopt wordt gedocumenteerd als **blauwdruk**
- Een andere gemeente kan die reis letterlijk herhalen via het platform
- Het platform *weet* in welke fase een organisatie zit en toont alleen wat relevant is

---

## Primaire gebruikers (nu)
- **TIMS / Regiegroep**: Concerncontroller, CIO, CARM, BCM Manager, IB&P Manager
- **3e lijn (toezicht, niet in TIMS)**: CISO, FG, Interne Accountant
- Niet het lijnmanagement (dat komt in Fase 1)

---

## Fasering platform

```
Fase 0 (Q1-Q2 2026)  → Bouwplaats: TIMS richt het IMS in
Fase 1 (Q3 2026)     → Werktool: lijnmanagement doet risicoanalyse
Fase 2 (Q1 2027)     → Beheertool: PDCA draait, controls, evidence
Fase 3 (2028+)       → Volwassen GRC-platform
```

Elke fase heeft een **formeel eindpunt** (go/no-go besluit) voordat de volgende fase begint.

---

## Stap-patroon (geldt voor elke processtap)

```
Input verzamelen (gebruiker vult in)
    → AI agent genereert concept-document
    → Bevoegd gremium reviewt en accordeert
    → Output vastgelegd (besluitlog / handboek / register)
    → Volgende stap ontgrendeld
```

### Stappen overslaan
Stappen zijn niet hard geblokkeerd. Als een gemeente een stap overslaat:
- Expliciete waarschuwing: "zonder deze context kunnen vervolgstappen minder helder zijn"
- Bewuste keuze wordt vastgelegd (wie, wanneer, waarom)
- Traceerbaar in het systeem — "onbekend is bestuurlijke informatie"

---

## Documentatiefamilie (output van het proces)

### Generiek (skelet voor elke gemeente)
- **IMS Handboek** — organisatiecontext, governance, PDCA-structuur, escalatiemodel
- **Besluitlog** — alle formele besluiten

### Domeinspecifiek (per systeem eigen uitwerking)
- **ISMS-documentatie** — BIO-normenkader, risicoanalyse IB, ICF
- **PIMS-documentatie** — Register van Verwerkingen, DPIA-procedure, AVG-verplichtingen
- **BCMS-documentatie** — BIA, kritische processen, continuïteitsplannen

AI agents genereren deze documenten op basis van wat de gemeente tijdens het proces heeft ingevuld.

---

## Stappenvolgorde (in opbouw — wordt aangevuld)

### Fase 0 — Fundament

| # | Stap | Output | Gremium | Status |
|---|------|--------|---------|--------|
| 1 | Bestuurlijk commitment | Besluitmemo + besluitlog #001 | SIMS | Vastgesteld |
| 2a | Organisatiecontext vaststellen | Organisatiecontextdocument + stakeholderregister + PII-rol (sectie IMS Handboek) | TIMS | Vastgesteld |
| 2b | Scope bepalen | Formeel scopebesluit (besluitlog) | SIMS | Vastgesteld |
| 3a | Governance- en beleidsvoorstel opstellen | Concept governance + concept IMS-beleid + communicatiematrix | TIMS | Vastgesteld |
| 3b | Governance en beleid vaststellen | Formeel governance-besluit + IMS-beleid + besluitlog | SIMS | Vastgesteld |
| 4 | Gap-analyse | Nulmeting per domein + besluitlog | TIMS | Vastgesteld |
| 5 | Registers & risicobeoordeling | Registerinventarisatie + eerste risicobeeld + risicobeoordelingsmethodiek | TIMS | Vastgesteld |
| 6 | Normenkader & kerncontrols | Normenkader + minimale werkset kerncontrols + besluitlog | SIMS | Vastgesteld |

### Fase 1 — Lijnmanagement doet risicoanalyse

| # | Stap | Output | Gremium | Status |
|---|------|--------|---------|--------|
| 7 | Onboarding & awareness lijnmanagement | Awareness-materiaal + competentiebeoordeling + documentbeheerprocedure | TIMS | Vastgesteld |
| 8 | Koppeling processen, systemen & verwerkingen | Geïntegreerd register (proces → systeem → verwerking) + PII-doorgifte-inventarisatie (PIMS-track) + privacy-by-design procedure | TIMS + lijnmanagement | Vastgesteld |
| 9 | Risicoanalyse door lijnmanagement | Risicoregister per afdeling/proces + BIA (BCMS-track) | Lijnmanagement | Vastgesteld |
| 10 | Risicobehandeling & controls toewijzen | Risicobehandelplan + controls met eigenaren + implementatieplan + continuïteitsstrategieën + business continuity plans (BCMS-track) + PII-doorgifte-waarborgen (PIMS-track) | TIMS | Vastgesteld |
| 11 | Statement of Applicability (SoA) | SoA-document incl. ISO 27701 Annex A/B (gegenereerd of handmatig) | SIMS | Vastgesteld |
| 12 | Monitoring & rapportage inrichten | KPI's + rapportagelijnen + dashboards | TIMS | Vastgesteld |

### Fase 2 — PDCA draait, controls, evidence

| # | Stap | Output | Gremium | Status |
|---|------|--------|---------|--------|
| 13 | Interne audit plannen & uitvoeren | Auditprogramma + auditrapportages + BC-oefenrapportage (BCMS-track) | TIMS | Vastgesteld |
| 14 | Management review | Review-rapportage (verplichte inputchecklist ISO 9.3.2) + verbeterbeslissingen | SIMS | Vastgesteld |
| 15 | Afwijkingen, incidenten & corrigerende maatregelen | Non-conformiteitenregister + incidentmanagement + correctieve acties | TIMS | Vastgesteld |
| 16 | Evidence-verzameling & control-monitoring | Bewijs per control + continue monitoring + privacy-procedures (PIMS-track) | Lijnmanagement | Vastgesteld |
| 17 | PDCA-cyclus formaliseren | Jaarplanning + reviewcyclus + periodieke risicoherbeoordeling + communicatieprocedures + verbeterdoelen | SIMS | Vastgesteld |

*Fase 2 is cyclisch, niet lineair. Deze stappen herhalen zich. Het platform schakelt hier van inrichtingsmodus (IMS-proces) naar beheermodus (IMS-tooling).*

### Fase 3 — Volwassen GRC-platform (optioneel)

| # | Stap | Output | Gremium | Status |
|---|------|--------|---------|--------|
| 18 | Certificeringsgereedheid | Pre-audit rapport + gap-remediatie + certificeringsaanvraag | SIMS | Vastgesteld |
| 19 | Geavanceerde analytics & rapportage | Trendanalyses + predictive risk + geautomatiseerde rapportages | TIMS | Vastgesteld |
| 20 | Externe integraties | Ketenpartner-koppelingen + leveranciersportaal + data-uitwisseling | TIMS | Vastgesteld |
| 21 | Multi-framework optimalisatie | Cross-mapping controls naar meerdere normen + duplicatie-eliminatie | TIMS | Vastgesteld |
| 22 | Benchmarking & kennisdeling | Benchmark-rapportage + best practice bibliotheek | SIMS | Vastgesteld |

*Fase 3 is volledig optioneel. Er is geen go/no-go — de gemeente kiest per onderdeel of en wanneer het relevant wordt. Fase 2 (PDCA draait) is het minimale eindplaatje. Fase 3 is het ambitieplaatje.*

---

## Vastgestelde ontwerpbeslissingen

### Scope (stap 2)
Scope is één fase met twee deliverables. Context bepaalt scope (ISO 27001 4.1→4.3), maar scope krijgt eigen formeel besluitmoment omdat het politiek geladen is en mensen er later op worden afgerekend.

### AI-ondersteuning per stap
Uitgewerkt per fase — zie AI agents Fase 0, Fase 1 en Fase 3 secties.

### "Builders" als gremium
Vervallen. Oud concept. Niet opnemen in het generieke model.

### Governance-naamgeving
Meteen permanent: **SIMS en TIMS** vanaf dag één. Geen tijdelijke namen, geen latere transitie.

### Registers & risicobeoordeling (stap 5)
Optie A (registers eerst) is niet reëel — perfectionism trap. Keuze tussen:
- **Optie B**: risicobeoordeling eerst, registers volgen
- **Optie C**: parallel en iteratief, expliciet onvolledig

Volwassenheidscheck via vragen (generiek, niet tool-specifiek):
- Zijn er al (gedeeltelijke) registers beschikbaar? Voorbeelden per domein:
  - **ISMS**: applicatie-/systeemregister (CMDB), leveranciersregister, toegangsbeheerregister
  - **PIMS**: register van verwerkingen, DPIA-register, algoritmeregister
  - **BCMS**: lijst kritische processen, BIA, herstelplannen
- Is er capaciteit om registers en risicobeoordeling parallel bij te houden?
- Kunnen discipline-eigenaren risico's beoordelen zonder volledige registerdata?

**Hoog volwassen / data beschikbaar** → Optie B
**Laag volwassen / data ontbreekt** → Optie C (iteratief, onvolledigheid expliciet vastgelegd)

### Gap-analyse (stap 4)
Het platform stelt volwassenheidsbepalende vragen aan het begin van deze stap:
- Zijn er al bestaande risicoanalyses of audits beschikbaar?
- Heeft de organisatie eerder gewerkt met BIO, AVG of BCM-normenkaders?
- Zijn de drie discipline-eigenaren beschikbaar om gezamenlijk te werken?
- Is er al een gedeeld begrip van kritische processen?

Op basis van antwoorden kiest het systeem automatisch:
- **Hoog volwassen** → Optie B: geïntegreerde gap-analyse over alle drie domeinen
- **Laag volwassen / onzeker** → Optie C: pilot met ISMS eerst, daarna PIMS en BCMS

Keuze + redenering worden vastgelegd in besluitlog (traceerbaar).

### Governance en beleid inrichten (stap 3)
Één governance- en beleidspakket, één besluitmoment (SIMS). Niet drie aparte besluitrondes.
- TIMS bereidt voor (3a): governance-voorstel + concept IMS-beleid + communicatiematrix
- SIMS stelt vast (3b): governance + beleid in één sessie
- Het systeem vult zoveel mogelijk voor op basis van eerder ingevoerde context:
  - Actieve domeinen → welke discipline-eigenaren nodig
  - Organisatieonderdelen in scope → wie relevant voor SIMS/TIMS
  - Schaal organisatie → passende vergaderfrequentie
- Defaults: SIMS kwartaal 1,5u voorzitter DT-lid / TIMS maandelijks 2u voorzitter Concerncontroller

Het IMS-beleid (ISO 5.2) is één geïntegreerd document dat IB, privacy en continuïteit afdekt:
- Richting en commitment vanuit bestuur
- 3–5 hoog-niveau doelstellingen (ISO 6.2)
- Verwijzing naar toepasselijk normenkader
- Communicatiematrix: wie rapporteert wat aan wie binnen SIMS/TIMS (ISO 7.4)

---

## Architectuur (twee repo's, één platform)

| Repo | Doel |
|------|------|
| `IMS-tooling` | GRC-machine: risico's, controls, PDCA, evidence, assessments |
| `IMS-proces` | Implementatiebegeleiding: stappen, AI agents, documentgeneratie |

Beide repo's onder: `github.com/lugdunium`

---

## Normatief kader

Het stappenschema volgt best practices uit:
- **ISO 27001:2022** — met name clause 4 (context), 5 (leadership), 6 (planning), 9 (evaluation)
- **BIO 2.0** — Nederlandse overheidsspecifieke toepassing van ISO 27001
- **ISO 27701** — privacy-extensie op ISO 27001
- **ISO 22301:2019** — bedrijfscontinuïteit

---

## Vastgestelde ontwerpbeslissingen (vervolg)

### Stap 6: normenkader & kerncontrols (vastgesteld 12 maart 2026)
Stap 6 is **randvoorwaardelijk voor Fase 1** — niet de eerste stap ván Fase 1.

Fase 0 eindigt pas nadat:
- Het normenkader is vastgesteld (bijv. BIO 2.0, welke domeinen actief)
- Een minimale werkset kerncontrols is geselecteerd op basis van de top-risico's uit stap 5

Lijnmanagement kan pas zinvol instromen in Fase 1 als dit kader er ligt. Zonder dit stapt lijnmanagement in zonder te weten op basis van welke maatregelen ze moeten werken.

Stap 6 = **Normenkader & kerncontrols vaststellen** (minimaal, niet volledig).

### Granulariteit stappenvolgorde (vastgesteld 12 maart 2026)
Zelfde volwassenheidskeuze-patroon als stap 4 en 5: het systeem kiest automatisch op basis van opgebouwd profiel + gerichte bevestigingsvragen.

**Optie B: Geïntegreerd skelet, domeinspecifieke substappen**
- Hoofdstappen zijn generiek, binnen elke stap werken discipline-eigenaren op eigen domein-track
- TIMS coördineert samenhang tussen domeinen

**Optie C: Per domein apart**
- Elk domein heeft eigen stappenvolgorde en tempo
- ISMS als pilot, PIMS en BCMS volgen

Aanvullende vragen (bovenop het bestaande volwassenheidsprofiel uit stap 4/5):
- Zijn de drie discipline-eigenaren in staat om elkaars werk te reviewen en af te stemmen?
- Is er een gedeelde planning/ritme voor de drie domeinen, of werken ze onafhankelijk?
- Zijn er afhankelijkheden tussen domeinen die gelijktijdige voortgang vereisen?

**Hoge coördinatiekracht + hoge volwassenheid** → Optie B
**Lage coördinatiekracht of lage volwassenheid** → Optie C

Het systeem leidt dit grotendeels af uit eerder ingevulde data; geen zware nieuwe intake.

### Eindpunt Fase 0: go/no-go criteria (vastgesteld 12 maart 2026)
Fase 0 eindigt met een **formeel go/no-go besluit door de SIMS**. De SIMS is de stuurgroep.

Minimale checklist voor overgang naar Fase 1:
1. **Governance staat** — SIMS en TIMS zijn formeel ingesteld en hebben vergaderd
2. **Scope is vastgesteld** — formeel besluit over welke domeinen en organisatieonderdelen
3. **Gap-analyse is uitgevoerd** — nulmeting per actief domein is beschikbaar
4. **Registers hebben een bruikbare eerste vulling** — niet compleet, maar werkbaar
5. **Top-risico's zijn geïdentificeerd** — eerste risicobeeld per domein
6. **Normenkader & kerncontrols zijn vastgesteld** — lijnmanagement weet waarop ze werken
7. **IMS-beleid is vastgesteld** — beleid met doelstellingen is goedgekeurd door SIMS
8. **Resources voor Fase 1 zijn bevestigd** — capaciteit discipline-eigenaren, budget tooling, mandaat TIMS

Niet alles hoeft perfect te zijn. Onvolledigheid is acceptabel zolang expliciet vastgelegd (bestaand patroon). Het gaat erom dat het kader er ligt zodat lijnmanagement zinvol kan instromen.

### AI agent en bestaande documenten (vastgesteld 12 maart 2026)
**Hybride aanpak (optie C)**: het systeem vraagt bij elke stap of er al een bestaand document is.

- **Geen bestaand document** → AI genereert een nieuw concept op basis van eerder ingevulde data
- **Wel een bestaand document** → gebruiker uploadt het, AI analyseert gaps ten opzichte van de norm en genereert een verbeterd/aangevuld document

Past in het bestaande volwassenheidspatroon: het systeem past zich aan op basis van wat er al is. De gap-analyse (stap 4) stelt deze vraag al impliciet.

### Verplicht vs. optioneel per stap (vastgesteld 12 maart 2026)
Twee categorieën per stap-output:

- **Verplicht (V)** — vereist door de norm (ISO 27001, BIO 2.0, etc.) of noodzakelijk voor het functioneren van het systeem (bijv. scope is nodig voor gap-analyse)
- **Aanbevolen (A)** — voegt waarde toe maar is niet blokkerend voor de volgende stap

Overslaan van een aanbevolen document volgt het bestaande patroon: bewuste keuze wordt vastgelegd, systeem waarschuwt als vervolgstappen er last van kunnen hebben.

### V/A markering per output Fase 0 (vastgesteld 12 maart 2026)

| # | Output | V/A | Grondslag |
|---|--------|-----|-----------|
| 1 | Besluitmemo | V | ISO 5.1 |
| 1 | Besluitlog #001 | V | Systeemvereiste |
| 2a | Organisatiecontextdocument | V | ISO 4.1 |
| 2a | Stakeholderregister | V | ISO 4.2 |
| 2a | PII-rol bepaling | V | ISO 27701 |
| 2b | Formeel scopebesluit | V | ISO 4.3 |
| 3a | Concept governance-document | V | ISO 5.3 |
| 3a | Concept IMS-beleid | V | ISO 5.2 |
| 3a | Communicatiematrix | V | ISO 7.4 (shall-eis) |
| 3b | Formeel governance-besluit | V | ISO 5.3 |
| 3b | IMS-beleid (definitief) | V | ISO 5.2 |
| 3b | Besluitlog | V | Systeemvereiste |
| 4 | Nulmeting per domein | V | Fundament voor stap 5/6 |
| 4 | Besluitlog | V | Systeemvereiste |
| 5 | Registerinventarisatie | V | ISO 6.1 |
| 5 | Eerste risicobeeld | V | ISO 6.1 |
| 5 | Risicobeoordelingsmethodiek | V | ISO 6.1.2 |
| 6 | Normenkader | V | Randvoorwaarde Fase 1 |
| 6 | Minimale werkset kerncontrols | V | Randvoorwaarde Fase 1 |
| 6 | Besluitlog | V | Systeemvereiste |

Alles in Fase 0 is **V** — dit is het absolute fundament. Communicatiematrix is na ISO-toetsing opgehoogd van A naar V (shall-eis ISO 7.4).

### AI agents Fase 0 (vastgesteld 12 maart 2026)

| Stap | Agent | Doel | Hoe hij gebruikers helpt |
|------|-------|------|--------------------------|
| 1 | **Commitment-agent** | Besluitmemo opstellen | Stelt vragen over ambitieniveau, scope-intentie en middelen. Genereert besluitmemo. Bij bestaand document: analyseert volledigheid. |
| 2a | **Context-agent** | Organisatiecontext in kaart brengen | Leidt door ISO 4.1/4.2-vragen. Genereert contextdocument, stakeholderregister en PII-rolbepaling. Bij bestaande docs: identificeert gaps. |
| 2b | **Scope-agent** | Scopebesluit voorbereiden | Gebruikt output stap 2a om concept-scopestatement te genereren. Stelt vragen over domeinen en uitsluitingen. Waarschuwt bij risicovolle uitsluitingen. |
| 3a | **Governance-agent** | Governance, beleid en communicatie opstellen | Vult voor op basis van eerder ingevulde context. Genereert governance-document, IMS-beleid met doelstellingen, en communicatiematrix. |
| 3b | *Geen agent* | Besluitstap door SIMS | Goedkeuringsstap. De agent uit 3a levert het concept. |
| 4 | **Gap-agent** | Nulmeting per domein | Stelt volwassenheidsvragen. Voert gestructureerde gap-analyse uit per domein tegen normenkader. Integreert bestaande audits/analyses als input. |
| 5 | **Register-agent** | Registers, risicobeeld en methodiek opstellen | Vraagt per domein naar bestaande registers. Structureert en vult aan. Stelt risicobeoordelingsmethodiek op (criteria, acceptatieniveaus, methodiek). Begeleidt eerste risicobeoordeling. Past aanpak aan op volwassenheid (optie B/C). |
| 6 | **Controls-agent** | Normenkader en kerncontrols selecteren | Gebruikt gap-analyse en risicobeeld om normenkader voor te stellen en kerncontrols te koppelen aan top-risico's. |

**Doorsnijdend patroon voor elke agent:**
- Vraagt altijd eerst: "Heb je hier al een bestaand document voor?" (hybride aanpak)
- Genereert concept-documenten, nooit definitieve versies — het bevoegde gremium accordeert
- Legt keuzes en overgeslagen onderdelen vast in het besluitlog

### CISO-rol in SIMS (vastgesteld 13 maart 2026)
De CISO is **3e lijn** (onafhankelijk toezicht) conform het Three Lines Model. Dat betekent:
- CISO is **adviseur** van SIMS, geen lid met beslisrecht
- CISO adviseert en houdt toezicht, maar beslist niet mee
- Dezelfde scheiding geldt voor FG en Interne Accountant

Dit is consistent met de TIMS-samenstelling (3e lijn zit niet in TIMS) en voorkomt dat toezichthouders meebeslissen over zaken waar zij onafhankelijk op moeten toezien.

### Risicobereidheid: escalatieladder (vastgesteld 13 maart 2026)
Vier niveaus, consistent door het hele IMS:

| Niveau | Escalatie naar | Bevoegdheid |
|--------|---------------|-------------|
| 🟢 Groen | Discipline-eigenaar of risico-eigenaar | Monitort. Mag onderbouwd accepteren. TIMS kan bepalen dat zij niet akkoord gaan. |
| 🟡 Geel | TIMS | Tactische afweging en behandeling |
| 🟠 Oranje | SIMS | Strategische escalatie |
| 🔴 Rood | Directieteam | Bestuurlijke beslissing vereist |

De escalatieladder wordt uitgewerkt in het IMS Handboek (risicobereidheidstabel + bijlage 3 risicomethodiek).

### Handboek: blueprint + gemeente-invulling (vastgesteld 13 maart 2026)
Het IMS Handboek wordt gesplitst in twee versies:

- **Blueprint**: generiek skelet met placeholders, ISO-verwijzingen en structuur. Dit is het template dat AI agents gebruiken om een gemeente-specifiek handboek te genereren.
- **Gemeente-invulling**: ingevuld met organisatiespecifieke context, namen, stakeholders, risicobereidheid, governance-samenstelling etc. Dit is de output van het IMS-proces traject.

De agents vullen de blueprint-placeholders in op basis van wat de gemeente tijdens het proces invoert. Een andere gemeente die het platform later gebruikt, start met dezelfde blueprint en krijgt via dezelfde agents een eigen ingevulde versie.

Eerste invulling: Gemeente Leiden (en regio).

### Koppeling kritische processen/systemen/verwerkingen (vastgesteld 12 maart 2026)
In Fase 0 worden kritische processen (BCM), systemen (IB) en verwerkingen (privacy) per domein apart geïnventariseerd in stap 5. De onderlinge koppeling (welk proces gebruikt welk systeem en verwerkt welke persoonsgegevens) is Fase 1-werk.

### Wie is lijnmanagement (vastgesteld 12 maart 2026)
Volwassenheidskeuze-patroon, afgeleid via vraag aan de gemeente:
- Is er een formele proceseigenaarstructuur aanwezig?

**Ja** → Beide lagen: afdelingshoofden eindverantwoordelijk, proceseigenaren voeren risicoanalyse uit
**Nee** → Alleen afdelingshoofden: zij zijn zowel verantwoordelijk als uitvoerend

### Begeleiding bij risicoanalyse (vastgesteld 12 maart 2026)
Hybride via volwassenheid — gemeente kiest op basis van eigen situatie:
- Ervaren afdelingen → zelfstandig in de tool, discipline-eigenaar beschikbaar voor vragen
- Onervaren afdelingen → begeleid door discipline-eigenaar (sessie per afdeling/proces)

Het systeem stelt de vraag; gemeente bepaalt per afdeling.

### Statement of Applicability (vastgesteld 12 maart 2026)
De gemeente kiest zelf hoe de SoA tot stand komt:
- **Optie A**: AI genereert SoA automatisch op basis van risicoanalyse + controls (stap 9+10), SIMS accordeert
- **Optie B**: AI genereert concept-SoA, discipline-eigenaren reviewen en passen aan, SIMS stelt vast

In beide gevallen is er een AI-voorzet. De keuze wordt vastgelegd.

### Eindpunt Fase 1: go/no-go criteria (vastgesteld 12 maart 2026)
Fase 1 eindigt met een **formeel go/no-go besluit door de SIMS**.

Aanpak: **minimaal werkbaar + per domein apart doorstromen**.

Minimale checklist voor overgang naar Fase 2:
1. **Risicoanalyse is uitgevoerd** — minimaal de afdelingen/processen met de hoogste risico's
2. **Controls zijn toegewezen** — kerncontrols hebben een eigenaar
3. **SoA is vastgesteld** — al dan niet volledig, maar formeel goedgekeurd
4. **Rapportagelijn staat** — TIMS kan rapporteren aan SIMS
5. **Lijnmanagement is onboarded** — awareness + competentie geborgd

Domeinen die sneller klaar zijn mogen apart de overgang naar Fase 2 maken. ISMS kan al in PDCA draaien terwijl BCMS nog in Fase 1 zit. Dit voorkomt dat het snelste domein wacht op het langzaamste.

### V/A markering per output Fase 1 (vastgesteld 12 maart 2026)

| # | Output | V/A | Grondslag |
|---|--------|-----|-----------|
| 7 | Awareness-materiaal | V | ISO 7.3 |
| 7 | Competentiebeoordeling | V | ISO 7.2 |
| 7 | Documentbeheerprocedure | V | ISO 7.5 |
| 8 | Geïntegreerd register | V | Nodig voor risicoanalyse |
| 8 | PII-doorgifte-inventarisatie (PIMS-track) | V | ISO 27701 7.5/8.5 |
| 8 | Privacy-by-design procedure | V | ISO 27701 7.4/8.4, AVG art. 25 |
| 9 | Risicoregister per afdeling/proces | V | ISO 6.1.2 |
| 9 | BIA (BCMS-track) | V | ISO 22301 8.2.2 |
| 10 | Risicobehandelplan | V | ISO 6.1.3 |
| 10 | Controls met eigenaren | V | ISO 6.1.3 |
| 10 | Implementatieplan per control-eigenaar | V | ISO 8.1 |
| 10 | Continuïteitsstrategieën (BCMS-track) | V | ISO 22301 8.3 |
| 10 | Business continuity plans (BCMS-track) | V | ISO 22301 8.4 |
| 10 | PII-doorgifte-waarborgen (PIMS-track) | V | ISO 27701 7.5/8.5 |
| 11 | SoA-document incl. ISO 27701 Annex A/B | V | ISO 27001 6.1.3d + ISO 27701 |
| 12 | Rapportagelijnen | V | Nodig voor PDCA |
| 12 | KPI's | A | Waardevol maar niet blokkerend |
| 12 | Dashboards | A | Waardevol maar niet blokkerend |

### AI agents Fase 1 (vastgesteld 12 maart 2026)

| Stap | Agent | Doel | Hoe hij gebruikers helpt |
|------|-------|------|--------------------------|
| 7 | **Onboarding-agent** | Awareness en documentbeheer | Genereert awareness-materiaal op maat (beleid, normenkader, rol lijnmanager). Stelt competentievragen. Richt documentbeheerprocedure in of bevestigt dat IMS-tooling dit borgt. |
| 8 | **Koppeling-agent** | Registers verbinden + privacy-doorgifte + PbD | Haalt domeinregisters uit stap 5 op. Begeleidt verbanden: proces → systeem → verwerking. Inventariseert PII-doorgiften (derden, verwerkers, grensoverschrijdend). Stelt privacy-by-design procedure op. Signaleert ontbrekende koppelingen. |
| 9 | **Risico-agent** | Risicoanalyse begeleiden | Begeleidt per afdeling/proces: dreigingen, impact, kans, prioritering. Past begeleidingsniveau aan op volwassenheid. Voor BCMS-track: voert BIA uit (MTPD, RTO, RPO). |
| 10 | **Behandel-agent** | Risicobehandeling en implementatie | Stelt behandelopties voor per risico. Koppelt controls aan risico's. Genereert implementatieplan per eigenaar. Voor BCMS-track: stelt continuïteitsstrategieën + BCPs op (activatiecriteria, rollen, communicatie, herstel). Voor PIMS-track: stelt doorgifte-waarborgen voor (SCCs, verwerkersovereenkomsten). |
| 11 | **SoA-agent** | Statement of Applicability | Genereert (concept-)SoA op basis van stap 9+10. Dekt ISO 27001 Annex A + ISO 27701 Annex A (controller) en B (processor). Afhankelijk van gemeentekeuze: volledig automatisch of als reviewbaar concept. Legt per control vast waarom wel/niet van toepassing. |
| 12 | **Monitoring-agent** | Rapportage inrichten | Stelt rapportagelijnen voor op basis van governance (stap 3). Genereert KPI-voorstellen per domein. Richt dashboards in indien gewenst. |

Doorsnijdend patroon blijft gelijk aan Fase 0: altijd vragen naar bestaande documenten, altijd concept, altijd besluitlog.

### Best-practice check Fase 1 (uitgevoerd 12 maart 2026)
Fase 1 stappen getoetst aan ISO 27001:2022, ISO 27701, ISO 22301:2019 en BIO 2.0.

**Kritieke gaps gevonden en opgelost:**
- Documentbeheer (ISO 7.5) ontbrak → toegevoegd aan stap 7
- Implementatieplan controls (ISO 8.1) ontbrak → toegevoegd aan stap 10
- BIA (ISO 22301 8.2.2) was impliciet → expliciet gemaakt als BCMS-track in stap 9
- Continuïteitsstrategieën (ISO 22301 8.3) ontbraken → toegevoegd als BCMS-track in stap 10

**Kan wachten tot Fase 2:** operationele communicatieprocedures (7.4), periodieke herbeoordelingen (8.2/8.3), privacy operationele procedures (27701 A/B)

**Kernobservatie:** de brug beoordeling → implementatie was zwak. Opgelost door implementatieplan (8.1) toe te voegen aan stap 10. Zonder dit zou stap 12 controls meten die nog niet operationeel zijn.

### V/A markering per output Fase 2 (vastgesteld 12 maart 2026)

| # | Output | V/A | Grondslag |
|---|--------|-----|-----------|
| 13 | Auditprogramma | V | ISO 9.2 |
| 13 | Auditrapportages per domein | V | ISO 9.2 |
| 13 | BC-oefenrapportage (BCMS-track) | V | ISO 22301 8.5 |
| 14 | Review-rapportage (verplichte inputchecklist) | V | ISO 9.3.2 |
| 14 | Verbeterbeslissingen | V | ISO 9.3 |
| 15 | Non-conformiteitenregister | V | ISO 10.1 |
| 15 | Correctieve acties | V | ISO 10.2 |
| 15 | Incidentmanagementprocedure | V | ISO A.5.24-28, AVG 33/34 |
| 16 | Bewijs per control | V | ISO 9.1 |
| 16 | Continue monitoring | V | ISO 9.1 |
| 16 | Privacy operationele procedures (PIMS-track) | V | ISO 27701 A/B |
| 17 | Jaarplanning | V | ISO 8.1 |
| 17 | Reviewcyclus | V | ISO 9.3 |
| 17 | Periodieke risicoherbeoordeling | V | ISO 8.2/8.3 |
| 17 | Communicatieprocedures (incl. crisiscommunicatie BCM) | V | ISO 7.4 / ISO 22301 8.4.3 (shall-eis) |
| 17 | Verbeterdoelen | A | Best practice |

### AI agents Fase 2 (vastgesteld 12 maart 2026)

| Stap | Agent | Doel | Hoe hij gebruikers helpt |
|------|-------|------|--------------------------|
| 13 | **Interne-audit-agent** | Audits plannen en uitvoeren | Genereert auditprogramma op basis van domeinbelang en eerdere resultaten. Begeleidt audits met checklists per domein. Voor BCMS-track: plant en evalueert BC-oefeningen. |
| 14 | **Review-agent** | Management review voorbereiden | Verzamelt verplichte inputs (ISO 9.3.2): status vorige acties, context-wijzigingen, auditresultaten, risicostatus, stakeholder-feedback. Genereert concept review-rapportage voor SIMS. |
| 15 | **Afwijkingen-agent** | Non-conformiteiten en incidenten beheren | Registreert afwijkingen, begeleidt root cause analyse, volgt correctieve acties. Beheert incidentmanagement: classificatie, respons, lessons learned. Voor PIMS: privacy-incidenten en meldplicht AVG. |
| 16 | **Evidence-agent** | Bewijs verzamelen en monitoren | Koppelt evidence aan controls, signaleert ontbrekend bewijs, bewaakt deadlines. Voor PIMS-track: borgt privacy-procedures (rechten betrokkenen, DPIA, verwerkersovereenkomsten). |
| 17 | **PDCA-agent** | Jaarplanning en cyclus formaliseren | Genereert jaarplanning met audit-, review- en herbeoordelingsmomenten. Plant periodieke risicoherbeoordeling. Stelt verbeterdoelen voor op basis van trends. |

### Best-practice check Fase 2 (uitgevoerd 12 maart 2026)
Fase 2 stappen getoetst aan ISO 27001:2022, ISO 27701, ISO 22301:2019 en BIO 2.0.

**Hoge gaps gevonden en opgelost:**
- Periodieke risicoherbeoordeling (ISO 8.2/8.3) ontbrak → expliciet in stap 17
- BC-oefeningen (ISO 22301 8.5) ontbraken → BCMS-track in stap 13
- Incidentmanagement (ISO A.5.24-28, AVG 33/34) ontbrak volledig → ingebouwd in stap 15

**Medium gaps ingebed in bestaande stappen:**
- Management review inputchecklist (ISO 9.3.2) → verplicht format stap 14
- BC-documentatie-evaluatie (ISO 22301 8.6) → mee in risicoherbeoordeling stap 17
- Privacy operationele procedures (ISO 27701 A/B) → PIMS-track stap 16

**Lage punten:**
- Communicatieprocedures (ISO 7.4) → A-deliverable in stap 17
- Auditprogramma integratie-scope → richtlijn dat audits ook IMS-integratiepunten dekken

### V/A markering per output Fase 3 (vastgesteld 12 maart 2026)
Alles in Fase 3 is **A (aanbevolen)** — de hele fase is optioneel.

| # | Output | V/A | Toelichting |
|---|--------|-----|-------------|
| 18 | Pre-audit rapport | A | Alleen relevant bij certificeringsambitie |
| 18 | Gap-remediatie | A | Afhankelijk van pre-audit resultaat |
| 18 | Certificeringsaanvraag | A | Bewuste keuze, niet vereist voor functionerend IMS |
| 19 | Trendanalyses | A | Verdieping op basis-rapportage uit Fase 2 |
| 19 | Predictive risk | A | Geavanceerde functionaliteit |
| 19 | Geautomatiseerde rapportages | A | Efficiency-verbetering |
| 20 | Ketenpartner-koppelingen | A | Afhankelijk van ketenrelaties |
| 20 | Leveranciersportaal | A | Afhankelijk van leveranciersvolume |
| 21 | Cross-mapping controls | A | Eliminatie duplicatie bij meerdere normen |
| 22 | Benchmark-rapportage | A | Pas waardevol bij meerdere deelnemende gemeenten |
| 22 | Best practice bibliotheek | A | Kennisdeling tussen gemeenten |

### AI agents Fase 3 (vastgesteld 12 maart 2026)

| Stap | Agent | Doel | Hoe hij gebruikers helpt |
|------|-------|------|--------------------------|
| 18 | **Audit-agent** | Certificeringsgereedheid beoordelen | Voert interne pre-audit uit tegen ISO 27001 (optioneel 22301/27701). Identificeert gaps, genereert remediatieplan. Bereidt dossier voor certificeringsinstantie voor. |
| 19 | **Analytics-agent** | Geavanceerde analyses genereren | Analyseert trends in risico's, incidenten, control-effectiviteit over tijd. Signaleert patronen en voorspelt risico-ontwikkelingen. Automatiseert periodieke rapportages. |
| 20 | **Integratie-agent** | Externe koppelingen beheren | Begeleidt het inrichten van data-uitwisseling met ketenpartners en leveranciers. Bewaakt datakwaliteit en beveiligingseisen bij koppelingen. |
| 21 | **Framework-agent** | Multi-framework optimalisatie | Analyseert overlap tussen normen (BIO/AVG/BCM). Stelt cross-mappings voor: één control mapped naar meerdere eisen. Elimineert duplicatie in controles en evidence. |
| 22 | **Benchmark-agent** | Vergelijking en kennisdeling | Genereert geanonimiseerde benchmark-rapportages. Identificeert best practices uit andere gemeenten. Stelt verbetervoorstellen voor op basis van vergelijkingsdata. |

### Fase 3 ontwerpbeslissing (vastgesteld 12 maart 2026)
Fase 3 is volledig optioneel en modulair. Er is geen go/no-go, geen vaste volgorde. De gemeente activeert onderdelen wanneer de ambitie en capaciteit er is. Elke stap in Fase 3 is onafhankelijk van de andere — certificering vereist geen benchmarking, analytics vereist geen externe integraties.

Fase 3 wordt niet geïmplementeerd tenzij daar expliciet voor gekozen wordt. Het ontwerp documenteert de mogelijkheden zodat de product-roadmap compleet is.

### Best-practice check Fase 0 (uitgevoerd 12 maart 2026)
Fase 0 stappen getoetst aan ISO 27001:2022, ISO 27701, ISO 22301:2019 en BIO 2.0.

**Kritieke gap gevonden en opgelost:**
- IMS-beleid (ISO 5.2) ontbrak → ingebouwd in stap 3a/3b

**Kleine punten ingebed in bestaande stappen:**
- Stakeholderregister (ISO 4.2) → verplichte output stap 2a
- PII-rol controller/processor (ISO 27701 5.2.1) → verplichte output stap 2a
- Doelstellingen (ISO 6.2) → onderdeel IMS-beleid in stap 3
- Communicatiematrix (ISO 7.4) → onderdeel governance in stap 3
- Resourcebevestiging (ISO 7.1) → criterium 8 in go/no-go checklist

**Kan wachten tot Fase 1+:** competence (7.2), awareness (7.3)

### Volledige ISO-toetsing (uitgevoerd 12 maart 2026)
Alle 22 stappen clause-by-clause getoetst tegen ISO 27001:2022 (25 clauses), ISO 27701:2019 (18 clauses) en ISO 22301:2019 (24 clauses).

**6 kritieke gaps gevonden en opgelost:**

| # | Gap | Norm | Oplossing |
|---|-----|------|-----------|
| 1 | BCPs ontbraken (alleen strategieën, geen plannen) | ISO 22301 8.4 | BCPs met activatiecriteria, rollen, communicatie, herstel → stap 10 BCMS-track |
| 2 | Privacy by Design ontbrak volledig | ISO 27701 7.4/8.4, AVG art. 25 | PbD-procedure → stap 8 |
| 3 | Communicatieprocedures op A i.p.v. V | ISO 7.4 / ISO 22301 8.4.3 | Opgehoogd naar V in stap 3a en stap 17 (incl. crisiscommunicatie) |
| 4 | PII-transfers in Fase 3 (optioneel) i.p.v. verplicht | ISO 27701 7.5/8.5 | Doorgifte-inventarisatie → stap 8, waarborgen → stap 10 |
| 5 | Risicobeoordelingsmethodiek niet expliciet | ISO 27001 6.1.2 | Methodiek met criteria en acceptatieniveaus → stap 5 |
| 6 | SoA dekte ISO 27701 Annex A/B niet | ISO 27701 | SoA uitgebreid met 27701 controller- en processor-controls → stap 11 |

**Gedeeltelijke dekkingen (vastgelegd als aandachtspunten, geen structuurwijziging nodig):**
- Stakeholderregister: PII-specifieke en BCM-specifieke stakeholders expliciet prompten in Context-agent
- Scope: verwerkingstypen (27701) en producten/diensten (22301) meenemen in Scope-agent
- Awareness: privacy-specifieke content en "rol tijdens verstoring" (22301) meenemen in Onboarding-agent
- Management review: domein-specifieke inputs (BC-oefenresultaten, PII-audits) in inputchecklist
- Risico-eigenaar goedkeuring restrisico (6.1.3f): meenemen in Behandel-agent workflow
- Change management IMS (6.3): onderdeel PDCA-cyclus stap 17
- Diverse privacy controller/processor verplichtingen: geborgd via uitgebreide SoA + privacy-procedures stap 16

**Totaalscore na correcties:**

| Norm | Clauses | Gedekt | Gedeeltelijk | Ontbrekend |
|------|---------|--------|--------------|------------|
| ISO 27001:2022 | 25 | 24 | 1 (6.3 change mgmt) | 0 |
| ISO 27701:2019 | 18 | 15 | 3 (detail-niveau) | 0 |
| ISO 22301:2019 | 24 | 22 | 2 (detail-niveau) | 0 |

Resterende gedeeltelijke dekkingen zijn detail-kwesties die in de agent-implementatie worden opgelost, niet in het procesontwerp.

---

## Openstaande vragen

Alle procesontwerp-vragen zijn vastgesteld (12 maart 2026). Volledige ISO-toetsing afgerond.

**Het IMS-implementatieproces is volledig ontworpen en getoetst: 22 stappen, 4 fasen, 18 AI agents, clause-by-clause geverifieerd tegen ISO 27001:2022, ISO 27701:2019 en ISO 22301:2019.**

---

## Volgende stappen richting bouwfase (vastgesteld 13 maart 2026)

*Het procesontwerp (WAT en WAAROM) staat. Onderstaande punten moeten worden uitgewerkt voordat de bouwfase kan starten. Elk punt vereist sparring en expliciete keuzes.*

### 1. Stap → handboek mapping (moet verbeteren)
Expliciete mapping maken: welke processtap vult welke sectie(s) van het blueprint-handboek. Zonder dit weet een agent niet waar zijn output terechtkomt.

Voorbeelden die uitgewerkt moeten worden:
- Stap 2a → §4.1 (context), §4.2 (stakeholders)
- Stap 3a/3b → §5 (governance), IMS-beleid
- Stap 5 → bijlage 3 (risicomethodiek)
- Stap 6 → §8.4 (risicobehandeling), VvT
- etc. — voor alle 22 stappen

**Deliverable:** volledige mappingtabel in CONTEXT.md.

### 2. Dataflow tussen stappen (moet vastleggen)
Expliciet documenteren welke data-objecten elke stap produceert en welke vervolgstappen die consumeren. Nu is dit impliciet — agents kunnen niet gebouwd worden zonder deze kennis.

Uit te werken:
- Per stap: exacte input-objecten en output-objecten
- Het **volwassenheidsprofiel** als concreet data-object definiëren: wat bevat het, waar leeft het, hoe bouwt het zich op over stappen 4, 5, 7, 8, 9?
- Afhankelijkheidsgrafiek: welke stappen zijn echt blokkerend voor welke vervolgstappen (vs. "nice to have" input)

**Deliverable:** dataflow-tabel of -diagram per fase in CONTEXT.md.

### 3. Verplicht (V) vs. stappen overslaan (moet overleggen)
Tegenstrijdigheid oplossen: CONTEXT.md zegt "stappen zijn niet hard geblokkeerd", maar Fase 0 is 100% V (verplicht door ISO).

Te beslissen:
- Kan een V-output overslaan? Zo ja: is dat een bewuste ISO-non-compliance keuze die in het besluitlog komt?
- Of is V echt blokkerend in het platform (stap weigert door te gaan zonder output)?
- Verschil tussen "output is V" en "stap is blokkered voor volgende stap"?

**Deliverable:** beslissing vastleggen als ontwerpbeslissing in CONTEXT.md.

### 4. Implementatiecoördinator / projectleidersrol (moet overleggen)
Het proces definieert agents en gremia, maar niet wie het implementatietraject aanstuurt. Feedback noemt Bas als TIMS-voorzitter, maar CONTEXT.md definieert geen projectleidersrol.

Te beslissen:
- Is er een expliciete implementatiecoördinator-rol?
- Is dat de TIMS-voorzitter, of een aparte projectleider?
- Hoe verhoudt die rol zich tot de agents (opdrachtgever van de agents? Gebruiker?)?
- Moet deze rol in het generieke model (blueprint) of alleen in de Leiden-invulling?

**Deliverable:** rolbeschrijving + positie in governance.

### 5. Besluitlog-structuur (moet definiëren)
Elke stap produceert besluitlog-entries, maar het format is niet gedefinieerd.

Te beslissen:
- Vaste velden: wie, wat, wanneer, grondslag (ISO-clause), besluit, geldigheidsduur?
- Optionele velden: overwegingen, alternatieven, risico-acceptatie?
- Is het besluitlog één doorlopend register of per stap apart?
- Hoe verhoudt het zich tot de GRC-tool (wordt het daar opgeslagen)?

**Deliverable:** besluitlog-schema.

### 6. Fase 2 cyclisch mechanisme (moet definiëren)
Stappen 13-17 zijn "cyclisch, niet lineair", maar het herhalingsmechanisme is ongedefinieerd.

Te beslissen:
- Jaarlijkse cyclus (aangestuurd door jaarplanning uit stap 17)?
- Event-driven (getriggerd door incidenten, audit-bevindingen, context-wijzigingen)?
- Combinatie van beide?
- Hoe schakelt het platform van inrichtingsmodus naar beheermodus — is dat per domein apart (ISMS kan al draaien terwijl BCMS nog in Fase 1 zit)?

**Deliverable:** cyclus-beschrijving als ontwerpbeslissing.

### 7. IMS-beleid als apart document (moet overleggen)
Stap 3 produceert "IMS-beleid" als output. In het blueprint-handboek is het beleid verweven in §5 (governance). Maar ISO 5.2 vereist een vastgesteld beleidsdocument.

Te beslissen:
- Is het IMS-beleid een apart document (dat de agent genereert)?
- Of is het een sectie van het handboek die formeel wordt vastgesteld?
- Hoe verhoudt zich dat tot het blueprint-model (placeholder in handboek vs. apart template)?

**Deliverable:** beslissing + eventueel apart beleid-template.

---

*Pas als bovenstaande 7 punten zijn uitgewerkt en vastgelegd, is het ontwerp compleet genoeg voor de bouwfase.*
