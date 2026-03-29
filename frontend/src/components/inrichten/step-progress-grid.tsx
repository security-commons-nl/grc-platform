'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { StepCard } from './step-card';
import type {
  StepResponse,
  StepExecutionResponse,
  StepDependencyResponse,
} from '@/lib/api-types';

interface StepProgressGridProps {
  steps: StepResponse[];
  executions: StepExecutionResponse[];
  dependencies: StepDependencyResponse[];
}

const PHASE_LABELS: Record<number, string> = {
  0: 'Fase 0 -- Fundament',
  1: 'Fase 1 -- Lijnmanagement doet risicoanalyse',
  2: 'Fase 2 -- PDCA draait, controls, evidence',
  3: 'Fase 3 -- Volwassen GRC-platform',
};

function isStepBlocked(
  step: StepResponse,
  dependencies: StepDependencyResponse[],
  executionsByStepId: Map<string, StepExecutionResponse>,
): boolean {
  const deps = dependencies.filter((d) => d.step_id === step.id);
  if (deps.length === 0) return false;

  return deps.some((dep) => {
    const depExec = executionsByStepId.get(dep.depends_on_step_id);
    if (!depExec) return true;
    return depExec.status !== 'vastgesteld';
  });
}

export function StepProgressGrid({
  steps,
  executions,
  dependencies,
}: StepProgressGridProps) {
  const router = useRouter();
  const [collapsedPhases, setCollapsedPhases] = useState<Set<number>>(
    new Set(),
  );

  const executionsByStepId = new Map<string, StepExecutionResponse>();
  for (const exec of executions) {
    executionsByStepId.set(exec.step_id, exec);
  }

  const phases = [0, 1, 2, 3];
  const stepsByPhase = new Map<number, StepResponse[]>();
  for (const phase of phases) {
    stepsByPhase.set(
      phase,
      steps
        .filter((s) => s.phase === phase)
        .sort((a, b) => a.number.localeCompare(b.number, undefined, { numeric: true })),
    );
  }

  function togglePhase(phase: number) {
    setCollapsedPhases((prev) => {
      const next = new Set(prev);
      if (next.has(phase)) {
        next.delete(phase);
      } else {
        next.add(phase);
      }
      return next;
    });
  }

  function getPhaseCompletion(phase: number): { completed: number; total: number } {
    const phaseSteps = stepsByPhase.get(phase) || [];
    const completed = phaseSteps.filter((s) => {
      const exec = executionsByStepId.get(s.id);
      return exec?.status === 'vastgesteld';
    }).length;
    return { completed, total: phaseSteps.length };
  }

  return (
    <div className="space-y-6">
      {phases.map((phase) => {
        const phaseSteps = stepsByPhase.get(phase) || [];
        if (phaseSteps.length === 0) return null;

        const isCollapsed = collapsedPhases.has(phase);
        const { completed, total } = getPhaseCompletion(phase);

        return (
          <div key={phase}>
            <button
              type="button"
              onClick={() => togglePhase(phase)}
              className="flex w-full items-center gap-2 py-2 text-left"
            >
              {isCollapsed ? (
                <ChevronRightIcon className="h-5 w-5 text-neutral-400" />
              ) : (
                <ChevronDownIcon className="h-5 w-5 text-neutral-400" />
              )}
              <h2 className="text-base font-semibold text-neutral-900">
                {PHASE_LABELS[phase] || `Fase ${phase}`}
              </h2>
              <span className="text-sm text-neutral-500">
                {completed}/{total} afgerond
              </span>
            </button>

            {!isCollapsed && (
              <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                {phaseSteps.map((step) => (
                  <StepCard
                    key={step.id}
                    step={step}
                    execution={executionsByStepId.get(step.id)}
                    isBlocked={isStepBlocked(step, dependencies, executionsByStepId)}
                    onClick={() => router.push(`/inrichten/${step.id}`)}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
