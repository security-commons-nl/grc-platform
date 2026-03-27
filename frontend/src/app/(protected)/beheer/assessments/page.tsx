'use client';

import { useState } from 'react';
import { ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline';
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
import type { AssessmentResponse } from '@/lib/api-types';

const TYPE_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'audit', label: 'Audit' },
  { value: 'dpia', label: 'DPIA' },
  { value: 'pentest', label: 'Pentest' },
  { value: 'self_assessment', label: 'Self-assessment' },
  { value: 'bc_oefening', label: 'BC-oefening' },
  { value: 'gap_analysis', label: 'Gap-analyse' },
  { value: 'management_review', label: 'Management review' },
];

const DOMAIN_OPTIONS = [
  { value: '', label: 'Selecteer domein...' },
  { value: 'ISMS', label: 'ISMS' },
  { value: 'PIMS', label: 'PIMS' },
  { value: 'BCMS', label: 'BCMS' },
];

export default function AssessmentsPage() {
  const { data: assessments, error, isLoading, mutate } = useApi<AssessmentResponse[]>(
    '/assessments/',
    '/assessments/',
  );
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    assessment_type: '',
    domain: '',
    planned_at: '',
  });

  function resetForm() {
    setFormData({ assessment_type: '', domain: '', planned_at: '' });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.assessment_type || !formData.domain) {
      setFormError('Vul alle verplichte velden in.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const payload: Record<string, unknown> = {
        assessment_type: formData.assessment_type,
        domain: formData.domain,
        status: 'gepland',
      };
      if (formData.planned_at) {
        payload.planned_at = formData.planned_at;
      }
      await api.assessments.create(payload);
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        const detail = (err.body as Record<string, unknown>)?.detail || JSON.stringify(err.body);
        setFormError(`Fout bij aanmaken: ${detail}`);
      } else {
        setFormError(`Onbekende fout: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageWrapper
      title="Assessments"
      description="Overzicht van alle assessments, audits en beoordelingen."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw assessment
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van assessments: {error.message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw assessment</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Type *"
                options={TYPE_OPTIONS}
                value={formData.assessment_type}
                onChange={(e) => setFormData({ ...formData, assessment_type: e.target.value })}
              />
              <Select
                label="Domein *"
                options={DOMAIN_OPTIONS}
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
              <Input
                label="Gepland op"
                type="date"
                value={formData.planned_at}
                onChange={(e) => setFormData({ ...formData, planned_at: e.target.value })}
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
                onClick={() => { setShowForm(false); resetForm(); }}
              >
                Annuleren
              </Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading && <CardSkeleton />}

      {!isLoading && (!assessments || assessments.length === 0) && (
        <Card>
          <EmptyState
            icon={ClipboardDocumentCheckIcon}
            title="Nog geen assessments"
            description="Plan een assessment om te beginnen met verificatie."
          />
        </Card>
      )}

      {!isLoading && assessments && assessments.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Domein</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Gepland op</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {assessments.map((assessment: AssessmentResponse) => (
                  <tr key={assessment.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{assessment.assessment_type}</td>
                    <td className="px-4 py-3">
                      <Badge variant="primary">{assessment.domain}</Badge>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {assessment.planned_at
                        ? new Date(assessment.planned_at).toLocaleDateString('nl-NL')
                        : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={assessment.status} />
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
