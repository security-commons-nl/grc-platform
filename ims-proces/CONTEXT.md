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

### 1. Stap → handboek mapping (vastgesteld 18 maart 2026)

#### Het handboek is een bestuurlijk kader, geen operationeel werkdocument

Het IMS Handboek staat op **niveau 1** van de documentenpyramide:

```
Niveau 1: IMS Handboek          — bestuurlijk kader, governance, scope, PDCA-structuur
Niveau 2: Domeinplannen         — BIO-implementatieplan, AVG-procedures, BCP's (eigenaar per domein)
Niveau 3: Procedures/werkinstr. — concrete werkwijzen, checklists, templates
Niveau 4: Registraties/bewijs   — risicoregister, SoA, auditlogboeken, GRC-tool
```

Het handboek **verwijst** naar niveau 2-documenten via placeholders (`{{VERWIJZING_BIO_IMPLEMENTATIEPLAN}}` etc.) — het absorbeert ze niet. Domeinsporen (BIO-plan, AVG-procedures, BCP's) zijn subdocumenten die als apart document onder het IMS hangen, met een domein-eigenaar.

De agents vullen niveau 1 in. Niveau 2 wordt door domein-agents ondersteund als aparte documenten. Niveau 3 en 4 landen in de GRC-tool.

#### §4.3 heeft twee niveaus: overkoepelende scope + domein-specifieke scopes

§4.3 wordt niet ingevuld door één placeholder, maar per scope-niveau:

| Placeholder | Inhoud | Gevuld door stap | Scope-logica |
|-------------|--------|------------------|--------------|
| `{{IMS_SCOPE_ORGANISATIE}}` | Welke entiteiten (Leiden, regio, BVO?) | 2b | Bestuurlijk besluit |
| `{{ISMS_SCOPE}}` | Alle gevoelige informatie(systemen) | 2b + ISMS-track | Nader bepaald per domein |
| `{{PIMS_SCOPE}}` | Alle verwerkingen persoonsgegevens (AVG dwingt — weinig keuze) | 2b + PIMS-track | Nader bepaald per domein |
| `{{BCMS_SCOPE}}` | Kritische processen (volgt uit BIA) | 9 (BCMS-track) | Nader bepaald per domein |

De overkoepelende IMS-scope (welke organisatieonderdelen) wordt in stap 2b vastgesteld door SIMS. De domein-specifieke scopes worden door de respectievelijke discipline-eigenaren uitgewerkt en zijn onderdeel van de domeinplannen (niveau 2).

#### Volledige stap → handboek mappingtabel

| Stap | Output | Handboek-sectie | Placeholder |
|------|--------|-----------------|-------------|
| 2a | Organisatiecontextdocument | §4.1 | `{{CONTEXT_BESCHRIJVING}}`, `{{AMBITIES_BESCHRIJVING}}` |
| 2a | Organisatiecontextdocument | §4.1.6 | `{{VISIE}}`, `{{MISSIE}}`, `{{STRATEGIE}}`, `{{SWOT_ANALYSE}}` |
| 2a | Stakeholderregister | §4.2 + Bijlage 1 | `{{BELANGHEBBENDEN_ANALYSE}}` |
| 2b | Scopebesluit | §4.3 | `{{IMS_SCOPE_ORGANISATIE}}`, `{{ISMS_SCOPE}}`, `{{PIMS_SCOPE}}` |
| 3a/3b | Governance-document | §5.3.1 | `{{SIMS_SAMENSTELLING}}` |
| 3a/3b | Governance-document | §5.3.2 | `{{TIMS_SAMENSTELLING}}` |
| 3a/3b | Governance-document | §5.3.3 | `{{DISCIPLINE_EIGENAREN_TOEWIJZING}}` |
| 3a/3b | Communicatiematrix | §5.5 | `{{RAPPORTAGE_TABEL}}` |
| 3b | IMS-beleid | §6.2 | (apart document op niveau 2 — handboek verwijst ernaar) |
| 5 | Eerste risicobeeld | §8.2 | `{{STRATEGISCHE_RISICOANALYSE_BESCHRIJVING}}`, `{{OPERATIONELE_RISICOANALYSE_BESCHRIJVING}}` |
| 5 | Risicobeoordelingsmethodiek | Bijlage 3 | `{{IMPACTSCHALEN_TABEL}}`, `{{KANSSCHALEN_TABEL}}`, `{{RISICOMATRIX}}` |
| 6 | Normenkader | §2 | (vaste tekst, aangevuld met actieve normen per organisatie) |
| 9 | BIA (BCMS-track) | §4.3 | `{{BCMS_SCOPE}}` (pas beschikbaar na Fase 1) |

**Stappen die niet in het handboek landen — aparte documenten (niveau 2+):**

| Stap | Output | Waar |
|------|--------|------|
| 1 | Besluitmemo + besluitlog | Besluitlog (apart register) |
| 2a | PII-rol bepaling | Niveau 2 — PIMS-track document |
| 4 | Nulmeting per domein | Gap-analyse document (apart) |
| 5 | Registerinventarisatie | Domeinregisters (apart) |
| 6 | Minimale werkset kerncontrols | VvT / normenkader-document (niveau 2) |
| 7–12 | Fase 1-outputs | GRC-tool (risicoregister, SoA, etc.) |

### 2. Dataflow tussen stappen (vastgesteld 18 maart 2026)

#### Blokkade-principe (vastgesteld 18 maart 2026)

Twee soorten afhankelijkheden:
- **Blokkerend (B):** stap kan technisch niet starten zonder deze input
- **Waarschuwing (W):** stap mag starten, platform waarschuwt dat output minder nauwkeurig kan zijn

Stap 7 (onboarding lijnmanagement) is **W** voor stap 9: lijnmanagement mag instromen maar platform waarschuwt als awareness nog niet is afgerond.
Stap 8 (geïntegreerd register) is **W** voor stap 9: risicoanalyse mag starten zonder volledig register, iteratief aanvullen is toegestaan (optie C).

#### Volwassenheidsprofiel (vastgesteld 18 maart 2026)

Het volwassenheidsprofiel is een **database-tabel in het platform**. Het groeit tijdens de inrichtingsmodus (stappen 4/5/7/8/9) en blijft daarna beschikbaar als organisatieprofiel in de beheermodus.

```
VolwassenheidsProfiel {
  domein: ISMS | PIMS | BCMS
  bestaande_registers: aanwezig | gedeeltelijk | afwezig
  bestaande_analyses: aanwezig | gedeeltelijk | afwezig
  capaciteit_coordinatie: hoog | gemiddeld | laag
  lijnmanagement_structuur: formeel | informeel
  → keuze: optie_B | optie_C
}
```

#### Dataflow per stap — Fase 0

| Stap | Input | Output | Blokkeert |
|------|-------|--------|-----------|
| 1 | — | Besluitmemo, Besluitlog #001 | 2a (B) |
| 2a | Besluitlog #001 | Organisatiecontextdocument, Stakeholderregister, PII-rol | 2b (B), 3a (B) |
| 2b | Organisatiecontextdocument | Scopebesluit | 3a (B), 4 (B) |
| 3a | Contextdocument + Scopebesluit | Concept governance, Concept IMS-beleid, Communicatiematrix | 3b (B) |
| 3b | Concepten uit 3a | Governance-besluit, IMS-beleid (definitief) | 4 (B), 7 (B) |
| 4 | Scopebesluit + Governance-besluit | Nulmeting per domein, **Volwassenheidsprofiel v1** | 5 (B), 6 (B) |
| 5 | Nulmeting + Volwassenheidsprofiel v1 | Registerinventarisatie, Eerste risicobeeld, Risicobeoordelingsmethodiek, **Volwassenheidsprofiel v2** | 6 (B), 8 (W), 9 (W) |
| 6 | Nulmeting + Eerste risicobeeld | Normenkader, Kerncontrols | 7 (B), 9 (B), 10 (B) |

#### Dataflow per stap — Fase 1

| Stap | Input | Output | Blokkeert |
|------|-------|--------|-----------|
| 7 | Governance-besluit + Normenkader | Awareness-materiaal, Competentiebeoordeling, Documentbeheerprocedure, **Volwassenheidsprofiel v3** | 9 (W) |
| 8 | Registerinventarisatie (stap 5) + Scopebesluit | Geïntegreerd register, PII-doorgifte-inventarisatie, PbD-procedure, **Volwassenheidsprofiel v4** | 9 (W) |
| 9 | Geïntegreerd register (W) + Risicobeoordelingsmethodiek (B) + Normenkader (B) + Volwassenheidsprofiel v4 | Risicoregister per afdeling/proces, BIA | 10 (B) |
| 10 | Risicoregister + BIA + Normenkader/controls | Risicobehandelplan, Controls met eigenaren, Implementatieplan, BCPs, PII-doorgifte-waarborgen | 11 (B), 16 (B) |
| 11 | Risicoregister + Controls + Risicobehandelplan | SoA | 13 (B), 16 (B) |
| 12 | Governance (stap 3) + Doelstellingen | Rapportagelijnen, KPI's, Dashboards | 13 (W), 14 (W) |

#### Dataflow per stap — Fase 2 (cyclisch)

| Stap | Input | Output | Triggert |
|------|-------|--------|---------|
| 13 | SoA + Controls + Rapportagelijnen | Auditprogramma, Auditrapportages, BC-oefenrapportage | 14, 15 |
| 14 | Auditresultaten + Risicoregister + KPI's | Review-rapportage, Verbeterbeslissingen | 17 |
| 15 | Auditresultaten + Incidenten | Non-conformiteitenregister, Correctieve acties | 14, 16 |
| 16 | Controls + SoA + Correctieve acties | Bewijs per control, Privacy-procedures | 14 |
| 17 | Review-rapportage + Verbeterbeslissingen | Jaarplanning, Risicoherbeoordeling, Communicatieprocedures | → 13 (nieuwe cyclus) |

#### Platform-architectuur (vastgesteld 18 maart 2026)

Het IMS-platform is één geïntegreerde applicatie met twee modi:

```
INRICHTINGSMODUS (IMS-proces)     BEHEERMODUS (IMS-tooling)
22 stappen, 18 agents         →   Risico's, controls, PDCA
Document wizard                    Assessments, evidence
Handboek generatie                 Rapportages, dashboards
Volwassenheidsprofiel groeit   →   Blijft als organisatieprofiel
Fase 0 → 1 → 2               →   Fase 2 loopt over in beheermodus
```

Data stroomt één richting. Geen synchronisatie. Één waarheid. De architectuur en het datamodel worden apart uitgewerkt met als kernprincipe: simpel voor de gebruiker.

### 3. Verplicht (V) vs. stappen overslaan (vastgesteld 18 maart 2026)

V (ISO-verplicht), B (technisch blokkerend) en W (waarschuwing) zijn drie verschillende begrippen:

| Begrip | Betekenis |
|--------|-----------|
| **V** | De ISO-norm eist dit. Verantwoordelijkheid van de organisatie. |
| **B** | Het platform laat je technisch niet verder zonder dit (zie dataflow punt 2). |
| **W** | Het platform laat je verder, maar waarschuwt en legt vast. |

**V ≠ automatisch B.** Het platform dwingt geen ISO-compliance af — dat is de verantwoordelijkheid van de organisatie. Wat het platform doet bij het overslaan van een V-output:

1. Expliciete waarschuwing: *"Dit is een ISO-vereiste (clause X.X). Overslaan betekent bewuste non-compliance."*
2. Automatische vastlegging in het besluitlog: wie, wanneer, waarom, welke ISO-clause
3. Oranje vlag op vervolgstappen die van deze output afhangen: *"Gebaseerd op onvolledige input"*

B is gereserveerd voor technische onmogelijkheden — inputs die een agent echt niet kan missen om zijn werk te doen (zie dataflow-tabellen punt 2).

### 4. Implementatiecoördinator / projectleidersrol (vastgesteld 18 maart 2026)

Twee afzonderlijke rollen, beide in het generieke model:

| Rol | Karakter | Eindigt | Leiden-invulling |
|-----|----------|---------|-----------------|
| **TIMS-voorzitter** | Permanent, governance | Nooit | Luuk de Leede |
| **Implementatiecoördinator / Projectleider** | Tijdelijk, operationele regie over de 22 stappen | Bij go/no-go Fase 2 → overdracht aan discipline-eigenaren | Bas Stevens (projectleider-hoed, niet CISO-hoed) |

De CISO (Bas) heeft een 3e-lijn toezichtrol en staat buiten SIMS en TIMS. Als projectleider heeft hij een aparte, tijdelijke operationele rol. Het platform en de documentatie maken dit onderscheid expliciet.

**Relatie tot het platform:** de implementatiecoördinator is de primaire gebruiker tijdens de inrichtingsmodus. Zij triggeren stappen, reviewen agent-output en bewaken voortgang. De agents werken voor hen.

**Blueprint-placeholders:**
- `{{TIMS_VOORZITTER}}` — lid van TIMS, permanente governance
- `{{IMPLEMENTATIECOORDINATOR}}` — projectleider implementatietraject, tijdelijk

### 5. Besluitlog-structuur (vastgesteld 18 maart 2026)

**Één doorlopend register** in het platform (database). Nummering: `0001`, `0002`, ... (4 cijfers — ruimte voor groei). Exporteerbaar als PDF/Word voor audits en certificering (export is een platform-breed principe, niet besluitlog-specifiek).

Besluiten worden nooit overschreven. Een herzien besluit krijgt een nieuw entry met verwijzing naar het originele. Audit trail blijft altijd intact.

#### Schema

| Veld | V/A | Toelichting |
|------|-----|-------------|
| `id` | V | Doorlopend nummer (0001, 0002, ...) |
| `datum` | V | Datum van vaststelling |
| `stap` | V | Processtap (bijv. "2b") |
| `besluit` | V | Wat is er besloten — kort en feitelijk |
| `grondslag` | V | ISO-clause of systeemvereiste (bijv. "ISO 27001 §4.3") |
| `bevoegd_gremium` | V | SIMS / TIMS / discipline-eigenaar |
| `vastgesteld_door` | V | Naam van de persoon die accordeert |
| `geldigheidsduur` | V | Datum of "tot herziening" |
| `motivering` | A | Waarom deze keuze — bij niet-standaard besluiten |
| `alternatieven` | A | Welke opties zijn overwogen |
| `non_compliance` | A | Alleen bij overslaan V-output: welke ISO-clause, bewuste keuze |
| `herziet_besluit` | A | Verwijzing naar id van het originele besluit bij herziening |

### 6. Fase 2 cyclisch mechanisme (vastgesteld 18 maart 2026)

#### Cyclus-karakter per stap

| Stap | Karakter | Frequentie |
|------|----------|------------|
| 13 — Interne audit | Gepland | Jaarlijks (conform auditprogramma) |
| 14 — Management review | Gepland | Jaarlijks (ISO 9.3) |
| 15 — Afwijkingen & incidenten | Event-driven | Zodra het zich voordoet |
| 16 — Evidence & monitoring | Continu | Permanent actieve module in beheermodus |
| 17 — PDCA-cyclus formaliseren | Gepland | Jaarlijks — produceert jaarplanning voor volgend jaar |

Stap 17 produceert de jaarplanning die bepaalt wanneer 13 en 14 het volgende jaar plaatsvinden. Zo sluit de cirkel.

#### Schakeling inrichtingsmodus → beheermodus

Per domein apart, bij go/no-go Fase 2. ISMS kan al in Fase 2 draaien terwijl BCMS nog in Fase 1 zit. Het platform toont per domein in welke fase het zit. Beheermodus-functionaliteit wordt per domein ontgrendeld zodra het go/no-go besluit is vastgelegd in het besluitlog.

#### Platform-scope: governance, niet operationeel

Het IMS-platform beheert **geen individuele operationele events**. Individuele incidenten horen in operationele tools (TopDesk, ServiceNow). De koppeling loopt via integraties: operationele tools leveren input voor management review en correctieve acties, maar het incident zelf wordt niet in het platform beheerd.

Wat het platform wél doet rond incidenten:

| Wat | In platform |
|-----|-------------|
| Incidentmanagementprocedure (beleid) | Ja — output stap 15 |
| Non-conformiteiten uit audits | Ja — systemische afwijkingen |
| Correctieve acties | Ja — PDCA-verbetercyclus |
| Trenddata voor management review | Ja — aggregaat |
| Individuele incidenten registreren | Nee — TopDesk/ServiceNow |
| 72-uurs AVG-meldplicht uitvoeren | Nee — operationeel proces |

Dit is een **platform-breed principe**: het platform beheert governance en compliance, niet de dagelijkse operatie.

### 7. IMS-beleid als apart document (vastgesteld 18 maart 2026)

Het IMS-beleid (ISO 5.2) is **een sectie van het handboek**, niet een apart document. §5 (governance) + §6.2 (doelstellingen) samen vormen het vastgestelde beleid.

Stap 3b accordeert §5+§6 van het handboek. Er is geen apart beleidsdocument nodig.

Bestaande domeinbeleidsplannen zijn **niveau 2-documenten** die het handboek via verwijzingen insluit:

```
IMS Handboek §5+§6          — overkoepelend IMS-beleid (ISO 5.2)
      ↓ verwijst naar
Strategisch IB-beleid       — niveau 2, ISMS-domein (Leidse Regio, bestaat)
Strategisch Privacy-beleid  — niveau 2, PIMS-domein (Leidse Regio, bestaat)
BCM-beleid                  — niveau 2, BCMS-domein
```

Bestaande domeinbeleidsplannen worden in stap 3 gereviewed en via het handboek gepositioneerd als domeinspoor. Ze worden onderdeel ván het IMS, niet vervangen.

**Blueprint-placeholders toegevoegd:**
- `{{VERWIJZING_IB_BELEID}}` — verwijzing naar domein IB-beleid
- `{{VERWIJZING_PRIVACY_BELEID}}` — verwijzing naar domein privacy-beleid
- `{{VERWIJZING_BCM_BELEID}}` — verwijzing naar domein BCM-beleid

---

*Pas als bovenstaande 7 punten zijn uitgewerkt en vastgelegd, is het ontwerp compleet genoeg voor de bouwfase.*

---

## Bouwfase — knelpunten & architectuurkeuzes

### K1. Multi-tenant + RBAC (vastgesteld 18 maart 2026)
Zie `reference-docs/architectuur-multi-tenant.md`.

### K2. Document-generatie, bewerking en versies (vastgesteld 18 maart 2026)

**Bewerking:** in het platform — niet downloaden/uploaden. Platform behoudt controle, kan diff's tonen, agent kan helpen bij herziening.

**Versiemodel:**
```
Document
  ├── versie 1.0  [agent-concept]      → status: concept
  ├── versie 1.1  [bewerkt door ...]   → status: in review
  └── versie 2.0  [geaccordeerd]       → status: vastgesteld ← enige die telt
```

Drie statussen: **concept** → **in review** → **vastgesteld**. Alleen vastgesteld is de waarheid. Eerdere versies zijn auditspoor.

**Documenttypes bepalen herzieningsritme:**

| Type | Herzieningsritme | Versiemodel |
|------|-----------------|-------------|
| Levend document (handboek, risicoregister, SoA) | Bij wijziging | Nieuwe versie op zelfde document |
| Periodiek document (auditrapportage, management review, jaarplanning) | Per cyclus | Nieuw document, gekoppeld aan vorige |

Het handboek hoeft niet elk jaar opnieuw — alleen bij governance-/scope-/beleidswijziging.

### K6. Bestaande documenten uploaden + gap-analyse (vastgesteld 18 maart 2026)

**Bestandsformaten:** PDF, Word (.docx), Markdown.

**Agent-architectuur: twee aparte agents**

```
Gebruiker uploadt document
    ↓
[Gap-analyse agent]  — platform-breed herbruikbaar
Leest document, vergelijkt met normvereisten voor deze stap
Output: gestructureerde lijst gaps
    ↓
Gebruiker ziet gaps, klikt "vul aan"
    ↓
[Domein-agent voor deze stap]  — stap-specifiek, kent de norm al
Input: origineel document + gap-rapport + normvereisten
Output: ontbrekende secties bijgeschreven
    ↓
Gebruiker reviewt → accordering
```

Gap-analyse agent = platform-breed, bij elke stap inzetbaar waar een bestaand document wordt geüpload.
Domein-agent = stap-specifiek, verantwoordelijk voor het genereren van content.

### K5. Hergebruik in Fase 2 — cyclus-jaar koppeling (vastgesteld 18 maart 2026)

Elke stap-uitvoering in Fase 2 krijgt een `cyclus_id`. De jaarplanning uit stap 17 triggert de nieuwe cyclus.

```
Stap 13 — uitvoering 1 (2026):  cyclus_id: 2026, status: afgerond
Stap 13 — uitvoering 2 (2027):  cyclus_id: 2027, vorige_cyclus: 2026
Stap 13 — uitvoering 3 (2028):  cyclus_id: 2028, vorige_cyclus: 2027
```

Voordelen: trends zichtbaar over cycli, vorige cyclus raadpleegbaar, agents gebruiken vorige cyclus als context bij genereren.

### K4. Stap-ontgrendeling (vastgesteld 18 maart 2026)

Drie zichtbare staten per stap:

| Status | Wat de gebruiker ziet | Wat er kan |
|--------|----------------------|------------|
| 🔒 Geblokkeerd | "Stap X en Y moeten eerst worden afgerond" | Niets — B-inputs ontbreken |
| ⚠️ Beschikbaar met waarschuwing | "Je kunt starten, maar let op: [wat ontbreekt]" | Stap starten, waarschuwing blijft zichtbaar |
| ✅ Volledig beschikbaar | Geen melding | Stap starten |

Waarschuwing verdwijnt niet bij starten — blijft zichtbaar totdat de W-input alsnog is afgerond. Gebaseerd op de B/W-dataflow-tabellen uit punt 2.

### K3. Accordering (vastgesteld 18 maart 2026)

Optie A: naam + functie + datum + IP-adres vastgelegd in besluitlog. Immutable na accordering. Exporteerbaar als PDF met alle metadata. Voldoende voor ISO-audit.

```
Accordering:
  vastgesteld_door: "{{NAAM}}"
  functie:          "{{FUNCTIE}}"
  datum:            "2026-03-18T14:32:00"
  ip_adres:         "..." (intern gelogd, niet zichtbaar in export)
  besluitlog_id:    "0007"
  → immutable, niet te wijzigen na vastlegging
```
