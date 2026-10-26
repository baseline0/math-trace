"""
Scenario: State Diagrams for an Ideal Gas (Intermediate)

P-V isotherms, T-S curves, and P-T isochores for a fixed amount of ideal gas, plus a numerical check of
two Maxwell relations derived from the entropy and the equation of state.

Scope: an ideal gas has no phase transition, so there is no coexistence curve or critical point here.
The diagrams show the state-space geometry only.
"""

import numpy as np

from ..model import entropy, ideal_gas_pressure

R = 8.314  # J/(mol·K)


def isotherm_pressure(V: np.ndarray, n: float, T: float) -> np.ndarray:
    """P-V isotherm: P = n·R·T / V."""
    return n * R * T / V


def isochore_pressure(T: np.ndarray, n: float, V: float) -> np.ndarray:
    """P-T isochore: P = n·R·T / V, a straight line through the origin."""
    return n * R * T / V


def isobar_entropy(T: np.ndarray, n: float, C_p: float, S_0: float = 0.0, T_0: float = 1.0) -> np.ndarray:
    """T-S isobar: S = n·C_p·ln(T/T_0) + S_0, from dS = n·C_p·dT/T at fixed pressure."""
    return n * C_p * np.log(T / T_0) + S_0


def isochore_entropy(T: np.ndarray, n: float, C_v: float, S_0: float = 0.0, T_0: float = 1.0) -> np.ndarray:
    """T-S isochore: S = n·C_v·ln(T/T_0) + S_0, from dS = n·C_v·dT/T at fixed volume."""
    return n * C_v * np.log(T / T_0) + S_0


def maxwell_check(n: float, T: float, V: float, C_v: float, P: float, h: float = 1e-4) -> dict:
    """
    Check two Maxwell relations by central differences against their closed forms for an ideal gas.

    (∂S/∂V)_T = (∂P/∂T)_V = n·R/V, and (∂S/∂P)_T = -(∂V/∂T)_P = -n·R/P.

    Returns:
        The finite-difference and closed-form values for each relation.
    """
    dS_dV = (entropy(n, T, V + h * V, C_v) - entropy(n, T, V - h * V, C_v)) / (2 * h * V)
    dP_dT = (ideal_gas_pressure(n, V, T + h * T) - ideal_gas_pressure(n, V, T - h * T)) / (2 * h * T)

    dS_dP_at_const_T = (_entropy_at_pressure(n, T, P * (1 + h), C_v) - _entropy_at_pressure(n, T, P * (1 - h), C_v)) / (
        2 * h * P
    )
    dV_dT_at_const_P = ((n * R * (T + h * T) / P) - (n * R * (T - h * T) / P)) / (2 * h * T)

    return {
        "dS_dV_T": float(dS_dV),
        "dP_dT_V": float(dP_dT),
        "closed_form": float(n * R / V),
        "dS_dP_T": float(dS_dP_at_const_T),
        "minus_dV_dT_P": float(-dV_dT_at_const_P),
        "closed_form_pressure": float(-n * R / P),
    }


def _entropy_at_pressure(n: float, T: float, P: float, C_v: float) -> float:
    """Entropy of the ideal gas at (T, P), with V = n·R·T/P substituted into S(T, V)."""
    V = n * R * T / P
    return float(entropy(n, T, V, C_v))


if __name__ == "__main__":
    n = 1.0
    C_v = 2.5 * R

    print("=" * 70)
    print("State Diagrams: 1 mol ideal gas (no phase transition)")
    print("=" * 70)

    V = np.linspace(0.01, 0.05, 5)
    print("\nP-V isotherm at 300 K (Pa):")
    for v, p in zip(V, isotherm_pressure(V, n, 300.0)):
        print(f"  V = {v:.3f} m³  P = {p:,.0f} Pa")

    checks = maxwell_check(n, T=300.0, V=0.0249, C_v=C_v, P=1.0e5)
    print("\nMaxwell relations (finite difference vs closed form):")
    print(
        f"  (∂S/∂V)_T = {checks['dS_dV_T']:.4f}   (∂P/∂T)_V = {checks['dP_dT_V']:.4f}   nR/V = {checks['closed_form']:.4f}"
    )
    print(
        f"  (∂S/∂P)_T = {checks['dS_dP_T']:.4e}   -(∂V/∂T)_P = {checks['minus_dV_dT_P']:.4e}   -nR/P = {checks['closed_form_pressure']:.4e}"
    )

    print("\n✅ State diagram scenario complete")
