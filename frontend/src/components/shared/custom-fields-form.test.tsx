import { describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { useState, type ReactNode } from 'react';
import { SWRConfig } from 'swr';
import { CustomFieldsForm } from './custom-fields-form';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

type DefShape = {
  field_name: string;
  display_label: string;
  json_schema: Record<string, unknown>;
  is_required?: boolean;
  help_text?: string | null;
};

function mockDefs(entity: string, defs: DefShape[]) {
  server.use(
    http.get(`${API}/custom-fields/`, ({ request }) => {
      const url = new URL(request.url);
      const want = url.searchParams.get('entity_type');
      if (entity && want !== entity) return HttpResponse.json([]);
      return HttpResponse.json(
        defs.map((d, i) => ({
          id: `def-${i}`,
          tenant_id: 't',
          entity_type: entity,
          field_name: d.field_name,
          display_label: d.display_label,
          json_schema: d.json_schema,
          is_required: d.is_required ?? false,
          display_order: 0,
          help_text: d.help_text ?? null,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        })),
      );
    }),
  );
}

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

function Wrapper({ entityType = 'risk' as const }: { entityType?: 'risk' | 'control' | 'assessment' | 'finding' }) {
  const [value, setValue] = useState<Record<string, unknown>>({});
  return (
    <>
      <CustomFieldsForm entityType={entityType} value={value} onChange={setValue} />
      <output data-testid="value">{JSON.stringify(value)}</output>
    </>
  );
}

describe('CustomFieldsForm', () => {
  it('rendert niets als er geen definities zijn', async () => {
    mockDefs('risk', []);
    const { container } = render(withFreshSwr(<Wrapper />));
    // Wacht tot de "laden..."-state weg is
    await waitFor(() =>
      expect(container.querySelector('output')?.textContent).toBe('{}'),
    );
    expect(screen.queryByText('Aanvullende velden (tenant-specifiek)')).toBeNull();
  });

  it('rendert string-input en update onChange-state', async () => {
    mockDefs('risk', [
      {
        field_name: 'kadernota_programma',
        display_label: 'Kadernota-programma',
        json_schema: { type: 'string', maxLength: 100 },
      },
    ]);
    const user = userEvent.setup();
    render(withFreshSwr(<Wrapper />));

    const input = await screen.findByLabelText('Kadernota-programma');
    await user.type(input, 'Programma 5');
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({
      kadernota_programma: 'Programma 5',
    });
  });

  it('rendert enum als select met opties', async () => {
    mockDefs('control', [
      {
        field_name: 'criticality',
        display_label: 'Kritiekheid',
        json_schema: { type: 'string', enum: ['Laag', 'Midden', 'Hoog'] },
      },
    ]);
    const user = userEvent.setup();
    render(withFreshSwr(<Wrapper entityType="control" />));

    const select = await screen.findByLabelText('Kritiekheid');
    expect(screen.getByRole('option', { name: 'Laag' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Midden' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Hoog' })).toBeInTheDocument();

    await user.selectOptions(select, 'Hoog');
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({
      criticality: 'Hoog',
    });
  });

  it('rendert number-input en cast naar Number', async () => {
    mockDefs('risk', [
      {
        field_name: 'budget',
        display_label: 'Budget (€)',
        json_schema: { type: 'number' },
      },
    ]);
    const user = userEvent.setup();
    render(withFreshSwr(<Wrapper />));

    const input = await screen.findByLabelText('Budget (€)');
    await user.type(input, '4200');
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({
      budget: 4200,
    });
  });

  it('rendert boolean-checkbox en update naar true/false', async () => {
    mockDefs('finding', [
      {
        field_name: 'gerapporteerd_aan_ap',
        display_label: 'Gerapporteerd aan AP',
        json_schema: { type: 'boolean' },
      },
    ]);
    const user = userEvent.setup();
    render(withFreshSwr(<Wrapper entityType="finding" />));

    const cb = (await screen.findByRole('checkbox')) as HTMLInputElement;
    await user.click(cb);
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({
      gerapporteerd_aan_ap: true,
    });
  });

  it('toont required-marker (*) als is_required=true', async () => {
    mockDefs('risk', [
      {
        field_name: 'verplicht_veld',
        display_label: 'Verplicht veld',
        json_schema: { type: 'string' },
        is_required: true,
      },
    ]);
    render(withFreshSwr(<Wrapper />));
    expect(await screen.findByLabelText('Verplicht veld *')).toBeInTheDocument();
  });

  it('verwijdert key uit state bij leegmaken (string)', async () => {
    mockDefs('risk', [
      {
        field_name: 'opt_text',
        display_label: 'Optionele tekst',
        json_schema: { type: 'string' },
      },
    ]);
    const user = userEvent.setup();
    render(withFreshSwr(<Wrapper />));
    const input = await screen.findByLabelText('Optionele tekst');
    await user.type(input, 'iets');
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({
      opt_text: 'iets',
    });
    await user.clear(input);
    expect(JSON.parse(screen.getByTestId('value').textContent ?? '{}')).toEqual({});
  });
});
