'use client';

import { useState, useMemo } from 'react';
import { ClipboardDocumentListIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { DecisionLogTable } from '@/components/inrichten/decision-log-table';
import { useApi } from '@/lib/hooks/use-api';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type { DecisionResponse } from '@/lib/api-types';

const DECISION_TYPE_OPTIONS = [
  { value: '', label: 'Alle types' },
  { value: 'mandaat', label: 'Mandaat' },
  { value: 'scope', label: 'Scope' },
  { value: 'governance', label: 'Governance' },
  { value: 'beleid', label: 'Beleid' },
  { value: 'normenkader', label: 'Normenkader' },
  { value: 'risico', label: 'Risico' },
];

const DECISION_TYPE_FORM_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'mandaat', label: 'Mandaat' },
  { value: 'scope', label: 'Scope' },
  { value: 'governance', label: 'Governance' },
  { value: 'beleid', label: 'Beleid' },
  { value: 'normenkader', label: 'Normenkader' },
  { value: 'risico', label: 'Risico' },
];

const GREMIUM_OPTIONS = [
  { value: '', label: 'Alle gremia' },
  { value: 'Strategisch', label: 'Strategisch' },
  { value: 'Tactisch', label: 'Tactisch' },
  { value: 'Lijnmanagement', label: 'Lijnmanagement' },
];

const GREMIUM_FORM_OPTIONS = [
  { value: '', label: 'Selecteer gremium...' },
  { value: 'Strategisch', label: 'Strategisch' },
  { value: 'Tactisch', label: 'Tactisch' },
  { value: 'Lijnmanagement', label: 'Lijnmanagement' },
];

export default function BesluitenPage() {
  const { data: decisions, error, isLoading, mutate } = useApi<DecisionResponse[]>(
    '/decisions/',
    '/decisions/',
  );

  const [typeFilter, setTypeFilter] = useState('');
  const [gremiumFilter, setGremiumFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    decision_type: '',
    content: '',
    grondslag: '',
    gremium: '',
    decided_by_name: '',
    decided_by_role: '',
    number: '',
  });

  const filtered = useMemo(() => {
    if (!decisions) return [];
    return decisions.filter((d) => {
      if (typeFilter && d.decision_type !== typeFilter) return false;
      if (gremiumFilter && d.gremium !== gremiumFilter) return false;
      return true;
    });
  }, [decisions, typeFilter, gremiumFilter]);

  function resetForm() {
    setFormData({
      decision_type: '',
      content: '',
      grondslag: '',
      gremium: '',
      decided_by_name: '',
      decided_by_role: '',
      number: '',
    });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.decision_type || !formData.content || !formData.gremium || !formData.decided_by_name || !formData.decided_by_role) {
      setFormError('Vul alle verplichte velden in (inclusief rol).');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      // Auto-generate number if empty
      const number = formData.number || `B-${String((decisions?.length || 0) + 1).padStart(3, '0')}`;

      await api.decisions.create({
        ...formData,
        number,
        decided_at: new Date().toISOString(),
      });
      await mutate();
      setShowForm(false);
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(`Fout bij aanmaken: ${formatApiError(err.body)}`);
      } else {
        setFormError(`Onbekende fout: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageWrapper
      title="Besluitlog"
      description="Alle vastgelegde besluiten. Besluiten zijn onwijzigbaar — alleen superseding is mogelijk."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw besluit
          </Button>
        ) : undefined
      }
    >
      {/* Error state */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van besluiten: {error.message || 'Onbekende fout'}
        </div>
      )}

      {/* New decision form */}
      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw besluit</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Type *"
                options={DECISION_TYPE_FORM_OPTIONS}
                value={formData.decision_type}
                onChange={(e) => setFormData({ ...formData, decision_type: e.target.value })}
              />
              <Select
                label="Gremium *"
                options={GREMIUM_FORM_OPTIONS}
                value={formData.gremium}
                onChange={(e) => setFormData({ ...formData, gremium: e.target.value })}
              />
              <Input
                label="Nummer"
                value={formData.number}
                onChange={(e) => setFormData({ ...formData, number: e.target.value })}
                placeholder="Bijv. B-2026-001"
              />
              <Input
                label="Grondslag"
                value={formData.grondslag}
                onChange={(e) => setFormData({ ...formData, grondslag: e.target.value })}
                placeholder="Bijv. ISO 27001 A.5.1"
              />
              <Input
                label="Besluitnemer naam *"
                value={formData.decided_by_name}
                onChange={(e) => setFormData({ ...formData, decided_by_name: e.target.value })}
              />
              <Input
                label="Besluitnemer rol"
                value={formData.decided_by_role}
                onChange={(e) => setFormData({ ...formData, decided_by_role: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1.5">
                Inhoud *
              </label>
              <textarea
                className="block w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                rows={3}
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                placeholder="Beschrijf het besluit..."
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
            label="Type"
            options={DECISION_TYPE_OPTIONS}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          />
        </div>
        <div className="w-48">
          <Select
            label="Gremium"
            options={GREMIUM_OPTIONS}
            value={gremiumFilter}
            onChange={(e) => setGremiumFilter(e.target.value)}
          />
        </div>
      </div>

      {/* Content */}
      {isLoading && <CardSkeleton />}

      {!isLoading && (!decisions || decisions.length === 0) && (
        <Card>
          <EmptyState
            icon={ClipboardDocumentListIcon}
            title="Nog geen besluiten"
            description="Besluiten worden automatisch vastgelegd wanneer stappen worden afgerond."
          />
        </Card>
      )}

      {!isLoading && decisions && decisions.length > 0 && (
        <Card>
          <DecisionLogTable decisions={filtered} />
        </Card>
      )}
    </PageWrapper>
  );
}
