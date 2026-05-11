# EU AI Act risicoclassificatie

> Hoe het GRC-platform AI-systemen helpt classificeren onder EU AI Act (verordening (EU) 2024/1689). Aanvulling op [`modules.md`](modules.md) sectie M4.

Het platform houdt per AI-systeem in het register (`ims_ai_systems`) een veld `eu_ai_act_risk` bij met één van vier waarden plus een "nog niet beoordeeld" fallback. Dit document beschrijft wanneer welke classificatie van toepassing is, met verwijzingen naar de relevante artikelen.

---

## De vier risicocategorieën

### 1. `unacceptable` — Onaanvaardbaar risico (art. 5)

AI-systemen die **verboden** zijn in de EU. Geen mitigatie mogelijk: het systeem mag niet worden ingezet.

| Categorie | Voorbeeld | Verbodsgrond |
|-----------|-----------|--------------|
| Subliminaal manipuleren | UI-elementen die onbewust koopgedrag beïnvloeden | Art. 5(1)(a) |
| Uitbuiten van kwetsbaarheden | Targeting van minderjarigen of mensen met cognitieve beperkingen | Art. 5(1)(b) |
| Social scoring door overheden | Burgerscores die toegang tot diensten bepalen | Art. 5(1)(c) |
| Realtime biometrische identificatie in openbare ruimte | Live gezichtsherkenning in stationshal | Art. 5(1)(d) |
| Predictive policing op individu-niveau | Voorspellen wie strafbare feit zal plegen op persoonsniveau | Art. 5(1)(e) |
| Emotieherkenning op werkplek of school | Stress-monitoring van medewerkers | Art. 5(1)(f) |
| Biometrische categorisatie op gevoelige kenmerken | Afleiden van etniciteit, politieke voorkeur | Art. 5(1)(g) |

**Bij twijfel:** consulteer juridisch advies vóór elke ingebruikname.

---

### 2. `high` — Hoog risico (bijlage III)

AI-systemen waarvan inzet substantiële verplichtingen kent. **Conformiteitsbeoordeling vereist** vóór ingebruikname (art. 43).

Acht categorieën uit bijlage III:

| # | Categorie | Voorbeeld |
|---|-----------|-----------|
| 1 | Kritieke infrastructuur | Verkeersregeling, energienet-stabilisatie, drinkwatercontrole |
| 2 | Onderwijs en beroepsopleiding | Toelating, examenbeoordeling, automatische studievoortgang |
| 3 | Werkgelegenheid | CV-screening, geautomatiseerde ontslagbeslissingen, performance-management |
| 4 | Toegang tot essentiële diensten | Kredietbeoordeling, uitkering toekenning, fraudedetectie in sociale zekerheid |
| 5 | Rechtshandhaving | Risicobeoordeling verdachten, polygraaf-achtige systemen, bewijsanalyse |
| 6 | Migratie, asiel, grenscontrole | Asielaanvraag-triage, visumbeoordeling, identiteitsverificatie |
| 7 | Rechtspraak en democratische processen | Beslissingsondersteuning voor rechters, kiesgedrag-modellen |
| 8 | Biometrische identificatie post-hoc | Identificatie achteraf via beelden |

**Verplichtingen voor hoog-risico AI:**

- Risk management system (art. 9)
- Data-governance (art. 10) — kwaliteit trainingsdata
- Technische documentatie (art. 11)
- Logging (art. 12) — automatische logs bewaren
- Transparantie naar gebruikers (art. 13)
- **Menselijk toezicht (art. 14) — kies HITL-checkpoints via `/api/v1/ai-hitl-checkpoints`**
- Nauwkeurigheid, robuustheid, cybersecurity (art. 15)
- Conformiteitsbeoordeling vóór ingebruikname (art. 43)
- Registratie in EU AI-database (art. 49)

---

### 3. `limited` — Beperkt risico (art. 50)

AI-systemen met **transparantie-eisen** — informeer gebruikers dat ze met AI te maken hebben, of dat content synthetisch is.

| Type | Verplichting |
|------|--------------|
| Chatbots die met natuurlijke personen interageren | Maak duidelijk dat de gesprekspartner AI is |
| Emotieherkenningssystemen (buiten werkplek/school) | Informeer betrokkenen |
| Biometrische categorisatie | Informeer betrokkenen |
| Deepfakes / synthetische content | Label de content als AI-gegenereerd |
| Synthetische tekst over kwesties van publiek belang | Label als AI-gegenereerd tenzij menselijke redactie heeft plaatsgevonden |

Geen conformiteitsbeoordeling vereist, maar wel **disclosure-plicht**.

---

### 4. `minimal` — Minimaal risico

Alle overige AI-systemen. Geen specifieke EU AI Act-verplichtingen. Voorbeelden: spamfilters, AI-driven productaanbevelingen op een webshop, optimalisatie-algoritmen in non-kritieke processen.

**Wel:** vrijwillige gedragscodes zijn aanbevolen (art. 95). En andere wetgeving (AVG, sector-specifieke regels) blijft natuurlijk gewoon van kracht.

---

## Hoe het platform helpt

### Classificatie-suggestie

Het platform biedt een advies-endpoint dat op basis van beschrijving + use-case een eerste suggestie geeft:

```bash
curl -X POST https://grc.jouwdomein.nl/api/v1/ai-systems/classify-suggestion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "system_type": "decision_support",
    "description": "Beoordeelt bijstandsaanvragen op fraudekans",
    "use_case": "Triagestap vóór handmatige behandeling door consulent"
  }'
```

Response:

```json
{
  "suggested_risk": "high",
  "reasoning": "Het beschreven gebruik valt mogelijk onder bijlage III...",
  "triggered_by": ["high: 'bijstand beslissing'"]
}
```

**Het advies is een hint, geen oordeel.** De definitieve classificatie zet een tactisch of strategisch lid handmatig op het AI-systeem via `PATCH /api/v1/ai-systems/{id}` met `eu_ai_act_risk` veld.

### Implementatie

De classifier is deterministisch (keyword-based) — geen LLM-call. Dat heeft drie voordelen:

1. **Auditbaar** — voor elk advies is exact te zien welke regel triggerde
2. **Reproduceerbaar** — zelfde input geeft altijd zelfde output
3. **Versie-stable** — geen model-drift over de tijd

De keyword-lijsten staan in [`backend/app/services/eu_ai_act_classifier.py`](../backend/app/services/eu_ai_act_classifier.py) — uitbreiden via PR met onderbouwing in de PR-beschrijving.

### Workflow

```
1. Registreer AI-systeem        →  POST /api/v1/ai-systems
2. Vraag classificatie-advies   →  POST /api/v1/ai-systems/classify-suggestion
3. Menselijke review en beslist →  (offline)
4. Zet de classificatie         →  PATCH /api/v1/ai-systems/{id}
5. Plan een conformiteits-      →  POST /api/v1/assessments
   beoordeling als 'high'           (assessment_type='ai_conformity')
6. Leg menselijk toezicht-      →  POST /api/v1/ai-hitl-checkpoints
   momenten vast
```

---

## Inwerkingtreding

Belangrijke data uit verordening 2024/1689:

| Datum | Wat treedt in werking |
|-------|----------------------|
| 1 augustus 2024 | Inwerkingtreding verordening |
| 2 februari 2025 | Art. 5 (verboden praktijken) en algemene bepalingen |
| 2 augustus 2025 | Notified bodies en governance-structuur |
| 2 augustus 2026 | Bulk van verplichtingen — inclusief hoog-risico bijlage III |
| 2 augustus 2027 | Hoog-risico bijlage I (productveiligheid-AI) |

Voor het platform betekent dit: vanaf augustus 2026 zijn de hoog-risico-verplichtingen scherp. Plan conformiteitsbeoordelingen tijdig.

---

## Verantwoordelijkheid

Deze classificatie-tool is een hulpmiddel — geen juridisch advies. De uiteindelijke classificatie en compliance-verantwoordelijkheid liggen bij:

- **Aanbieder** (provider) — wie het AI-systeem ontwikkelt of namens wie het op de markt komt
- **Gebruiker** (deployer) — wie het systeem onder eigen verantwoordelijkheid inzet

Voor gemeenten als deployer: de meeste verplichtingen liggen bij de aanbieder, maar art. 26 verplicht ook deployers tot specifieke acties (instructies opvolgen, logs bewaren, toezicht inrichten). Zie de relevante secties van de verordening.
