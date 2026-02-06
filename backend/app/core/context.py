from contextvars import ContextVar
from typing import Optional

# Context variable to store the current tenant ID
tenant_context: ContextVar[Optional[int]] = ContextVar("tenant_context", default=None)

def get_current_tenant_id() -> Optional[int]:
    return tenant_context.get()

def set_current_tenant_id(tenant_id: int):
    return tenant_context.set(tenant_id)
