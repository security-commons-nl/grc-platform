# AI Knowledge Implementation Plan

## Overzicht

Dit document beschrijft hoe we de AI kennisbank vullen, opslaan en gebruiken binnen IMS.

---

## 1. OPHALEN van Kennis

### 1.1 Platform Kennis (category: "platform")

| Bron | Methode | Verantwoordelijke |
|------|---------|-------------------|
| DESIGN.md | Automatisch parsen bij setup | Systeem |
| README.md | Automatisch parsen bij setup | Systeem |
| Code comments/docstrings | Extract bij build | Systeem |
| Handmatige documentatie | Admin interface | IMS beheerder |

**Inhoud:**
- Wat is IMS en waarvoor dient het
- Hoe werken workflows (staten, transities)
- Rollen en rechten uitleg
- Navigatie en functionaliteiten

### 1.2 Methodiek Kennis (category: "methodology")

| Bron | Methode | Verantwoordelijke |
|------|---------|-------------------|
| "In Control" model documentatie | Handmatig invoeren | Domeinexpert |
| MAPGOOD standaard | Handmatig invoeren | Domeinexpert |
| Interne richtlijnen | Upload + AI extractie | Domeinexpert |

**Inhoud:**
- In Control model uitleg (kwadranten, wanneer welke)
- MAPGOOD categorieën met voorbeelden
- Impact/Kwetsbaarheid bepaling criteria
- Wanneer REDUCE vs TRANSFER vs AVOID
- Best practices risicobeoordeling

### 1.3 Framework Kennis (category: "framework")

| Bron | Methode | Verantwoordelijke |
|------|---------|-------------------|
| BIO 1.04 / 2.0 teksten | Import uit officiële bron | Systeem + review |
| ISO 27001:2022 structuur | Handmatig (copyright) | Domeinexpert |
| AVG artikelen | Import uit wettekst | Systeem |
| NEN 7510 | Handmatig (copyright) | Domeinexpert |

**Let op:** Sommige standaarden zijn auteursrechtelijk beschermd. Alleen structuur/uitleg opnemen, niet letterlijke tekst.

### 1.4 Best Practices (category: "best_practice")

| Bron | Methode | Verantwoordelijke |
|------|---------|-------------------|
| Interne ervaring | Interviews → AI samenvatting | Domeinexpert |
| NCSC richtlijnen | Web scrape + review | Systeem + review |
| CIS Controls | Handmatig samenvatten | Domeinexpert |
| Eigen audit ervaringen | Documenteren in systeem | Auditors |

### 1.5 Terminologie (category: "terminology")

| Bron | Methode | Verantwoordelijke |
|------|---------|-------------------|
| Bestaande glossaries | Import CSV/Excel | Systeem |
| Normen en standaarden | Extract definities | Domeinexpert |
| Organisatie-specifieke termen | Admin interface | Tenant admin |

---

## 2. OPSLAAN van Kennis

### 2.1 Database Structuur

```
AIKnowledgeBase
├── id (PK)
├── tenant_id (NULL = globaal, anders tenant-specifiek)
├── key (uniek, bijv. "METHODOLOGY_IN_CONTROL_QUADRANTS")
├── title ("De vier kwadranten van het In Control model")
├── content (markdown tekst)
├── category ("methodology")
├── subcategory ("in_control")
├── applicable_contexts (JSON: ["risk_assessment"])
├── applicable_entity_types (JSON: ["Risk"])
├── priority (0-100)
├── always_include (bool)
├── is_embedded (bool)
└── embedded_at (timestamp)
```

### 2.2 Lagen van Kennis

```
┌─────────────────────────────────────────────────────────────┐
│  LAAG 1: Systeem Kennis (tenant_id = NULL)                  │
│  - Platform werking                                          │
│  - Methodieken (In Control, MAPGOOD)                        │
│  - Framework structuren (BIO, ISO)                          │
│  - Algemene best practices                                   │
│  - Standaard terminologie                                    │
│                                                              │
│  → Beheerd door IMS platform team                           │
│  → Geldt voor ALLE tenants                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LAAG 2: Tenant Kennis (tenant_id = X)                      │
│  - Organisatie context (missie, visie)                      │
│  - Eigen richtlijnen en procedures                          │
│  - Organisatie-specifieke terminologie                      │
│  - Aanvullingen op methodieken                              │
│                                                              │
│  → Beheerd door tenant admin                                │
│  → Geldt alleen voor deze tenant                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LAAG 3: Dynamische Context                                 │
│  - Huidige pagina/entity                                    │
│  - Conversatie historie                                      │
│  - User rol en rechten                                       │
│                                                              │
│  → Automatisch bepaald                                      │
│  → Per sessie/interactie                                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Vector Embeddings (RAG)

Voor grote hoeveelheden kennis gebruiken we RAG (Retrieval Augmented Generation):

1. **Chunking**: Grote documenten opdelen in chunks (~500 tokens)
2. **Embedding**: Elk chunk omzetten naar vector (via lokale embedding model)
3. **Opslag**: Vectors opslaan in pgvector (PostgreSQL extensie)
4. **Retrieval**: Bij vraag → relevante chunks ophalen op basis van similarity

```sql
-- pgvector setup
CREATE EXTENSION vector;

ALTER TABLE aiknowledgebase
ADD COLUMN embedding vector(1536);

CREATE INDEX ON aiknowledgebase
USING ivfflat (embedding vector_cosine_ops);
```

### 2.4 Beheer Interface

**Admin schermen nodig:**

1. **Knowledge Browser**
   - Lijst van alle kennis items
   - Filteren op category, tenant
   - Zoeken in content

2. **Knowledge Editor**
   - Markdown editor
   - Preview
   - Metadata invullen
   - Testen van embedding

3. **Import Wizard**
   - Upload document (PDF, Word, Markdown)
   - AI extraheert kennis
   - Review en goedkeuren
   - Opslaan in juiste categorie

4. **Glossary Manager**
   - Termen beheren
   - Aliassen toevoegen
   - Relaties leggen

---

## 3. GEBRUIKEN van Kennis

### 3.1 Context Samenstelling

Bij elke AI interactie wordt context samengesteld:

```
┌─────────────────────────────────────────────────────────────┐
│  STAP 1: Bepaal situatie                                    │
│  - Welke pagina/entity?                                     │
│  - Welke actie (classificeren, reviewen, uitleggen)?        │
│  - Welke user rol?                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STAP 2: Selecteer prompt template                          │
│  - Zoek AIPromptTemplate waar trigger_context matcht        │
│  - Laad system_prompt en initial_message                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STAP 3: Verzamel relevante kennis                          │
│                                                              │
│  A. Always-include items                                    │
│     WHERE always_include = true                             │
│                                                              │
│  B. Context-relevante items                                 │
│     WHERE applicable_entity_types CONTAINS current_type     │
│     WHERE applicable_contexts CONTAINS current_context      │
│                                                              │
│  C. RAG retrieval (voor specifieke vragen)                  │
│     → Embed vraag → Zoek similar chunks → Top 5 results     │
│                                                              │
│  D. Organisatie context                                     │
│     → OrganizationContext voor deze tenant                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STAP 4: Bouw prompt                                        │
│                                                              │
│  SYSTEM: {prompt_template.system_prompt}                    │
│                                                              │
│  CONTEXT:                                                   │
│  ## Platform & Methodiek                                    │
│  {relevante AIKnowledgeBase items}                          │
│                                                              │
│  ## Organisatie                                             │
│  {OrganizationContext items}                                │
│                                                              │
│  ## Huidige situatie                                        │
│  Je kijkt naar: {entity_type} "{entity_title}"              │
│  Huidige waarden: {entity_fields}                           │
│                                                              │
│  CONVERSATION: {eerdere berichten}                          │
│                                                              │
│  USER: {nieuwe vraag/input}                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STAP 5: Roep LLM aan                                       │
│  - Lokaal: Ollama + Mistral                                 │
│  - Response verwerken                                        │
│  - Suggesties extraheren → AISuggestion records             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Voorbeeld: Risk Classificatie

**Situatie:** User opent een nieuw risico en vraagt "Help me dit te classificeren"

**Context die AI krijgt:**

```markdown
## SYSTEM PROMPT (uit AIPromptTemplate "risk_classifier")
Je bent een risk management expert binnen een Nederlandse gemeente.
Help de gebruiker om risico's te classificeren volgens de In Control methode.
Stel doorvragen om impact en kwetsbaarheid te bepalen.
Geef concrete suggesties die de gebruiker kan accepteren.

## METHODIEK KENNIS
### "In Control" Model
Het In Control model bepaalt hoeveel aandacht een risico krijgt op basis van:
- **Impact**: Hoe erg is het als dit misgaat? (Hoog/Laag)
- **Kwetsbaarheid**: Hoe waarschijnlijk is het, gegeven huidige maatregelen? (Hoog/Laag)

De vier kwadranten:
| Impact/Kwetsbaarheid | Hoog Impact | Laag Impact |
|----------------------|-------------|-------------|
| Hoge Kwetsbaarheid   | MITIGEREN   | MONITOREN   |
| Lage Kwetsbaarheid   | ZEKERHEID   | ACCEPTEREN  |

### Impact bepalen
Hoge impact als:
- Financiële schade > €100.000
- Reputatieschade (landelijk nieuws)
- Wettelijke consequenties
- Uitval kritieke dienstverlening > 4 uur
...

### MAPGOOD Categorieën
- **M**enselijk falen: menselijke fouten, social engineering
- **A**pplicatie falen: software bugs, crashes
- **P**roces falen: proceduele fouten
- **G**egevens: data kwaliteit, integriteit
- **O**mgeving: brand, overstroming, stroomuitval
- **O**pzet: bewuste aanvallen, sabotage
- **D**erden: leveranciers, ketenpartners

## ORGANISATIE CONTEXT
Gemeente: [Naam Organisatie]
Risk Appetite: Voorzichtig (CAUTIOUS)
Sector: Overheid
Kritieke processen: Burgerzaken, Sociale Zaken, Vergunningen

## HUIDIGE SITUATIE
Entity: Risk (nieuw, nog niet opgeslagen)
Titel: "Ransomware aanval op gemeentelijk netwerk"
Beschrijving: "Risico dat ransomware het netwerk infecteert"
Huidige classificatie: Niet ingevuld

## CONVERSATIE
(nog geen eerdere berichten)

## USER INPUT
"Help me dit risico te classificeren"
```

**AI Response:**

```
Ik help je graag dit ransomware risico te classificeren.

Laten we beginnen met de **impact** te bepalen. Stel dat ransomware
het gemeentelijk netwerk platlegt:

1. **Dienstverlening**: Welke diensten vallen dan uit?
   - Burgerzaken (paspoorten, rijbewijzen)?
   - Sociale zaken (uitkeringen)?
   - Vergunningen?

2. **Duur**: Hoe lang zou herstel duren zonder te betalen?

3. **Data**: Is er risico op datalekken (persoonsgegevens burgers)?

Kun je inschatten welke van deze scenario's van toepassing zijn?
```

### 3.3 Token Budget Management

LLMs hebben een context limiet. We moeten slim omgaan met tokens:

```
┌─────────────────────────────────────────────────────────────┐
│  TOTAAL BUDGET: ~8000 tokens (voor Mistral 7B)              │
│                                                              │
│  Verdeling:                                                  │
│  ├── System prompt:        ~500 tokens (vast)               │
│  ├── Methodiek kennis:    ~1500 tokens (geselecteerd)       │
│  ├── Organisatie context:  ~500 tokens                      │
│  ├── Entity context:       ~500 tokens                      │
│  ├── Conversatie historie: ~2000 tokens (sliding window)    │
│  ├── User input:           ~500 tokens                      │
│  └── Response ruimte:     ~2500 tokens                      │
└─────────────────────────────────────────────────────────────┘
```

**Strategieën:**
1. **Prioriteit**: Items met hogere `priority` eerst
2. **Relevantie**: RAG selecteert meest relevante chunks
3. **Sliding window**: Oude conversatie berichten samenvatten
4. **Lazy loading**: Details alleen laden als nodig

---

## 4. Initiële Vulling

### 4.1 Fase 1: Core Setup (Week 1-2)

**Platform kennis:**
```
KEY                          | TITLE
─────────────────────────────┼──────────────────────────────
PLATFORM_OVERVIEW            | Wat is IMS
PLATFORM_WORKFLOWS           | Hoe werken workflows
PLATFORM_ROLES               | Rollen en rechten
PLATFORM_NAVIGATION          | Navigatie en schermen
```

**In Control methodiek:**
```
KEY                          | TITLE
─────────────────────────────┼──────────────────────────────
METHOD_IN_CONTROL_OVERVIEW   | "In Control" model
METHOD_IN_CONTROL_QUADRANTS  | De vier kwadranten
METHOD_IN_CONTROL_IMPACT     | Impact bepalen
METHOD_IN_CONTROL_VULNERABILITY | Kwetsbaarheid bepalen
METHOD_MITIGATION_APPROACHES | REDUCE vs TRANSFER vs AVOID
```

**MAPGOOD:**
```
KEY                          | TITLE
─────────────────────────────┼──────────────────────────────
METHOD_MAPGOOD_OVERVIEW      | MAPGOOD dreigingscategorieën
METHOD_MAPGOOD_M             | Menselijk falen
METHOD_MAPGOOD_A             | Applicatie falen
METHOD_MAPGOOD_P             | Proces falen
METHOD_MAPGOOD_G             | Gegevens issues
METHOD_MAPGOOD_O_OMGEVING    | Omgevingsfactoren
METHOD_MAPGOOD_O_OPZET       | Opzettelijk handelen
METHOD_MAPGOOD_D             | Derden / Third parties
```

### 4.2 Fase 2: Frameworks (Week 3-4)

**BIO:**
```
KEY                          | TITLE
─────────────────────────────┼──────────────────────────────
FRAMEWORK_BIO_OVERVIEW       | BIO structuur en doel
FRAMEWORK_BIO_CLASSIFICATIONS| BIO classificaties (BBN)
FRAMEWORK_BIO_DOMAINS        | BIO domeinen overzicht
```

**ISO 27001:**
```
KEY                          | TITLE
─────────────────────────────┼──────────────────────────────
FRAMEWORK_ISO27001_OVERVIEW  | ISO 27001 structuur
FRAMEWORK_ISO27001_PDCA      | PDCA cyclus
FRAMEWORK_ISO27001_ANNEX_A   | Annex A controls overzicht
```

### 4.3 Fase 3: Best Practices & Glossary (Week 5-6)

**Best practices:**
- Hoe schrijf je een goede risico beschrijving
- Hoe bepaal je effectiviteit van maatregelen
- Wanneer is een exception acceptabel
- Hoe bereid je een audit voor

**Glossary:**
- Import bestaande definities
- Review en aanvullen
- Koppel aan relevante contexten

### 4.4 Fase 4: Tenant-specifiek (Ongoing)

Per tenant:
- OrganizationContext vullen
- Eigen richtlijnen importeren
- Specifieke terminologie toevoegen

---

## 5. Onderhoud

### 5.1 Review Cyclus

| Wat | Frequentie | Door wie |
|-----|------------|----------|
| Platform kennis | Bij releases | Dev team |
| Methodiek kennis | Jaarlijks | Domeinexpert |
| Framework kennis | Bij nieuwe versies | Domeinexpert |
| Best practices | Halfjaarlijks | Auditors + experts |
| Terminologie | Doorlopend | Allen |

### 5.2 Kwaliteitscontrole

1. **Feedback loop**: Track `was_helpful` op AIConversationMessage
2. **Rejected suggestions**: Analyseer waarom AISuggestions worden afgewezen
3. **Missing knowledge**: Log wanneer AI zegt "dat weet ik niet"
4. **Periodic review**: Steekproef van AI responses door experts

### 5.3 Versioning

- Elke wijziging in AIKnowledgeBase verhoogt `version`
- Oude versies bewaren voor audit trail
- Rollback mogelijk bij problemen

---

## 6. Technische Vereisten

### 6.1 Dependencies

```
- PostgreSQL 15+ met pgvector extensie
- Ollama (lokaal) met Mistral model
- Embedding model (bijv. all-MiniLM-L6-v2)
- Python libraries: langchain, pgvector, sentence-transformers
```

### 6.2 Privacy & Security

- Alle kennis lokaal opgeslagen
- Geen data naar externe LLM services
- Tenant isolatie: kennis is tenant-scoped
- Audit trail van alle AI interacties

---

## 7. Success Criteria

| Metric | Target |
|--------|--------|
| AI suggesties geaccepteerd | > 60% |
| "Was helpful" positief | > 75% |
| Tijd om risico te classificeren | -50% vs zonder AI |
| User satisfaction score | > 4/5 |
