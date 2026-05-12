'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { KeyIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { useAuth } from '@/providers/auth-provider';
import { api, ApiError } from '@/lib/api-client';
import { formatApiError } from '@/lib/format-error';
import type {
  AISystemResponse,
  AgentTokenResponse,
} from '@/lib/api-types';

/**
 * Vooraf-gedefinieerde scopes. Houdt de set klein en bewust — uitbreiden
 * vergt expliciet vervolg-RFC, niet ad-hoc keuze door admin.
 */
const SCOPE_PRESETS: { value: string; label: string; description: string }[] = [
  { value: 'risks:read', label: 'Risico\'s lezen', description: 'GET /risks/*' },
  { value: 'risks:write', label: 'Risico\'s schrijven', description: 'POST/PATCH /risks/*' },
  { value: 'controls:read', label: 'Controls lezen', description: 'GET /controls/*' },
  { value: 'controls:write', label: 'Controls schrijven', description: 'POST/PATCH /controls/*' },
  { value: 'assessments:read', label: 'Assessments lezen', description: 'GET /assessments/*' },
  { value: 'assessments:write', label: 'Assessments schrijven', description: 'POST/PATCH /assessments/*' },
  { value: 'hitl:write', label: 'HITL-checkpoints schrijven', description: 'Agent legt eigen HITL-input vast' },
  { value: 'documents:read', label: 'Documenten lezen', description: 'GET /documents/*' },
];

const TTL_OPTIONS: { value: number; label: string }[] = [
  { value: 15, label: '15 minuten' },
  { value: 60, label: '1 uur (standaard)' },
  { value: 240, label: '4 uur' },
  { value: 480, label: '8 uur' },
  { value: 24 * 60, label: '24 uur (maximum)' },
];

export default function AgentTokensPage() {
  const { user } = useAuth();
  const { data: aiSystems } = useSWR<AISystemResponse[]>(
    'admin-agent-tokens-ai-systems',
    () => api.aiSystems.list(),
  );

  const [agentName, setAgentName] = useState('');
  const [scope, setScope] = useState<string[]>(['risks:read']);
  const [ttl, setTtl] = useState(60);
  const [aiSystemId, setAiSystemId] = useState<string>('');
  const [confirmStep, setConfirmStep] = useState(false);

  const [issued, setIssued] = useState<AgentTokenResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  function toggleScope(s: string) {
    setScope((curr) =>
      curr.includes(s) ? curr.filter((x) => x !== s) : [...curr, s],
    );
  }

  async function handleIssue() {
    if (!user) {
      setFormError('Niet ingelogd.');
      return;
    }
    if (!agentName.trim()) {
      setFormError('Geef de agent een herkenbare naam.');
      return;
    }
    if (scope.length === 0) {
      setFormError('Kies minstens één scope.');
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const token = await api.auth.agentToken({
        tenant_id: user.tenant_id,
        agent_name: agentName.trim(),
        scope,
        ttl_minutes: ttl,
        ai_system_id: aiSystemId || null,
      });
      setIssued(token);
      setConfirmStep(false);
    } catch (err) {
      const detail = err instanceof ApiError ? formatApiError(err.body) : String(err);
      setFormError(`Token uitgeven mislukt: ${detail}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function copyToken() {
    if (!issued) return;
    try {
      await navigator.clipboard.writeText(issued.access_token);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  function startOver() {
    setIssued(null);
    setAgentName('');
    setScope(['risks:read']);
    setTtl(60);
    setAiSystemId('');
    setConfirmStep(false);
    setFormError(null);
    setCopied(false);
  }

  return (
    <PageWrapper
      title="Agent-tokens"
      description="Uitgifte van Non-Human Identity (NHI) tokens voor AI-agents en automatisering. Tokens zijn kort-levend en scope-beperkt."
    >
      {issued ? (
        <Card className="mb-4 border-amber-300 bg-amber-50/60">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 shrink-0 text-amber-700 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-base font-semibold text-neutral-900">
                Token uitgegeven — kopieer nu
              </h3>
              <p className="mt-1 text-sm text-amber-900">
                Deze JWT wordt <strong>niet opnieuw getoond</strong>. Bewaar hem direct in de
                geheime-opslag van de agent. Bij verlies moet u een nieuwe uitgeven.
              </p>

              <div className="mt-3 rounded-md border border-amber-200 bg-white p-3">
                <code className="block break-all text-xs text-neutral-800">
                  {issued.access_token}
                </code>
              </div>

              <div className="mt-3 flex items-center gap-2">
                <Button variant="primary" size="sm" onClick={copyToken}>
                  {copied ? 'Gekopieerd ✓' : 'Kopieer naar klembord'}
                </Button>
                <Button variant="ghost" size="sm" onClick={startOver}>
                  Nieuwe token uitgeven
                </Button>
              </div>

              <dl className="mt-4 grid grid-cols-1 gap-2 text-xs text-neutral-700 sm:grid-cols-2">
                <div>
                  <dt className="text-neutral-500">Geldig</dt>
                  <dd>
                    {Math.round(issued.expires_in / 60)} minuten (
                    {issued.expires_in.toLocaleString('nl-NL')} seconden)
                  </dd>
                </div>
                <div>
                  <dt className="text-neutral-500">Scope</dt>
                  <dd>{issued.scope?.join(', ') ?? '—'}</dd>
                </div>
                {issued.ai_system_id && (
                  <div className="sm:col-span-2">
                    <dt className="text-neutral-500">Gekoppeld AI-systeem</dt>
                    <dd>
                      <code>{issued.ai_system_id}</code>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        </Card>
      ) : (
        <Card className="mb-4">
          <div className="flex items-start gap-3">
            <KeyIcon className="h-6 w-6 shrink-0 text-primary-700 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-base font-semibold text-neutral-900">
                Nieuwe agent-token
              </h3>
              <p className="mt-1 text-sm text-neutral-600">
                Tokens hebben een maximale levensduur van 24 uur en zijn beperkt tot de
                hieronder gekozen scopes. Geef alleen wat de agent strikt nodig heeft.
              </p>

              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Naam van de agent *"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="bv. incident-summarizer"
                />
                <Select
                  label="Geldigheid"
                  options={TTL_OPTIONS.map((o) => ({
                    value: String(o.value),
                    label: o.label,
                  }))}
                  value={String(ttl)}
                  onChange={(e) => setTtl(Number(e.target.value))}
                />
              </div>

              <div className="mt-4">
                <Select
                  label="Koppel aan AI-systeem (optioneel)"
                  options={[
                    { value: '', label: 'Geen koppeling — alleen-staande agent' },
                    ...(aiSystems ?? []).map((s) => ({ value: s.id, label: s.name })),
                  ]}
                  value={aiSystemId}
                  onChange={(e) => setAiSystemId(e.target.value)}
                />
                <p className="mt-1 text-xs text-neutral-500">
                  Aanbevolen voor traceability: elke agent-actie wordt zo herleidbaar tot
                  een geregistreerd AI-systeem.
                </p>
              </div>

              <div className="mt-4">
                <div className="text-sm font-medium text-neutral-800 mb-1.5">Scopes *</div>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {SCOPE_PRESETS.map((preset) => {
                    const checked = scope.includes(preset.value);
                    return (
                      <label
                        key={preset.value}
                        className={`flex items-start gap-2 rounded-md border p-2.5 cursor-pointer transition-colors ${
                          checked
                            ? 'border-primary-300 bg-primary-50'
                            : 'border-neutral-200 hover:border-neutral-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          className="mt-1"
                          checked={checked}
                          onChange={() => toggleScope(preset.value)}
                        />
                        <div className="flex-1 text-sm">
                          <div className="font-medium text-neutral-800">{preset.label}</div>
                          <div className="text-xs text-neutral-500">
                            <code>{preset.value}</code> · {preset.description}
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {formError && <p className="mt-3 text-sm text-red-600">{formError}</p>}

              <div className="mt-4 flex items-center gap-3">
                {!confirmStep ? (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      if (!agentName.trim() || scope.length === 0) {
                        setFormError('Vul naam en minstens één scope in.');
                        return;
                      }
                      setFormError(null);
                      setConfirmStep(true);
                    }}
                  >
                    Token uitgeven...
                  </Button>
                ) : (
                  <>
                    <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                      Weet u zeker dat u deze token wilt uitgeven? Hij wordt eenmalig getoond
                      en is niet intrekbaar vóór afloop.
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleIssue}
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Bezig...' : 'Ja, uitgeven'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setConfirmStep(false)}
                    >
                      Annuleren
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        </Card>
      )}

      <Card>
        <h3 className="text-sm font-semibold text-neutral-800 mb-2">
          Waarom agent-tokens?
        </h3>
        <ul className="text-sm text-neutral-700 list-disc pl-5 space-y-1">
          <li>
            <strong>Korte levensduur:</strong> bij lekken is de blootstelling beperkt tot
            maximaal 24 uur.
          </li>
          <li>
            <strong>Scope-beperkt:</strong> de agent kan alleen wat u expliciet toestaat —
            geen volledige admin-rechten.
          </li>
          <li>
            <strong>Auditeerbaar:</strong> elke agent-actie verschijnt in <code>ai_audit_logs</code>{' '}
            en is reviewbaar via de HITL-pagina.
          </li>
          <li>
            <strong>EU AI Act art. 14:</strong> menselijk toezicht is gewaarborgd doordat
            agent-acties op een mens-naam (uitgevende admin) zijn herleidbaar.
          </li>
        </ul>
      </Card>
    </PageWrapper>
  );
}
