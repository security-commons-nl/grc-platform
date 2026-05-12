'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { BuildingOffice2Icon, ChevronRightIcon } from '@heroicons/react/24/outline';
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
  OrganizationalUnitResponse,
  OrganizationalUnitTreeNode,
  OrganizationalUnitCreate,
} from '@/lib/api-types';

const UNIT_TYPE_OPTIONS = [
  { value: '', label: 'Selecteer type...' },
  { value: 'directie', label: 'Directie' },
  { value: 'cluster', label: 'Cluster' },
  { value: 'afdeling', label: 'Afdeling' },
  { value: 'team', label: 'Team' },
  { value: 'overig', label: 'Overig' },
];

type FormState = {
  name: string;
  code: string;
  unit_type: string;
  parent_id: string;
  is_active: boolean;
};

const EMPTY_FORM: FormState = {
  name: '',
  code: '',
  unit_type: '',
  parent_id: '',
  is_active: true,
};

function TreeNode({
  node,
  depth,
  onSelect,
  selectedId,
}: {
  node: OrganizationalUnitTreeNode;
  depth: number;
  onSelect: (u: OrganizationalUnitResponse) => void;
  selectedId: string | null;
}) {
  const isSelected = node.id === selectedId;
  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(node)}
        className={`flex items-center w-full gap-2 px-2 py-1.5 rounded-md text-left text-sm transition-colors ${
          isSelected
            ? 'bg-primary-50 text-primary-800'
            : 'hover:bg-neutral-50 text-neutral-700'
        }`}
        style={{ paddingLeft: `${depth * 18 + 8}px` }}
      >
        {node.children.length > 0 ? (
          <ChevronRightIcon className="h-3.5 w-3.5 shrink-0 text-neutral-400" />
        ) : (
          <span className="w-3.5" />
        )}
        <span className="flex-1 truncate">{node.name}</span>
        {node.code && (
          <Badge className="bg-neutral-100 text-neutral-600">{node.code}</Badge>
        )}
        {!node.is_active && (
          <Badge className="bg-amber-100 text-amber-700">inactief</Badge>
        )}
      </button>
      {node.children.length > 0 && (
        <ul className="space-y-0.5">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              depth={depth + 1}
              onSelect={onSelect}
              selectedId={selectedId}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function OrganisatiePage() {
  const { data: tree, error, isLoading, mutate } = useSWR<OrganizationalUnitTreeNode[]>(
    'organizational-units-tree',
    () => api.organizationalUnits.tree(),
  );

  const { data: flat } = useSWR<OrganizationalUnitResponse[]>(
    'organizational-units-flat',
    () => api.organizationalUnits.list(),
  );

  const [selected, setSelected] = useState<OrganizationalUnitResponse | null>(null);
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
    if (!formData.name || !formData.unit_type) {
      setFormError('Naam en type zijn verplicht.');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const payload: OrganizationalUnitCreate = {
        name: formData.name,
        code: formData.code || null,
        unit_type: formData.unit_type,
        parent_id: formData.parent_id || null,
        is_active: formData.is_active,
      };
      await api.organizationalUnits.create(payload);
      await Promise.all([
        mutate(),
        // Refresh flat-list zodat parent-dropdown actueel blijft.
        // SWR keeps both keys; force second.
      ]);
      // Force revalidate flat-list met SWR's mutate via key.
      // (Eenvoudige aanpak: window.location.reload niet gewenst.)
      setShowForm(false);
      resetForm();
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      setFormError(`Aanmaken mislukt: ${detail}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete() {
    if (!selected) return;
    if (
      !confirm(
        `Verwijder organisatie-eenheid "${selected.name}"? Werkt alleen als er geen sub-units zijn.`,
      )
    ) {
      return;
    }
    try {
      await api.organizationalUnits.delete(selected.id);
      await mutate();
      setSelected(null);
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      alert(`Verwijderen mislukt: ${detail}`);
    }
  }

  const parentOptions = [
    { value: '', label: 'Geen parent (root-niveau)' },
    ...(flat ?? []).map((u) => ({ value: u.id, label: u.name })),
  ];

  return (
    <PageWrapper
      title="Organisatie"
      description="Beheer hiërarchische organisatie-eenheden (cluster, team, afdeling). Risico's, controls en assessments kunnen aan deze units gekoppeld worden voor aggregatie."
      actions={
        !showForm ? (
          <Button variant="primary" size="sm" onClick={() => setShowForm(true)}>
            Nieuwe eenheid
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
              Nieuwe organisatie-eenheid
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Input
                label="Naam *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="bv. Cluster Bedrijfsvoering"
              />
              <Input
                label="Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="bv. BV"
              />
              <Select
                label="Type *"
                options={UNIT_TYPE_OPTIONS}
                value={formData.unit_type}
                onChange={(e) => setFormData({ ...formData, unit_type: e.target.value })}
              />
              <Select
                label="Parent (optioneel)"
                options={parentOptions}
                value={formData.parent_id}
                onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
              />
            </div>
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
          </form>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          {isLoading && <CardSkeleton />}

          {!isLoading && (!tree || tree.length === 0) && (
            <Card>
              <EmptyState
                icon={BuildingOffice2Icon}
                title="Nog geen organisatie-eenheden"
                description="Maak een root-eenheid aan (bv. de directie of een hoofd-cluster) om de boom te beginnen."
              />
            </Card>
          )}

          {!isLoading && tree && tree.length > 0 && (
            <Card>
              <h3 className="text-sm font-semibold text-neutral-800 mb-2">
                Boomstructuur
              </h3>
              <ul className="space-y-0.5">
                {tree.map((node) => (
                  <TreeNode
                    key={node.id}
                    node={node}
                    depth={0}
                    onSelect={setSelected}
                    selectedId={selected?.id ?? null}
                  />
                ))}
              </ul>
            </Card>
          )}
        </div>

        <div className="lg:col-span-2">
          {!selected && (
            <Card>
              <p className="text-sm text-neutral-500">
                Klik op een eenheid in de boom voor details en acties.
              </p>
            </Card>
          )}

          {selected && (
            <Card>
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <div className="text-xs uppercase tracking-wide text-neutral-500">
                    {selected.unit_type}
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900">
                    {selected.name}
                  </h3>
                  {selected.code && (
                    <p className="mt-0.5 text-xs text-neutral-500">
                      Code: <code>{selected.code}</code>
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setSelected(null)}
                  className="text-xs text-neutral-500 hover:text-neutral-700"
                >
                  Sluiten
                </button>
              </div>

              <dl className="text-sm space-y-2">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-neutral-500">
                    Status
                  </dt>
                  <dd>
                    {selected.is_active ? (
                      <Badge variant="success">Actief</Badge>
                    ) : (
                      <Badge className="bg-amber-100 text-amber-700">Inactief</Badge>
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-neutral-500">
                    Parent
                  </dt>
                  <dd className="text-neutral-700">
                    {selected.parent_id
                      ? flat?.find((u) => u.id === selected.parent_id)?.name ??
                        '— (onbekend)'
                      : '— (root-niveau)'}
                  </dd>
                </div>
              </dl>

              <div className="mt-4 flex flex-wrap gap-2">
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleDelete}
                >
                  Verwijderen
                </Button>
              </div>

              <p className="mt-3 text-xs text-neutral-500">
                Edit-flow + verplaatsen-binnen-boom volgen in vervolg-PR. Voor nu:
                inactief markeren via DB of via dedicated update-endpoint.
              </p>
            </Card>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
