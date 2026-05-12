'use client';

import { useState } from 'react';
import useSWR from 'swr';
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
import { OrgUnitSelect } from '@/components/shared/org-unit-select';
import { CustomFieldsForm } from '@/components/shared/custom-fields-form';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
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
  // RFC 0002 — filter-state stuurt SWR-key.
  const [filterUnitId, setFilterUnitId] = useState<string>('');
  const [includeDescendants, setIncludeDescendants] = useState<boolean>(false);

  const {
    data: controls,
    error,
    isLoading,
    mutate,
  } = useSWR<ControlResponse[]>(
    ['controls-list', filterUnitId, includeDescendants],
    () =>
      api.controls.list({
        organizationalUnitId: filterUnitId || undefined,
        includeDescendants: includeDescendants && !!filterUnitId,
      }),
  );

  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    domain: '',
    implementation_status: '',
    organizational_unit_id: '',
  });
  const [customAttributes, setCustomAttributes] = useState<Record<string, unknown>>({});

  function resetForm() {
    setFormData({
      title: '',
      description: '',
      domain: '',
      implementation_status: '',
      organizational_unit_id: '',
    });
    setCustomAttributes({});
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
      const payload: Record<string, unknown> = {
        title: formData.title,
        description: formData.description,
        domain: formData.domain,
        implementation_status: formData.implementation_status,
      };
      if (formData.organizational_unit_id) {
        payload.organizational_unit_id = formData.organizational_unit_id;
      }
      if (Object.keys(customAttributes).length > 0) {
        payload.custom_attributes = customAttributes;
      }
      await api.controls.create(payload);
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        const detail = formatApiError(err.body);
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
          Fout bij laden van controls: {(error as Error).message || 'Onbekende fout'}
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

            {/* RFC 0002 — Optionele koppeling aan organisatie-eenheid */}
            <div>
              <OrgUnitSelect
                value={formData.organizational_unit_id}
                onChange={(id) =>
                  setFormData({ ...formData, organizational_unit_id: id })
                }
              />
              <p className="mt-1 text-xs text-neutral-500">
                Optioneel — laat leeg om de control op tenant-niveau te houden.
              </p>
            </div>

            {/* RFC 0001 — Tenant-specifieke custom velden */}
            <CustomFieldsForm
              entityType="control"
              value={customAttributes}
              onChange={setCustomAttributes}
            />

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

      {/* RFC 0002 — Filter op organisatie-eenheid */}
      <Card className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[260px]">
            <OrgUnitSelect
              label="Filter op organisatie-eenheid"
              placeholder="Alle units (tenant-totaal)"
              value={filterUnitId}
              onChange={setFilterUnitId}
            />
          </div>
          {filterUnitId && (
            <label className="inline-flex items-center gap-2 text-sm text-neutral-700 mb-2">
              <input
                type="checkbox"
                checked={includeDescendants}
                onChange={(e) => setIncludeDescendants(e.target.checked)}
              />
              <span>Inclusief sub-units</span>
            </label>
          )}
          {filterUnitId && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setFilterUnitId('');
                setIncludeDescendants(false);
              }}
            >
              Filter wissen
            </Button>
          )}
        </div>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && (!controls || controls.length === 0) && (
        <Card>
          <EmptyState
            icon={ShieldCheckIcon}
            title={filterUnitId ? 'Geen controls in deze unit' : 'Nog geen controls'}
            description={
              filterUnitId
                ? 'Wissel filter of zet sub-units aan om bredere matches te zien.'
                : 'Voeg een control toe om te beginnen.'
            }
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
