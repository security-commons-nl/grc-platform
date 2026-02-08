"""
Organization Profile State — wizard + profile management.
All vars are flat primitives (no nested dicts — Reflex pitfall).
"""
import reflex as rx
from typing import Any, Dict
from ims.api.client import api_client


class OrganizationProfileState(rx.State):
    """State for the organization profile / onboarding wizard."""

    # --- Load state ---
    profile_loaded: bool = False
    is_saving: bool = False
    error: str = ""

    # --- Wizard meta ---
    wizard_completed: bool = False
    wizard_current_step: int = 0
    active_step: int = 0
    completion_pct: int = 0
    show_wizard: bool = False  # True = wizard mode, False = profile view

    # --- Blok 1: Identiteit ---
    org_type: str = ""
    sector: str = ""
    employee_count: str = ""
    location_count: str = ""
    geographic_scope: str = ""
    parent_organization: str = ""
    core_services: str = ""

    # --- Blok 2: Governance ---
    existing_certifications: str = ""
    applicable_frameworks: str = ""
    has_security_officer: str = ""  # "true"/"false"/""
    has_dpo: str = ""
    governance_maturity: str = ""
    risk_appetite_availability: str = ""
    risk_appetite_integrity: str = ""
    risk_appetite_confidentiality: str = ""

    # --- Blok 3: IT-Landschap ---
    cloud_strategy: str = ""
    cloud_providers: str = ""
    workstation_count: str = ""
    has_remote_work: str = ""
    has_byod: str = ""
    critical_systems: str = ""
    outsourced_it: str = ""
    primary_it_supplier: str = ""

    # --- Blok 4: Privacy ---
    processes_personal_data: str = ""
    data_subject_types: str = ""
    has_special_categories: str = ""
    international_transfers: str = ""
    processing_count_estimate: str = ""

    # --- Blok 5: Continuiteit ---
    has_bcp: str = ""
    has_incident_response_plan: str = ""
    max_tolerable_downtime: str = ""
    critical_process_count: str = ""
    key_dependencies: str = ""

    # --- Blok 6: Mensen ---
    has_awareness_program: str = ""
    has_background_checks: str = ""
    training_frequency: str = ""

    # Bool fields that need string<->bool conversion for the API
    _BOOL_FIELDS = [
        "has_security_officer", "has_dpo", "has_remote_work", "has_byod",
        "outsourced_it", "processes_personal_data", "has_special_categories",
        "international_transfers", "has_bcp", "has_incident_response_plan",
        "has_awareness_program", "has_background_checks",
    ]

    # Int fields
    _INT_FIELDS = ["location_count", "critical_process_count"]

    # Step field groups (matches backend STEP_FIELDS)
    _STEP_FIELDS = {
        0: ["org_type", "sector", "employee_count", "location_count",
            "geographic_scope", "parent_organization", "core_services"],
        1: ["existing_certifications", "applicable_frameworks", "has_security_officer",
            "has_dpo", "governance_maturity", "risk_appetite_availability",
            "risk_appetite_integrity", "risk_appetite_confidentiality"],
        2: ["cloud_strategy", "cloud_providers", "workstation_count", "has_remote_work",
            "has_byod", "critical_systems", "outsourced_it", "primary_it_supplier"],
        3: ["processes_personal_data", "data_subject_types", "has_special_categories",
            "international_transfers", "processing_count_estimate"],
        4: ["has_bcp", "has_incident_response_plan", "max_tolerable_downtime",
            "critical_process_count", "key_dependencies"],
        5: ["has_awareness_program", "has_background_checks", "training_frequency"],
    }

    def _bool_to_str(self, val) -> str:
        if val is None:
            return ""
        return "true" if val else "false"

    def _str_to_bool(self, val: str):
        if val == "true":
            return True
        if val == "false":
            return False
        return None

    def _populate_from_data(self, data: dict):
        """Fill state vars from API response dict."""
        for key in self._STEP_FIELDS[0] + self._STEP_FIELDS[1] + self._STEP_FIELDS[2] + self._STEP_FIELDS[3] + self._STEP_FIELDS[4] + self._STEP_FIELDS[5]:
            val = data.get(key)
            if key in self._BOOL_FIELDS:
                setattr(self, key, self._bool_to_str(val))
            elif key in self._INT_FIELDS:
                setattr(self, key, str(val) if val is not None else "")
            else:
                setattr(self, key, str(val) if val is not None else "")
        self.wizard_completed = data.get("wizard_completed", False)
        self.wizard_current_step = data.get("wizard_current_step", 0)
        self.completion_pct = data.get("completion_pct", 0)

    def _build_step_payload(self, step: int) -> dict:
        """Build dict payload for a single wizard step."""
        payload = {}
        for field in self._STEP_FIELDS.get(step, []):
            val = getattr(self, field, "")
            if field in self._BOOL_FIELDS:
                payload[field] = self._str_to_bool(val)
            elif field in self._INT_FIELDS:
                payload[field] = int(val) if val and val.isdigit() else None
            else:
                payload[field] = val if val else None
        payload["wizard_current_step"] = step
        return payload

    def _build_full_payload(self) -> dict:
        """Build full profile payload."""
        payload = {}
        for step in range(6):
            payload.update(self._build_step_payload(step))
        payload["wizard_completed"] = True
        return payload

    # --- Event handlers ---

    async def load_profile(self):
        """Load profile from API on page mount."""
        try:
            data = await api_client.get_organization_profile()
            self._populate_from_data(data)
            self.profile_loaded = True
            # Show wizard if not completed yet
            self.show_wizard = not self.wizard_completed
            self.active_step = self.wizard_current_step if not self.wizard_completed else 0
        except Exception as e:
            self.error = str(e)
            self.profile_loaded = True
            self.show_wizard = True

    async def save_step(self):
        """Save current wizard step (PATCH)."""
        self.is_saving = True
        try:
            payload = self._build_step_payload(self.active_step)
            data = await api_client.patch_organization_profile(payload)
            self.completion_pct = data.get("completion_pct", 0)
            self.wizard_current_step = self.active_step
            self.error = ""
        except Exception as e:
            self.error = str(e)
        finally:
            self.is_saving = False

    async def save_all(self):
        """Save complete profile (PUT) — marks wizard as completed."""
        self.is_saving = True
        try:
            payload = self._build_full_payload()
            data = await api_client.upsert_organization_profile(payload)
            self._populate_from_data(data)
            self.wizard_completed = True
            self.show_wizard = False
            self.error = ""
        except Exception as e:
            self.error = str(e)
        finally:
            self.is_saving = False

    async def next_step(self):
        """Save current step and advance to next."""
        await self.save_step()
        if self.active_step < 5:
            self.active_step += 1

    async def prev_step(self):
        """Go to previous step."""
        if self.active_step > 0:
            self.active_step -= 1

    def go_to_step(self, step: int):
        """Jump to a specific step."""
        self.active_step = step

    def start_wizard(self):
        """Enter wizard mode (for re-editing)."""
        self.show_wizard = True
        self.active_step = 0

    def cancel_wizard(self):
        """Exit wizard mode without saving."""
        if self.wizard_completed:
            self.show_wizard = False

    # --- Setters for form fields ---
    def set_org_type(self, val: str):
        self.org_type = val
    def set_sector(self, val: str):
        self.sector = val
    def set_employee_count(self, val: str):
        self.employee_count = val
    def set_location_count(self, val: str):
        self.location_count = val
    def set_geographic_scope(self, val: str):
        self.geographic_scope = val
    def set_parent_organization(self, val: str):
        self.parent_organization = val
    def set_core_services(self, val: str):
        self.core_services = val
    def set_existing_certifications(self, val: str):
        self.existing_certifications = val
    def set_applicable_frameworks(self, val: str):
        self.applicable_frameworks = val
    def set_has_security_officer(self, val: str):
        self.has_security_officer = val
    def set_has_dpo(self, val: str):
        self.has_dpo = val
    def set_governance_maturity(self, val: str):
        self.governance_maturity = val
    def set_risk_appetite_availability(self, val: str):
        self.risk_appetite_availability = val
    def set_risk_appetite_integrity(self, val: str):
        self.risk_appetite_integrity = val
    def set_risk_appetite_confidentiality(self, val: str):
        self.risk_appetite_confidentiality = val
    def set_cloud_strategy(self, val: str):
        self.cloud_strategy = val
    def set_cloud_providers(self, val: str):
        self.cloud_providers = val
    def set_workstation_count(self, val: str):
        self.workstation_count = val
    def set_has_remote_work(self, val: str):
        self.has_remote_work = val
    def set_has_byod(self, val: str):
        self.has_byod = val
    def set_critical_systems(self, val: str):
        self.critical_systems = val
    def set_outsourced_it(self, val: str):
        self.outsourced_it = val
    def set_primary_it_supplier(self, val: str):
        self.primary_it_supplier = val
    def set_processes_personal_data(self, val: str):
        self.processes_personal_data = val
    def set_data_subject_types(self, val: str):
        self.data_subject_types = val
    def set_has_special_categories(self, val: str):
        self.has_special_categories = val
    def set_international_transfers(self, val: str):
        self.international_transfers = val
    def set_processing_count_estimate(self, val: str):
        self.processing_count_estimate = val
    def set_has_bcp(self, val: str):
        self.has_bcp = val
    def set_has_incident_response_plan(self, val: str):
        self.has_incident_response_plan = val
    def set_max_tolerable_downtime(self, val: str):
        self.max_tolerable_downtime = val
    def set_critical_process_count(self, val: str):
        self.critical_process_count = val
    def set_key_dependencies(self, val: str):
        self.key_dependencies = val
    def set_has_awareness_program(self, val: str):
        self.has_awareness_program = val
    def set_has_background_checks(self, val: str):
        self.has_background_checks = val
    def set_training_frequency(self, val: str):
        self.training_frequency = val
