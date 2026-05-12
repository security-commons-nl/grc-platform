import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SimulationInterpretation } from './simulation-interpretation';
import type { RiskSimulationResponse } from '@/lib/api-types';

function makeResult(
  overrides: Partial<RiskSimulationResponse> = {},
): RiskSimulationResponse {
  return {
    risk_id: 'risk-1',
    distribution: 'triangular',
    parameters: { min: 10000, mode: 25000, max: 100000 },
    iterations: 10000,
    statistics: { mean: 44987, std: 18234, min: 10012, max: 99876 },
    percentiles: { p5: 15234, p25: 28456, p50: 42345, p75: 58234, p95: 78456, p99: 89234 },
    expected_loss: 44987,
    var_95: 78456,
    var_99: 89234,
    ...overrides,
  };
}

describe('SimulationInterpretation', () => {
  it('toont 1-op-20 en 1-op-100 zinnen met bedragen', () => {
    render(<SimulationInterpretation result={makeResult()} />);
    expect(
      screen.getByText(/In 1 op de 20 gevallen .*5%.* loopt de schade op tot meer dan/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/In 1 op de 100 gevallen .*1%.* loopt de schade op tot meer dan/),
    ).toBeInTheDocument();
  });

  it('toont verwachte schade met aantal iteraties', () => {
    render(<SimulationInterpretation result={makeResult({ iterations: 5000 })} />);
    expect(
      screen.getByText(/Verwachte schade per voorval/),
    ).toBeInTheDocument();
    expect(screen.getByText(/5\.000 simulaties/)).toBeInTheDocument();
  });

  it('toont spread-waarschuwing als P95-P5 > 1.5× expected loss', () => {
    // P5=10k, P95=100k → range 90k. EL=30k → spread 3.0x → waarschuwing
    render(
      <SimulationInterpretation
        result={makeResult({
          expected_loss: 30000,
          percentiles: { p5: 10000, p25: 15000, p50: 25000, p75: 60000, p95: 100000, p99: 120000 },
        })}
      />,
    );
    expect(screen.getByText(/spreiding is groot/i)).toBeInTheDocument();
  });

  it('toont géén spread-waarschuwing bij smalle spreiding', () => {
    // P5=29k, P95=31k → range 2k. EL=30k → spread 0.07 → geen waarschuwing
    render(
      <SimulationInterpretation
        result={makeResult({
          expected_loss: 30000,
          percentiles: { p5: 29000, p25: 29500, p50: 30000, p75: 30500, p95: 31000, p99: 31500 },
          var_95: 31000,
          var_99: 31500,
        })}
      />,
    );
    expect(screen.queryByText(/spreiding is groot/i)).not.toBeInTheDocument();
  });

  it('toont staartrisico-waarschuwing als VaR-99 > 3× expected loss', () => {
    render(
      <SimulationInterpretation
        result={makeResult({
          expected_loss: 10000,
          var_99: 40000,
          percentiles: { p5: 5000, p25: 7000, p50: 9000, p75: 12000, p95: 25000, p99: 40000 },
        })}
      />,
    );
    expect(screen.getByText(/Staartrisico is materieel/i)).toBeInTheDocument();
  });
});
