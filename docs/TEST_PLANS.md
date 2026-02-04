# IMS Test Plannen

Dit document bevat gedetailleerde testplannen voor elke implementatiefase.

---

## Fase 1: Foundation - Test Plan

### 1.1 Database & Migraties

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F1-DB-01 | Database connectie | Integration | PostgreSQL connectie succesvol |
| F1-DB-02 | pgvector extensie | Integration | `CREATE EXTENSION vector` werkt |
| F1-DB-03 | Alembic migratie up | Integration | `alembic upgrade head` zonder errors |
| F1-DB-04 | Alembic migratie down | Integration | `alembic downgrade -1` zonder errors |
| F1-DB-05 | Schema creatie | Integration | Alle 85+ tabellen aangemaakt |
| F1-DB-06 | Foreign keys | Unit | Relaties correct gedefinieerd |

**Handmatige test stappen:**
```bash
# Start database
docker-compose up -d db

# Test connectie
psql -h localhost -U postgres -d ims -c "SELECT 1"

# Test pgvector
psql -h localhost -U postgres -d ims -c "CREATE EXTENSION IF NOT EXISTS vector"

# Test migraties
cd backend
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

---

### 1.2 FastAPI Basis

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F1-API-01 | Server start | Smoke | `uvicorn` start zonder errors |
| F1-API-02 | Health endpoint | Integration | `GET /health` returns 200 |
| F1-API-03 | OpenAPI docs | Integration | `GET /docs` laadt Swagger UI |
| F1-API-04 | CORS headers | Integration | CORS headers aanwezig in response |
| F1-API-05 | Error handling | Unit | 404/500 responses correct format |

**Handmatige test stappen:**
```bash
# Start API
cd backend
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl http://localhost:8000/api/v1/risks/
```

---

### 1.3 Core CRUD Endpoints

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F1-CRUD-01 | Create Risk | Integration | POST /risks/ returns 200 + created object |
| F1-CRUD-02 | Read Risk | Integration | GET /risks/{id} returns object |
| F1-CRUD-03 | Update Risk | Integration | PATCH /risks/{id} updates fields |
| F1-CRUD-04 | Delete Risk | Integration | DELETE /risks/{id} removes object |
| F1-CRUD-05 | List Risks | Integration | GET /risks/ returns array |
| F1-CRUD-06 | Filter Risks | Integration | Query params filter results |
| F1-CRUD-07 | Pagination | Integration | skip/limit params work |
| F1-CRUD-08 | Create Measure | Integration | POST /measures/ returns 200 |
| F1-CRUD-09 | Create Scope | Integration | POST /scopes/ returns 200 |
| F1-CRUD-10 | Create Tenant | Integration | POST /tenants/ returns 200 |

**Pytest tests:** `backend/tests/test_risks.py`

---

### 1.4 Multi-Tenancy

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F1-MT-01 | Tenant header required | Integration | Request zonder X-Tenant-ID faalt |
| F1-MT-02 | Tenant isolation read | Integration | Tenant 1 ziet geen data van Tenant 2 |
| F1-MT-03 | Tenant isolation write | Integration | Create zet correct tenant_id |
| F1-MT-04 | Cross-tenant access denied | Security | GET op andere tenant's object = 404 |
| F1-MT-05 | Tenant in all queries | Code Review | Alle endpoints gebruiken tenant filter |

**Test stappen:**
```bash
# Create data for tenant 1
curl -X POST http://localhost:8000/api/v1/risks/ \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Tenant 1 Risk", "tenant_id": 1}'

# Verify tenant 2 cannot see it
curl http://localhost:8000/api/v1/risks/ \
  -H "X-Tenant-ID: 2"
# Should return empty array or not include Tenant 1's risk
```

---

## Fase 2: Core Features - Test Plan

### 2.1 Workflow Engine

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-WF-01 | Policy: Draft → Review | Integration | State transition succeeds |
| F2-WF-02 | Policy: Review → Approved | Integration | State transition succeeds |
| F2-WF-03 | Policy: Approved → Published | Integration | State transition succeeds |
| F2-WF-04 | Policy: Published → Archived | Integration | State transition succeeds |
| F2-WF-05 | Policy: Skip step blocked | Integration | Draft → Published fails |
| F2-WF-06 | Policy: Reject returns to Draft | Integration | Review → Draft succeeds |
| F2-WF-07 | Policy: Edit blocked when Published | Integration | PATCH on Published fails |
| F2-WF-08 | Policy: Delete blocked when Published | Integration | DELETE on Published fails |
| F2-WF-09 | Policy: New version creates Draft | Integration | POST /new-version creates v2 |
| F2-WF-10 | Risk acceptance workflow | Integration | Accept sets risk_accepted=true |

**Pytest tests:** `backend/tests/test_policies.py`

---

### 2.2 Assessment Module

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-AS-01 | Create Assessment | Integration | POST /assessments/ returns 200 |
| F2-AS-02 | Assessment types | Integration | Audit/DPIA/Pentest types supported |
| F2-AS-03 | Add Finding | Integration | POST /assessments/{id}/findings works |
| F2-AS-04 | Add Evidence | Integration | POST /findings/{id}/evidence works |
| F2-AS-05 | Assessment lifecycle | Integration | Planned → Active → Completed |
| F2-AS-06 | Link to Scope | Integration | Assessment linked to scope |
| F2-AS-07 | Questions & Responses | Integration | Self-assessment flow works |

**Test stappen:**
```bash
# Create assessment
curl -X POST http://localhost:8000/api/v1/assessments/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Q1 Audit", "assessment_type": "Internal Audit", "tenant_id": 1}'

# Add finding
curl -X POST http://localhost:8000/api/v1/assessments/1/findings \
  -H "Content-Type: application/json" \
  -d '{"title": "Missing policy", "severity": "Medium"}'
```

---

### 2.3 Compliance/SoA Module

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-SOA-01 | Initialize SoA from Standard | Integration | Creates entries for all requirements |
| F2-SOA-02 | Update applicability | Integration | PATCH is_applicable works |
| F2-SOA-03 | Link measure to requirement | Integration | MeasureRequirementLink created |
| F2-SOA-04 | Gap analysis | Integration | Returns non-compliant requirements |
| F2-SOA-05 | SoA summary | Integration | Returns compliance percentages |
| F2-SOA-06 | Multiple standards | Integration | BIO + ISO 27001 both supported |

**Test stappen:**
```bash
# Create standard with requirements
curl -X POST http://localhost:8000/api/v1/standards/ \
  -d '{"name": "BIO", "version": "1.0"}'

# Initialize SoA
curl -X POST http://localhost:8000/api/v1/soa/scope/1/initialize-from-standard/1

# Get gaps
curl http://localhost:8000/api/v1/soa/scope/1/gaps
```

---

### 2.4 Reporting

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-RP-01 | Executive dashboard | Integration | Returns summary stats |
| F2-RP-02 | Risk heatmap data | Integration | Returns quadrant counts |
| F2-RP-03 | Compliance overview | Integration | Returns compliance % |
| F2-RP-04 | Filter by tenant | Integration | Reports respect tenant |
| F2-RP-05 | Filter by scope | Integration | Reports filter by scope |

---

### 2.5 Incident Management

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-IN-01 | Create Incident | Integration | POST /incidents/ returns 200 |
| F2-IN-02 | Severity levels | Integration | Critical/High/Medium/Low supported |
| F2-IN-03 | Data breach flag | Integration | is_data_breach field works |
| F2-IN-04 | Link to Risk | Integration | Incident links to existing risk |
| F2-IN-05 | Corrective Action | Integration | Create CA from incident |
| F2-IN-06 | Incident timeline | Integration | Status changes logged |

---

### 2.6 Measures/Controls

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F2-ME-01 | Create Measure | Integration | POST /measures/ returns 200 |
| F2-ME-02 | Activate Measure | Integration | POST /measures/{id}/activate works |
| F2-ME-03 | Deactivate Measure | Integration | POST /measures/{id}/deactivate works |
| F2-ME-04 | Effectiveness score | Integration | PATCH effectiveness works |
| F2-ME-05 | Link to Risk | Integration | POST /measures/{id}/risks/{rid} works |
| F2-ME-06 | Link to Requirement | Integration | POST /measures/{id}/requirements/{rid} works |
| F2-ME-07 | Stats by status | Integration | GET /measures/stats/by-status works |
| F2-ME-08 | RAG indexing | Integration | Measure indexed on create |

**Pytest tests:** `backend/tests/test_measures.py`

---

## Fase 3: AI Integration - Test Plan

### 3.1 Ollama/LLM Connectivity

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-LLM-01 | Ollama server running | Smoke | `curl http://localhost:11434/api/tags` returns 200 |
| F3-LLM-02 | Mistral model loaded | Smoke | Model "mistral" in available models |
| F3-LLM-03 | Embedding model loaded | Smoke | Model "nomic-embed-text" available |
| F3-LLM-04 | Basic completion | Integration | Simple prompt returns response |
| F3-LLM-05 | Timeout handling | Integration | Long request times out gracefully |
| F3-LLM-06 | Error handling | Integration | Ollama down returns graceful error |

**Handmatige test stappen:**
```bash
# Check Ollama running
curl http://localhost:11434/api/tags

# Pull models if needed
ollama pull mistral
ollama pull nomic-embed-text

# Test completion
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Wat is informatiebeveiliging?",
  "stream": false
}'
```

---

### 3.2 Knowledge Base / RAG

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-KB-01 | Add knowledge entry | Integration | `add_knowledge()` returns entry with embedding |
| F3-KB-02 | Embedding generation | Integration | Vector has correct dimensions (nomic = 768) |
| F3-KB-03 | Semantic search | Integration | `search_knowledge()` returns relevant results |
| F3-KB-04 | Search ranking | Integration | Most relevant result is first |
| F3-KB-05 | Empty query handling | Integration | Empty search returns empty array |
| F3-KB-06 | Category filtering | Integration | Search can filter by category |
| F3-KB-07 | Policy auto-index | Integration | Published policy appears in KB |
| F3-KB-08 | Risk auto-index | Integration | Created risk appears in KB |
| F3-KB-09 | Measure auto-index | Integration | Created measure appears in KB |
| F3-KB-10 | Requirement auto-index | Integration | Created requirement appears in KB |

**Test stappen:**
```bash
# Seed knowledge
cd backend
python -m app.scripts.seed_knowledge

# Test search via agent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat is het In Control model?", "agent_name": "risk"}'
```

---

### 3.3 AI Agents - Core

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-AG-01 | List agents | Integration | GET /agents/ returns 17 agents |
| F3-AG-02 | Agent health check | Integration | GET /agents/health returns healthy |
| F3-AG-03 | Risk agent chat | Integration | POST /agents/chat with risk agent works |
| F3-AG-04 | Compliance agent chat | Integration | POST /agents/chat with compliance agent works |
| F3-AG-05 | Agent detection | Integration | GET /agents/detect returns correct agent for page |
| F3-AG-06 | Context passing | Integration | Context (page, entity_id) passed to agent |
| F3-AG-07 | Unknown agent fallback | Integration | Unknown agent falls back to risk |
| F3-AG-08 | Empty message handling | Integration | Empty message returns helpful response |

**Test stappen:**
```bash
# List agents
curl http://localhost:8000/api/v1/agents/

# Health check
curl http://localhost:8000/api/v1/agents/health

# Chat with risk agent
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hoe classificeer ik een risico met hoge impact en lage kwetsbaarheid?", "agent_name": "risk"}'

# Test agent detection
curl "http://localhost:8000/api/v1/agents/detect?page=risks"
curl "http://localhost:8000/api/v1/agents/detect?page=policies"
curl "http://localhost:8000/api/v1/agents/detect?entity_type=incident"
```

---

### 3.4 AI Agents - Domain Specific

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-DOM-01 | Risk agent: classify_risk tool | Integration | Tool returns correct quadrant |
| F3-DOM-02 | Risk agent: search_knowledge tool | Integration | Tool returns KB results |
| F3-DOM-03 | Measure agent: list_measures tool | Integration | Tool returns measures |
| F3-DOM-04 | Policy agent: get_policy tool | Integration | Tool returns policy details |
| F3-DOM-05 | Privacy agent: AVG guidance | Functional | Agent knows AVG/GDPR basics |
| F3-DOM-06 | BCM agent: BIA guidance | Functional | Agent knows RTO/RPO concepts |
| F3-DOM-07 | Incident agent: breach advice | Functional | Agent advises on AP meldplicht |
| F3-DOM-08 | Compliance agent: BIO knowledge | Functional | Agent knows BIO framework |

**Test stappen:**
```bash
# Test Risk agent quadrant classification
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Classificeer een risico met HOGE impact en LAGE kwetsbaarheid", "agent_name": "risk"}'
# Expected: Agent mentions "ZEKERHEID/ASSURANCE" quadrant

# Test Privacy agent AVG knowledge
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat zijn de grondslagen voor verwerking onder de AVG?", "agent_name": "privacy"}'
# Expected: Agent lists 6 legal bases

# Test Incident agent breach advice
curl -X POST http://localhost:8000/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "We hebben een datalek ontdekt. Wat moeten we doen?", "agent_name": "incident"}'
# Expected: Agent mentions 72-hour AP notification
```

---

### 3.5 AI Tools

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-TL-01 | get_risk tool | Integration | Returns risk details |
| F3-TL-02 | list_risks tool | Integration | Returns risk list |
| F3-TL-03 | search_risks tool | Integration | Searches by title/description |
| F3-TL-04 | get_measure tool | Integration | Returns measure details |
| F3-TL-05 | list_measures tool | Integration | Returns measure list |
| F3-TL-06 | get_policy tool | Integration | Returns policy details |
| F3-TL-07 | create_risk tool | Integration | Creates risk in database |
| F3-TL-08 | update_risk tool | Integration | Updates risk in database |
| F3-TL-09 | create_measure tool | Integration | Creates measure in database |
| F3-TL-10 | link_measure_to_risk tool | Integration | Creates MeasureRiskLink |
| F3-TL-11 | create_corrective_action tool | Integration | Creates CA in database |
| F3-TL-12 | search_knowledge tool | Integration | Returns KB results |
| F3-TL-13 | get_methodology tool | Integration | Returns methodology info |
| F3-TL-14 | classify_risk_quadrant tool | Integration | Returns correct quadrant |

**Test: Direct tool invocation (Python)**
```python
# backend/tests/test_ai_tools.py
import pytest
from app.agents.tools.read_tools import get_risk, list_risks
from app.agents.tools.knowledge_tools import classify_risk_quadrant

@pytest.mark.asyncio
async def test_classify_risk_quadrant():
    result = classify_risk_quadrant.invoke({"impact": "HIGH", "vulnerability": "LOW"})
    assert "ASSURANCE" in result or "ZEKERHEID" in result

@pytest.mark.asyncio
async def test_get_methodology():
    from app.agents.tools.knowledge_tools import get_methodology
    result = get_methodology.invoke({"methodology_name": "in_control"})
    assert "MITIGATE" in result
    assert "ACCEPT" in result
```

---

### 3.6 Chat Island UI

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-UI-01 | Toggle button visible | E2E | Floating button in bottom-right |
| F3-UI-02 | Panel opens on click | E2E | Chat panel expands |
| F3-UI-03 | Panel closes on X | E2E | Panel collapses |
| F3-UI-04 | Agent selector works | E2E | Dropdown changes agent |
| F3-UI-05 | Send message | E2E | Message appears in chat |
| F3-UI-06 | Receive response | E2E | AI response appears |
| F3-UI-07 | Loading state | E2E | Spinner shown while waiting |
| F3-UI-08 | Clear conversation | E2E | Trash button clears messages |
| F3-UI-09 | Error handling | E2E | Error shown on API failure |
| F3-UI-10 | Auto-detect agent | E2E | Agent changes based on page |

**Handmatige UI test stappen:**
1. Open http://localhost:3000 (na `reflex run`)
2. Log in
3. Klik op chat bubble (rechtsonder)
4. Verifieer: panel opent met agent selector
5. Type vraag en druk Enter
6. Verifieer: loading spinner verschijnt
7. Verifieer: AI antwoord verschijnt
8. Wissel agent via dropdown
9. Klik prullenbak - chat wordt geleegd
10. Klik X - panel sluit

---

### 3.7 Agent Orchestration

| Test ID | Test Case | Type | Acceptatiecriteria |
|---------|-----------|------|-------------------|
| F3-OR-01 | All 17 agents registered | Unit | orchestrator.list_agents() returns 17 |
| F3-OR-02 | Context detection: risks page | Unit | Returns "risk" agent |
| F3-OR-03 | Context detection: policies page | Unit | Returns "policy" agent |
| F3-OR-04 | Context detection: compliance page | Unit | Returns "compliance" agent |
| F3-OR-05 | Context detection: incidents page | Unit | Returns "incident" agent |
| F3-OR-06 | Context detection: unknown page | Unit | Returns "risk" (default) |
| F3-OR-07 | Route request to correct agent | Integration | Message handled by specified agent |

**Test: Orchestrator (Python)**
```python
# backend/tests/test_orchestrator.py
from app.agents.core.orchestrator import orchestrator

def test_all_agents_registered():
    agents = orchestrator.list_agents()
    assert len(agents) == 17

def test_context_detection_risks():
    agent = orchestrator.detect_agent_from_context(page="risks")
    assert agent == "risk"

def test_context_detection_policies():
    agent = orchestrator.detect_agent_from_context(page="policies")
    assert agent == "policy"

def test_context_detection_unknown():
    agent = orchestrator.detect_agent_from_context(page="unknown_page")
    assert agent == "risk"  # default fallback
```

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Docker containers running (`docker-compose up -d`)
- [ ] Database migrated (`alembic upgrade head`)
- [ ] API running (`uvicorn app.main:app --reload`)
- [ ] Test data seeded (if applicable)
- [ ] Ollama running with models (Fase 3)
- [ ] Frontend running (`reflex run`) (Fase 3 UI tests)

### Fase 1: Foundation (26 tests)
- [ ] F1-DB-01 through F1-DB-06 (Database)
- [ ] F1-API-01 through F1-API-05 (FastAPI)
- [ ] F1-CRUD-01 through F1-CRUD-10 (CRUD)
- [ ] F1-MT-01 through F1-MT-05 (Multi-tenancy)

### Fase 2: Core Features (42 tests)
- [ ] F2-WF-01 through F2-WF-10 (Workflow)
- [ ] F2-AS-01 through F2-AS-07 (Assessment)
- [ ] F2-SOA-01 through F2-SOA-06 (Compliance)
- [ ] F2-RP-01 through F2-RP-05 (Reporting)
- [ ] F2-IN-01 through F2-IN-06 (Incidents)
- [ ] F2-ME-01 through F2-ME-08 (Measures)

### Fase 3: AI Integration (55 tests)
- [ ] F3-LLM-01 through F3-LLM-06 (Ollama/LLM)
- [ ] F3-KB-01 through F3-KB-10 (Knowledge Base)
- [ ] F3-AG-01 through F3-AG-08 (Agents Core)
- [ ] F3-DOM-01 through F3-DOM-08 (Domain Agents)
- [ ] F3-TL-01 through F3-TL-14 (AI Tools)
- [ ] F3-UI-01 through F3-UI-10 (Chat Island UI)
- [ ] F3-OR-01 through F3-OR-07 (Orchestration)

### Post-Test
- [ ] All critical tests passed
- [ ] Defects logged in backlog
- [ ] Test report generated

---

## Defect Template

```markdown
## Defect: [ID] [Title]

**Test Case:** F1-XX-XX
**Severity:** Critical / High / Medium / Low
**Status:** Open / In Progress / Resolved

**Steps to Reproduce:**
1. ...
2. ...

**Expected Result:**
...

**Actual Result:**
...

**Environment:**
- OS:
- Python:
- Database:

**Notes:**
...
```

---

*Gegenereerd op 4 februari 2025*
