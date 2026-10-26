"""
Polytropic process contract tests.

Heat is computed as Q = ΔU + W, so the First Law holds by construction. The tests check Q against
independent expressions: Q = 0 on the adiabat, Q = W on the isotherm, Q = nC_p·ΔT on the isobar,
and Q = nC_v·ΔT on the isochore. They also check the work formulas and the exponent of each path.
"""

import numpy as np
import pytest

from ..scenarios.polytropic_processes import R, compare_paths, heat_capacity_ratio, run_path

P1 = 1.0e5
V1 = 0.0249
MOLES = 1.0
F = 5


@pytest.fixture(scope="module")
def paths():
    return compare_paths(P1=P1, V1=V1, expansion=2.0, moles=MOLES)


def test_heat_capacity_ratio_for_diatomic_gas():
    assert heat_capacity_ratio(5) == pytest.approx(1.4)


def test_isobaric_work_is_p_delta_v(paths):
    assert paths["isobaric"]["work"] == pytest.approx(P1 * V1)


def test_isothermal_work_is_nrt_ln_ratio(paths):
    T1 = P1 * V1 / (MOLES * R)
    assert paths["isothermal"]["work"] == pytest.approx(MOLES * R * T1 * np.log(2.0))


def test_isothermal_temperature_is_unchanged(paths):
    assert paths["isothermal"]["T2"] == pytest.approx(paths["isothermal"]["T1"])
    assert paths["isothermal"]["delta_U"] == pytest.approx(0.0, abs=1e-9)


def test_adiabatic_heat_is_zero(paths):
    assert paths["adiabatic"]["heat"] == pytest.approx(0.0, abs=1e-6)


def test_adiabatic_obeys_pv_gamma(paths):
    r = paths["adiabatic"]
    gamma = heat_capacity_ratio(F)
    assert r["P2"] * r["V2"] ** gamma == pytest.approx(r["P1"] * r["V1"] ** gamma)


def test_isobaric_heat_is_n_cp_delta_t(paths):
    r = paths["isobaric"]
    C_p = (F + 2) / 2 * R
    assert r["heat"] == pytest.approx(MOLES * C_p * (r["T2"] - r["T1"]))


def test_isochoric_work_is_zero_and_heat_is_n_cv_delta_t(paths):
    r = paths["isochoric"]
    C_v = F / 2 * R
    assert r["work"] == 0.0
    assert r["heat"] == pytest.approx(MOLES * C_v * (r["T2"] - r["T1"]))


def test_isochoric_requires_final_pressure():
    with pytest.raises(ValueError, match="P2_isochoric"):
        run_path("isochoric", P1, V1, V1)


def test_isochoric_requires_equal_volumes():
    with pytest.raises(ValueError, match="V2 == V1"):
        run_path("isochoric", P1, V1, 2 * V1, P2_isochoric=2 * P1)


def test_unknown_path_raises():
    with pytest.raises(ValueError, match="unknown path"):
        run_path("isentropic-ish", P1, V1, 2 * V1)
