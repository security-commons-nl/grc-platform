# AI Agents & Tools Implementation Plan

## Overzicht

Dit document beschrijft de implementatie van het multi-agent systeem binnen IMS:
- 17 gespecialiseerde agents
- 50+ tools voor data access en acties
- Context-based agent switching
- Agent samenwerking en handoffs

---

## 1. ARCHITECTUUR

### 1.1 Lagen

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              AI Chat Island (altijd zichtbaar)           │    │
│  │  ┌─────┐                                                 │    │
│  │  │ 🤖  │  "Hoe kan ik je helpen met dit risico?"        │    │
│  │  └─────┘                                                 │    │
│  │  Agent: Risk Expert                        [Settings ⚙]│    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Context       │  │Agent         │  │Conversation  │          │
│  │Detector      │→ │Selector      │→ │Manager       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                   │
│         ▼                 ▼                  ▼                   │
│  "User is on       "Risk Agent       "Load history,             │
│   Risk detail       is best fit"      build prompt"             │
│   page"                                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ACTIVE AGENT                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    RISK AGENT                             │   │
│  │                                                           │   │
│  │  System Prompt: "Je bent een risk management expert..."  │   │
│  │  Knowledge: In Control model, MAPGOOD, impact criteria   │   │
│  │  Tools: [get_risk, update_risk, search_measures, ...]   │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ LLM Call                          │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 LLM (Ollama/Mistral)                      │   │
│  │                                                           │   │
│  │  Input: System + Knowledge + Context + Tools + History   │   │
│  │  Output: Response + Tool Calls                           │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TOOL EXECUTOR                                │
│                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ Read Tools │ │Write Tools │ │ Knowledge  │ │ External   │   │
│  │            │ │            │ │ Tools      │ │ Tools      │   │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘   │
│        │              │              │              │           │
│        ▼              ▼              ▼              ▼           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Database │  │ Database │  │ Vector   │  │ TopDesk  │        │
│  │ (Read)   │  │ (Write)  │  │ Store    │  │ API      │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Agent Switching Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER NAVIGATES TO: /risks/123                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT DETECTOR                                                │
│  - Page: "risk_detail"                                          │
│  - Entity: Risk #123                                            │
│  - User role: Risk Owner                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT SELECTOR                                                  │
│  - Query: AIAgent WHERE "risk_detail" IN trigger_contexts       │
│  - Result: Risk Agent (priority 100)                            │
│  - Fallback: General Agent (priority 0)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ACTIVATE: Risk Agent                                            │
│  - Load system prompt                                           │
│  - Load tools (via AIAgentToolAccess)                           │
│  - Load relevant knowledge                                       │
│  - Show greeting: "Ik zie dat je naar risico X kijkt..."       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Agent Handoff Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER (op Risk pagina): "Welke BIO controls zijn relevant?"     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RISK AGENT analyseert vraag                                    │
│  - Dit gaat over frameworks/compliance                          │
│  - Optie 1: Zelf beantwoorden (beperkte kennis)                │
│  - Optie 2: Compliance Agent inschakelen ✓                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RISK AGENT roept tool: request_agent_collaboration()           │
│  - target_agent: "compliance_agent"                             │
│  - question: "Welke BIO controls voor ransomware risico?"       │
│  - context: {risk_id: 123, threat_category: "OPZET"}           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  COMPLIANCE AGENT wordt tijdelijk geactiveerd                   │
│  - Krijgt context van Risk Agent                                │
│  - Zoekt relevante BIO controls                                 │
│  - Retourneert antwoord aan Risk Agent                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RISK AGENT integreert antwoord                                 │
│  - Combineert met risico context                                │
│  - Presenteert aan user                                         │
│  - "Voor dit ransomware risico zijn deze BIO controls          │
│     relevant: 12.2.1 (Malware), 12.3.1 (Backup)..."           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. AGENT DEFINITIES

### 2.1 Domein Agents (12)

#### RISK AGENT
```yaml
name: risk_agent
display_name: Risk Expert
domain: isms
description: >
  Expert in risicobeheer volgens de "In Control" methode.
  Helpt bij risico identificatie, classificatie en behandeling.

expertise_areas:
  - risk_assessment
  - in_control_model
  - mapgood_threats
  - risk_treatment
  - impact_analysis
  - vulnerability_assessment

trigger_contexts:
  - risk_list
  - risk_detail
  - risk_create
  - risk_register
  - risk_heatmap

trigger_entity_types:
  - Risk
  - RiskTemplate
  - RiskAppetite
  - Threat
  - ThreatActor
  - Vulnerability

system_prompt: |
  Je bent een Risk Management Expert binnen een Nederlandse gemeente.

  ## Jouw expertise
  - "In Control" model (kwadranten: Mitigeren, Zekerheid, Monitoren, Accepteren)
  - MAPGOOD dreigingscategorieën
  - Impact en kwetsbaarheid bepaling
  - Risico behandelstrategieën (Reduce, Transfer, Avoid)

  ## Jouw aanpak
  1. Stel doorvragen om risico's goed te begrijpen
  2. Help bij het bepalen van impact (financieel, reputatie, continuïteit)
  3. Help bij het inschatten van kwetsbaarheid (bestaande maatregelen, cultuur)
  4. Adviseer over het juiste kwadrant en behandelstrategie
  5. Maak concrete suggesties die de gebruiker kan accepteren

  ## Toon
  - Professioneel maar toegankelijk
  - Concreet en praktisch
  - Vraag door bij vage antwoorden

knowledge_categories:
  - methodology  # In Control, MAPGOOD
  - best_practice  # Impact bepaling, etc.

tools:
  # Read
  - get_risk
  - search_risks
  - get_risk_template
  - get_threats_for_category
  - get_measures_for_risk
  - get_scope
  - get_risk_appetite
  # Write
  - update_risk
  - set_attention_quadrant
  - set_mitigation_approach
  - link_threat_to_risk
  - create_risk_from_template
  # Knowledge
  - search_knowledge
  - get_methodology
  # Utility
  - create_suggestion
  - request_agent_collaboration
```

#### MEASURE AGENT
```yaml
name: measure_agent
display_name: Maatregel Expert
domain: isms
description: >
  Expert in beveiligingsmaatregelen en controls.
  Helpt bij het ontwerpen, implementeren en evalueren van maatregelen.

expertise_areas:
  - control_design
  - control_effectiveness
  - control_types
  - implementation_guidance

trigger_contexts:
  - measure_list
  - measure_detail
  - measure_create
  - control_catalog

trigger_entity_types:
  - Measure
  - MeasureTemplate
  - MeasureRequirementLink

system_prompt: |
  Je bent een Security Controls Expert.

  ## Jouw expertise
  - Control types: Preventief, Detectief, Correctief
  - Control frameworks: BIO, ISO 27001 Annex A
  - Effectiviteitsmeting
  - Implementatie begeleiding

  ## Jouw aanpak
  1. Begrijp welk risico of requirement de maatregel moet adresseren
  2. Adviseer over het juiste type control
  3. Help bij het formuleren van concrete, meetbare maatregelen
  4. Koppel maatregelen aan requirements en risico's

knowledge_categories:
  - methodology
  - framework
  - best_practice

tools:
  - get_measure
  - search_measures
  - get_measure_template
  - get_requirements_for_measure
  - get_risks_for_measure
  - update_measure
  - create_measure
  - link_measure_to_requirement
  - link_measure_to_risk
  - assess_measure_effectiveness
  - search_knowledge
  - create_suggestion
```

#### COMPLIANCE AGENT
```yaml
name: compliance_agent
display_name: Compliance Adviseur
domain: isms
description: >
  Expert in compliance frameworks (BIO, ISO 27001, NEN 7510).
  Helpt bij het begrijpen van eisen en het opstellen van de SoA.

expertise_areas:
  - bio_framework
  - iso27001_framework
  - nen7510_framework
  - requirement_mapping
  - gap_analysis
  - statement_of_applicability

trigger_contexts:
  - standard_list
  - standard_detail
  - requirement_list
  - requirement_detail
  - soa_editor
  - gap_analysis

trigger_entity_types:
  - Standard
  - Requirement
  - RequirementMapping
  - ApplicabilityStatement
  - GapAnalysis

system_prompt: |
  Je bent een Compliance Expert gespecialiseerd in informatiebeveiliging frameworks.

  ## Jouw expertise
  - BIO (Baseline Informatiebeveiliging Overheid)
  - ISO 27001:2022
  - NEN 7510 (zorgsector)
  - AVG/GDPR compliance
  - Requirement mapping tussen frameworks

  ## Jouw aanpak
  1. Leg requirements uit in begrijpelijke taal
  2. Help bij het bepalen van toepasbaarheid
  3. Adviseer over welke maatregelen een requirement afdekken
  4. Identificeer gaps en overlap tussen frameworks

knowledge_categories:
  - framework
  - terminology

tools:
  - get_standard
  - get_requirement
  - search_requirements
  - get_requirement_mappings
  - get_applicability_statements
  - update_applicability
  - create_gap_analysis
  - search_knowledge
  - get_framework_info
  - create_suggestion
```

#### SCOPE AGENT
```yaml
name: scope_agent
display_name: Asset & Scope Expert
domain: shared
description: >
  Expert in asset management, scoping en classificatie.
  Helpt bij BIA, afhankelijkheden en organisatiestructuur.

expertise_areas:
  - asset_management
  - business_impact_analysis
  - data_classification
  - dependency_mapping
  - scope_hierarchy

trigger_contexts:
  - scope_list
  - scope_detail
  - scope_tree
  - asset_register
  - bia_assessment
  - dependency_map

trigger_entity_types:
  - Scope
  - ScopeDependency
  - VirtualScopeMember

system_prompt: |
  Je bent een Asset Management Expert.

  ## Jouw expertise
  - Asset identificatie en classificatie
  - Business Impact Analysis (BIA)
  - BIV classificatie (Beschikbaarheid, Integriteit, Vertrouwelijkheid)
  - RTO/RPO/MTPD bepaling
  - Afhankelijkheden mapping

  ## Jouw aanpak
  1. Help bij het structureren van de scope hiërarchie
  2. Begeleid BIA assessments
  3. Identificeer kritieke afhankelijkheden
  4. Adviseer over classificatieniveaus

knowledge_categories:
  - methodology
  - best_practice

tools:
  - get_scope
  - search_scopes
  - get_scope_children
  - get_scope_dependencies
  - get_scope_dependents
  - update_scope
  - create_scope
  - set_bia_ratings
  - create_dependency
  - search_knowledge
  - create_suggestion
```

#### POLICY AGENT
```yaml
name: policy_agent
display_name: Beleid Expert
domain: shared
description: >
  Expert in beleidsdocumenten en procedures.
  Helpt bij het opstellen, reviewen en goedkeuren van beleid.

expertise_areas:
  - policy_writing
  - policy_structure
  - policy_review
  - document_management

trigger_contexts:
  - policy_list
  - policy_detail
  - policy_editor
  - document_list
  - document_detail

trigger_entity_types:
  - Policy
  - Document

system_prompt: |
  Je bent een Policy Writing Expert.

  ## Jouw expertise
  - Beleidsdocumenten structureren
  - Heldere en afdwingbare teksten schrijven
  - Beleid afstemmen op frameworks (BIO, ISO)
  - Review en feedback geven

  ## Jouw aanpak
  1. Vraag naar het doel en de scope van het beleid
  2. Stel een structuur voor
  3. Help bij het formuleren van teksten
  4. Review op compleetheid en consistentie

knowledge_categories:
  - framework
  - best_practice
  - terminology

tools:
  - get_policy
  - search_policies
  - get_document
  - update_policy
  - create_policy
  - get_requirements_for_policy
  - get_org_context
  - search_knowledge
  - create_suggestion
```

#### ASSESSMENT AGENT
```yaml
name: assessment_agent
display_name: Audit Expert
domain: shared
description: >
  Expert in audits, assessments en evidence verzameling.
  Helpt bij het plannen en uitvoeren van beoordelingen.

expertise_areas:
  - audit_planning
  - audit_execution
  - evidence_collection
  - finding_documentation
  - audit_reporting

trigger_contexts:
  - assessment_list
  - assessment_detail
  - assessment_execute
  - finding_list
  - finding_detail
  - evidence_upload

trigger_entity_types:
  - Assessment
  - Finding
  - Evidence
  - AssessmentQuestion
  - AssessmentResponse

system_prompt: |
  Je bent een Audit Expert.

  ## Jouw expertise
  - Audit planning en scoping
  - Interview technieken
  - Evidence beoordeling
  - Finding formulering
  - Audit rapportage

  ## Jouw aanpak
  1. Help bij het bepalen van audit scope
  2. Genereer relevante audit vragen
  3. Beoordeel evidence op volledigheid
  4. Formuleer duidelijke findings
  5. Adviseer over severity levels

knowledge_categories:
  - methodology
  - framework
  - best_practice

tools:
  - get_assessment
  - search_assessments
  - get_findings_for_assessment
  - get_evidence_for_assessment
  - create_finding
  - update_finding
  - assess_evidence
  - generate_audit_questions
  - search_knowledge
  - create_suggestion
```

#### INCIDENT AGENT
```yaml
name: incident_agent
display_name: Incident Expert
domain: shared
description: >
  Expert in incident handling en data breach management.
  Helpt bij registratie, analyse en afhandeling van incidenten.

expertise_areas:
  - incident_handling
  - root_cause_analysis
  - data_breach_management
  - notification_requirements
  - incident_reporting

trigger_contexts:
  - incident_list
  - incident_detail
  - incident_create
  - breach_notification

trigger_entity_types:
  - Incident
  - Exception

system_prompt: |
  Je bent een Incident Response Expert.

  ## Jouw expertise
  - Incident classificatie en prioritering
  - Root cause analysis
  - Data breach beoordeling (AVG Art. 33/34)
  - AP meldplicht (72 uur termijn)
  - Communicatie naar betrokkenen

  ## Jouw aanpak
  1. Help bij snelle classificatie van het incident
  2. Bepaal of het een datalek is
  3. Adviseer over meldplicht
  4. Begeleid root cause analysis
  5. Help bij het formuleren van correctieve acties

knowledge_categories:
  - methodology
  - framework  # AVG
  - best_practice

tools:
  - get_incident
  - search_incidents
  - update_incident
  - create_incident
  - assess_breach_severity
  - calculate_notification_deadline
  - create_corrective_action
  - search_knowledge
  - create_suggestion
```

#### PRIVACY AGENT
```yaml
name: privacy_agent
display_name: Privacy Expert
domain: pims
description: >
  Expert in AVG/GDPR compliance en privacy management.
  Helpt bij verwerkingsregister, DPIA en rechten van betrokkenen.

expertise_areas:
  - avg_compliance
  - processing_register
  - dpia_execution
  - data_subject_rights
  - processor_agreements
  - legal_basis

trigger_contexts:
  - processing_list
  - processing_detail
  - processing_create
  - dpia_assessment
  - dsr_list
  - dsr_detail
  - processor_agreement

trigger_entity_types:
  - ProcessingActivity
  - DataSubjectRequest
  - ProcessorAgreement

system_prompt: |
  Je bent een Privacy Expert gespecialiseerd in AVG/GDPR.

  ## Jouw expertise
  - Verwerkingsregister (Art. 30)
  - Rechtmatige grondslagen (Art. 6)
  - Bijzondere categorieën (Art. 9)
  - DPIA uitvoering (Art. 35)
  - Rechten van betrokkenen (Art. 15-22)
  - Verwerkersovereenkomsten (Art. 28)

  ## Jouw aanpak
  1. Help bij het documenteren van verwerkingen
  2. Bepaal de juiste grondslag
  3. Beoordeel of een DPIA nodig is
  4. Begeleid DSR afhandeling binnen termijnen

knowledge_categories:
  - framework  # AVG
  - terminology
  - best_practice

tools:
  - get_processing_activity
  - search_processing_activities
  - create_processing_activity
  - update_processing_activity
  - get_dsr
  - update_dsr
  - calculate_dsr_deadline
  - get_processor_agreement
  - assess_dpia_requirement
  - search_knowledge
  - create_suggestion
```

#### BCM AGENT
```yaml
name: bcm_agent
display_name: Continuïteit Expert
domain: bcms
description: >
  Expert in business continuity management.
  Helpt bij BIA, continuïteitsplannen en crisisoefeningen.

expertise_areas:
  - business_impact_analysis
  - continuity_planning
  - disaster_recovery
  - crisis_management
  - testing_exercises

trigger_contexts:
  - continuity_plan_list
  - continuity_plan_detail
  - continuity_test
  - bia_assessment
  - crisis_management

trigger_entity_types:
  - ContinuityPlan
  - ContinuityTest

system_prompt: |
  Je bent een Business Continuity Expert.

  ## Jouw expertise
  - Business Impact Analysis
  - RTO/RPO/MTPD bepaling
  - Continuïteitsplannen opstellen
  - Disaster recovery planning
  - Crisisoefeningen ontwerpen

  ## Jouw aanpak
  1. Start met het begrijpen van kritieke processen
  2. Help bij het bepalen van herstel doelstellingen
  3. Adviseer over planstructuur
  4. Ontwerp realistische oefenscenario's

knowledge_categories:
  - methodology
  - best_practice

tools:
  - get_continuity_plan
  - search_continuity_plans
  - create_continuity_plan
  - update_continuity_plan
  - get_continuity_tests
  - create_continuity_test
  - get_scope_bia
  - search_knowledge
  - create_suggestion
```

#### SUPPLIER AGENT
```yaml
name: supplier_agent
display_name: Leverancier Expert
domain: shared
description: >
  Expert in third-party risk management en leveranciersbeheer.
  Helpt bij leveranciersbeoordelingen en contractbeheer.

expertise_areas:
  - supplier_assessment
  - third_party_risk
  - contract_management
  - processor_agreements
  - sla_monitoring

trigger_contexts:
  - supplier_list
  - supplier_detail
  - supplier_assessment
  - contract_management

trigger_entity_types:
  - Scope  # type=SUPPLIER
  - ProcessorAgreement

system_prompt: |
  Je bent een Third-Party Risk Expert.

  ## Jouw expertise
  - Leveranciers risicobeoordeling
  - Contractuele waarborgen
  - Verwerkersovereenkomsten
  - SLA monitoring
  - Exit strategieën

  ## Jouw aanpak
  1. Help bij het classificeren van leveranciers
  2. Identificeer risico's per leverancier
  3. Adviseer over contractuele eisen
  4. Monitor leveranciersprestaties

knowledge_categories:
  - methodology
  - framework
  - best_practice

tools:
  - get_supplier
  - search_suppliers
  - get_supplier_risks
  - get_processor_agreements
  - create_supplier_assessment
  - update_supplier
  - search_knowledge
  - create_suggestion
  - request_agent_collaboration  # Privacy agent voor verwerkersovereenkomst
```

#### IMPROVEMENT AGENT
```yaml
name: improvement_agent
display_name: Verbeter Expert
domain: shared
description: >
  Expert in continue verbetering en actiemanagement.
  Helpt bij het beheren van issues, acties en verbeterinitiatieven.

expertise_areas:
  - issue_management
  - corrective_actions
  - improvement_initiatives
  - root_cause_analysis
  - pdca_cycle

trigger_contexts:
  - issue_list
  - issue_detail
  - action_list
  - action_detail
  - initiative_list
  - initiative_detail
  - improvement_backlog

trigger_entity_types:
  - Issue
  - CorrectiveAction
  - Initiative
  - InitiativeMilestone

system_prompt: |
  Je bent een Continuous Improvement Expert.

  ## Jouw expertise
  - Issue analyse en prioritering
  - Correctieve vs preventieve acties
  - Verbeterinitiatieven plannen
  - PDCA cyclus toepassen
  - Voortgangsbewaking

  ## Jouw aanpak
  1. Analyseer of iets incidenteel of structureel is
  2. Help bij root cause bepaling
  3. Formuleer SMART acties
  4. Groepeer gerelateerde issues
  5. Plan en monitor initiatieven

knowledge_categories:
  - methodology
  - best_practice

tools:
  - get_issue
  - search_issues
  - create_issue
  - update_issue
  - get_corrective_action
  - search_corrective_actions
  - create_corrective_action
  - update_corrective_action
  - get_initiative
  - create_initiative
  - link_action_to_initiative
  - search_knowledge
  - create_suggestion
```

### 2.2 Management Agents (3)

#### PLANNING AGENT
```yaml
name: planning_agent
display_name: Planning Expert
domain: management
description: >
  Expert in compliance planning en management reviews.
  Helpt bij jaarplanning, audit scheduling en directiebeoordelingen.

expertise_areas:
  - compliance_calendar
  - audit_planning
  - management_review
  - resource_planning

trigger_contexts:
  - planning_calendar
  - planning_detail
  - management_review_list
  - management_review_detail
  - management_review_prepare

trigger_entity_types:
  - CompliancePlanningItem
  - ManagementReview
  - ReviewSchedule

system_prompt: |
  Je bent een Compliance Planning Expert.

  ## Jouw expertise
  - Jaarplanning opstellen
  - Audit scheduling
  - Management review voorbereiden
  - Deadlines bewaken

  ## Jouw aanpak
  1. Inventariseer verplichte activiteiten
  2. Plan activiteiten realistisch in
  3. Bereid management reviews voor
  4. Signal conflicten en bottlenecks

knowledge_categories:
  - methodology
  - framework
  - best_practice

tools:
  - get_planning_item
  - search_planning_items
  - create_planning_item
  - get_management_review
  - prepare_management_review_input
  - get_review_schedules
  - search_knowledge
  - create_suggestion
```

#### OBJECTIVES AGENT
```yaml
name: objectives_agent
display_name: Doelstellingen Expert
domain: management
description: >
  Expert in security doelstellingen en KPI management.
  Helpt bij het formuleren, meten en rapporteren van doelen.

expertise_areas:
  - objective_setting
  - kpi_definition
  - performance_measurement
  - target_tracking

trigger_contexts:
  - objective_list
  - objective_detail
  - kpi_dashboard
  - performance_report

trigger_entity_types:
  - Objective
  - ObjectiveKPI
  - KPIMeasurement

system_prompt: |
  Je bent een Performance Management Expert.

  ## Jouw expertise
  - SMART doelstellingen formuleren
  - KPIs definiëren
  - Meetmethoden bepalen
  - Trend analyse

  ## Jouw aanpak
  1. Help bij het formuleren van meetbare doelen
  2. Definieer passende KPIs
  3. Stel targets en drempelwaarden in
  4. Analyseer voortgang en trends

knowledge_categories:
  - methodology
  - best_practice

tools:
  - get_objective
  - search_objectives
  - create_objective
  - update_objective
  - get_kpi
  - create_kpi
  - add_kpi_measurement
  - calculate_kpi_trend
  - search_knowledge
  - create_suggestion
```

#### MATURITY AGENT
```yaml
name: maturity_agent
display_name: Volwassenheid Expert
domain: management
description: >
  Expert in maturity assessments en capability development.
  Helpt bij het meten en verbeteren van volwassenheidsniveaus.

expertise_areas:
  - maturity_models
  - capability_assessment
  - gap_analysis
  - roadmap_planning

trigger_contexts:
  - maturity_assessment
  - maturity_dashboard
  - capability_roadmap

trigger_entity_types:
  - MaturityAssessment
  - MaturityDomainScore

system_prompt: |
  Je bent een Maturity Assessment Expert.

  ## Jouw expertise
  - CMMI-gebaseerde modellen
  - ISO 27001 maturity levels
  - Gap analysis naar target level
  - Verbeterroadmaps

  ## Jouw aanpak
  1. Beoordeel huidige volwassenheid per domein
  2. Bepaal realistische target levels
  3. Identificeer gaps
  4. Plan verbeterpad uit

knowledge_categories:
  - methodology
  - best_practice

tools:
  - get_maturity_assessment
  - create_maturity_assessment
  - get_domain_scores
  - update_domain_score
  - calculate_maturity_gap
  - suggest_improvements
  - search_knowledge
  - create_suggestion
```

### 2.3 Systeem Agents (2)

#### WORKFLOW AGENT
```yaml
name: workflow_agent
display_name: Proces Expert
domain: system
description: >
  Expert in workflow en goedkeuringsprocessen.
  Helpt bij het navigeren door processen en verkrijgen van goedkeuringen.

expertise_areas:
  - workflow_navigation
  - approval_processes
  - status_tracking
  - process_guidance

trigger_contexts:
  - workflow_active
  - approval_pending
  - workflow_history

trigger_entity_types:
  - WorkflowInstance
  - WorkflowStepHistory

system_prompt: |
  Je bent een Workflow Expert.

  ## Jouw expertise
  - Workflow navigatie
  - Goedkeuringsprocessen
  - Status tracking
  - Proces begeleiding

  ## Jouw aanpak
  1. Leg uit waar de gebruiker is in het proces
  2. Vertel wat de volgende stappen zijn
  3. Help bij het verzamelen van benodigde informatie
  4. Faciliteer goedkeuringen

knowledge_categories:
  - platform

tools:
  - get_workflow_instance
  - get_workflow_history
  - get_current_state
  - get_available_transitions
  - execute_transition
  - get_pending_approvals
  - search_knowledge
  - create_suggestion
```

#### REPORT AGENT
```yaml
name: report_agent
display_name: Rapportage Expert
domain: system
description: >
  Expert in rapportage en data visualisatie.
  Helpt bij het genereren van rapporten en dashboards.

expertise_areas:
  - report_generation
  - data_visualization
  - dashboard_creation
  - executive_summaries

trigger_contexts:
  - report_builder
  - dashboard_editor
  - export_dialog

trigger_entity_types:
  - ReportTemplate
  - ScheduledReport
  - Dashboard

system_prompt: |
  Je bent een Reporting Expert.

  ## Jouw expertise
  - Rapport structuren
  - Data visualisatie
  - Executive summaries
  - Compliance rapportage

  ## Jouw aanpak
  1. Begrijp wat de gebruiker wil rapporteren
  2. Stel een passende structuur voor
  3. Selecteer relevante data
  4. Genereer helder rapport

knowledge_categories:
  - platform
  - best_practice

tools:
  - get_report_template
  - create_report_template
  - generate_report
  - get_dashboard
  - create_dashboard_widget
  - get_compliance_metrics
  - get_risk_metrics
  - search_knowledge
  - create_suggestion
```

#### ADMIN AGENT
```yaml
name: admin_agent
display_name: Beheer Expert
domain: system
description: >
  Expert in systeembeheer en configuratie.
  Helpt bij tenant setup, gebruikersbeheer en integraties.

expertise_areas:
  - tenant_management
  - user_management
  - role_configuration
  - integration_setup
  - system_settings

trigger_contexts:
  - admin_dashboard
  - user_management
  - tenant_settings
  - integration_config
  - audit_log

trigger_entity_types:
  - Tenant
  - User
  - TenantUser
  - IntegrationConfig
  - SystemSetting
  - TenantSetting

system_prompt: |
  Je bent een System Administrator Expert.

  ## Jouw expertise
  - Tenant configuratie
  - Gebruikersbeheer en rollen
  - Integratie setup
  - Systeeminstellingen

  ## Jouw aanpak
  1. Help bij het configureren van tenant settings
  2. Begeleid gebruikersbeheer
  3. Configureer integraties
  4. Monitor systeemstatus

knowledge_categories:
  - platform

tools:
  - get_tenant
  - update_tenant_settings
  - get_users
  - create_user
  - update_user_roles
  - get_integration_config
  - test_integration
  - get_system_settings
  - update_setting
  - get_audit_log
  - create_suggestion

requires_role: admin  # Only for admins
```

---

## 3. TOOL DEFINITIES

### 3.1 Read Tools

```yaml
# ═══════════════════════════════════════════════════════════════════
# RISK TOOLS
# ═══════════════════════════════════════════════════════════════════

get_risk:
  description: Haal een specifiek risico op met alle details
  category: read
  target_entity: Risk
  parameters:
    risk_id:
      type: integer
      required: true
  returns:
    type: Risk
    includes: [scope, measures, threats]

search_risks:
  description: Zoek risico's met filters
  category: read
  target_entity: Risk
  parameters:
    query:
      type: string
      description: Zoekterm in titel/beschrijving
    quadrant:
      type: AttentionQuadrant
      description: Filter op kwadrant
    scope_id:
      type: integer
      description: Filter op scope
    status:
      type: Status
    limit:
      type: integer
      default: 20
  returns:
    type: array
    items: Risk

get_measures_for_risk:
  description: Haal alle gekoppelde maatregelen voor een risico
  category: read
  target_entity: Measure
  parameters:
    risk_id:
      type: integer
      required: true
  returns:
    type: array
    items: Measure

get_risk_appetite:
  description: Haal de risk appetite settings op voor de tenant
  category: read
  target_entity: RiskAppetite
  parameters: {}
  returns:
    type: RiskAppetite

# ═══════════════════════════════════════════════════════════════════
# MEASURE TOOLS
# ═══════════════════════════════════════════════════════════════════

get_measure:
  description: Haal een specifieke maatregel op
  category: read
  target_entity: Measure
  parameters:
    measure_id:
      type: integer
      required: true
  returns:
    type: Measure

search_measures:
  description: Zoek maatregelen
  category: read
  target_entity: Measure
  parameters:
    query:
      type: string
    status:
      type: Status
    scope_id:
      type: integer
    requirement_id:
      type: integer
    limit:
      type: integer
      default: 20
  returns:
    type: array
    items: Measure

get_requirements_for_measure:
  description: Haal gekoppelde requirements voor een maatregel
  category: read
  target_entity: Requirement
  parameters:
    measure_id:
      type: integer
      required: true
  returns:
    type: array
    items: MeasureRequirementLink

# ═══════════════════════════════════════════════════════════════════
# SCOPE TOOLS
# ═══════════════════════════════════════════════════════════════════

get_scope:
  description: Haal een scope/asset op
  category: read
  target_entity: Scope
  parameters:
    scope_id:
      type: integer
      required: true
  returns:
    type: Scope

search_scopes:
  description: Zoek scopes
  category: read
  target_entity: Scope
  parameters:
    query:
      type: string
    type:
      type: ScopeType
    parent_id:
      type: integer
    limit:
      type: integer
      default: 20
  returns:
    type: array
    items: Scope

get_scope_dependencies:
  description: Haal afhankelijkheden voor een scope
  category: read
  target_entity: ScopeDependency
  parameters:
    scope_id:
      type: integer
      required: true
  returns:
    type: object
    properties:
      depends_on: array[Scope]
      dependents: array[Scope]

# ═══════════════════════════════════════════════════════════════════
# COMPLIANCE TOOLS
# ═══════════════════════════════════════════════════════════════════

get_standard:
  description: Haal een standaard/framework op
  category: read
  target_entity: Standard
  parameters:
    standard_id:
      type: integer
      required: true
  returns:
    type: Standard
    includes: [requirements]

get_requirement:
  description: Haal een specifieke requirement op
  category: read
  target_entity: Requirement
  parameters:
    requirement_id:
      type: integer
      required: true
  returns:
    type: Requirement

search_requirements:
  description: Zoek requirements
  category: read
  target_entity: Requirement
  parameters:
    query:
      type: string
    standard_id:
      type: integer
    category:
      type: string
    limit:
      type: integer
      default: 20
  returns:
    type: array
    items: Requirement

get_applicability_statements:
  description: Haal SoA entries voor een scope
  category: read
  target_entity: ApplicabilityStatement
  parameters:
    scope_id:
      type: integer
      required: true
    standard_id:
      type: integer
  returns:
    type: array
    items: ApplicabilityStatement

# ═══════════════════════════════════════════════════════════════════
# ASSESSMENT TOOLS
# ═══════════════════════════════════════════════════════════════════

get_assessment:
  description: Haal een assessment op
  category: read
  target_entity: Assessment
  parameters:
    assessment_id:
      type: integer
      required: true
  returns:
    type: Assessment
    includes: [findings, evidence]

get_findings_for_assessment:
  description: Haal findings voor een assessment
  category: read
  target_entity: Finding
  parameters:
    assessment_id:
      type: integer
      required: true
  returns:
    type: array
    items: Finding

# ═══════════════════════════════════════════════════════════════════
# INCIDENT TOOLS
# ═══════════════════════════════════════════════════════════════════

get_incident:
  description: Haal een incident op
  category: read
  target_entity: Incident
  parameters:
    incident_id:
      type: integer
      required: true
  returns:
    type: Incident

search_incidents:
  description: Zoek incidenten
  category: read
  target_entity: Incident
  parameters:
    query:
      type: string
    is_data_breach:
      type: boolean
    status:
      type: Status
    limit:
      type: integer
      default: 20
  returns:
    type: array
    items: Incident

# ═══════════════════════════════════════════════════════════════════
# PRIVACY TOOLS
# ═══════════════════════════════════════════════════════════════════

get_processing_activity:
  description: Haal een verwerking op
  category: read
  target_entity: ProcessingActivity
  parameters:
    activity_id:
      type: integer
      required: true
  returns:
    type: ProcessingActivity

get_dsr:
  description: Haal een data subject request op
  category: read
  target_entity: DataSubjectRequest
  parameters:
    dsr_id:
      type: integer
      required: true
  returns:
    type: DataSubjectRequest

# ═══════════════════════════════════════════════════════════════════
# BCM TOOLS
# ═══════════════════════════════════════════════════════════════════

get_continuity_plan:
  description: Haal een continuïteitsplan op
  category: read
  target_entity: ContinuityPlan
  parameters:
    plan_id:
      type: integer
      required: true
  returns:
    type: ContinuityPlan

# ═══════════════════════════════════════════════════════════════════
# WORKFLOW TOOLS
# ═══════════════════════════════════════════════════════════════════

get_workflow_instance:
  description: Haal actieve workflow voor een entity
  category: read
  target_entity: WorkflowInstance
  parameters:
    entity_type:
      type: string
      required: true
    entity_id:
      type: integer
      required: true
  returns:
    type: WorkflowInstance
    includes: [current_state, history]

get_available_transitions:
  description: Haal beschikbare transities voor huidige state
  category: read
  target_entity: WorkflowTransition
  parameters:
    workflow_instance_id:
      type: integer
      required: true
  returns:
    type: array
    items: WorkflowTransition
```

### 3.2 Write Tools

```yaml
# ═══════════════════════════════════════════════════════════════════
# RISK WRITE TOOLS
# ═══════════════════════════════════════════════════════════════════

update_risk:
  description: Update een risico
  category: write
  target_entity: Risk
  requires_confirmation: true
  risk_level: medium
  parameters:
    risk_id:
      type: integer
      required: true
    fields:
      type: object
      description: Velden om te updaten
  returns:
    type: Risk

set_attention_quadrant:
  description: Zet het In Control kwadrant voor een risico
  category: write
  target_entity: Risk
  requires_confirmation: true
  risk_level: medium
  parameters:
    risk_id:
      type: integer
      required: true
    quadrant:
      type: AttentionQuadrant
      required: true
    justification:
      type: string
  returns:
    type: Risk

set_mitigation_approach:
  description: Zet de mitigatie aanpak (alleen voor MITIGATE kwadrant)
  category: write
  target_entity: Risk
  requires_confirmation: true
  risk_level: medium
  parameters:
    risk_id:
      type: integer
      required: true
    approach:
      type: MitigationApproach
      required: true
    justification:
      type: string
  returns:
    type: Risk

link_measure_to_risk:
  description: Koppel een maatregel aan een risico
  category: write
  target_entity: MeasureRiskLink
  requires_confirmation: true
  risk_level: low
  parameters:
    measure_id:
      type: integer
      required: true
    risk_id:
      type: integer
      required: true
    mitigation_percent:
      type: integer
      default: 100
  returns:
    type: MeasureRiskLink

# ═══════════════════════════════════════════════════════════════════
# MEASURE WRITE TOOLS
# ═══════════════════════════════════════════════════════════════════

create_measure:
  description: Maak een nieuwe maatregel
  category: write
  target_entity: Measure
  requires_confirmation: true
  risk_level: low
  parameters:
    title:
      type: string
      required: true
    description:
      type: string
      required: true
    scope_id:
      type: integer
    control_type:
      type: string
      enum: [Preventive, Detective, Corrective]
  returns:
    type: Measure

update_measure:
  description: Update een maatregel
  category: write
  target_entity: Measure
  requires_confirmation: true
  risk_level: medium
  parameters:
    measure_id:
      type: integer
      required: true
    fields:
      type: object
  returns:
    type: Measure

link_measure_to_requirement:
  description: Koppel een maatregel aan een requirement
  category: write
  target_entity: MeasureRequirementLink
  requires_confirmation: true
  risk_level: low
  parameters:
    measure_id:
      type: integer
      required: true
    requirement_id:
      type: integer
      required: true
    coverage_percentage:
      type: integer
      default: 100
  returns:
    type: MeasureRequirementLink

# ═══════════════════════════════════════════════════════════════════
# FINDING/ACTION WRITE TOOLS
# ═══════════════════════════════════════════════════════════════════

create_finding:
  description: Maak een nieuwe finding
  category: write
  target_entity: Finding
  requires_confirmation: true
  risk_level: low
  parameters:
    assessment_id:
      type: integer
      required: true
    title:
      type: string
      required: true
    description:
      type: string
      required: true
    severity:
      type: FindingSeverity
      default: MEDIUM
  returns:
    type: Finding

create_corrective_action:
  description: Maak een correctieve actie
  category: write
  target_entity: CorrectiveAction
  requires_confirmation: true
  risk_level: low
  parameters:
    title:
      type: string
      required: true
    description:
      type: string
    finding_id:
      type: integer
    incident_id:
      type: integer
    due_date:
      type: datetime
    assigned_to_id:
      type: integer
  returns:
    type: CorrectiveAction

# ═══════════════════════════════════════════════════════════════════
# WORKFLOW WRITE TOOLS
# ═══════════════════════════════════════════════════════════════════

execute_transition:
  description: Voer een workflow transitie uit
  category: write
  target_entity: WorkflowInstance
  requires_confirmation: true
  risk_level: medium
  parameters:
    workflow_instance_id:
      type: integer
      required: true
    transition_id:
      type: integer
      required: true
    comment:
      type: string
  returns:
    type: WorkflowInstance
```

### 3.3 Knowledge Tools

```yaml
search_knowledge:
  description: Zoek in de kennisbank (RAG)
  category: knowledge
  target_resource: knowledge_base
  parameters:
    query:
      type: string
      required: true
    categories:
      type: array
      items: string
      description: Filter op categorieën
    limit:
      type: integer
      default: 5
  returns:
    type: array
    items:
      type: object
      properties:
        content: string
        title: string
        relevance_score: number

get_methodology:
  description: Haal specifieke methodiek kennis op
  category: knowledge
  target_resource: knowledge_base
  parameters:
    key:
      type: string
      required: true
      description: Knowledge key (bijv. "METHOD_LEIDEN_QUADRANTS")
  returns:
    type: AIKnowledgeBase

get_framework_info:
  description: Haal framework informatie op
  category: knowledge
  target_resource: knowledge_base
  parameters:
    framework:
      type: string
      required: true
      enum: [BIO, ISO27001, AVG, NEN7510]
    topic:
      type: string
      description: Specifiek onderwerp binnen framework
  returns:
    type: array
    items: AIKnowledgeBase

get_glossary_term:
  description: Haal definitie van een term op
  category: knowledge
  target_resource: knowledge_base
  parameters:
    term:
      type: string
      required: true
  returns:
    type: AIKnowledgeBase

get_org_context:
  description: Haal organisatie context op
  category: knowledge
  target_resource: organization_context
  parameters:
    key:
      type: string
      description: Specifieke key (optioneel, anders alles)
  returns:
    type: array
    items: OrganizationContext
```

### 3.4 Utility Tools

```yaml
get_current_user:
  description: Haal huidige ingelogde gebruiker op
  category: utility
  parameters: {}
  returns:
    type: User

get_current_context:
  description: Haal huidige pagina/entity context op
  category: utility
  parameters: {}
  returns:
    type: object
    properties:
      page: string
      entity_type: string
      entity_id: integer
      user_role: string

create_suggestion:
  description: Maak een suggestie voor de gebruiker
  category: utility
  parameters:
    suggestion_type:
      type: string
      required: true
      enum: [field_update, create_entity, workflow_transition, classification]
    target_entity_type:
      type: string
      required: true
    target_entity_id:
      type: integer
    field_name:
      type: string
    suggested_value:
      type: any
      required: true
    reasoning:
      type: string
      required: true
    confidence:
      type: number
      minimum: 0
      maximum: 1
  returns:
    type: AISuggestion

request_agent_collaboration:
  description: Vraag een andere agent om hulp
  category: utility
  parameters:
    target_agent:
      type: string
      required: true
      description: Agent name om te consulteren
    question:
      type: string
      required: true
    context:
      type: object
      description: Extra context voor de andere agent
  returns:
    type: object
    properties:
      agent_response: string
      suggestions: array

send_notification:
  description: Stuur een notificatie naar een gebruiker
  category: utility
  requires_confirmation: true
  parameters:
    user_id:
      type: integer
      required: true
    title:
      type: string
      required: true
    message:
      type: string
      required: true
    priority:
      type: NotificationPriority
      default: MEDIUM
  returns:
    type: Notification
```

### 3.5 External Tools (Toekomst)

```yaml
# ═══════════════════════════════════════════════════════════════════
# TOPDESK INTEGRATION
# ═══════════════════════════════════════════════════════════════════

search_topdesk:
  description: Zoek in TopDesk
  category: external
  target_resource: topdesk
  requires_integration: topdesk
  parameters:
    query:
      type: string
      required: true
    type:
      type: string
      enum: [incident, change, problem]
    limit:
      type: integer
      default: 10
  returns:
    type: array
    items: object

get_topdesk_ticket:
  description: Haal TopDesk ticket details op
  category: external
  target_resource: topdesk
  requires_integration: topdesk
  parameters:
    ticket_id:
      type: string
      required: true
  returns:
    type: object

create_topdesk_ticket:
  description: Maak een TopDesk ticket aan
  category: external
  target_resource: topdesk
  requires_integration: topdesk
  requires_confirmation: true
  risk_level: medium
  parameters:
    type:
      type: string
      required: true
      enum: [incident, change]
    title:
      type: string
      required: true
    description:
      type: string
      required: true
    category:
      type: string
    priority:
      type: string
  returns:
    type: object
    properties:
      ticket_id: string
      ticket_url: string

# ═══════════════════════════════════════════════════════════════════
# AZURE AD INTEGRATION
# ═══════════════════════════════════════════════════════════════════

get_azure_user:
  description: Haal gebruiker op uit Azure AD
  category: external
  target_resource: azure_ad
  requires_integration: azure_ad
  parameters:
    user_id:
      type: string
    email:
      type: string
  returns:
    type: object
    properties:
      id: string
      displayName: string
      email: string
      department: string
      jobTitle: string

search_azure_users:
  description: Zoek gebruikers in Azure AD
  category: external
  target_resource: azure_ad
  requires_integration: azure_ad
  parameters:
    query:
      type: string
      required: true
    limit:
      type: integer
      default: 10
  returns:
    type: array
    items: object
```

---

## 4. AGENT-TOOL MAPPING

### 4.1 Volledige Mapping Matrix

| Agent | Read Tools | Write Tools | Knowledge Tools | Utility Tools | External Tools |
|-------|------------|-------------|-----------------|---------------|----------------|
| **Risk Agent** | get_risk, search_risks, get_measures_for_risk, get_scope, get_risk_appetite | update_risk, set_attention_quadrant, set_mitigation_approach, link_measure_to_risk | search_knowledge, get_methodology | create_suggestion, request_agent_collaboration | - |
| **Measure Agent** | get_measure, search_measures, get_requirements_for_measure, get_risks_for_measure | create_measure, update_measure, link_measure_to_requirement, link_measure_to_risk | search_knowledge, get_methodology | create_suggestion | - |
| **Compliance Agent** | get_standard, get_requirement, search_requirements, get_applicability_statements, get_requirement_mappings | update_applicability, create_gap_analysis | search_knowledge, get_framework_info | create_suggestion | - |
| **Scope Agent** | get_scope, search_scopes, get_scope_dependencies | create_scope, update_scope, set_bia_ratings, create_dependency | search_knowledge | create_suggestion | - |
| **Policy Agent** | get_policy, search_policies, get_document | create_policy, update_policy | search_knowledge, get_framework_info, get_org_context | create_suggestion | - |
| **Assessment Agent** | get_assessment, search_assessments, get_findings_for_assessment, get_evidence | create_finding, update_finding, assess_evidence | search_knowledge | create_suggestion | - |
| **Incident Agent** | get_incident, search_incidents | create_incident, update_incident, create_corrective_action | search_knowledge, get_framework_info (AVG) | create_suggestion, send_notification | - |
| **Privacy Agent** | get_processing_activity, search_processing_activities, get_dsr, get_processor_agreement | create_processing_activity, update_processing_activity, update_dsr | search_knowledge, get_framework_info (AVG) | create_suggestion | - |
| **BCM Agent** | get_continuity_plan, search_continuity_plans, get_continuity_tests, get_scope (BIA) | create_continuity_plan, update_continuity_plan, create_continuity_test | search_knowledge | create_suggestion | - |
| **Supplier Agent** | get_supplier, search_suppliers, get_supplier_risks, get_processor_agreements | create_supplier_assessment, update_supplier | search_knowledge | create_suggestion, request_agent_collaboration | - |
| **Improvement Agent** | get_issue, search_issues, get_corrective_action, search_corrective_actions, get_initiative | create_issue, update_issue, create_corrective_action, update_corrective_action, create_initiative | search_knowledge | create_suggestion | - |
| **Planning Agent** | get_planning_item, search_planning_items, get_management_review, get_review_schedules | create_planning_item, prepare_management_review_input | search_knowledge | create_suggestion | - |
| **Objectives Agent** | get_objective, search_objectives, get_kpi, get_kpi_measurements | create_objective, update_objective, create_kpi, add_kpi_measurement | search_knowledge | create_suggestion | - |
| **Maturity Agent** | get_maturity_assessment, get_domain_scores | create_maturity_assessment, update_domain_score | search_knowledge | create_suggestion | - |
| **Workflow Agent** | get_workflow_instance, get_workflow_history, get_available_transitions | execute_transition | search_knowledge | create_suggestion | - |
| **Report Agent** | get_report_template, get_dashboard, get_compliance_metrics, get_risk_metrics | create_report_template, generate_report, create_dashboard_widget | search_knowledge | create_suggestion | - |
| **Admin Agent** | get_tenant, get_users, get_integration_config, get_system_settings, get_audit_log | update_tenant_settings, create_user, update_user_roles, update_setting | search_knowledge | create_suggestion | test_integration |

### 4.2 Tool Prioriteit per Agent

Elke agent heeft een prioriteit voor tools (hogere prioriteit = vaker gebruiken):

```yaml
risk_agent:
  high_priority:
    - get_risk
    - search_risks
    - set_attention_quadrant
    - get_methodology
    - create_suggestion
  medium_priority:
    - get_measures_for_risk
    - link_measure_to_risk
    - update_risk
  low_priority:
    - get_scope
    - request_agent_collaboration
```

---

## 5. IMPLEMENTATIE FASES

### 5.1 Fase 1: Core Infrastructure (Week 1-2)

**Doel:** Basis agent systeem werkend

**Taken:**
1. Database tabellen aanmaken (AIAgent, AITool, AIAgentToolAccess, AIToolExecution)
2. Agent Orchestrator service bouwen
   - Context detection
   - Agent selection
   - Tool execution framework
3. Basis LLM integratie (Ollama + Mistral)
4. 2 pilot agents implementeren:
   - Risk Agent (meest complete)
   - Workflow Agent (cross-cutting)

**Deliverables:**
- [ ] Database migraties
- [ ] AgentOrchestrator class
- [ ] ToolExecutor class
- [ ] LLMService class
- [ ] Risk Agent werkend
- [ ] Workflow Agent werkend

### 5.2 Fase 2: Core Agents (Week 3-4)

**Doel:** Alle domein agents werkend

**Taken:**
1. Implementeer alle Read tools
2. Implementeer alle Knowledge tools
3. Implementeer 10 resterende domein agents:
   - Measure Agent
   - Compliance Agent
   - Scope Agent
   - Policy Agent
   - Assessment Agent
   - Incident Agent
   - Privacy Agent
   - BCM Agent
   - Supplier Agent
   - Improvement Agent

**Deliverables:**
- [ ] Alle Read tools
- [ ] Alle Knowledge tools
- [ ] 12 domein agents werkend

### 5.3 Fase 3: Write Tools & Safety (Week 5-6)

**Doel:** Write functionaliteit met beveiliging

**Taken:**
1. Implementeer Write tools met confirmation flow
2. Build suggestion system (AISuggestion)
3. Implementeer audit logging (AIToolExecution)
4. User confirmation UI component
5. Permission checks per tool

**Deliverables:**
- [ ] Alle Write tools
- [ ] Suggestion accept/reject flow
- [ ] Audit trail compleet
- [ ] Permission system

### 5.4 Fase 4: Management & System Agents (Week 7-8)

**Doel:** Complete agent set

**Taken:**
1. Implementeer management agents:
   - Planning Agent
   - Objectives Agent
   - Maturity Agent
2. Implementeer system agents:
   - Report Agent
   - Admin Agent
3. Agent collaboration (request_agent_collaboration)
4. Agent handoff UI

**Deliverables:**
- [ ] 17 agents compleet
- [ ] Agent collaboration werkend
- [ ] Handoff UI

### 5.5 Fase 5: External Integrations (Week 9-10)

**Doel:** TopDesk en Azure AD integratie

**Taken:**
1. TopDesk API integratie
   - search_topdesk
   - get_topdesk_ticket
   - create_topdesk_ticket
2. Azure AD integratie
   - get_azure_user
   - search_azure_users
3. Integration configuration UI
4. Sync logging

**Deliverables:**
- [ ] TopDesk tools werkend
- [ ] Azure AD tools werkend
- [ ] Integration config UI

### 5.6 Fase 6: Optimalisatie (Week 11-12)

**Doel:** Performance en kwaliteit

**Taken:**
1. Response time optimalisatie
2. Token budget tuning
3. Prompt optimalisatie per agent
4. Feedback loop implementatie (was_helpful)
5. Analytics dashboard voor agent performance
6. A/B testing framework voor prompts

**Deliverables:**
- [ ] Response time < 3 sec
- [ ] Token usage optimized
- [ ] Feedback system
- [ ] Analytics dashboard

---

## 6. TECHNISCHE DETAILS

### 6.1 Agent Orchestrator Pseudocode

```python
class AgentOrchestrator:
    def __init__(self, llm_service, tool_executor, knowledge_service):
        self.llm = llm_service
        self.tools = tool_executor
        self.knowledge = knowledge_service

    async def handle_message(
        self,
        conversation: AIConversation,
        user_message: str
    ) -> AgentResponse:

        # 1. Detect context
        context = self.detect_context(conversation)

        # 2. Select agent
        agent = self.select_agent(context, conversation.current_agent_id)

        # 3. Check for agent switch
        if agent.id != conversation.current_agent_id:
            await self.switch_agent(conversation, agent)

        # 4. Build prompt
        prompt = self.build_prompt(agent, context, conversation, user_message)

        # 5. Get available tools for this agent
        tools = self.get_agent_tools(agent)

        # 6. Call LLM with function calling
        response = await self.llm.generate(
            prompt=prompt,
            tools=tools,
            temperature=agent.temperature or 0.7
        )

        # 7. Execute any tool calls
        if response.tool_calls:
            tool_results = await self.execute_tools(
                response.tool_calls,
                agent,
                conversation
            )
            # Re-generate with tool results
            response = await self.llm.generate(
                prompt=prompt,
                tool_results=tool_results
            )

        # 8. Extract and store suggestions
        suggestions = self.extract_suggestions(response)
        for suggestion in suggestions:
            await self.store_suggestion(suggestion, conversation)

        # 9. Store message
        await self.store_message(conversation, "assistant", response.content)

        return AgentResponse(
            content=response.content,
            agent=agent,
            suggestions=suggestions,
            tool_calls_made=response.tool_calls
        )

    def select_agent(self, context: Context, current_agent_id: int) -> AIAgent:
        # Query agents matching context
        matching_agents = AIAgent.query(
            trigger_contexts__contains=context.page,
            is_active=True
        ).order_by('-priority')

        if matching_agents:
            return matching_agents[0]

        # Fallback to current or general agent
        if current_agent_id:
            return AIAgent.get(current_agent_id)

        return AIAgent.get_by_name('general_agent')

    def build_prompt(
        self,
        agent: AIAgent,
        context: Context,
        conversation: AIConversation,
        user_message: str
    ) -> str:
        # System prompt from agent
        system = agent.system_prompt

        # Knowledge context
        knowledge = self.knowledge.get_for_agent(
            agent=agent,
            context=context
        )

        # Organization context
        org_context = self.knowledge.get_org_context(
            tenant_id=context.tenant_id
        )

        # Entity context
        entity_context = self.get_entity_context(context)

        # Conversation history
        history = conversation.get_recent_messages(limit=10)

        return f"""
{system}

## Kennisbank
{knowledge}

## Organisatie Context
{org_context}

## Huidige Situatie
{entity_context}

## Gesprek
{self.format_history(history)}

## Gebruiker
{user_message}
"""
```

### 6.2 Tool Executor Pseudocode

```python
class ToolExecutor:
    def __init__(self, db_session, external_services):
        self.db = db_session
        self.external = external_services
        self.tool_registry = self.load_tools()

    async def execute(
        self,
        tool_call: ToolCall,
        agent: AIAgent,
        conversation: AIConversation
    ) -> ToolResult:

        tool = self.tool_registry.get(tool_call.name)

        # 1. Check permissions
        access = AIAgentToolAccess.get(agent_id=agent.id, tool_id=tool.id)
        if not access or not access.is_active:
            raise PermissionDenied(f"Agent {agent.name} cannot use {tool.name}")

        # 2. Check if confirmation needed
        if tool.requires_confirmation and not access.auto_execute:
            suggestion = await self.create_tool_suggestion(tool_call, agent)
            return ToolResult(
                status="pending_confirmation",
                suggestion_id=suggestion.id
            )

        # 3. Execute tool
        start_time = datetime.now()
        try:
            result = await self.run_tool(tool, tool_call.parameters)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        # 4. Log execution
        await self.log_execution(
            tool=tool,
            agent=agent,
            conversation=conversation,
            parameters=tool_call.parameters,
            result=result,
            success=success,
            error=error,
            duration_ms=(datetime.now() - start_time).milliseconds
        )

        return ToolResult(
            status="success" if success else "error",
            data=result,
            error=error
        )

    async def run_tool(self, tool: AITool, parameters: dict) -> Any:
        # Route to appropriate handler
        if tool.category == "read":
            return await self.execute_read(tool, parameters)
        elif tool.category == "write":
            return await self.execute_write(tool, parameters)
        elif tool.category == "knowledge":
            return await self.execute_knowledge(tool, parameters)
        elif tool.category == "external":
            return await self.execute_external(tool, parameters)
        elif tool.category == "utility":
            return await self.execute_utility(tool, parameters)
```

### 6.3 LLM Service met Function Calling

```python
class LLMService:
    def __init__(self, config: Settings):
        self.base_url = config.AI_API_BASE  # http://localhost:11434/v1
        self.model = config.AI_MODEL_NAME   # mistral

    async def generate(
        self,
        prompt: str,
        tools: List[AITool] = None,
        tool_results: List[ToolResult] = None,
        temperature: float = 0.7
    ) -> LLMResponse:

        messages = [{"role": "user", "content": prompt}]

        if tool_results:
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": result.call_id,
                    "content": json.dumps(result.data)
                })

        request = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if tools:
            request["tools"] = self.format_tools_for_llm(tools)
            request["tool_choice"] = "auto"

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            json=request
        )

        return self.parse_response(response.json())

    def format_tools_for_llm(self, tools: List[AITool]) -> List[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": json.loads(tool.parameters_schema)
                }
            }
            for tool in tools
        ]
```

---

## 7. SUCCESS CRITERIA

| Metric | Target | Meetmethode |
|--------|--------|-------------|
| Agent response time | < 3 seconden | P95 latency |
| Tool execution success | > 95% | Success rate in AIToolExecution |
| Suggestion acceptance | > 60% | Accepted / Total suggestions |
| User satisfaction | > 4/5 | In-app rating |
| Agent handoff success | > 90% | Successful collaborations |
| Context detection accuracy | > 95% | Manual review sample |

---

## 8. RISICO'S EN MITIGATIES

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| LLM hallucineert onjuiste data | Hoog | Alle write acties via confirmation flow |
| Token budget overschrijding | Medium | Strict budget management, prioritization |
| Trage response times | Medium | Caching, async processing, model optimization |
| Agent kiest verkeerde tool | Medium | Tool prioritization, explicit routing rules |
| Privacy data lekt via prompts | Hoog | Tenant isolation, data masking in logs |
| External API downtime | Medium | Graceful degradation, retry logic |
