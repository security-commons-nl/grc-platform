import asyncio
from typing import List, Optional

import reflex as rx
from .base import BaseState
from ..api.client import api_client

class IsmsImplementerState(BaseState):
    """
    State for the ISMS Implementation Guide (ISO 27001).
    Manages the 7-step process and data for each step.
    """
    
    # UI Control
    active_step: int = 1
    
    # Data Loading
    is_loading: bool = False
    error: str = ""
    
    # --- Step 1 Data (Context) ---
    stakeholders: List[dict] = []
    organization_profile: Optional[dict] = None
    organization_context: List[dict] = [] # SWOT/PESTLE items
    scopes: List[dict] = []
    
    # --- Step 2 Data (Leadership) ---
    policies: List[dict] = []
    objectives: List[dict] = []
    risk_appetite: Optional[dict] = None
    
    # --- Step 3 Data (Planning) ---
    risks: List[dict] = []
    risk_framework: Optional[dict] = None
    
    # ... other steps data can be loaded on demand or initially
    
    async def load_data(self):
        """Load initial data for the implementer page."""
        self.is_loading = True
        self.error = ""
        
        try:
            # Helper for safe fetching
            async def safe_fetch(coro):
                try:
                    return await coro
                except Exception as e:
                    print(f"Fetch error: {e}")
                    return [] if "list" in str(type(coro)).lower() else None

            # Parallel fetch of core data needed for the overview
            # We fetch Step 1 & 2 data initially as they are most critical
            results = await asyncio.gather(
                safe_fetch(api_client.get_stakeholders()),
                safe_fetch(api_client.get_organization_profile()),
                safe_fetch(api_client.get_policies()),
                safe_fetch(api_client.get_risks(limit=10)), # Just a sample to show status
                safe_fetch(api_client.get_scopes()),
            )
            
            self.stakeholders = results[0] or []
            self.organization_profile = results[1]
            self.policies = results[2] or []
            self.risks = results[3] or []
            self.scopes = results[4] or []
            
            # Context (SWOT) is usually fetched via generic "context" endpoint if exists, 
            # or we might need to filter a generic table. 
            # For now, we assume we might need to add a method to client or use existing.
            # let's skip explicit context fetch for now until we confirmed the endpoint.
            
        except Exception as e:
            self.error = f"Kon data niet laden: {str(e)}"
            print(f"ISMS Load Error: {e}")
        
        self.is_loading = False
        
    def set_step(self, step: int):
        self.active_step = step

    # --- Actions for Step 1 ---

    async def add_stakeholder_from_ui(self):
        """Create a new stakeholder from the UI form."""
        form_data = await self.get_state(rx.State.get_value("sh_name"), rx.State.get_value("sh_type"), rx.State.get_value("sh_reqs"), rx.State.get_value("sh_rel")) 
        # Reflex weirdness with get_value... let's try a different approach.
        # Actually reflex form handling usually involves State vars bound to input value.
        pass

    # We need bound variables for the form
    new_stakeholder_name: str = ""
    new_stakeholder_type: str = "Internal"
    new_stakeholder_reqs: str = ""
    new_stakeholder_rel: str = "High"

    async def add_stakeholder(self):
        """Create a new stakeholder."""
        if not self.new_stakeholder_name:
            return
            
        try:
            data = {
                "name": self.new_stakeholder_name,
                "type": self.new_stakeholder_type,
                "requirements": self.new_stakeholder_reqs,
                "relevance_level": self.new_stakeholder_rel,
                "tenant_id": 1 # Should be dynamic but for now
            }
            await api_client.create_stakeholder(data)
            
            # Refresh list
            self.stakeholders = await api_client.get_stakeholders()
            
            # Reset form
            self.new_stakeholder_name = ""
            self.new_stakeholder_reqs = ""
            
        except Exception as e:
            self.error = f"Fout bij toevoegen stakeholder: {str(e)}"
        
    async def delete_stakeholder(self, id: int):
        """Delete a stakeholder."""
        try:
            await api_client.delete_stakeholder(id)
            # Remove from local list to avoid re-fetch or just re-fetch
            self.stakeholders = [s for s in self.stakeholders if s["id"] != id]
        except Exception as e:
            self.error = f"Fout bij verwijderen stakeholder: {str(e)}"

    # --- Actions for Scope ---
    
    new_scope_description: str = ""
    
    async def add_scope(self):
        """Add a scope definition."""
        if not self.new_scope_description:
            return
            
        try:
            # We treat scope as a single item or list of items defining the ISMS boundaries
            data = {"description": self.new_scope_description, "tenant_id": 1}
            # Assuming create_scope exists, if not we might need to adapt
            await api_client.create_scope(data) # Placeholder if not exists
            
            self.scopes = await api_client.get_scopes()
            self.new_scope_description = ""
        except Exception as e:
            self.error = f"Fout bij toevoegen scope: {str(e)}"

    async def delete_scope(self, id: int):
        try:
            await api_client.delete_scope(id)
            self.scopes = [s for s in self.scopes if s["id"] != id]
        except Exception as e:
            self.error = f"Fout bij verwijderen scope: {str(e)}"

    # --- Progress Calculation ---

    @rx.var
    def context_progress(self) -> int:
        """
        Calculate percentage completion for Context phase.
        Based on:
        1. Issues/Context (using organization_profile or context items) - 33%
        2. Stakeholders (at least 1) - 33%
        3. Scope (at least 1) - 34%
        """
        progress = 0
        
        # 1. Context / Issues (simple check if profile exists for now, or use context items if valid)
        if self.organization_profile: 
            progress += 33
            
        # 2. Stakeholders
        if self.stakeholders and len(self.stakeholders) > 0:
            progress += 33
            
        # 3. Scope
        if self.scopes and len(self.scopes) > 0:
            progress += 34
            
        return progress

    @rx.var
    def has_context_issues(self) -> bool:
        return self.organization_profile is not None

    @rx.var
    def has_stakeholders(self) -> bool:
        return len(self.stakeholders) > 0

    @rx.var
    def has_scope(self) -> bool:
        return len(self.scopes) > 0

