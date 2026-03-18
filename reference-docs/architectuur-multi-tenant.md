# Multi-tenant architectuur — Transparantiemodel

## Hoe data stroomt tussen gemeenten

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        LEIDSE REGIO                                      ║
║                                                                          ║
║   ┌─────────────────────────────────────────────────────────────────┐   ║
║   │                   REGIONAAL DASHBOARD                           │   ║
║   │                                                                 │   ║
║   │   Leiden ████████████ 78%      Leiderdorp ███████░░░ 61%       │   ║
║   │   Oegstgeest ██████░░░░ 54%    Zoeterwoude ████░░░░░░ 43%      │   ║
║   │                                                                 │   ║
║   │   Normenkader: BIO 2.0 (gedeeld)  ✓ alle 4 gemeenten           │   ║
║   └─────────────────────────────────────────────────────────────────┘   ║
║              ↑ regionaal zichtbaar        ↑ regionaal zichtbaar          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌──────────────────────┐      ┌──────────────────────┐                 ║
║  │   GEMEENTE LEIDEN    │      │  GEMEENTE LEIDERDORP  │   ...           ║
║  │                      │      │                       │                 ║
║  │  🟢 GOVERNANCE       │ ───→ │  🟢 GOVERNANCE        │                 ║
║  │  Normenkader         │ lees │  (overgenomen van     │                 ║
║  │  IB-beleid           │ baar │   Leiden of eigen)    │                 ║
║  │  Controls-templates  │      │                       │                 ║
║  │                      │      │                       │                 ║
║  │  🟡 COMPLIANCE       │ ───→ │  🟡 COMPLIANCE        │                 ║
║  │  SoA-score           │score │  SoA-score            │                 ║
║  │  Volwassenheid %     │ only │  Volwassenheid %      │                 ║
║  │  Audit-resultaten    │      │  Audit-resultaten     │                 ║
║  │                      │      │                       │                 ║
║  │  🔴 OPERATIONEEL     │      │  🔴 OPERATIONEEL      │                 ║
║  │  Verwerkingen (AVG)  │  ✗   │  Verwerkingen (AVG)  │                 ║
║  │  Concrete risico's   │nooit │  Concrete risico's   │                 ║
║  │  Persoonsgegevens    │      │  Persoonsgegevens    │                 ║
║  └──────────────────────┘      └──────────────────────┘                 ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## Deellogica per data-type

```
┌─────────────────┬──────────────────────────────┬────────────────────────┐
│ Type            │ Wat                          │ Hoe gedeeld            │
├─────────────────┼──────────────────────────────┼────────────────────────┤
│ 🟢 GOVERNANCE   │ Normenkader, controls,        │ Leiden publiceert →    │
│                 │ IB-beleid, Privacy-beleid     │ anderen lezen/adopteren │
├─────────────────┼──────────────────────────────┼────────────────────────┤
│ 🟡 COMPLIANCE   │ SoA %, volwassenheidsscores,  │ Scores zichtbaar in    │
│                 │ audit-resultaten, KPI's       │ regionaal dashboard    │
├─────────────────┼──────────────────────────────┼────────────────────────┤
│ 🔴 OPERATIONEEL │ Verwerkingen, risico's,       │ Altijd privé           │
│                 │ persoonsgegevens, incidenten  │ AVG — nooit regionaal  │
└─────────────────┴──────────────────────────────┴────────────────────────┘
```

## Hoe het technisch werkt

```
Elke entiteit in de database heeft:

  tenant_id   = "gemeente-leiden"          ← eigenaar
  visibility  = "privé" | "regionaal"      ← deelinstelling

Voorbeelden:

  Normenkader  → tenant: leiden, visibility: regionaal  ✓ zichtbaar voor regio
  SoA-score    → tenant: leiden, visibility: regionaal  ✓ zichtbaar voor regio
  Verwerking   → tenant: leiden, visibility: privé      ✗ alleen Leiden ziet dit
  Risicoregister → tenant: leiden, visibility: privé    ✗ alleen Leiden ziet dit

Regionaal dashboard filtert:
  SELECT * FROM entities
  WHERE visibility = 'regionaal'
  → toont data van alle gemeenten, maar nooit privé-data
```

## RBAC — twee soorten gebruikers

Sommige functies werken regionaal (CISO, FG, privacy officers). Het RBAC-model kent daarom twee lagen:

```
Lokale gebruiker:    gebruiker → rol → tenant
Regionale gebruiker: gebruiker → rol → tenant  (eigen gemeente)
                   + gebruiker → regionale rol → regio
```

### Lokale vs. regionale rollen

| Gebruiker | Lokale rol | Regionale rol |
|-----------|-----------|---------------|
| Luuk | TIMS-voorzitter Gemeente Leiden | — |
| Bas | CISO Gemeente Leiden (3e lijn) | Regionaal toezichthouder |
| Robert (FG) | FG Gemeente Leiden (3e lijn) | Regionaal FG |
| Leiderdorp TIMS | TIMS-voorzitter Leiderdorp | — |

### Wat een regionale rol geeft

- ✅ Compliance-scores van alle gemeenten zien
- ✅ Gedeeld normenkader en beleid lezen
- ✅ Cross-gemeente rapportages draaien
- ✅ Regionaal dashboard volledig
- ❌ Operationele data van andere gemeenten (verwerkingen, risico's) — nooit

Zelfs de regionale CISO ziet geen Leiderdorpse verwerkingen. Zijn toezichtrol gaat over het *systeem* (werkt het IMS?), niet over de *inhoud* van individuele verwerkingen.

### Technisch: één extra tabel

```
UserRegionRole:
  user_id
  region_id
  role: regionaal_toezichthouder | regionaal_coordinator | regionaal_viewer
```

## Groeipad

```
Nu (Fase 0):
  Leiden werkt alleen → visibility-veld bestaat maar alles is 'privé'

Later (Fase 1, regio doet mee):
  Leiden zet normenkader op 'regionaal'
  Leiderdorp koppelt aan → ziet normenkader, ziet Leidens scores
  Regionaal dashboard wordt actief

Nog later (meerdere regio's):
  Zelfde model, andere region_id
  Geen architectuurwijziging nodig
```
