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

export interface StepResponse {
  id: string;
  number: string;
  phase: number;
  name: string;
  waarom_nu?: string;
  required_gremium: string;
  is_optional: boolean;
  domain?: string | null;
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
