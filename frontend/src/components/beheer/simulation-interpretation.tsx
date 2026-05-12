'use client';

import type { RiskSimulationResponse } from '@/lib/api-types';

const euro = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
});

type Severity = 'info' | 'warning';

type Sentence = {
  text: string;
  severity: Severity;
};

function buildSentences(result: RiskSimulationResponse): Sentence[] {
  const lines: Sentence[] = [];

  lines.push({
    severity: 'info',
    text: `Verwachte schade per voorval: ${euro.format(result.expected_loss)} (gemiddelde over ${result.iterations.toLocaleString('nl-NL')} simulaties).`,
  });

  lines.push({
    severity: 'info',
    text: `In 1 op de 20 gevallen (5%) loopt de schade op tot meer dan ${euro.format(result.var_95)}.`,
  });

  lines.push({
    severity: 'info',
    text: `In 1 op de 100 gevallen (1%) loopt de schade op tot meer dan ${euro.format(result.var_99)}.`,
  });

  const range = result.percentiles.p95 - result.percentiles.p5;
  const spread = result.expected_loss > 0 ? range / result.expected_loss : 0;
  if (spread > 1.5) {
    lines.push({
      severity: 'warning',
      text: `De spreiding is groot — bandbreedte tussen P5 en P95 is ${spread.toFixed(1)}× de verwachte schade. Onzekerheid weegt zwaar mee; overweeg of een puntschatting hier nog informatief is.`,
    });
  }

  const tailRatio =
    result.expected_loss > 0 ? result.var_99 / result.expected_loss : 0;
  if (tailRatio > 3) {
    lines.push({
      severity: 'warning',
      text: `Staartrisico is materieel — VaR-99 is ${tailRatio.toFixed(1)}× de verwachte schade. Het zeldzame-maar-grote-schade-scenario verdient aparte aandacht in mitigatie.`,
    });
  }

  return lines;
}

export function SimulationInterpretation({
  result,
}: {
  result: RiskSimulationResponse;
}) {
  const sentences = buildSentences(result);

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-3">
      <div className="mb-2 text-xs uppercase tracking-wide text-neutral-500">
        Interpretatie
      </div>
      <ul className="space-y-1.5">
        {sentences.map((s, i) => (
          <li
            key={i}
            className={`flex gap-2 text-sm ${
              s.severity === 'warning' ? 'text-amber-800' : 'text-neutral-700'
            }`}
          >
            <span
              aria-hidden
              className={`mt-1.5 inline-block size-1.5 shrink-0 rounded-full ${
                s.severity === 'warning' ? 'bg-amber-500' : 'bg-neutral-400'
              }`}
            />
            <span>{s.text}</span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-neutral-500">
        Interpretatie is een hulpmiddel; de onderliggende waarden (expected loss, VaR-95/99, percentielen) blijven leidend.
        Zie <a className="underline" href="/docs/risico-kwantificatie" target="_blank">documentatie</a> voor de formele definities.
      </p>
    </div>
  );
}
