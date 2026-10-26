"""
Double-slit contract tests.

Checks the de Broglie wavelength, the fringe spacing λL/d for a narrow slit (where the envelope is flat),
the envelope zeros, the cos² fringe pattern, and that finite slit width pulls the outer fringes inward.
"""

import numpy as np
import pytest

from ..scenarios.double_slit_interference import (
    ELECTRON_MASS,
    PLANCK,
    de_broglie_wavelength,
    envelope_zero_spacing,
    fringe_peaks,
    fringe_spacing,
    intensity,
    simulate_scenario,
    visibility,
)


def test_de_broglie_wavelength_formula():
    assert de_broglie_wavelength(ELECTRON_MASS, 2.0e6) == pytest.approx(PLANCK / (ELECTRON_MASS * 2.0e6))


def test_fringe_spacing_formula():
    assert fringe_spacing(500e-9, 2.0, 1e-4) == pytest.approx(0.01)


def test_envelope_zero_spacing_formula():
    assert envelope_zero_spacing(500e-9, 2.0, 2e-6) == pytest.approx(0.5)


def test_narrow_slit_fringes_sit_at_multiples_of_spacing():
    wavelength, L, d, w = 500e-9, 1.0, 1e-4, 1e-9  # envelope flat across the window
    spacing = fringe_spacing(wavelength, L, d)
    y = np.linspace(-3 * spacing, 3 * spacing, 40001)
    peaks = fringe_peaks(y, intensity(y, wavelength, L, w, d))

    assert len(peaks) >= 5
    assert np.allclose(np.diff(peaks), spacing, rtol=1e-3)


def test_central_maximum_is_unity():
    value = intensity(np.array([0.0]), 500e-9, 1.0, 2e-6, 1e-4)

    assert value[0] == pytest.approx(1.0)


def test_envelope_suppresses_fringes_past_first_zero():
    wavelength, L, w, d = 500e-9, 1.0, 2e-6, 1e-4
    zero = envelope_zero_spacing(wavelength, L, w)
    y = np.array([zero])

    assert intensity(y, wavelength, L, w, d)[0] == pytest.approx(0.0, abs=1e-12)


def test_narrow_slit_visibility_is_one():
    wavelength, L, d = 500e-9, 1.0, 1e-4
    spacing = fringe_spacing(wavelength, L, d)
    y = np.linspace(-spacing, spacing, 20001)  # one full fringe period, so both maxima and minima are in the window
    pattern = intensity(y, wavelength, L, 1e-9, d)

    assert visibility(pattern) == pytest.approx(1.0, abs=1e-3)


def test_finite_width_pulls_outer_fringes_inward():
    result = simulate_scenario()

    assert result["measured_fringe_spacing"] < result["analytic_fringe_spacing"]
    assert result["measured_fringe_spacing"] == pytest.approx(result["analytic_fringe_spacing"], rel=0.03)
    assert result["central_fringes"] >= 3
