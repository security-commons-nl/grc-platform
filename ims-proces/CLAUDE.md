# IMS-proces

## Wat is dit?

`IMS-proces` is de **implementatiemethodologie** voor het inrichten van een Integrated Management System (IMS) bij gemeenten. Het begeleidt een gemeente stap voor stap door het IMS-implementatietraject — van bestuurlijk commitment tot volwassen GRC-platform.

Het IMS dekt drie domeinen:
- **ISMS** — Informatiebeveiliging (ISO 27001, BIO 2.0)
- **PIMS** — Privacy (ISO 27701, AVG · 154 controls)
- **BCMS** — Bedrijfscontinuïteit (ISO 22301)

## Kernbestanden

| Bestand | Doel |
|---------|------|
| `CONTEXT.md` | Centraal ontwerpregister: 22 stappen, 4 fasen, 18 AI agents, alle ontwerpbeslissingen |
| `blueprint-handboek.md` | Generiek IMS Handboek template met placeholders (ISO HLS structuur) |

## Relatie met grc-platform

`IMS-proces` is onderdeel van `grc-platform` (de GRC-engine). Samen vormen ze één platform.

### Consolidatievisie

**Einddoel:** het volledige IMS-proces (alle 4 fasen, alle 22 stappen) wordt ondersteund door één geïntegreerde GRC-engine.

- **IMS-proces** is leidend — het definieert de stappen, agents en documentgeneratie
- **GRC-engine** levert: risico's, controls, assessments, PDCA, evidence
- De inrichtingsmodus *is* de configuratie van de beheermodus
- Data die tijdens onboarding wordt ingevoerd vloeit direct door — geen synchronisatie, één waarheid

## Architectuur & conventies

### Fasering

```
Fase 0 (Q1-Q2 2026)  → Bouwplaats: TIMS richt het IMS in
Fase 1 (Q3 2026)     → Werktool: lijnmanagement doet risicoanalyse
Fase 2 (Q1 2027)     → Beheertool: PDCA draait, controls, evidence
Fase 3 (2028+)       → Volwassen GRC-platform (optioneel)
```

### Governance-naamgeving

- **SIMS** — Strategisch IMS-team (kwartaal, strategische besluiten)
- **TIMS** — Tactisch IMS-team (maandelijks, coördinatie)
- CISO, FG en Interne Accountant zijn **3e lijn** — adviseur, geen lid van SIMS of TIMS

### Blueprint vs. gemeente-invulling

Het IMS Handboek heeft twee versies:
- **Blueprint** (`blueprint-handboek.md`): generiek skelet met `{{PLACEHOLDER}}`-syntax
- **Gemeente-invulling**: ingevuld met organisatiespecifieke context — output van het IMS-proces

AI agents vullen de blueprint in op basis van wat de gemeente tijdens het proces invoert.

### Stap-patroon

Elke processtap volgt hetzelfde patroon:
```
Input verzamelen → AI agent genereert concept → Gremium reviewt → Output vastgelegd → Volgende stap ontgrendeld
```

### Risicobereidheid — escalatieladder

| Niveau | Escalatie naar |
|--------|---------------|
| Groen | Discipline-eigenaar |
| Geel | TIMS |
| Oranje | SIMS |
| Rood | Directieteam |

## Normatief kader

- ISO 27001:2022 (25 clauses — 24 gedekt, 1 gedeeltelijk)
- ISO 27701:2019 (18 clauses — 15 gedekt, 3 gedeeltelijk op detailniveau)
- ISO 22301:2019 (24 clauses — 22 gedekt, 2 gedeeltelijk op detailniveau)

Volledige clause-by-clause toetsing uitgevoerd en gedocumenteerd in CONTEXT.md.
