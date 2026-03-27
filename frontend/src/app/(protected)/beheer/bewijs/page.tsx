'use client';

import { useState } from 'react';
import { DocumentMagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { useApi } from '@/lib/hooks/use-api';
import { api, ApiError } from '@/lib/api-client';
import type { EvidenceResponse } from '@/lib/api-types';

const EVIDENCE_TYPE_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'document', label: 'Document' },
  { value: 'screenshot', label: 'Screenshot' },
  { value: 'log', label: 'Log' },
  { value: 'rapport', label: 'Rapport' },
  { value: 'verklaring', label: 'Verklaring' },
];

export default function BewijsPage() {
  const { data: evidence, error, isLoading, mutate } = useApi<EvidenceResponse[]>(
    '/evidence/',
    '/evidence/',
  );
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    evidence_type: '',
    collected_at: '',
    valid_until: '',
  });

  function resetForm() {
    setFormData({ title: '', evidence_type: '', collected_at: '', valid_until: '' });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.title || !formData.evidence_type || !formData.collected_at) {
      setFormError('Vul alle verplichte velden in.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const payload: Record<string, unknown> = {
        title: formData.title,
        evidence_type: formData.evidence_type,
        collected_at: formData.collected_at,
      };
      if (formData.valid_until) {
        payload.valid_until = formData.valid_until;
      }
      await api.evidence.create(payload);
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
      title="Bewijs"
      description="Overzicht van alle verzamelde bewijsstukken."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw bewijs
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van bewijs: {error.message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw bewijs</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Bewijstitel"
              />
              <Select
                label="Type *"
                options={EVIDENCE_TYPE_OPTIONS}
                value={formData.evidence_type}
                onChange={(e) => setFormData({ ...formData, evidence_type: e.target.value })}
              />
              <Input
                label="Verzameld op *"
                type="date"
                value={formData.collected_at}
                onChange={(e) => setFormData({ ...formData, collected_at: e.target.value })}
              />
              <Input
                label="Geldig tot"
                type="date"
                value={formData.valid_until}
                onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
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

      {!isLoading && (!evidence || evidence.length === 0) && (
        <Card>
          <EmptyState
            icon={DocumentMagnifyingGlassIcon}
            title="Nog geen bewijs"
            description="Voeg bewijsstukken toe om controls te onderbouwen."
          />
        </Card>
      )}

      {!isLoading && evidence && evidence.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Titel</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Verzameld op</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Geldig tot</th>
                </tr>
              </thead>
              <tbody>
                {evidence.map((item: EvidenceResponse) => (
                  <tr key={item.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{item.title}</td>
                    <td className="px-4 py-3 text-neutral-600">{item.evidence_type}</td>
                    <td className="px-4 py-3 text-neutral-600">
                      {item.collected_at
                        ? new Date(item.collected_at).toLocaleDateString('nl-NL')
                        : '-'}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {item.valid_until
                        ? new Date(item.valid_until).toLocaleDateString('nl-NL')
                        : '-'}
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
