"""
Journey State - 7-step PDCA onboarding progress tracker
Loads data from existing endpoints and computes step completion/blockers.
"""
import asyncio
import httpx
import reflex as rx
from typing import List, Dict, Any

from ims.api.client import API_BASE_URL


_JOURNEY_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)
_JOURNEY_HEADERS = {"X-User-ID": "1", "X-Tenant-ID": "1"}

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
    "Kies strategie",
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
        """Behandeling bepalen: all risks have treatment_strategy."""
        if len(self._risks) == 0:
            return False
        for r in self._risks:
            strategy = r.get("treatment_strategy", "")
            if not strategy or strategy in ("", "NONE", "Geen"):
                return False
        return True

    @rx.var
    def step4_blocker(self) -> str:
        if self.step4_ok:
            return ""
        missing = 0
        for r in self._risks:
            strategy = r.get("treatment_strategy", "")
            if not strategy or strategy in ("", "NONE", "Geen"):
                missing += 1
        if missing == 0:
            return "Registreer eerst risico's"
        return f"{missing} risico's zonder behandelstrategie"

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
                strategy = r.get("treatment_strategy", "")
                if not strategy or strategy in ("", "NONE", "Geen"):
                    missing += 1
            return f"{missing} risico's zonder behandelstrategie — kies Vermijden/Reduceren/Overdragen/Accepteren"
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
        """Load data from 6 endpoints in parallel."""
        self.is_loading = True
        self.error = ""

        try:
            async with httpx.AsyncClient(
                base_url=API_BASE_URL, timeout=_JOURNEY_TIMEOUT,
                headers=_JOURNEY_HEADERS,
            ) as client:
                responses = await asyncio.gather(
                    client.get("/scopes/", params={"limit": 500}),
                    client.get("/risks/", params={"limit": 500}),
                    client.get("/controls/", params={"limit": 500}),
                    client.get("/decisions/", params={"limit": 500}),
                    client.get("/assessments/", params={"limit": 500}),
                    return_exceptions=True,
                )

            def safe_json(r):
                if isinstance(r, Exception):
                    return []
                if r.status_code == 200:
                    data = r.json()
                    return data if isinstance(data, list) else []
                return []

            self._scopes = safe_json(responses[0])
            self._risks = safe_json(responses[1])
            controls = safe_json(responses[2])
            self._controls = controls
            self._decisions = safe_json(responses[3])
            self._assessments = safe_json(responses[4])

            # Count risk-control links: controls that have linked risks
            links = 0
            for c in controls:
                if c.get("risk_ids") or c.get("linked_risks"):
                    links += 1
                elif c.get("scope_id"):
                    links += 1  # Scope-bound controls count as linked
            self._risk_control_links = links

        except Exception:
            self.error = "Kon voortgangsdata niet laden"

        self.is_loading = False
