"""
Risk Appetite State — Risicotolerantie
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client
from ims.state.auth import AuthState


# Appetite level options for dropdowns
APPETITE_LEVELS = [
    ("Risicomijdend", "AVERSE"),
    ("Minimaal", "MINIMAL"),
    ("Voorzichtig", "CAUTIOUS"),
    ("Gematigd", "MODERATE"),
    ("Open", "OPEN"),
    ("Risicozoekend", "HUNGRY"),
]

APPETITE_LABEL_MAP = {v: k for k, v in APPETITE_LEVELS}


class RiskAppetiteState(rx.State):
    """State for the risk appetite configuration page."""

    # --- Data ---
    appetite: Dict[str, Any] = {}
    heatmap: Dict[str, Any] = {}
    evaluation: Dict[str, Any] = {}
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # --- Form fields ---
    show_form_dialog: bool = False
    is_editing: bool = False

    form_overall: str = "CAUTIOUS"
    form_isms: str = ""
    form_pims: str = ""
    form_bcms: str = ""
    form_financial: str = ""
    form_reputational: str = ""
    form_compliance: str = ""
    form_auto_accept: str = "LOW"
    form_escalation: str = "HIGH"
    form_max_score: int = 6
    form_financial_threshold: int = 0
    form_statement: str = ""

    # --- Preview heatmap level ---
    preview_level: str = "CAUTIOUS"

    # --- Computed vars ---
    @rx.var
    def has_appetite(self) -> bool:
        return bool(self.appetite and self.appetite.get("id"))

    @rx.var
    def appetite_label(self) -> str:
        level = self.appetite.get("overall_appetite", "")
        return APPETITE_LABEL_MAP.get(level, level)

    @rx.var
    def heatmap_matrix(self) -> List[List[Dict[str, Any]]]:
        return self.heatmap.get("matrix", [])

    @rx.var
    def eval_total(self) -> int:
        return self.evaluation.get("total", 0)

    @rx.var
    def eval_acceptable(self) -> int:
        return self.evaluation.get("acceptable", 0)

    @rx.var
    def eval_conditional(self) -> int:
        return self.evaluation.get("conditional", 0)

    @rx.var
    def eval_escalation(self) -> int:
        return self.evaluation.get("escalation", 0)

    @rx.var
    def eval_unacceptable(self) -> int:
        return self.evaluation.get("unacceptable", 0)

    @rx.var
    def eval_not_assessed(self) -> int:
        return self.evaluation.get("not_assessed", 0)

    @rx.var
    def eval_decision_count(self) -> int:
        return self.evaluation.get("requires_decision_count", 0)

    # --- Load ---
    async def load_appetite(self):
        self.is_loading = True
        self.error = ""
        self.success_message = ""
        try:
            result = await api_client.get_current_risk_appetite()
            self.appetite = result or {}

            # Load heatmap
            try:
                self.heatmap = await api_client.get_appetite_heatmap()
            except Exception:
                self.heatmap = {}

            # Load tenant evaluation
            try:
                self.evaluation = await api_client.evaluate_tenant_risks()
            except Exception:
                self.evaluation = {}

        except Exception as e:
            self.error = f"Fout bij laden: {str(e)}"
            self.appetite = {}
        finally:
            self.is_loading = False

    async def load_heatmap_preview(self):
        """Load heatmap for the preview level."""
        try:
            self.heatmap = await api_client.get_appetite_heatmap(
                appetite_level=self.preview_level
            )
        except Exception:
            pass

    # --- Form handlers ---
    def set_form_overall(self, v: str):
        self.form_overall = v
        self.preview_level = v

    def set_form_isms(self, v: str): self.form_isms = v
    def set_form_pims(self, v: str): self.form_pims = v
    def set_form_bcms(self, v: str): self.form_bcms = v
    def set_form_financial(self, v: str): self.form_financial = v
    def set_form_reputational(self, v: str): self.form_reputational = v
    def set_form_compliance(self, v: str): self.form_compliance = v
    def set_form_auto_accept(self, v: str): self.form_auto_accept = v
    def set_form_escalation(self, v: str): self.form_escalation = v
    def set_form_statement(self, v: str): self.form_statement = v

    def set_form_max_score(self, v: str):
        try:
            self.form_max_score = int(v)
        except (ValueError, TypeError):
            pass

    def set_form_financial_threshold(self, v: str):
        try:
            self.form_financial_threshold = int(v.replace(".", "").replace(",", ""))
        except (ValueError, TypeError):
            pass

    def open_create_dialog(self):
        self.is_editing = False
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self):
        self.is_editing = True
        a = self.appetite
        self.form_overall = a.get("overall_appetite", "CAUTIOUS")
        self.form_isms = a.get("isms_appetite") or ""
        self.form_pims = a.get("pims_appetite") or ""
        self.form_bcms = a.get("bcms_appetite") or ""
        self.form_financial = a.get("financial_appetite") or ""
        self.form_reputational = a.get("reputational_appetite") or ""
        self.form_compliance = a.get("compliance_appetite") or ""
        self.form_auto_accept = a.get("auto_accept_threshold", "LOW")
        self.form_escalation = a.get("escalation_threshold", "HIGH")
        self.form_max_score = a.get("max_acceptable_risk_score", 6)
        self.form_financial_threshold = a.get("financial_threshold_value") or 0
        self.form_statement = a.get("appetite_statement") or ""
        self.preview_level = self.form_overall
        self.show_form_dialog = True

    def close_form_dialog(self):
        self.show_form_dialog = False
        self._reset_form()

    def _reset_form(self):
        self.form_overall = "CAUTIOUS"
        self.form_isms = ""
        self.form_pims = ""
        self.form_bcms = ""
        self.form_financial = ""
        self.form_reputational = ""
        self.form_compliance = ""
        self.form_auto_accept = "LOW"
        self.form_escalation = "HIGH"
        self.form_max_score = 6
        self.form_financial_threshold = 0
        self.form_statement = ""
        self.preview_level = "CAUTIOUS"
        self.error = ""

    async def save_appetite(self):
        self.error = ""
        auth = await self.get_state(AuthState)
        tid = auth.tenant_id

        data = {
            "tenant_id": tid,
            "overall_appetite": self.form_overall,
            "auto_accept_threshold": self.form_auto_accept,
            "escalation_threshold": self.form_escalation,
            "max_acceptable_risk_score": self.form_max_score,
            "is_current": True,
        }

        # Optional domain appetites
        if self.form_isms:
            data["isms_appetite"] = self.form_isms
        if self.form_pims:
            data["pims_appetite"] = self.form_pims
        if self.form_bcms:
            data["bcms_appetite"] = self.form_bcms
        if self.form_financial:
            data["financial_appetite"] = self.form_financial
        if self.form_reputational:
            data["reputational_appetite"] = self.form_reputational
        if self.form_compliance:
            data["compliance_appetite"] = self.form_compliance
        if self.form_financial_threshold:
            data["financial_threshold_value"] = self.form_financial_threshold
        if self.form_statement.strip():
            data["appetite_statement"] = self.form_statement.strip()

        try:
            if self.is_editing and self.appetite.get("id"):
                await api_client.update_risk_appetite(self.appetite["id"], data)
                self.success_message = "Risicotolerantie bijgewerkt"
            else:
                await api_client.create_risk_appetite(data)
                self.success_message = "Risicotolerantie aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            return RiskAppetiteState.load_appetite
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"
