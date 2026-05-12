'use client';

import useSWR from 'swr';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { api } from '@/lib/api-client';
import type {
  CustomFieldDefinition,
  CustomFieldEntityType,
} from '@/lib/api-types';

/**
 * Renderer voor dynamische custom-velden op basis van tenant-definities.
 *
 * Per entity_type laadt het de definities en rendert input-elementen
 * gebaseerd op het JSON-Schema-type. Resultaat is een dict met
 * `field_name → waarde` die direct als `custom_attributes` naar de API
 * gestuurd kan worden.
 */
export function CustomFieldsForm({
  entityType,
  value,
  onChange,
}: {
  entityType: CustomFieldEntityType;
  value: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
}) {
  const { data: definitions, isLoading } = useSWR<CustomFieldDefinition[]>(
    ['custom-fields-form', entityType],
    () => api.customFields.list(entityType),
  );

  if (isLoading) {
    return (
      <div className="text-xs text-neutral-500">Custom velden laden...</div>
    );
  }
  if (!definitions || definitions.length === 0) {
    return null;
  }

  function setField(name: string, val: unknown) {
    const next = { ...value };
    if (val === '' || val === null || val === undefined) {
      delete next[name];
    } else {
      next[name] = val;
    }
    onChange(next);
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-neutral-50/40 p-3">
      <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">
        Aanvullende velden (tenant-specifiek)
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {definitions.map((def) => (
          <FieldRenderer
            key={def.id}
            def={def}
            value={value[def.field_name]}
            onChange={(v) => setField(def.field_name, v)}
          />
        ))}
      </div>
    </div>
  );
}

function FieldRenderer({
  def,
  value,
  onChange,
}: {
  def: CustomFieldDefinition;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  const schema = def.json_schema as Record<string, unknown>;
  const type = schema.type as string;
  const labelSuffix = def.is_required ? ' *' : '';

  // Enum (string + enum-array)
  if (type === 'string' && Array.isArray(schema.enum)) {
    const opts = [
      { value: '', label: 'Selecteer...' },
      ...(schema.enum as string[]).map((v) => ({ value: v, label: v })),
    ];
    return (
      <div>
        <Select
          label={`${def.display_label}${labelSuffix}`}
          options={opts}
          value={(value as string) ?? ''}
          onChange={(e) => onChange(e.target.value || null)}
        />
        {def.help_text && (
          <p className="mt-1 text-xs text-neutral-500">{def.help_text}</p>
        )}
      </div>
    );
  }

  if (type === 'boolean') {
    return (
      <div>
        <label className="block text-sm font-medium text-neutral-800 mb-1.5">
          {def.display_label}
          {labelSuffix}
        </label>
        <label className="inline-flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span>Ja</span>
        </label>
        {def.help_text && (
          <p className="mt-1 text-xs text-neutral-500">{def.help_text}</p>
        )}
      </div>
    );
  }

  if (type === 'number') {
    return (
      <div>
        <Input
          type="number"
          label={`${def.display_label}${labelSuffix}`}
          value={value === undefined || value === null ? '' : String(value)}
          onChange={(e) => {
            const v = e.target.value;
            onChange(v === '' ? null : Number(v));
          }}
        />
        {def.help_text && (
          <p className="mt-1 text-xs text-neutral-500">{def.help_text}</p>
        )}
      </div>
    );
  }

  // String fallback
  return (
    <div>
      <Input
        type="text"
        label={`${def.display_label}${labelSuffix}`}
        value={(value as string) ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={def.help_text ?? undefined}
      />
      {def.help_text && (
        <p className="mt-1 text-xs text-neutral-500">{def.help_text}</p>
      )}
    </div>
  );
}
