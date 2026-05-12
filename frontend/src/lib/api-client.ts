import { getToken, clearToken } from './auth';
import { API_BASE_URL } from './constants';
import type {
  TokenResponse,
  DevTokenRequest,
  CurrentUser,
  StepResponse,
  StepExecutionResponse,
  StepDependencyResponse,
  UserResponse,
  UserTenantRoleResponse,
  StepReadiness,
  StepOutputFulfillmentResponse,
  AgentConversationResponse,
  AgentMessageResponse,
  GenerateDocumentsResponse,
  DecisionResponse,
  DocumentResponse,
  DocumentVersionResponse,
  SetupScoreResponse,
  RiskResponse,
  ControlResponse,
  ScopeResponse,
  AssessmentResponse,
  FindingResponse,
  CorrectiveActionResponse,
  EvidenceResponse,
  IncidentResponse,
  KnowledgeArtifactResponse,
  AISystemResponse,
  AISystemCreate,
  AISystemUpdate,
  AISystemClassifyRequest,
  AISystemClassifySuggestion,
  AISystemFilters,
  HITLCheckpointCreate,
  HITLCheckpointResponse,
  AIAuditLogWithReview,
  AgentTokenRequest,
  AgentTokenResponse,
  CustomFieldDefinition,
  CustomFieldDefinitionCreate,
  CustomFieldDefinitionUpdate,
  CustomFieldEntityType,
  OrganizationalUnitCreate,
  OrganizationalUnitResponse,
  OrganizationalUnitTreeNode,
  OrganizationalUnitUpdate,
} from './api-types';

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API Error ${status}`);
  }
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== 'undefined') window.location.href = '/login';
    throw new ApiError(401, 'Unauthorized');
  }

  if (!res.ok) {
    throw new ApiError(res.status, await res.json().catch(() => null));
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  auth: {
    devToken: (data: DevTokenRequest) =>
      apiFetch<TokenResponse>('/auth/dev-token', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    agentToken: (data: AgentTokenRequest) =>
      apiFetch<AgentTokenResponse>('/auth/agent-token', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    me: () => apiFetch<CurrentUser>('/auth/me'),
  },
  steps: {
    list: () => apiFetch<StepResponse[]>('/steps/'),
    get: (id: string) => apiFetch<StepResponse>(`/steps/${id}`),
    listExecutions: () =>
      apiFetch<StepExecutionResponse[]>('/steps/executions/'),
    createExecution: (data: { step_id: string; status?: string }) =>
      apiFetch<StepExecutionResponse>('/steps/executions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateExecution: (id: string, data: { status?: string; skipped?: boolean; skip_reason?: string }) =>
      apiFetch<StepExecutionResponse>(`/steps/executions/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    listDependencies: () =>
      apiFetch<StepDependencyResponse[]>('/steps/dependencies/'),
    getReadiness: (executionId: string) =>
      apiFetch<StepReadiness>(`/steps/executions/${executionId}/readiness`),
    listFulfillments: (executionId: string) =>
      apiFetch<StepOutputFulfillmentResponse[]>(
        `/steps/executions/${executionId}/fulfillments`
      ),
    createFulfillment: (
      executionId: string,
      data: { step_output_id: string; decision_id?: string; document_id?: string }
    ) =>
      apiFetch<StepOutputFulfillmentResponse>(
        `/steps/executions/${executionId}/fulfillments`,
        { method: 'POST', body: JSON.stringify(data) }
      ),
    deleteFulfillment: (fulfillmentId: string) =>
      apiFetch<void>(`/steps/fulfillments/${fulfillmentId}`, {
        method: 'DELETE',
      }),
  },
  tenants: {
    listUsers: (tenantId: string) =>
      apiFetch<UserResponse[]>(`/tenants/users/?tenant_id=${tenantId}`),
    createUser: (data: Record<string, unknown>) =>
      apiFetch<UserResponse>('/tenants/users/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateUser: (id: string, data: Record<string, unknown>) =>
      apiFetch<UserResponse>(`/tenants/users/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    listRoles: (tenantId: string) =>
      apiFetch<UserTenantRoleResponse[]>(
        `/tenants/user-tenant-roles/?tenant_id=${tenantId}`
      ),
    createRole: (data: Record<string, unknown>) =>
      apiFetch<UserTenantRoleResponse>('/tenants/user-tenant-roles/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    deleteRole: (id: string) =>
      apiFetch<void>(`/tenants/user-tenant-roles/${id}`, {
        method: 'DELETE',
      }),
  },
  agents: {
    startConversation: (agentName: string, data: { step_execution_id: string }) =>
      apiFetch<AgentConversationResponse>(
        `/agents/${agentName}/conversations`,
        { method: 'POST', body: JSON.stringify(data) }
      ),
    getConversation: (conversationId: string) =>
      apiFetch<AgentConversationResponse>(
        `/agents/conversations/${conversationId}`
      ),
    sendMessage: (conversationId: string, data: { content: string }) =>
      apiFetch<AgentMessageResponse>(
        `/agents/conversations/${conversationId}/messages`,
        { method: 'POST', body: JSON.stringify(data) }
      ),
    submitFeedback: (
      conversationId: string,
      data: { feedback: string; comment?: string }
    ) =>
      apiFetch<void>(
        `/agents/conversations/${conversationId}/feedback`,
        { method: 'POST', body: JSON.stringify(data) }
      ),
    generateDocuments: (conversationId: string) =>
      apiFetch<GenerateDocumentsResponse>(
        `/agents/conversations/${conversationId}/generate`,
        { method: 'POST' }
      ),
  },
  decisions: {
    list: () => apiFetch<DecisionResponse[]>('/decisions/'),
    create: (data: Record<string, unknown>) =>
      apiFetch<DecisionResponse>('/decisions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  documents: {
    list: () => apiFetch<DocumentResponse[]>('/documents/'),
    get: (id: string) => apiFetch<DocumentResponse>(`/documents/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<DocumentResponse>('/documents/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    exportVersion: (versionId: string, format: 'md' | 'html' = 'html') => {
      const token = getToken();
      return fetch(`${API_BASE_URL}/documents/versions/${versionId}/export?format=${format}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }).then((res) => {
        if (!res.ok) throw new ApiError(res.status, null);
        return res.blob();
      }).then((blob) => {
        const ext = format === 'md' ? 'md' : 'html';
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `concept-document.${ext}`;
        a.click();
        URL.revokeObjectURL(a.href);
      });
    },
    listVersions: (docId: string) =>
      apiFetch<DocumentVersionResponse[]>(`/documents/versions/?document_id=${docId}`),
    createVersion: (docId: string, data: Record<string, unknown>) =>
      apiFetch<DocumentVersionResponse>(`/documents/versions/?document_id=${docId}`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  scores: {
    setupScores: () => apiFetch<SetupScoreResponse[]>('/scores/setup-scores/'),
  },
  risks: {
    list: (
      filters: {
        organizationalUnitId?: string;
        includeDescendants?: boolean;
        scopeId?: string;
        status?: string;
        domain?: string;
      } = {},
    ) => {
      const params = new URLSearchParams();
      if (filters.organizationalUnitId)
        params.set('organizational_unit_id', filters.organizationalUnitId);
      if (filters.includeDescendants) params.set('include_descendants', 'true');
      if (filters.scopeId) params.set('scope_id', filters.scopeId);
      if (filters.status) params.set('status', filters.status);
      if (filters.domain) params.set('domain', filters.domain);
      const qs = params.toString() ? `?${params.toString()}` : '';
      return apiFetch<RiskResponse[]>(`/risks/${qs}`);
    },
    get: (id: string) => apiFetch<RiskResponse>(`/risks/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<RiskResponse>('/risks/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Record<string, unknown>) =>
      apiFetch<RiskResponse>(`/risks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/risks/${id}`, { method: 'DELETE' }),
    // M5 — Monte Carlo simulation
    simulate: (
      id: string,
      opts: { iterations?: number; seed?: number; includeSamples?: boolean } = {},
    ) => {
      const params = new URLSearchParams();
      if (opts.iterations) params.set('iterations', String(opts.iterations));
      if (opts.seed !== undefined) params.set('seed', String(opts.seed));
      if (opts.includeSamples) params.set('include_samples', 'true');
      const qs = params.toString() ? `?${params.toString()}` : '';
      return apiFetch<import('./api-types').RiskSimulationResponse>(
        `/risks/${id}/simulate${qs}`,
        { method: 'POST' },
      );
    },
  },
  controls: {
    list: () => apiFetch<ControlResponse[]>('/controls/'),
    get: (id: string) => apiFetch<ControlResponse>(`/controls/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<ControlResponse>('/controls/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Record<string, unknown>) =>
      apiFetch<ControlResponse>(`/controls/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/controls/${id}`, { method: 'DELETE' }),
  },
  scopes: {
    list: () => apiFetch<ScopeResponse[]>('/scopes/'),
    get: (id: string) => apiFetch<ScopeResponse>(`/scopes/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<ScopeResponse>('/scopes/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  assessments: {
    list: () => apiFetch<AssessmentResponse[]>('/assessments/'),
    get: (id: string) => apiFetch<AssessmentResponse>(`/assessments/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<AssessmentResponse>('/assessments/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  findings: {
    list: () => apiFetch<FindingResponse[]>('/assessments/findings/'),
    get: (id: string) => apiFetch<FindingResponse>(`/assessments/findings/${id}`),
  },
  correctiveActions: {
    list: () => apiFetch<CorrectiveActionResponse[]>('/assessments/corrective-actions/'),
    get: (id: string) => apiFetch<CorrectiveActionResponse>(`/assessments/corrective-actions/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<CorrectiveActionResponse>('/assessments/corrective-actions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  evidence: {
    list: () => apiFetch<EvidenceResponse[]>('/evidence/'),
    get: (id: string) => apiFetch<EvidenceResponse>(`/evidence/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<EvidenceResponse>('/evidence/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  incidents: {
    list: () => apiFetch<IncidentResponse[]>('/incidents/'),
    get: (id: string) => apiFetch<IncidentResponse>(`/incidents/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<IncidentResponse>('/incidents/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  knowledge: {
    list: () => apiFetch<KnowledgeArtifactResponse[]>('/knowledge/'),
    get: (id: string) => apiFetch<KnowledgeArtifactResponse>(`/knowledge/${id}`),
    create: (data: Record<string, unknown>) =>
      apiFetch<KnowledgeArtifactResponse>('/knowledge/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  aiSystems: {
    list: (filters?: AISystemFilters) => {
      const params = new URLSearchParams();
      if (filters?.eu_ai_act_risk) params.set('eu_ai_act_risk', filters.eu_ai_act_risk);
      if (filters?.deployment_status) params.set('deployment_status', filters.deployment_status);
      if (filters?.system_type) params.set('system_type', filters.system_type);
      const qs = params.toString() ? `?${params.toString()}` : '';
      return apiFetch<AISystemResponse[]>(`/ai-systems/${qs}`);
    },
    get: (id: string) => apiFetch<AISystemResponse>(`/ai-systems/${id}`),
    create: (data: AISystemCreate) =>
      apiFetch<AISystemResponse>('/ai-systems/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: AISystemUpdate) =>
      apiFetch<AISystemResponse>(`/ai-systems/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/ai-systems/${id}`, { method: 'DELETE' }),
    classifySuggestion: (data: AISystemClassifyRequest) =>
      apiFetch<AISystemClassifySuggestion>('/ai-systems/classify-suggestion', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  customFields: {
    list: (entityType?: CustomFieldEntityType) => {
      const qs = entityType ? `?entity_type=${entityType}` : '';
      return apiFetch<CustomFieldDefinition[]>(`/custom-fields/${qs}`);
    },
    get: (id: string) => apiFetch<CustomFieldDefinition>(`/custom-fields/${id}`),
    create: (data: CustomFieldDefinitionCreate) =>
      apiFetch<CustomFieldDefinition>('/custom-fields/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: CustomFieldDefinitionUpdate) =>
      apiFetch<CustomFieldDefinition>(`/custom-fields/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/custom-fields/${id}`, { method: 'DELETE' }),
  },
  organizationalUnits: {
    list: (opts: { isActive?: boolean } = {}) => {
      const qs =
        opts.isActive !== undefined ? `?is_active=${opts.isActive}` : '';
      return apiFetch<OrganizationalUnitResponse[]>(
        `/organizational-units/${qs}`,
      );
    },
    tree: () =>
      apiFetch<OrganizationalUnitTreeNode[]>('/organizational-units/tree'),
    get: (id: string) =>
      apiFetch<OrganizationalUnitResponse>(`/organizational-units/${id}`),
    descendants: (id: string) =>
      apiFetch<string[]>(`/organizational-units/${id}/descendants`),
    create: (data: OrganizationalUnitCreate) =>
      apiFetch<OrganizationalUnitResponse>('/organizational-units/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: OrganizationalUnitUpdate) =>
      apiFetch<OrganizationalUnitResponse>(`/organizational-units/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/organizational-units/${id}`, { method: 'DELETE' }),
  },
  hitl: {
    listAuditLogs: (opts: { onlyUnreviewed?: boolean; agentName?: string } = {}) => {
      const params = new URLSearchParams();
      if (opts.onlyUnreviewed) params.set('only_unreviewed', 'true');
      if (opts.agentName) params.set('agent_name', opts.agentName);
      const qs = params.toString() ? `?${params.toString()}` : '';
      return apiFetch<AIAuditLogWithReview[]>(`/ai-hitl-checkpoints/audit-logs${qs}`);
    },
    listCheckpoints: (auditLogId?: string) => {
      const qs = auditLogId ? `?audit_log_id=${auditLogId}` : '';
      return apiFetch<HITLCheckpointResponse[]>(`/ai-hitl-checkpoints/${qs}`);
    },
    createCheckpoint: (data: HITLCheckpointCreate) =>
      apiFetch<HITLCheckpointResponse>('/ai-hitl-checkpoints/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};

export { apiFetch };
