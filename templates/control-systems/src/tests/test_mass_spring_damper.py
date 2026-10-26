"""
Mass-spring-damper contract tests.

Checks the damping ratio and natural frequency, the regime classification, the state-space poles against the
characteristic polynomial, the overshoot formula against a simulated step, and convergence to F/k.
"""

import numpy as np
import pytest

from ..scenarios.mass_spring_damper import (
    classify_damping,
    damping_ratio,
    natural_frequency,
    percent_overshoot,
    simulate_scenario,
    state_space,
    step_response,
)


class TestParameters:
    """ω_n = √(k/m) and ζ = c/(2√(km))."""

    def test_natural_frequency_and_damping_ratio(self):
        assert natural_frequency(1.0, 4.0) == pytest.approx(2.0)
        assert damping_ratio(1.0, 0.4, 4.0) == pytest.approx(0.1)

    @pytest.mark.parametrize(
        ("c", "expected"),
        [(0.4, "underdamped"), (4.0, "critically_damped"), (8.0, "overdamped")],
    )
    def test_regime_from_damping(self, c, expected):
        assert classify_damping(damping_ratio(1.0, c, 4.0)) == expected


class TestPoles:
    """The state-space poles are the roots of m·s² + c·s + k."""

    def test_poles_match_characteristic_polynomial(self):
        m, c, k = 2.0, 3.0, 8.0
        poles = np.sort_complex(state_space(m, c, k).poles())
        roots = np.sort_complex(np.roots([m, c, k]))

        assert np.allclose(poles, roots)

    def test_stable_for_positive_damping(self):
        assert state_space(1.0, 0.4, 4.0).is_stable()


class TestOvershoot:
    """The simulated overshoot matches the closed form for an underdamped system."""

    def test_overshoot_formula_at_zeta_point_one(self):
        assert percent_overshoot(0.1) == pytest.approx(72.92, abs=0.01)

    def test_no_overshoot_when_critically_or_over_damped(self):
        assert percent_overshoot(1.0) == 0.0
        assert percent_overshoot(2.0) == 0.0

    def test_simulated_overshoot_matches_formula(self):
        result = simulate_scenario()

        assert result["measured_overshoot_percent"] == pytest.approx(result["analytic_overshoot_percent"], abs=0.1)


class TestSteadyState:
    """The response converges to F/k. The decay rate is ζ·ω_n, so a long horizon is needed at ζ = 0.1."""

    def test_converges_to_static_deflection(self):
        t, x = step_response(1.0, 0.4, 4.0, force=1.0, t_end=40.0)

        assert x[-1] == pytest.approx(0.25, abs=1e-3)
        assert t[-1] == pytest.approx(40.0)
