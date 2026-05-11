"""Monte Carlo-simulatie voor risicokwantificatie (M5).

Bewust deterministisch wanneer een random seed wordt meegegeven — voor
tests en reproduceerbaarheid. NumPy is de enige dependency.
"""

from app.services.simulation.monte_carlo import (
    SimulationResult,
    simulate_risk,
)

__all__ = ["SimulationResult", "simulate_risk"]
