"""
Simulation State - Handles Monte Carlo simulation logic and configuration
"""
import reflex as rx
import json
from typing import Dict, Any, List, Optional
from ims.api.client import api_client

class SimulationState(rx.State):
    """State for Monte Carlo Simulation."""

    # Configuration
    profile_id: Optional[int] = None
    currency: str = "EUR"
    iterations: int = 10000

    # Global Config Form Fields
    # Frequency (per year)
    low_freq_min: float = 0.05
    low_freq_max: float = 0.2
    med_freq_min: float = 0.2
    med_freq_max: float = 1.0
    high_freq_min: float = 1.0
    high_freq_max: float = 5.0
    crit_freq_min: float = 5.0
    crit_freq_max: float = 10.0

    # Impact (Euros)
    low_imp_min: float = 1000.0
    low_imp_max: float = 10000.0
    med_imp_min: float = 10000.0
    med_imp_max: float = 50000.0
    high_imp_min: float = 50000.0
    high_imp_max: float = 250000.0
    crit_imp_min: float = 250000.0
    crit_imp_max: float = 1000000.0

    # Raw JSON configs (for categories/backup)
    global_config_json: str = ""
    category_configs_json: str = "{}"

    # Simulation Results
    results: Dict[str, Any] = {}
    is_running: bool = False
    error: str = ""
    success_message: str = ""

    # Chart Data
    # List of dicts: [{"range": "0-10k", "count": 50}, ...]
    histogram_data: List[Dict[str, Any]] = []

    @rx.var
    def has_results(self) -> bool:
        return len(self.results) > 0

    @rx.var
    def mean_loss_formatted(self) -> str:
        val = self.results.get("mean_loss", 0)
        return f"€ {val:,.2f}"

    @rx.var
    def var95_formatted(self) -> str:
        val = self.results.get("var_95", 0)
        return f"€ {val:,.2f}"

    @rx.var
    def var99_formatted(self) -> str:
        val = self.results.get("var_99", 0)
        return f"€ {val:,.2f}"

    @rx.var
    def histogram_data_normalized(self) -> List[Dict[str, Any]]:
        """Return histogram data with normalized height percentage for charting."""
        if not self.histogram_data:
            return []
        # Calculate max count for scaling
        # Use simple iteration
        counts = [d.get("count", 0) for d in self.histogram_data]
        max_count = max(counts) if counts else 1

        # Avoid division by zero
        if max_count == 0:
            max_count = 1

        result = []
        for d in self.histogram_data:
            new_d = d.copy()
            # Scale to percentage (max height 100%)
            pct = (d.get("count", 0) / max_count) * 100
            new_d["height_pct"] = f"{pct}%"
            result.append(new_d)
        return result

    async def load_config(self):
        """Load configuration from backend."""
        self.error = ""
        try:
            # Hardcoded tenant_id=1 for now
            data = await api_client.get_quantification_config(tenant_id=1)
            self.profile_id = data.get("id")
            self.currency = data.get("currency", "EUR")
            self.iterations = data.get("iterations", 10000)

            # Parse Global Config
            global_conf_str = data.get("global_config", "{}")
            self.global_config_json = global_conf_str
            self.category_configs_json = data.get("category_configs") or "{}"

            try:
                g_conf = json.loads(global_conf_str)
                # Map to fields
                self.low_freq_min = g_conf.get("LOW", {}).get("freq_min", 0.0)
                self.low_freq_max = g_conf.get("LOW", {}).get("freq_max", 0.0)
                self.low_imp_min = g_conf.get("LOW", {}).get("impact_min", 0.0)
                self.low_imp_max = g_conf.get("LOW", {}).get("impact_max", 0.0)

                self.med_freq_min = g_conf.get("MEDIUM", {}).get("freq_min", 0.0)
                self.med_freq_max = g_conf.get("MEDIUM", {}).get("freq_max", 0.0)
                self.med_imp_min = g_conf.get("MEDIUM", {}).get("impact_min", 0.0)
                self.med_imp_max = g_conf.get("MEDIUM", {}).get("impact_max", 0.0)

                self.high_freq_min = g_conf.get("HIGH", {}).get("freq_min", 0.0)
                self.high_freq_max = g_conf.get("HIGH", {}).get("freq_max", 0.0)
                self.high_imp_min = g_conf.get("HIGH", {}).get("impact_min", 0.0)
                self.high_imp_max = g_conf.get("HIGH", {}).get("impact_max", 0.0)

                self.crit_freq_min = g_conf.get("CRITICAL", {}).get("freq_min", 0.0)
                self.crit_freq_max = g_conf.get("CRITICAL", {}).get("freq_max", 0.0)
                self.crit_imp_min = g_conf.get("CRITICAL", {}).get("impact_min", 0.0)
                self.crit_imp_max = g_conf.get("CRITICAL", {}).get("impact_max", 0.0)

            except json.JSONDecodeError:
                self.error = "Fout bij parsen configuratie"

        except Exception as e:
            self.error = f"Kon configuratie niet laden: {str(e)}"

    async def save_config(self):
        """Save configuration to backend."""
        self.error = ""
        self.success_message = ""

        # Construct JSON from fields
        new_conf = {
            "LOW": {"freq_min": self.low_freq_min, "freq_max": self.low_freq_max, "impact_min": self.low_imp_min, "impact_max": self.low_imp_max},
            "MEDIUM": {"freq_min": self.med_freq_min, "freq_max": self.med_freq_max, "impact_min": self.med_imp_min, "impact_max": self.med_imp_max},
            "HIGH": {"freq_min": self.high_freq_min, "freq_max": self.high_freq_max, "impact_min": self.high_imp_min, "impact_max": self.high_imp_max},
            "CRITICAL": {"freq_min": self.crit_freq_min, "freq_max": self.crit_freq_max, "impact_min": self.crit_imp_min, "impact_max": self.crit_imp_max},
        }

        payload = {
            "tenant_id": 1,
            "global_config": json.dumps(new_conf),
            "category_configs": self.category_configs_json, # Keep existing category configs for now
            "currency": self.currency,
            "iterations": self.iterations
        }

        try:
            await api_client.save_quantification_config(payload)
            self.success_message = "Configuratie opgeslagen"
            # Update raw json
            self.global_config_json = json.dumps(new_conf, indent=2)
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    async def run_simulation(self):
        """Execute simulation."""
        self.is_running = True
        self.error = ""
        self.results = {}
        self.histogram_data = []

        # Ensure config is saved first? Or just use what's on backend.
        # Ideally we save first if dirty, but let's assume user saved.

        try:
            payload = {
                "tenant_id": 1,
                "iterations": self.iterations
            }
            data = await api_client.run_simulation(payload)
            self.results = data
            self.histogram_data = data.get("histogram", [])
        except Exception as e:
            self.error = f"Simulatie mislukt: {str(e)}"
        finally:
            self.is_running = False

    # Setters for form fields (Reflex needs these for input binding sometimes, or direct var access works too)
    def set_iterations(self, val: str):
        if val and val.isdigit():
            self.iterations = int(val)

    def set_currency(self, val: str):
        self.currency = val

    def set_category_configs_json(self, val: str):
        self.category_configs_json = val

    # Frequency Setters
    # Frequency Setters
    def set_low_freq_min(self, val: str):
        if val: self.low_freq_min = float(val)
    def set_low_freq_max(self, val: str):
        if val: self.low_freq_max = float(val)
    def set_med_freq_min(self, val: str):
        if val: self.med_freq_min = float(val)
    def set_med_freq_max(self, val: str):
        if val: self.med_freq_max = float(val)
    def set_high_freq_min(self, val: str):
        if val: self.high_freq_min = float(val)
    def set_high_freq_max(self, val: str):
        if val: self.high_freq_max = float(val)
    def set_crit_freq_min(self, val: str):
        if val: self.crit_freq_min = float(val)
    def set_crit_freq_max(self, val: str):
        if val: self.crit_freq_max = float(val)

    # Impact Setters
    # Impact Setters
    def set_low_imp_min(self, val: str):
        if val: self.low_imp_min = float(val)
    def set_low_imp_max(self, val: str):
        if val: self.low_imp_max = float(val)
    def set_med_imp_min(self, val: str):
        if val: self.med_imp_min = float(val)
    def set_med_imp_max(self, val: str):
        if val: self.med_imp_max = float(val)
    def set_high_imp_min(self, val: str):
        if val: self.high_imp_min = float(val)
    def set_high_imp_max(self, val: str):
        if val: self.high_imp_max = float(val)
    def set_crit_imp_min(self, val: str):
        if val: self.crit_imp_min = float(val)
    def set_crit_imp_max(self, val: str):
        if val: self.crit_imp_max = float(val)
