// ── Auth ────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface CurrentUser {
  id: string;
  tenant_id: string;
  role: string;
  domain?: string | null;
  token_type: string;
  agent_name?: string | null;
}

export interface DevTokenRequest {
  user_id: string;
  tenant_id: string;
  role?: string;
  domain?: string | null;
}

// ── Tenants ─────────────────────────────────────────────────────────────────

export interface TenantResponse {
  id: string;
  name: string;
  type: string;
  region_id?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Steps ───────────────────────────────────────────────────────────────────

export interface StepOutputResponse {
  id: string;
  step_id: string;
  name: string;
  output_type: string;
  requirement: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface StepResponse {
  id: string;
  number: string;
  phase: number;
  name: string;
  waarom_nu?: string;
  required_gremium: string;
  is_optional: boolean;
  domain?: string | null;
  outputs: StepOutputResponse[];
  created_at: string;
  updated_at: string;
}

export interface StepExecutionResponse {
  id: string;
  tenant_id: string;
  step_id: string;
  cyclus_id?: number | null;
  status: string;
  started_at?: string | null;
  completed_at?: string | null;
  skipped: boolean;
  skip_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface StepDependencyResponse {
  id: string;
  step_id: string;
  depends_on_step_id: string;
  dependency_type: string;
  created_at: string;
  updated_at: string;
}

export interface StepOutputFulfillmentResponse {
  id: string;
  tenant_id: string;
  step_output_id: string;
  step_execution_id: string;
  decision_id?: string | null;
  document_id?: string | null;
  fulfilled_at: string;
  fulfilled_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutputReadinessItem {
  output: StepOutputResponse;
  fulfilled: boolean;
  fulfillment?: StepOutputFulfillmentResponse | null;
}

export interface StepReadiness {
  step_id: string;
  execution_id?: string | null;
  current_status: string;
  outputs: OutputReadinessItem[];
  required_fulfilled: number;
  required_total: number;
  all_required_met: boolean;
  dependencies_met: boolean;
  blocking_dependencies: string[];
  allowed_transitions: string[];
  can_advance: boolean;
}

// ── Agent Conversations ─────────────────────────────────────────────────────

export interface AgentMessageResponse {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  metadata_json?: unknown;
  audit_log_id?: string | null;
  created_at: string;
}

export interface GeneratedDocumentItem {
  document_id: string;
  version_id: string;
  output_name: string;
  content_json: unknown;
}

export interface GenerateDocumentsResponse {
  documents: GeneratedDocumentItem[];
  message: string;
}

export interface AgentConversationResponse {
  id: string;
  tenant_id: string;
  step_execution_id: string;
  agent_name: string;
  status: string;
  messages: AgentMessageResponse[];
  created_at: string;
  updated_at: string;
}

// ── Decisions ───────────────────────────────────────────────────────────────

export interface DecisionResponse {
  id: string;
  tenant_id: string;
  number?: string;
  step_execution_id?: string | null;
  decision_type: string;
  content: string;
  grondslag?: string;
  gremium: string;
  decided_by_name: string;
  decided_by_role?: string;
  decided_at: string;
  valid_until?: string | null;
  motivation?: string | null;
  alternatives?: string | null;
  iso_clause?: string | null;
  supersedes_id?: string | null;
  created_at: string;
}

// ── Risks ───────────────────────────────────────────────────────────────────

export interface RiskResponse {
  id: string;
  tenant_id: string;
  scope_id: string;
  domain: string;
  title: string;
  description: string;
  likelihood: number;
  impact: number;
  risk_score: number;
  financial_impact_eur?: number | null;
  risk_level: string;
  status: string;
  owner_user_id?: string | null;
  cyclus_id?: number | null;
  treatment_decision_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Controls ────────────────────────────────────────────────────────────────

export interface ControlResponse {
  id: string;
  tenant_id: string;
  requirement_id?: string | null;
  title: string;
  description: string;
  domain: string;
  owner_user_id?: string | null;
  implementation_status: string;
  implementation_date?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Scores ──────────────────────────────────────────────────────────────────

export interface SetupScoreResponse {
  id: string;
  tenant_id: string;
  domain: string;
  cyclus_year: number;
  score_pct: number;
  steps_completed: number;
  steps_total: number;
  confirmed_at?: string | null;
  calculated_at: string;
}

export interface GRCScoreResponse {
  id: string;
  tenant_id: string;
  domain: string;
  cyclus_year: number;
  score_pct: number;
  components_json: Record<string, unknown>;
  calculated_at: string;
}

// ── Documents ────────────────────────────────────────────────────────────────

export interface DocumentResponse {
  id: string;
  tenant_id: string;
  step_execution_id?: string | null;
  document_type: string;
  title: string;
  domain?: string | null;
  visibility: string;
  withdrawn_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersionResponse {
  id: string;
  document_id: string;
  version_number: string;
  content_json?: unknown;
  status: string;
  generated_by_agent?: string | null;
  created_by_user_id?: string | null;
  vastgesteld_at?: string | null;
  vastgesteld_by_name?: string | null;
  vastgesteld_by_role?: string | null;
  decision_id?: string | null;
  created_at: string;
}

// ── Scopes ──────────────────────────────────────────────────────────────────

export interface ScopeResponse {
  id: string;
  tenant_id: string;
  parent_id?: string | null;
  name: string;
  scope_type: string;
  domain?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Assessments ─────────────────────────────────────────────────────────────

export interface AssessmentResponse {
  id: string;
  tenant_id: string;
  scope_id?: string | null;
  assessment_type: string;
  domain?: string | null;
  status: string;
  planned_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  cyclus_id?: number | null;
  document_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Findings ────────────────────────────────────────────────────────────────

export interface FindingResponse {
  id: string;
  tenant_id: string;
  assessment_id: string;
  title: string;
  description?: string | null;
  severity: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// ── Corrective Actions ──────────────────────────────────────────────────────

export interface CorrectiveActionResponse {
  id: string;
  tenant_id: string;
  finding_id?: string | null;
  title: string;
  description?: string | null;
  status: string;
  due_date?: string | null;
  owner_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Evidence ────────────────────────────────────────────────────────────────

export interface EvidenceResponse {
  id: string;
  tenant_id: string;
  control_id?: string | null;
  title: string;
  evidence_type: string;
  collected_at?: string | null;
  valid_until?: string | null;
  collected_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Incidents ───────────────────────────────────────────────────────────────

export interface IncidentResponse {
  id: string;
  tenant_id: string;
  title: string;
  incident_type: string;
  severity: string;
  status: string;
  reported_at?: string | null;
  resolved_at?: string | null;
  external_ticket_id?: string | null;
  corrective_action_id?: string | null;
  created_at: string;
  updated_at: string;
}

// ── Knowledge ───────────────────────────────────────────────────────────────

export interface KnowledgeArtifactResponse {
  id: string;
  tenant_id: string;
  title: string;
  content?: string | null;
  artifact_type: string;
  created_at: string;
  updated_at: string;
}
