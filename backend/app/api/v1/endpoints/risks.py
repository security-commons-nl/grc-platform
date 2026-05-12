from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSRisk, IMSRiskControlLink, IMSRiskSimulation, User
from app.schemas.risks import (
    RiskCreate, RiskUpdate, RiskResponse,
    RiskControlLinkCreate, RiskControlLinkResponse,
    RiskSimulationResponse, RiskSimulationHistoryItem,
    SimulationStatistics, SimulationPercentiles,
)
from app.services.simulation import simulate_risk

router = APIRouter()


def calculate_risk_level(score: int) -> str:
    if score <= 4:
        return "groen"
    if score <= 9:
        return "geel"
    if score <= 14:
        return "oranje"
    return "rood"


# ── Risks ──────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[RiskResponse])
async def list_risks(
    domain: str | None = None,
    status: str | None = None,
    scope_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRisk).where(IMSRisk.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(IMSRisk.domain == domain)
    if status:
        query = query.where(IMSRisk.status == status)
    if scope_id:
        query = query.where(IMSRisk.scope_id == scope_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risico niet gevonden")
    return risk


@router.post("/", response_model=RiskResponse, status_code=201)
async def create_risk(
    data: RiskCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    risk_score = data.likelihood * data.impact
    risk_level = calculate_risk_level(risk_score)

    risk_data = data.model_dump()
    risk_data.pop("likelihood", None)
    risk_data.pop("impact", None)

    risk = IMSRisk(
        tenant_id=current_user.tenant_id,
        likelihood=data.likelihood,
        impact=data.impact,
        risk_level=risk_level,
        **risk_data,
    )
    db.add(risk)
    await db.flush()
    await db.refresh(risk)
    return risk


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: UUID,
    data: RiskUpdate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risico niet gevonden")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(risk, field, value)

    # Recalculate risk_level if likelihood or impact changed
    likelihood = update_data.get("likelihood", risk.likelihood)
    impact = update_data.get("impact", risk.impact)
    if "likelihood" in update_data or "impact" in update_data:
        risk_score = likelihood * impact
        risk.risk_level = calculate_risk_level(risk_score)

    await db.flush()
    await db.refresh(risk)
    return risk


@router.delete("/{risk_id}", status_code=204)
async def delete_risk(
    risk_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSRisk).where(IMSRisk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risico niet gevonden")
    # Delete associated risk-control links first
    links_result = await db.execute(
        select(IMSRiskControlLink).where(IMSRiskControlLink.risk_id == risk_id)
    )
    for link in links_result.scalars().all():
        await db.delete(link)
    await db.delete(risk)
    await db.flush()


# ── M5: Risicokwantificatie ────────────────────────────────────────────────


@router.post("/{risk_id}/simulate", response_model=RiskSimulationResponse)
async def simulate_risk_endpoint(
    risk_id: UUID,
    iterations: int = Query(10000, ge=1000, le=1000000),
    seed: int | None = Query(None, description="Optional seed for reproducibility"),
    include_samples: bool = Query(
        False,
        description=(
            "Voeg ruwe samples toe aan response voor histogram/CDF-visualisatie. "
            "Default false — bij 10k iteraties is dit ~80kB JSON extra."
        ),
    ),
    label: str | None = Query(
        None,
        max_length=200,
        description="Optionele annotatie voor de simulatie-run, bv. 'Baseline' of 'Na mitigatie X'.",
    ),
    note: str | None = Query(
        None,
        max_length=2000,
        description="Optionele vrije notitie bij de run (bv. wat is aangepast t.o.v. baseline).",
    ),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Monte Carlo-simulatie op de financiële impact van een risico.

    Het risico moet een distributie hebben gezet (`impact_distribution` =
    'uniform' of 'triangular') en de bijbehorende parameters:
      - uniform: financial_impact_min_eur + financial_impact_max_eur
      - triangular: financial_impact_min_eur + financial_impact_eur (mode)
                    + financial_impact_max_eur

    Returnt percentielen (P5..P99), gemiddelde, standaarddeviatie, en
    Value-at-Risk op 95% en 99% niveau. Wanneer `include_samples=true` is
    de ruwe trekkingen-array bijgevoegd voor frontend-visualisatie.
    """
    result = await db.execute(
        select(IMSRisk).where(
            IMSRisk.id == risk_id,
            IMSRisk.tenant_id == current_user.tenant_id,
        )
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risico niet gevonden")

    if not risk.impact_distribution or risk.impact_distribution == "single":
        raise HTTPException(
            status_code=400,
            detail=(
                "Risico heeft geen distributie geconfigureerd. Zet "
                "impact_distribution op 'uniform' of 'triangular' en vul de "
                "bijbehorende min/max(/mode) velden in."
            ),
        )

    min_v = float(risk.financial_impact_min_eur) if risk.financial_impact_min_eur is not None else None
    max_v = float(risk.financial_impact_max_eur) if risk.financial_impact_max_eur is not None else None
    mode_v = float(risk.financial_impact_eur) if risk.financial_impact_eur is not None else None

    try:
        sim = simulate_risk(
            distribution=risk.impact_distribution,
            min_value=min_v,
            max_value=max_v,
            mode=mode_v,
            iterations=iterations,
            seed=seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    percentiles = {
        "p5":  sim.percentile(5),
        "p25": sim.percentile(25),
        "p50": sim.percentile(50),
        "p75": sim.percentile(75),
        "p95": sim.percentile(95),
        "p99": sim.percentile(99),
    }
    statistics = {
        "mean": sim.mean,
        "std":  sim.std,
        "min":  sim.sample_min,
        "max":  sim.sample_max,
    }

    # Persist samenvatting in historie. Samples niet opslaan (reproductie via seed).
    # user_id alleen zetten als de gebruiker echt in users-table staat — bij
    # agent-tokens (NHI) of dev-tokens met fictieve sub klopt current_user.id
    # niet met een users-row en zou de FK-insert falen.
    user_check = await db.execute(
        select(User.id).where(User.id == current_user.id)
    )
    persisted_user_id = (
        current_user.id if user_check.scalar_one_or_none() is not None else None
    )

    history_row = IMSRiskSimulation(
        tenant_id=current_user.tenant_id,
        risk_id=risk.id,
        user_id=persisted_user_id,
        distribution=sim.distribution,
        parameters=sim.parameters,
        iterations=sim.iterations,
        seed=seed,
        expected_loss=Decimal(str(round(sim.mean, 2))),
        var_95=Decimal(str(round(sim.percentile(95), 2))),
        var_99=Decimal(str(round(sim.percentile(99), 2))),
        percentiles=percentiles,
        statistics=statistics,
        label=label,
        note=note,
    )
    db.add(history_row)
    await db.flush()
    await db.refresh(history_row)

    return RiskSimulationResponse(
        risk_id=risk.id,
        distribution=sim.distribution,
        parameters=sim.parameters,
        iterations=sim.iterations,
        statistics=SimulationStatistics(
            mean=sim.mean,
            std=sim.std,
            min=sim.sample_min,
            max=sim.sample_max,
        ),
        percentiles=SimulationPercentiles(**percentiles),
        expected_loss=sim.mean,
        var_95=sim.percentile(95),
        var_99=sim.percentile(99),
        samples=sim.samples.tolist() if include_samples else None,
        simulation_id=history_row.id,
    )


@router.get(
    "/{risk_id}/simulations",
    response_model=list[RiskSimulationHistoryItem],
)
async def list_risk_simulations(
    risk_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Historie van Monte Carlo-runs voor dit risico, nieuwste eerst.

    Tenant-isolatie via RLS én expliciete `tenant_id`-filter. Samples zitten
    bewust niet in de respons — alleen de samenvatting per run.
    """
    # Risico moet bestaan binnen tenant — anders 404, niet lege lijst.
    risk_q = await db.execute(
        select(IMSRisk).where(
            IMSRisk.id == risk_id,
            IMSRisk.tenant_id == current_user.tenant_id,
        )
    )
    if not risk_q.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Risico niet gevonden")

    query = (
        select(IMSRiskSimulation)
        .where(
            IMSRiskSimulation.tenant_id == current_user.tenant_id,
            IMSRiskSimulation.risk_id == risk_id,
        )
        .order_by(desc(IMSRiskSimulation.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


# ── Risk-Control Links ─────────────────────────────────────────────────────


@router.get("/links/", response_model=list[RiskControlLinkResponse])
async def list_risk_control_links(
    risk_id: UUID | None = None,
    control_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSRiskControlLink)
    if risk_id:
        query = query.where(IMSRiskControlLink.risk_id == risk_id)
    if control_id:
        query = query.where(IMSRiskControlLink.control_id == control_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/links/", response_model=RiskControlLinkResponse, status_code=201)
async def create_risk_control_link(
    data: RiskControlLinkCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    link = IMSRiskControlLink(**data.model_dump())
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


@router.delete("/links/{risk_id}/{control_id}", status_code=204)
async def delete_risk_control_link(
    risk_id: UUID,
    control_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSRiskControlLink).where(
            and_(
                IMSRiskControlLink.risk_id == risk_id,
                IMSRiskControlLink.control_id == control_id,
            )
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Risico-control koppeling niet gevonden")
    await db.delete(link)
    await db.flush()
