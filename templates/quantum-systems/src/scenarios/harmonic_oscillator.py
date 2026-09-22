"""
Scenario 1: Quantum Harmonic Oscillator (Beginner)

The quantum harmonic oscillator is the simplest non-trivial quantum system
with an analytical solution. It demonstrates:
- Discrete energy levels: E_n = ℏω(n + 1/2)
- Wavefunction structure (Hermite polynomials)
- Energy conservation in time evolution
- Expectation values ⟨x⟩, ⟨p⟩, ⟨x²⟩

Analytical reference: Griffiths, Ch. 2.3
"""

import numpy as np
from typing import Tuple
from ..model import (
    solve_tise_fdm, propagate_ssfm, normalize_wavefunction,
    expectation_value, total_energy, probability_density,
    harmonic_potential, position_operator, momentum_operator,
    kinetic_energy_operator, potential_energy_operator,
)


def analytical_harmonic_eigenvalues(n_max: int, omega: float = 1.0, hbar: float = 1.0) -> np.ndarray:
    """
    Analytical eigenvalues: E_n = ℏω(n + 1/2)

    Args:
        n_max: Highest quantum number
        omega: Angular frequency
        hbar: Planck constant / 2π

    Returns:
        E: Eigenvalues [E_0, E_1, ..., E_n_max]
    """
    n = np.arange(n_max + 1)
    return hbar * omega * (n + 0.5)


def analytical_harmonic_period(omega: float = 1.0) -> float:
    """
    Classical turning point period for a Gaussian wavepacket
    in the ground state harmonic potential.

    Period T = 2π/ω

    The peak probability oscillates with this period.
    """
    return 2 * np.pi / omega


def compute_quantum_harmonic_oscillator(
    x_min: float = -5.0,
    x_max: float = 5.0,
    num_points: int = 256,
    omega: float = 1.0,
    num_eigenstates: int = 5,
    hbar: float = 1.0,
    mass: float = 1.0,
) -> dict:
    """
    Solve for harmonic oscillator eigenstates and energies.

    Returns:
        Dictionary with:
        - x: Position grid
        - energies: Eigenvalues (numerical)
        - energies_analytical: Eigenvalues (analytical)
        - eigenstates: Eigenfunctions ψ_n(x)
        - error: |E_numerical - E_analytical| / E_analytical
    """
    # Position grid
    x = np.linspace(x_min, x_max, num_points)

    # Potential: V(x) = ½ω² x² (with m=ℏ=1)
    V = lambda xg: harmonic_potential(xg, omega=omega)

    # Solve TISE
    energies, eigenstates = solve_tise_fdm(
        x, V, num_eigenstates=num_eigenstates, hbar=hbar, mass=mass
    )

    # Analytical energies
    energies_analytical = analytical_harmonic_eigenvalues(num_eigenstates - 1, omega=omega, hbar=hbar)

    # Relative error
    error = np.abs(energies - energies_analytical) / np.abs(energies_analytical)

    return {
        "x": x,
        "energies": energies,
        "energies_analytical": energies_analytical,
        "eigenstates": eigenstates,
        "error": error,
        "V": V(x),
    }


def evolve_ground_state_oscillator(
    x_min: float = -5.0,
    x_max: float = 5.0,
    num_points: int = 256,
    t_max: float = 10.0,
    dt: float = 0.01,
    omega: float = 1.0,
    hbar: float = 1.0,
    mass: float = 1.0,
) -> dict:
    """
    Time-evolve the ground state ψ_0 and monitor energy conservation.

    Returns:
        Dictionary with:
        - times: Time points
        - psi_t: Wavefunction at each time
        - energies: Total energy at each time (should be constant)
        - energy_error: |E(t) - E(0)| / E(0)
    """
    # Position grid
    x = np.linspace(x_min, x_max, num_points)
    dx = x[1] - x[0]

    # Potential
    V = lambda xg: harmonic_potential(xg, omega=omega)

    # Initial state: Ground state (Gaussian)
    # ψ_0(x) = (π^{-1/4}) exp(-x²/2) (with ℏ=m=ω=1)
    sigma = np.sqrt(hbar / (mass * omega))  # Ground state width
    psi_0 = np.pi**(-0.25) * np.exp(-x**2 / (2 * sigma**2))
    psi_0 = normalize_wavefunction(psi_0, x)

    # Propagate
    times, psi_t = propagate_ssfm(
        psi_0, x, t_max, dt, V, hbar=hbar, mass=mass
    )

    # Monitor energy
    energies = np.array([
        total_energy(psi_t[:, i], x, V, mass=mass)
        for i in range(psi_t.shape[1])
    ])

    energy_error = np.abs(energies - energies[0]) / np.abs(energies[0])

    return {
        "x": x,
        "times": times,
        "psi_t": psi_t,
        "energies": energies,
        "energy_error": energy_error,
        "V": V(x),
    }


def compute_expectation_values_harmonic(
    eigenstates: np.ndarray,
    x: np.ndarray,
    omega: float = 1.0,
    mass: float = 1.0,
) -> dict:
    """
    Compute expectation values ⟨x⟩, ⟨p⟩, ⟨x²⟩, ⟨p²⟩ for each eigenstate.

    For harmonic oscillator:
    - ⟨x⟩ = 0 (even/odd parity)
    - ⟨p⟩ = 0 (real wavefunctions)
    - ⟨x²⟩ = (2n+1)/(2mω)
    - ⟨p²⟩ = mω(2n+1)/2
    """
    V = lambda xg: harmonic_potential(xg, omega=omega)

    num_states = eigenstates.shape[1]
    results = {
        "expectation_x": [],
        "expectation_p": [],
        "expectation_x2": [],
        "expectation_p2": [],
    }

    for i in range(num_states):
        psi = eigenstates[:, i]

        # ⟨x⟩
        exp_x = expectation_value(psi, x, position_operator)
        results["expectation_x"].append(exp_x)

        # ⟨p⟩
        exp_p = expectation_value(psi, x, momentum_operator)
        results["expectation_p"].append(exp_p)

        # ⟨x²⟩
        exp_x2 = expectation_value(psi, x, lambda p, xg: x * position_operator(p, xg))
        results["expectation_x2"].append(exp_x2)

        # ⟨p²⟩
        exp_p2 = expectation_value(psi, x, lambda p, xg: momentum_operator(p, xg) * momentum_operator(p, xg))
        results["expectation_p2"].append(exp_p2)

    return results


if __name__ == "__main__":
    # Scenario 1: Eigenvalues and eigenstates
    print("=" * 60)
    print("Quantum Harmonic Oscillator: Eigenvalues")
    print("=" * 60)

    result = compute_quantum_harmonic_oscillator(num_eigenstates=5)

    print("\nNumerical vs Analytical Energies:")
    print("  n   E_numerical   E_analytical   Relative Error")
    for n in range(len(result["energies"])):
        E_num = result["energies"][n]
        E_ana = result["energies_analytical"][n]
        err = result["error"][n]
        print(f"  {n}   {E_num:10.6f}   {E_ana:10.6f}   {err:.2e}")

    # Scenario 2: Time evolution and energy conservation
    print("\n" + "=" * 60)
    print("Time Evolution: Energy Conservation")
    print("=" * 60)

    result_t = evolve_ground_state_oscillator(t_max=10.0, num_points=512)

    print(f"\nInitial Energy:  {result_t['energies'][0]:.6f}")
    print(f"Final Energy:    {result_t['energies'][-1]:.6f}")
    print(f"Max Energy Error: {np.max(result_t['energy_error']):.2e}")
    print(f"Avg Energy Error: {np.mean(result_t['energy_error']):.2e}")

    print("\n✅ Harmonic oscillator scenario complete")
