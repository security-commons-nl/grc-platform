import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import BevindingenPage from './page';
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
    http.get(`${API}/assessments/findings/`, () => HttpResponse.json([])),
    http.get(`${API}/assessments/`, () => HttpResponse.json([])),
  );
}

function mockWithAssessment() {
  server.use(
    http.get(`${API}/assessments/findings/`, () => HttpResponse.json([])),
    http.get(`${API}/assessments/`, () =>
      HttpResponse.json([
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
          organizational_unit_id: null,
          custom_attributes: {},
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        },
      ]),
    ),
  );
}

describe('Bevindingen pagina', () => {
  it('toont empty-state + waarschuwing als er geen assessments zijn', async () => {
    mockEmpty();
    render(withFreshSwr(<BevindingenPage />));
    expect(await screen.findByText('Nog geen bevindingen')).toBeInTheDocument();
    expect(
      await screen.findByText(/Er zijn nog geen assessments/),
    ).toBeInTheDocument();
    // Knop bestaat maar is disabled
    const btn = screen.getByRole('button', { name: 'Nieuwe bevinding' });
    expect(btn).toBeDisabled();
  });

  it('opent form en valideert verplichte velden', async () => {
    mockWithAssessment();
    const user = userEvent.setup();
    render(withFreshSwr(<BevindingenPage />));

    await user.click(
      await screen.findByRole('button', { name: 'Nieuwe bevinding' }),
    );
    await screen.findByRole('heading', { name: 'Nieuwe bevinding' });

    // Submit zonder assessment/ernst → foutmelding
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));
    expect(
      await screen.findByText(/Vul alle verplichte velden in/),
    ).toBeInTheDocument();
  });

  it('submit met alle velden roept create + ververst lijst', async () => {
    mockWithAssessment();
    const createSpy = vi.fn();
    server.use(
      http.post(`${API}/assessments/findings/`, async ({ request }) => {
        createSpy(await request.json());
        return HttpResponse.json(
          {
            id: 'f-1',
            tenant_id: 't',
            assessment_id: 'a-1',
            title: 'Lek in toegangsbeheer',
            description: '',
            severity: 'hoog',
            status: 'open',
            requirement_id: null,
            custom_attributes: {},
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<BevindingenPage />));

    await user.click(
      await screen.findByRole('button', { name: 'Nieuwe bevinding' }),
    );
    await user.selectOptions(screen.getByLabelText('Assessment *'), 'a-1');
    await user.type(
      screen.getByLabelText('Titel *'),
      'Lek in toegangsbeheer',
    );
    await user.selectOptions(screen.getByLabelText('Ernst *'), 'hoog');
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));

    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    expect(createSpy.mock.calls[0][0]).toMatchObject({
      assessment_id: 'a-1',
      title: 'Lek in toegangsbeheer',
      severity: 'hoog',
      status: 'open',
    });
  });

  it('filtert op ernst', async () => {
    server.use(
      http.get(`${API}/assessments/findings/`, () =>
        HttpResponse.json([
          {
            id: 'f-1',
            tenant_id: 't',
            assessment_id: 'a-1',
            title: 'Hoog-ernst-bevinding',
            description: '',
            severity: 'hoog',
            status: 'open',
            requirement_id: null,
            custom_attributes: {},
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          {
            id: 'f-2',
            tenant_id: 't',
            assessment_id: 'a-1',
            title: 'Laag-ernst-bevinding',
            description: '',
            severity: 'laag',
            status: 'open',
            requirement_id: null,
            custom_attributes: {},
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
        ]),
      ),
      http.get(`${API}/assessments/`, () => HttpResponse.json([])),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<BevindingenPage />));

    // Beide rijen zichtbaar
    await waitFor(() =>
      expect(screen.getByText('Hoog-ernst-bevinding')).toBeInTheDocument(),
    );
    expect(screen.getByText('Laag-ernst-bevinding')).toBeInTheDocument();

    // Filter op ernst=hoog → laag verdwijnt
    await user.selectOptions(screen.getByLabelText('Ernst'), 'hoog');
    expect(screen.getByText('Hoog-ernst-bevinding')).toBeInTheDocument();
    expect(screen.queryByText('Laag-ernst-bevinding')).not.toBeInTheDocument();
  });
});
