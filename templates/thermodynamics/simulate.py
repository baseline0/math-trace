"""Thermodynamics simulations: ideal gas and carnot cycles."""

import numpy as np

from src.model import (
    carnot_efficiency,
    ideal_gas_pressure,
    ideal_gas_volume,
)


def isothermal_process(T: float = 300, P_init: float = 101325, V_init: float = 1.0, n: float = 1.0):
    """Isothermal (constant T) expansion."""
    V = np.linspace(V_init, 2 * V_init, 50)
    P = ideal_gas_pressure(n, V, T)
    return V, P


def isobaric_process(P: float = 101325, T_init: float = 300, V_init: float = 1.0, n: float = 1.0):
    """Isobaric (constant P) heating."""
    T = np.linspace(T_init, 2 * T_init, 50)
    V = ideal_gas_volume(n, P, T)
    return T, V


def carnot_engine_analysis(T_hot: float = 400, T_cold: float = 300, Q_hot: float = 1000):
    """Carnot engine efficiency and work output."""
    eta = carnot_efficiency(T_hot, T_cold)
    W = eta * Q_hot
    Q_cold = Q_hot - W
    return {"efficiency": eta, "work": W, "heat_rejected": Q_cold}
