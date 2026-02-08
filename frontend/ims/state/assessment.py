"""
Assessment State - handles assessment/verification data including BIA workflow
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


# Phase definitions for the stepper
ASSESSMENT_PHASES = [
    "Aangevraagd",
    "Planning",
    "Voorbereiding",
    "In uitvoering",
    "Review",
    "Rapportage",
    "Afgerond",
]

ASSESSMENT_TYPES = [
    ("DPIA", "DPIA"),
    ("Pentest", "Pentest"),
    ("Audit", "Audit"),
    ("Self-Assessment", "Self-Assessment"),
    ("Compliance Journey", "Compliance Journey"),
    ("BIA", "BIA"),
    ("Supplier Assessment", "Supplier Assessment"),
    ("Maturity Assessment", "Maturity Assessment"),
]


class AssessmentState(rx.State):
    """Assessment management state."""

    # Assessment list
    assessments: List[Dict[str, Any]] = []
    selected_assessment: Dict[str, Any] = {}

    # Filters
    filter_type: str = "ALLE"
    filter_status: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Wizard dialog
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_assessment_id: int = 0

    # Form fields
    form_title: str = ""
    form_description: str = ""
    form_type: str = "Self-Assessment"
    form_scope_id: str = ""
    form_lead_assessor_id: str = ""
    form_external_assessor: str = ""
    form_methodology: str = ""
    form_deadline: str = ""

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_assessment_id: int = 0
    deleting_assessment_title: str = ""

    # Detail page
    detail_assessment: Dict[str, Any] = {}
    detail_findings: List[Dict[str, Any]] = []
    detail_evidence: List[Dict[str, Any]] = []
    detail_corrective_actions: List[Dict[str, Any]] = []
    detail_tab: str = "overzicht"
    detail_loading: bool = False

    # Findings form
    show_finding_dialog: bool = False
    finding_title: str = ""
    finding_description: str = ""
    finding_severity: str = "Medium"

    # Corrective action form
    show_action_dialog: bool = False
    action_finding_id: int = 0
    action_description: str = ""
    action_due_date: str = ""
    action_assigned_to: str = ""

    # Evidence form
    show_evidence_dialog: bool = False
    evidence_title: str = ""
    evidence_description: str = ""
    evidence_type: str = ""
    evidence_url: str = ""

    # BIA questionnaire
    bia_questions: List[Dict[str, Any]] = []
    bia_responses: Dict[str, int] = {}
    bia_progress_total: int = 0
    bia_progress_answered: int = 0
    bia_progress_pct: int = 0
    bia_result: Dict[str, Any] = {}
    bia_calculating: bool = False

    # Scopes list for dropdown
    available_scopes: List[Dict[str, Any]] = []
    # Users list for dropdown
    available_users: List[Dict[str, Any]] = []

    # ==========================================================================
    # COMPUTED VARS
    # ==========================================================================

    @rx.var
    def active_count(self) -> int:
        return len([a for a in self.assessments if a.get("status") == "Active"])

    @rx.var
    def completed_count(self) -> int:
        return len([a for a in self.assessments if a.get("status") == "Closed"])

    @rx.var
    def draft_count(self) -> int:
        return len([a for a in self.assessments if a.get("status") == "Draft"])

    @rx.var
    def total_count(self) -> int:
        return len(self.assessments)

    @rx.var
    def detail_phase(self) -> str:
        return self.detail_assessment.get("phase", "Aangevraagd")

    @rx.var
    def detail_phase_index(self) -> int:
        phase = self.detail_assessment.get("phase", "Aangevraagd")
        if phase in ASSESSMENT_PHASES:
            return ASSESSMENT_PHASES.index(phase)
        return 0

    @rx.var
    def detail_is_bia(self) -> bool:
        return self.detail_assessment.get("type") == "BIA"

    @rx.var
    def detail_has_bia_result(self) -> bool:
        return bool(self.detail_assessment.get("bia_cia_label"))

    @rx.var
    def detail_findings_count(self) -> int:
        return len(self.detail_findings)

    @rx.var
    def detail_evidence_count(self) -> int:
        return len(self.detail_evidence)

    @rx.var
    def bia_has_all_answers(self) -> bool:
        return self.bia_progress_total > 0 and self.bia_progress_answered >= self.bia_progress_total

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_assessments(self):
        """Load assessments from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            params = {}
            if self.filter_type and self.filter_type != "ALLE":
                params["assessment_type"] = self.filter_type
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status

            self.assessments = await api_client.get_assessments(**params)
        except Exception as e:
            self.error = f"Kan assessments niet laden: {str(e)}"
            self.assessments = []
        finally:
            self.is_loading = False

    async def load_dropdowns(self):
        """Load scopes and users for form dropdowns."""
        try:
            self.available_scopes = await api_client.get_scopes(limit=200)
        except Exception:
            self.available_scopes = []
        try:
            self.available_users = await api_client.get_users(limit=200)
        except Exception:
            self.available_users = []

    async def load_detail(self):
        """Load full assessment detail by ID from route params."""
        self.detail_loading = True
        self.error = ""
        self.detail_tab = "overzicht"

        try:
            aid = int(self.router.page.params.get("id", "0"))
            if not aid:
                self.error = "Geen assessment ID opgegeven"
                return

            self.detail_assessment = await api_client.get_assessment(aid)
            self.detail_findings = await api_client.get_assessment_findings(aid)
            self.detail_evidence = await api_client.get_assessment_evidence(aid)
        except Exception as e:
            self.error = f"Kan assessment niet laden: {str(e)}"
        finally:
            self.detail_loading = False

    async def load_bia_questions(self):
        """Load BIA questions and existing responses for the current assessment."""
        aid = self.detail_assessment.get("id")
        if not aid:
            return

        try:
            self.bia_questions = await api_client.get_assessment_questions(aid)
            responses = await api_client.get_assessment_responses(aid)

            # Build response map: question_id -> score
            resp_map = {}
            for r in responses:
                qid = str(r.get("question_id", ""))
                score = r.get("score")
                if qid and score is not None:
                    resp_map[qid] = int(score)
            self.bia_responses = resp_map

            # Load progress
            progress = await api_client.get_assessment_progress(aid)
            self.bia_progress_total = progress.get("total", 0)
            self.bia_progress_answered = progress.get("answered", 0)
            self.bia_progress_pct = progress.get("pct", 0)
        except Exception as e:
            self.error = f"Kan BIA vragen niet laden: {str(e)}"

    # ==========================================================================
    # FILTER METHODS
    # ==========================================================================

    def set_filter_type(self, type_value: str):
        """Set type filter."""
        self.filter_type = type_value
        return AssessmentState.load_assessments

    def set_filter_status(self, status: str):
        """Set status filter."""
        self.filter_status = status
        return AssessmentState.load_assessments

    def clear_filters(self):
        """Clear all filters."""
        self.filter_type = "ALLE"
        self.filter_status = "ALLE"
        return AssessmentState.load_assessments

    # ==========================================================================
    # WIZARD: CREATE / EDIT
    # ==========================================================================

    async def open_create_dialog(self):
        """Open wizard for new assessment."""
        self.is_editing = False
        self.editing_assessment_id = 0
        self.form_title = ""
        self.form_description = ""
        self.form_type = "Self-Assessment"
        self.form_scope_id = ""
        self.form_lead_assessor_id = ""
        self.form_external_assessor = ""
        self.form_methodology = ""
        self.form_deadline = ""
        self.show_form_dialog = True
        self.error = ""
        self.success_message = ""
        await self.load_dropdowns()

    async def open_edit_dialog(self, assessment: Dict[str, Any]):
        """Open wizard to edit existing assessment."""
        self.is_editing = True
        self.editing_assessment_id = assessment.get("id", 0)
        self.form_title = assessment.get("title", "")
        self.form_description = assessment.get("description", "") or ""
        self.form_type = assessment.get("type", "Self-Assessment")
        self.form_scope_id = str(assessment.get("scope_id", "")) if assessment.get("scope_id") else ""
        self.form_lead_assessor_id = str(assessment.get("lead_assessor_id", "")) if assessment.get("lead_assessor_id") else ""
        self.form_external_assessor = assessment.get("external_assessor", "") or ""
        self.form_methodology = assessment.get("methodology", "") or ""
        self.form_deadline = ""
        self.show_form_dialog = True
        self.error = ""
        self.success_message = ""
        await self.load_dropdowns()

    def close_form_dialog(self):
        self.show_form_dialog = False

    def set_form_title(self, value: str):
        self.form_title = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_type(self, value: str):
        self.form_type = value

    def set_form_scope_id(self, value: str):
        self.form_scope_id = value

    def set_form_lead_assessor_id(self, value: str):
        self.form_lead_assessor_id = value

    def set_form_external_assessor(self, value: str):
        self.form_external_assessor = value

    def set_form_methodology(self, value: str):
        self.form_methodology = value

    def set_form_deadline(self, value: str):
        self.form_deadline = value

    async def save_assessment(self):
        """Create or update assessment."""
        if not self.form_title.strip():
            self.error = "Titel is verplicht"
            return

        data = {
            "tenant_id": 1,
            "title": self.form_title.strip(),
            "description": self.form_description.strip() or None,
            "type": self.form_type,
            "methodology": self.form_methodology.strip() or None,
            "external_assessor": self.form_external_assessor.strip() or None,
        }

        if self.form_scope_id:
            data["scope_id"] = int(self.form_scope_id)
        if self.form_lead_assessor_id:
            data["lead_assessor_id"] = int(self.form_lead_assessor_id)

        try:
            if self.is_editing and self.editing_assessment_id:
                await api_client.update_assessment(self.editing_assessment_id, data)
                self.success_message = "Assessment bijgewerkt"
            else:
                await api_client.create_assessment(data)
                self.success_message = "Assessment aangemaakt"

            self.show_form_dialog = False
            self.error = ""
            await self.load_assessments()
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE
    # ==========================================================================

    def confirm_delete(self, assessment: Dict[str, Any]):
        self.deleting_assessment_id = assessment.get("id", 0)
        self.deleting_assessment_title = assessment.get("title", "")
        self.show_delete_dialog = True

    def cancel_delete(self):
        self.show_delete_dialog = False

    async def delete_assessment(self):
        """Delete the assessment."""
        if not self.deleting_assessment_id:
            return

        try:
            await api_client.delete_assessment(self.deleting_assessment_id)
            self.success_message = "Assessment verwijderd"
            self.show_delete_dialog = False
            await self.load_assessments()
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"

    # ==========================================================================
    # NAVIGATION
    # ==========================================================================

    def go_to_detail(self, assessment: Dict[str, Any]):
        aid = assessment.get("id")
        if aid:
            return rx.redirect(f"/assessments/{aid}")

    # ==========================================================================
    # PHASE MANAGEMENT
    # ==========================================================================

    async def advance_phase(self, phase: str):
        """Advance the assessment to a new phase."""
        aid = self.detail_assessment.get("id")
        if not aid:
            return

        try:
            result = await api_client.advance_assessment_phase(aid, phase)
            self.detail_assessment = result
            self.success_message = f"Fase bijgewerkt naar: {phase}"
            self.error = ""
        except Exception as e:
            self.error = f"Fout bij fase-overgang: {str(e)}"

    # ==========================================================================
    # FINDINGS
    # ==========================================================================

    def open_finding_dialog(self):
        self.finding_title = ""
        self.finding_description = ""
        self.finding_severity = "Medium"
        self.show_finding_dialog = True

    def close_finding_dialog(self):
        self.show_finding_dialog = False

    def set_finding_title(self, value: str):
        self.finding_title = value

    def set_finding_description(self, value: str):
        self.finding_description = value

    def set_finding_severity(self, value: str):
        self.finding_severity = value

    async def create_finding(self):
        """Create a finding for the current assessment."""
        aid = self.detail_assessment.get("id")
        if not aid or not self.finding_title.strip():
            self.error = "Titel is verplicht"
            return

        try:
            await api_client.create_finding(aid, {
                "tenant_id": 1,
                "title": self.finding_title.strip(),
                "description": self.finding_description.strip() or "-",
                "severity": self.finding_severity,
                "status": "Active",
            })
            self.show_finding_dialog = False
            self.success_message = "Bevinding toegevoegd"
            self.detail_findings = await api_client.get_assessment_findings(aid)
        except Exception as e:
            self.error = f"Fout bij aanmaken bevinding: {str(e)}"

    async def close_finding_action(self, finding_id: int):
        """Close a finding (requires completed corrective action)."""
        try:
            await api_client.close_finding(finding_id)
            aid = self.detail_assessment.get("id")
            if aid:
                self.detail_findings = await api_client.get_assessment_findings(aid)
            self.success_message = "Bevinding afgesloten"
        except Exception as e:
            self.error = f"Kan bevinding niet sluiten: {str(e)}"

    # ==========================================================================
    # CORRECTIVE ACTIONS
    # ==========================================================================

    def open_action_dialog(self, finding_id: int):
        self.action_finding_id = finding_id
        self.action_description = ""
        self.action_due_date = ""
        self.action_assigned_to = ""
        self.show_action_dialog = True

    def close_action_dialog(self):
        self.show_action_dialog = False

    def set_action_description(self, value: str):
        self.action_description = value

    def set_action_due_date(self, value: str):
        self.action_due_date = value

    def set_action_assigned_to(self, value: str):
        self.action_assigned_to = value

    async def create_corrective_action(self):
        """Create a corrective action."""
        if not self.action_finding_id or not self.action_description.strip():
            self.error = "Beschrijving is verplicht"
            return

        try:
            await api_client.create_corrective_action(self.action_finding_id, {
                "tenant_id": 1,
                "title": self.action_description.strip(),
                "description": self.action_description.strip(),
                "status": "Active",
            })
            self.show_action_dialog = False
            self.success_message = "Corrigerende maatregel toegevoegd"
        except Exception as e:
            self.error = f"Fout bij aanmaken actie: {str(e)}"

    # ==========================================================================
    # EVIDENCE
    # ==========================================================================

    def open_evidence_dialog(self):
        self.evidence_title = ""
        self.evidence_description = ""
        self.evidence_type = ""
        self.evidence_url = ""
        self.show_evidence_dialog = True

    def close_evidence_dialog(self):
        self.show_evidence_dialog = False

    def set_evidence_title(self, value: str):
        self.evidence_title = value

    def set_evidence_description(self, value: str):
        self.evidence_description = value

    def set_evidence_type(self, value: str):
        self.evidence_type = value

    def set_evidence_url(self, value: str):
        self.evidence_url = value

    async def create_evidence(self):
        """Create evidence for the current assessment."""
        aid = self.detail_assessment.get("id")
        if not aid or not self.evidence_title.strip():
            self.error = "Titel is verplicht"
            return

        try:
            await api_client.create_evidence({
                "tenant_id": 1,
                "assessment_id": aid,
                "title": self.evidence_title.strip(),
                "description": self.evidence_description.strip() or None,
                "evidence_type": self.evidence_type or None,
                "url": self.evidence_url.strip() or None,
            })
            self.show_evidence_dialog = False
            self.success_message = "Bewijs toegevoegd"
            self.detail_evidence = await api_client.get_assessment_evidence(aid)
        except Exception as e:
            self.error = f"Fout bij aanmaken bewijs: {str(e)}"

    # ==========================================================================
    # BIA QUESTIONNAIRE
    # ==========================================================================

    async def set_bia_response(self, question_id: str, score: str):
        """Save a single BIA response."""
        aid = self.detail_assessment.get("id")
        if not aid:
            return

        score_int = int(score)
        try:
            await api_client.save_assessment_response(aid, {
                "tenant_id": 1,
                "question_id": int(question_id),
                "response_value": str(score_int),
                "score": float(score_int),
            })
            # Update local state
            self.bia_responses[question_id] = score_int

            # Refresh progress
            progress = await api_client.get_assessment_progress(aid)
            self.bia_progress_total = progress.get("total", 0)
            self.bia_progress_answered = progress.get("answered", 0)
            self.bia_progress_pct = progress.get("pct", 0)
        except Exception as e:
            self.error = f"Fout bij opslaan antwoord: {str(e)}"

    async def calculate_bia(self):
        """Calculate BIA scores from responses."""
        aid = self.detail_assessment.get("id")
        if not aid:
            return

        self.bia_calculating = True
        self.error = ""

        try:
            result = await api_client.calculate_bia(aid)
            self.bia_result = result
            self.success_message = "BIA score berekend"

            # Refresh assessment detail to get updated snapshot
            self.detail_assessment = await api_client.get_assessment(aid)
        except Exception as e:
            self.error = f"Fout bij BIA berekening: {str(e)}"
        finally:
            self.bia_calculating = False

    # ==========================================================================
    # TAB NAVIGATION
    # ==========================================================================

    def set_detail_tab(self, tab: str):
        self.detail_tab = tab
