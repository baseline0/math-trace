"""Unit tests: Thermodynamics model validation.

Happy path tests for ideal gas law, internal energy, and Carnot cycles.
"""

import importlib.util
from pathlib import Path

import pytest

# Load thermodynamics model module
thermo_model_path = Path(__file__).parent.parent.parent / "templates" / "thermodynamics" / "src" / "model.py"
spec = importlib.util.spec_from_file_location("thermo_model", thermo_model_path)
thermo_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thermo_model)

carnot_efficiency = thermo_model.carnot_efficiency
ideal_gas_pressure = thermo_model.ideal_gas_pressure
ideal_gas_temperature = thermo_model.ideal_gas_temperature
ideal_gas_volume = thermo_model.ideal_gas_volume
internal_energy = thermo_model.internal_energy


class TestIdealGasLaw:
    """Validate ideal gas law: PV = nRT"""

    def test_ideal_gas_pressure_happy_path(self):
        """P = nRT/V for standard conditions."""
        n = 1.0
        V = 1.0
        T = 273.15
        R = 8.314

        P = ideal_gas_pressure(n, V, T, R)

        assert P > 2000 and P < 2500

    def test_ideal_gas_volume_happy_path(self):
        """V = nRT/P"""
        n = 1.0
        P = 101325
        T = 273.15
        R = 8.314

        V = ideal_gas_volume(n, P, T, R)

        assert V > 0.022 and V < 0.023

    def test_ideal_gas_temperature_happy_path(self):
        """T = PV/(nR)"""
        n = 1.0
        P = 101325
        V = 0.0224
        R = 8.314

        T = ideal_gas_temperature(n, P, V, R)

        assert T > 270 and T < 280

    def test_ideal_gas_consistency(self):
        """P, V, T should satisfy PV=nRT consistently."""
        n = 2.0
        P = 50000
        T = 300
        R = 8.314

        V = ideal_gas_volume(n, P, T, R)
        P_check = ideal_gas_pressure(n, V, T, R)

        assert abs(P_check - P) / P < 1e-10


class TestInternalEnergy:
    """Validate internal energy: U = n·C_v·T"""

    def test_internal_energy_monatomic_gas(self):
        """U = n·(3/2)R·T for monatomic gas."""
        n = 1.0
        T = 300
        C_v = 1.5 * 8.314

        U = internal_energy(n, T, C_v)

        assert U > 0

    def test_internal_energy_diatomic_gas(self):
        """U = n·(5/2)R·T for diatomic gas."""
        n = 1.0
        T = 300
        C_v = 2.5 * 8.314

        U = internal_energy(n, T, C_v)

        C_v_mono = 1.5 * 8.314
        U_mono = internal_energy(n, T, C_v_mono)

        assert U_mono < U

    def test_internal_energy_linear_in_temperature(self):
        """U ∝ T (linear relationship)."""
        n = 1.0
        C_v = 2.5 * 8.314

        U_300 = internal_energy(n, 300, C_v)
        U_600 = internal_energy(n, 600, C_v)

        assert abs(U_600 - 2 * U_300) / U_300 < 1e-10


class TestCarnotCycle:
    """Validate Carnot efficiency."""

    def test_carnot_efficiency_happy_path(self):
        """η = 1 - T_cold/T_hot"""
        T_hot = 373
        T_cold = 273

        eta = carnot_efficiency(T_hot, T_cold)

        assert 0.25 < eta < 0.30

    def test_carnot_efficiency_requires_temperature_difference(self):
        """Function requires T_hot > T_cold (raises error otherwise)."""
        T_hot = 300
        T_cold = 300

        with pytest.raises(ValueError):
            carnot_efficiency(T_hot, T_cold)

    def test_carnot_efficiency_increases_with_temperature_ratio(self):
        """Higher ΔT → higher efficiency."""
        T_cold = 273

        eta_small_delta = carnot_efficiency(300, T_cold)
        eta_large_delta = carnot_efficiency(373, T_cold)

        assert eta_large_delta > eta_small_delta

    def test_carnot_efficiency_bounded(self):
        """Carnot efficiency must be < 1."""
        T_hot = 500
        T_cold = 100

        eta = carnot_efficiency(T_hot, T_cold)

        assert 0 <= eta < 1
