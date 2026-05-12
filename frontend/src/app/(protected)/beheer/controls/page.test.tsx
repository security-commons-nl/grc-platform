import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import ControlsPage from './page';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

function mockEmptyControls() {
  server.use(http.get(`${API}/controls/`, () => HttpResponse.json([])));
}

function mockNoOrgUnits() {
  server.use(
    http.get(`${API}/organizational-units/`, () => HttpResponse.json([])),
  );
}

function mockNoCustomFields() {
  server.use(
    http.get(`${API}/custom-fields/`, () => HttpResponse.json([])),
  );
}

describe('Controls pagina (RFC 0001 + 0002)', () => {
  it('toont empty-state als er geen controls zijn', async () => {
    mockEmptyControls();
    mockNoOrgUnits();
    render(withFreshSwr(<ControlsPage />));
    expect(await screen.findByText('Nog geen controls')).toBeInTheDocument();
  });

  it('form bevat OrgUnitSelect + render custom-fields-form-block bij definities', async () => {
    mockEmptyControls();
    mockNoOrgUnits();
    server.use(
      http.get(`${API}/custom-fields/`, ({ request }) => {
        const url = new URL(request.url);
        if (url.searchParams.get('entity_type') !== 'control') {
          return HttpResponse.json([]);
        }
        return HttpResponse.json([
          {
            id: 'd1',
            tenant_id: 't',
            entity_type: 'control',
            field_name: 'kpgm',
            display_label: 'Kadernota-programma',
            json_schema: { type: 'string' },
            is_required: false,
            display_order: 0,
            help_text: null,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]);
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<ControlsPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuwe control' }));
    await screen.findByRole('heading', { name: 'Nieuwe control' });

    // Custom-field-input verschijnt zodra defs geladen zijn
    expect(
      await screen.findByLabelText('Kadernota-programma'),
    ).toBeInTheDocument();
    // OrgUnitSelect zit erin (form-versie, niet de filter)
    expect(
      screen.getAllByLabelText('Organisatie-eenheid').length,
    ).toBeGreaterThanOrEqual(1);
  });

  it('submit met alleen-verplichte-velden roept create + stuurt geen org-unit/custom-attr mee', async () => {
    mockEmptyControls();
    mockNoOrgUnits();
    mockNoCustomFields();
    const createSpy = vi.fn();
    server.use(
      http.post(`${API}/controls/`, async ({ request }) => {
        createSpy(await request.json());
        return HttpResponse.json(
          {
            id: 'c-1',
            tenant_id: 't',
            requirement_id: null,
            title: 'Toegangsbeheer',
            description: '',
            domain: 'ISMS',
            owner_user_id: null,
            implementation_status: 'operationeel',
            implementation_date: null,
            organizational_unit_id: null,
            custom_attributes: {},
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<ControlsPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuwe control' }));
    await user.type(screen.getByLabelText('Titel *'), 'Toegangsbeheer');
    await user.selectOptions(screen.getByLabelText('Domein *'), 'ISMS');
    await user.selectOptions(
      screen.getByLabelText('Implementatiestatus *'),
      'operationeel',
    );
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));

    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    const payload = createSpy.mock.calls[0][0];
    expect(payload).toMatchObject({
      title: 'Toegangsbeheer',
      domain: 'ISMS',
      implementation_status: 'operationeel',
    });
    expect(payload).not.toHaveProperty('organizational_unit_id');
    expect(payload).not.toHaveProperty('custom_attributes');
  });
});
