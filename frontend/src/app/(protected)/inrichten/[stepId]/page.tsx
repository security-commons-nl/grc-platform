'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { StatusBadge } from '@/components/shared/status-badge';
import { WaaromTooltip } from '@/components/shared/waarom-tooltip';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { api, ApiError } from '@/lib/api-client';
import { STEP_CONFIGS } from '@/lib/step-config';
import type { StepResponse, StepExecutionResponse, StepDependencyResponse } from '@/lib/api-types';

const NEXT_STATUS_OPTIONS: Record<string, { value: string; label: string }[]> = {
  niet_gestart: [{ value: 'in_uitvoering', label: 'Start deze stap' }],
  in_uitvoering: [{ value: 'concept', label: 'Markeer als concept' }],
  concept: [{ value: 'in_review', label: 'Indienen voor review' }],
  in_review: [
    { value: 'vastgesteld', label: 'Goedkeuren' },
    { value: 'concept', label: 'Terugsturen naar concept' },
  ],
  vastgesteld: [],
};

export default function StepDetailPage({
  params,
}: {
  params: Promise<{ stepId: string }>;
}) {
  const { stepId } = use(params);
  const router = useRouter();
  const [isUpdating, setIsUpdating] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('');
  const [error, setError] = useState<string | null>(null);

  const { data: step, isLoading: stepLoading } = useSWR<StepResponse>(
    `/steps/${stepId}`,
    () => api.steps.get(stepId),
  );

  const { data: allExecutions, isLoading: execLoading, mutate: mutateExecutions } = useSWR<StepExecutionResponse[]>(
    '/steps/executions/',
    () => api.steps.listExecutions(),
  );

  const { data: dependencies } = useSWR<StepDependencyResponse[]>(
    '/steps/dependencies/',
    () => api.steps.listDependencies(),
  );

  const execution = allExecutions?.find((e) => e.step_id === stepId);
  const currentStatus = execution?.status || 'niet_gestart';
  const isCompleted = currentStatus === 'vastgesteld';

  const stepConfig = step
    ? STEP_CONFIGS[step.number] || null
    : null;

  // Check if dependencies are met
  const stepDeps = dependencies?.filter((d) => d.step_id === stepId) || [];
  const depsBlocked = stepDeps.some((dep) => {
    const depExec = allExecutions?.find((e) => e.step_id === dep.depends_on_step_id);
    return !depExec || depExec.status !== 'vastgesteld';
  });

  const statusOptions = NEXT_STATUS_OPTIONS[currentStatus] || [];

  async function handleStatusUpdate() {
    if (!selectedStatus) return;
    setIsUpdating(true);
    setError(null);

    try {
      if (!execution) {
        // Create execution with default status, then transition to desired status
        const created = await api.steps.createExecution({
          step_id: stepId,
          status: 'niet_gestart',
        });
        if (selectedStatus !== 'niet_gestart') {
          await api.steps.updateExecution(created.id, { status: selectedStatus });
        }
      } else {
        await api.steps.updateExecution(execution.id, { status: selectedStatus });
      }
      // Revalidate
      await mutateExecutions();
      setSelectedStatus('');
    } catch (err) {
      if (err instanceof ApiError) {
        const detail = (err.body as Record<string, unknown>)?.detail || JSON.stringify(err.body);
        setError(`Fout bij statuswijziging: ${detail}`);
      } else {
        setError(`Onbekende fout: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setIsUpdating(false);
    }
  }

  if (stepLoading || execLoading) {
    return (
      <PageWrapper title="Stap laden...">
        <CardSkeleton />
      </PageWrapper>
    );
  }

  if (!step) {
    return (
      <PageWrapper title="Stap niet gevonden">
        <Card>
          <p className="text-sm text-neutral-600">
            De gevraagde stap kon niet worden gevonden.
          </p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => router.push('/inrichten')}
          >
            Terug naar overzicht
          </Button>
        </Card>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper
      title={`Stap ${step.number} -- ${step.name}`}
      actions={
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/inrichten')}
        >
          <ArrowLeftIcon className="mr-1.5 h-4 w-4" />
          Overzicht
        </Button>
      }
    >
      <div className="flex flex-col gap-6 lg:flex-row">
        {/* Left sidebar — step metadata */}
        <div className="w-full lg:w-[300px] flex-shrink-0">
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-xl font-bold text-primary-700">
                  {step.number}
                </div>
                <div>
                  <p className="text-xs text-neutral-500">
                    Fase {step.phase}
                  </p>
                  <h2 className="text-sm font-semibold text-neutral-900">
                    {step.name}
                  </h2>
                </div>
              </div>

              <div className="space-y-3 pt-2 border-t border-neutral-100">
                <div>
                  <p className="text-xs text-neutral-500 mb-1">Status</p>
                  <StatusBadge status={currentStatus} />
                </div>

                <div>
                  <p className="text-xs text-neutral-500 mb-1">Gremium</p>
                  <Badge variant="neutral">{step.required_gremium}</Badge>
                </div>

                {step.domain && (
                  <div>
                    <p className="text-xs text-neutral-500 mb-1">Domein</p>
                    <Badge variant="primary">{step.domain}</Badge>
                  </div>
                )}

                {step.is_optional && (
                  <div>
                    <Badge variant="default">Optioneel</Badge>
                  </div>
                )}

                {depsBlocked && (
                  <div className="flex items-center gap-2 rounded-md bg-yellow-50 px-3 py-2 text-xs text-yellow-800">
                    <LockClosedIcon className="h-4 w-4" />
                    <span>Afhankelijkheden nog niet voldaan</span>
                  </div>
                )}
              </div>

              {step.waarom_nu && (
                <div className="pt-2 border-t border-neutral-100">
                  <div className="flex items-center gap-1 mb-1">
                    <p className="text-xs text-neutral-500">Waarom nu</p>
                    <WaaromTooltip text={step.waarom_nu} />
                  </div>
                  <p className="text-xs text-neutral-600 leading-relaxed">
                    {step.waarom_nu}
                  </p>
                </div>
              )}

              {stepConfig && stepConfig.outputs.length > 0 && (
                <div className="pt-2 border-t border-neutral-100">
                  <p className="text-xs text-neutral-500 mb-2">Outputs</p>
                  <ul className="space-y-1">
                    {stepConfig.outputs.map((output) => (
                      <li
                        key={output}
                        className="text-xs text-neutral-600 flex items-start gap-1.5"
                      >
                        <span className="mt-1 h-1 w-1 rounded-full bg-neutral-400 flex-shrink-0" />
                        {output}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right main area — step content */}
        <div className="flex-1 min-w-0">
          {/* Completed banner */}
          {isCompleted && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium text-green-800">
                Deze stap is vastgesteld
              </span>
            </div>
          )}

          {/* Step content card */}
          <Card>
            {stepConfig && (
              <div className="mb-6">
                <h3 className="text-base font-semibold text-neutral-900 mb-2">
                  {stepConfig.title}
                </h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  {stepConfig.description}
                </p>
              </div>
            )}

            {/* Status update form */}
            {!isCompleted && statusOptions.length > 0 && !depsBlocked && (
              <div className="border-t border-neutral-100 pt-4">
                <h4 className="text-sm font-medium text-neutral-800 mb-3">
                  Status wijzigen
                </h4>
                <div className="flex items-end gap-3">
                  <div className="flex-1 max-w-xs">
                    <Select
                      label="Volgende status"
                      options={[
                        { value: '', label: 'Selecteer...' },
                        ...statusOptions,
                      ]}
                      value={selectedStatus}
                      onChange={(e) => setSelectedStatus(e.target.value)}
                    />
                  </div>
                  <Button
                    size="sm"
                    disabled={!selectedStatus || isUpdating}
                    onClick={handleStatusUpdate}
                  >
                    {isUpdating ? 'Bezig...' : 'Opslaan'}
                  </Button>
                </div>
                {error && (
                  <p className="mt-2 text-sm text-red-600">{error}</p>
                )}
              </div>
            )}

            {/* Blocked message */}
            {depsBlocked && !isCompleted && (
              <div className="border-t border-neutral-100 pt-4">
                <div className="flex items-center gap-2 text-sm text-neutral-500">
                  <LockClosedIcon className="h-4 w-4" />
                  <span>
                    Deze stap kan pas worden gestart nadat alle afhankelijkheden zijn vastgesteld.
                  </span>
                </div>
              </div>
            )}

            {/* Completed read-only message */}
            {isCompleted && (
              <div className="border-t border-neutral-100 pt-4 text-sm text-neutral-500">
                Deze stap is afgerond en kan niet meer worden gewijzigd.
              </div>
            )}
          </Card>
        </div>
      </div>
    </PageWrapper>
  );
}
