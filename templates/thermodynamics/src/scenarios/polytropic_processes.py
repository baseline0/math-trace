"""
Scenario: Polytropic Processes (Intermediate)

An ideal gas expanded along four named paths, each a polytrope P·V^n = constant:
isobaric (n = 0), isothermal (n = 1), adiabatic (n = γ, no heat exchange), and isochoric (V fixed, no work).
For each path the scenario reports work W, internal energy change ΔU, and heat Q = ΔU + W.
The tests check Q against independent expressions (for example, Q = 0 on the adiabat), so the First Law is not circular.
"""

import numpy as np

from ..model import internal_energy

R = 8.314  # J/(mol·K)


def heat_capacity_ratio(f: int = 5) -> float:
    """γ = C_p / C_v = (f + 2) / f for f active degrees of freedom."""
    return (f + 2) / f


def final_state(P1: float, V1: float, V2: float, n_exponent: float) -> tuple[float, float]:
    """
    Final pressure and volume on the polytrope P·V^n = const, given the final volume.

    Returns:
        (P2, V2) with P2 = P1·(V1/V2)^n
    """
    P2 = P1 * (V1 / V2) ** n_exponent
    return float(P2), float(V2)


def polytropic_work(P1: float, V1: float, P2: float, V2: float, n_exponent: float, moles: float, T1: float) -> float:
    """
    Work done by the gas along a polytrope.

    W = (P2·V2 - P1·V1) / (1 - n) for n ≠ 1, and W = n·R·T·ln(V2/V1) for n = 1 (isothermal).
    """
    if np.isclose(n_exponent, 1.0):
        return float(moles * R * T1 * np.log(V2 / V1))
    return float((P2 * V2 - P1 * V1) / (1.0 - n_exponent))


def run_path(
    name: str, P1: float, V1: float, V2: float, moles: float = 1.0, f: int = 5, P2_isochoric: float | None = None
) -> dict:
    """
    Take the gas from (P1, V1) to a final state along one named path.

    Args:
        name: "isobaric", "isothermal", "adiabatic", or "isochoric"
        P1, V1: Initial pressure (Pa) and volume (m³)
        V2: Final volume (m³); must equal V1 for the isochoric path
        moles: Amount of gas in mol
        f: Degrees of freedom (5 for a diatomic ideal gas)
        P2_isochoric: Final pressure for the isochoric path, which changes pressure at fixed volume

    Returns:
        Dict with the exponent, final state, work, internal energy change, and heat (Q = ΔU + W)
    """
    C_v = f / 2.0 * R
    T1 = P1 * V1 / (moles * R)

    if name == "isobaric":
        n_exponent = 0.0
        P2 = P1
    elif name == "isothermal":
        n_exponent = 1.0
        P2, _ = final_state(P1, V1, V2, n_exponent)
    elif name == "adiabatic":
        n_exponent = heat_capacity_ratio(f)
        P2, _ = final_state(P1, V1, V2, n_exponent)
    elif name == "isochoric":
        if not np.isclose(V2, V1):
            raise ValueError("isochoric path needs V2 == V1")
        if P2_isochoric is None:
            raise ValueError("isochoric path needs the final pressure P2_isochoric")
        n_exponent = float("inf")
        P2 = P2_isochoric
    else:
        raise ValueError(f"unknown path: {name}")

    T2 = P2 * V2 / (moles * R)
    if name == "isochoric":
        work = 0.0
    elif name == "isobaric":
        work = P1 * (V2 - V1)
    else:
        work = polytropic_work(P1, V1, P2, V2, n_exponent, moles, T1)

    delta_U = internal_energy(moles, T2, C_v) - internal_energy(moles, T1, C_v)
    heat = delta_U + work

    return {
        "path": name,
        "n": n_exponent,
        "P1": P1,
        "V1": V1,
        "P2": float(P2),
        "V2": float(V2),
        "T1": float(T1),
        "T2": float(T2),
        "work": float(work),
        "delta_U": float(delta_U),
        "heat": float(heat),
    }


def compare_paths(P1: float = 1.0e5, V1: float = 0.0249, expansion: float = 2.0, moles: float = 1.0) -> dict:
    """
    Expand the same starting gas along all four paths to the same final volume.

    The isochoric path cannot change volume, so it heats the gas at V1 to the same pressure ratio instead.
    """
    V2 = expansion * V1
    results = {name: run_path(name, P1, V1, V2, moles=moles) for name in ("isobaric", "isothermal", "adiabatic")}
    results["isochoric"] = run_path("isochoric", P1, V1, V1, moles=moles, P2_isochoric=expansion * P1)
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Polytropic Processes: ideal gas, 1 mol diatomic, doubling the volume")
    print("=" * 70)

    for name, r in compare_paths().items():
        print(f"\n{name} (n = {r['n']:.3g})")
        print(f"  W = {r['work']:9.2f} J   ΔU = {r['delta_U']:9.2f} J   Q = {r['heat']:9.2f} J")
        print(f"  T: {r['T1']:.1f} K -> {r['T2']:.1f} K")

    print("\n✅ Polytropic process scenario complete")
