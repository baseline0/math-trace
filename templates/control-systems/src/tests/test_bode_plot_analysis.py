"""
Bode plot analysis contract tests.

Checks the grid peak and bandwidth against the closed forms, the phase at the natural frequency,
and that heavily damped prototypes have no resonance peak.
"""

import numpy as np
import pytest

from ..scenarios.bode_plot_analysis import (
    analyse,
    bandwidth_3db,
    frequency_response,
    phase_deg,
    resonance_frequency,
    resonance_peak,
)


class TestClosedForms:
    """Closed-form peak and bandwidth."""

    def test_resonance_peak_at_zeta_point_one(self):
        assert resonance_peak(0.1) == pytest.approx(5.0249, rel=1e-4)

    def test_resonance_frequency_below_natural(self):
        assert resonance_frequency(1.0, 0.1) == pytest.approx(np.sqrt(1 - 2 * 0.01))

    def test_no_peak_when_zeta_at_least_one_over_root_two(self):
        assert resonance_frequency(1.0, 0.8) is None
        assert resonance_peak(0.8) == 1.0


class TestGridAgreement:
    """The sampled response reproduces the closed-form peak and bandwidth."""

    @pytest.mark.parametrize("zeta", [0.1, 0.3])
    def test_grid_peak_matches_closed_form(self, zeta):
        result = analyse(omega_n=1.0, zeta=zeta)

        assert result["grid_peak_db"] == pytest.approx(result["analytic_peak_db"], abs=0.01)
        assert result["grid_peak_frequency"] == pytest.approx(result["analytic_peak_frequency"], rel=1e-3)

    @pytest.mark.parametrize("zeta", [0.1, 0.3, 0.7])
    def test_grid_bandwidth_matches_closed_form(self, zeta):
        result = analyse(omega_n=1.0, zeta=zeta)

        assert result["grid_bandwidth_3db"] == pytest.approx(result["analytic_bandwidth_3db"], rel=1e-3)


class TestPhase:
    """The phase is -90° at the natural frequency for any damping."""

    @pytest.mark.parametrize("zeta", [0.1, 0.5, 0.9])
    def test_phase_is_minus_ninety_at_natural_frequency(self, zeta):
        response = frequency_response(np.array([1.0]), 1.0, zeta)

        assert phase_deg(response)[0] == pytest.approx(-90.0)

    def test_dc_gain_is_unity(self):
        response = frequency_response(np.array([1e-9]), 1.0, 0.3)

        assert abs(response[0]) == pytest.approx(1.0, rel=1e-6)


def test_bandwidth_formula_at_zeta_zero_point_seven_is_natural_frequency_band():
    """At ζ = 1/√2 the -3 dB bandwidth is exactly ω_n, the boundary where the resonance peak disappears."""
    assert bandwidth_3db(1.0, 1 / np.sqrt(2)) == pytest.approx(1.0, rel=1e-9)
