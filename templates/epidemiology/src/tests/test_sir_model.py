"""Test suite: SIR Model validation against analytical solutions."""

import pytest
import numpy as np
from ..model import (
    basic_reproduction_number,
    propagate_sir,
    check_population_conservation,
    sir_equilibrium,
)


class TestBasicReproductionNumber:
    """Validate R₀ calculation."""
    
    def test_r0_covid_parameters(self):
        """COVID-19: R₀ ≈ 2-2.5"""
        beta = 0.25  # per day
        gamma = 0.1   # per day (10-day infectious period)
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
        t, sol = propagate_sir(S0, I0, R0, t_max=100, dt=0.1, beta=0.25, gamma=0.1)
        
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
