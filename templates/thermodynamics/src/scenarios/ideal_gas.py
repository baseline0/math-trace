"""
Scenario: Ideal Gas Properties (Beginner)

Explore PVT relations and thermodynamic properties.
"""

import numpy as np
from typing import Dict
from ..model import (
    ideal_gas_pressure, ideal_gas_temperature,
    internal_energy, entropy, carnot_efficiency,
    heat_capacity_constant_volume, heat_capacity_constant_pressure
)


def explore_ideal_gas_properties() -> Dict:
    """
    Simulate ideal gas behavior at various conditions.

    Returns:
        Dictionary with PVT relations and thermodynamic properties
    """
    n = 1.0  # 1 mole
    R = 8.314  # Gas constant

    # Temperature range
    T_range = np.array([200, 300, 400, 500])  # K
    V = 0.024  # m³ (approximately 24 liters, STP)

    results = {
        "T": T_range,
        "P": [],
        "U": [],
        "S": [],
    }

    C_v = (5 / 2) * R  # Diatomic gas (air)

    for T in T_range:
        P = ideal_gas_pressure(n, V, T, R)
        U = internal_energy(n, T, C_v)
        S = entropy(n, T, V, C_v, R)

        results["P"].append(P)
        results["U"].append(U)
        results["S"].append(S)

    results["P"] = np.array(results["P"])
    results["U"] = np.array(results["U"])
    results["S"] = np.array(results["S"])

    return results


def explore_carnot_cycle(T_hot: float = 300, T_cold: float = 100) -> Dict:
    """
    Analyze Carnot cycle efficiency.

    Args:
        T_hot: Hot reservoir temperature (K)
        T_cold: Cold reservoir temperature (K)

    Returns:
        Dictionary with cycle analysis
    """
    eta = carnot_efficiency(T_hot, T_cold)

    # For 1000 J of heat input
    Q_hot = 1000.0
    W = Q_hot * eta
    Q_cold = Q_hot - W

    return {
        "T_hot": T_hot,
        "T_cold": T_cold,
        "efficiency": eta,
        "Q_hot": Q_hot,
        "W": W,
        "Q_cold": Q_cold,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Ideal Gas Properties")
    print("=" * 70)

    gas = explore_ideal_gas_properties()

    print("\nPVT Relations (1 mole, V = 0.024 m³):")
    print("  T(K)   P(Pa)      U(J)       S(J/K)")
    for i in range(len(gas["T"])):
        print(f"  {gas['T'][i]:3.0f}    {gas['P'][i]:8.0f}   {gas['U'][i]:8.1f}   {gas['S'][i]:8.2f}")

    print("\n" + "=" * 70)
    print("Carnot Cycle Analysis")
    print("=" * 70)

    carnot = explore_carnot_cycle(T_hot=300, T_cold=100)

    print(f"\nTemperatures: T_hot = {carnot['T_hot']} K, T_cold = {carnot['T_cold']} K")
    print(f"Carnot Efficiency: η = {carnot['efficiency']:.1%}")
    print(f"\nFor Q_h = {carnot['Q_hot']:.0f} J:")
    print(f"  Work extracted: W = {carnot['W']:.0f} J")
    print(f"  Heat rejected:  Q_c = {carnot['Q_cold']:.0f} J")
    print(f"  Check: Q_h = W + Q_c: {carnot['Q_hot']:.0f} = {carnot['W']:.0f} + {carnot['Q_cold']:.0f} ✓")

    print("\n✅ Thermodynamics scenario complete")
