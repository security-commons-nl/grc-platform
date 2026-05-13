# RFC 0005 — M5 UI-uitbreiding (Monte Carlo-visualisatie en simulatie-historie)

> **Status:** V1 geïmplementeerd · **Auteur:** open-source projectteam · **Datum:** 2026-05-12 (status bijgewerkt 2026-05-13)
> **Type:** Frontend + lichte backend-uitbreiding · **Module-impact:** M5 (risicokwantificatie)
> **Beslissing nodig vóór:** demo aan eerste pilot-gemeente (controllers / concernadviseur risicomanagement)
>
> **Implementatie-stand (2026-05-13)**
> - Backend: `app/services/simulation/monte_carlo.py` met uniform + triangular distributies (NumPy), reproduceerbaar via `?seed=`. `POST /api/v1/risks/{id}/simulate` met percentielen p5–p99, VaR-95/99, expected loss en optioneel `?include_samples=true` voor histogram-rendering. Simulatie-historie via `ims_risk_simulations` (Alembic 015) met auto-save per run, optionele `?label`+`?note`, lijst-endpoint `GET /risks/{id}/simulations`.
> - Frontend: `SimulationHistogram` (recharts, 30 klassen, VaR-95/99 referentielijnen) + `SimulationInterpretation` (natuurlijke-taal-uitleg met conditionele waarschuwingen voor grote spreiding en materieel staartrisico). Beide lazy-loaded via `next/dynamic`.
> - Tests: 5 vitest-tests op `simulation-interpretation`; e2e `m5-simulatie` valideert UI + API + historie + reproduceerbaarheid (seed).
> - **V2-werk in `[Unreleased]` van CHANGELOG**: CDF-curve, scenario-vergelijking-UI, PDF-export via weasyprint, dedicated `/beheer/risicos/[id]/simulaties`-route, lognormal-distributie, portfolio-aggregatie.

---

## 1. Probleem

M5 backend is operationeel (zie `ROADMAP.md` sectie "M5 — scope-beperkt" en [`docs/risico-kwantificatie.md`](../risico-kwantificatie.md)): ranges, distributies, Monte Carlo-endpoint met 10.000 iteraties, percentielen, VaR-95/99, expected loss, reproduceerbaarheid via seed.

De frontend (`frontend/src/components/beheer/simulation-results.tsx`, 119 regels) toont vandaag:

- Verwachte schade (mean)
- VaR-95 en VaR-99
- Horizontale staafbalken voor P5/P25/P50/P75/P95/P99
- Tekstuele toelichting onder grafiek

Wat *ontbreekt* voor de doelgroep "controller / concernadviseur risicomanagement":

1. **Vorm van de verdeling** — staafbalken op percentielen tonen geen vorm. Triangular en uniform leveren visueel hetzelfde plaatje op. Voor risicomanagement-discipline is dichtheid (histogram) het primaire artefact.
2. **Cumulatieve verdeling (CDF)** — laat de relatie tussen kans en bedrag zien ("Wat is de kans op meer dan €X schade?"). Dit is *de* vraag waar Monte Carlo voor wordt gebruikt.
3. **Simulatie-historie** — elke run is vandaag eenmalig. Je kunt twee runs niet vergelijken, eerdere runs niet terughalen, geen audit-trail van "wanneer is gesimuleerd door wie". Ondergraaft reproduceerbaarheid in praktijk.
4. **Scenario-vergelijking** — "Wat als we mitigatie X invoeren?" is *de* manier waarop kwantitatief risk-management waarde levert. Vandaag niet mogelijk zonder spreadsheet ernaast.
5. **Natuurlijke-taal-uitleg** — "Verwachte schade €44.987" zegt niet-specialist weinig. "In 1 op de 20 gevallen kost dit risico meer dan €78.000" wel.
6. **Dedicated simulatie-route** — simulatie-resultaat is nu embedded in het edit-formulier van een risico. Verlies van context bij herladen, geen deelbare URL.
7. **Export** — geen PDF-uitvoer voor MT-rapportage of audit-bewijs.

---

## 2. Niet-doelen

Dit RFC behandelt **niet**:

- **Portfolio-aggregatie** (simulatie over meerdere risico's tegelijk). Apart RFC nodig — vergt nieuwe backend-endpoint en heel ander UI-paradigma. Staat in M5-uitbreidingslijst.
- **Correlaties tussen risico's**. Idem.
- **Lognormal / aanvullende distributies**. Apart RFC bij klantvraag.
- **Mitigatie-modellering met expliciete control-effectiviteit**. Mitigatie-impact wordt voor nu handmatig ingevoerd als "alternatief scenario"; geen formele control-koppeling.
- **Real-time co-editing** van simulaties. Eén-gebruiker-tegelijk volstaat.

---

## 3. Voorstel

### 3.1 Visualisatie-uitbreiding

**Library-keuze:** `recharts` (~120kB gzipped, MIT-licentie, breed gebruikt in React-ecosysteem). Alternatieven afgewogen in sectie 4.

Drie nieuwe componenten naast bestaande `simulation-results.tsx`:

**(a) `SimulationHistogram` — dichtheidsplot**

- BarChart met 30 bins (vaste keuze; debat over `freedman-diaconis` parkeren)
- X-as: schade-bedrag (euro-formatter)
- Y-as: aantal trekkingen
- VaR-95 en VaR-99 als verticale referentielijnen met label
- Hover: bin-range + frequency
- Backend-aanpassing: simulate-endpoint krijgt optionele `include_samples=true` query-parameter; default `false` (terugwaarts compatibel). Bij `true` retourneert response een array `samples: number[]` (10.000 floats ≈ 80kB JSON — acceptabel).

**(b) `SimulationCdf` — cumulatieve verdeling**

- LineChart met `samples.sort()` op x-as, cumulatieve waarschijnlijkheid (0–1) op y-as
- Interactieve crosshair: gebruiker klikt op bedrag → toont "kans op ≤ dat bedrag"
- Of: gebruiker klikt op waarschijnlijkheid → toont bijbehorende drempel
- Onderliggende data: zelfde `samples`-array als histogram (geen extra fetch)

**(c) `SimulationInterpretation` — natuurlijke-taal-uitleg**

Geen library; gewone React-component met regels:

```tsx
function interpret(result: RiskSimulationResponse): string[] {
  const lines: string[] = [];
  lines.push(`Verwachte schade per voorval: ${euro(result.expected_loss)}`);
  lines.push(`In 1 op de 20 gevallen (5%) loopt de schade op tot meer dan ${euro(result.var_95)}`);
  lines.push(`In 1 op de 100 gevallen (1%) loopt de schade op tot meer dan ${euro(result.var_99)}`);
  const range = result.percentiles.p95 - result.percentiles.p5;
  const spread = range / result.expected_loss;
  if (spread > 1.5) lines.push(`De spreiding is groot — bandbreedte (P5–P95) is ${spread.toFixed(1)}× de verwachte schade. Onzekerheid weegt zwaar mee.`);
  return lines;
}
```

### 3.2 Simulatie-historie

**Nieuwe tabel `ims_risk_simulations`:**

```python
class IMSRiskSimulation(Base):
    __tablename__ = "ims_risk_simulations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    risk_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ims_risks.id"), nullable=False)
    user_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Input snapshot — risico kan ondertussen aangepast zijn, snapshot geeft reproduceerbaarheid
    distribution: Mapped[str] = mapped_column(String(20), nullable=False)
    parameters:   Mapped[dict] = mapped_column(JSONB, nullable=False)  # {min, max, mode} subset
    iterations:   Mapped[int] = mapped_column(Integer, nullable=False)
    seed:         Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Output — minimaal de samenvatting; samples niet opslaan (~80kB × N runs = bloat)
    expected_loss: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    var_95:        Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    var_99:        Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    percentiles:   Mapped[dict] = mapped_column(JSONB, nullable=False)  # {p5..p99}
    statistics:    Mapped[dict] = mapped_column(JSONB, nullable=False)  # {mean, std, min, max}

    # Optioneel: gebruikers-annotatie ("Scenario na mitigatie X")
    label:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    note:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_risk_simulations_tenant_risk", "tenant_id", "risk_id", "created_at"),
    )
```

**RLS:** standaard tenant-isolatie zoals andere `ims_*` tabellen.

**Workflow:**

- Elke `POST /api/v1/risks/{id}/simulate` slaat automatisch een row op (na de berekening, vóór response).
- Optioneel `?label=...&note=...` query-params om scenario te annoteren.
- `GET /api/v1/risks/{id}/simulations` retourneert lijst (gepagineerd, default 20).
- `GET /api/v1/risks/{id}/simulations/{sim_id}` retourneert specifieke run, opnieuw uitvoerbaar via `?rerun=true` (gebruikt opgeslagen `seed`).
- `DELETE /api/v1/risks/{id}/simulations/{sim_id}` voor opruimen (admin-only).

**Samples niet persisteren.** Reden: 10k floats × veel runs = DB-bloat. Bij `?rerun=true` met gelijke `seed` reproduceer je samples exact. Zonder seed waren samples sowieso niet vergelijkbaar.

### 3.3 Scenario-vergelijking

UI-paradigma: gebruiker selecteert 2–4 simulatie-runs uit de historie en krijgt naast-elkaar-vergelijking.

**Component `SimulationCompare`:**

- Tabel-rij per metric (expected_loss, VaR-95, VaR-99, P50, P95): waarde + delta t.o.v. baseline (eerst geselecteerde)
- Overlay-grafiek: 2–4 histogrammen / CDF's met verschillende kleuren over elkaar
- Annotatie: gebruiker noteert "scenario A: huidig", "scenario B: na invoer control X-Y"

**Backend-uitbreiding:** geen. Frontend laadt N simulaties en rendert.

**Beperking:** zonder formele control-koppeling is "scenario B" gewoon een handmatig aangepaste range/distributie. Acceptabel voor v1; control-effectiviteit-modellering is apart RFC.

### 3.4 Dedicated route

Vandaag: simulatie-resultaat wordt getoond binnen het risico-edit-form (`/beheer/risicos`). Niet deelbaar, niet bookmarkbaar.

**Nieuwe routes:**

- `/beheer/risicos/[id]/simulatie` — laatste simulatie + knop "Opnieuw simuleren"
- `/beheer/risicos/[id]/simulaties` — historie (lijst met labels, timestamps, gebruiker)
- `/beheer/risicos/[id]/simulaties/vergelijken?ids=A,B,C` — vergelijk-view

Bestaande inline `SimulationResults` blijft beschikbaar als compact widget binnen het edit-form (voor snelle iteratie).

### 3.5 Export naar PDF

**Aanpak:** server-side, **niet** client-side. Reden: consistente fonts/rendering, audit-trail (server logt wat is geëxporteerd), geen JS-versie-afhankelijkheden.

- Bestaande backend gebruikt geen PDF-library. Voorstel: `weasyprint` (Python, MIT-licentie) — leest HTML+CSS, schrijft PDF. Past bij FastAPI-stack.
- Endpoint: `GET /api/v1/risks/{id}/simulations/{sim_id}/pdf` retourneert `application/pdf`.
- Template: Jinja2 met embedded SVG (recharts kan SVG exporteren als data-url; alternatief: server rendert chart met matplotlib).
- **Eenvoudigste eerste versie:** alleen tekst + tabel + percentielen-staaf (geen histogram/CDF). Histogram/CDF in versie 2.

**Niet-doel:** Word-export, Excel-export. Eén formaat is genoeg voor demo.

---

## 4. Alternatieven (afgewezen of geparkeerd)

| Alternatief | Status |
|-------------|--------|
| **`victory` chart-library** | Afgewezen. Mooie API maar zwaarder (~200kB) en minder onderhouden recent. Geen feature die we missen. |
| **`@visx` (Airbnb)** | Geparkeerd. Zeer flexibel maar low-level — meer custom-werk per chart. Voor M5 V1 te veel. |
| **`d3` direct** | Afgewezen. Veel boilerplate; geen tijdwinst t.o.v. recharts. |
| **Histogram zonder samples (alleen percentielen interpolereren)** | Afgewezen. Misleidende vorm; defeats het Monte Carlo-doel. |
| **Samples in DB opslaan** | Afgewezen. ~80kB × N runs = bloat zonder duidelijke meerwaarde (reproduceren via `seed` werkt al). |
| **Client-side PDF (jsPDF/html2pdf)** | Afgewezen. Inconsistente rendering tussen browsers, geen server-audit-trail, fonts onbetrouwbaar. |
| **Vergelijking als overlay zonder historie-tabel** | Afgewezen. Gebruiker moet eerst weten welke runs er zijn voordat ze vergelijken — historie-tabel is voorvereiste. |

---

## 5. Risico's en mitigaties

| Risico | Mitigatie |
|--------|-----------|
| `recharts` introduceert eerste zware frontend-dependency | Acceptabel (~120kB). Lazy-import op `/beheer/risicos/[id]/simulatie`-route zodat bundel niet groeit voor inrichten-flow. |
| Samples-array (80kB) in response te groot voor mobiel | Default `include_samples=false`. UI fetcht samples alleen op simulatie-detail-pagina, niet in lijst-views. |
| Simulatie-historie groeit ongelimiteerd | Soft-cap: lijst-endpoint paginerend (20/page). Geen automatische purge — admin DELETE-endpoint volstaat. Indexering dekt performance. |
| PDF-templating als nieuwe complexity-bron | Eerste versie bewust beperkt (tekst + tabel). Histogram in versie 2 wanneer use case duidelijker is. |
| Natuurlijke-taal-interpretatie geeft verkeerd beeld bij rare distributies | Tooltip met formele definitie naast elke natural-language-zin. Bron-tekst gelinkt aan [`docs/risico-kwantificatie.md`](../risico-kwantificatie.md). |
| Vergelijking suggereert oorzakelijkheid die er niet is | UI-tekst explicit: "vergelijking toont rekenkundig verschil, geen bewezen mitigatie-effect". |
| Server-side PDF rendering verhoogt latency | Endpoint is `GET` met `Cache-Control: private, max-age=3600` op simulatie-id (resultaten zijn immutable per sim_id). Generatie eenmaal. |

---

## 6. Acceptatie-criteria

Dit RFC is "geïmplementeerd" wanneer:

- [ ] `recharts` toegevoegd aan `frontend/package.json`
- [ ] Backend: `simulate`-endpoint accepteert `include_samples=true` query-param; nieuwe tabel `ims_risk_simulations` via Alembic; CRUD-endpoints voor historie operationeel
- [ ] Frontend-componenten `SimulationHistogram`, `SimulationCdf`, `SimulationInterpretation`, `SimulationCompare` aanwezig
- [ ] Nieuwe routes `/beheer/risicos/[id]/simulatie`, `/simulaties`, `/simulaties/vergelijken` werken
- [ ] PDF-export via `weasyprint` (alleen tekst + percentielen-staaf in V1)
- [ ] Backend-tests: simulatie wordt opgeslagen, lijst-endpoint paginerend, RLS-isolatie tussen tenants, `?rerun=true` reproduceert met seed
- [ ] Frontend e2e Playwright-spec: open risico → simuleer → zie histogram → simulate opnieuw met label → vergelijk twee runs
- [ ] `docs/risico-kwantificatie.md` uitgebreid met sectie "Visualisatie en historie"

---

## 7. Open vragen voor discussie

1. **Aantal histogram-bins**: 30 vast, of `floor(sqrt(N))` (~100 bij N=10k)? 30 leest beter; 100 toont fijnere structuur. Voorstel: 30 default met UI-toggle "fijner".
2. **Bewaarbeleid `samples`**: niet opslaan (huidig voorstel) → herrekenen kost compute bij CDF/histogram-view; opslaan → 80kB × N. Compromis: cache laatste run in Redis (TTL 24h) zodat veelgebruikte pagina's snel zijn.
3. **Annotatie-velden** (label, note): vrije tekst nu — moeten we structuur opleggen (bv. dropdown "scenario-type: baseline / na-mitigatie / worst-case")? Vrij start; bij vraag uitbreiden.
4. **Toegang historie**: alle rollen die risico mogen lezen? Of alleen admin/risk-officer? Voorstel: zelfde permissies als risico-lezen.
5. **PDF-template thematisering**: tenant-logo in header? Tenant-config-tabel kennen we al; uitbreiden of overslaan voor V1?
6. **Vergelijking-maximum**: 4 runs (huidig voorstel), 2, 6? Visueel werkt 4 nog; meer wordt confetti. Hardlimiet 4.

---

## 8. Beslismomenten

- **Goedkeuring RFC** vóór recharts-toevoeging en Alembic-migratie
- **Per-tenant beslissing**: gebruikt klant simulatie-historie wel/niet? UI moet beide werken (lege historie = leeg-state met uitleg).
- **Acceptatie scope V1**: alleen tekst+staaf in PDF; histogram/CDF in versie 2. Expliciet gecommuniceerd.

---

## 9. Referenties

- Beslispunt 4 in intern document `grc-platform-beslispunten.md` — UI-verrijking M5 (deze RFC operationaliseert dat)
- `docs/risico-kwantificatie.md` — backend-API en distributies
- `frontend/src/components/beheer/simulation-results.tsx` — bestaande inline-weergave
- `frontend/src/app/(protected)/beheer/risicos/page.tsx` — bestaand risico-edit-form
- recharts: https://recharts.org/
- weasyprint: https://weasyprint.org/

---

## Changelog

| Datum | Wijziging | Door |
|-------|-----------|------|
| 2026-05-12 | Initieel concept | open-source projectteam |
