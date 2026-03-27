'use client';

import { useState } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
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
import type { IncidentResponse } from '@/lib/api-types';

const TYPE_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'datalek', label: 'Datalek' },
  { value: 'beveiligingsincident', label: 'Beveiligingsincident' },
  { value: 'beschikbaarheid', label: 'Beschikbaarheid' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'overig', label: 'Overig' },
];

const SEVERITY_OPTIONS = [
  { value: '', label: 'Selecteer ernst...' },
  { value: 'laag', label: 'Laag' },
  { value: 'midden', label: 'Midden' },
  { value: 'hoog', label: 'Hoog' },
  { value: 'kritiek', label: 'Kritiek' },
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

export default function IncidentenPage() {
  const { data: incidents, error, isLoading, mutate } = useApi<IncidentResponse[]>(
    '/incidents/',
    '/incidents/',
  );
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    incident_type: '',
    severity: '',
  });

  function resetForm() {
    setFormData({ title: '', incident_type: '', severity: '' });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.title || !formData.incident_type || !formData.severity) {
      setFormError('Vul alle verplichte velden in.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      await api.incidents.create({
        title: formData.title,
        incident_type: formData.incident_type,
        severity: formData.severity,
        status: 'open',
        reported_at: new Date().toISOString(),
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
      title="Incidenten"
      description="Overzicht van alle gemelde incidenten."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw incident
          </Button>
        ) : undefined
      }
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van incidenten: {error.message || 'Onbekende fout'}
        </div>
      )}

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw incident</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Korte beschrijving van het incident"
              />
              <Select
                label="Type *"
                options={TYPE_OPTIONS}
                value={formData.incident_type}
                onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
              />
              <Select
                label="Ernst *"
                options={SEVERITY_OPTIONS}
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
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

      {!isLoading && (!incidents || incidents.length === 0) && (
        <Card>
          <EmptyState
            icon={ExclamationTriangleIcon}
            title="Nog geen incidenten"
            description="Meld een incident om te beginnen met incidentmanagement."
          />
        </Card>
      )}

      {!isLoading && incidents && incidents.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Titel</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Ernst</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Gemeld op</th>
                </tr>
              </thead>
              <tbody>
                {incidents.map((incident: IncidentResponse) => (
                  <tr key={incident.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{incident.title}</td>
                    <td className="px-4 py-3 text-neutral-600">{incident.incident_type}</td>
                    <td className="px-4 py-3">
                      {severityBadge(incident.severity)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={incident.status} />
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {incident.reported_at
                        ? new Date(incident.reported_at).toLocaleDateString('nl-NL')
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
