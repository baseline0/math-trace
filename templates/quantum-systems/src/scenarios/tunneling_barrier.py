"""
Scenario: Quantum Tunneling Through a Rectangular Barrier (Intermediate)

A particle of energy E meets a barrier of height V0 and width a. Units: ħ = m = 1.
For E < V0 the wavefunction decays inside the barrier, yet a finite fraction tunnels through.

Two independent routes give the transmission probability T:
  1. The closed form T = 1 / (1 + V0²·sinh²(κa) / (4E(V0 - E))) with κ = √(2(V0 - E)),
  2. Plane-wave matching at both barrier edges, solved as a 4×4 linear system.
They agree to machine precision, and the WKB estimate T ≈ exp(-2κa) approaches them for thick barriers.
"""

import numpy as np


def transmission_closed_form(E: float, V0: float, a: float) -> float:
    """
    Transmission probability for a rectangular barrier, closed form.

    Valid for E < V0 (tunneling) and E > V0 (over-barrier, with sin² in place of sinh²).
    """
    if E < V0:
        kappa = np.sqrt(2.0 * (V0 - E))
        return float(1.0 / (1.0 + V0**2 * np.sinh(kappa * a) ** 2 / (4.0 * E * (V0 - E))))
    k2 = np.sqrt(2.0 * (E - V0))
    return float(1.0 / (1.0 + V0**2 * np.sin(k2 * a) ** 2 / (4.0 * E * (E - V0))))


def transmission_matching(E: float, V0: float, a: float) -> tuple[float, float]:
    """
    Transmission and reflection from plane-wave matching at x = 0 and x = a.

    Incident wave from the left with amplitude 1, no wave returning from the right.
    Unknowns (r, C, D, t) solve four continuity conditions for ψ and ψ' at the two edges.

    Returns:
        (T, R) with T = |t|² and R = |r|²
    """
    k = np.sqrt(2.0 * E + 0j)
    q = np.sqrt(2.0 * (V0 - E) + 0j)
    e_plus = np.exp(q * a)
    e_minus = np.exp(-q * a)
    e_ka = np.exp(1j * k * a)

    M = np.array(
        [
            [1.0, -1.0, -1.0, 0.0],  # ψ continuous at x = 0:  r - C - D = -1
            [-1j * k, -q, q, 0.0],  # ψ' continuous at x = 0: -ik·r - qC + qD = -ik
            [0.0, e_plus, e_minus, -e_ka],  # ψ continuous at x = a
            [0.0, q * e_plus, -q * e_minus, -1j * k * e_ka],  # ψ' continuous at x = a
        ],
        dtype=complex,
    )
    b = np.array([-1.0, -1j * k, 0.0, 0.0], dtype=complex)
    r, _C, _D, t = np.linalg.solve(M, b)

    return float(np.abs(t) ** 2), float(np.abs(r) ** 2)


def wkb_transmission(E: float, V0: float, a: float) -> float:
    """WKB estimate T ≈ exp(-2κa) for E < V0; the thick-barrier limit of the closed form."""
    if E >= V0:
        raise ValueError("the WKB tunneling estimate applies only for E < V0")
    kappa = np.sqrt(2.0 * (V0 - E))
    return float(np.exp(-2.0 * kappa * a))


def scan_widths(E: float, V0: float, widths: np.ndarray) -> dict:
    """
    Transmission against barrier width for the closed form and the matching solve, plus WKB when E < V0.
    """
    closed = np.array([transmission_closed_form(E, V0, a) for a in widths])
    matched = np.array([transmission_matching(E, V0, a)[0] for a in widths])
    result = {"widths": widths, "closed_form": closed, "matching": matched}
    if E < V0:
        result["wkb"] = np.array([wkb_transmission(E, V0, a) for a in widths])
    return result


def simulate_scenario(E: float = 1.0, V0: float = 2.0, a: float = 1.0) -> dict:
    """Single-barrier summary: closed form, matching solve, flux conservation, and the WKB comparison."""
    T_closed = transmission_closed_form(E, V0, a)
    T_match, R_match = transmission_matching(E, V0, a)
    return {
        "E": E,
        "V0": V0,
        "a": a,
        "kappa": float(np.sqrt(2.0 * (V0 - E))),
        "T_closed_form": T_closed,
        "T_matching": T_match,
        "R_matching": R_match,
        "flux_residual": T_match + R_match - 1.0,
        "T_wkb": wkb_transmission(E, V0, a),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Quantum Tunneling: rectangular barrier (ħ = m = 1)")
    print("=" * 70)

    result = simulate_scenario()
    print(f"\nE = {result['E']}, V0 = {result['V0']}, a = {result['a']}, κ = {result['kappa']:.4f}")
    print(f"  T (closed form) = {result['T_closed_form']:.6f}")
    print(f"  T (matching)    = {result['T_matching']:.6f}")
    print(f"  R (matching)    = {result['R_matching']:.6f}")
    print(f"  flux residual   = {result['flux_residual']:.2e}")
    print(f"  T (WKB)         = {result['T_wkb']:.4e}")

    print("\n✅ Tunneling scenario complete")
