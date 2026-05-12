'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { RectangleStackIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type {
  CustomFieldDefinition,
  CustomFieldDefinitionCreate,
  CustomFieldEntityType,
} from '@/lib/api-types';

const ENTITY_OPTIONS: { value: CustomFieldEntityType; label: string }[] = [
  { value: 'risk', label: 'Risico' },
  { value: 'control', label: 'Control' },
  { value: 'assessment', label: 'Assessment' },
  { value: 'finding', label: 'Bevinding' },
];

type FieldType = 'string' | 'number' | 'boolean' | 'enum';

const TYPE_OPTIONS: { value: FieldType; label: string }[] = [
  { value: 'string', label: 'Tekst' },
  { value: 'number', label: 'Getal' },
  { value: 'boolean', label: 'Ja/nee' },
  { value: 'enum', label: 'Keuzelijst' },
];

type FormState = {
  entity_type: CustomFieldEntityType;
  field_name: string;
  display_label: string;
  help_text: string;
  field_type: FieldType;
  enum_values: string;
  is_required: boolean;
};

const EMPTY_FORM: FormState = {
  entity_type: 'risk',
  field_name: '',
  display_label: '',
  help_text: '',
  field_type: 'string',
  enum_values: '',
  is_required: false,
};

function buildJsonSchema(state: FormState): Record<string, unknown> {
  switch (state.field_type) {
    case 'number':
      return { type: 'number' };
    case 'boolean':
      return { type: 'boolean' };
    case 'enum': {
      const values = state.enum_values
        .split(',')
        .map((v) => v.trim())
        .filter(Boolean);
      return { type: 'string', enum: values };
    }
    case 'string':
    default:
      return { type: 'string', maxLength: 500 };
  }
}

function describeSchema(schema: Record<string, unknown>): string {
  const type = schema.type as string;
  if (type === 'string' && Array.isArray(schema.enum)) {
    return `Keuzelijst (${(schema.enum as string[]).join(', ')})`;
  }
  switch (type) {
    case 'string':
      return 'Tekst';
    case 'number':
      return 'Getal';
    case 'boolean':
      return 'Ja/nee';
    default:
      return type ?? 'onbekend';
  }
}

export default function VeldenPage() {
  const [filterEntity, setFilterEntity] = useState<CustomFieldEntityType | ''>('');

  const { data, error, isLoading, mutate } = useSWR<CustomFieldDefinition[]>(
    ['custom-fields', filterEntity],
    () => api.customFields.list(filterEntity || undefined),
  );

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormState>(EMPTY_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function resetForm() {
    setFormData(EMPTY_FORM);
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.field_name || !formData.display_label) {
      setFormError('Veldnaam en label zijn verplicht.');
      return;
    }
    if (formData.field_type === 'enum' && !formData.enum_values.trim()) {
      setFormError('Voor een keuzelijst zijn de waarden verplicht (komma-gescheiden).');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const payload: CustomFieldDefinitionCreate = {
        entity_type: formData.entity_type,
        field_name: formData.field_name,
        display_label: formData.display_label,
        help_text: formData.help_text || null,
        json_schema: buildJsonSchema(formData),
        is_required: formData.is_required,
        display_order: 0,
      };
      await api.customFields.create(payload);
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      setFormError(`Aanmaken mislukt: ${detail}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Veld-definitie verwijderen? Waarden in bestaande rijen blijven staan.')) {
      return;
    }
    try {
      await api.customFields.delete(id);
      await mutate();
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      alert(`Verwijderen mislukt: ${detail}`);
    }
  }

  return (
    <PageWrapper
      title="Custom velden"
      description="Definieer extra velden per entiteit zodat je gemeente-specifieke gegevens (kadernota-programma, intern dossier-nummer, ...) kunt vastleggen zonder code-wijziging."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw veld
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
            <h3 className="text-base font-semibold text-neutral-900">
              Nieuw custom-veld
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Op entiteit *"
                options={ENTITY_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
                value={formData.entity_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    entity_type: e.target.value as CustomFieldEntityType,
                  })
                }
              />
              <Select
                label="Type *"
                options={TYPE_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
                value={formData.field_type}
                onChange={(e) =>
                  setFormData({ ...formData, field_type: e.target.value as FieldType })
                }
              />
              <Input
                label="Veldnaam (snake_case) *"
                value={formData.field_name}
                onChange={(e) => setFormData({ ...formData, field_name: e.target.value })}
                placeholder="bv. kadernota_programma"
              />
              <Input
                label="Label (zichtbaar) *"
                value={formData.display_label}
                onChange={(e) => setFormData({ ...formData, display_label: e.target.value })}
                placeholder="bv. Kadernota-programma"
              />
            </div>

            {formData.field_type === 'enum' && (
              <Input
                label="Keuze-waarden (komma-gescheiden) *"
                value={formData.enum_values}
                onChange={(e) => setFormData({ ...formData, enum_values: e.target.value })}
                placeholder="bv. Programma 1, Programma 2, Programma 3"
              />
            )}

            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                Toelichting (tooltip)
              </label>
              <textarea
                rows={2}
                className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                value={formData.help_text}
                onChange={(e) => setFormData({ ...formData, help_text: e.target.value })}
                placeholder="Wat moet de invuller hier opgeven?"
              />
            </div>

            <label className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.is_required}
                onChange={(e) =>
                  setFormData({ ...formData, is_required: e.target.checked })
                }
              />
              <span>Verplicht veld</span>
            </label>

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
            <p className="text-xs text-neutral-500">
              <strong>Let op:</strong> veldnamen mogen niet botsen met kernvelden
              (zoals <code>tenant_id</code>, <code>status</code>, <code>likelihood</code>).
              De server controleert dit en weigert het anders.
            </p>
          </form>
        </Card>
      )}

      <Card className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[200px]">
            <Select
              label="Filter op entiteit"
              options={[
                { value: '', label: 'Alle entiteiten' },
                ...ENTITY_OPTIONS,
              ]}
              value={filterEntity}
              onChange={(e) =>
                setFilterEntity(e.target.value as CustomFieldEntityType | '')
              }
            />
          </div>
        </div>
      </Card>

      {isLoading && <CardSkeleton />}

      {!isLoading && (!data || data.length === 0) && (
        <Card>
          <EmptyState
            icon={RectangleStackIcon}
            title="Nog geen custom velden"
            description="Definieer een eerste veld om gemeente-specifieke gegevens vast te leggen op risico's, controls of assessments."
          />
        </Card>
      )}

      {!isLoading && data && data.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Entiteit</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Label</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Veldnaam</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Type</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Verplicht</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {data.map((def) => (
                  <tr key={def.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3">
                      <Badge variant="primary">{def.entity_type}</Badge>
                    </td>
                    <td className="px-4 py-3 font-medium text-neutral-900">
                      {def.display_label}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      <code className="text-xs">{def.field_name}</code>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {describeSchema(def.json_schema)}
                    </td>
                    <td className="px-4 py-3">
                      {def.is_required ? (
                        <Badge className="bg-red-100 text-red-700">Verplicht</Badge>
                      ) : (
                        <span className="text-xs text-neutral-400">optioneel</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleDelete(def.id)}
                        className="text-xs text-red-600 hover:text-red-800"
                      >
                        Verwijderen
                      </button>
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
