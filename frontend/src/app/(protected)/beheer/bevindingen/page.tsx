'use client';

import { useState } from 'react';
import { MagnifyingGlassCircleIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { StatusBadge } from '@/components/shared/status-badge';
import { useApi } from '@/lib/hooks/use-api';
import type { FindingResponse } from '@/lib/api-types';

const SEVERITY_FILTER_OPTIONS = [
  { value: '', label: 'Alle ernstgraden' },
  { value: 'laag', label: 'Laag' },
  { value: 'midden', label: 'Midden' },
  { value: 'hoog', label: 'Hoog' },
  { value: 'kritiek', label: 'Kritiek' },
];

const STATUS_FILTER_OPTIONS = [
  { value: '', label: 'Alle statussen' },
  { value: 'open', label: 'Open' },
  { value: 'in_behandeling', label: 'In behandeling' },
  { value: 'afgesloten', label: 'Afgesloten' },
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
  const { data: findings, error, isLoading } = useApi<FindingResponse[]>(
    '/findings/',
    '/findings/',
  );

  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const filtered = findings?.filter((f) => {
    if (severityFilter && f.severity !== severityFilter) return false;
    if (statusFilter && f.status !== statusFilter) return false;
    return true;
  }) || [];

  return (
    <PageWrapper
      title="Bevindingen"
      description="Overzicht van alle bevindingen uit assessments. Bevindingen worden aangemaakt via assessments."
    >
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van bevindingen: {error.message || 'Onbekende fout'}
        </div>
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
            description="Bevindingen worden aangemaakt via assessments."
          />
        </Card>
      )}

      {!isLoading && findings && findings.length > 0 && (
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Titel</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Ernst</th>
                  <th className="px-4 py-3 text-left font-medium text-neutral-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((finding: FindingResponse) => (
                  <tr key={finding.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium text-neutral-900">{finding.title}</td>
                    <td className="px-4 py-3">
                      {severityBadge(finding.severity)}
                    </td>
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
