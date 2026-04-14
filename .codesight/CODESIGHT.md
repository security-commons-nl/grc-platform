# grc-platform — AI Context Map

> **Stack:** fastapi | sqlalchemy | react | python
> **Microservices:** backend, frontend

> 132 routes | 36 models | 32 components | 75 lib files | 29 env vars | 6 middleware | 4% test coverage
> **Token savings:** this file is ~11.000 tokens. Without it, AI exploration would cost ~124.300 tokens. **Saves ~113.200 tokens per conversation.**
> **Last scanned:** 2026-04-14 21:32 — re-run after significant changes

---

# Routes

## CRUD Resources

- **``** GET | GET/:id | PATCH/:id | DELETE/:id
- **`/findings`** GET/:id | PATCH/:id | DELETE/:id → Finding
- **`/corrective-actions`** GET/:id | PATCH/:id | DELETE/:id → Corrective-action
- **`/maturity-profiles`** GET/:id | PATCH/:id | DELETE/:id → Maturity-profile
- **`/setup-scores`** GET/:id | PATCH/:id | DELETE/:id → Setup-score
- **`/grc-scores`** GET/:id | PATCH/:id | DELETE/:id → Grc-score
- **`/requirements`** GET/:id | PATCH/:id | DELETE/:id → Requirement
- **`/mappings`** GET/:id | PATCH/:id | DELETE/:id → Mapping
- **`/ingestions`** GET/:id | PATCH/:id | DELETE/:id → Ingestion
- **`/executions`** GET/:id | PATCH/:id | DELETE/:id → Execution
- **`/regions`** GET/:id | PATCH/:id | DELETE/:id → Region
- **`/users`** GET/:id | PATCH/:id | DELETE/:id → User

## Other Routes

- `POST` `/{agent_name}/conversations` params(agent_name) → out: ConversationResponse [auth, db]
- `GET` `/conversations/{conversation_id}` params(conversation_id) → in: UUID, out: ConversationResponse [auth, db]
- `POST` `/conversations/{conversation_id}/messages` params(conversation_id) → out: ConversationResponse [auth, db]
- `POST` `/conversations/{conversation_id}/feedback` params(conversation_id) → out: ConversationResponse [auth, db]
- `POST` `/conversations/{conversation_id}/generate` params(conversation_id) → out: ConversationResponse [auth, db]
- `GET` `/` params() → out: list [auth, db]
- `POST` `/` params() → in: AssessmentCreate, out: list [auth, db]
- `GET` `/findings/` params() → out: list [auth, db]
- `POST` `/findings/` params() → in: AssessmentCreate, out: list [auth, db]
- `GET` `/corrective-actions/` params() → out: list [auth, db]
- `POST` `/corrective-actions/` params() → in: AssessmentCreate, out: list [auth, db]
- `POST` `/dev-token` params() → in: DevTokenRequest, out: TokenResponse [auth] ✓
- `POST` `/agent-token` params() → in: DevTokenRequest, out: TokenResponse [auth] ✓
- `GET` `/me` params() → in: CurrentUse, out: TokenResponse [auth] ✓
- `GET` `/versions/` params() → out: list [auth, db]
- `GET` `/versions/{version_id}` params(version_id) → out: list [auth, db]
- `GET` `/versions/{version_id}/export` params(version_id) → out: list [auth, db]
- `POST` `/versions/` params() → in: DocumentCreate, out: list [auth, db]
- `GET` `/input-documents/` params() → out: list [auth, db]
- `GET` `/input-documents/{input_doc_id}` params(input_doc_id) → out: list [auth, db]
- `POST` `/input-documents/` params() → in: DocumentCreate, out: list [auth, db]
- `PATCH` `/input-documents/{input_doc_id}` params(input_doc_id) → in: UUID, out: list [auth, db]
- `GET` `/gap-analysis/` params() → out: list [auth, db]
- `GET` `/gap-analysis/{gap_id}` params(gap_id) → out: list [auth, db]
- `POST` `/gap-analysis/` params() → in: DocumentCreate, out: list [auth, db]
- `PATCH` `/gap-analysis/{gap_id}` params(gap_id) → in: UUID, out: list [auth, db]
- `GET` `/links/` params() → out: list [auth, db]
- `POST` `/links/` params() → in: RiskCreate, out: list [auth, db]
- `DELETE` `/links/{risk_id}/{control_id}` params(risk_id, control_id) → in: UUID, out: list [auth, db]
- `GET` `/maturity-profiles/` params() → out: list [auth, db]
- `POST` `/maturity-profiles/` params() → in: MaturityProfileCreate, out: list [auth, db]
- `GET` `/setup-scores/` params() → out: list [auth, db]
- `POST` `/setup-scores/` params() → in: MaturityProfileCreate, out: list [auth, db]
- `GET` `/grc-scores/` params() → out: list [auth, db]
- `POST` `/grc-scores/` params() → in: MaturityProfileCreate, out: list [auth, db]
- `GET` `/requirements/` params() → out: list [auth, db]
- `POST` `/requirements/` params() → in: StandardCreate, out: list [auth, db]
- `GET` `/mappings/` params() → out: list [auth, db]
- `POST` `/mappings/` params() → in: StandardCreate, out: list [auth, db]
- `GET` `/normenkader/` params() → out: list [auth, db]
- `POST` `/normenkader/` params() → in: StandardCreate, out: list [auth, db]
- `PATCH` `/normenkader/{nk_id}` params(nk_id) → in: UUID, out: list [auth, db]
- `DELETE` `/normenkader/{nk_id}` params(nk_id) → in: UUID, out: list [auth, db]
- `GET` `/ingestions/` params() → out: list [auth, db]
- `POST` `/ingestions/` params() → in: StandardCreate, out: list [auth, db]
- `GET` `/dependencies/` params() → out: list [auth, db]
- `POST` `/dependencies/` params() → in: StepCreate, out: list [auth, db]
- `DELETE` `/dependencies/{dep_id}` params(dep_id) → in: UUID, out: list [auth, db]
- `GET` `/executions/` params() → out: list [auth, db]
- `POST` `/executions/` params() → in: StepCreate, out: list [auth, db]
- `GET` `/executions/{execution_id}/readiness` params(execution_id) → out: list [auth, db]
- `GET` `/executions/{execution_id}/fulfillments` params(execution_id) → out: list [auth, db]
- `POST` `/executions/{execution_id}/fulfillments` params(execution_id) → in: StepCreate, out: list [auth, db]
- `DELETE` `/fulfillments/{fulfillment_id}` params(fulfillment_id) → in: UUID, out: list [auth, db]
- `GET` `/regions/` params() → out: list [auth, db]
- `POST` `/regions/` params() → in: TenantCreate, out: list [auth, db]
- `GET` `/users/` params() → out: list [auth, db]
- `POST` `/users/` params() → in: TenantCreate, out: list [auth, db]
- `GET` `/user-tenant-roles/` params() → out: list [auth, db]
- `POST` `/user-tenant-roles/` params() → in: TenantCreate, out: list [auth, db]
- `DELETE` `/user-tenant-roles/{role_id}` params(role_id) → in: UUID, out: list [auth, db]
- `GET` `/user-region-roles/` params() → out: list [auth, db]
- `POST` `/user-region-roles/` params() → in: TenantCreate, out: list [auth, db]
- `DELETE` `/user-region-roles/{role_id}` params(role_id) → in: UUID, out: list [auth, db]

---

# Schema

### Region
- id: UUID (pk, default)
- name: String
- centrum_tenant_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### Tenant
- id: UUID (pk, default)
- name: String
- type: String
- region_id: UUID (fk, nullable)
- is_active: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### User
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- external_id: String (unique)
- name: String
- email: String
- is_active: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### UserTenantRole
- id: UUID (pk, default)
- user_id: UUID (fk)
- tenant_id: UUID (fk)
- role: String
- domain: String (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### UserRegionRole
- id: UUID (pk, default)
- user_id: UUID (fk)
- region_id: UUID (fk)
- role: String
- created_at: DateTime (default)
- updated_at: DateTime (default)

### AIAuditLog
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- user_id: UUID (fk, nullable)
- agent_name: Text
- step_execution_id: UUID (fk, nullable)
- model: Text
- prompt_tokens: Integer (default)
- completion_tokens: Integer (default)
- langfuse_trace_id: Text (nullable)
- feedback: String (nullable)
- feedback_comment: Text (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSStep
- id: UUID (pk, default)
- number: String
- phase: Integer
- name: String
- waarom_nu: Text
- uitleg: Text (nullable)
- voorbeeld_content: JSONB (nullable)
- required_gremium: String
- is_optional: Boolean (default)
- domain: String (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- _relations_: outputs: IMSStepOutput

### IMSStepDependency
- id: UUID (pk, default)
- step_id: UUID (fk)
- depends_on_step_id: UUID (fk)
- dependency_type: String
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSStepExecution
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- step_id: UUID (fk)
- cyclus_id: Integer (nullable)
- status: String
- started_at: DateTime (nullable)
- completed_at: DateTime (nullable)
- skipped: Boolean (default)
- skip_reason: Text (nullable)
- skip_logged_by: Text (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSStepOutput
- id: UUID (pk, default)
- step_id: UUID (fk)
- name: String
- output_type: String
- requirement: String (default)
- sort_order: Integer (default)
- skip_warning: Text (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- _relations_: step: IMSStep

### IMSStepOutputFulfillment
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- step_output_id: UUID (fk)
- step_execution_id: UUID (fk)
- decision_id: UUID (fk, nullable)
- document_id: UUID (fk, nullable)
- fulfilled_at: DateTime (default)
- fulfilled_by: String (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSDecision
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- number: String
- step_execution_id: UUID (fk, nullable)
- decision_type: String
- content: Text
- grondslag: Text
- gremium: String
- decided_by_name: String
- decided_by_role: String
- decided_at: DateTime
- valid_until: Text (nullable)
- motivation: Text (nullable)
- alternatives: Text (nullable)
- iso_clause: String (nullable)
- supersedes_id: UUID (fk, nullable)
- created_at: DateTime (default)

### IMSDocument
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- step_execution_id: UUID (fk, nullable)
- document_type: String
- title: Text
- domain: String (nullable)
- visibility: String
- withdrawn_at: DateTime (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSDocumentVersion
- id: UUID (pk, default)
- document_id: UUID (fk)
- version_number: String
- content_json: JSONB (nullable)
- status: String
- generated_by_agent: Text (nullable)
- created_by_user_id: UUID (fk, nullable)
- vastgesteld_at: DateTime (nullable)
- vastgesteld_by_name: String (nullable)
- vastgesteld_by_role: String (nullable)
- decision_id: UUID (fk, nullable)
- created_at: DateTime (default)

### IMSStepInputDocument
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- step_execution_id: UUID (fk)
- source_type: String
- storage_path: Text
- status: String
- uploaded_at: DateTime
- uploaded_by_user_id: UUID (fk)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSGapAnalysisResult
- id: UUID (pk, default)
- input_document_id: UUID (fk)
- tenant_id: UUID (fk)
- field_reference: Text
- ai_suggestion: Text
- uncertainty: Boolean (default)
- validated: Boolean (default)
- validated_at: DateTime (nullable)
- validated_by_user_id: UUID (fk, nullable)
- created_at: DateTime (default)

### IMSStandard
- id: UUID (pk, default)
- name: String
- version: String
- published_at: Date (nullable)
- status: String
- superseded_by_id: UUID (fk, nullable)
- domain: String
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSRequirement
- id: UUID (pk, default)
- standard_id: UUID (fk)
- code: String
- title: String
- description: Text
- domain: String
- is_mandatory: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSRequirementMapping
- id: UUID (pk, default)
- source_requirement_id: UUID (fk)
- target_requirement_id: UUID (fk)
- norm_version_source: Text
- confidence_score: Numeric
- created_by: String
- verified: Boolean (default)
- orphaned: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSTenantNormenkader
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- standard_id: UUID (fk)
- adopted_at: Date
- is_active: Boolean (default)
- decision_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSStandardIngestion
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- uploaded_by_user_id: UUID (fk)
- source_type: String
- source_path: Text
- detected_standard_id: UUID (fk, nullable)
- detected_version: String (nullable)
- status: String
- parsed_requirements_json: JSONB (nullable)
- reviewed_at: DateTime (nullable)
- reviewed_by_user_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSScope
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- type: String
- name: Text
- parent_id: UUID (fk, nullable)
- domain: String (nullable)
- is_critical: Boolean (default)
- verwerkt_pii: Boolean (default)
- ext_verwerking_ref: Text (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSRisk
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- scope_id: UUID (fk)
- domain: String
- title: Text
- description: Text
- likelihood: Integer
- impact: Integer
- risk_score: Integer
- financial_impact_eur: Numeric (nullable)
- risk_level: String
- status: String
- owner_user_id: UUID (fk, nullable)
- cyclus_id: Integer (nullable)
- treatment_decision_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSControl
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- requirement_id: UUID (fk, nullable)
- title: Text
- description: Text
- domain: String
- owner_user_id: UUID (fk, nullable)
- implementation_status: String
- implementation_date: Date (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSRiskControlLink
- risk_id: UUID (fk, pk)
- control_id: UUID (fk, pk)

### IMSAssessment
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- assessment_type: String
- scope_id: UUID (fk, nullable)
- domain: String (nullable)
- planned_at: Date
- started_at: DateTime (nullable)
- completed_at: DateTime (nullable)
- status: String
- cyclus_id: Integer (nullable)
- document_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSFinding
- id: UUID (pk, default)
- assessment_id: UUID (fk)
- tenant_id: UUID (fk)
- title: Text
- description: Text
- severity: String
- status: String
- requirement_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSCorrectiveAction
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- finding_id: UUID (fk, nullable)
- risk_id: UUID (fk, nullable)
- title: Text
- description: Text
- owner_user_id: UUID (fk, nullable)
- due_date: Date
- status: String
- completed_at: DateTime (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSEvidence
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- control_id: UUID (fk)
- title: Text
- evidence_type: String
- storage_path: Text
- collected_at: Date
- valid_until: Date (nullable)
- collected_by_user_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSIncident
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- title: Text
- incident_type: String
- severity: String
- status: String
- reported_at: DateTime
- resolved_at: DateTime (nullable)
- external_ticket_id: Text (nullable)
- corrective_action_id: UUID (fk, nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSMaturityProfile
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- domain: String
- existing_registers: String
- existing_analyses: String
- coordination_capacity: String
- linemanagement_structure: String
- recommended_option: String (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSSetupScore
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- domain: String
- cyclus_year: Integer
- score_pct: Numeric
- steps_completed: Integer
- steps_total: Integer
- confirmed_at: DateTime (nullable)
- calculated_at: DateTime
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSGRCScore
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- domain: String
- cyclus_year: Integer
- score_pct: Numeric
- components_json: JSONB
- calculated_at: DateTime
- created_at: DateTime (default)
- updated_at: DateTime (default)

### IMSKnowledgeChunk
- id: UUID (pk, default)
- layer: String
- tenant_id: UUID (fk, nullable)
- source_type: String
- source_id: UUID (nullable)
- chunk_index: Integer
- content: Text
- embedding: Any
- model_used: Text
- created_at: DateTime (default)
- updated_at: DateTime (default)

### AgentConversation
- id: UUID (pk, default)
- tenant_id: UUID (fk)
- step_execution_id: UUID (fk)
- agent_name: String
- status: String (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- _relations_: messages: AgentMessage

### AgentMessage
- id: UUID (pk, default)
- conversation_id: UUID (fk)
- role: String
- content: Text
- metadata_json: JSONB (nullable)
- audit_log_id: UUID (fk, nullable)
- created_at: DateTime (default)
- _relations_: conversation: AgentConversation

---

# Components

- **GebruikersPage** [client] — `frontend\src\app\(protected)\admin\gebruikers\page.tsx`
- **TenantPage** [client] — `frontend\src\app\(protected)\admin\tenant\page.tsx`
- **AssessmentsPage** [client] — `frontend\src\app\(protected)\beheer\assessments\page.tsx`
- **BevindingenPage** [client] — `frontend\src\app\(protected)\beheer\bevindingen\page.tsx`
- **BewijsPage** [client] — `frontend\src\app\(protected)\beheer\bewijs\page.tsx`
- **ControlsPage** [client] — `frontend\src\app\(protected)\beheer\controls\page.tsx`
- **IncidentenPage** [client] — `frontend\src\app\(protected)\beheer\incidenten\page.tsx`
- **BeheerDashboardPage** [client] — `frontend\src\app\(protected)\beheer\page.tsx`
- **RisicosPage** [client] — `frontend\src\app\(protected)\beheer\risicos\page.tsx`
- **BesluitenPage** [client] — `frontend\src\app\(protected)\inrichten\besluiten\page.tsx`
- **DocumentenPage** [client] — `frontend\src\app\(protected)\inrichten\documenten\page.tsx`
- **InrichtenOverzichtPage** [client] — `frontend\src\app\(protected)\inrichten\page.tsx`
- **StepDetailPage** [client] — props: params — `frontend\src\app\(protected)\inrichten\[stepId]\page.tsx`
- **ProtectedLayout** [client] — `frontend\src\app\(protected)\layout.tsx`
- **RootLayout** — `frontend\src\app\layout.tsx`
- **LoginPage** [client] — `frontend\src\app\login\page.tsx`
- **RootPage** [client] — `frontend\src\app\page.tsx`
- **ChatIsland** [client] — props: stepNumber, executionId — `frontend\src\components\ai\chat-island.tsx`
- **ChatPanel** [client] — props: conversation, onClose, onUpdate — `frontend\src\components\ai\chat-panel.tsx`
- **RiskMatrix** [client] — props: mode, value — `frontend\src\components\beheer\risk-matrix.tsx`
- **DecisionLogTable** [client] — props: decisions — `frontend\src\components\inrichten\decision-log-table.tsx`
- **DocumentVersionList** [client] — props: documents — `frontend\src\components\inrichten\document-version-list.tsx`
- **StepCard** [client] — props: step, execution, isBlocked, onClick — `frontend\src\components\inrichten\step-card.tsx`
- **StepProgressGrid** [client] — props: steps, executions, dependencies — `frontend\src\components\inrichten\step-progress-grid.tsx`
- **Header** [client] — props: title — `frontend\src\components\layout\header.tsx`
- **PageWrapper** — props: title, description, actions — `frontend\src\components\layout\page-wrapper.tsx`
- **ScoreBar** — props: value, label, size — `frontend\src\components\shared\score-bar.tsx`
- **StatusBadge** — props: status — `frontend\src\components\shared\status-badge.tsx`
- **WaaromTooltip** — props: text — `frontend\src\components\shared\waarom-tooltip.tsx`
- **EmptyState** — props: icon, title, description, actionLabel, onAction — `frontend\src\components\ui\empty-state.tsx`
- **LoadingSkeleton** — props: className, lines — `frontend\src\components\ui\loading-skeleton.tsx`
- **AuthProvider** [client] — `frontend\src\providers\auth-provider.tsx`

---

# Libraries

- `backend\alembic\env.py` — function run_migrations_offline: () -> None, function run_migrations_online: () -> None
- `backend\alembic\versions\001_initial_schema.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\002_enable_rls.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\003_seed_reference_data.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\004_step_outputs.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\005_seed_step_outputs.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\006_agent_conversations.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\007_rename_terminology.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\008_step_uitleg_voorbeeld.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\alembic\versions\009_decision_outputs_recommended.py` — function upgrade: () -> None, function downgrade: () -> None
- `backend\app\api\v1\endpoints\auth.py`
  - function create_dev_token: (data)
  - class DevTokenRequest
  - class AgentTokenRequest
  - class TokenResponse
- `backend\app\api\v1\endpoints\risks.py` — function calculate_risk_level: (score) -> str
- `backend\app\core\auth.py`
  - function create_token: (data, expires_delta) -> str
  - function decode_token: (token) -> TokenData
  - function require_role: (*roles)
  - class TokenData
  - class CurrentUser
- `backend\app\core\config.py` — class Settings
- `backend\app\core\db.py` — function get_db: ()
- `backend\app\main.py` — function lifespan: (app)
- `backend\app\models\core_models.py`
  - class Base
  - class TenantType
  - class TenantRoleEnum
  - class RegionRoleEnum
  - class DomainEnum
  - class AIFeedbackEnum
  - _...73 more_
- `backend\app\schemas\agents.py`
  - class ConversationStartRequest
  - class MessageCreate
  - class MessageResponse
  - class ConversationResponse
  - class GeneratedDocumentItem
  - class GenerateDocumentsResponse
  - _...1 more_
- `backend\app\schemas\assessments.py`
  - class AssessmentCreate
  - class AssessmentUpdate
  - class AssessmentResponse
  - class FindingCreate
  - class FindingUpdate
  - class FindingResponse
  - _...3 more_
- `backend\app\schemas\controls.py`
  - class ControlCreate
  - class ControlUpdate
  - class ControlResponse
- `backend\app\schemas\decisions.py` — class DecisionCreate, class DecisionResponse
- `backend\app\schemas\documents.py`
  - class DocumentCreate
  - class DocumentUpdate
  - class DocumentResponse
  - class DocumentVersionCreate
  - class DocumentVersionResponse
  - class StepInputDocumentCreate
  - _...5 more_
- `backend\app\schemas\evidence.py`
  - class EvidenceCreate
  - class EvidenceUpdate
  - class EvidenceResponse
- `backend\app\schemas\incidents.py`
  - class IncidentCreate
  - class IncidentUpdate
  - class IncidentResponse
- `backend\app\schemas\knowledge.py`
  - class KnowledgeChunkCreate
  - class KnowledgeChunkUpdate
  - class KnowledgeChunkResponse
- `backend\app\schemas\risks.py`
  - class RiskCreate
  - class RiskUpdate
  - class RiskResponse
  - class RiskControlLinkCreate
  - class RiskControlLinkResponse
- `backend\app\schemas\scopes.py`
  - class ScopeCreate
  - class ScopeUpdate
  - class ScopeResponse
- `backend\app\schemas\scores.py`
  - class MaturityProfileCreate
  - class MaturityProfileUpdate
  - class MaturityProfileResponse
  - class SetupScoreCreate
  - class SetupScoreUpdate
  - class SetupScoreResponse
  - _...3 more_
- `backend\app\schemas\standards.py`
  - class StandardCreate
  - class StandardUpdate
  - class StandardResponse
  - class RequirementCreate
  - class RequirementUpdate
  - class RequirementResponse
  - _...9 more_
- `backend\app\schemas\steps.py`
  - class StepCreate
  - class StepUpdate
  - class StepResponse
  - class StepDependencyCreate
  - class StepDependencyResponse
  - class StepExecutionCreate
  - _...7 more_
- `backend\app\schemas\tenants.py`
  - class TenantCreate
  - class TenantUpdate
  - class TenantResponse
  - class RegionCreate
  - class RegionUpdate
  - class RegionResponse
  - _...7 more_
- `backend\app\services\agents\base_agent.py` — class BaseAgent
- `backend\app\services\agents\commitment_agent.py` — class CommitmentAgent
- `backend\app\services\agents\context_agent.py` — class ContextAgent
- `backend\app\services\agents\controls_agent.py` — class ControlsAgent
- `backend\app\services\agents\gap_agent.py` — class GapAgent
- `backend\app\services\agents\governance_agent.py` — class GovernanceAgent
- `backend\app\services\agents\register_agent.py` — class RegisterAgent
- `backend\app\services\agents\registry.py` — function get_agent_for_step: (step_number) -> BaseAgent | None, function get_agent_by_name: (agent_name) -> BaseAgent | None
- `backend\app\services\agents\scope_agent.py` — class ScopeAgent
- `backend\app\services\document_export.py` — function content_json_to_markdown: (content_json) -> str, function content_json_to_html: (content_json) -> str
- `backend\app\services\document_processing\gap_analysis.py` — function analyze_document: (document_text, step_execution_id, input_document_id, tenant_id, db) -> list[IMSGapAnalysisResult]
- `backend\app\services\document_processing\parser.py`
  - function parse_pdf: (file_path) -> str
  - function parse_docx: (file_path) -> str
  - function parse_markdown: (file_path) -> str
  - function parse_document: (file_path, source_type) -> str
- `backend\app\services\llm_client.py`
  - function get_client: () -> AsyncOpenAI
  - function chat_completion: (messages, model, temperature, max_tokens) -> dict
  - function chat_completion_stream: (messages, model, temperature, max_tokens) -> AsyncGenerator[str, None]
  - function create_embedding: (text, model) -> list[float]
- `backend\app\services\rag\embedding_service.py` — function chunk_text: (text, chunk_size, overlap) -> list[str], function generate_embedding: (text) -> list[float]
- `backend\app\services\rag\ingestion_service.py` — function ingest_text: (content, source_type, source_id, tenant_id, layer, model_used, db) -> list[IMSKnowledgeChunk]
- `backend\app\services\rag\retrieval_service.py` — function search_knowledge: (query, tenant_id, db, layer, top_k) -> list[IMSKnowledgeChunk]
- `backend\tests\conftest.py`
  - function make_token: (user_id, tenant_id, role, domain, token_type, agent_name)
  - function engine: ()
  - function clean_tables: (engine)
  - function client: (engine)
  - function admin_token: ()
  - function test_tenant: (client, admin_token)
  - _...4 more_
- `backend\tests\test_agents.py`
  - function test_start_conversation: (client, test_tenant, tenant_token)
  - function test_start_conversation_resume_existing: (client, test_tenant, tenant_token)
  - function test_start_conversation_wrong_agent: (client, test_tenant, tenant_token)
  - function test_start_conversation_unknown_agent: (client, test_tenant, tenant_token)
  - function test_get_conversation: (client, test_tenant, tenant_token)
  - function test_get_conversation_not_found: (client, tenant_token)
  - _...7 more_
- `backend\tests\test_assessments.py`
  - function test_create_assessment: (client, test_tenant, tenant_token)
  - function test_create_assessment_types: (client, test_tenant, tenant_token)
  - function test_list_assessments: (client, test_tenant, tenant_token)
  - function test_create_finding: (client, test_tenant, tenant_token)
  - function test_create_corrective_action_from_finding: (client, test_tenant, tenant_token)
  - function test_create_corrective_action_from_risk: (client, test_tenant, tenant_token)
  - _...1 more_
- `backend\tests\test_auth.py`
  - function test_dev_token: (client)
  - function test_me_authenticated: (client)
  - function test_me_unauthenticated: (client)
  - function test_role_hierarchy: (client, test_tenant, tenant_token)
  - function test_viewer_cannot_create: (client, test_tenant, viewer_token)
  - function test_agent_token_requires_admin: (client, test_tenant)
  - _...1 more_
- `backend\tests\test_controls.py`
  - function test_create_control: (client, test_tenant, tenant_token)
  - function test_create_control_with_requirement: (client, test_tenant, tenant_token)
  - function test_update_implementation_status: (client, test_tenant, tenant_token)
  - function test_list_controls: (client, test_tenant, tenant_token)
  - function test_delete_control_cascades_links: (client, test_tenant, tenant_token)
  - function test_control_not_found: (client, admin_token)
- `backend\tests\test_decisions.py`
  - function test_create_decision: (client, test_tenant, tenant_token)
  - function test_create_restrisico_acceptatie_sims: (client, test_tenant, tenant_token)
  - function test_reject_restrisico_wrong_gremium: (client, test_tenant, tenant_token)
  - function test_reject_beleidsafwijking_wrong_gremium: (client, test_tenant, tenant_token)
  - function test_decision_immutability_no_patch: (client, test_tenant, tenant_token)
  - function test_decision_immutability_no_delete: (client, test_tenant, tenant_token)
  - _...3 more_
- `backend\tests\test_documents.py`
  - function test_create_document: (client, test_tenant, tenant_token)
  - function test_list_documents: (client, test_tenant, tenant_token)
  - function test_add_document_version_immutable: (client, test_tenant, tenant_token)
  - function test_list_document_versions: (client, test_tenant, tenant_token)
  - function test_create_step_input_document: (client, test_tenant, test_user, tenant_token)
  - function test_create_gap_analysis_result: (client, test_tenant, test_user, tenant_token)
  - _...1 more_
- `backend\tests\test_evidence.py`
  - function test_create_evidence: (client, test_tenant, tenant_token)
  - function test_create_evidence_with_valid_until: (client, test_tenant, tenant_token)
  - function test_list_evidence_by_control: (client, test_tenant, tenant_token)
  - function test_evidence_not_found: (client, admin_token)
- `backend\tests\test_incidents.py`
  - function test_create_incident: (client, test_tenant, tenant_token)
  - function test_incident_with_corrective_action: (client, test_tenant, tenant_token)
  - function test_update_incident_status: (client, test_tenant, tenant_token)
  - function test_list_incidents: (client, test_tenant, tenant_token)
  - function test_incident_not_found: (client, admin_token)
- `backend\tests\test_knowledge.py`
  - function test_create_knowledge_chunk: (client, test_tenant, tenant_token)
  - function test_create_normatief_chunk_no_tenant: (client, admin_token)
  - function test_list_knowledge_filter_layer: (client, test_tenant, tenant_token)
  - function test_knowledge_chunk_not_found: (client, admin_token)
  - function test_update_knowledge_chunk: (client, test_tenant, tenant_token)
  - function test_delete_knowledge_chunk: (client, test_tenant, tenant_token)
- `backend\tests\test_risks.py`
  - function test_create_risk_auto_score: (client, test_tenant, tenant_token)
  - function test_risk_level_groen: (client, test_tenant, tenant_token)
  - function test_risk_level_geel: (client, test_tenant, tenant_token)
  - function test_risk_level_rood: (client, test_tenant, tenant_token)
  - function test_update_risk_recalculates_level: (client, test_tenant, tenant_token)
  - function test_list_risks_filter: (client, test_tenant, tenant_token)
  - _...3 more_
- `backend\tests\test_scopes.py`
  - function test_create_scope_organisatie: (client, test_tenant, tenant_token)
  - function test_create_scope_hierarchy: (client, test_tenant, tenant_token)
  - function test_scope_verwerkt_pii: (client, test_tenant, tenant_token)
  - function test_list_scopes_filter: (client, test_tenant, tenant_token)
  - function test_scope_not_found: (client, admin_token)
- `backend\tests\test_scores.py`
  - function test_create_maturity_profile: (client, test_tenant, tenant_token)
  - function test_list_maturity_profiles: (client, test_tenant, tenant_token)
  - function test_create_setup_score: (client, test_tenant, tenant_token)
  - function test_list_setup_scores: (client, test_tenant, tenant_token)
  - function test_create_grc_score: (client, test_tenant, tenant_token)
  - function test_list_grc_scores: (client, test_tenant, tenant_token)
- `backend\tests\test_seed_data.py`
  - function test_steps_are_seeded: (client)
  - function test_steps_have_correct_phases: (client)
  - function test_fase3_steps_are_optional: (client)
  - function test_step_dependencies_exist: (client)
  - function test_standards_are_seeded: (client)
  - function test_step_1_details: (client)
- `backend\tests\test_standards.py`
  - function test_create_standard: (client, admin_token)
  - function test_list_standards: (client, admin_token)
  - function test_create_requirement: (client, admin_token)
  - function test_create_requirement_mapping: (client, admin_token)
  - function test_create_tenant_normenkader: (client, test_tenant, tenant_token)
  - function test_create_standard_ingestion: (client, test_tenant, test_user, tenant_token)
  - _...1 more_
- `backend\tests\test_steps.py`
  - function test_create_step: (client, admin_token)
  - function test_list_steps: (client, admin_token)
  - function test_list_steps_filter_phase: (client, admin_token)
  - function test_create_step_execution: (client, test_tenant, tenant_token)
  - function test_step_execution_valid_transition: (client, test_tenant, tenant_token)
  - function test_step_execution_invalid_transition: (client, test_tenant, tenant_token)
  - _...2 more_
- `backend\tests\test_step_outputs.py`
  - function test_list_steps_includes_outputs: (client, admin_token)
  - function test_get_step_includes_outputs: (client, admin_token)
  - function test_readiness_no_fulfillments: (client, test_tenant, tenant_token)
  - function test_readiness_not_found: (client, admin_token)
  - function test_fulfillment_create_and_list: (client, test_tenant, tenant_token)
  - function test_fulfillment_requires_exactly_one_link: (client, test_tenant, tenant_token)
  - _...4 more_
- `backend\tests\test_tenants.py`
  - function test_create_tenant: (client, admin_token)
  - function test_create_tenant_centrum: (client, admin_token)
  - function test_list_tenants: (client, test_tenant, tenant_token)
  - function test_get_tenant: (client, test_tenant, tenant_token)
  - function test_tenant_not_found: (client, admin_token)
  - function test_update_tenant: (client, test_tenant, tenant_token)
  - _...7 more_
- `frontend\src\lib\api-client.ts` — class ApiError, const api
- `frontend\src\lib\auth.ts`
  - function getToken: () => string | null
  - function setToken: (token) => void
  - function clearToken: () => void
  - function getUser: () => CurrentUser | null
  - function isAuthenticated: () => boolean
- `frontend\src\lib\constants.ts`
  - function hasMinRole: (userRole, requiredRole) => boolean
  - const API_BASE_URL
  - const ROLE_HIERARCHY: Record<string, number>
  - const ROLE_LABELS: Record<string, string>
  - const STATUS_LABELS: Record<string, string>
  - const STATUS_COLORS: Record<string, string>
- `frontend\src\lib\format-error.ts` — function formatApiError: (body) => string
- `frontend\src\lib\hooks\use-api.ts` — function useApi: (key, path?) => void
- `frontend\src\lib\hooks\use-controls.ts` — function useControls: () => void
- `frontend\src\lib\hooks\use-risks.ts` — function useRisks: () => void
- `frontend\src\lib\hooks\use-scores.ts` — function useSetupScores: () => void
- `frontend\src\lib\hooks\use-steps.ts`
  - function useSteps: () => void
  - function useStepExecutions: () => void
  - function useStepDependencies: () => void
- `generate-docs.py`
  - function get_steps_and_outputs: ()
  - function get_outputs: ()
  - function get_agents: ()
  - function get_models: ()
  - function get_routes: ()
  - function get_migrations: ()
  - _...5 more_

---

# Config

## Environment Variables

- `AI_API_BASE` (has default) — .env.example
- `AI_API_KEY` **required** — .env.example
- `AI_EMBEDDING_MODEL` (has default) — .env.example
- `AI_MAX_TOKENS` (has default) — .env.example
- `AI_MODEL_NAME` (has default) — .env.example
- `AI_TEMPERATURE` (has default) — .env.example
- `ALLOWED_ORIGINS` (has default) — .env.example
- `API_URL` (has default) — .env
- `DEFAULT_TENANT_ID` (has default) — .env.example
- `ENVIRONMENT` (has default) — .env.example
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (has default) — .env.example
- `JWT_ALGORITHM` (has default) — .env.example
- `JWT_EXPIRE_MINUTES` (has default) — .env
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` (has default) — .env.example
- `JWT_SECRET` (has default) — .env
- `JWT_SECRET_KEY` (has default) — .env.example
- `LANGFUSE_HOST` **required** — .env.example
- `LANGFUSE_PUBLIC_KEY` **required** — .env.example
- `LANGFUSE_SECRET_KEY` **required** — .env.example
- `NEXT_PUBLIC_API_URL` **required** — frontend\src\lib\constants.ts
- `PGADMIN_DEFAULT_EMAIL` (has default) — .env
- `PGADMIN_DEFAULT_PASSWORD` (has default) — .env
- `POSTGRES_APP_PASSWORD` (has default) — .env
- `POSTGRES_APP_USER` (has default) — .env
- `POSTGRES_DB` (has default) — .env.example
- `POSTGRES_PASSWORD` (has default) — .env.example
- `POSTGRES_PORT` (has default) — .env.example
- `POSTGRES_SERVER` (has default) — .env.example
- `POSTGRES_USER` (has default) — .env.example

## Config Files

- `.env.example`
- `docker-compose.yml`
- `frontend\next.config.ts`

---

# Middleware

## auth
- auth — `backend\app\api\v1\endpoints\auth.py`
- auth — `backend\app\core\auth.py`
- auth.spec — `frontend\e2e\auth.spec.ts`
- auth — `frontend\src\lib\auth.ts`
- auth-provider — `frontend\src\providers\auth-provider.tsx`

## validation
- generate-docs — `generate-docs.py`

---

# Dependency Graph

## Most Imported Files (change these carefully)

- `frontend\src\lib\hooks\use-api.ts` — imported by **4** files
- `frontend\src\components\inrichten\step-card.tsx` — imported by **1** files
- `frontend\src\components\ui\button.tsx` — imported by **1** files
- `frontend\src\lib\auth.ts` — imported by **1** files
- `frontend\src\lib\constants.ts` — imported by **1** files
- `frontend\src\lib\api-types.ts` — imported by **1** files

## Import Map (who imports what)

- `frontend\src\lib\hooks\use-api.ts` ← `frontend\src\lib\hooks\use-controls.ts`, `frontend\src\lib\hooks\use-risks.ts`, `frontend\src\lib\hooks\use-scores.ts`, `frontend\src\lib\hooks\use-steps.ts`
- `frontend\src\components\inrichten\step-card.tsx` ← `frontend\src\components\inrichten\step-progress-grid.tsx`
- `frontend\src\components\ui\button.tsx` ← `frontend\src\components\ui\empty-state.tsx`
- `frontend\src\lib\auth.ts` ← `frontend\src\lib\api-client.ts`
- `frontend\src\lib\constants.ts` ← `frontend\src\lib\api-client.ts`
- `frontend\src\lib\api-types.ts` ← `frontend\src\lib\auth.ts`

---

# Test Coverage

> **4%** of routes and models are covered by tests
> 20 test files found

## Covered Routes

- POST:/dev-token
- POST:/agent-token
- GET:/me
- GET:

## Covered Models

- Region
- Tenant
- User

---

_Generated by [codesight](https://github.com/Houseofmvps/codesight) — see your codebase clearly_