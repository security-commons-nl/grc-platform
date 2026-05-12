from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal


# ── IMSRisk ─────────────────────────────────────────────────────────────────


ImpactDistribution = Optional[str]  # "single" | "uniform" | "triangular" | None


class RiskCreate(BaseModel):
    scope_id: UUID
    domain: str
    title: str
    description: str
    likelihood: int
    impact: int
    status: str = "open"
    owner_user_id: Optional[UUID] = None
    cyclus_id: Optional[int] = None
    financial_impact_eur: Optional[Decimal] = None
    financial_impact_min_eur: Optional[Decimal] = None
    financial_impact_max_eur: Optional[Decimal] = None
    impact_distribution: ImpactDistribution = None
    treatment_decision_id: Optional[UUID] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    status: Optional[str] = None
    owner_user_id: Optional[UUID] = None
    cyclus_id: Optional[int] = None
    financial_impact_eur: Optional[Decimal] = None
    financial_impact_min_eur: Optional[Decimal] = None
    financial_impact_max_eur: Optional[Decimal] = None
    impact_distribution: ImpactDistribution = None
    treatment_decision_id: Optional[UUID] = None


class RiskResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    scope_id: UUID
    domain: str
    title: str
    description: str
    likelihood: int
    impact: int
    risk_score: int
    financial_impact_eur: Optional[Decimal]
    financial_impact_min_eur: Optional[Decimal]
    financial_impact_max_eur: Optional[Decimal]
    impact_distribution: ImpactDistribution
    risk_level: str
    status: str
    owner_user_id: Optional[UUID]
    cyclus_id: Optional[int]
    treatment_decision_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── M5: Simulation response ────────────────────────────────────────────────


class SimulationStatistics(BaseModel):
    mean: float
    std: float
    min: float
    max: float


class SimulationPercentiles(BaseModel):
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    p99: float


class RiskSimulationResponse(BaseModel):
    risk_id: UUID
    distribution: str
    parameters: dict
    iterations: int
    statistics: SimulationStatistics
    percentiles: SimulationPercentiles
    expected_loss: float  # gemiddelde van alle simulaties
    var_95: float          # Value-at-Risk op 95% niveau (= p95)
    var_99: float          # Value-at-Risk op 99% niveau (= p99)
    samples: Optional[list[float]] = None
    # Ruwe trekkingen voor histogram/CDF-visualisatie. Default afwezig om payload
    # klein te houden (10k floats ≈ 80kB JSON). Aanvragen via ?include_samples=true.
    simulation_id: Optional[UUID] = None
    # ID van de bijhorende ims_risk_simulations-row, voor het opvragen of
    # vergelijken van eerdere runs.


class RiskSimulationHistoryItem(BaseModel):
    """Samenvatting per opgeslagen Monte Carlo-run (zonder samples)."""

    id: UUID
    risk_id: UUID
    user_id: Optional[UUID]
    distribution: str
    parameters: dict
    iterations: int
    seed: Optional[int]
    expected_loss: float
    var_95: float
    var_99: float
    percentiles: dict
    statistics: dict
    label: Optional[str]
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── IMSRiskControlLink ─────────────────────────────────────────────────────


class RiskControlLinkCreate(BaseModel):
    risk_id: UUID
    control_id: UUID


class RiskControlLinkResponse(BaseModel):
    risk_id: UUID
    control_id: UUID

    model_config = {"from_attributes": True}
