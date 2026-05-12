import { describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { useState, type ReactNode } from 'react';
import { SWRConfig } from 'swr';
import { OrgUnitSelect } from './org-unit-select';
import { server } from '@/test/msw-server';

// Geef elke test een verse SWR-cache, anders deelt de hele suite één
// cache-instance en blijven oude responses hangen.
function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

const API = 'http://localhost:8000/api/v1';

function mockUnits(units: Array<{ id: string; name: string; code?: string | null }>) {
  server.use(
    http.get(`${API}/organizational-units/`, () =>
      HttpResponse.json(
        units.map((u) => ({
          id: u.id,
          tenant_id: 't',
          parent_id: null,
          name: u.name,
          code: u.code ?? null,
          unit_type: 'cluster',
          is_active: true,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        })),
      ),
    ),
  );
}

function Wrapper({ initial = '' }: { initial?: string }) {
  const [value, setValue] = useState(initial);
  return (
    <>
      <OrgUnitSelect value={value} onChange={setValue} />
      <output data-testid="value">{value}</output>
    </>
  );
}

describe('OrgUnitSelect', () => {
  it('toont default-label "Organisatie-eenheid" en placeholder-optie', async () => {
    mockUnits([]);
    render(withFreshSwr(<Wrapper />));
    await waitFor(() =>
      expect(screen.getByLabelText('Organisatie-eenheid')).toBeInTheDocument(),
    );
    // Standaard placeholder
    expect(
      screen.getByRole('option', { name: 'Tenant-niveau (geen unit)' }),
    ).toBeInTheDocument();
  });

  it('rendert opties uit API met "Naam (code)"-format als code aanwezig is', async () => {
    mockUnits([
      { id: 'u1', name: 'Cluster Bedrijfsvoering', code: 'BV' },
      { id: 'u2', name: 'Team Beleid', code: null },
    ]);
    render(withFreshSwr(<Wrapper />));
    await waitFor(() =>
      expect(
        screen.getByRole('option', { name: 'Cluster Bedrijfsvoering (BV)' }),
      ).toBeInTheDocument(),
    );
    // Geen code → puur de naam
    expect(
      screen.getByRole('option', { name: 'Team Beleid' }),
    ).toBeInTheDocument();
  });

  it('propageert selectie via onChange', async () => {
    const user = userEvent.setup();
    mockUnits([{ id: 'unit-abc', name: 'Cluster X', code: 'X' }]);
    render(withFreshSwr(<Wrapper />));

    await waitFor(() =>
      expect(
        screen.getByRole('option', { name: 'Cluster X (X)' }),
      ).toBeInTheDocument(),
    );

    await user.selectOptions(
      screen.getByLabelText('Organisatie-eenheid'),
      'unit-abc',
    );
    expect(screen.getByTestId('value').textContent).toBe('unit-abc');
  });

  it('respecteert custom label en placeholder (filter-modus)', async () => {
    mockUnits([{ id: 'u', name: 'Cluster', code: null }]);
    function Filter() {
      const [v, setV] = useState('');
      return (
        <OrgUnitSelect
          value={v}
          onChange={setV}
          label="Filter op organisatie-eenheid"
          placeholder="Alle units (tenant-totaal)"
        />
      );
    }
    render(withFreshSwr(<Filter />));
    expect(
      await screen.findByLabelText('Filter op organisatie-eenheid'),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('option', { name: 'Alle units (tenant-totaal)' }),
    ).toBeInTheDocument();
  });
});
