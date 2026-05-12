'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { EyeIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type {
  AIAuditLogWithReview,
  HITLCheckpointResponse,
  HITLDecision,
} from '@/lib/api-types';

const DECISION_OPTIONS: { value: HITLDecision; label: string }[] = [
  { value: 'approved', label: 'Goedgekeurd' },
  { value: 'rejected', label: 'Afgewezen' },
  { value: 'modified', label: 'Aangepast' },
  { value: 'pending', label: 'In behandeling' },
];

const DECISION_BADGE: Record<HITLDecision, { label: string; className: string }> = {
  approved: { label: 'Goedgekeurd', className: 'bg-emerald-100 text-emerald-800' },
  rejected: { label: 'Afgewezen', className: 'bg-red-100 text-red-800' },
  modified: { label: 'Aangepast', className: 'bg-amber-100 text-amber-800' },
  pending: { label: 'In behandeling', className: 'bg-neutral-100 text-neutral-700' },
};

const FILTER_OPTIONS = [
  { value: 'all', label: 'Alle activiteit' },
  { value: 'unreviewed', label: 'Alleen niet-gereviewd' },
];

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleString('nl-NL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return ts;
  }
}

export default function HitlCheckpointsPage() {
  const [filter, setFilter] = useState<'all' | 'unreviewed'>('all');

  const {
    data: auditLogs,
    error,
    isLoading,
    mutate,
  } = useSWR<AIAuditLogWithReview[]>(
    ['hitl-audit-logs', filter],
    () => api.hitl.listAuditLogs({ onlyUnreviewed: filter === 'unreviewed' }),
  );

  const [selectedLog, setSelectedLog] = useState<AIAuditLogWithReview | null>(null);
  const [history, setHistory] = useState<HITLCheckpointResponse[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [decision, setDecision] = useState<HITLDecision>('approved');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function openLog(log: AIAuditLogWithReview) {
    setSelectedLog(log);
    setHistory([]);
    setFormError(null);
    setReason('');
    setDecision('approved');
    setHistoryLoading(true);
    try {
      const items = await api.hitl.listCheckpoints(log.id);
      setHistory(items);
    } catch (err) {
      setFormError(
        err instanceof ApiError
          ? `Historie laden mislukt: ${formatApiError(err.body)}`
          : `Onbekende fout: ${err instanceof Error ? err.message : String(err)}`,
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  async function submitReview() {
    if (!selectedLog) return;
    if (!reason.trim()) {
      setFormError('Motivatie is verplicht — leg vast waarom u deze beslissing neemt.');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const created = await api.hitl.createCheckpoint({
        audit_log_id: selectedLog.id,
        decision,
        reason: reason.trim(),
      });
      setHistory((h) => [created, ...h]);
      setReason('');
      // Update audit-logs lijst (review_count + last_decision)
      await mutate();
      // Refresh geselecteerde log met nieuwe telling
      setSelectedLog({
        ...selectedLog,
        review_count: selectedLog.review_count + 1,
        last_decision: decision,
      });
    } catch (err) {
      setFormError(
        err instanceof ApiError
          ? `Review opslaan mislukt: ${formatApiError(err.body)}`
          : `Onbekende fout: ${err instanceof Error ? err.message : String(err)}`,
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageWrapper
      title="HITL-review"
      description="Menselijk toezicht op AI-agent-activiteit (EU AI Act art. 14). Bekijk wat agents hebben gedaan en leg uw oordeel vast."
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden: {(error as Error).message || 'Onbekende fout'}
        </div>
      )}

      <Card className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[240px]">
            <Select
              label="Toon"
              options={FILTER_OPTIONS}
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'unreviewed')}
            />
          </div>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          {isLoading && <CardSkeleton />}

          {!isLoading && (!auditLogs || auditLogs.length === 0) && (
            <Card>
              <EmptyState
                icon={EyeIcon}
                title={filter === 'unreviewed' ? 'Niets om te reviewen' : 'Geen AI-activiteit'}
                description={
                  filter === 'unreviewed'
                    ? 'Alle agent-activiteit heeft al een HITL-review gekregen.'
                    : 'Nog geen audit-logs van AI-agents in deze tenant.'
                }
              />
            </Card>
          )}

          {!isLoading && auditLogs && auditLogs.length > 0 && (
            <Card padding="none">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 bg-neutral-50">
                      <th className="px-4 py-3 text-left font-medium text-neutral-600">Agent</th>
                      <th className="px-4 py-3 text-left font-medium text-neutral-600">Model</th>
                      <th className="px-4 py-3 text-left font-medium text-neutral-600">Tijd</th>
                      <th className="px-4 py-3 text-left font-medium text-neutral-600">Reviews</th>
                      <th className="px-4 py-3 text-left font-medium text-neutral-600">Laatste oordeel</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => {
                      const isSelected = selectedLog?.id === log.id;
                      return (
                        <tr
                          key={log.id}
                          className={`border-b border-neutral-100 hover:bg-neutral-50 ${
                            isSelected ? 'bg-primary-50/40' : ''
                          }`}
                        >
                          <td className="px-4 py-3 font-medium text-neutral-900">
                            {log.agent_name}
                          </td>
                          <td className="px-4 py-3 text-neutral-600">
                            <code className="text-xs">{log.model}</code>
                          </td>
                          <td className="px-4 py-3 text-neutral-600 whitespace-nowrap">
                            {formatTimestamp(log.created_at)}
                          </td>
                          <td className="px-4 py-3">
                            {log.review_count === 0 ? (
                              <Badge className="bg-neutral-100 text-neutral-700">0</Badge>
                            ) : (
                              <Badge variant="primary">{log.review_count}</Badge>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            {log.last_decision ? (
                              <span
                                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                  DECISION_BADGE[log.last_decision].className
                                }`}
                              >
                                {DECISION_BADGE[log.last_decision].label}
                              </span>
                            ) : (
                              <span className="text-xs text-neutral-400">niet beoordeeld</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Button
                              variant={isSelected ? 'primary' : 'secondary'}
                              size="sm"
                              onClick={() => openLog(log)}
                            >
                              {isSelected ? 'Geopend' : 'Bekijk'}
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>

        <div className="lg:col-span-2">
          {!selectedLog && (
            <Card>
              <p className="text-sm text-neutral-500">
                Klik op een rij om de details en review-historie te zien, of zelf een
                review vast te leggen.
              </p>
            </Card>
          )}

          {selectedLog && (
            <Card>
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <div className="text-xs uppercase tracking-wide text-neutral-500">
                    Agent-activiteit
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">
                    {selectedLog.agent_name}
                  </h3>
                  <p className="mt-0.5 text-xs text-neutral-500">
                    {formatTimestamp(selectedLog.created_at)} &middot;{' '}
                    <code>{selectedLog.model}</code>
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    Prompt {selectedLog.prompt_tokens.toLocaleString('nl-NL')} tokens &middot;
                    completion {selectedLog.completion_tokens.toLocaleString('nl-NL')} tokens
                  </p>
                </div>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-xs text-neutral-500 hover:text-neutral-700"
                >
                  Sluiten
                </button>
              </div>

              <div className="mb-4 rounded-lg border border-neutral-200 p-3">
                <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">
                  Nieuwe review
                </div>
                <Select
                  label="Beslissing"
                  options={DECISION_OPTIONS}
                  value={decision}
                  onChange={(e) => setDecision(e.target.value as HITLDecision)}
                />
                <div className="mt-3">
                  <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                    Motivatie *
                  </label>
                  <textarea
                    rows={3}
                    className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Waarom neemt u deze beslissing? Wat heeft de agent juist of fout gedaan?"
                  />
                </div>
                {formError && <p className="mt-2 text-sm text-red-600">{formError}</p>}
                <div className="mt-3">
                  <Button size="sm" onClick={submitReview} disabled={isSubmitting}>
                    {isSubmitting ? 'Bezig...' : 'Review vastleggen'}
                  </Button>
                </div>
              </div>

              <div>
                <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">
                  Historie ({history.length})
                </div>
                {historyLoading && <CardSkeleton />}
                {!historyLoading && history.length === 0 && (
                  <p className="text-sm text-neutral-500">Nog geen review-beslissing vastgelegd.</p>
                )}
                {!historyLoading && history.length > 0 && (
                  <ul className="space-y-2">
                    {history.map((cp) => (
                      <li
                        key={cp.id}
                        className="rounded-md border border-neutral-200 bg-neutral-50 p-2.5 text-sm"
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                              DECISION_BADGE[cp.decision].className
                            }`}
                          >
                            {DECISION_BADGE[cp.decision].label}
                          </span>
                          <span className="text-xs text-neutral-500">
                            {formatTimestamp(cp.created_at)}
                          </span>
                        </div>
                        {cp.reason && (
                          <p className="mt-1 text-sm text-neutral-700">{cp.reason}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
