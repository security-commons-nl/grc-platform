# IMS Handboek — Blueprint

*Generiek skelet voor het IMS Handboek. AI agents vullen de `{{PLACEHOLDER}}`-velden in op basis van wat een organisatie tijdens het IMS-implementatieproces invoert. Dit document is niveau 1 van de IMS-documentenpyramide.*

*Structuur: ISO High Level Structure (HLS) — toepasbaar op ISO 27001, ISO 27701 en ISO 22301.*

---

**Documentpyramide**

```
Niveau 1: IMS Handboek (dit document)  — bestuurlijk kader, governance, scope, PDCA
Niveau 2: Domeinplannen                — BIO-implementatieplan, AVG-procedures, BCP's
Niveau 3: Procedures & werkinstructies — concrete werkwijzen, checklists, templates
Niveau 4: Registraties & bewijs        — risicoregister, SoA, auditlogboeken, GRC-tool
```

*Dit handboek beschrijft het kader en verwijst naar niveau 2-documenten. Details en uitwerkingen horen daar thuis, niet hier.*

---

**Documentbeheer**

| Veld | Waarde |
|------|--------|
| Organisatie | {{GEMEENTE_NAAM}} |
| Versie | {{VERSIE}} |
| Datum | {{DATUM}} |
| Eigenaar | {{DOCUMENT_EIGENAAR}} |
| Vastgesteld door | {{VASTGESTELD_DOOR}} |
| Geldig tot | {{GELDIG_TOT}} |

---

## Inhoud

1. Onderwerp en toepassingsgebied
2. Normatieve verwijzingen
3. Termen en definities
4. Context van de organisatie
5. Governance & Leiderschap
6. Planning
7. Ondersteuning
8. Uitvoering
9. Evaluatie van de prestaties
10. Verbetering
- Bijlage 1: Belanghebbenden
- Bijlage 2: Formele escalatieprocedure
- Bijlage 3: Risicobeoordelingsmethodiek

---

## 1. Onderwerp en toepassingsgebied

Dit document beschrijft de manier waarop het Integraal Management Systeem, hierna IMS, binnen {{GEMEENTE_NAAM}} is ingericht.

Het IMS van {{GEMEENTE_NAAM}} beschrijft de bestuurlijke inrichting, beheersstructuur en verbetercyclus voor:

- Informatiebeveiliging (ISMS)
- Privacybescherming (PIMS)
- Bedrijfscontinuïteit (BCMS)

Het IMS borgt dat deze domeinen:

- Integraal worden aangestuurd
- Risicogestuurd worden beheerst
- Structureel worden gemonitord
- Continu worden verbeterd

{{GEMEENTE_NAAM}} is verplicht aan de BIO 2.0 te voldoen, waarin expliciet staat opgenomen dat een managementsysteem moet worden ingericht volgens de ISO 27001. Omdat er ook afgeleide normen bestaan voor bedrijfscontinuïteit (ISO/IEC 22301) en privacy (ISO/IEC 27701) is gekozen om het IMS te baseren op de High Level Structure (HLS) van de ISO-managementsystemen.

---

## 2. Normatieve verwijzingen

Dit document en het beleid zijn gebaseerd op de normatieve referentie van:

- De BIO 2.0 als gemeentelijke specifieke norm
- De ISO/IEC 27001 als algemeen leidraad voor de inrichting van het IMS en de norm waar de BIO 2.0 op is gebaseerd
- De Cyberbeveiligingswet en de NIS2-richtlijn
- De ISO/IEC 22301 als leidraad voor bedrijfscontinuïteit
- De ISO/IEC 27701 als leidraad voor privacy
- De Algemene Verordening Gegevensbescherming (AVG)

Overige normen, wetgeving en beleidskaders die niet zien op de werking van het IMS, maar waar de organisatie wel aan moet voldoen, worden genoemd in §4.1.2 als onderdeel van de contextanalyse.

---

## 3. Termen en definities

In dit document worden verschillende termen gebruikt. Wanneer de termen niet expliciet beschreven zijn, gebruiken we de definities zoals die in hoofdstuk 3 van de BIO 2.0 of in de ISO/IEC normen zijn beschreven.

---

## 4. Context van de organisatie

### 4.1 De context

De contextanalyse vormt de basis voor het IMS en de keuzes die daarbinnen worden gemaakt.

{{CONTEXT_BESCHRIJVING}}

In de context worden de volgende elementen herkend:

- Ambities en maatschappelijke impact
- Wet- en regelgeving
- Dreigingen en ontwikkelingen
- Ketenafhankelijkheden
- Interne organisatie
- Strategisch kader

De contextanalyse is specifiek gericht op het overkoepelende IMS. Het kan zijn dat het voor bedrijfscontinuïteit, informatiebeveiliging of privacy noodzakelijk is om een aanvullende analyse te doen. Hiervoor worden dezelfde stappen gevolgd, maar dan specifiek voor de betreffende discipline.

#### 4.1.1 Ambities en maatschappelijke impact

{{AMBITIES_BESCHRIJVING}}

Als overheid heeft de gemeente een bijzondere verantwoordelijkheid. Verstoring of falen kan leiden tot:

- Beperking van essentiële dienstverlening
- Aantasting van grondrechten (privacy, gelijke behandeling) en ander onrechtmatig handelen
- Financiële schade voor inwoners en ondernemers
- Vertrouwensverlies in het lokaal bestuur
- Politieke en bestuurlijke consequenties

De maatschappelijke impact van incidenten is vaak groter dan de directe operationele schade. Daarom hanteert de gemeente een risicobenadering waarin maatschappelijke effecten expliciet worden meegewogen bij risicoanalyses en prioritering van maatregelen.

#### 4.1.2 Wet- en regelgeving

De gemeente heeft te maken met een uitgebreid en dynamisch wettelijk kader. De volgende wettelijke kaders zijn van belang:

- De Algemene verordening gegevensbescherming (AVG)
- De Wet politiegegevens (Wpg)
- De Wet justitiële en strafvorderlijke gegevens (Wjsg)
- De Wet open overheid (Woo)
- De Archiefwet 1995
- De Wet beveiliging netwerk- en informatiesystemen (Wbni) — voor zover van toepassing
- De Wet weerbaarheid kritieke entiteiten (Wwke) — voor zover de organisatie wordt aangewezen als kritieke entiteit
- Gemeentelijke regelgeving, sectorale normen (zoals BIO) en relevante Europese regelgeving

Wijzigingen in wet- en regelgeving, toezichtkaders en jurisprudentie vormen een continue bron van compliance- en reputatierisico's. Het IMS borgt dat relevante ontwikkelingen structureel worden gevolgd en vertaald naar beleid en maatregelen.

#### 4.1.3 Dreigingen en ontwikkelingen

De gemeente opereert in een dreigingslandschap dat continu verandert. Belangrijke dreigingscategorieën zijn:

**Cyberdreigingen**
- Ransomware, phishing en datalekken
- Gerichte aanvallen op gemeentelijke infrastructuur
- Verstoring van digitale dienstverlening

**Informatierisico's**
- Onrechtmatige of onzorgvuldige verwerking van persoonsgegevens
- Onvoldoende toegangsbeheer of logging
- Onbetrouwbare of onvolledige gegevens

**Fysieke en maatschappelijke dreigingen**
- Stroomuitval, brand, wateroverlast of pandemieën
- Maatschappelijke onrust of incidenten met grote bestuurlijke impact
- Desinformatie en reputatieschade

**Organisatorische factoren**
- Toenemende digitalisering en afhankelijkheid van ICT
- Krapte op de arbeidsmarkt en kennisafhankelijkheid
- Veranderende bestuurlijke prioriteiten

Deze dreigingen beïnvloeden zowel de vertrouwelijkheid, integriteit en beschikbaarheid van informatie als de continuïteit van primaire processen.

#### 4.1.4 Ketenafhankelijkheden

De gemeente opereert in een uitgebreid netwerk van ketenpartners, leveranciers en samenwerkingsverbanden. Voorbeelden zijn:

- Gemeenschappelijke regelingen en regionale samenwerkingsverbanden
- Landelijke voorzieningen (zoals basisregistraties)
- ICT-leveranciers en cloud-dienstverleners
- Zorg- en veiligheidsketens

De afhankelijkheid van externe partijen vergroot het risico op:

- Uitval van dienstverlening door verstoringen bij leveranciers
- Onvoldoende beveiligingsniveau in de keten
- Onduidelijkheid over verantwoordelijkheden bij incidenten
- Complexiteit bij gegevensuitwisseling

Het IMS adresseert deze ketenrisico's door:

- Heldere contractuele afspraken (beveiliging, privacy, continuïteit)
- Leveranciersbeoordelingen en -monitoring
- Afstemming van incidentmanagement
- Structurele ketensamenwerking en informatie-uitwisseling

#### 4.1.5 Interne context

Naast externe factoren spelen interne kenmerken een belangrijke rol:

- De bestuurlijke en ambtelijke structuur
- De mate van digitalisering van processen
- De risicobereidheid (risk appetite) van het bestuur
- De volwassenheid van processen en interne beheersing
- De cultuur rondom informatiebewustzijn en compliance

Deze factoren bepalen mede de effectiviteit van beheersmaatregelen en de haalbaarheid van verbetertrajecten.

#### 4.1.6 Strategisch kader

{{VISIE}}

{{MISSIE}}

{{STRATEGIE}}

De strategie is SMART gemaakt door hier specifieke doelstellingen aan te verbinden (zie verder: §6.2).

#### 4.1.7 SWOT-analyse

{{GEMEENTE_NAAM}} heeft middels een SWOT-analyse haar interne sterktes, zwaktes en externe kansen en bedreigingen geïdentificeerd, die van invloed zijn op het vermogen om de beoogde uitkomsten van het IMS te realiseren.

{{SWOT_ANALYSE}}

*Tabel: interne factoren (sterktes / zwaktes) en externe factoren (kansen / bedreigingen) — minimaal 3 per kwadrant.*

Het analyseren van bovenstaande issues wordt gebruikt om:

- Het toepassingsgebied van het managementsysteem te kunnen bij- en/of vaststellen
- De aan de context gerelateerde risico's en kansen te kunnen bij- en/of vaststellen

Bovenstaande wordt gereviewed en aangepast als gevolg van grote wijzigingen, dan wel als onderdeel van de periodieke directiebeoordeling.

### 4.2 Behoefte en verwachtingen van belanghebbenden

De gemeente identificeert relevante belanghebbenden en hun eisen. Deze eisen worden vertaald naar beheersdoelstellingen binnen het IMS. Stakeholdereisen worden periodiek geëvalueerd. De belanghebbendenanalyse is terug te vinden in Bijlage 1.

Deze belanghebbendenanalyse wordt gebruikt voor:

- Vaststellen van scope van het IMS
- Identificeren van compliance-verplichtingen
- Input voor risicoanalyse
- Directiebeoordeling
- Actualisatie van beleidskaders

De analyse wordt minimaal jaarlijks herzien of bij significante organisatorische of wettelijke wijzigingen.

### 4.3 Toepassingsgebied van het IMS

Het toepassingsgebied kent twee niveaus: de overkoepelende IMS-scope en de domein-specifieke scopes.

#### Overkoepelende IMS-scope

{{IMS_SCOPE_ORGANISATIE}}

*Welke organisatieonderdelen, rechtspersonen en/of samenwerkingsverbanden vallen onder dit IMS. Vastgesteld door SIMS (stap 2b van het IMS-implementatieproces).*

#### Domein-specifieke scopes

| Domein | Scope | Eigenaar |
|--------|-------|---------|
| **ISMS** (informatiebeveiliging) | {{ISMS_SCOPE}} | {{ISMS_EIGENAAR}} |
| **PIMS** (privacy) | Alle verwerkingen van persoonsgegevens conform AVG art. 30 | {{PIMS_EIGENAAR}} |
| **BCMS** (bedrijfscontinuïteit) | {{BCMS_SCOPE}} | {{BCMS_EIGENAAR}} |

*De PIMS-scope omvat per definitie alle verwerkingen — de AVG laat hier geen keuzeruimte. De ISMS- en BCMS-scopes worden nader uitgewerkt in de respectievelijke domeinplannen (niveau 2). De BCMS-scope wordt definitief bepaald na de Business Impact Analyse (BIA, stap 9).*

De domein-specifieke uitwerking is opgenomen in:

- ISMS: {{VERWIJZING_BIO_IMPLEMENTATIEPLAN}}
- PIMS: {{VERWIJZING_AVG_PROCEDURES}}
- BCMS: {{VERWIJZING_BCP_DOCUMENTEN}}

Het toepassingsgebied wordt jaarlijks beoordeeld.

### 4.4 Functioneren van het IMS

Beoogd wordt het vastgestelde IMS te onderhouden en continu te verbeteren. Dit betekent dat:

- De behoeften en verwachtingen van de organisatie en belanghebbenden worden opgenomen en onderhouden met betrekking tot bedrijfscontinuïteit, informatiebeveiliging en privacy
- Beleidsregels, processen, procedures en standaarden worden samengebracht, gepland, opgesteld, goedgekeurd, geïmplementeerd, gecontroleerd en regelmatig herzien
- Het IMS een periodieke risicobeoordeling doorloopt, op basis waarvan geïdentificeerde risico's en kansen worden aangepakt
- De effectiviteit en efficiëntie van het IMS worden beoordeeld via onafhankelijke interne audits, prestatiebewaking en directiebeoordelingen
- Opleidings- en ontwikkelingsbehoeften in kaart worden gebracht en beschikbaar worden gesteld
- Alle non-conformiteiten worden gerapporteerd, onderzocht en tijdig actie op wordt ondernomen
- Voor afgenomen diensten bij derden de informatiebeveiliging wordt gecontroleerd door middel van geschikte contracten, SLA's, monitoring en audits

---

## 5. Governance & Leiderschap

### 5.1 Verantwoordelijkheid Directieteam

Het Directieteam is eindverantwoordelijk voor:

- Vaststelling van beleid
- Beschikbaar stellen van middelen
- Sturing op strategische risico's
- Acceptatie van restrisico's
- Toezicht op werking van het IMS

### 5.2 Rollen en verantwoordelijkheden binnen het IMS

Binnen het IMS gelden de volgende uitgangspunten:

- Risico-eigenaarschap ligt altijd in de lijn
- Kaderstelling en advies liggen in de tweede lijn
- Onafhankelijke toetsing ligt in de derde lijn
- Strategische risicoacceptatie ligt bij het directieteam

Deze rolverdeling wordt periodiek geëvalueerd in het kader van de directiebeoordeling.

### 5.3 Overlegstructuren

Het IMS kent een gelaagde overleg- en besluitvormingsstructuur conform het Three Lines Model en de PDCA-cyclus. De overlegstructuur waarborgt:

- Strategische sturing
- Tactische coördinatie
- Operationele uitvoering
- Transparante rapportage en escalatie

De overlegstructuur kent drie niveaus:

- Strategisch (SIMS)
- Tactisch (TIMS)
- Operationeel (discipline-eigenaren)

Een formele escalatieprocedure is te vinden in Bijlage 2.

#### 5.3.1 Stuurgroep / Strategisch IMS-team (SIMS)

**Implementatiefase**

Tijdens de implementatiefase fungeert de stuurgroep als bestuurlijk opdrachtgever van het IMS. De stuurgroep:

- Bewaakt scope, planning en voortgang van implementatie
- Stelt kaders en prioriteiten vast
- Neemt besluiten over inrichting en positionering van het IMS
- Bewaakt samenhang tussen privacy, informatiebeveiliging en bedrijfscontinuïteit
- Beslist over escalaties vanuit de regiegroep
- Rapporteert rechtstreeks aan het directieteam

De stuurgroep beschikt over mandaat van het directieteam voor besluitvorming binnen de vastgestelde scope, inclusief prioritering van middelen.

**Beheerfase (SIMS)**

Na implementatie gaat de stuurgroep over in het Strategisch IMS-team (SIMS). Het SIMS is verantwoordelijk voor:

- Vaststellen en herzien van IMS-beleid
- Vaststellen van strategische doelstellingen
- Acceptatie van restrisico's op strategisch niveau
- Bewaken van samenhang tussen organisatiedoelen en IMS
- Toezien op effectiviteit van het IMS
- Voorbereiden van de bestuurlijke managementreview
- Escalatieniveau voor risico's of afwijkingen die het tactisch niveau overstijgen

**Samenstelling SIMS:**

{{SIMS_SAMENSTELLING}}

*De CISO, FG en Interne Accountant zijn 3e lijn (onafhankelijk toezicht) en nemen daarom geen deel aan SIMS als lid. Zij kunnen worden uitgenodigd als adviseur zonder beslisrecht.*

**Frequentie:** Het SIMS komt minimaal ieder kwartaal bijeen. Indien nodig kan een extra vergadering worden ingelast bij significante risico's of incidenten.

#### 5.3.2 Regiegroep / Tactisch IMS-team (TIMS)

**Implementatiefase**

Gedurende de implementatie is de regiegroep verantwoordelijk voor:

- Ontwerp en inrichting van het IMS
- Uitwerking van beleidsstructuur
- Vaststellen van procesinrichting
- Coördineren van implementatieactiviteiten
- Voorbereiden van besluitvorming door de stuurgroep

De regiegroep heeft mandaat om voorstellen te doen en ontwerpkeuzes te maken, maar formele vaststelling geschiedt door de stuurgroep.

**Beheerfase (TIMS)**

Na implementatie wordt de regiegroep het Tactisch IMS-team (TIMS). Het TIMS is verantwoordelijk voor de integrale coördinatie van het IMS en borgt de werking van de PDCA-cyclus. Het TIMS:

- Coördineert risico-identificatie en actualisatie
- Bewaakt voortgang van doelstellingen
- Consolideert rapportages vanuit disciplines
- Bereidt managementreview voor
- Stuurt discipline-eigenaren functioneel aan
- Signaleert samenhangende risico's over disciplines heen
- Adviseert SIMS over strategische keuzes
- Heeft mandaat om binnen vastgestelde beleidskaders prioriteiten te stellen en corrigerende acties uit te zetten

**Escalatie naar SIMS** vindt plaats bij:

- Overschrijding van risicobereidheid
- Structurele non-conformiteiten
- Beleidsmatige keuzes
- Capaciteits- of prioriteringsconflicten

**Samenstelling TIMS:**

{{TIMS_SAMENSTELLING}}

*De CISO, FG en Interne Accountant zijn 3e lijn (onafhankelijk toezicht) en nemen daarom geen deel aan TIMS. Zij worden op uitnodiging gehoord als adviseur.*

**Frequentie:** Het TIMS komt maandelijks bijeen. Bij verhoogd risicoprofiel kan de frequentie tijdelijk worden verhoogd.

#### 5.3.3 Operationele sturing (discipline-eigenaren)

De operationele sturing binnen het IMS is belegd bij discipline-eigenaren. Een discipline-eigenaar is integraal verantwoordelijk voor de werking van de PDCA-cyclus binnen zijn of haar domein.

**Verantwoordelijkheden discipline-eigenaar:**

- Borgt uitvoering van vastgesteld beleid
- Actualiseert het risicoprofiel binnen de discipline
- Zorgt voor tijdige rapportage
- Initieert verbetermaatregelen
- Borgt opvolging van auditbevindingen
- Escaleert restrisico's of afwijkingen naar TIMS
- Zorgt voor documentatie en registratie

De discipline-eigenaar kan operationele taken delegeren, maar blijft verantwoordelijk voor de beheersing binnen het domein.

**Toewijzing discipline-eigenaren:**

{{DISCIPLINE_EIGENAREN_TOEWIJZING}}

Bij samenloop van verantwoordelijkheden waarborgt het TIMS integrale afstemming.

### 5.4 Integratie met het Three Lines Model

#### Uitgangspunt

De gemeente hanteert het Three Lines Model als structuur voor verantwoordelijkheidsverdeling binnen het IMS. Het model waarborgt:

- Heldere rolverdeling
- Onafhankelijke toetsing
- Voorkomen van belangenverstrengeling
- Transparante verantwoording

#### Eerste lijn — Uitvoering en eigenaarschap

De eerste lijn bestaat uit proceseigenaren, discipline-eigenaren en lijnmanagement. Zij zijn verantwoordelijk voor:

- Uitvoering van beleid
- Identificatie van risico's
- Implementatie van beheersmaatregelen
- Registratie van afwijkingen
- Rapportage aan TIMS

De eerste lijn is eigenaar van risico's.

#### Tweede lijn — Kaderstelling en coördinatie

De tweede lijn bestaat uit functies die kaders stellen, adviseren en monitoren. De tweede lijn:

- Ontwikkelt beleidskaders
- Ondersteunt bij risicobeoordeling
- Monitort naleving
- Adviseert over escalatie
- Consolideert rapportages richting TIMS

De tweede lijn is niet verantwoordelijk voor operationele uitvoering.

#### Derde lijn — Onafhankelijk toezicht

De derde lijn (CISO, FG, Interne Accountant/Auditfunctie):

- Toetst onafhankelijk de effectiviteit van het IMS
- Beoordeelt naleving van beleid en normenkader
- Rapporteert rechtstreeks aan het directieteam
- Doet aanbevelingen voor verbetering

De derde lijn heeft geen uitvoerende, kaderstellende of besluitvormende rol in SIMS of TIMS. Zij worden op uitnodiging gehoord als adviseur.

#### Relatie met SIMS en TIMS

- Discipline-eigenaren (1e lijn) rapporteren aan TIMS
- Tweede lijn functies participeren in TIMS
- Derde lijn rapporteert onafhankelijk aan directieteam en deelt bevindingen met SIMS
- SIMS bewaakt de samenhang tussen de drie lijnen en ziet toe op onafhankelijke positionering van toezicht

#### Waarborgen van onafhankelijkheid

Om rolvermenging te voorkomen:

- De derde lijn neemt geen deel aan besluitvorming over risicobehandeling
- De tweede lijn is niet eindverantwoordelijk voor risicoacceptatie
- Risicoacceptatie vindt uitsluitend plaats op het daartoe gemandateerde bestuurlijke niveau

Deze scheiding wordt periodiek geëvalueerd tijdens de directiebeoordeling.

### 5.5 Rapportagestructuren

De rapportagestructuur volgt de hiërarchie van het IMS en sluit aan op de PDCA-cyclus.

{{RAPPORTAGE_TABEL}}

*Rapportages over de werking van het IMS worden periodiek opgemaakt door de verschillende lagen. Rapportages over individuele beheersmaatregelen (opzet-bestaan-werking) zijn onderdeel van de maatregel zelf en worden op operationeel niveau voorgelegd aan discipline-eigenaren, die een algemeen beeld meenemen in hun IMS-rapportage aan het TIMS.*

---

## 6. Planning

Dit hoofdstuk beschrijft hoe de gemeente het IMS planmatig inricht, aanstuurt en ontwikkelt. Planning binnen het IMS is risicogestuurd en sluit aan bij de strategische doelstellingen van de organisatie.

### 6.1 Acties om risico's te beperken en kansen te benutten

#### 6.1.1 Risicogestuurde benadering

De gemeente hanteert een integrale risicomanagementmethodiek voor informatiebeveiliging, privacy en bedrijfscontinuïteit. Risicomanagement is gebaseerd op:

- Periodieke en gestructureerde risico-inventarisatie
- Risicoanalyse op basis van kans en impact
- Bestuurlijk vastgestelde risicobereidheid (risk appetite)
- Expliciete acceptatie van restrisico's op het juiste niveau
- Herleidbare documentatie van risicobeoordelingen

Het risicomanagementproces omvat: identificatie → analyse → evaluatie → behandeling → acceptatie → monitoring. Risico's worden vastgelegd in de GRC-tool.

#### 6.1.2 Privacy-specifieke analyse (DPIA)

Voor verwerkingen met verhoogd risico wordt een gestructureerde privacy-risicobeoordeling (DPIA) uitgevoerd. Deze wordt uitgevoerd voorafgaand aan nieuwe of gewijzigde verwerkingen, herzien bij materiële wijzigingen, en betrokken bij besluitvorming. De FG houdt toezicht op correcte toepassing.

De uitwerking is beschreven in {{VERWIJZING_DPIA_PROCEDURE}}.

#### 6.1.3 Privacy by Design

Bij de ontwikkeling of wijziging van processen, systemen of verwerkingen waarin persoonsgegevens worden verwerkt, wordt privacy by design toegepast conform ISO 27701 7.4/8.4 en AVG art. 25. Privacyaspecten worden meegenomen vanaf de ontwerpfase en standaardinstellingen zijn gericht op minimale gegevensverwerking.

De uitwerking is beschreven in {{VERWIJZING_PBD_PROCEDURE}}.

#### 6.1.4 Business Impact Analyse

Ten behoeve van bedrijfscontinuïteit wordt een periodieke Business Impact Analyse (BIA) uitgevoerd. De BIA identificeert kritieke processen, bepaalt MTPD, RTO en RPO, en levert input voor prioritering binnen het IMS. De BIA wordt minimaal jaarlijks herijkt.

De uitwerking is beschreven in {{VERWIJZING_BIA_DOCUMENT}}.

#### 6.1.5 Kansen

Naast risico's identificeert de gemeente kansen die bijdragen aan versterking van beheersing, verbetering van rapportage, verhoging van IMS-volwassenheid en efficiëntere integratie van disciplines. Kansen worden meegenomen in jaarplanning en doelstellingen.

### 6.2 IMS-doelstellingen en plannen om ze te bereiken

Jaarlijks worden IMS-doelstellingen vastgesteld door het directieteam op advies van het SIMS. De doelstellingen zijn SMART geformuleerd, gekoppeld aan risico's en prioriteiten, en meetbaar en tijdgebonden.

{{IMS_DOELSTELLINGEN}}

De jaarplanning bevat: planning risicoherijking, auditplanning, managementreviewmomenten, evaluatie doelstellingen, rapportagemomenten en herziening van beleid. De planning is geïntegreerd in de reguliere planning- en controlcyclus.

### 6.3 Plannen van wijzigingen

Wijzigingen met impact op het IMS (organisatorisch, wetgeving, technologie, scope, risicoprofiel) worden beheerst doorgevoerd: voorafgaande impactanalyse, betrokkenheid relevante rollen, documentatie van besluitvorming.

### 6.4 Samenhang binnen het IMS

Privacy, informatiebeveiliging en bedrijfscontinuïteit volgen één gezamenlijke planningscyclus, één integraal risicoregister en één verbetercyclus.

### 6.5 Evaluatie van de planningcyclus

De effectiviteit van de planningscyclus wordt minimaal jaarlijks beoordeeld tijdens de directiebeoordeling.

---

## 7. Ondersteuning

### 7.1 Middelen

Het directieteam stelt via SIMS en TIMS voldoende financiële middelen en tooling beschikbaar om het IMS op te zetten, te implementeren, te onderhouden en continu te verbeteren.

### 7.2 Competenties

De organisatie zorgt voor adequate competentie door middel van duidelijke rolbeschrijvingen voor betrokken rollen en heldere verantwoordelijkheden voor iedereen die werkt met informatie van de organisatie.

### 7.3 Bewustzijn

Opleiding voor iedereen die met informatie van de organisatie werkt omvat bewustzijn van het IMS-beleid, verwachtingen voor al het personeel en de implicaties van het niet naleven van IMS-verplichtingen. Dit omvat domein-specifieke content voor privacy (AVG-bewustzijn), informatiebeveiliging (BIO-bewustzijn) en bedrijfscontinuïteit (gedrag bij verstoring).

### 7.4 Communicatie

Om adequaat begrip van het IMS te garanderen, wordt regelmatig gecommuniceerd met interne en externe belanghebbenden:

- Regelmatige nieuwsberichten bij verhoogde risico's of incidenten
- Jaarlijkse directiebeoordelingen opgesteld door het TIMS
- Organisatiebrede communicatie indien nodig, opgesteld door discipline-eigenaren
- Updates over beleid aan alle belanghebbenden

De communicatiematrix is opgenomen in {{VERWIJZING_COMMUNICATIEMATRIX}}.

### 7.5 Gedocumenteerde informatie

De organisatie zorgt ervoor dat geschikte gedocumenteerde informatie het IMS ondersteunt:

- Dit IMS-handboek
- Het risicomanagementproces (Bijlage 3)
- Het IMS-beleid en domeinspecifieke beleidsdocumenten
- Processen ter ondersteuning van de drie domeinen
- Een centraal beheerd risicoregister (GRC-tool)
- Een Verklaring van Toepasselijkheid (VvT)

Alle IMS-documenten volgen het documentbeheersproces: titel, aanmaakdatum, auteur, versie, goedkeuringsvereisten, classificatie. Het documentbeheersproces is beschreven in {{VERWIJZING_DOCUMENTBEHEERPROCEDURE}}.

---

## 8. Uitvoering

### 8.1 Operationele planning en beheersing

Er is een reeks processen, procedures en beheersmaatregelen gedefinieerd en geïmplementeerd om te voldoen aan de eisen van het IMS en de eisen afgeleid van de risicobeoordeling. De uitwerking per domein is opgenomen in de domeinplannen (niveau 2).

### 8.2 Risicobeoordeling

Alle risicoanalyses volgen het risicomanagementproces beschreven in Bijlage 3.

#### Strategische risicoanalyse

{{STRATEGISCHE_RISICOANALYSE_BESCHRIJVING}}

De focus van de strategische risicoanalyse is het identificeren, analyseren en monitoren van risico's die de organisatie dusdanig kunnen raken dat kritische of catastrofale gevolgen worden ondervonden.

#### Operationele risicoanalyse

{{OPERATIONELE_RISICOANALYSE_BESCHRIJVING}}

#### DPIA's

In §6.1.2 staat uitgelegd wanneer en hoe een DPIA uitgevoerd moet worden.

#### Overige momenten voor een risicoanalyse

Een risicoanalyse vindt ook plaats bij:

- Organisatorische of technologische wijzigingen
- Significante veranderingen in de context
- Op verzoek van directieteam, SIMS of een proceseigenaar
- Bij de start van een project

### 8.3 Risicobereidheid

De risicobereidheid is bestuurlijk vastgesteld en kent vier niveaus:

| Niveau | Escalatie naar | Actie |
|--------|---------------|-------|
| 🔴 **Rood** | Directieteam (via SIMS) | Direct melden met actieplan. Moet worden gemitigeerd. |
| 🟠 **Oranje** | SIMS (via TIMS) | Direct voorleggen met actieplan. Maximaal 6 maanden onbehandeld mits actieplan loopt. Moet worden gemitigeerd, tenzij directieteam restrisico accepteert. |
| 🟡 **Geel** | TIMS | Melden door discipline-eigenaar met plan van aanpak. TIMS beslist over maatregelen. Acceptatie door TIMS, onderbouwd. SIMS kan bepalen dat zij niet akkoord gaan. |
| 🟢 **Groen** | Discipline-eigenaar of risico-eigenaar | Monitort. Mag onderbouwd accepteren. TIMS kan bepalen dat zij niet akkoord gaan. |

De nadere uitwerking (impactschalen, kansschalen, risicomatrix) is opgenomen in Bijlage 3.

### 8.4 Risicobehandeling

Er is een set van beheersmaatregelen gedefinieerd. Maatregelen omvatten documentatie, implementatie en effectiviteitsindicatoren. Alle maatregelen worden, indien mogelijk, centraal beheerd in de GRC-tool.

De uitwerking per domein:

- ISMS: {{VERWIJZING_BIO_IMPLEMENTATIEPLAN}}
- PIMS: {{VERWIJZING_AVG_PROCEDURES}}
- BCMS: {{VERWIJZING_BCP_DOCUMENTEN}}

### 8.5 PII-doorgifte (transfers)

Bij doorgifte van persoonsgegevens aan derden, verwerkers of naar derde landen wordt getoetst of passende waarborgen zijn getroffen conform ISO 27701 7.5/8.5 en de AVG. Dit omvat:

- Inventarisatie van alle doorgiften (intern, extern, grensoverschrijdend)
- Beoordeling van de rechtsgrondslag per doorgifte
- Vaststelling van passende waarborgen (verwerkersovereenkomsten, SCCs, adequaatheidsbesluit)
- Periodieke herbeoordeling

De doorgifte-inventarisatie is opgenomen in {{VERWIJZING_DOORGIFTE_REGISTER}}.

### 8.6 Incidentmanagement

De gemeente heeft een geïntegreerd incidentmanagementproces ingericht voor informatiebeveiligingsincidenten, datalekken en continuïteitsverstoringen, conform ISO 27001 A.5.24-28 en AVG art. 33/34. Het proces omvat:

- Classificatie en prioritering van incidenten
- Responsprocedure met escalatie naar het juiste niveau
- Melding aan toezichthouders waar wettelijk vereist (AP bij datalekken binnen 72 uur, betrokkenen bij hoog risico)
- Registratie en opvolging
- Lessons learned en structurele verbetering

De uitwerking is beschreven in {{VERWIJZING_INCIDENTPROCEDURE}}.

---

## 9. Evaluatie van de prestaties

### 9.1 Monitoren, meten, analyseren en evalueren

De doeltreffendheid van het IMS wordt geëvalueerd op basis van omschreven doelstellingen. De rapportagestructuur is beschreven in §5.5.

### 9.2 Interne audit

In aanvulling op interne evaluaties worden onafhankelijke interne audits uitgevoerd. Op basis van een risicoanalyse kunnen de volgende onderwerpen worden betrokken:

- Werking van de PDCA-cyclus of onderdelen daarvan
- Mate van opvolging van eerdere aanbevelingen
- Kwaliteit van interne rapportages
- Kwaliteit en tijdigheid van risico-inventarisaties en maatregelen
- Hantering van de juiste normen

Het auditprogramma is opgenomen in {{VERWIJZING_AUDITPROGRAMMA}}.

### 9.3 BC-oefeningen

Om de effectiviteit van continuïteitsplannen te toetsen, worden periodiek oefeningen uitgevoerd conform ISO 22301 8.5. Het oefenprogramma omvat:

- Jaarlijkse planning van oefeningen (opgenomen in de IMS-jaarplanning)
- Variatie in oefenvormen (tabletop, functioneel, fullscale)
- Evaluatie en rapportage na elke oefening
- Opvolging van verbeterpunten

De uitwerking is beschreven in {{VERWIJZING_OEFENPROGRAMMA}}.

### 9.4 Directiebeoordeling

Op jaarlijkse basis (of na een ernstig incident of datalek) vindt een directiebeoordeling plaats. Minimaal aan de orde:

- Status gedefinieerde actiepunten (n.a.v. vorige directiebeoordeling)
- Wijzigingen in interne en externe context en feedback van belanghebbenden
- Trends in prestaties van het IMS:
  - Afwijkingen en corrigerende maatregelen
  - Resultaten monitoring- en meetresultaten
  - Auditresultaten
  - Resultaten BC-oefeningen
  - Realisatie van IMS-doelstellingen
  - Resultaten strategische risicobeoordelingen
  - Mogelijkheden voor continue verbetering

De output wordt vastgelegd en vertaald naar concrete plannen.

---

## 10. Verbetering

### 10.1 Afwijkingen en corrigerende maatregelen

Wanneer afwijkingen geconstateerd worden, wordt hierop tijdig gereageerd:

1. Oorzaak achterhalen
2. Actie ondernemen om de afwijking te beheersen
3. Beoordelen of de afwijking elders ook optreedt
4. Gevolgen aanpakken
5. Maatregelen nemen om herhaling te voorkomen
6. Doeltreffendheid van preventieve maatregelen beoordelen
7. Indien nodig het IMS bijwerken

### 10.2 Continue verbetering

De geschiktheid, toereikendheid en effectiviteit van het IMS wordt voortdurend verbeterd op basis van de PDCA-cyclus.

---

## Bijlage 1: Belanghebbenden

{{BELANGHEBBENDEN_ANALYSE}}

*Minimale inhoud: naam/groep belanghebbende, belang/verwachting, relevantie voor IMS (scope/compliance/risico/review), evaluatiefrequentie.*

---

## Bijlage 2: Formele escalatieprocedure

### Doel en uitgangspunten

De formele escalatieprocedure waarborgt dat risico's, afwijkingen en tekortkomingen tijdig, transparant en proportioneel worden opgepakt op het juiste bestuurlijke niveau.

Escalatie vindt plaats op basis van vooraf vastgestelde criteria, niet uitsluitend op basis van hiërarchie.

### Escalatiecriteria

Escalatie is verplicht wanneer:

- Vastgestelde risicobereidheid wordt overschreden
- Structurele of herhaalde non-conformiteiten optreden
- Onvoldoende voortgang bij corrigerende maatregelen
- Onvoldoende middelen om risico's te beheersen
- Domeinoverstijgende risico's met organisatorische impact
- Juridische of reputatiegevoelige kwesties
- Noodzaak tot formele restrisicoacceptatie

### Escalatieniveaus

**Niveau 1 — Discipline-eigenaar (Operationeel)**
Beoordeelt afwijkingen binnen eigen domein, neemt corrigerende maatregelen binnen mandaat, legt vast, escaleert indien criteria worden overschreden.

**Niveau 2 — TIMS (Tactisch)**
Escalatie bij: risico dat meerdere disciplines raakt, aanvullende middelen of prioritering nodig, beleidsinterpretatie vereist. TIMS beoordeelt impact, stelt mitigerende richting vast, documenteert.

**Niveau 3 — SIMS (Strategisch)**
Escalatie bij: restrisicoacceptatie op strategisch niveau, beleidsaanpassing noodzakelijk, organisatiebrede impact, bestuurlijke of maatschappelijke consequenties. Besluiten expliciet vastgelegd inclusief motivatie en geldigheidsduur.

**Niveau 4 — Directieteam**
Escalatie bij: structureel systeemfalen, strategische herijking van het IMS, substantiële reputatie- of aansprakelijkheidsrisico's, wijziging van risicobereidheid. Het directieteam is eindverantwoordelijk voor acceptatie van restrisico's.

---

## Bijlage 3: Risicobeoordelingsmethodiek

### Overzicht

Het risicomanagementproces vormt de basis waarop alle risicoanalyses binnen het IMS draaien. Deze bijlage beschrijft de methodiek, schalen en acceptatiecriteria.

{{RISICOMANAGEMENT_PROCESDIAGRAM}}

### Impactschalen

{{IMPACTSCHALEN_TABEL}}

*De impactschalen dekken minimaal: financiële impact, maatschappelijke impact, reputatieschade, juridische en bestuurlijke impact, operationele impact.*

### Kansschalen

{{KANSSCHALEN_TABEL}}

### Risicomatrix

{{RISICOMATRIX}}

### Acceptatiecriteria

De acceptatiecriteria sluiten aan op de risicobereidheid (§8.3):

- 🔴 Rood: niet acceptabel — directe mitigatie vereist, escalatie naar directieteam
- 🟠 Oranje: niet acceptabel — mitigatie vereist, escalatie naar SIMS
- 🟡 Geel: voorwaardelijk acceptabel — TIMS beslist, onderbouwde acceptatie mogelijk
- 🟢 Groen: acceptabel — discipline-eigenaar monitort, onderbouwde acceptatie mogelijk

### Procesuitleg

**1. Identificatie** — scope en context vaststellen, assets inventariseren, dreigingen en kwetsbaarheden identificeren, risico-eigenaar toewijzen.

**2. Analyse** — kans van optreden bepalen (onderbouwd), impact bepalen (financieel + overige categorieën), risicoscore berekenen.

**3. Evaluatie** — risico's prioriteren, vergelijken met risicocriteria (acceptabel vs. niet-acceptabel).

**4. Behandeling** — maatregelen vaststellen: vermijden, mitigeren of overdragen.

**5. Acceptatie** — formeel beslissen conform de escalatieladder (§8.3). Geaccepteerde restrisico's documenteren in het risicoregister.

**6. Monitoring** — periodieke reviews en audits uitvoeren, risicobeoordelingen updaten bij veranderingen, effectiviteit van maatregelen evalueren.

### Aanvullende richtlijnen per domein

{{AANVULLENDE_RICHTLIJNEN_VERWIJZINGEN}}

*Per domein kunnen aanvullende richtlijnen worden opgesteld die aansluiten op de aard van de risicoanalyse (ISMS: dreigingen-gebaseerd, PIMS: verwerkings-gebaseerd, BCMS: BIA-gebaseerd). Deze worden goedgekeurd door het TIMS.*
