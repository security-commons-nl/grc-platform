'use client';

import useSWR from 'swr';
import {
  ShieldExclamationIcon,
  AdjustmentsHorizontalIcon,
  ExclamationTriangleIcon,
  BellAlertIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { ScoreBar } from '@/components/shared/score-bar';
import { api } from '@/lib/api-client';
import type {
  SetupScoreResponse,
  RiskResponse,
  ControlResponse,
  FindingResponse,
  IncidentResponse,
  StepExecutionResponse,
} from '@/lib/api-types';

const DOMAIN_COLORS: Record<string, string> = {
  ISMS: 'border-l-blue-500',
  PIMS: 'border-l-purple-500',
  BCMS: 'border-l-emerald-500',
};

const DOMAIN_LABELS: Record<string, string> = {
  ISMS: 'Informatiebeveiliging',
  PIMS: 'Privacy',
  BCMS: 'Bedrijfscontinuïteit',
};

export default function BeheerDashboardPage() {
  const { data: scores, isLoading: scoresLoading } = useSWR<SetupScoreResponse[]>(
    '/scores/setup-scores/',
    () => api.scores.setupScores(),
  );
  const { data: risks } = useSWR<RiskResponse[]>('/risks/', () => api.risks.list());
  const { data: controls } = useSWR<ControlResponse[]>('/controls/', () => api.controls.list());
  const { data: findings } = useSWR<FindingResponse[]>('/findings/', () => api.findings.list());
  const { data: incidents } = useSWR<IncidentResponse[]>('/incidents/', () => api.incidents.list());
  const { data: executions } = useSWR<StepExecutionResponse[]>(
    '/steps/executions/',
    () => api.steps.listExecutions(),
  );

  const openRisks = risks?.filter((r) => r.status === 'open').length || 0;
  const totalControls = controls?.length || 0;
  const openFindings = findings?.filter((f) => f.status !== 'afgerond').length || 0;
  const recentIncidents = incidents?.length || 0;
  const stepsCompleted = executions?.filter((e) => e.status === 'vastgesteld').length || 0;
  const totalSteps = 22;

  if (scoresLoading) {
    return (
      <PageWrapper title="Beheer — Dashboard" description="Centrale overzichtspagina voor governance, risico en compliance.">
        <CardSkeleton />
      </PageWrapper>
    );
  }

  return (
    <PageWrapper
      title="Beheer — Dashboard"
      description="Centrale overzichtspagina voor governance, risico en compliance."
    >
      {/* Domain score cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3 mb-6">
        {['ISMS', 'PIMS', 'BCMS'].map((domain) => {
          const score = scores?.find((s) => s.domain === domain);
          const pct = score ? Math.round(score.score_pct) : 0;

          return (
            <Card key={domain} className={`border-l-4 ${DOMAIN_COLORS[domain]}`}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-neutral-900">
                    {DOMAIN_LABELS[domain]}
                  </h3>
                  <Badge variant="primary">{domain}</Badge>
                </div>
                <ScoreBar value={pct} label="Inrichtingsscore" />
                {score && (
                  <p className="text-xs text-neutral-500">
                    {score.steps_completed}/{score.steps_total} stappen afgerond
                  </p>
                )}
                {!score && (
                  <p className="text-xs text-neutral-400">Nog geen score beschikbaar</p>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 mb-6">
        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50">
              <ShieldExclamationIcon className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{openRisks}</p>
              <p className="text-xs text-neutral-500">Open risico&apos;s</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
              <AdjustmentsHorizontalIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{totalControls}</p>
              <p className="text-xs text-neutral-500">Controls</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-50">
              <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{openFindings}</p>
              <p className="text-xs text-neutral-500">Open bevindingen</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-50">
              <BellAlertIcon className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900">{recentIncidents}</p>
              <p className="text-xs text-neutral-500">Incidenten</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Step progress */}
      <Card>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <CheckCircleIcon className="h-5 w-5 text-green-600" />
            <h3 className="text-sm font-semibold text-neutral-900">Inrichtingsvoortgang</h3>
          </div>
          <ScoreBar
            value={(stepsCompleted / totalSteps) * 100}
            label={`${stepsCompleted} van ${totalSteps} stappen afgerond`}
          />
        </div>
      </Card>
    </PageWrapper>
  );
}
