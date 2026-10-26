"""
State diagram contract tests.

Checks the isotherm and isochore forms, the entropy curves, and the two Maxwell relations
computed by finite differences against their closed forms.
"""

import numpy as np
import pytest

from ..scenarios.phase_diagrams import (
    R,
    isobar_entropy,
    isochore_entropy,
    isochore_pressure,
    isotherm_pressure,
    maxwell_check,
)


def test_isotherm_is_inverse_in_volume():
    V = np.array([1.0, 2.0, 4.0])
    P = isotherm_pressure(V, 1.0, 300.0)
    assert np.allclose(P * V, 1.0 * R * 300.0)


def test_isochore_is_linear_through_origin():
    T = np.array([100.0, 200.0, 300.0])
    P = isochore_pressure(T, 1.0, 0.02)
    assert np.allclose(P / T, P[0] / T[0])


def test_isobar_has_larger_slope_than_isochore_in_ln_t():
    """dS/d(ln T) is n·C_p on the isobar and n·C_v on the isochore, so the isobar is steeper."""
    T = np.array([300.0, 600.0])
    C_v = 2.5 * R
    C_p = 3.5 * R
    isobar = isobar_entropy(T, 1.0, C_p)
    isochore = isochore_entropy(T, 1.0, C_v)

    assert (isobar[1] - isobar[0]) > (isochore[1] - isochore[0])
    assert isobar[1] - isobar[0] == pytest.approx(C_p * np.log(2.0))


@pytest.fixture(scope="module")
def maxwell():
    return maxwell_check(n=1.0, T=300.0, V=0.0249, C_v=2.5 * R, P=1.0e5)


def test_maxwell_relation_s_v_equals_p_t(maxwell):
    assert maxwell["dS_dV_T"] == pytest.approx(maxwell["dP_dT_V"], rel=1e-6)


def test_maxwell_relation_matches_closed_form(maxwell):
    assert maxwell["dP_dT_V"] == pytest.approx(maxwell["closed_form"], rel=1e-6)


def test_maxwell_relation_s_p_matches_closed_form(maxwell):
    assert maxwell["dS_dP_T"] == pytest.approx(maxwell["minus_dV_dT_P"], rel=1e-6)
    assert maxwell["minus_dV_dT_P"] == pytest.approx(maxwell["closed_form_pressure"], rel=1e-6)
