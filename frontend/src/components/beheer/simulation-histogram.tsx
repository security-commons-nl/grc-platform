'use client';

import { useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const BIN_COUNT = 30;

const euroShort = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
  notation: 'compact',
});

const euroFull = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
});

type Bin = {
  start: number;
  end: number;
  center: number;
  count: number;
  label: string;
};

function makeBins(samples: number[], binCount: number): Bin[] {
  if (samples.length === 0) return [];
  let min = samples[0];
  let max = samples[0];
  for (const s of samples) {
    if (s < min) min = s;
    if (s > max) max = s;
  }
  const range = max - min;
  if (range === 0) {
    return [
      {
        start: min,
        end: max,
        center: min,
        count: samples.length,
        label: euroShort.format(min),
      },
    ];
  }
  const width = range / binCount;
  const bins: Bin[] = [];
  for (let i = 0; i < binCount; i++) {
    const start = min + i * width;
    const end = i === binCount - 1 ? max : start + width;
    bins.push({
      start,
      end,
      center: (start + end) / 2,
      count: 0,
      label: euroShort.format((start + end) / 2),
    });
  }
  for (const s of samples) {
    let idx = Math.floor((s - min) / width);
    if (idx >= binCount) idx = binCount - 1;
    if (idx < 0) idx = 0;
    bins[idx].count += 1;
  }
  return bins;
}

function TooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: Bin }>;
}) {
  if (!active || !payload || payload.length === 0) return null;
  const bin = payload[0].payload;
  return (
    <div className="rounded border border-neutral-200 bg-white px-3 py-2 text-xs shadow-sm">
      <div className="font-semibold text-neutral-900">
        {euroFull.format(bin.start)} &ndash; {euroFull.format(bin.end)}
      </div>
      <div className="text-neutral-600">
        {bin.count.toLocaleString('nl-NL')} simulaties
      </div>
    </div>
  );
}

export function SimulationHistogram({
  samples,
  var95,
  var99,
  expectedLoss,
}: {
  samples: number[];
  var95: number;
  var99: number;
  expectedLoss: number;
}) {
  const bins = useMemo(() => makeBins(samples, BIN_COUNT), [samples]);

  if (bins.length === 0) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm text-neutral-500">
        Geen samples beschikbaar — vraag opnieuw simulatie aan met
        <code className="mx-1 rounded bg-neutral-100 px-1 py-0.5 text-xs">
          include_samples=true
        </code>
        voor visualisatie.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-3">
      <div className="mb-2 flex items-baseline justify-between">
        <div className="text-xs uppercase tracking-wide text-neutral-500">
          Verdeling van schade-uitkomsten
        </div>
        <div className="text-xs text-neutral-500">
          {samples.length.toLocaleString('nl-NL')} simulaties &middot; {BIN_COUNT} klassen
        </div>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={bins}
            margin={{ top: 16, right: 16, bottom: 8, left: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="center"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(v: number) => euroShort.format(v)}
              tick={{ fontSize: 11, fill: '#64748b' }}
              stroke="#cbd5e1"
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#64748b' }}
              stroke="#cbd5e1"
              allowDecimals={false}
            />
            <Tooltip content={<TooltipContent />} cursor={{ fill: '#f1f5f9' }} />
            <Bar
              dataKey="count"
              fill="#3b82f6"
              fillOpacity={0.65}
              isAnimationActive={false}
            />
            <ReferenceLine
              x={expectedLoss}
              stroke="#0f172a"
              strokeDasharray="4 2"
              label={{
                value: `EL ${euroShort.format(expectedLoss)}`,
                position: 'top',
                fontSize: 10,
                fill: '#0f172a',
              }}
            />
            <ReferenceLine
              x={var95}
              stroke="#dc2626"
              strokeDasharray="2 2"
              label={{
                value: `VaR-95 ${euroShort.format(var95)}`,
                position: 'top',
                fontSize: 10,
                fill: '#dc2626',
              }}
            />
            <ReferenceLine
              x={var99}
              stroke="#7c2d12"
              strokeDasharray="2 2"
              label={{
                value: `VaR-99 ${euroShort.format(var99)}`,
                position: 'top',
                fontSize: 10,
                fill: '#7c2d12',
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-xs text-neutral-500">
        Elke staaf telt hoe vaak een schade-bedrag in deze klasse voorkwam over alle simulaties.
        De rode lijnen markeren de drempels waarboven respectievelijk 5% (VaR-95) en 1% (VaR-99) van de scenario&apos;s vallen.
      </p>
    </div>
  );
}
