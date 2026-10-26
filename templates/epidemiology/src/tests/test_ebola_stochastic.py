"""
Ebola stochastic SEIR contract tests.

Checks the scenario's parameters, the integer conservation of every run, seed reproducibility,
and that the ensemble mean final size agrees with the deterministic SEIR final size.
"""

import numpy as np
import pytest

from ..scenarios.ebola_stochastic import (
    deterministic_final_size,
    ebola_parameters,
    run_ensemble,
    simulate_scenario,
    summarise,
)


class TestEbolaParameters:
    """R₀ = β/γ must hold by construction."""

    def test_r0_is_beta_over_gamma(self):
        params = ebola_parameters()
        assert params["beta"] / params["gamma"] == pytest.approx(params["R0"])
        assert params["R0"] == 1.8


class TestEnsembleConservation:
    """Integer compartment counts sum to the population at every step of every run."""

    def test_counts_sum_to_population(self):
        population = 10000
        _t, ensemble, _params = run_ensemble(population=population, num_runs=3, t_max=120.0)

        assert ensemble.shape[0] == 3
        assert np.all(ensemble.sum(axis=2) == population)


class TestSeedReproducibility:
    """The same seed gives the same ensemble."""

    def test_same_seed_same_ensemble(self):
        _t, first, _ = run_ensemble(num_runs=2, t_max=120.0, seed=11)
        _t, second, _ = run_ensemble(num_runs=2, t_max=120.0, seed=11)

        assert np.array_equal(first, second)


class TestAgreementWithDeterministic:
    """Ensemble mean final size tracks the deterministic SEIR final size."""

    def test_mean_final_size_matches_deterministic(self):
        population = 10000
        _t, ensemble, params = run_ensemble(population=population, num_runs=10)
        summary = summarise(ensemble, population, params["case_fatality_ratio"])
        deterministic = deterministic_final_size(population=population)

        assert abs(summary["mean_final_attack_rate"] - deterministic) < 0.05

    def test_deterministic_final_size_is_epidemic_for_r0_above_one(self):
        assert deterministic_final_size() > 0.5


class TestScenarioOutputs:
    """The scenario's reported quantities are consistent with the raw ensemble."""

    def test_deaths_are_cfr_times_removed(self):
        result = simulate_scenario()
        removed_final = result["ensemble"][:, -1, 3]

        assert np.allclose(result["estimated_deaths"], 0.5 * removed_final)
