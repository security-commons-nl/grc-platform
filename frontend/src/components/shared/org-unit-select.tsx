'use client';

import useSWR from 'swr';
import { Select } from '@/components/ui/select';
import { api } from '@/lib/api-client';
import type { OrganizationalUnitResponse } from '@/lib/api-types';

/**
 * Dropdown voor organisatie-eenheden binnen de huidige tenant.
 *
 * Werkt voor zowel formulieren (verplicht of optioneel kiezen) als filters.
 * Lege string-waarde = "geen unit gekozen" (NULL in DB = tenant-niveau).
 */
export function OrgUnitSelect({
  value,
  onChange,
  label = 'Organisatie-eenheid',
  placeholder = 'Tenant-niveau (geen unit)',
  disabled,
}: {
  value: string;
  onChange: (id: string) => void;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
}) {
  const { data } = useSWR<OrganizationalUnitResponse[]>(
    'org-units-select',
    () => api.organizationalUnits.list({ isActive: true }),
  );

  const options = [
    { value: '', label: placeholder },
    ...(data ?? []).map((u) => ({
      value: u.id,
      label: u.code ? `${u.name} (${u.code})` : u.name,
    })),
  ];

  return (
    <Select
      label={label}
      options={options}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    />
  );
}
