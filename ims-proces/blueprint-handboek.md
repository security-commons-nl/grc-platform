# IMS Handboek — Blueprint

*Dit is het generieke skelet (blueprint) van het IMS Handboek. AI agents gebruiken dit template om een gemeente-specifiek handboek te genereren. Placeholders zijn gemarkeerd met `{{PLACEHOLDER}}`.*

*Structuur: ISO High Level Structure (HLS) — toepasbaar op ISO 27001, ISO 27701 en ISO 22301.*

---

## 1. Onderwerp en toepassingsgebied

Dit document beschrijft de manier waarop het Integraal Management Systeem, hierna IMS, binnen {{GEMEENTE_NAAM}} is ingericht.

Het IMS van {{GEMEENTE_NAAM}} beschrijft de bestuurlijke inrichting, beheersstructuur en verbetercyclus voor:
- Informatiebeveiliging
- Privacybescherming
- Business continuity

Het IMS borgt dat deze domeinen:
- Integraal worden aangestuurd
- Risicogestuurd worden beheerst
- Structureel worden gemonitord
- Continu worden verbeterd

{{GEMEENTE_NAAM}} is verplicht aan de BIO 2.0 te voldoen, waarin expliciet staat opgenomen dat een managementsysteem moet worden ingericht volgens de ISO 27001. Omdat er ook afgeleide normen bestaan voor business continuity (ISO/IEC 22301) en privacy (ISO/IEC 27701) is gekozen om het IMS te baseren op de High Level Structure (HLS) van de ISO-managementsystemen.

---

## 2. Normatieve verwijzingen

Dit document en het beleid zijn gebaseerd op de normatieve referentie van:
- De BIO 2.0 als gemeentelijke specifieke norm
- De ISO/IEC 27001 als algemeen leidraad voor de inrichting van het IMS en de norm waar de BIO 2.0 op is gebaseerd
- De Cyberbeveiligingswet en de NIS 2 richtlijn
- De ISO/IEC 22301 als leidraad voor business continuity
- De ISO/IEC 27701 als leidraad voor privacy
- De Algemene Verordening Gegevensbescherming (AVG)

Overige normen, wetgeving en beleidskaders die niet zien op de werking van het IMS, maar waar de organisatie wel aan moet voldoen, worden genoemd in paragraaf 4.1.2 als onderdeel van de contextanalyse.

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

De contextanalyse is specifiek gericht op het overkoepelende IMS. Het kan zijn dat het voor business continuity, informatiebeveiliging of privacy noodzakelijk is om een aanvullende analyse te doen. Hiervoor worden dezelfde stappen gevolgd, maar dan specifiek voor de betreffende discipline.

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

De strategie is SMART gemaakt door hier specifieke doelstellingen aan te verbinden (zie verder: hoofdstuk 6.2).

{{SWOT_ANALYSE}}

Het analyseren van bovenstaande issues wordt gebruikt om:
- Het toepassingsgebied van het managementsysteem te kunnen bij- en/of vaststellen
- De aan de context gerelateerde risico's en kansen te kunnen bij- en/of vaststellen

Bovenstaande wordt gereviewd en aangepast als gevolg van grote wijzigingen, dan wel als onderdeel van de periodieke directiebeoordeling.

### 4.2 Behoefte en verwachtingen van belanghebbenden

De gemeente identificeert relevante belanghebbenden en hun eisen. Deze eisen worden vertaald naar beheersdoelstellingen binnen het IMS. Stakeholdereisen worden periodiek geëvalueerd. De belanghebbendenanalyse is terug te vinden in bijlage 1.

Deze belanghebbendenanalyse wordt gebruikt voor:
- Vaststellen van scope van het IMS
- Identificeren van compliance-verplichtingen
- Input voor risicoanalyse
- Directiebeoordeling
- Actualisatie van beleidskaders

De analyse wordt minimaal jaarlijks herzien of bij significante organisatorische of wettelijke wijzigingen.

### 4.3 Toepassingsgebied van het IMS

Het IMS is van toepassing op:
- Alle gemeentelijke organisatieonderdelen
- Alle processen waarin informatie wordt verwerkt
- Alle verwerkingen van persoonsgegevens
- Alle ondersteunende en primaire processen

Het toepassingsgebied wordt jaarlijks beoordeeld.

### 4.4 Functioneren van het IMS

Beoogd wordt het vastgestelde IMS te onderhouden en continu te verbeteren, rekening houdend met de vereisten van de BIO 2.0 norm. Dit betekent dat:
- De behoeften en verwachtingen van de organisatie en belanghebbenden worden opgenomen en onderhouden met betrekking tot business continuity, informatiebeveiliging en privacy
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

Een formele escalatieprocedure is te vinden in bijlage 2.

#### 5.3.1 Stuurgroep / Strategisch IMS-team (SIMS)

**Implementatiefase**

Tijdens de implementatiefase fungeert de stuurgroep als bestuurlijk opdrachtgever van het IMS.
De stuurgroep:
- Bewaakt scope, planning en voortgang van implementatie
- Stelt kaders en prioriteiten vast
- Neemt besluiten over inrichting en positionering van het IMS
- Bewaakt samenhang tussen privacy, informatiebeveiliging en business continuity
- Beslist over escalaties vanuit de regiegroep
- Rapporteert rechtstreeks aan het directieteam

De stuurgroep beschikt over mandaat van het directieteam voor besluitvorming binnen de vastgestelde scope, inclusief prioritering van middelen.

**Beheerfase (SIMS)**

Na implementatie gaat de stuurgroep over in het Strategisch IMS-team (SIMS).
Het SIMS is verantwoordelijk voor:
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

Na implementatie wordt de regiegroep het Tactisch IMS-team (TIMS).
Het TIMS is verantwoordelijk voor de integrale coördinatie van het IMS en borgt de werking van de PDCA-cyclus. Het TIMS:
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

De eerste lijn bestaat uit:
- Proceseigenaren
- Discipline-eigenaren
- Lijnmanagement

Zij zijn verantwoordelijk voor:
- Uitvoering van beleid
- Identificatie van risico's
- Implementatie van beheersmaatregelen
- Registratie van afwijkingen
- Rapportage aan TIMS

De eerste lijn is eigenaar van risico's.

#### Tweede lijn — Kaderstelling en coördinatie

De tweede lijn bestaat uit functies die kaders stellen, adviseren en monitoren, waaronder:
- Concerncontroller (in-control perspectief)
- CARM
- BCM-coördinator
- Privacy Officer

De tweede lijn:
- Ontwikkelt beleidskaders
- Ondersteunt bij risicobeoordeling
- Monitort naleving
- Adviseert over escalatie
- Consolideert rapportages richting TIMS

De tweede lijn is niet verantwoordelijk voor operationele uitvoering.

#### Derde lijn — Onafhankelijk toezicht

De derde lijn bestaat uit:
- CISO
- Functionaris Gegevensbescherming (FG)
- Interne Accountant / Interne Auditfunctie

De derde lijn:
- Toetst onafhankelijk de effectiviteit van het IMS
- Beoordeelt naleving van beleid en normenkader
- Rapporteert rechtstreeks aan het directieteam
- Doet aanbevelingen voor verbetering

De derde lijn heeft geen uitvoerende, kaderstellende of besluitvormende rol in SIMS of TIMS. Zij worden op uitnodiging gehoord als adviseur.

#### Relatie met SIMS en TIMS

Het Three Lines Model is geïntegreerd in de overlegstructuur:
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

De rapportagestructuur volgt de hiërarchie van het IMS en sluit aan op de PDCA-cyclus. De rapportagelijnen waarborgen:
- Transparantie
- Tijdige signalering van risico's
- Bestuurlijke sturing
- Continue verbetering

Een formele escalatieprocedure is te vinden in bijlage 2.

#### Rapportagelijn

{{RAPPORTAGE_TABEL}}

Rapportages over de werking van het IMS worden periodiek opgemaakt door de verschillende lagen. Deze rapportages omvatten niet de werking van de individuele beheersmaatregelen. Dit is onderdeel van de maatregel zelf (opzet-bestaan-werking). Een rapportage over de maatregelen wordt op operationeel niveau voorgelegd aan de discipline-eigenaren, die een algemeen beeld meenemen in hun IMS-rapportage aan het TIMS.

---

## 6. Planning

Dit hoofdstuk beschrijft hoe de gemeente het IMS planmatig inricht, aanstuurt en ontwikkelt. Planning binnen het IMS is risicogestuurd en sluit aan bij de strategische doelstellingen van de organisatie.

Het planningsproces borgt dat:
- Risico's systematisch worden geïdentificeerd en beoordeeld
- Kansen worden benut
- Doelstellingen worden vastgesteld
- Wijzigingen beheerst worden doorgevoerd

### 6.1 Acties om risico's te beperken en kansen te benutten

#### 6.1.1 Risicogestuurde benadering

De gemeente hanteert een integrale risicomanagementmethodiek voor:
- Informatiebeveiliging
- Privacy
- Business Continuity

Risicomanagement is gebaseerd op de volgende uitgangspunten:
- Risico's worden periodiek en gestructureerd geïnventariseerd
- Risicoanalyse vindt plaats op basis van kans en impact
- De risicobereidheid (risk appetite) is bestuurlijk vastgesteld
- Restrisico's worden expliciet geaccepteerd op het juiste niveau
- Risicobeoordelingen worden vastgelegd en herleidbaar gedocumenteerd

Het risicomanagementproces omvat:
1. Identificatie
2. Analyse
3. Evaluatie
4. Behandeling
5. Acceptatie
6. Monitoring

Risico's worden vastgelegd in de GRC-tool.

#### 6.1.2 Privacy-specifieke analyse

Voor verwerkingen met verhoogd risico wordt een gestructureerde privacy-risicobeoordeling uitgevoerd (zoals een DPIA). Deze beoordeling:
- Wordt uitgevoerd voorafgaand aan nieuwe of gewijzigde verwerkingen
- Wordt herzien bij materiële wijzigingen
- Wordt betrokken bij besluitvorming

De Functionaris Gegevensbescherming houdt toezicht op correcte toepassing. De uitwerking van dit proces is beschreven in {{VERWIJZING_DPIA_PROCEDURE}}.

#### 6.1.3 Privacy by Design

Bij de ontwikkeling of wijziging van processen, systemen of verwerkingen waarin persoonsgegevens worden verwerkt, wordt privacy by design (gegevensbescherming door ontwerp en door standaardinstellingen) toegepast conform ISO 27701 7.4/8.4 en AVG art. 25.

Dit houdt in dat:
- Privacyaspecten worden meegenomen vanaf de ontwerpfase
- Standaardinstellingen gericht zijn op minimale gegevensverwerking
- De Privacy Officer adviseert bij de beoordeling

De uitwerking van deze procedure is beschreven in {{VERWIJZING_PBD_PROCEDURE}}.

#### 6.1.4 Business Impact Analyse

Ten behoeve van business continuity wordt een periodieke Business Impact Analyse uitgevoerd. De BIA:
- Identificeert kritieke processen
- Bepaalt maximaal toelaatbare uitvalperiode (MTPD), hersteltijd (RTO) en herstelpunt (RPO)
- Bepaalt impact bij uitval
- Levert input voor prioritering binnen het IMS
- Wordt minimaal jaarlijks herijkt

De uitwerking van het BIA-proces is beschreven in {{VERWIJZING_BIA_DOCUMENT}}.

#### 6.1.5 Kansen

Naast risico's identificeert de gemeente kansen die bijdragen aan:
- Versterking van beheersing
- Verbetering van rapportage
- Verhoging van volwassenheid van het IMS
- Efficiëntere integratie van disciplines

Kansen worden meegenomen in jaarplanning en doelstellingen.

### 6.2 IMS-doelstellingen en plannen om ze te bereiken

#### Vaststelling doelstellingen

Jaarlijks worden IMS-doelstellingen vastgesteld door het directieteam op advies van het SIMS. De doelstellingen:
- Sluiten aan bij de strategische kaders (hoofdstuk 4)
- Zijn SMART geformuleerd
- Zijn gekoppeld aan risico's en prioriteiten
- Zijn meetbaar en tijdgebonden

De doelstellingen hebben betrekking op bijvoorbeeld:
- Volwassenheid van het IMS
- Actualiteit van risicoregisters
- Tijdigheid van managementreview
- Opvolging van auditbevindingen
- Verbetering van rapportagekwaliteit

#### Planning en jaarcyclus

De planning van het IMS wordt vastgelegd in een jaarlijkse IMS-jaarplanning. De jaarplanning bevat:
- Planning risicoherijking
- Auditplanning
- Managementreviewmomenten
- Evaluatie van doelstellingen
- Rapportagemomenten
- Herziening van beleid

De planning is geïntegreerd in de reguliere planning- en controlcyclus van de gemeente.

#### Monitoring van doelstellingen

De voortgang van doelstellingen wordt:
- Periodiek gemonitord
- Gerapporteerd via de vastgestelde rapportagestructuur
- Geëvalueerd tijdens de managementreview

Indien doelstellingen niet worden behaald, worden corrigerende acties vastgesteld.

### 6.3 Plannen van wijzigingen

Wijzigingen die impact kunnen hebben op het IMS worden beheerst doorgevoerd. Onder wijzigingen wordt verstaan:
- Organisatorische wijzigingen
- Wijzigingen in wet- en regelgeving
- Technologische ontwikkelingen
- Wijzigingen in scope van het IMS
- Structurele wijzigingen in risicoprofiel

Voor significante wijzigingen geldt:
- Voorafgaande impactanalyse
- Betrokkenheid van relevante rollen
- Documentatie van besluitvorming
- Aanpassing van registers en doelstellingen indien nodig

### 6.4 Samenhang binnen het IMS

Planning binnen het IMS is integraal. Dit betekent dat:
- Privacy, informatiebeveiliging en business continuity één gezamenlijke planningscyclus volgen
- Eén integraal risicoregister wordt gehanteerd
- Eén verbetercyclus wordt toegepast
- Besluitvorming plaatsvindt op basis van samenhangende informatie

### 6.5 Evaluatie van de planningcyclus

De effectiviteit van de planningscyclus wordt minimaal jaarlijks beoordeeld tijdens de directiebeoordeling. Hierbij wordt gekeken naar:
- Actualiteit van risicoanalyses
- Realisatie van doelstellingen
- Effectiviteit van corrigerende acties
- Aansluiting bij strategische ontwikkelingen

---

## 7. Ondersteuning

### 7.1 Middelen

Het directieteam ondersteunt het IMS via de aangestelde SIMS en TIMS. Er worden voldoende financiële middelen en tooling beschikbaar gesteld om het IMS op te zetten, te implementeren, te onderhouden en continu te verbeteren. Wanneer blijkt dat middelen niet meer toereikend zijn kan het TIMS in afstemming met het SIMS het directieteam verzoeken om aanvullende middelen beschikbaar te stellen.

### 7.2 Competenties

Mensen kunnen het IMS alleen adequaat ondersteunen als ze voldoende bekwaam zijn. De organisatie zorgt voor deze competentie door middel van:
- Een duidelijke rolbeschrijving voor de betrokken rollen in het IMS
- Duidelijke rollen en verantwoordelijkheden voor iedereen die werkt met de informatie van de organisatie

### 7.3 Bewustzijn

Een deel van de opleiding voor iedereen die met informatie van de organisatie werkt omvat bewustzijn en begrip van het informatiebeveiligings- en privacybeleid, de verwachtingen voor al het personeel en de implicaties van het niet naleven van de IMS-verplichtingen.

### 7.4 Communicatie

Om een adequaat begrip van het IMS te garanderen, wordt regelmatig gecommuniceerd met verschillende groepen belanghebbenden, zowel intern als extern. Deze communicatie omvat:
- Regelmatige nieuwsberichten n.a.v. potentiële incidenten en verhoogde risico's
- Jaarlijkse directiebeoordelingen opgesteld door het TIMS
- Organisatiebrede nieuwsberichten indien nodig, opgesteld door de discipline-eigenaren
- Updates over het beleid aan alle belanghebbenden

### 7.5 Gedocumenteerde informatie

#### Algemeen

De organisatie zorgt ervoor dat geschikte, gedocumenteerde informatie het IMS ondersteunt, zoals:
- Het IMS-handboek
- Het risicomanagementproces
- Het informatiebeveiligingsbeleid en bijbehorende normen
- Processen ter ondersteuning van informatiebeveiliging
- Sjablonen ter ondersteuning van standaardisatie van het IMS
- Een centraal beheerd risicoregister
- Een Verklaring van Toepasselijkheid (VvT)
- Een centrale opslagplaats voor alle ISO-bronnen

#### Creëren en actualiseren

Alle documenten met betrekking tot het IMS moeten een titel, aanmaakdatum en auteur bevatten. Elk document geeft eventuele beoordelings- en goedkeuringsvereisten op. Deze eisen staan beschreven in het documentbeheersproces.

#### Beheer van IMS-documenten

Alle documenten met betrekking tot het IMS moeten het documentbeheersproces volgen, waarin de verwachtingen voor versiebeheer, goedkeuring, gegevensclassificatie en andere belangrijke beheerfactoren worden beschreven.

---

## 8. Uitvoering

### 8.1 Operationele planning en beheersing

Er is een reeks processen, procedures en controles gedefinieerd en geïmplementeerd om te voldoen aan de eisen van het beheersysteem, evenals de eisen die zijn afgeleid van de risicobeoordeling.

#### Adresseren van de doelstellingen

Om te voldoen aan de in paragraaf 6.2 beschreven doelstellingen, worden de in het addendum beschreven maatregelen genomen.

### 8.2 Risicobeoordeling

Alle risicoanalyses volgen het risicomanagementproces te vinden in bijlage 3 van dit document. In bijlage 3 is ook te vinden hoe de kwantificatie van kans en impact eruitziet, en hoe de matrix eruitziet.

Het kan zijn dat voor de specifieke disciplines aanvullende richtlijnen worden opgeschreven om beter aan te sluiten op de aard van de risicoanalyse. Deze aanvullende richtlijnen worden beoordeeld en goedgekeurd door het TIMS. Verwijzingen naar deze richtlijnen worden opgenomen in bijlage 3.

#### Strategische risicoanalyse

{{STRATEGISCHE_RISICOANALYSE_BESCHRIJVING}}

De focus van de strategische risicoanalyse is het identificeren, analyseren en monitoren van de grootste IV-risico's die de gemeente dusdanig kunnen raken waardoor kritische of zelfs catastrofale gevolgen worden ondervonden.

In grote lijnen volgt de analyse het proces omschreven in bijlage 3.

#### Operationele risicoanalyse

{{OPERATIONELE_RISICOANALYSE_BESCHRIJVING}}

#### DPIA's

In paragraaf 6.1.2 staat uitgelegd wanneer en hoe een DPIA uitgevoerd moet worden.

#### Overige momenten voor een risicoanalyse

Er kunnen ook andere belangrijke momenten zijn voor een risicoanalyse:
- Wanneer zich veranderingen in de organisatie voordoen, technisch of niet-technisch
- Wanneer belangrijke veranderingen in de context leiden tot een mogelijke nieuwe kijk op risico's
- Wanneer het directieteam of het SIMS besluit dat een nieuwe analyse moet worden uitgevoerd
- Als een proceseigenaar een verzoek indient voor een nieuwe risicoanalyse
- Bij de start van een project

### 8.3 Risicobereidheid

In bijlage 3 staat uitgeschreven hoe de kwantificering van impact en kans eruitziet. Het risico wordt vervolgens geplot in de risicomatrix.

Het directieteam heeft de volgende risicobereidheid vastgesteld:

| Niveau | Escalatie naar | Actie |
|--------|---------------|-------|
| **Rood** | Directieteam (via SIMS) | Direct melden met actieplan. Moet worden gemitigeerd. |
| **Oranje** | SIMS (via TIMS) | Direct voorleggen met actieplan. Maximaal 6 maanden onbehandeld mits actieplan loopt. Moet worden gemitigeerd, tenzij DT restrisico accepteert. |
| **Geel** | TIMS | Melden door discipline-eigenaar/risico-eigenaar met plan van aanpak. TIMS beslist over maatregelen. Acceptatie door TIMS, onderbouwd. SIMS kan bepalen dat zij niet akkoord gaan. |
| **Groen** | Discipline-eigenaar of risico-eigenaar | Monitort. Mag onderbouwd accepteren. TIMS kan bepalen dat zij niet akkoord gaan. |

### 8.4 Risicobehandeling

Er is een set van maatregelen gedefinieerd. De maatregelen omvatten documentatie, implementatie en effectiviteitsindicatoren. Alle maatregelen worden, indien mogelijk, centraal beheerd.

### 8.5 PII-doorgifte (transfers)

Bij doorgifte van persoonsgegevens aan derden, verwerkers of naar derde landen wordt getoetst of passende waarborgen zijn getroffen conform ISO 27701 7.5/8.5 en de AVG.

Dit omvat:
- Inventarisatie van alle doorgiften (intern, extern, grensoverschrijdend)
- Beoordeling van de rechtsgrondslag per doorgifte
- Vaststelling van passende waarborgen (verwerkersovereenkomsten, SCCs, adequaatheidsbesluit)
- Periodieke herbeoordeling

De doorgifte-inventarisatie is opgenomen in {{VERWIJZING_DOORGIFTE_REGISTER}}.

### 8.6 Incidentmanagement

De gemeente heeft een geïntegreerd incidentmanagementproces ingericht voor informatiebeveiligingsincidenten, datalekken en continuïteitsverstoringen, conform ISO 27001 A.5.24-28 en AVG art. 33/34.

Het proces omvat:
- Classificatie en prioritering van incidenten
- Responsprocedure met escalatie naar het juiste niveau
- Melding aan toezichthouders waar wettelijk vereist (AP bij datalekken, betrokkenen bij hoog risico)
- Registratie en opvolging
- Lessons learned en structurele verbetering

De uitwerking van het incidentmanagementproces is beschreven in {{VERWIJZING_INCIDENTPROCEDURE}}.

---

## 9. Evaluatie van de prestaties

### 9.1 Monitoren, meten, analyseren en evalueren

De doeltreffendheid van het IMS wordt geëvalueerd op basis van omschreven doelstellingen. Aanvullende doelstellingen kunnen altijd worden gedefinieerd als blijkt dat vorige doelstellingen zijn behaald of consequent worden gehaald.

In paragraaf 5.5 staat alles omschreven over de rapportagestructuren binnen het IMS.

### 9.2 Interne audit

In aanvulling op de eigen interne evaluaties en de rapportages daarover worden verbijzonderde (onafhankelijke) interne controles uitgevoerd. Op basis van een eigen risicoanalyse kunnen de volgende onderwerpen worden betrokken:
- Werking van de gehele cyclus of onderdelen daarvan
- Mate waarin eerdere aanbevelingen zijn of worden opgevolgd
- De kwaliteit van de interne rapportages
- De kwaliteit en tijdigheid van de geïnventariseerde risico's en maatregelen
- Het hanteren van de juiste normen en de juiste en volledige vertaling daarvan in het systeem

### 9.3 BC-oefeningen

Om de effectiviteit van business continuity plannen te toetsen en te verbeteren, worden periodiek oefeningen uitgevoerd conform ISO 22301 8.5.

Het oefenprogramma omvat:
- Jaarlijkse planning van oefeningen (opgenomen in de IMS-jaarplanning)
- Variatie in oefenvormen (tabletop, functioneel, fullscale)
- Evaluatie en rapportage na elke oefening
- Opvolging van verbeterpunten via het reguliere verbeterproces

De uitwerking van het oefenprogramma is beschreven in {{VERWIJZING_OEFENPROGRAMMA}}.

### 9.4 Directiebeoordeling

Op jaarlijkse basis (of als zich een ernstig incident of datalek heeft voorgedaan) vindt een directiebeoordeling plaats omtrent het IMS. Minimaal de volgende zaken komen aan de orde:
- De status van de gedefinieerde actiepunten (n.a.v. voorgaande directiebeoordeling)
- Wijzigingen in de interne en externe issues en feedback van belanghebbenden
- Verzamelde input en trends omtrent de prestaties van het IMS:
  - Afwijkingen (niet-naleving) en corrigerende maatregelen
  - Resultaten en trends op basis van monitoring- en meetresultaten (rapportages)
  - Auditresultaten
  - Resultaten BC-oefeningen
  - Realisatie van de IMS-doelstellingen
  - Resultaten van de strategische risicobeoordelingen en status van de behandelplannen
  - Mogelijkheden voor continue verbetering

De output van de directiebeoordeling wordt vastgelegd. Op basis daarvan worden plannen gedefinieerd en gecommuniceerd die de geschiktheid, toereikendheid en doeltreffendheid van het IMS wijzigen of verbeteren.

---

## 10. Verbetering

### 10.1 Afwijkingen en corrigerende maatregelen

Wanneer afwijkingen geconstateerd worden, wordt hierop tijdig gereageerd en, indien van toepassing:
1. De oorzaak achterhaald
2. Actie ondernomen om de afwijking te beheersen (corrigerende maatregelen)
3. Achterhaald of de geconstateerde afwijking mogelijk ook elders optreedt (detectie)
4. De gevolgen aangepakt (verwijderen en herstellen)
5. Maatregelen genomen om herhaling te voorkomen (preventieve maatregelen)
6. De doeltreffendheid van alle genomen preventieve maatregelen beoordeeld
7. Indien nodig het IMS bijgewerkt

### 10.2 Continue verbetering

De geschiktheid, toereikendheid en effectiviteit van het IMS wordt voortdurend verbeterd.

---

## Bijlage 1: Belanghebbenden

{{BELANGHEBBENDEN_ANALYSE}}

---

## Bijlage 2: Formele escalatieprocedure

### Doel en uitgangspunten

De formele escalatieprocedure waarborgt dat risico's, afwijkingen en tekortkomingen binnen het IMS tijdig, transparant en proportioneel worden opgepakt op het juiste bestuurlijke niveau.

De procedure heeft tot doel:
- Tijdige besluitvorming bij overschrijding van risicobereidheid
- Borging van bestuurlijke verantwoordelijkheid
- Voorkomen van informele of niet-gedocumenteerde besluitvorming
- Vastlegging van risicoacceptaties en prioriteringskeuzes
- Eenduidige rapportage binnen de PDCA-cyclus

Escalatie vindt plaats op basis van vooraf vastgestelde criteria en niet uitsluitend op basis van hiërarchie.

### Escalatiecriteria

Escalatie is verplicht wanneer één of meer van de volgende situaties zich voordoen:
- Overschrijding van vastgestelde risicobereidheid (risk appetite)
- Structurele of herhaalde non-conformiteiten
- Onvoldoende voortgang bij corrigerende maatregelen
- Onvoldoende beschikbare middelen om risico's te beheersen
- Domeinoverstijgende risico's met organisatorische impact
- Juridische of reputatiegevoelige kwesties
- Noodzaak tot formele restrisicoacceptatie

De escalatiecriteria worden periodiek herijkt door het TIMS en vastgesteld door het SIMS.

### Escalatieniveaus

**Niveau 1 — Discipline-eigenaar (Operationeel)**

De discipline-eigenaar:
- Beoordeelt afwijkingen en risico's binnen het eigen domein
- Neemt corrigerende maatregelen binnen mandaat
- Legt besluiten en voortgang vast
- Escaleert indien criteria worden overschreden

Besluitvorming binnen dit niveau mag niet leiden tot impliciete risicoacceptatie buiten vastgesteld mandaat.

**Niveau 2 — TIMS (Tactisch)**

Escalatie naar het TIMS vindt plaats wanneer:
- Het risico meerdere disciplines raakt
- Aanvullende middelen of prioritering nodig zijn
- Beleidsinterpretatie of kaderstelling vereist is

Het TIMS:
- Beoordeelt impact en samenhang
- Stelt mitigerende richting vast
- Bepaalt of escalatie naar SIMS noodzakelijk is
- Documenteert advies en besluitvorming

Het TIMS heeft mandaat binnen bestaande beleidskaders, maar kan geen strategische risicoacceptatie uitvoeren.

**Niveau 3 — SIMS (Strategisch)**

Escalatie naar het SIMS vindt plaats wanneer:
- Restrisicoacceptatie op strategisch niveau vereist is
- Beleidsaanpassing noodzakelijk is
- Organisatiebrede impact verwacht wordt
- Risico's bestuurlijke of maatschappelijke consequenties hebben

Het SIMS:
- Neemt formeel besluit over risicoacceptatie
- Stelt prioriteiten bij capaciteitsvraagstukken
- Draagt zorg voor bestuurlijke verantwoording
- Escaleert indien nodig naar het directieteam

Besluiten worden expliciet vastgelegd inclusief motivatie en geldigheidsduur.

**Niveau 4 — Directieteam**

Escalatie naar het directieteam vindt plaats bij:
- Structurele systeemfalen
- Strategische herijking van het IMS
- Substantiële reputatie- of aansprakelijkheidsrisico's
- Wijziging van risicobereidheid

Het directieteam is eindverantwoordelijk voor de uiteindelijke acceptatie van restrisico's.

---

## Bijlage 3: Risicobeoordelingsmethodiek

### Overzicht

Het risicomanagementproces is de basis waarop alle risicoanalyses binnen het IMS draaien. Deze bijlage beschrijft de methodiek, schalen en acceptatiecriteria.

{{RISICOMANAGEMENT_PROCESDIAGRAM}}

### Impactschalen

{{IMPACTSCHALEN_TABEL}}

*De impactschalen dekken minimaal de volgende categorieën:*
- *Financiële impact*
- *Maatschappelijke impact*
- *Reputatieschade*
- *Juridische en bestuurlijke impact*
- *Operationele impact*

### Kansschalen

{{KANSSCHALEN_TABEL}}

### Risicomatrix

{{RISICOMATRIX}}

### Acceptatiecriteria

De acceptatiecriteria sluiten aan op de risicobereidheid zoals beschreven in paragraaf 8.3:
- **Rood**: niet acceptabel — directe mitigatie vereist, escalatie naar directieteam
- **Oranje**: niet acceptabel — mitigatie vereist, escalatie naar SIMS
- **Geel**: voorwaardelijk acceptabel — TIMS beslist, onderbouwde acceptatie mogelijk
- **Groen**: acceptabel — discipline-eigenaar monitort, onderbouwde acceptatie mogelijk

### Procesuitleg

**1. Identificatie en toebedelen**

Doel: vaststellen welke risico's er zijn en welke assets ze beïnvloeden.
- Bepaal scope en context (organisatie, processen, systemen)
- Inventariseer assets (hardware, software, data, personeel)
- Identificeer dreigingen en kwetsbaarheden
- Elk risico krijgt een risico-eigenaar

**2. Analyse**

Doel: begrijpen van de risico's en hun effect.
- Bepaal kans van optreden (onderbouwd met uitleg)
- Bepaal impact (financieel + overige categorieën)
- Bereken risicoscore

**3. Evaluatie**

Doel: prioriteren van risico's.
- Vergelijk risico's met risicocriteria (acceptabel vs. niet-acceptabel)
- Stel vast welke risico's behandeld moeten worden

**4. Behandeling**

Doel: maatregelen vaststellen om risico's te beheersen.
- Risico vermijden (processen stoppen/aanpassen)
- Risico mitigeren (maatregelen implementeren)
- Risico overdragen (verzekering, contracten)

**5. Acceptatie**

Doel: formeel beslissen welke risico's worden geaccepteerd.
- Risico-eigenaar/discipline-eigenaar/TIMS/SIMS/DT beoordeelt en accepteert conform de escalatieladder
- Documenteer geaccepteerde risico's in het risicoregister

**6. Monitoring**

Doel: continu bewaken en bijsturen.
- Voer periodieke reviews en audits uit
- Update risicobeoordelingen bij veranderingen
- Evalueer effectiviteit van maatregelen

### Aanvullende richtlijnen per discipline

Voor de specifieke disciplines kunnen aanvullende richtlijnen worden opgesteld:

{{AANVULLENDE_RICHTLIJNEN_VERWIJZINGEN}}
