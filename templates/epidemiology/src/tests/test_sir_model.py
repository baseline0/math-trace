"""Test suite: SIR Model validation against analytical solutions."""

import numpy as np
import pytest

from ..model import (
    basic_reproduction_number,
    check_population_conservation,
    propagate_seir,
    propagate_seir_stochastic,
    propagate_sir,
    sir_equilibrium,
)


class TestBasicReproductionNumber:
    """Validate R₀ calculation."""

    def test_r0_covid_parameters(self):
        """COVID-19: R₀ ≈ 2-2.5"""
        beta = 0.25  # per day
        gamma = 0.1  # per day (10-day infectious period)
        R0 = basic_reproduction_number(beta, gamma)

        assert 2.0 <= R0 <= 2.5, f"COVID R₀ expected 2-2.5, got {R0}"

    def test_r0_measles_parameters(self):
        """Measles: R₀ ≈ 12-18 (highly contagious)"""
        beta = 1.5
        gamma = 0.1  # 10-day infectious period
        R0 = basic_reproduction_number(beta, gamma)

        assert 12 <= R0 <= 18, f"Measles R₀ expected 12-18, got {R0}"


class TestSIRPopulationConservation:
    """Verify S + I + R = N throughout evolution."""

    def test_conservation_over_100_days(self):
        """Population conserved to machine precision."""
        S0, I0, R0 = 0.99, 0.01, 0.0
        _t, sol = propagate_sir(S0, I0, R0, t_max=100, dt=0.1, beta=0.25, gamma=0.1)

        error = check_population_conservation(sol, N=1.0)
        assert error < 1e-10, f"Conservation error {error:.2e} too large"


class TestSIREquilibrium:
    """Verify long-time equilibrium matches analytical solution."""

    def test_equilibrium_r0_less_than_one(self):
        """When R₀ < 1, disease dies out."""
        beta = 0.05  # R₀ = 0.5
        gamma = 0.1
        eq = sir_equilibrium(beta, gamma, N=1.0)

        assert eq["R0"] < 1.0
        assert eq["I"] == 0.0


class TestSEIRPopulationConservation:
    """Verify S + E + I + R = N throughout SEIR evolution."""

    def test_seir_conservation_over_100_days(self):
        """Population conserved to machine precision."""
        S0, E0, I0, R0 = 0.98, 0.01, 0.01, 0.0
        _t, sol = propagate_seir(S0, E0, I0, R0, t_max=100, dt=0.1, beta=0.5, sigma=0.1, gamma=0.1)

        total = sol.sum(axis=1)
        assert np.abs(total - 1.0).max() < 1e-10


class TestStochasticSEIR:
    """Verify the Poisson-transition SEIR ensemble."""

    def test_stochastic_conservation_per_run(self):
        """Integer counts sum to N at every step of every run."""
        N = 1000
        _t, ensemble = propagate_seir_stochastic(
            990, 5, 5, 0, t_max=50, dt=0.1, beta=0.5, sigma=0.2, gamma=0.1, N=N, num_runs=3, seed=1
        )

        assert ensemble.shape[0] == 3
        assert np.all(ensemble.sum(axis=2) == N)

    def test_stochastic_same_seed_same_ensemble(self):
        """A fixed seed reproduces the ensemble exactly."""
        args = {"t_max": 30, "dt": 0.1, "beta": 0.4, "sigma": 0.2, "gamma": 0.1, "N": 500, "num_runs": 2, "seed": 7}
        _t, first = propagate_seir_stochastic(495, 0, 5, 0, **args)
        _t, second = propagate_seir_stochastic(495, 0, 5, 0, **args)

        assert np.array_equal(first, second)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
