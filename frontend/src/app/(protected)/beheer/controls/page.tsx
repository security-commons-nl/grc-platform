'use client';

import { useState } from 'react';
import { ShieldCheckIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { useControls } from '@/lib/hooks/use-controls';
import { api, ApiError } from '@/lib/api-client';
import type { ControlResponse } from '@/lib/api-types';

const DOMAIN_OPTIONS = [
  { value: '', label: 'Selecteer domein...' },
  { value: 'ISMS', label: 'ISMS' },
  { value: 'PIMS', label: 'PIMS' },
  { value: 'BCMS', label: 'BCMS' },
];

const STATUS_OPTIONS = [
  { value: '', label: 'Selecteer status...' },
  { value: 'gepland', label: 'Gepland' },
  { value: 'in_uitvoering', label: 'In uitvoering' },
  { value: 'operationeel', label: 'Operationeel' },
  { value: 'niet_effectief', label: 'Niet effectief' },
];

export default function ControlsPage() {
  const { data: controls, error, isLoading, mutate } = useControls();
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    domain: '',
    implementation_status: '',
  });

  function resetForm() {
    setFormData({ title: '', description: '', domain: '', implementation_status: '' });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.title || !formData.domain || !formData.implementation_status) {
      setFormError('Vul alle verplichte velden in.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      await api.controls.create({
        title: formData.title,
        description: formData.description,
        domain: formData.domain,
        implementation_status: formData.implementation_status,
      });
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
      title="Controls"
      description="Overzicht van alle beheersmaatregelen."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuwe control
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van controls: {error.message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuwe control</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Naam van de control"
              />
              <Select
                label="Domein *"
                options={DOMAIN_OPTIONS}
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
              <Select
                label="Implementatiestatus *"
                options={STATUS_OPTIONS}
                value={formData.implementation_status}
                onChange={(e) => setFormData({ ...formData, implementation_status: e.target.value })}
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
                placeholder="Beschrijf de control..."
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

      {!isLoading && (!controls || controls.length === 0) && (
        <Card>
          <EmptyState
            icon={ShieldCheckIcon}
            title="Nog geen controls"
            description="Voeg een control toe om te beginnen."
          />
        </Card>
      )}

      {!isLoading && controls && controls.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Titel</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Domein</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {controls.map((control: ControlResponse) => (
                  <tr key={control.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{control.title}</td>
                    <td className="px-4 py-3">
                      <Badge variant="primary">{control.domain}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={control.implementation_status} />
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
