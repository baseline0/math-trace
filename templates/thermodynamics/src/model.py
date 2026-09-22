"""
Thermodynamics: Ideal Gas & Carnot Cycle

Fundamental thermodynamic equations and cycle analysis.

References:
- Callen, H. B. (1985). Thermodynamics and an Introduction to Thermostatistics.
- Kittel & Kroemer (1980). Thermal Physics.
"""

import numpy as np
import json
from typing import Dict, Any, Tuple


# ============================================================================
# Equation 1: Ideal Gas Law
# ============================================================================
# PV = nRT  (or: PV = NkT for N particles, k = Boltzmann constant)
#
# Code Reference: ideal_gas_pressure(), ideal_gas_volume()

def ideal_gas_pressure(n: float, V: float, T: float, R: float = 8.314) -> float:
    """
    Ideal gas pressure.

    P = (nRT) / V

    Args:
        n: Number of moles
        V: Volume (m³)
        T: Temperature (K)
        R: Gas constant (8.314 J/(mol·K))

    Returns:
        Pressure (Pa)
    """
    return (n * R * T) / V


def ideal_gas_volume(n: float, P: float, T: float, R: float = 8.314) -> float:
    """V = nRT/P"""
    return (n * R * T) / P


def ideal_gas_temperature(n: float, P: float, V: float, R: float = 8.314) -> float:
    """T = PV/(nR)"""
    return (P * V) / (n * R)


# ============================================================================
# Equation 2: Internal Energy (Ideal Gas)
# ============================================================================
# U = n·C_v·T  (for ideal gas, depends only on T)
# C_v = (f/2)·R where f = degrees of freedom
#
# Code Reference: internal_energy()

def internal_energy(n: float, T: float, C_v: float) -> float:
    """
    Internal energy of ideal gas.

    U = n·C_v·T

    Args:
        n: Number of moles
        T: Temperature (K)
        C_v: Heat capacity at constant volume (J/(mol·K))

    Returns:
        Internal energy (J)

    Note:
        Monatomic: C_v = (3/2)R
        Diatomic: C_v = (5/2)R
        Polyatomic: C_v ≈ 3R
    """
    return n * C_v * T


# ============================================================================
# Equation 3: First Law of Thermodynamics
# ============================================================================
# dU = δQ - δW  (or: dU = δQ - P·dV)
#
# Code Reference: first_law()

def first_law(dQ: float, dW: float) -> float:
    """
    First Law: Change in internal energy.

    dU = δQ - δW

    Where:
    - δQ: Heat added to system (J)
    - δW: Work done by system (J)
    - dU: Change in internal energy (J)

    Args:
        dQ: Heat added (positive if into system)
        dW: Work done by system (positive if system expands)

    Returns:
        Change in internal energy dU
    """
    return dQ - dW


def work_done_isobaric(P: float, dV: float) -> float:
    """Work in constant-pressure process: W = P·ΔV"""
    return P * dV


# ============================================================================
# Equation 4: Entropy (Ideal Gas)
# ============================================================================
# S = n·C_v·ln(T) + n·R·ln(V) + S_0
#
# Code Reference: entropy()

def entropy(n: float, T: float, V: float, C_v: float, R: float = 8.314, S_0: float = 0.0) -> float:
    """
    Entropy of ideal gas.

    S = n·C_v·ln(T) + n·R·ln(V) + S_0

    Args:
        n: Number of moles
        T: Temperature (K)
        V: Volume (m³)
        C_v: Heat capacity at constant volume
        R: Gas constant
        S_0: Reference entropy

    Returns:
        Entropy (J/K)

    Physical interpretation:
    - ∝ ln(T): More disorder at higher temperature
    - ∝ ln(V): More disorder with larger volume
    """
    return n * C_v * np.log(T) + n * R * np.log(V) + S_0


# ============================================================================
# Equation 5: Carnot Efficiency
# ============================================================================
# η_Carnot = 1 - (T_cold / T_hot)
#
# Code Reference: carnot_efficiency()

def carnot_efficiency(T_hot: float, T_cold: float) -> float:
    """
    Maximum possible efficiency for heat engine.

    η = 1 - (T_c / T_h)

    Args:
        T_hot: Hot reservoir temperature (K)
        T_cold: Cold reservoir temperature (K)

    Returns:
        Carnot efficiency (0 to 1)

    Properties:
    - η = 0 if T_c = T_h (no temperature difference, no work)
    - η → 1 if T_c → 0 (infinite efficiency at absolute zero)
    - Real engines: η < η_Carnot (irreversible)
    """
    if T_hot <= T_cold:
        raise ValueError("Hot temperature must exceed cold temperature")

    return 1 - (T_cold / T_hot)


def carnot_cycle_work(Q_hot: float, T_hot: float, T_cold: float) -> float:
    """
    Work extracted by Carnot engine.

    W = Q_h·(1 - T_c/T_h)

    Args:
        Q_hot: Heat absorbed from hot reservoir (J)
        T_hot: Hot reservoir temperature (K)
        T_cold: Cold reservoir temperature (K)

    Returns:
        Work done by engine (J)
    """
    eta = carnot_efficiency(T_hot, T_cold)
    return Q_hot * eta


def carnot_cycle_cold_heat(Q_hot: float, T_hot: float, T_cold: float) -> float:
    """
    Heat rejected to cold reservoir.

    Q_c = Q_h - W = Q_h·(T_c / T_h)
    """
    W = carnot_cycle_work(Q_hot, T_hot, T_cold)
    return Q_hot - W


# ============================================================================
# Observable: Heat Capacity
# ============================================================================

def heat_capacity_constant_volume(n: float, f: int = 5) -> float:
    """
    Heat capacity at constant volume.

    C_v = (f/2)·nR

    Args:
        n: Number of moles
        f: Degrees of freedom (3 for monatomic, 5 for diatomic, 6+ for polyatomic)

    Returns:
        C_v (J/K)
    """
    R = 8.314
    return (f / 2) * n * R


def heat_capacity_constant_pressure(n: float, f: int = 5) -> float:
    """
    Heat capacity at constant pressure.

    C_p = C_v + nR = ((f+2)/2)·nR
    """
    R = 8.314
    return ((f + 2) / 2) * n * R


def export_equation_metadata() -> Dict[str, Any]:
    """Auto-generate equations.json for paper.typ."""
    return {
        "ideal_gas_law": {
            "latex": r"PV = nRT",
            "code_ref": "model.py:ideal_gas_pressure()",
            "line": 32,
            "description": "State equation for ideal gas; relates P, V, T, n",
        },
        "internal_energy": {
            "latex": r"U = n C_v T",
            "code_ref": "model.py:internal_energy()",
            "line": 71,
            "description": "Internal energy (kinetic energy of molecules)",
        },
        "first_law": {
            "latex": r"dU = \delta Q - \delta W",
            "code_ref": "model.py:first_law()",
            "line": 108,
            "description": "Energy conservation: heat in - work out = energy change",
        },
        "entropy": {
            "latex": r"S = n C_v \ln(T) + n R \ln(V) + S_0",
            "code_ref": "model.py:entropy()",
            "line": 154,
            "description": "Entropy: measure of disorder; ∝ ln(T) and ln(V)",
        },
        "carnot_efficiency": {
            "latex": r"\eta_{\text{Carnot}} = 1 - \frac{T_c}{T_h}",
            "code_ref": "model.py:carnot_efficiency()",
            "line": 189,
            "validation": "η = 0 at T_c = T_h; η < 1 always (2nd Law)",
        },
    }


if __name__ == "__main__":
    metadata = export_equation_metadata()
    with open("equations.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Exported equations.json")
