# Database

> **Navigation aid.** Schema shapes and field types extracted via AST. Read the actual schema source files before writing migrations or query logic.

**sqlalchemy** — 36 models

### Region

pk: `id` (UUID) · fk: centrum_tenant_id

- `id`: UUID _(pk, default)_
- `name`: String
- `centrum_tenant_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### Tenant

pk: `id` (UUID) · fk: region_id

- `id`: UUID _(pk, default)_
- `name`: String
- `type`: String
- `region_id`: UUID _(fk, nullable)_
- `is_active`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### User

pk: `id` (UUID) · fk: tenant_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `external_id`: String _(unique)_
- `name`: String
- `email`: String
- `is_active`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### UserTenantRole

pk: `id` (UUID) · fk: user_id, tenant_id

- `id`: UUID _(pk, default)_
- `user_id`: UUID _(fk)_
- `tenant_id`: UUID _(fk)_
- `role`: String
- `domain`: String _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### UserRegionRole

pk: `id` (UUID) · fk: user_id, region_id

- `id`: UUID _(pk, default)_
- `user_id`: UUID _(fk)_
- `region_id`: UUID _(fk)_
- `role`: String
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### AIAuditLog

pk: `id` (UUID) · fk: tenant_id, user_id, step_execution_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `user_id`: UUID _(fk, nullable)_
- `agent_name`: Text
- `step_execution_id`: UUID _(fk, nullable)_
- `model`: Text
- `prompt_tokens`: Integer _(default)_
- `completion_tokens`: Integer _(default)_
- `langfuse_trace_id`: Text _(nullable)_
- `feedback`: String _(nullable)_
- `feedback_comment`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSStep

pk: `id` (UUID)

- `id`: UUID _(pk, default)_
- `number`: String
- `phase`: Integer
- `name`: String
- `waarom_nu`: Text
- `uitleg`: Text _(nullable)_
- `voorbeeld_content`: JSONB _(nullable)_
- `required_gremium`: String
- `is_optional`: Boolean _(default)_
- `domain`: String _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- _relations_: outputs: IMSStepOutput

### IMSStepDependency

pk: `id` (UUID) · fk: step_id, depends_on_step_id

- `id`: UUID _(pk, default)_
- `step_id`: UUID _(fk)_
- `depends_on_step_id`: UUID _(fk)_
- `dependency_type`: String
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSStepExecution

pk: `id` (UUID) · fk: tenant_id, step_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `step_id`: UUID _(fk)_
- `cyclus_id`: Integer _(nullable)_
- `status`: String
- `started_at`: DateTime _(nullable)_
- `completed_at`: DateTime _(nullable)_
- `skipped`: Boolean _(default)_
- `skip_reason`: Text _(nullable)_
- `skip_logged_by`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSStepOutput

pk: `id` (UUID) · fk: step_id

- `id`: UUID _(pk, default)_
- `step_id`: UUID _(fk)_
- `name`: String
- `output_type`: String
- `requirement`: String _(default)_
- `sort_order`: Integer _(default)_
- `skip_warning`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- _relations_: step: IMSStep

### IMSStepOutputFulfillment

pk: `id` (UUID) · fk: tenant_id, step_output_id, step_execution_id, decision_id, document_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `step_output_id`: UUID _(fk)_
- `step_execution_id`: UUID _(fk)_
- `decision_id`: UUID _(fk, nullable)_
- `document_id`: UUID _(fk, nullable)_
- `fulfilled_at`: DateTime _(default)_
- `fulfilled_by`: String _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSDecision

pk: `id` (UUID) · fk: tenant_id, step_execution_id, supersedes_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `number`: String
- `step_execution_id`: UUID _(fk, nullable)_
- `decision_type`: String
- `content`: Text
- `grondslag`: Text
- `gremium`: String
- `decided_by_name`: String
- `decided_by_role`: String
- `decided_at`: DateTime
- `valid_until`: Text _(nullable)_
- `motivation`: Text _(nullable)_
- `alternatives`: Text _(nullable)_
- `iso_clause`: String _(nullable)_
- `supersedes_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_

### IMSDocument

pk: `id` (UUID) · fk: tenant_id, step_execution_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `step_execution_id`: UUID _(fk, nullable)_
- `document_type`: String
- `title`: Text
- `domain`: String _(nullable)_
- `visibility`: String
- `withdrawn_at`: DateTime _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSDocumentVersion

pk: `id` (UUID) · fk: document_id, created_by_user_id, decision_id

- `id`: UUID _(pk, default)_
- `document_id`: UUID _(fk)_
- `version_number`: String
- `content_json`: JSONB _(nullable)_
- `status`: String
- `generated_by_agent`: Text _(nullable)_
- `created_by_user_id`: UUID _(fk, nullable)_
- `vastgesteld_at`: DateTime _(nullable)_
- `vastgesteld_by_name`: String _(nullable)_
- `vastgesteld_by_role`: String _(nullable)_
- `decision_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_

### IMSStepInputDocument

pk: `id` (UUID) · fk: tenant_id, step_execution_id, uploaded_by_user_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `step_execution_id`: UUID _(fk)_
- `source_type`: String
- `storage_path`: Text
- `status`: String
- `uploaded_at`: DateTime
- `uploaded_by_user_id`: UUID _(fk)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSGapAnalysisResult

pk: `id` (UUID) · fk: input_document_id, tenant_id, validated_by_user_id

- `id`: UUID _(pk, default)_
- `input_document_id`: UUID _(fk)_
- `tenant_id`: UUID _(fk)_
- `field_reference`: Text
- `ai_suggestion`: Text
- `uncertainty`: Boolean _(default)_
- `validated`: Boolean _(default)_
- `validated_at`: DateTime _(nullable)_
- `validated_by_user_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_

### IMSStandard

pk: `id` (UUID) · fk: superseded_by_id

- `id`: UUID _(pk, default)_
- `name`: String
- `version`: String
- `published_at`: Date _(nullable)_
- `status`: String
- `superseded_by_id`: UUID _(fk, nullable)_
- `domain`: String
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSRequirement

pk: `id` (UUID) · fk: standard_id

- `id`: UUID _(pk, default)_
- `standard_id`: UUID _(fk)_
- `code`: String
- `title`: String
- `description`: Text
- `domain`: String
- `is_mandatory`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSRequirementMapping

pk: `id` (UUID) · fk: source_requirement_id, target_requirement_id

- `id`: UUID _(pk, default)_
- `source_requirement_id`: UUID _(fk)_
- `target_requirement_id`: UUID _(fk)_
- `norm_version_source`: Text
- `confidence_score`: Numeric
- `created_by`: String
- `verified`: Boolean _(default)_
- `orphaned`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSTenantNormenkader

pk: `id` (UUID) · fk: tenant_id, standard_id, decision_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `standard_id`: UUID _(fk)_
- `adopted_at`: Date
- `is_active`: Boolean _(default)_
- `decision_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSStandardIngestion

pk: `id` (UUID) · fk: tenant_id, uploaded_by_user_id, detected_standard_id, reviewed_by_user_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `uploaded_by_user_id`: UUID _(fk)_
- `source_type`: String
- `source_path`: Text
- `detected_standard_id`: UUID _(fk, nullable)_
- `detected_version`: String _(nullable)_
- `status`: String
- `parsed_requirements_json`: JSONB _(nullable)_
- `reviewed_at`: DateTime _(nullable)_
- `reviewed_by_user_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSScope

pk: `id` (UUID) · fk: tenant_id, parent_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `type`: String
- `name`: Text
- `parent_id`: UUID _(fk, nullable)_
- `domain`: String _(nullable)_
- `is_critical`: Boolean _(default)_
- `verwerkt_pii`: Boolean _(default)_
- `ext_verwerking_ref`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSRisk

pk: `id` (UUID) · fk: tenant_id, scope_id, owner_user_id, treatment_decision_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `scope_id`: UUID _(fk)_
- `domain`: String
- `title`: Text
- `description`: Text
- `likelihood`: Integer
- `impact`: Integer
- `risk_score`: Integer
- `financial_impact_eur`: Numeric _(nullable)_
- `risk_level`: String
- `status`: String
- `owner_user_id`: UUID _(fk, nullable)_
- `cyclus_id`: Integer _(nullable)_
- `treatment_decision_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSControl

pk: `id` (UUID) · fk: tenant_id, requirement_id, owner_user_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `requirement_id`: UUID _(fk, nullable)_
- `title`: Text
- `description`: Text
- `domain`: String
- `owner_user_id`: UUID _(fk, nullable)_
- `implementation_status`: String
- `implementation_date`: Date _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSRiskControlLink

pk: `risk_id` (UUID) · fk: risk_id, control_id

- `risk_id`: UUID _(fk, pk)_
- `control_id`: UUID _(fk, pk)_

### IMSAssessment

pk: `id` (UUID) · fk: tenant_id, scope_id, document_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `assessment_type`: String
- `scope_id`: UUID _(fk, nullable)_
- `domain`: String _(nullable)_
- `planned_at`: Date
- `started_at`: DateTime _(nullable)_
- `completed_at`: DateTime _(nullable)_
- `status`: String
- `cyclus_id`: Integer _(nullable)_
- `document_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSFinding

pk: `id` (UUID) · fk: assessment_id, tenant_id, requirement_id

- `id`: UUID _(pk, default)_
- `assessment_id`: UUID _(fk)_
- `tenant_id`: UUID _(fk)_
- `title`: Text
- `description`: Text
- `severity`: String
- `status`: String
- `requirement_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSCorrectiveAction

pk: `id` (UUID) · fk: tenant_id, finding_id, risk_id, owner_user_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `finding_id`: UUID _(fk, nullable)_
- `risk_id`: UUID _(fk, nullable)_
- `title`: Text
- `description`: Text
- `owner_user_id`: UUID _(fk, nullable)_
- `due_date`: Date
- `status`: String
- `completed_at`: DateTime _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSEvidence

pk: `id` (UUID) · fk: tenant_id, control_id, collected_by_user_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `control_id`: UUID _(fk)_
- `title`: Text
- `evidence_type`: String
- `storage_path`: Text
- `collected_at`: Date
- `valid_until`: Date _(nullable)_
- `collected_by_user_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSIncident

pk: `id` (UUID) · fk: tenant_id, corrective_action_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `title`: Text
- `incident_type`: String
- `severity`: String
- `status`: String
- `reported_at`: DateTime
- `resolved_at`: DateTime _(nullable)_
- `external_ticket_id`: Text _(nullable)_
- `corrective_action_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSMaturityProfile

pk: `id` (UUID) · fk: tenant_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `domain`: String
- `existing_registers`: String
- `existing_analyses`: String
- `coordination_capacity`: String
- `linemanagement_structure`: String
- `recommended_option`: String _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSSetupScore

pk: `id` (UUID) · fk: tenant_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `domain`: String
- `cyclus_year`: Integer
- `score_pct`: Numeric
- `steps_completed`: Integer
- `steps_total`: Integer
- `confirmed_at`: DateTime _(nullable)_
- `calculated_at`: DateTime
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSGRCScore

pk: `id` (UUID) · fk: tenant_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `domain`: String
- `cyclus_year`: Integer
- `score_pct`: Numeric
- `components_json`: JSONB
- `calculated_at`: DateTime
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### IMSKnowledgeChunk

pk: `id` (UUID) · fk: tenant_id

- `id`: UUID _(pk, default)_
- `layer`: String
- `tenant_id`: UUID _(fk, nullable)_
- `source_type`: String
- `source_id`: UUID _(nullable)_
- `chunk_index`: Integer
- `content`: Text
- `embedding`: Any
- `model_used`: Text
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_

### AgentConversation

pk: `id` (UUID) · fk: tenant_id, step_execution_id

- `id`: UUID _(pk, default)_
- `tenant_id`: UUID _(fk)_
- `step_execution_id`: UUID _(fk)_
- `agent_name`: String
- `status`: String _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- _relations_: messages: AgentMessage

### AgentMessage

pk: `id` (UUID) · fk: conversation_id, audit_log_id

- `id`: UUID _(pk, default)_
- `conversation_id`: UUID _(fk)_
- `role`: String
- `content`: Text
- `metadata_json`: JSONB _(nullable)_
- `audit_log_id`: UUID _(fk, nullable)_
- `created_at`: DateTime _(default)_
- _relations_: conversation: AgentConversation

## Schema Source Files

Search for ORM schema declarations:
- Drizzle: `pgTable` / `mysqlTable` / `sqliteTable`
- Prisma: `prisma/schema.prisma`
- TypeORM: `@Entity()` decorator
- SQLAlchemy: class inheriting `Base`

---
_Back to [overview.md](./overview.md)_