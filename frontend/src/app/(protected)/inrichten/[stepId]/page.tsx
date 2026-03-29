'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  LockClosedIcon,
  ArrowUpTrayIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { StatusBadge } from '@/components/shared/status-badge';
import { WaaromTooltip } from '@/components/shared/waarom-tooltip';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { ChatIsland } from '@/components/ai/chat-island';
import { formatApiError } from '@/lib/format-error';
import { api, apiFetch, ApiError } from '@/lib/api-client';
import type {
  StepResponse,
  StepExecutionResponse,
  StepReadiness,
  DecisionResponse,
  DocumentResponse,
} from '@/lib/api-types';

// Pure UI labels — no process logic
const TRANSITION_LABELS: Record<string, { label: string; variant: 'primary' | 'secondary' | 'danger' }> = {
  in_uitvoering: { label: 'Start deze stap', variant: 'primary' },
  concept: { label: 'Markeer als concept', variant: 'primary' },
  in_review: { label: 'Indienen voor review', variant: 'primary' },
  vastgesteld: { label: 'Goedkeuren', variant: 'primary' },
};

// For the "terugsturen" case (in_review → concept)
const BACK_TRANSITION_LABEL = { label: 'Terugsturen', variant: 'secondary' as const };

export default function StepDetailPage({
  params,
}: {
  params: Promise<{ stepId: string }>;
}) {
  const { stepId } = use(params);
  const router = useRouter();
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFile, setUploadFile] = useState('');
  const [uploadType, setUploadType] = useState('pdf');
  const [linkingOutputId, setLinkingOutputId] = useState<string | null>(null);

  const { data: step, isLoading: stepLoading } = useSWR<StepResponse>(
    `/steps/${stepId}`,
    () => api.steps.get(stepId),
  );

  const {
    data: allExecutions,
    isLoading: execLoading,
    mutate: mutateExecutions,
  } = useSWR<StepExecutionResponse[]>('/steps/executions/', () =>
    api.steps.listExecutions(),
  );

  const execution = allExecutions?.find((e) => e.step_id === stepId);
  const executionId = execution?.id;
  const currentStatus = execution?.status || 'niet_gestart';
  const isCompleted = currentStatus === 'vastgesteld';

  // Readiness from API — the single source of truth for gates and transitions
  const {
    data: readiness,
    mutate: mutateReadiness,
  } = useSWR<StepReadiness>(
    executionId ? `/steps/executions/${executionId}/readiness` : null,
    () => (executionId ? api.steps.getReadiness(executionId) : null!),
  );

  // Load decisions and documents for fulfillment linking
  const { data: decisions = [] } = useSWR<DecisionResponse[]>(
    executionId ? `/decisions-for-${executionId}` : null,
    () => api.decisions.list(),
  );
  const { data: documents = [] } = useSWR<DocumentResponse[]>(
    executionId ? `/documents-for-${executionId}` : null,
    () => api.documents.list(),
  );

  const isBlocked = readiness ? !readiness.dependencies_met : false;
  const allowedTransitions = readiness?.allowed_transitions || [];

  // Filter to this step's execution
  const stepDecisions = decisions.filter((d) => d.step_execution_id === executionId);
  const stepDocuments = documents.filter((d) => d.step_execution_id === executionId);

  async function handleLinkFulfillment(outputId: string, outputType: string, linkedId: string) {
    if (!executionId) return;
    setIsUpdating(true);
    setError(null);
    try {
      const payload: Record<string, string> = { step_output_id: outputId };
      if (outputType === 'decision') {
        payload.decision_id = linkedId;
      } else {
        payload.document_id = linkedId;
      }
      await api.steps.createFulfillment(executionId, payload);
      await mutateReadiness();
      setLinkingOutputId(null);
    } catch (err) {
      if (err instanceof ApiError) {
        const detail = (err.body as Record<string, unknown>)?.detail || 'Koppelen mislukt';
        setError(String(detail));
      }
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleTransition(targetStatus: string) {
    setIsUpdating(true);
    setError(null);

    try {
      if (!execution) {
        // Create execution first, then transition
        const created = await api.steps.createExecution({
          step_id: stepId,
          status: 'niet_gestart',
        });
        if (targetStatus !== 'niet_gestart') {
          await api.steps.updateExecution(created.id, {
            status: targetStatus,
          });
        }
      } else {
        await api.steps.updateExecution(execution.id, {
          status: targetStatus,
        });
      }
      await mutateExecutions();
      await mutateReadiness();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Fout: ${formatApiError(err.body)}`);
      } else {
        setError(
          `Fout: ${err instanceof Error ? err.message : String(err)}`,
        );
      }
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleUpload() {
    if (!uploadFile.trim() || !executionId) return;
    setIsUpdating(true);
    setError(null);
    try {
      await apiFetch('/documents/input-documents/', {
        method: 'POST',
        body: JSON.stringify({
          step_execution_id: executionId,
          source_type: uploadType,
          storage_path: uploadFile.trim(),
          status: 'pending',
          uploaded_at: new Date().toISOString(),
        }),
      });
      setShowUpload(false);
      setUploadFile('');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Upload fout: ${formatApiError(err.body)}`);
      } else {
        setError(`Upload fout: ${err instanceof Error ? err.message : String(err)}`);
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

  // Build action buttons from API-provided allowed transitions
  const actions = allowedTransitions.map((t) => {
    // Special case: going back from in_review to concept
    if (currentStatus === 'in_review' && t === 'concept') {
      return { target: t, ...BACK_TRANSITION_LABEL };
    }
    const label = TRANSITION_LABELS[t] || { label: t, variant: 'primary' as const };
    return { target: t, ...label };
  });

  // For niet_gestart without execution, allow starting
  const canStart = !execution && !isCompleted;
  if (canStart) {
    actions.push({
      target: 'in_uitvoering',
      label: 'Start deze stap',
      variant: 'primary',
    });
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
        {/* Left sidebar -- step metadata */}
        <div className="w-full lg:w-[300px] flex-shrink-0 space-y-4">
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-xl font-bold text-primary-700">
                  {step.number}
                </div>
                <div>
                  <p className="text-xs text-neutral-500">Fase {step.phase}</p>
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
                  <Badge variant="default">Optioneel</Badge>
                )}

                {isBlocked && (
                  <div className="flex items-center gap-2 rounded-md bg-yellow-50 px-3 py-2 text-xs text-yellow-800">
                    <LockClosedIcon className="h-4 w-4" />
                    <span>Blokkerende afhankelijkheden niet voldaan</span>
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

              {/* Outputs from API (step.outputs) with link buttons */}
              {step.outputs && step.outputs.length > 0 && (
                <div className="pt-2 border-t border-neutral-100">
                  <p className="text-xs text-neutral-500 mb-2">
                    Outputs ({readiness ? `${readiness.required_fulfilled}/${readiness.required_total}` : '...'})
                  </p>
                  <ul className="space-y-2">
                    {step.outputs
                      .sort((a, b) => a.sort_order - b.sort_order)
                      .map((output) => {
                        const item = readiness?.outputs.find(
                          (o) => o.output.id === output.id,
                        );
                        const fulfilled = item?.fulfilled || false;
                        const isLinking = linkingOutputId === output.id;
                        const canLink = executionId && !fulfilled && !isCompleted;
                        const isDecisionType = output.output_type === 'decision';
                        const linkOptions = isDecisionType ? stepDecisions : stepDocuments;

                        return (
                          <li key={output.id} className="text-xs">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`h-2 w-2 rounded-full flex-shrink-0 ${
                                  fulfilled
                                    ? 'bg-green-500'
                                    : output.requirement === 'V'
                                      ? 'bg-red-400'
                                      : 'bg-neutral-300'
                                }`}
                              />
                              <span
                                className={`flex-1 ${
                                  fulfilled ? 'text-green-700' : 'text-neutral-600'
                                }`}
                              >
                                {output.name}
                                {output.requirement === 'V' && (
                                  <span className="ml-1 text-neutral-400">(V)</span>
                                )}
                              </span>
                              {canLink && !isLinking && (
                                <button
                                  onClick={() => setLinkingOutputId(output.id)}
                                  className="text-primary-600 hover:text-primary-800 font-medium"
                                >
                                  Koppel
                                </button>
                              )}
                            </div>

                            {/* Inline picker */}
                            {isLinking && (
                              <div className="mt-1.5 ml-3.5 space-y-1">
                                {linkOptions.length === 0 ? (
                                  <p className="text-neutral-400 italic">
                                    Geen {isDecisionType ? 'besluiten' : 'documenten'} beschikbaar.
                                    Maak er eerst een aan.
                                  </p>
                                ) : (
                                  linkOptions.map((item) => (
                                    <button
                                      key={item.id}
                                      onClick={() =>
                                        handleLinkFulfillment(
                                          output.id,
                                          output.output_type,
                                          item.id,
                                        )
                                      }
                                      disabled={isUpdating}
                                      className="block w-full text-left rounded px-2 py-1 hover:bg-primary-50 text-neutral-700"
                                    >
                                      {'content' in item
                                        ? (item as DecisionResponse).content?.slice(0, 50)
                                        : (item as DocumentResponse).title}
                                    </button>
                                  ))
                                )}
                                <button
                                  onClick={() => setLinkingOutputId(null)}
                                  className="text-neutral-400 hover:text-neutral-600"
                                >
                                  Annuleren
                                </button>
                              </div>
                            )}
                          </li>
                        );
                      })}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right main area */}
        <div className="flex-1 min-w-0 space-y-4">
          {/* Completed banner */}
          {isCompleted && (
            <div className="flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium text-green-800">
                Deze stap is vastgesteld
              </span>
            </div>
          )}

          {/* Step description */}
          <Card>
            <div>
              <h3 className="text-base font-semibold text-neutral-900 mb-2">
                {step.name}
              </h3>
              <p className="text-sm text-neutral-600 leading-relaxed">
                {step.waarom_nu}
              </p>
            </div>
          </Card>

          {/* Action buttons (direct, no dropdown) */}
          {!isCompleted && !isBlocked && actions.length > 0 && (
            <Card>
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-neutral-800">
                  Acties
                </h4>

                {/* Missing outputs warning from readiness */}
                {readiness && !readiness.all_required_met && currentStatus !== 'niet_gestart' && (
                  <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
                    Niet alle verplichte outputs zijn ingevuld ({readiness.required_fulfilled}/{readiness.required_total}).
                    Vul de ontbrekende outputs aan om verder te kunnen.
                  </div>
                )}

                <div className="flex flex-wrap gap-2">
                  {actions.map((action) => (
                    <Button
                      key={action.target}
                      variant={action.variant}
                      size="md"
                      disabled={isUpdating}
                      onClick={() => handleTransition(action.target)}
                    >
                      {isUpdating ? 'Bezig...' : action.label}
                    </Button>
                  ))}
                </div>

                {error && (
                  <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                    {error}
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Document upload (secundaire invoerroute K6) */}
          {execution && !isCompleted && (
            <Card>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-neutral-800">
                    Document uploaden
                  </h4>
                  {!showUpload && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setShowUpload(true)}
                    >
                      <ArrowUpTrayIcon className="mr-1.5 h-4 w-4" />
                      Upload
                    </Button>
                  )}
                </div>

                <p className="text-xs text-neutral-500">
                  Upload een bestaand document (PDF, Word, Markdown) als input
                  voor deze stap. Het document wordt geanalyseerd door een
                  AI-agent.
                </p>

                {showUpload && (
                  <div className="space-y-3 pt-2 border-t border-neutral-100">
                    <Select
                      label="Documenttype"
                      value={uploadType}
                      onChange={(e) => setUploadType(e.target.value)}
                      options={[
                        { value: 'pdf', label: 'PDF' },
                        { value: 'docx', label: 'Word (docx)' },
                        { value: 'markdown', label: 'Markdown' },
                      ]}
                    />
                    <Input
                      label="Bestandspad of URL"
                      placeholder="bijv. /docs/beleidsdocument-isms.pdf"
                      value={uploadFile}
                      onChange={(e) => setUploadFile(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        disabled={!uploadFile.trim() || isUpdating}
                        onClick={handleUpload}
                      >
                        {isUpdating ? 'Bezig...' : 'Uploaden'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setShowUpload(false);
                          setUploadFile('');
                        }}
                      >
                        Annuleren
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Blocked message */}
          {isBlocked && !isCompleted && (
            <Card>
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <LockClosedIcon className="h-4 w-4" />
                <span>
                  Deze stap kan pas worden gestart nadat alle blokkerende
                  afhankelijkheden zijn vastgesteld.
                </span>
              </div>
            </Card>
          )}

          {/* Completed read-only */}
          {isCompleted && (
            <Card>
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <DocumentTextIcon className="h-4 w-4" />
                <span>
                  Deze stap is afgerond. Bekijk de gekoppelde besluiten en
                  documenten in het besluitlog en de documentenviewer.
                </span>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* AI Chat Island — visible when step is active */}
      {step && executionId && (currentStatus === 'in_uitvoering' || currentStatus === 'concept') && (
        <ChatIsland stepNumber={step.number} executionId={executionId} />
      )}
    </PageWrapper>
  );
}
