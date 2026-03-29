'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { ShieldExclamationIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { useRisks } from '@/lib/hooks/use-risks';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type { RiskResponse, ScopeResponse } from '@/lib/api-types';

const DOMAIN_OPTIONS = [
  { value: '', label: 'Selecteer domein...' },
  { value: 'ISMS', label: 'ISMS' },
  { value: 'PIMS', label: 'PIMS' },
  { value: 'BCMS', label: 'BCMS' },
];

const LIKELIHOOD_OPTIONS = [
  { value: '', label: 'Selecteer...' },
  { value: '1', label: '1 - Zeer laag' },
  { value: '2', label: '2 - Laag' },
  { value: '3', label: '3 - Midden' },
  { value: '4', label: '4 - Hoog' },
  { value: '5', label: '5 - Zeer hoog' },
];

const IMPACT_OPTIONS = [
  { value: '', label: 'Selecteer...' },
  { value: '1', label: '1 - Zeer laag' },
  { value: '2', label: '2 - Laag' },
  { value: '3', label: '3 - Midden' },
  { value: '4', label: '4 - Hoog' },
  { value: '5', label: '5 - Zeer hoog' },
];

function getRiskLevelBadge(score: number) {
  if (score <= 4) return <Badge variant="success">Groen</Badge>;
  if (score <= 9) return <Badge variant="warning">Geel</Badge>;
  if (score <= 14) return <Badge className="bg-orange-100 text-orange-800">Oranje</Badge>;
  return <Badge variant="danger">Rood</Badge>;
}

export default function RisicosPage() {
  const { data: risks, error, isLoading, mutate } = useRisks();
  const { data: scopes } = useSWR<ScopeResponse[]>('/scopes/', () => api.scopes.list());
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    scope_id: '',
    domain: '',
    title: '',
    description: '',
    likelihood: '',
    impact: '',
  });

  const scopeOptions = [
    { value: '', label: 'Selecteer scope...' },
    ...(scopes || []).map((s) => ({ value: s.id, label: s.name })),
  ];

  function resetForm() {
    setFormData({ scope_id: '', domain: '', title: '', description: '', likelihood: '', impact: '' });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.scope_id || !formData.domain || !formData.title || !formData.likelihood || !formData.impact) {
      setFormError('Vul alle verplichte velden in (inclusief scope).');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      await api.risks.create({
        scope_id: formData.scope_id,
        domain: formData.domain,
        title: formData.title,
        description: formData.description,
        likelihood: Number(formData.likelihood),
        impact: Number(formData.impact),
        status: 'open',
      });
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(`Fout bij aanmaken: ${formatApiError(err.body)}`);
      } else {
        setFormError(`Onbekende fout: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageWrapper
      title="Risico's"
      description="Overzicht van alle geidentificeerde risico's."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw risico
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van risico's: {error.message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw risico</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Scope *"
                options={scopeOptions}
                value={formData.scope_id}
                onChange={(e) => setFormData({ ...formData, scope_id: e.target.value })}
              />
              <Select
                label="Domein *"
                options={DOMAIN_OPTIONS}
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Risicotitel"
              />
              <Select
                label="Kans *"
                options={LIKELIHOOD_OPTIONS}
                value={formData.likelihood}
                onChange={(e) => setFormData({ ...formData, likelihood: e.target.value })}
              />
              <Select
                label="Impact *"
                options={IMPACT_OPTIONS}
                value={formData.impact}
                onChange={(e) => setFormData({ ...formData, impact: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                Beschrijving
              </label>
              <textarea
                className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Beschrijf het risico..."
              />
            </div>
            {formData.likelihood && formData.impact && (
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <span>Berekende score: {Number(formData.likelihood) * Number(formData.impact)}</span>
                {getRiskLevelBadge(Number(formData.likelihood) * Number(formData.impact))}
              </div>
            )}
            {formError && (
              <p className="text-sm text-red-600">{formError}</p>
            )}
            <div className="flex items-center gap-3">
              <Button type="submit" size="sm" disabled={isSubmitting}>
                {isSubmitting ? 'Bezig...' : 'Opslaan'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => { setShowForm(false); resetForm(); }}
              >
                Annuleren
              </Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading && <CardSkeleton />}

      {!isLoading && (!risks || risks.length === 0) && (
        <Card>
          <EmptyState
            icon={ShieldExclamationIcon}
            title="Nog geen risico's"
            description="Voeg een risico toe om te beginnen met risicomanagement."
          />
        </Card>
      )}

      {!isLoading && risks && risks.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Titel</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Domein</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Kans x Impact = Score</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Niveau</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk: RiskResponse) => (
                  <tr key={risk.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{risk.title}</td>
                    <td className="px-4 py-3">
                      <Badge variant="primary">{risk.domain}</Badge>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {risk.likelihood} x {risk.impact} = {risk.risk_score}
                    </td>
                    <td className="px-4 py-3">
                      {getRiskLevelBadge(risk.risk_score)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={risk.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </PageWrapper>
  );
}
