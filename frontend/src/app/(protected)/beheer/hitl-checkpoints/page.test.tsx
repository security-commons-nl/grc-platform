import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import type { ReactNode } from 'react';
import { SWRConfig } from 'swr';
import HitlCheckpointsPage from './page';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

function withFreshSwr(node: ReactNode) {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {node}
    </SWRConfig>
  );
}

function mockAuditLogs(logs: Array<{ agent_name: string; review_count?: number; last_decision?: string | null }>) {
  server.use(
    http.get(`${API}/ai-hitl-checkpoints/audit-logs`, () =>
      HttpResponse.json(
        logs.map((l, i) => ({
          id: `audit-${i}`,
          tenant_id: 't',
          user_id: null,
          agent_name: l.agent_name,
          model: 'gpt-4o',
          prompt_tokens: 100,
          completion_tokens: 50,
          feedback: null,
          review_count: l.review_count ?? 0,
          last_decision: l.last_decision ?? null,
          created_at: '2026-05-01T10:00:00Z',
        })),
      ),
    ),
  );
}

describe('HITL-review pagina + review-form', () => {
  it('toont empty-state als er geen audit-logs zijn', async () => {
    mockAuditLogs([]);
    render(withFreshSwr(<HitlCheckpointsPage />));
    expect(await screen.findByText('Geen AI-activiteit')).toBeInTheDocument();
  });

  it('toont audit-log-rij + review-tellingen', async () => {
    mockAuditLogs([
      { agent_name: 'gap-analyse', review_count: 2, last_decision: 'approved' },
    ]);
    render(withFreshSwr(<HitlCheckpointsPage />));

    expect(await screen.findByText('gap-analyse')).toBeInTheDocument();
    // last_decision-badge
    expect(screen.getByText('Goedgekeurd')).toBeInTheDocument();
  });

  it('bekijk-knop opent detailpaneel + laadt historie', async () => {
    mockAuditLogs([{ agent_name: 'risico-suggestie', review_count: 0 }]);
    server.use(
      http.get(`${API}/ai-hitl-checkpoints/`, () => HttpResponse.json([])),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<HitlCheckpointsPage />));

    await user.click(await screen.findByRole('button', { name: 'Bekijk' }));
    expect(await screen.findByText('Nieuwe review')).toBeInTheDocument();
    expect(screen.getByText(/Nog geen review-beslissing/)).toBeInTheDocument();
  });

  it('review submitten zonder motivatie toont validatiefout', async () => {
    mockAuditLogs([{ agent_name: 'control-suggestie' }]);
    server.use(
      http.get(`${API}/ai-hitl-checkpoints/`, () => HttpResponse.json([])),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<HitlCheckpointsPage />));

    await user.click(await screen.findByRole('button', { name: 'Bekijk' }));
    await screen.findByText('Nieuwe review');

    await user.click(screen.getByRole('button', { name: 'Review vastleggen' }));
    expect(
      await screen.findByText(/Motivatie is verplicht/),
    ).toBeInTheDocument();
  });

  it('review submitten met motivatie roept create-endpoint aan + voegt toe aan historie', async () => {
    mockAuditLogs([{ agent_name: 'eval-agent' }]);
    server.use(
      http.get(`${API}/ai-hitl-checkpoints/`, () => HttpResponse.json([])),
    );
    const createSpy = vi.fn();
    server.use(
      http.post(`${API}/ai-hitl-checkpoints/`, async ({ request }) => {
        createSpy(await request.json());
        return HttpResponse.json(
          {
            id: 'cp-1',
            tenant_id: 't',
            audit_log_id: 'audit-0',
            reviewer_user_id: 'u',
            decision: 'rejected',
            reason: 'Output bevatte foutieve PII-detectie.',
            created_at: '2026-05-12T10:00:00Z',
          },
          { status: 201 },
        );
      }),
    );

    const user = userEvent.setup();
    render(withFreshSwr(<HitlCheckpointsPage />));
    await user.click(await screen.findByRole('button', { name: 'Bekijk' }));
    await screen.findByText('Nieuwe review');

    await user.selectOptions(screen.getByLabelText('Beslissing'), 'rejected');
    await user.type(
      screen.getByPlaceholderText(/Waarom neemt u deze beslissing/),
      'Output bevatte foutieve PII-detectie.',
    );
    await user.click(screen.getByRole('button', { name: 'Review vastleggen' }));

    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    expect(createSpy.mock.calls[0][0]).toMatchObject({
      audit_log_id: 'audit-0',
      decision: 'rejected',
      reason: 'Output bevatte foutieve PII-detectie.',
    });

    // Historie toont nu 1 entry
    await waitFor(() =>
      expect(screen.getByText('Historie (1)')).toBeInTheDocument(),
    );
  });
});
