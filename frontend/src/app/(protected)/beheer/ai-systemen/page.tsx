'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { CpuChipIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type {
  AISystemResponse,
  AISystemCreate,
  AISystemType,
  EUAIActRisk,
  AISystemDeploymentStatus,
  AISystemClassifySuggestion,
} from '@/lib/api-types';

const SYSTEM_TYPE_OPTIONS: { value: AISystemType | ''; label: string }[] = [
  { value: '', label: 'Selecteer type...' },
  { value: 'chatbot', label: 'Chatbot / conversational' },
  { value: 'decision_support', label: 'Beslis-ondersteuning' },
  { value: 'content_generation', label: 'Content-generatie' },
  { value: 'classification', label: 'Classificatie' },
  { value: 'monitoring', label: 'Monitoring' },
  { value: 'automation', label: 'Automatisering' },
  { value: 'other', label: 'Anders' },
];

const RISK_OPTIONS: { value: EUAIActRisk | ''; label: string }[] = [
  { value: '', label: 'Alle risico-categorieën' },
  { value: 'unacceptable', label: 'Verboden (art. 5)' },
  { value: 'high', label: 'Hoog-risico (bijlage III)' },
  { value: 'limited', label: 'Beperkt (transparantie)' },
  { value: 'minimal', label: 'Minimaal' },
  { value: 'not_classified', label: 'Nog niet beoordeeld' },
];

const DEPLOYMENT_OPTIONS: { value: AISystemDeploymentStatus | ''; label: string }[] = [
  { value: '', label: 'Alle statussen' },
  { value: 'planned', label: 'Gepland' },
  { value: 'building', label: 'In opbouw' },
  { value: 'deployed', label: 'In productie' },
  { value: 'retired', label: 'Uit gebruik' },
];

const RISK_BADGE: Record<EUAIActRisk, { label: string; className: string }> = {
  unacceptable: { label: 'Verboden', className: 'bg-red-100 text-red-800' },
  high: { label: 'Hoog-risico', className: 'bg-orange-100 text-orange-800' },
  limited: { label: 'Beperkt', className: 'bg-amber-100 text-amber-800' },
  minimal: { label: 'Minimaal', className: 'bg-emerald-100 text-emerald-800' },
  not_classified: { label: 'Niet beoordeeld', className: 'bg-neutral-100 text-neutral-700' },
};

const DEPLOYMENT_BADGE: Record<AISystemDeploymentStatus, string> = {
  planned: 'Gepland',
  building: 'In opbouw',
  deployed: 'In productie',
  retired: 'Uit gebruik',
};

type FormState = {
  name: string;
  description: string;
  vendor: string;
  use_case: string;
  system_type: AISystemType | '';
  eu_ai_act_risk: EUAIActRisk;
  deployment_status: AISystemDeploymentStatus;
};

const EMPTY_FORM: FormState = {
  name: '',
  description: '',
  vendor: '',
  use_case: '',
  system_type: '',
  eu_ai_act_risk: 'not_classified',
  deployment_status: 'planned',
};

export default function AiSystemenPage() {
  const [filterRisk, setFilterRisk] = useState<EUAIActRisk | ''>('');
  const [filterStatus, setFilterStatus] = useState<AISystemDeploymentStatus | ''>('');

  const { data, error, isLoading, mutate } = useSWR<AISystemResponse[]>(
    ['ai-systems', filterRisk, filterStatus],
    () =>
      api.aiSystems.list({
        eu_ai_act_risk: filterRisk || undefined,
        deployment_status: filterStatus || undefined,
      }),
  );

  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormState>(EMPTY_FORM);

  const [advice, setAdvice] = useState<AISystemClassifySuggestion | null>(null);
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [adviceError, setAdviceError] = useState<string | null>(null);

  function resetForm() {
    setFormData(EMPTY_FORM);
    setAdvice(null);
    setAdviceError(null);
    setFormError(null);
  }

  async function handleClassify() {
    if (!formData.system_type) {
      setAdviceError('Kies eerst een systeem-type.');
      return;
    }
    setAdviceLoading(true);
    setAdviceError(null);
    try {
      const res = await api.aiSystems.classifySuggestion({
        system_type: formData.system_type,
        description: formData.description,
        use_case: formData.use_case,
      });
      setAdvice(res);
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      setAdviceError(`Advies mislukt: ${detail}`);
    } finally {
      setAdviceLoading(false);
    }
  }

  function applyAdvice() {
    if (!advice) return;
    setFormData((s) => ({ ...s, eu_ai_act_risk: advice.suggested_risk }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.name || !formData.system_type) {
      setFormError('Naam en systeem-type zijn verplicht.');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const payload: AISystemCreate = {
        name: formData.name,
        description: formData.description || null,
        vendor: formData.vendor || null,
        system_type: formData.system_type as AISystemType,
        eu_ai_act_risk: formData.eu_ai_act_risk,
        deployment_status: formData.deployment_status,
      };
      await api.aiSystems.create(payload);
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      setFormError(`Fout bij aanmaken: ${detail}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('AI-systeem verwijderen? Deze actie is niet ongedaan te maken.')) return;
    try {
      await api.aiSystems.delete(id);
      await mutate();
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      alert(`Verwijderen mislukt: ${detail}`);
    }
  }

  return (
    <PageWrapper
      title="AI-systemen"
      description="Register van AI-toepassingen met EU AI Act-risicoclassificatie. Operationaliseert M4 AI Governance."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw AI-systeem
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden: {(error as Error).message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw AI-systeem</h3>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Naam *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="bv. Klant-chatbot 'Lisa'"
              />
              <Input
                label="Leverancier"
                value={formData.vendor}
                onChange={(e) => setFormData({ ...formData, vendor: e.target.value })}
                placeholder="bv. Interne ontwikkeling, OpenAI, Mistral"
              />
              <Select
                label="Systeem-type *"
                options={SYSTEM_TYPE_OPTIONS}
                value={formData.system_type}
                onChange={(e) =>
                  setFormData({ ...formData, system_type: e.target.value as AISystemType | '' })
                }
              />
              <Select
                label="Levenscyclus-status"
                options={DEPLOYMENT_OPTIONS.filter((o) => o.value !== '')}
                value={formData.deployment_status}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    deployment_status: e.target.value as AISystemDeploymentStatus,
                  })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                Beschrijving
              </label>
              <textarea
                rows={3}
                className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Wat doet dit AI-systeem? Welke data verwerkt het?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                Use case
              </label>
              <textarea
                rows={2}
                className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                value={formData.use_case}
                onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
                placeholder="Voor wie en met welk doel? Beslist het AI-systeem zelfstandig of adviseert het alleen?"
              />
            </div>

            <div className="rounded-lg border border-blue-200 bg-blue-50/40 p-3">
              <div className="flex items-start gap-3">
                <SparklesIcon className="h-5 w-5 shrink-0 text-blue-700 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-semibold text-blue-900">
                    EU AI Act classificatie
                  </div>
                  <p className="text-xs text-blue-800 mt-0.5">
                    Het advies is een keyword-gebaseerde indicatie, geen besluit. Een menselijke
                    beoordelaar bepaalt de uiteindelijke categorie.
                  </p>

                  <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <Select
                      label="Gekozen risico-categorie"
                      options={RISK_OPTIONS.filter((o) => o.value !== '')}
                      value={formData.eu_ai_act_risk}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          eu_ai_act_risk: e.target.value as EUAIActRisk,
                        })
                      }
                    />
                    <div className="flex items-end">
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={handleClassify}
                        disabled={adviceLoading || !formData.system_type}
                      >
                        {adviceLoading ? 'Bezig...' : 'Classificatie-advies opvragen'}
                      </Button>
                    </div>
                  </div>

                  {adviceError && (
                    <p className="mt-2 text-sm text-red-700">{adviceError}</p>
                  )}

                  {advice && (
                    <div className="mt-3 rounded-md bg-white border border-blue-200 p-3 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-xs uppercase tracking-wide text-neutral-500">
                          Voorgesteld
                        </span>
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                            RISK_BADGE[advice.suggested_risk].className
                          }`}
                        >
                          {RISK_BADGE[advice.suggested_risk].label}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-neutral-700">{advice.reasoning}</p>
                      {advice.triggered_by.length > 0 && (
                        <p className="mt-1 text-xs text-neutral-500">
                          Op basis van: {advice.triggered_by.join(', ')}
                        </p>
                      )}
                      <div className="mt-3 flex items-center gap-2">
                        <Button
                          type="button"
                          variant="primary"
                          size="sm"
                          onClick={applyAdvice}
                          disabled={formData.eu_ai_act_risk === advice.suggested_risk}
                        >
                          Advies overnemen
                        </Button>
                        {formData.eu_ai_act_risk !== advice.suggested_risk && (
                          <span className="text-xs text-neutral-500">
                            U heeft een andere keuze gemaakt — leg de motivatie vast in de beschrijving.
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {formError && <p className="text-sm text-red-600">{formError}</p>}

            <div className="flex items-center gap-3">
              <Button type="submit" size="sm" disabled={isSubmitting}>
                {isSubmitting ? 'Bezig...' : 'Opslaan'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
              >
                Annuleren
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[200px]">
            <Select
              label="Filter op risico"
              options={RISK_OPTIONS}
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value as EUAIActRisk | '')}
            />
          </div>
          <div className="min-w-[200px]">
            <Select
              label="Filter op status"
              options={DEPLOYMENT_OPTIONS}
              value={filterStatus}
              onChange={(e) =>
                setFilterStatus(e.target.value as AISystemDeploymentStatus | '')
              }
            />
          </div>
          {(filterRisk || filterStatus) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setFilterRisk('');
                setFilterStatus('');
              }}
            >
              Filters wissen
            </Button>
          )}
        </div>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && (!data || data.length === 0) && (
        <Card>
          <EmptyState
            icon={CpuChipIcon}
            title="Nog geen AI-systemen"
            description="Registreer een AI-toepassing om EU AI Act-conformiteit te kunnen aantonen."
          />
        </Card>
      )}

      {!isLoading && data && data.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Naam</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Leverancier</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">
                    EU AI Act
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {data.map((sys) => {
                  const risk = RISK_BADGE[sys.eu_ai_act_risk];
                  return (
                    <tr key={sys.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                      <td className="px-4 py-3 font-medium text-neutral-900">{sys.name}</td>
                      <td className="px-4 py-3 text-neutral-600">
                        <Badge variant="primary">{sys.system_type}</Badge>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">{sys.vendor || '—'}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${risk.className}`}
                        >
                          {risk.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-neutral-600">
                        {DEPLOYMENT_BADGE[sys.deployment_status]}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleDelete(sys.id)}
                          className="text-xs text-red-600 hover:text-red-800"
                        >
                          Verwijderen
                        </button>
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
