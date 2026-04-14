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
