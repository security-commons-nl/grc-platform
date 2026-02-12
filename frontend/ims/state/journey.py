"""
Journey State - 7-step PDCA onboarding progress tracker
Loads data from existing endpoints and computes step completion/blockers.
"""
import asyncio
import reflex as rx
from typing import List, Dict, Any

from ims.api.client import API_BASE_URL, api_client
from ims.state.auth import AuthState


# Step definitions (1-indexed for display)
STEP_TITLES = [
    "Scopes definiëren",
    "BIA uitvoeren",
    "Risico's identificeren",
    "Behandeling bepalen",
    "Controls implementeren",
    "Besluiten vastleggen",
    "Review uitvoeren",
]

STEP_ICONS = [
    "git-branch",
    "shield-check",
    "triangle-alert",
    "target",
    "shield-check",
    "gavel",
    "clipboard-check",
]

STEP_LINKS = [
    "/scopes",
    "/scopes",
    "/risks",
    "/risks",
    "/controls",
    "/decisions",
    "/assessments",
]

STEP_LINK_LABELS = [
    "Ga naar Scopes",
    "Voeg BIA toe",
    "Registreer risico's",
    "Bepaal kwadrant",
    "Koppel controls",
    "Documenteer besluiten",
    "Start assessment",
]


class JourneyState(rx.State):
    """Tracks the 7-step IMS onboarding journey."""

    # Raw data from API
    _scopes: List[Dict[str, Any]] = []
    _risks: List[Dict[str, Any]] = []
    _controls: List[Dict[str, Any]] = []
    _decisions: List[Dict[str, Any]] = []
    _assessments: List[Dict[str, Any]] = []
    _risk_control_links: int = 0

    is_loading: bool = False
    error: str = ""

    # --- Step completion computed vars ---

    @rx.var
    def step1_ok(self) -> bool:
        """Scopes definiëren: at least 1 scope."""
        return len(self._scopes) > 0

    @rx.var
    def step1_blocker(self) -> str:
        if len(self._scopes) > 0:
            return ""
        return "Geen scopes gedefinieerd"

    @rx.var
    def step2_ok(self) -> bool:
        """BIA uitvoeren: at least 1 scope with BIA rating."""
        for s in self._scopes:
            if s.get("availability_rating") or s.get("integrity_rating") or s.get("confidentiality_rating"):
                return True
        return False

    @rx.var
    def step2_blocker(self) -> str:
        if self.step2_ok:
            return ""
        missing = len(self._scopes)
        if missing == 0:
            return "Geen scopes om BIA op uit te voeren"
        return f"{missing} scopes missen BIA-classificatie"

    @rx.var
    def step3_ok(self) -> bool:
        """Risico's identificeren: at least 3 risks."""
        return len(self._risks) >= 3

    @rx.var
    def step3_blocker(self) -> str:
        count = len(self._risks)
        if count >= 3:
            return ""
        return f"Slechts {count} risico's geregistreerd (minimaal 3)"

    @rx.var
    def step4_ok(self) -> bool:
        """Behandeling bepalen: all risks have attention_quadrant."""
        if len(self._risks) == 0:
            return False
        for r in self._risks:
            quadrant = r.get("attention_quadrant", "")
            if not quadrant or quadrant in ("", "NONE", "Geen"):
                return False
        return True

    @rx.var
    def step4_blocker(self) -> str:
        if self.step4_ok:
            return ""
        missing = 0
        for r in self._risks:
            quadrant = r.get("attention_quadrant", "")
            if not quadrant or quadrant in ("", "NONE", "Geen"):
                missing += 1
        if missing == 0:
            return "Registreer eerst risico's"
        return f"{missing} risico's zonder aandachtskwadrant"

    @rx.var
    def step5_ok(self) -> bool:
        """Controls implementeren: at least 1 control linked to a risk."""
        return self._risk_control_links > 0

    @rx.var
    def step5_blocker(self) -> str:
        if self._risk_control_links > 0:
            return ""
        return "Controls niet gekoppeld aan risico's"

    @rx.var
    def step6_ok(self) -> bool:
        """Besluiten vastleggen: at least 1 decision."""
        return len(self._decisions) > 0

    @rx.var
    def step6_blocker(self) -> str:
        if len(self._decisions) > 0:
            return ""
        return "Geen formele besluiten vastgelegd"

    @rx.var
    def step7_ok(self) -> bool:
        """Review uitvoeren: at least 1 completed assessment."""
        for a in self._assessments:
            if a.get("status") in ("Completed", "completed", "COMPLETED"):
                return True
        return False

    @rx.var
    def step7_blocker(self) -> str:
        if self.step7_ok:
            return ""
        return "Nog geen assessments afgerond"

    # --- Aggregate computed vars ---

    @rx.var
    def steps_done(self) -> int:
        return sum([
            self.step1_ok, self.step2_ok, self.step3_ok, self.step4_ok,
            self.step5_ok, self.step6_ok, self.step7_ok,
        ])

    @rx.var
    def overall_progress_pct(self) -> int:
        return int(self.steps_done * 100 / 7)

    @rx.var
    def current_step(self) -> int:
        """First incomplete step (1-indexed). Returns 8 if all done."""
        steps = [
            self.step1_ok, self.step2_ok, self.step3_ok, self.step4_ok,
            self.step5_ok, self.step6_ok, self.step7_ok,
        ]
        for i, ok in enumerate(steps):
            if not ok:
                return i + 1
        return 8

    @rx.var
    def current_step_label(self) -> str:
        idx = self.current_step
        if idx > 7:
            return "Alle stappen afgerond!"
        return STEP_TITLES[idx - 1]

    # --- Hint texts for domain pages ---

    @rx.var
    def risks_hint(self) -> str:
        """Hint for risks page."""
        if not self.step3_ok:
            count = len(self._risks)
            return f"Registreer minimaal 3 risico's (nu: {count})"
        if not self.step4_ok:
            missing = 0
            for r in self._risks:
                quadrant = r.get("attention_quadrant", "")
                if not quadrant or quadrant in ("", "NONE", "Geen"):
                    missing += 1
            return f"{missing} risico's zonder aandachtskwadrant — kies Mitigeren/Zekerheid/Monitoren/Accepteren"
        return ""

    @rx.var
    def controls_hint(self) -> str:
        """Hint for controls page."""
        if not self.step5_ok:
            return "Koppel minstens 1 control aan een risico via het bewerkscherm"
        return ""

    @rx.var
    def scopes_hint(self) -> str:
        """Hint for scopes page."""
        if not self.step1_ok:
            return "Definieer minstens 1 scope (organisatie, afdeling of proces)"
        if not self.step2_ok:
            missing = 0
            for s in self._scopes:
                if not (s.get("availability_rating") or s.get("integrity_rating") or s.get("confidentiality_rating")):
                    missing += 1
            return f"{missing} scopes missen BIA-classificatie — voeg beschikbaarheid/integriteit/vertrouwelijkheid toe"
        return ""

    @rx.var
    def policies_hint(self) -> str:
        """Hint for policies page — generic guidance."""
        return ""

    # --- Data loading ---

    async def load_journey_data(self):
        """Load data from 5 endpoints in parallel using api_client."""
        self.is_loading = True
        self.error = ""

        try:
            # Helper to wrap api_client calls and return empty list on error
            async def safe_fetch(coro):
                try:
                    return await coro
                except Exception:
                    return []

            # Use api_client which handles auth internally (defaults to X-User-ID: 1)
            # This matches RiskState's working implementation.
            results = await asyncio.gather(
                safe_fetch(api_client.get_scopes(limit=500)),
                safe_fetch(api_client.get_risks(limit=500)),
                safe_fetch(api_client.get_controls(limit=500)),
                safe_fetch(api_client.get_decisions(limit=500)),
                safe_fetch(api_client.get_assessments(limit=500)),
            )

            self._scopes = results[0]
            self._risks = results[1]
            controls = results[2]
            self._controls = controls
            self._decisions = results[3]
            self._assessments = results[4]

            # Count risk-control links: controls that have linked risks
            links = 0
            for c in controls:
                # Check for various link indicators based on API response structure
                if c.get("risk_ids") or c.get("linked_risks"):
                    links += 1
                elif c.get("scope_id"):
                    links += 1  # Scope-bound controls count as linked
            self._risk_control_links = links

        except Exception as e:
            self.error = "Kon voortgangsdata niet laden"
            # print(f"Journey load error: {e}")

        self.is_loading = False
