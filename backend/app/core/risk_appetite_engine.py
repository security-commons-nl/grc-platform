"""
Risk Appetite Engine — Rekenmodel voor dynamische risicotolerantie.

Vertaalt organisatie-brede RiskAppetite-instellingen naar:
1. Per-cel heatmap classificatie (acceptabel / escalatie / onacceptabel)
2. RiskScope acceptability check
3. Drempelwaarden voor de 4x4 risicomatrix
"""
import json
from typing import Optional
from app.models.core_models import (
    RiskAppetite,
    RiskAppetiteLevel,
    RiskLevel,
    RiskScope,
)

# =============================================================================
# RISK LEVEL NUMERIC MAPPING
# =============================================================================

RISK_LEVEL_VALUE = {
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}

# Reverse: int → RiskLevel
VALUE_RISK_LEVEL = {v: k for k, v in RISK_LEVEL_VALUE.items()}


# =============================================================================
# APPETITE LEVEL → MAX ACCEPTABLE IMPACT
# =============================================================================
# Defines the maximum impact level that is generally acceptable per appetite level.
# Above this, risks must be mitigated/escalated regardless of likelihood.

APPETITE_MAX_IMPACT = {
    RiskAppetiteLevel.AVERSE: 1,     # Only LOW impact acceptable
    RiskAppetiteLevel.MINIMAL: 1,    # Only LOW impact acceptable
    RiskAppetiteLevel.CAUTIOUS: 2,   # Up to MEDIUM impact
    RiskAppetiteLevel.MODERATE: 2,   # Up to MEDIUM, HIGH only if low likelihood
    RiskAppetiteLevel.OPEN: 3,       # Up to HIGH impact
    RiskAppetiteLevel.HUNGRY: 4,     # All impact levels considered
}

# For MODERATE and OPEN, high-impact risks may still be acceptable if likelihood is low.
# This maps appetite → (max_impact, max_likelihood_for_higher_impact)
APPETITE_CONDITIONAL_RULES = {
    RiskAppetiteLevel.MODERATE: {
        "base_max_impact": 2,
        "conditional_impact": 3,       # Impact 3 (HIGH) is conditionally acceptable
        "max_likelihood_for_conditional": 2,  # Only if likelihood ≤ MEDIUM
    },
    RiskAppetiteLevel.OPEN: {
        "base_max_impact": 3,
        "conditional_impact": 4,       # Impact 4 (CRITICAL) is conditionally acceptable
        "max_likelihood_for_conditional": 1,  # Only if likelihood = LOW
    },
}


# =============================================================================
# HEATMAP CLASSIFICATION
# =============================================================================

class HeatmapZone:
    ACCEPTABLE = "acceptable"         # Within appetite — green
    CONDITIONAL = "conditional"       # Within appetite if conditions met — yellow
    ESCALATION = "escalation"         # Above appetite, needs management decision — orange
    UNACCEPTABLE = "unacceptable"     # Far above appetite, must mitigate — red


def classify_cell(
    appetite_level: RiskAppetiteLevel,
    likelihood: int,
    impact: int,
) -> str:
    """
    Classify a heatmap cell (likelihood × impact) against the appetite level.

    Args:
        appetite_level: The organization's appetite setting
        likelihood: 1-4 (LOW=1, CRITICAL=4)
        impact: 1-4

    Returns:
        HeatmapZone classification string
    """
    max_impact = APPETITE_MAX_IMPACT.get(appetite_level, 2)

    # Check base acceptability
    if impact <= max_impact:
        # Exception: even within appetite, very high likelihood (4) with impact > 1
        # is always escalation (daily occurrence of any meaningful loss)
        if likelihood == 4 and impact > 1:
            return HeatmapZone.ESCALATION
        return HeatmapZone.ACCEPTABLE

    # Check conditional rules
    conditional = APPETITE_CONDITIONAL_RULES.get(appetite_level)
    if conditional and impact <= conditional["conditional_impact"]:
        if likelihood <= conditional["max_likelihood_for_conditional"]:
            return HeatmapZone.CONDITIONAL

    # Above appetite
    score = likelihood * impact
    if score >= 12:  # 3×4, 4×3, 4×4
        return HeatmapZone.UNACCEPTABLE

    return HeatmapZone.ESCALATION


def generate_heatmap_matrix(appetite_level: RiskAppetiteLevel) -> list[list[dict]]:
    """
    Generate a full 4×4 heatmap matrix with zone classifications.

    Returns:
        4×4 matrix where [likelihood_idx][impact_idx] = {
            "likelihood": int, "impact": int,
            "score": int, "zone": str
        }
        likelihood_idx 0 = LOW (1), 3 = CRITICAL (4)
        impact_idx 0 = LOW (1), 3 = CRITICAL (4)
    """
    matrix = []
    for likelihood in range(1, 5):
        row = []
        for impact in range(1, 5):
            zone = classify_cell(appetite_level, likelihood, impact)
            row.append({
                "likelihood": likelihood,
                "impact": impact,
                "score": likelihood * impact,
                "zone": zone,
            })
        matrix.append(row)
    return matrix


# =============================================================================
# FINANCIAL THRESHOLD → IMPACT MAPPING
# =============================================================================

def resolve_financial_impact_level(
    threshold_value: int,
    impact_correlation: dict,
) -> int:
    """
    Map a financial threshold (e.g. €50.000) to an impact level (1-4)
    using the impact_correlation config.

    Args:
        threshold_value: Max acceptable single-event loss in euros
        impact_correlation: {"LOW": 10000, "MEDIUM": 100000, ...} — upper bounds per level

    Returns:
        Maximum acceptable impact level (1-4)
    """
    # Sort by value ascending to find which bucket the threshold falls into
    level_map = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    max_acceptable = 1
    for level_name in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        upper_bound = impact_correlation.get(level_name, 0)
        if threshold_value >= upper_bound:
            max_acceptable = level_map[level_name]
        else:
            break

    return max_acceptable


# =============================================================================
# RISK SCOPE EVALUATION
# =============================================================================

def evaluate_risk_scope(
    risk_scope: RiskScope,
    appetite: RiskAppetite,
    category: Optional[str] = None,
) -> dict:
    """
    Evaluate a RiskScope against the active RiskAppetite.

    Returns dict with:
        - is_acceptable: bool
        - zone: HeatmapZone string
        - requires_decision: bool
        - requires_escalation: bool
        - reason: str (human-readable explanation)
    """
    # Get the relevant appetite level
    appetite_level = _get_domain_appetite(appetite, category)

    # Get residual scores (these are what matters for acceptance)
    res_likelihood = RISK_LEVEL_VALUE.get(risk_scope.residual_likelihood, 0)
    res_impact = RISK_LEVEL_VALUE.get(risk_scope.residual_impact, 0)
    res_score = risk_scope.residual_risk_score or (res_likelihood * res_impact)

    if res_likelihood == 0 or res_impact == 0:
        return {
            "is_acceptable": None,
            "zone": None,
            "requires_decision": False,
            "requires_escalation": False,
            "reason": "Residueel risico nog niet beoordeeld",
        }

    # Classify against appetite
    zone = classify_cell(appetite_level, res_likelihood, res_impact)

    # Check against hard thresholds
    escalation_value = RISK_LEVEL_VALUE.get(appetite.escalation_threshold, 3)
    max_score = appetite.max_acceptable_risk_score

    is_acceptable = zone == HeatmapZone.ACCEPTABLE
    requires_decision = (
        zone in (HeatmapZone.ESCALATION, HeatmapZone.CONDITIONAL)
        or res_score > max_score
    )
    requires_escalation = (
        zone == HeatmapZone.UNACCEPTABLE
        or res_impact >= escalation_value
    )

    # Build reason
    if is_acceptable:
        reason = f"Residueel risico ({res_score}) valt binnen appetite ({appetite_level.value})"
    elif requires_escalation:
        reason = (
            f"Residueel risico ({res_score}) overschrijdt escalatiedrempel "
            f"({appetite.escalation_threshold.value}). Managementbesluit vereist."
        )
    elif requires_decision:
        reason = (
            f"Residueel risico ({res_score}) valt buiten appetite ({appetite_level.value}). "
            f"Besluit of behandeling vereist."
        )
    else:
        reason = f"Residueel risico ({res_score}) — beoordeling nodig"

    return {
        "is_acceptable": is_acceptable,
        "zone": zone,
        "requires_decision": requires_decision,
        "requires_escalation": requires_escalation,
        "residual_score": res_score,
        "appetite_level": appetite_level.value,
        "reason": reason,
    }


def _get_domain_appetite(
    appetite: RiskAppetite,
    category: Optional[str],
) -> RiskAppetiteLevel:
    """Get the most specific appetite level for a risk category."""
    if category:
        cat_lower = category.lower()
        domain_map = {
            "financial": appetite.financial_appetite,
            "financieel": appetite.financial_appetite,
            "legal": appetite.compliance_appetite,
            "juridisch": appetite.compliance_appetite,
            "compliance": appetite.compliance_appetite,
            "reputation": appetite.reputational_appetite,
            "reputatie": appetite.reputational_appetite,
            "operational": appetite.isms_appetite,
            "operationeel": appetite.isms_appetite,
            "isms": appetite.isms_appetite,
            "privacy": appetite.pims_appetite,
            "pims": appetite.pims_appetite,
            "bcm": appetite.bcms_appetite,
            "continuity": appetite.bcms_appetite,
        }
        domain_appetite = domain_map.get(cat_lower)
        if domain_appetite:
            return domain_appetite

    return appetite.overall_appetite


# =============================================================================
# BULK EVALUATION (for dashboard)
# =============================================================================

def evaluate_scope_risks_bulk(
    risk_scopes: list[RiskScope],
    appetite: RiskAppetite,
) -> dict:
    """
    Evaluate multiple RiskScopes and return aggregate stats.

    Returns:
        {
            "total": int,
            "acceptable": int,
            "conditional": int,
            "escalation": int,
            "unacceptable": int,
            "not_assessed": int,
            "requires_decision_count": int,
            "details": [...]  # per-risk evaluations
        }
    """
    stats = {
        "total": len(risk_scopes),
        "acceptable": 0,
        "conditional": 0,
        "escalation": 0,
        "unacceptable": 0,
        "not_assessed": 0,
        "requires_decision_count": 0,
        "details": [],
    }

    for rs in risk_scopes:
        # Try to get category from the risk itself
        category = None  # Would need risk.risk_category — passed separately
        evaluation = evaluate_risk_scope(rs, appetite, category)
        stats["details"].append({
            "risk_scope_id": rs.id,
            "risk_id": rs.risk_id,
            "scope_id": rs.scope_id,
            **evaluation,
        })

        zone = evaluation.get("zone")
        if zone is None:
            stats["not_assessed"] += 1
        elif zone == HeatmapZone.ACCEPTABLE:
            stats["acceptable"] += 1
        elif zone == HeatmapZone.CONDITIONAL:
            stats["conditional"] += 1
        elif zone == HeatmapZone.ESCALATION:
            stats["escalation"] += 1
        elif zone == HeatmapZone.UNACCEPTABLE:
            stats["unacceptable"] += 1

        if evaluation.get("requires_decision"):
            stats["requires_decision_count"] += 1

    return stats
