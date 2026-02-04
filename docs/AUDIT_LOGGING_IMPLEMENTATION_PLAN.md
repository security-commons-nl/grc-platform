# Plan: System-Wide Audit Logging ("The Black Box")

Dit document beschrijft de technische implementatie van een volledig dekkende **Audit Trail** voor het IMS platform. Het is ontworpen voor **NIS2/ISO 27001** compliance en biedt volledige reconstructie-mogelijkheden bij incidenten.

---

## 1. Doelstelling

Elke mutatie (Create, Update, Delete) op datamodellen moet automatisch worden vastgelegd in de `AuditLog` tabel, zonder dat ontwikkelaars hier bij elke API-endpoint over na hoeven te denken.

**Wat loggen we?**
| Veld | Beschrijving | Voorbeeld |
|------|--------------|-----------|
| **Wie** | User ID (uit request context) | `user_id: 42` |
| **Wanneer** | Timestamp (UTC) | `2026-02-04T18:30:00Z` |
| **Wat (Target)** | Entity Type + Entity ID | `Risk #123` |
| **Wat (Diff)** | Oude vs. Nieuwe waarde (JSON) | `{"status": "Draft"} → {"status": "Active"}` |
| **Correlation ID** | Unieke request identifier | `req-abc123-xyz` |
| **Context** | IP adres, User Agent | `192.168.1.1, Chrome/120` |

---

## 2. Architectuur Keuze: SQLAlchemy Event Listeners

We kiezen voor **SQLAlchemy Event Listeners** (specifiek `after_flush`) in plaats van API Middleware.

| Optie | Voordeel | Nadeel |
|-------|----------|--------|
| **API Middleware** | Simpel te implementeren | Ziet alleen de *input*, niet wat daadwerkelijk opgeslagen wordt |
| **SQLAlchemy Events** ✅ | Ziet exacte database state na validatie/defaults | Complexer, vereist context passing |

**Waarom `after_flush`?**
*   Middleware ziet de JSON body, maar weet niet of de database constraints slagen.
*   SQLAlchemy ziet precies welke kolommen "dirty" zijn en wat de definitieve waarden zijn.

### De Uitdaging: "Wie ben ik?"
SQLAlchemy modellen weten van zichzelf niet wie de huidige HTTP-user is.

**Oplossing:** Python's `contextvars` om de user context veilig door te geven van de API laag naar de Database laag.

---

## 3. Implementatie Stappen

### Stap 1: Context Management (`core/context.py`)

```python
from contextvars import ContextVar
import uuid

# Request-scoped context variables (async-safe)
current_user_id: ContextVar[int] = ContextVar("current_user_id", default=None)
current_tenant_id: ContextVar[int] = ContextVar("current_tenant_id", default=None)
correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)
request_ip: ContextVar[str] = ContextVar("request_ip", default=None)
user_agent: ContextVar[str] = ContextVar("user_agent", default=None)

def generate_correlation_id() -> str:
    """Generate unique correlation ID for request tracing."""
    return f"req-{uuid.uuid4().hex[:12]}"
```

### Stap 2: Middleware (`core/middleware.py`)

```python
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import (
    current_user_id, current_tenant_id, correlation_id,
    request_ip, user_agent, generate_correlation_id
)

class AuditContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 1. Generate & set Correlation ID (VERPLICHT)
        corr_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
        correlation_id.set(corr_id)
        
        # 2. Extract user from token (indien aanwezig)
        token = request.headers.get("Authorization")
        if token:
            try:
                user = decode_token(token)  # Your auth logic
                current_user_id.set(user.id)
                current_tenant_id.set(user.tenant_id)
            except Exception:
                pass  # Anonymous request
        
        # 3. Capture request metadata
        request_ip.set(request.client.host if request.client else "unknown")
        user_agent.set(request.headers.get("User-Agent", "unknown"))
        
        # 4. Process request & add correlation ID to response
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = corr_id
        return response
```

### Stap 3: Model-Level Opt-in (`__audit__` flag)

In plaats van een hardcoded lijst, markeert elk model zichzelf als "audit-worthy":

```python
# In core_models.py
class Risk(SQLModel, table=True):
    __audit__ = True  # Dit model wordt gelogd
    # ... fields ...

class AuditLog(SQLModel, table=True):
    __audit__ = False  # Nooit loggen (voorkomt recursie)
    # ... fields ...

class Session(SQLModel, table=True):
    __audit__ = False  # Technische data, niet loggen
    # ... fields ...
```

### Stap 4: The Interceptor (`core/audit.py`)

```python
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session as SASession
from app.models.core_models import AuditLog, AuditAction
from app.core.context import (
    current_user_id, current_tenant_id, correlation_id,
    request_ip, user_agent
)
import json

# Fields die NOOIT in logs mogen verschijnen
MASKED_FIELDS = {"password_hash", "api_key", "secret", "token", "private_key"}

def setup_audit_logging(session_factory):
    """Attach audit listener to session factory."""
    event.listen(session_factory, "after_flush", audit_listener)

def should_audit(obj) -> bool:
    """Check if model should be audited."""
    return getattr(obj.__class__, "__audit__", False)

def is_soft_delete(obj) -> bool:
    """Detect soft delete (deleted_at field set)."""
    if not hasattr(obj, "deleted_at"):
        return False
    state = inspect(obj)
    history = state.attrs.deleted_at.history
    return history.has_changes() and history.added and history.added[0] is not None

def get_model_changes(obj) -> dict:
    """Extract changed fields with old/new values."""
    state = inspect(obj)
    changes = {"old": {}, "new": {}}
    
    for attr in state.attrs:
        if attr.key in MASKED_FIELDS:
            continue  # Skip sensitive fields
        history = attr.history
        if history.has_changes():
            old_val = history.deleted[0] if history.deleted else None
            new_val = history.added[0] if history.added else None
            # Convert to JSON-serializable
            changes["old"][attr.key] = str(old_val) if old_val else None
            changes["new"][attr.key] = str(new_val) if new_val else None
    
    return changes if changes["old"] or changes["new"] else None

def audit_listener(session: SASession, flush_context):
    """Core audit logic - runs after every flush."""
    user_id = current_user_id.get()
    tenant_id = current_tenant_id.get()
    corr_id = correlation_id.get()
    
    logs_to_add = []
    
    # Created objects
    for obj in session.new:
        if not should_audit(obj):
            continue
        logs_to_add.append(AuditLog(
            tenant_id=getattr(obj, "tenant_id", tenant_id),
            entity_type=obj.__class__.__name__,
            entity_id=obj.id,
            action=AuditAction.CREATE,
            new_value=json.dumps({"id": obj.id}),
            changed_by_id=user_id,
            correlation_id=corr_id,
            ip_address=request_ip.get(),
            user_agent=user_agent.get(),
        ))
    
    # Updated objects
    for obj in session.dirty:
        if not should_audit(obj):
            continue
        
        # Detect soft delete
        if is_soft_delete(obj):
            action = AuditAction.DELETE
            changes = None
        else:
            action = AuditAction.UPDATE
            changes = get_model_changes(obj)
            if not changes:
                continue  # No actual changes
        
        logs_to_add.append(AuditLog(
            tenant_id=getattr(obj, "tenant_id", tenant_id),
            entity_type=obj.__class__.__name__,
            entity_id=obj.id,
            action=action,
            old_value=json.dumps(changes["old"]) if changes else None,
            new_value=json.dumps(changes["new"]) if changes else None,
            changed_by_id=user_id,
            correlation_id=corr_id,
            ip_address=request_ip.get(),
            user_agent=user_agent.get(),
        ))
    
    # Hard deleted objects
    for obj in session.deleted:
        if not should_audit(obj):
            continue
        logs_to_add.append(AuditLog(
            tenant_id=getattr(obj, "tenant_id", tenant_id),
            entity_type=obj.__class__.__name__,
            entity_id=obj.id,
            action=AuditAction.DELETE,
            old_value=json.dumps({"id": obj.id}),
            changed_by_id=user_id,
            correlation_id=corr_id,
            ip_address=request_ip.get(),
            user_agent=user_agent.get(),
        ))
    
    # Add all logs to session (will be persisted in same transaction)
    for log in logs_to_add:
        session.add(log)
```

---

## 4. Functionaliteiten & Rules

### 4.1 Model Audit Status

| Model | `__audit__` | Reden |
|-------|-------------|-------|
| `Risk` | ✅ True | Core business data |
| `Control` | ✅ True | Core business data |
| `Measure` | ✅ True | Policy/norm data |
| `User` | ✅ True | Gebruikersbeheer |
| `Incident` | ✅ True | Security events |
| `AuditLog` | ❌ False | Voorkomt recursie |
| `Session` | ❌ False | Technisch/ephemeral |
| `Notification` | ❌ False | Transactioneel, geen business waarde |

### 4.2 Diff Engine
Bij een `UPDATE` slaan we alleen de gewijzigde velden op:
```json
// Voorbeeld: Alleen title gewijzigd
{
  "old": {"title": "Oude Naam"},
  "new": {"title": "Nieuwe Naam"}
}
```

### 4.3 Sensitive Data Masking
Velden in `MASKED_FIELDS` worden **nooit** gelogd:
*   `password_hash`
*   `api_key`
*   `secret`
*   `token`
*   `private_key`

### 4.4 Soft Delete Detectie
Als een model `deleted_at` heeft en dit veld wordt gezet, registreren we dit als een `DELETE` actie in plaats van `UPDATE`.

---

## 5. Bekende Beperkingen

> [!CAUTION]
> **Bulk Operations Bypass**
> 
> De volgende operaties **omzeilen** de SQLAlchemy event listeners:
> *   `session.bulk_update_mappings()`
> *   `session.bulk_insert_mappings()`
> *   Raw SQL queries (`session.execute(text("UPDATE ..."))`)
>
> **Beleid:** Deze functies zijn **verboden** voor audit-plichtige modellen. Gebruik altijd ORM-operaties voor `__audit__ = True` modellen.

---

## 6. Roadmap Implementatie

| Fase | Onderdeel | Geschatte Tijd |
|------|-----------|----------------|
| 1 | `core/context.py` + Middleware | 2 uur |
| 2 | `core/audit.py` (listener + diff logic) | 4 uur |
| 3 | `__audit__` flag toevoegen aan modellen | 1 uur |
| 4 | Integratie met `db.py` session factory | 1 uur |
| 5 | Testing & Verificatie | 2 uur |

**Totaal:** ~10 uur development

---

## 7. Risico's & Mitigatie

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| **Performance** | Elke write = 2 writes | Acceptabel voor IMS (integriteit > snelheid) |
| **Recursie** | Infinite loop crash | `should_audit()` check + `__audit__ = False` op AuditLog |
| **Bulk bypass** | Ontbrekende logs | Verbod op bulk ops voor audit modellen |
| **Context verlies** | Ontbrekende user_id | `current_user_id` default to `None` (system action) |

---

## 8. Compliance Waarde

Dit systeem biedt:
*   **NIS2 Artikel 21:** Incident response & logging vereisten
*   **ISO 27001 A.12.4:** Logging and monitoring controls
*   **AVG Artikel 30:** Verwerkingsactiviteiten kunnen worden gereconstrueerd
*   **Forensische waarde:** Volledige reconstructie "Wie deed wat, wanneer, en waarom?"

---

**Status:** ✅ Ready for Development
