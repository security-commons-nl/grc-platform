"""Unit tests voor Monte Carlo-simulator (M5)."""

import numpy as np
import pytest

from app.services.simulation.monte_carlo import (
    SUPPORTED_DISTRIBUTIONS,
    simulate_risk,
)


# ── Uniform ─────────────────────────────────────────────────────────────────


def test_uniform_basic_stats():
    """Uniform(10, 20) heeft mean ≈ 15 en std ≈ (20-10)/sqrt(12) ≈ 2.887."""
    r = simulate_risk(
        "uniform", min_value=10, max_value=20, iterations=50_000, seed=42
    )
    assert 14.9 < r.mean < 15.1
    expected_std = (20 - 10) / np.sqrt(12)
    assert abs(r.std - expected_std) < 0.05


def test_uniform_all_samples_within_range():
    r = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=10_000, seed=1
    )
    assert r.sample_min >= 0
    assert r.sample_max <= 100


def test_uniform_requires_min_and_max():
    with pytest.raises(ValueError, match="min_value and max_value"):
        simulate_risk("uniform", max_value=10, iterations=1000)


def test_uniform_max_below_min_rejected():
    with pytest.raises(ValueError, match="must be >="):
        simulate_risk("uniform", min_value=100, max_value=50, iterations=1000)


# ── Triangular ──────────────────────────────────────────────────────────────


def test_triangular_basic_stats():
    """Triangular(0, 5, 10) heeft mean = (0+5+10)/3 ≈ 5."""
    r = simulate_risk(
        "triangular",
        min_value=0,
        max_value=10,
        mode=5,
        iterations=50_000,
        seed=42,
    )
    assert 4.95 < r.mean < 5.05


def test_triangular_skewed_right():
    """Triangular(0, 1, 10) heeft mode dicht bij min → rechtskewe distributie.
    P50 < mean."""
    r = simulate_risk(
        "triangular",
        min_value=0,
        max_value=10,
        mode=1,
        iterations=50_000,
        seed=42,
    )
    assert r.percentile(50) < r.mean


def test_triangular_requires_all_three_params():
    with pytest.raises(ValueError, match="min_value, max_value, and mode"):
        simulate_risk(
            "triangular", min_value=0, max_value=10, iterations=1000
        )


def test_triangular_mode_outside_range_rejected():
    with pytest.raises(ValueError, match="must lie between"):
        simulate_risk(
            "triangular",
            min_value=0,
            max_value=10,
            mode=15,  # buiten range
            iterations=1000,
        )


def test_triangular_collapsed_range_rejected():
    with pytest.raises(ValueError, match="max_value > min_value"):
        simulate_risk(
            "triangular",
            min_value=10,
            max_value=10,
            mode=10,
            iterations=1000,
        )


# ── Algemeen ────────────────────────────────────────────────────────────────


def test_unsupported_distribution_rejected():
    with pytest.raises(ValueError, match="Unsupported distribution"):
        simulate_risk("normal", iterations=1000)


def test_iterations_below_minimum_rejected():
    with pytest.raises(ValueError, match="iterations must be between"):
        simulate_risk(
            "uniform", min_value=0, max_value=1, iterations=10
        )


def test_iterations_above_maximum_rejected():
    with pytest.raises(ValueError, match="iterations must be between"):
        simulate_risk(
            "uniform", min_value=0, max_value=1, iterations=10_000_000
        )


def test_seed_makes_results_reproducible():
    """Twee runs met dezelfde seed moeten identieke samples geven."""
    a = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=1000, seed=123
    )
    b = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=1000, seed=123
    )
    assert np.array_equal(a.samples, b.samples)


def test_no_seed_gives_different_runs():
    """Twee runs zonder seed mogen niet identiek zijn (zou wijzen op een bug
    waardoor productie altijd dezelfde simulatie geeft)."""
    a = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=1000
    )
    b = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=1000
    )
    assert not np.array_equal(a.samples, b.samples)


def test_percentiles_are_monotonic_increasing():
    r = simulate_risk(
        "uniform", min_value=0, max_value=100, iterations=10_000, seed=7
    )
    assert r.percentile(5) <= r.percentile(25) <= r.percentile(50)
    assert r.percentile(50) <= r.percentile(75) <= r.percentile(95)


def test_supported_distributions_constant_present():
    assert "uniform" in SUPPORTED_DISTRIBUTIONS
    assert "triangular" in SUPPORTED_DISTRIBUTIONS
