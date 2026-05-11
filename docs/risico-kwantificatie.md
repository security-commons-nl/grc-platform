# Risicokwantificatie (M5)

> Monte Carlo-simulatie op financiële impact-distributies voor risico's in `ims_risks`. Aanvulling op de kwalitatieve likelihood × impact-matrix.

Het platform ondersteunt twee impact-modellen naast elkaar:

| Model | Veld | Wanneer |
|-------|------|---------|
| **Point estimate** | `financial_impact_eur` (single waarde) | Wanneer één bedrag het beste de impact omschrijft |
| **Distributie** | `financial_impact_min_eur` + `financial_impact_max_eur` + `impact_distribution` | Wanneer onzekerheid expliciet meegerekend moet worden |

De kwantitatieve uitbreiding is **bewust scope-beperkt** (zie [`modules.md`](modules.md) sectie M5): organisatie-units (team/cluster), planning-en-control-koppeling, en configureerbare velden zijn niet opgenomen in deze iteratie.

---

## Distributies

### Uniform

Elke waarde tussen `financial_impact_min_eur` en `financial_impact_max_eur` is even waarschijnlijk. Gebruik wanneer je geen aanwijzing hebt dat de impact richting een bepaalde waarde neigt.

| Veld | Verplicht |
|------|-----------|
| `financial_impact_min_eur` | ja |
| `financial_impact_max_eur` | ja |
| `financial_impact_eur` | optioneel (niet gebruikt) |

### Triangular

Driehoekige verdeling met piek op `financial_impact_eur` (de mode). Meest gebruikte distributie in pragmatisch risicowerk omdat je drie waarden expert-judgemenstijl invult: best-case, meest waarschijnlijk, worst-case.

| Veld | Verplicht |
|------|-----------|
| `financial_impact_min_eur` | ja — best-case |
| `financial_impact_eur` | ja — meest waarschijnlijke (mode) |
| `financial_impact_max_eur` | ja — worst-case |

Voorbeeld: bij een ransomware-incident verwacht je in 80% van de gevallen ~€25k aan herstelkosten (mode), met een ondergrens van €10k en een uitschieter naar €100k. Triangular(10000, 25000, 100000).

---

## API

### Simulatie uitvoeren

```http
POST /api/v1/risks/{risk_id}/simulate?iterations=10000&seed=42
Authorization: Bearer <token>
```

Query-parameters:

| Param | Default | Range |
|-------|---------|-------|
| `iterations` | 10000 | 1000–1000000 |
| `seed` | (geen) | integer, voor reproduceerbare runs |

Voorbeeld-response:

```json
{
  "risk_id": "31b013ae-...",
  "distribution": "triangular",
  "parameters": {"min": 10000, "mode": 25000, "max": 100000},
  "iterations": 10000,
  "statistics": {
    "mean": 44987.34,
    "std": 18234.56,
    "min": 10012.45,
    "max": 99876.21
  },
  "percentiles": {
    "p5":  15234.12,
    "p25": 28456.78,
    "p50": 42345.67,
    "p75": 58234.12,
    "p95": 78456.78,
    "p99": 89234.45
  },
  "expected_loss": 44987.34,
  "var_95": 78456.78,
  "var_99": 89234.45
}
```

### Interpretatie

| Term | Betekenis |
|------|-----------|
| **expected_loss** | Gemiddelde schade over alle simulaties. "Wat verwachten we gemiddeld te verliezen als dit risico zich materialiseert." |
| **var_95** | Value-at-Risk op 95%. "In 95% van de gevallen blijft de schade onder dit bedrag." |
| **var_99** | Idem voor 99%. Gangbaar voor zeldzame-maar-grote-impact scenario's. |
| **percentiles** | Verdeling — `p50` is mediaan, `p95` is de 1-op-20-uitschieter. |

---

## Validatie

De simulatie-endpoint geeft 400 wanneer:
- Het risico heeft geen `impact_distribution`, of staat op `single`
- Bij `uniform`: `financial_impact_min_eur` of `financial_impact_max_eur` ontbreekt
- Bij `triangular`: een van de drie velden ontbreekt of `mode` ligt buiten `[min, max]`

DB-niveau check-constraints:
- `impact_distribution` mag alleen 'single', 'uniform' of 'triangular' zijn
- `financial_impact_max_eur` ≥ `financial_impact_min_eur` (als beide gezet)

---

## Reproduceerbaarheid

Specificeer `seed=<int>` in de query-parameters om identieke samples te krijgen bij herhaalde runs. Dit is bedoeld voor:
- Audit-trail (laat zien dat de uitkomst bij dezelfde input gelijk blijft)
- Vergelijken van twee mitigatie-scenario's met dezelfde "onderliggende toevalstrekking"

Zonder seed gebruikt NumPy een niet-deterministische RNG.

---

## Wat NIET in M5 zit

Bewust uitgesteld tot er klantvraag voor is buiten één gemeente:

- **Organisatie-units** (team / cluster / afdeling) — risico's blijven onder tenant-niveau aggregeerbaar via `scope_id`, maar geen hiërarchische org-structuur
- **Planning-en-control-cyclus** — geen first-class `ims_planning_cycles` of `ims_objectives` tabellen
- **Lognormal-distributie** — alleen uniform + triangular nu; lognormal later wanneer er gevraagd wordt
- **Aggregatie over meerdere risico's** — simulatie is per-risico, niet over een portfolio
- **Correlaties tussen risico's** — onafhankelijke trekking per risico

Voor uitbreiding: open een GitHub Discussion of issue met de concrete use case.

---

## Theoretisch raamwerk

Voor lezers nieuw bij Monte Carlo / kwantitatief risicomanagement:

1. **Onzekerheid expliciet maken**: in plaats van één getal (€50k) een range (€10k–€100k met meest waarschijnlijke €25k)
2. **Vele scenario's simuleren**: NumPy trekt N willekeurige waarden uit de distributie (default 10.000)
3. **Statistieken berekenen**: gemiddelde, percentielen, VaR
4. **Beslissen**: op basis van de hele verdeling, niet één punt

Verdere lectuur:
- *How to Measure Anything in Cybersecurity Risk* — Douglas Hubbard
- *FAIR (Factor Analysis of Information Risk)* — methodiek waar deze module pragmatisch op aansluit
