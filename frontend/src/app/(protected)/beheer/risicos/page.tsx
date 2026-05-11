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
import { RiskMatrix } from '@/components/beheer/risk-matrix';
import { SimulationResults } from '@/components/beheer/simulation-results';
import { useRisks } from '@/lib/hooks/use-risks';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type { RiskResponse, RiskSimulationResponse, ScopeResponse } from '@/lib/api-types';

const DISTRIBUTION_OPTIONS = [
  { value: '', label: 'Geen (alleen point estimate)' },
  { value: 'uniform', label: 'Uniform (min/max)' },
  { value: 'triangular', label: 'Triangular (min / meest waarschijnlijk / max)' },
];

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
    // M5 — kwantitatieve impact (optioneel)
    financial_impact_eur: '',
    financial_impact_min_eur: '',
    financial_impact_max_eur: '',
    impact_distribution: '',
  });
  const [showQuantitative, setShowQuantitative] = useState(false);

  // M5 — simulatie state
  const [simulationResult, setSimulationResult] = useState<RiskSimulationResponse | null>(null);
  const [simulationRiskTitle, setSimulationRiskTitle] = useState<string>('');
  const [simulatingRiskId, setSimulatingRiskId] = useState<string | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const scopeOptions = [
    { value: '', label: 'Selecteer scope...' },
    ...(scopes || []).map((s) => ({ value: s.id, label: s.name })),
  ];

  function resetForm() {
    setFormData({
      scope_id: '', domain: '', title: '', description: '', likelihood: '', impact: '',
      financial_impact_eur: '', financial_impact_min_eur: '', financial_impact_max_eur: '',
      impact_distribution: '',
    });
    setShowQuantitative(false);
    setFormError(null);
  }

  async function handleSimulate(risk: RiskResponse) {
    setSimulatingRiskId(risk.id);
    setSimulationError(null);
    try {
      const result = await api.risks.simulate(risk.id, { iterations: 10000 });
      setSimulationResult(result);
      setSimulationRiskTitle(risk.title);
      // Scroll naar resultaat
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err instanceof ApiError) {
        setSimulationError(`Simulatie mislukt: ${formatApiError(err.body)}`);
      } else {
        setSimulationError(`Onbekende fout: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setSimulatingRiskId(null);
    }
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
      const payload: Record<string, unknown> = {
        scope_id: formData.scope_id,
        domain: formData.domain,
        title: formData.title,
        description: formData.description,
        likelihood: Number(formData.likelihood),
        impact: Number(formData.impact),
        status: 'open',
      };
      // M5 — optionele kwantitatieve velden alleen meesturen als ingevuld
      if (formData.financial_impact_eur) {
        payload.financial_impact_eur = Number(formData.financial_impact_eur);
      }
      if (formData.financial_impact_min_eur) {
        payload.financial_impact_min_eur = Number(formData.financial_impact_min_eur);
      }
      if (formData.financial_impact_max_eur) {
        payload.financial_impact_max_eur = Number(formData.financial_impact_max_eur);
      }
      if (formData.impact_distribution) {
        payload.impact_distribution = formData.impact_distribution;
      }
      await api.risks.create(payload);
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

      {simulationError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {simulationError}
        </div>
      )}

      {simulationResult && (
        <SimulationResults
          result={simulationResult}
          riskTitle={simulationRiskTitle}
          onDismiss={() => setSimulationResult(null)}
        />
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
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-2">
                Kans × Impact *
              </label>
              <RiskMatrix
                mode="select"
                value={{
                  likelihood: formData.likelihood ? Number(formData.likelihood) : '',
                  impact: formData.impact ? Number(formData.impact) : '',
                }}
                onChange={(l, i) => setFormData({ ...formData, likelihood: String(l), impact: String(i) })}
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

            {/* M5 — Kwantitatieve impact (optioneel, collapsible) */}
            <div className="border-t border-neutral-200 pt-3">
              <button
                type="button"
                className="text-sm font-medium text-primary-700 hover:text-primary-800"
                onClick={() => setShowQuantitative(!showQuantitative)}
              >
                {showQuantitative ? '−' : '+'} Kwantitatieve impact (optioneel)
              </button>
              {showQuantitative && (
                <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <Select
                    label="Distributie"
                    options={DISTRIBUTION_OPTIONS}
                    value={formData.impact_distribution}
                    onChange={(e) => setFormData({ ...formData, impact_distribution: e.target.value })}
                  />
                  <Input
                    type="number"
                    label="Meest waarschijnlijk (€) — mode bij triangular"
                    value={formData.financial_impact_eur}
                    onChange={(e) => setFormData({ ...formData, financial_impact_eur: e.target.value })}
                    placeholder="bv. 25000"
                  />
                  <Input
                    type="number"
                    label="Minimum schade (€)"
                    value={formData.financial_impact_min_eur}
                    onChange={(e) => setFormData({ ...formData, financial_impact_min_eur: e.target.value })}
                    placeholder="bv. 10000"
                  />
                  <Input
                    type="number"
                    label="Maximum schade (€)"
                    value={formData.financial_impact_max_eur}
                    onChange={(e) => setFormData({ ...formData, financial_impact_max_eur: e.target.value })}
                    placeholder="bv. 100000"
                  />
                  <p className="sm:col-span-2 text-xs text-neutral-500">
                    Met een distributie kun je Monte Carlo-simulatie uitvoeren via de "Simuleer"-knop in de tabel.
                    Triangular vereist alle drie de bedragen; uniform alleen min en max.
                  </p>
                </div>
              )}
            </div>
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
        <Card className="mb-4">
          <h3 className="text-sm font-semibold text-neutral-700 mb-3">Risicokaart</h3>
          <RiskMatrix mode="view" risks={risks} />
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
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Kwantitatief</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk: RiskResponse) => {
                  const hasDistribution =
                    risk.impact_distribution === 'uniform' ||
                    risk.impact_distribution === 'triangular';
                  return (
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
                    <td className="px-4 py-3">
                      {hasDistribution ? (
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={simulatingRiskId === risk.id}
                          onClick={() => handleSimulate(risk)}
                        >
                          {simulatingRiskId === risk.id ? 'Simuleren...' : 'Simuleer'}
                        </Button>
                      ) : (
                        <span className="text-xs text-neutral-400">geen distributie</span>
                      )}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </PageWrapper>
  );
}
