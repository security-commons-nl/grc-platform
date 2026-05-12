import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import { server } from '@/test/msw-server';

// useAuth() mocken zodat we de page kunnen renderen zonder echte AuthProvider.
vi.mock('@/providers/auth-provider', () => ({
  useAuth: () => ({
    user: {
      id: 'user-1',
      tenant_id: 'tenant-1',
      role: 'admin',
      domain: null,
      token_type: 'user',
      agent_name: null,
    },
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

// Async import na de mock zodat de module met gemockte hook gebundeld wordt
const { default: AgentTokensPage } = await import('./page');

const API = 'http://localhost:8000/api/v1';

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

describe('Agent-tokens admin pagina', () => {
  it('rendert form + default scope risks:read aangevinkt', async () => {
    server.use(http.get(`${API}/ai-systems/`, () => HttpResponse.json([])));
    render(withFreshSwr(<AgentTokensPage />));

    expect(await screen.findByLabelText('Naam van de agent *')).toBeInTheDocument();
    // Default scope
    const readScope = screen.getByLabelText(/Risico's lezen/) as HTMLInputElement;
    expect(readScope.checked).toBe(true);
  });

  it('validatie: geen naam → form-error en geen confirm-stap', async () => {
    server.use(http.get(`${API}/ai-systems/`, () => HttpResponse.json([])));
    const user = userEvent.setup();
    render(withFreshSwr(<AgentTokensPage />));

    await user.click(
      await screen.findByRole('button', { name: 'Token uitgeven...' }),
    );
    expect(
      await screen.findByText(/Vul naam en minstens één scope in/),
    ).toBeInTheDocument();
  });

  it('two-step confirm + uitgifte → toont JWT + scope-summary', async () => {
    server.use(http.get(`${API}/ai-systems/`, () => HttpResponse.json([])));

    const issueSpy = vi.fn();
    server.use(
      http.post(`${API}/auth/agent-token`, async ({ request }) => {
        issueSpy(await request.json());
        return HttpResponse.json({
          access_token: 'header.payload.signature',
          token_type: 'bearer',
          expires_in: 3600,
          scope: ['risks:read', 'controls:read'],
          ai_system_id: null,
        });
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<AgentTokensPage />));

    await user.type(
      await screen.findByLabelText('Naam van de agent *'),
      'incident-summarizer',
    );
    // Extra scope toevoegen
    await user.click(screen.getByLabelText(/Controls lezen/));

    // Stap 1
    await user.click(screen.getByRole('button', { name: 'Token uitgeven...' }));
    expect(
      await screen.findByText(/Weet u zeker dat u deze token wilt uitgeven/),
    ).toBeInTheDocument();

    // Stap 2
    await user.click(screen.getByRole('button', { name: 'Ja, uitgeven' }));

    await waitFor(() => expect(issueSpy).toHaveBeenCalled());
    expect(issueSpy.mock.calls[0][0]).toMatchObject({
      agent_name: 'incident-summarizer',
      scope: ['risks:read', 'controls:read'],
      tenant_id: 'tenant-1',
    });

    // Success-card toont JWT
    expect(
      await screen.findByRole('heading', { name: /Token uitgegeven — kopieer nu/ }),
    ).toBeInTheDocument();
    expect(screen.getByText('header.payload.signature')).toBeInTheDocument();
  });

  it('uitgifte zonder scope blokkeert vóór confirm-stap', async () => {
    server.use(http.get(`${API}/ai-systems/`, () => HttpResponse.json([])));
    const user = userEvent.setup();
    render(withFreshSwr(<AgentTokensPage />));

    await user.type(
      await screen.findByLabelText('Naam van de agent *'),
      'leeg-scope-agent',
    );
    // Default 'risks:read' uitvinken → 0 scopes
    await user.click(screen.getByLabelText(/Risico's lezen/));
    await user.click(screen.getByRole('button', { name: 'Token uitgeven...' }));

    expect(
      await screen.findByText(/Vul naam en minstens één scope in/),
    ).toBeInTheDocument();
  });
});
