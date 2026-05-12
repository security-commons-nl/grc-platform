import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import AiSystemenPage from './page';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

// Layout-componenten (sidebar/header) hangen aan AuthProvider — die zit hier
// niet in de testboom. We renderen alleen de page-content.

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

function mockEmptyList() {
  server.use(http.get(`${API}/ai-systems/`, () => HttpResponse.json([])));
}

describe('AI-systemen pagina + form', () => {
  it('toont empty-state-boodschap zonder systemen', async () => {
    mockEmptyList();
    render(withFreshSwr(<AiSystemenPage />));
    expect(await screen.findByText('Nog geen AI-systemen')).toBeInTheDocument();
  });

  it('form-validatie: lege naam blokkeert submit', async () => {
    mockEmptyList();
    const user = userEvent.setup();
    render(withFreshSwr(<AiSystemenPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw AI-systeem' }));
    // Form opent
    await screen.findByRole('heading', { name: 'Nieuw AI-systeem' });

    // Submit zonder naam → foutmelding
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));
    expect(
      await screen.findByText('Naam en systeem-type zijn verplicht.'),
    ).toBeInTheDocument();
  });

  it('classifier-advies opvragen vereist systeem-type', async () => {
    mockEmptyList();
    const user = userEvent.setup();
    render(withFreshSwr(<AiSystemenPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw AI-systeem' }));
    await screen.findByRole('heading', { name: 'Nieuw AI-systeem' });

    // De knop is initieel disabled omdat systeem-type leeg is
    const adviceBtn = screen.getByRole('button', {
      name: 'Classificatie-advies opvragen',
    });
    expect(adviceBtn).toBeDisabled();
  });

  it('classifier-advies → toont voorstel + reasoning + triggered_by; advies-overnemen vult dropdown', async () => {
    mockEmptyList();
    // Mock classifier
    server.use(
      http.post(`${API}/ai-systems/classify-suggestion`, () =>
        HttpResponse.json({
          suggested_risk: 'high',
          reasoning: 'Beslis-flow met menselijke check — hoog-risico.',
          triggered_by: ['decision_support', 'beslist'],
        }),
      ),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<AiSystemenPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw AI-systeem' }));
    await screen.findByRole('heading', { name: 'Nieuw AI-systeem' });

    // Vul minimaal de velden zodat advies opgevraagd kan worden
    await user.type(screen.getByLabelText('Naam *'), 'Beslis-AI');
    await user.selectOptions(screen.getByLabelText('Systeem-type *'), 'decision_support');

    await user.click(screen.getByRole('button', { name: 'Classificatie-advies opvragen' }));

    // Advies komt binnen
    expect(await screen.findByText('Voorgesteld')).toBeInTheDocument();
    expect(
      screen.getByText('Beslis-flow met menselijke check — hoog-risico.'),
    ).toBeInTheDocument();

    // Advies overnemen vult de dropdown met 'high'
    await user.click(screen.getByRole('button', { name: 'Advies overnemen' }));
    expect(
      (screen.getByLabelText('Gekozen risico-categorie') as HTMLSelectElement).value,
    ).toBe('high');
    expect(
      screen.getByRole('button', { name: 'Advies overnemen' }),
    ).toBeDisabled();
  });

  it('submit met geldige velden roept create-API aan', async () => {
    mockEmptyList();
    const createSpy = vi.fn();
    server.use(
      http.post(`${API}/ai-systems/`, async ({ request }) => {
        createSpy(await request.json());
        return HttpResponse.json(
          {
            id: 'new-1',
            tenant_id: 't',
            name: 'Spell-check',
            description: null,
            vendor: null,
            system_type: 'other',
            eu_ai_act_risk: 'not_classified',
            deployment_status: 'planned',
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<AiSystemenPage />));

    await user.click(await screen.findByRole('button', { name: 'Nieuw AI-systeem' }));
    await user.type(screen.getByLabelText('Naam *'), 'Spell-check');
    await user.selectOptions(screen.getByLabelText('Systeem-type *'), 'other');
    await user.click(screen.getByRole('button', { name: 'Opslaan' }));

    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    expect(createSpy.mock.calls[0][0]).toMatchObject({
      name: 'Spell-check',
      system_type: 'other',
      eu_ai_act_risk: 'not_classified',
    });
  });
});
