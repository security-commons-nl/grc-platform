"""Monte Carlo-simulator voor financiële impact-distributies.

Ondersteunde distributies:
- `uniform(min, max)` — elke waarde tussen min en max even waarschijnlijk
- `triangular(min, mode, max)` — driehoekige verdeling met piek op mode
  (in dit platform: mode = `financial_impact_eur`)

Deterministisch wanneer een `seed` wordt meegegeven, anders niet-
deterministisch (NumPy's default_rng). Voor productie zonder seed,
voor tests met seed.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np


SUPPORTED_DISTRIBUTIONS = ("uniform", "triangular")
DEFAULT_ITERATIONS = 10_000
MIN_ITERATIONS = 1_000
MAX_ITERATIONS = 1_000_000


@dataclass(frozen=True)
class SimulationResult:
    distribution: str
    parameters: dict
    iterations: int
    samples: np.ndarray  # ruwe samples — handig voor histogram-rendering later

    @property
    def mean(self) -> float:
        return float(np.mean(self.samples))

    @property
    def std(self) -> float:
        return float(np.std(self.samples))

    @property
    def sample_min(self) -> float:
        return float(np.min(self.samples))

    @property
    def sample_max(self) -> float:
        return float(np.max(self.samples))

    def percentile(self, p: float) -> float:
        return float(np.percentile(self.samples, p))


def simulate_risk(
    distribution: str,
    *,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    mode: Optional[float] = None,
    iterations: int = DEFAULT_ITERATIONS,
    seed: Optional[int] = None,
) -> SimulationResult:
    """Run a Monte Carlo simulation for the given distribution.

    Raises ValueError on invalid input — callers (typically the API layer)
    map this to a 400 / 422 response.
    """
    if distribution not in SUPPORTED_DISTRIBUTIONS:
        raise ValueError(
            f"Unsupported distribution '{distribution}'. "
            f"Supported: {', '.join(SUPPORTED_DISTRIBUTIONS)}"
        )
    if iterations < MIN_ITERATIONS or iterations > MAX_ITERATIONS:
        raise ValueError(
            f"iterations must be between {MIN_ITERATIONS} and {MAX_ITERATIONS}, "
            f"got {iterations}"
        )

    rng = np.random.default_rng(seed)

    if distribution == "uniform":
        if min_value is None or max_value is None:
            raise ValueError("uniform requires min_value and max_value")
        if max_value < min_value:
            raise ValueError(
                f"max_value ({max_value}) must be >= min_value ({min_value})"
            )
        samples = rng.uniform(low=min_value, high=max_value, size=iterations)
        params = {"min": min_value, "max": max_value}

    elif distribution == "triangular":
        if min_value is None or max_value is None or mode is None:
            raise ValueError(
                "triangular requires min_value, max_value, and mode"
            )
        if not (min_value <= mode <= max_value):
            raise ValueError(
                f"mode ({mode}) must lie between min_value ({min_value}) "
                f"and max_value ({max_value})"
            )
        if max_value == min_value:
            raise ValueError("triangular requires max_value > min_value")
        samples = rng.triangular(
            left=min_value, mode=mode, right=max_value, size=iterations
        )
        params = {"min": min_value, "mode": mode, "max": max_value}

    else:  # pragma: no cover — covered by SUPPORTED_DISTRIBUTIONS check above
        raise ValueError(f"Unsupported distribution: {distribution}")

    return SimulationResult(
        distribution=distribution,
        parameters=params,
        iterations=iterations,
        samples=samples,
    )
