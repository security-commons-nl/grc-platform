import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import AssessmentsPage from './page';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

function mockEmpty() {
  server.use(
    http.get(`${API}/assessments/`, () => HttpResponse.json([])),
    http.get(`${API}/organizational-units/`, () => HttpResponse.json([])),
    http.get(`${API}/custom-fields/`, () => HttpResponse.json([])),
  );
}

describe('Assessments pagina (RFC 0001 + 0002)', () => {
  it('empty-state zonder assessments', async () => {
    mockEmpty();
    render(withFreshSwr(<AssessmentsPage />));
    expect(await screen.findByText('Nog geen assessments')).toBeInTheDocument();
  });

  it('form-validatie: zonder planned_at toont fout', async () => {
    mockEmpty();
    const user = userEvent.setup();
    render(withFreshSwr(<AssessmentsPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw assessment' }));
    await user.selectOptions(screen.getByLabelText('Type *'), 'audit');
    await user.selectOptions(screen.getByLabelText('Domein *'), 'ISMS');
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));

    expect(
      await screen.findByText(/Vul alle verplichte velden in/),
    ).toBeInTheDocument();
  });

  it('submit met org-unit roept create met organizational_unit_id', async () => {
    server.use(
      http.get(`${API}/assessments/`, () => HttpResponse.json([])),
      http.get(`${API}/organizational-units/`, () =>
        HttpResponse.json([
          {
            id: 'unit-1',
            tenant_id: 't',
            parent_id: null,
            name: 'Cluster Centraal',
            code: null,
            unit_type: 'cluster',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]),
      ),
      http.get(`${API}/custom-fields/`, () => HttpResponse.json([])),
    );

    const createSpy = vi.fn();
    server.use(
      http.post(`${API}/assessments/`, async ({ request }) => {
        createSpy(await request.json());
        return HttpResponse.json(
          {
            id: 'a-1',
            tenant_id: 't',
            assessment_type: 'audit',
            scope_id: null,
            domain: 'ISMS',
            planned_at: '2026-07-01',
            started_at: null,
            completed_at: null,
            status: 'gepland',
            cyclus_id: null,
            document_id: null,
            ai_system_id: null,
            organizational_unit_id: 'unit-1',
            custom_attributes: {},
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<AssessmentsPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw assessment' }));
    await user.selectOptions(screen.getByLabelText('Type *'), 'audit');
    await user.selectOptions(screen.getByLabelText('Domein *'), 'ISMS');
    await user.type(screen.getByLabelText('Gepland op'), '2026-07-01');

    // Org-unit-dropdown: wacht tot de optie geladen is, dan selecteren.
    const orgSelects = await screen.findAllByLabelText('Organisatie-eenheid');
    // De eerste hoort bij het form (filter-versie heeft custom label)
    await user.selectOptions(orgSelects[0], 'unit-1');

    await user.click(screen.getByRole('button', { name: 'Opslaan' }));
    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    expect(createSpy.mock.calls[0][0]).toMatchObject({
      assessment_type: 'audit',
      domain: 'ISMS',
      planned_at: '2026-07-01',
      organizational_unit_id: 'unit-1',
    });
  });
});
