'use client';

import dynamic from 'next/dynamic';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SimulationInterpretation } from '@/components/beheer/simulation-interpretation';
import type { RiskSimulationResponse } from '@/lib/api-types';

// Lazy-load histogram zodat recharts-bundle (~120kB) niet in elke pagina-bundle landt.
const SimulationHistogram = dynamic(
  () => import('@/components/beheer/simulation-histogram').then((m) => m.SimulationHistogram),
  {
    ssr: false,
    loading: () => (
      <div className="h-64 animate-pulse rounded-lg border border-neutral-200 bg-neutral-50" />
    ),
  },
);

const euro = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
});

function PercentileBar({
  label,
  value,
  max,
  emphasis = false,
}: {
  label: string;
  value: number;
  max: number;
  emphasis?: boolean;
}) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="flex items-center gap-3">
      <span className={`w-12 text-xs ${emphasis ? 'font-semibold text-neutral-900' : 'text-neutral-500'}`}>
        {label}
      </span>
      <div className="relative flex-1 h-6 rounded bg-neutral-100 overflow-hidden">
        <div
          className={`absolute inset-y-0 left-0 ${
            emphasis ? 'bg-red-500/80' : 'bg-primary-500/60'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`w-28 text-right text-sm tabular-nums ${emphasis ? 'font-semibold text-neutral-900' : 'text-neutral-700'}`}>
        {euro.format(value)}
      </span>
    </div>
  );
}

export function SimulationResults({
  result,
  riskTitle,
  onDismiss,
}: {
  result: RiskSimulationResponse;
  riskTitle?: string;
  onDismiss: () => void;
}) {
  const max = result.statistics.max;
  const distLabel = result.distribution === 'uniform' ? 'Uniform' : 'Triangular';

  return (
    <Card className="mb-4 border-primary-200 bg-primary-50/40">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-base font-semibold text-neutral-900">
            Monte Carlo-simulatie
            {riskTitle && <span className="text-neutral-500 font-normal"> — {riskTitle}</span>}
          </h3>
          <p className="mt-1 text-xs text-neutral-600">
            <Badge variant="primary">{distLabel}</Badge>{' '}
            <span className="ml-1">
              parameters: {Object.entries(result.parameters).map(([k, v]) => `${k}=${euro.format(v)}`).join(', ')}
            </span>
            <span className="ml-2 text-neutral-500">· {result.iterations.toLocaleString('nl-NL')} iteraties</span>
          </p>
        </div>
        <button
          onClick={onDismiss}
          className="text-xs text-neutral-500 hover:text-neutral-700"
        >
          Sluiten
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 mb-4">
        <div className="rounded-lg bg-white border border-neutral-200 p-3">
          <div className="text-xs uppercase tracking-wide text-neutral-500">Verwachte schade</div>
          <div className="text-2xl font-semibold text-neutral-900 mt-1">
            {euro.format(result.expected_loss)}
          </div>
          <div className="text-xs text-neutral-500 mt-1">
            gemiddelde van alle simulaties (std: {euro.format(result.statistics.std)})
          </div>
        </div>
        <div className="rounded-lg bg-white border border-red-200 p-3">
          <div className="text-xs uppercase tracking-wide text-red-700">Value-at-Risk 95% / 99%</div>
          <div className="text-2xl font-semibold text-neutral-900 mt-1 tabular-nums">
            {euro.format(result.var_95)}
            <span className="text-base text-neutral-500"> / {euro.format(result.var_99)}</span>
          </div>
          <div className="text-xs text-neutral-500 mt-1">
            In 95% van de scenario&apos;s blijft de schade onder VaR-95
          </div>
        </div>
      </div>

      {result.samples && result.samples.length > 0 && (
        <div className="mb-4">
          <SimulationHistogram
            samples={result.samples}
            var95={result.var_95}
            var99={result.var_99}
            expectedLoss={result.expected_loss}
          />
        </div>
      )}

      <div className="rounded-lg bg-white border border-neutral-200 p-3 mb-4">
        <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">Percentielen (samenvattend)</div>
        <div className="space-y-1.5">
          <PercentileBar label="P5"  value={result.percentiles.p5}  max={max} />
          <PercentileBar label="P25" value={result.percentiles.p25} max={max} />
          <PercentileBar label="P50" value={result.percentiles.p50} max={max} />
          <PercentileBar label="P75" value={result.percentiles.p75} max={max} />
          <PercentileBar label="P95" value={result.percentiles.p95} max={max} emphasis />
          <PercentileBar label="P99" value={result.percentiles.p99} max={max} emphasis />
        </div>
        <div className="mt-2 text-xs text-neutral-500">
          P50 is de mediaan. P95 en P99 zijn de drempels waaronder respectievelijk 95% en 99% van de scenario&apos;s vallen.
        </div>
      </div>

      <SimulationInterpretation result={result} />
    </Card>
  );
}
