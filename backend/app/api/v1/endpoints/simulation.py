import json
import random
import math
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.core_models import (
    Risk,
    RiskQuantificationProfile,
    RiskLevel
)
from app.core.crud import CRUDBase

router = APIRouter()
crud_profile = CRUDBase(RiskQuantificationProfile)
crud_risk = CRUDBase(Risk)

# Default configuration values
DEFAULT_GLOBAL_CONFIG = {
    "LOW": {"freq_min": 0.05, "freq_max": 0.2, "impact_min": 1000, "impact_max": 10000},
    "MEDIUM": {"freq_min": 0.2, "freq_max": 1.0, "impact_min": 10000, "impact_max": 50000},
    "HIGH": {"freq_min": 1.0, "freq_max": 5.0, "impact_min": 50000, "impact_max": 250000},
    "CRITICAL": {"freq_min": 5.0, "freq_max": 10.0, "impact_min": 250000, "impact_max": 1000000},
}

def poisson_sample(lmbda: float) -> int:
    """Sample from Poisson distribution using Knuth's algorithm."""
    if lmbda > 30: # Use normal approximation for large lambda
        return int(max(0, random.gauss(lmbda, math.sqrt(lmbda))))

    L = math.exp(-lmbda)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

@router.get("/config", response_model=RiskQuantificationProfile)
async def get_config(
    # TODO: Replace Query param with Depends(get_current_tenant) from auth context
    # This is a security risk - tenant_id should come from authenticated user context
    tenant_id: int = Query(..., description="Tenant ID"),
    session: AsyncSession = Depends(get_session),
):
    """Get the quantification profile for a tenant, or default if none exists."""
    result = await session.execute(
        select(RiskQuantificationProfile).where(RiskQuantificationProfile.tenant_id == tenant_id)
    )
    profile = result.scalars().first()

    if not profile:
        # Create a transient default profile (not saved yet)
        profile = RiskQuantificationProfile(
            tenant_id=tenant_id,
            global_config=json.dumps(DEFAULT_GLOBAL_CONFIG),
            category_configs=json.dumps({})
        )

    return profile

@router.post("/config", response_model=RiskQuantificationProfile)
async def save_config(
    profile_in: RiskQuantificationProfile,
    session: AsyncSession = Depends(get_session),
):
    """Create or update the quantification profile."""
    result = await session.execute(
        select(RiskQuantificationProfile).where(RiskQuantificationProfile.tenant_id == profile_in.tenant_id)
    )
    existing_profile = result.scalars().first()

    if existing_profile:
        # Update
        existing_profile.global_config = profile_in.global_config
        existing_profile.category_configs = profile_in.category_configs
        existing_profile.currency = profile_in.currency
        existing_profile.iterations = profile_in.iterations
        session.add(existing_profile)
        await session.commit()
        await session.refresh(existing_profile)
        return existing_profile
    else:
        # Create
        session.add(profile_in)
        await session.commit()
        await session.refresh(profile_in)
        return profile_in

@router.post("/run", response_model=Dict[str, Any])
async def run_simulation(
    # TODO: Replace with Depends(get_current_tenant) from auth context
    tenant_id: int = Query(..., description="Tenant ID"),
    iterations: int = Query(default=10000, ge=100, le=100000, description="Number of iterations (max 100,000)"),
    scope_id: Optional[int] = None,
    risk_ids: Optional[List[int]] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Run Monte Carlo simulation.
    """
    # 1. Fetch Config
    result = await session.execute(
        select(RiskQuantificationProfile).where(RiskQuantificationProfile.tenant_id == tenant_id)
    )
    profile = result.scalars().first()

    global_config = DEFAULT_GLOBAL_CONFIG
    category_configs = {}

    if profile:
        try:
            global_config = json.loads(profile.global_config)
            if profile.category_configs:
                category_configs = json.loads(profile.category_configs)
        except json.JSONDecodeError:
            pass # Use defaults on error

    # 2. Fetch Risks
    query = select(Risk).where(Risk.tenant_id == tenant_id)
    if scope_id:
        query = query.where(Risk.scope_id == scope_id)
    if risk_ids:
        query = query.where(Risk.id.in_(risk_ids))

    result = await session.execute(query)
    risks = result.scalars().all()

    if not risks:
        return {
            "histogram": [],
            "var_95": 0,
            "mean_loss": 0,
            "total_iterations": iterations,
            "risk_count": 0
        }

    # 3. Prepare Simulation Params per Risk
    risk_params = []
    for risk in risks:
        # Determine config to use
        config = global_config

        # Check category override
        if risk.risk_category and risk.risk_category in category_configs:
            # We assume category config overrides specific levels or provides a full set
            # Simple merge:
            cat_cfg = category_configs[risk.risk_category]
            # Check if this category has config for this risk's levels
            # NOTE: Assuming category_config structure matches global: { "LOW": {...} }
            # Or is it just { "impact_min": ... }?
            # Let's assume structure is { "LOW": {...}, "MEDIUM": {...} } just like global
            # If so, we merge/override.
            pass # Logic implemented below

        # Get Likelihood Params
        l_level = risk.inherent_likelihood.upper() if hasattr(risk.inherent_likelihood, 'upper') else "LOW"
        i_level = risk.inherent_impact.upper() if hasattr(risk.inherent_impact, 'upper') else "LOW"

        # Helper to get value with fallback
        def get_param(level, key, default):
            # Check category first
            if risk.risk_category and risk.risk_category in category_configs:
                cat_cfg = category_configs[risk.risk_category]
                if level in cat_cfg and key in cat_cfg[level]:
                    return float(cat_cfg[level][key])

            # Check global
            if level in global_config and key in global_config[level]:
                return float(global_config[level][key])

            return default

        freq_min = get_param(l_level, "freq_min", 0.0)
        freq_max = get_param(l_level, "freq_max", 1.0)

        imp_min = get_param(i_level, "impact_min", 0.0)
        imp_max = get_param(i_level, "impact_max", 1000.0)

        risk_params.append({
            "freq_min": freq_min,
            "freq_max": freq_max,
            "imp_min": imp_min,
            "imp_max": imp_max
        })

    # 4. Run Simulation (offload CPU-bound work to thread pool)
    def run_simulation_sync(risk_params: List[Dict], iterations: int) -> List[float]:
        """CPU-bound simulation - runs in thread pool to avoid blocking event loop."""
        annual_losses = []
        for _ in range(iterations):
            annual_loss = 0.0
            for rp in risk_params:
                freq_rate = random.uniform(rp["freq_min"], rp["freq_max"])
                n_events = poisson_sample(freq_rate)
                if n_events > 0:
                    for _ in range(n_events):
                        annual_loss += random.uniform(rp["imp_min"], rp["imp_max"])
            annual_losses.append(annual_loss)
        return annual_losses

    annual_losses = await asyncio.to_thread(run_simulation_sync, risk_params, iterations)

    # 5. Calculate Stats
    annual_losses.sort()

    mean_loss = sum(annual_losses) / iterations
    var_95 = annual_losses[int(iterations * 0.95)]
    var_99 = annual_losses[int(iterations * 0.99)]
    max_loss = annual_losses[-1]

    # 6. Generate Histogram
    # determine buckets
    if max_loss == 0:
        bins = []
    else:
        num_bins = 20
        bin_width = max_loss / num_bins
        # Or better: remove top 1% outliers for binning to make chart readable
        display_max = annual_losses[int(iterations * 0.99)]
        if display_max == 0: display_max = max_loss

        bin_width = display_max / num_bins

        counts = [0] * (num_bins + 1) # +1 for overflow

        for loss in annual_losses:
            if loss >= display_max:
                counts[-1] += 1
            else:
                bin_idx = int(loss / bin_width)
                counts[bin_idx] += 1

        bins = []
        for i in range(num_bins):
            bins.append({
                "range": f"{int(i*bin_width)}-{int((i+1)*bin_width)}",
                "count": counts[i],
                "min": i*bin_width,
                "max": (i+1)*bin_width
            })
        # Add overflow bin if significant
        if counts[-1] > 0:
            bins.append({
                "range": f">{int(display_max)}",
                "count": counts[-1],
                "min": display_max,
                "max": max_loss
            })

    return {
        "histogram": bins,
        "var_95": var_95,
        "var_99": var_99,
        "mean_loss": mean_loss,
        "total_iterations": iterations,
        "risk_count": len(risks)
    }
