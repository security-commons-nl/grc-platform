'use client';

import { useState, useMemo } from 'react';
import { DocumentTextIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { DocumentVersionList } from '@/components/inrichten/document-version-list';
import { useApi } from '@/lib/hooks/use-api';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import { formatApiError } from '@/lib/format-error';
import type { DocumentResponse } from '@/lib/api-types';

const DOC_TYPE_OPTIONS = [
  { value: '', label: 'Alle types' },
  { value: 'beleid', label: 'Beleid' },
  { value: 'governance', label: 'Governance' },
  { value: 'register', label: 'Register' },
  { value: 'rapport', label: 'Rapport' },
  { value: 'procedure', label: 'Procedure' },
];

const DOC_TYPE_FORM_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'beleid', label: 'Beleid' },
  { value: 'governance', label: 'Governance' },
  { value: 'register', label: 'Register' },
  { value: 'rapport', label: 'Rapport' },
  { value: 'procedure', label: 'Procedure' },
];

const DOMAIN_OPTIONS = [
  { value: '', label: 'Alle domeinen' },
  { value: 'ISMS', label: 'ISMS' },
  { value: 'PIMS', label: 'PIMS' },
  { value: 'BCMS', label: 'BCMS' },
];

const DOMAIN_FORM_OPTIONS = [
  { value: '', label: 'Geen domein' },
  { value: 'ISMS', label: 'ISMS' },
  { value: 'PIMS', label: 'PIMS' },
  { value: 'BCMS', label: 'BCMS' },
];

const VISIBILITY_OPTIONS = [
  { value: 'intern', label: 'Intern' },
  { value: 'vertrouwelijk', label: 'Vertrouwelijk' },
  { value: 'openbaar', label: 'Openbaar' },
];

export default function DocumentenPage() {
  const { data: documents, error, isLoading, mutate } = useApi<DocumentResponse[]>(
    '/documents/',
    '/documents/',
  );

  const [typeFilter, setTypeFilter] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    document_type: '',
    title: '',
    domain: '',
    visibility: 'intern',
  });

  const filtered = useMemo(() => {
    if (!documents) return [];
    return documents.filter((d) => {
      if (typeFilter && d.document_type !== typeFilter) return false;
      if (domainFilter && d.domain !== domainFilter) return false;
      return true;
    });
  }, [documents, typeFilter, domainFilter]);

  function resetForm() {
    setFormData({
      document_type: '',
      title: '',
      domain: '',
      visibility: 'intern',
    });
    setFormError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.document_type || !formData.title) {
      setFormError('Vul alle verplichte velden in.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const payload: Record<string, unknown> = {
        document_type: formData.document_type,
        title: formData.title,
        visibility: formData.visibility,
      };
      if (formData.domain) {
        payload.domain = formData.domain;
      }
      await api.documents.create(payload);
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
      title="Documenten"
      description="Alle IMS-documenten met versiegeschiedenis."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuw document
          </Button>
        ) : undefined
      }
    >
      {/* Error state */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Fout bij laden van documenten: {error.message || 'Onbekende fout'}
        </div>
      )}

      {/* New document form */}
      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-base font-semibold text-neutral-900">Nieuw document</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Select
                label="Type *"
                options={DOC_TYPE_FORM_OPTIONS}
                value={formData.document_type}
                onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
              />
              <Input
                label="Titel *"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Documenttitel"
              />
              <Select
                label="Domein"
                options={DOMAIN_FORM_OPTIONS}
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
              <Select
                label="Zichtbaarheid"
                options={VISIBILITY_OPTIONS}
                value={formData.visibility}
                onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
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
            options={DOC_TYPE_OPTIONS}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          />
        </div>
        <div className="w-48">
          <Select
            label="Domein"
            options={DOMAIN_OPTIONS}
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
          />
        </div>
      </div>

      {/* Content */}
      {isLoading && <CardSkeleton />}

      {!isLoading && (!documents || documents.length === 0) && (
        <Card>
          <EmptyState
            icon={DocumentTextIcon}
            title="Nog geen documenten"
            description="Documenten worden aangemaakt wanneer stappen worden uitgevoerd."
          />
        </Card>
      )}

      {!isLoading && documents && documents.length > 0 && (
        <DocumentVersionList documents={filtered} />
      )}
    </PageWrapper>
  );
}
