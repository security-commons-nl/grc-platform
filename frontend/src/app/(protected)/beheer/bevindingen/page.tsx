'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { MagnifyingGlassCircleIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { useApi } from '@/lib/hooks/use-api';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type { FindingResponse, AssessmentResponse } from '@/lib/api-types';

const SEVERITY_OPTIONS = [
  { value: '', label: 'Selecteer ernst...' },
  { value: 'laag', label: 'Laag' },
  { value: 'midden', label: 'Midden' },
  { value: 'hoog', label: 'Hoog' },
  { value: 'kritiek', label: 'Kritiek' },
];

const STATUS_OPTIONS = [
  { value: 'open', label: 'Open' },
  { value: 'in_behandeling', label: 'In behandeling' },
  { value: 'afgesloten', label: 'Afgesloten' },
];

const SEVERITY_FILTER_OPTIONS = [
  { value: '', label: 'Alle ernstgraden' },
  ...SEVERITY_OPTIONS.slice(1),
];

const STATUS_FILTER_OPTIONS = [
  { value: '', label: 'Alle statussen' },
  ...STATUS_OPTIONS,
];

function severityBadge(severity: string) {
  switch (severity) {
    case 'kritiek':
      return <Badge variant="danger">Kritiek</Badge>;
    case 'hoog':
      return <Badge className="bg-orange-100 text-orange-800">Hoog</Badge>;
    case 'midden':
      return <Badge variant="warning">Midden</Badge>;
    case 'laag':
      return <Badge variant="success">Laag</Badge>;
    default:
      return <Badge variant="neutral">{severity}</Badge>;
  }
}

export default function BevindingenPage() {
  const { data: findings, error, isLoading, mutate } = useApi<FindingResponse[]>(
    '/assessments/findings/',
    '/assessments/findings/',
  );

  const { data: assessments } = useSWR<AssessmentResponse[]>(
    '/assessments/',
    () => api.assessments.list(),
  );

  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    assessment_id: '',
    title: '',
    description: '',
    severity: '',
    status: 'open',
  });

  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const assessmentOptions = [
    { value: '', label: 'Selecteer assessment...' },
    ...(assessments ?? []).map((a) => {
      const datum = a.planned_at
        ? new Date(a.planned_at).toLocaleDateString('nl-NL')
        : '';
      const label = `${a.assessment_type}${a.domain ? ` · ${a.domain}` : ''}${
        datum ? ` · ${datum}` : ''
      }`;
      return { value: a.id, label };
    }),
  ];

  function resetForm() {
    setFormData({
      assessment_id: '',
      title: '',
      description: '',
      severity: '',
      status: 'open',
    });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (
      !formData.assessment_id ||
      !formData.title ||
      !formData.severity ||
      !formData.status
    ) {
      setFormError('Vul alle verplichte velden in (inclusief assessment).');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      await api.findings.create({
        assessment_id: formData.assessment_id,
        title: formData.title,
        description: formData.description,
        severity: formData.severity,
        status: formData.status,
      });
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(`Fout bij aanmaken: ${formatApiError(err.body)}`);
      } else {
        setFormError(
          `Onbekende fout: ${err instanceof Error ? err.message : String(err)}`,
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const filtered =
    findings?.filter((f) => {
      if (severityFilter && f.severity !== severityFilter) return false;
      if (statusFilter && f.status !== statusFilter) return false;
      return true;
    }) || [];

  const noAssessments = (assessments ?? []).length === 0;

  return (
    <PageWrapper
      title="Bevindingen"
      description="Bevindingen uit assessments. Een bevinding hangt altijd aan een assessment en kan worden opgevolgd via corrective actions."
      actions={
        !showForm ? (
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowForm(true)}
            disabled={noAssessments}
            title={
              noAssessments
                ? 'Maak eerst een assessment aan onder /beheer/assessments'
                : undefined
            }
          >
            Nieuwe bevinding
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van bevindingen: {error.message || 'Onbekende fout'}
        </div>
      )}

      {noAssessments && !showForm && (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Er zijn nog geen assessments. Bevindingen hangen altijd aan een
          assessment — maak er eerst een aan onder <code>/beheer/assessments</code>.
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">
              Nieuwe bevinding
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Assessment *"
                options={assessmentOptions}
                value={formData.assessment_id}
                onChange={(e) =>
                  setFormData({ ...formData, assessment_id: e.target.value })
                }
              />
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="Korte omschrijving van de bevinding"
              />
              <Select
                label="Ernst *"
                options={SEVERITY_OPTIONS}
                value={formData.severity}
                onChange={(e) =>
                  setFormData({ ...formData, severity: e.target.value })
                }
              />
              <Select
                label="Status *"
                options={STATUS_OPTIONS}
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
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
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Wat is er geconstateerd? Wie/wat is geraakt?"
              />
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

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="w-48">
          <Select
            label="Ernst"
            options={SEVERITY_FILTER_OPTIONS}
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          />
        </div>
        <div className="w-48">
          <Select
            label="Status"
            options={STATUS_FILTER_OPTIONS}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          />
        </div>
      </div>

      {isLoading && <CardSkeleton />}

      {!isLoading && (!findings || findings.length === 0) && (
        <Card>
          <EmptyState
            icon={MagnifyingGlassCircleIcon}
            title="Nog geen bevindingen"
            description="Bevindingen worden vastgelegd vanuit een assessment."
          />
        </Card>
      )}

      {!isLoading && findings && findings.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">
                    Titel
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">
                    Ernst
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((finding: FindingResponse) => (
                  <tr
                    key={finding.id}
                    className="border-b border-neutral-100 hover:bg-neutral-50"
                  >
                    <td className="px-4 py-3 font-medium text-neutral-900">
                      {finding.title}
                    </td>
                    <td className="px-4 py-3">{severityBadge(finding.severity)}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={finding.status} />
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
