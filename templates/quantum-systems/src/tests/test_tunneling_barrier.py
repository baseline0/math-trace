"""
Rectangular barrier tunneling contract tests.

Checks the closed-form transmission against the independent plane-wave matching solve, flux conservation
T + R = 1, the over-barrier limit, and the thick-barrier WKB limit.
"""

import numpy as np
import pytest

from ..scenarios.tunneling_barrier import (
    scan_widths,
    simulate_scenario,
    transmission_closed_form,
    transmission_matching,
    wkb_transmission,
)

CASES = [(1.0, 2.0, 1.0), (0.5, 4.0, 2.0), (0.3, 1.0, 0.5)]  # all E < V0


@pytest.mark.parametrize(("E", "V0", "a"), CASES)
def test_closed_form_matches_matching_solve(E, V0, a):
    assert transmission_matching(E, V0, a)[0] == pytest.approx(transmission_closed_form(E, V0, a), rel=1e-9)


@pytest.mark.parametrize(("E", "V0", "a"), [*CASES, (3.0, 2.0, 0.7)])
def test_flux_is_conserved(E, V0, a):
    T, R = transmission_matching(E, V0, a)
    assert pytest.approx(1.0, abs=1e-10) == T + R


def test_over_barrier_transmission_is_below_one_and_oscillates():
    values = [transmission_closed_form(3.0, 2.0, a) for a in np.linspace(0.1, 2.0, 50)]
    assert max(values) <= 1.0 + 1e-12
    assert min(values) < 0.99  # resonances dip below one, unlike a barrier-free wave


def test_thick_barrier_approaches_wkb():
    E, V0 = 0.5, 4.0
    a = 6.0
    exact = transmission_closed_form(E, V0, a)
    wkb = wkb_transmission(E, V0, a)

    assert exact == pytest.approx(wkb, rel=0.02)


def test_wkb_rejects_energy_above_barrier():
    with pytest.raises(ValueError, match="E < V0"):
        wkb_transmission(3.0, 2.0, 1.0)


def test_transmission_decreases_with_width():
    widths = np.linspace(0.2, 3.0, 30)
    result = scan_widths(E=1.0, V0=2.0, widths=widths)

    assert np.all(np.diff(result["closed_form"]) < 0)
    assert np.allclose(result["closed_form"], result["matching"], rtol=1e-9)


def test_scenario_reports_flux_residual_near_zero():
    result = simulate_scenario()

    assert abs(result["flux_residual"]) < 1e-12
    assert result["T_closed_form"] == pytest.approx(result["T_matching"], rel=1e-9)
