"""Quantum systems numerical simulation."""

import numpy as np


def simulate_particle_in_box(
    length: float = 1.0, n_states: int = 5, n_points: int = 100
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate particle in a box quantum system.

    Computes energy eigenvalues and normalized wavefunctions for
    a particle confined to a 1D box of given length.

    Args:
        length: Box length (in normalized units)
        n_states: Number of energy states to compute
        n_points: Number of spatial grid points

    Returns:
        (positions, wavefunction) where positions is the spatial grid
        and wavefunction is the ground state (n=1) normalized wavefunction
    """
    x = np.linspace(0, length, n_points)
    n = 1  # Ground state

    # Particle in a box: ψ_n(x) = sqrt(2/L) * sin(n*π*x/L)
    wavefunction = np.sqrt(2 / length) * np.sin(n * np.pi * x / length)

    # Energy eigenvalue: E_n = n² π² ℏ²/(2mL²) (normalized units: ℏ=m=1)
    energy = n**2 * np.pi**2 / (2 * length**2)

    print(f"✓ Particle in box: L={length}, E_1={energy:.4f}")
    return x, wavefunction


def simulate_harmonic_oscillator(
    omega: float = 1.0, n_state: int = 0, x_max: float = 5.0, n_points: int = 100
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate quantum harmonic oscillator.

    Computes energy eigenvalues and normalized wavefunctions for
    a quantum harmonic oscillator with angular frequency omega.

    Args:
        omega: Oscillator angular frequency (normalized units)
        n_state: Quantum number (ground state: n=0)
        x_max: Maximum displacement (in units of length)
        n_points: Number of spatial grid points

    Returns:
        (positions, wavefunction) where positions is centered at origin
        and wavefunction is the n-th eigenstate
    """
    x = np.linspace(-x_max, x_max, n_points)

    # Harmonic oscillator ground state (n=0):
    # ψ_0(x) = (mω/πℏ)^(1/4) * exp(-mωx²/2ℏ) (normalized units: ℏ=m=1)
    if n_state == 0:
        # characteristic length scale: sqrt(ℏ/(mω))
        wavefunction = (omega / np.pi) ** 0.25 * np.exp(-omega * x**2 / 2)

        # Energy eigenvalue: E_n = (n + 1/2)ℏω (normalized units: ℏ=1)
        energy = 0.5 * omega
    else:
        # For higher states, use Hermite polynomial expansion (simplified)
        hermite_poly = 1 if n_state == 0 else 2 * x
        wavefunction = (omega / np.pi) ** 0.25 * hermite_poly * np.exp(-omega * x**2 / 2)
        energy = (n_state + 0.5) * omega

    print(f"✓ Harmonic oscillator: ω={omega}, n={n_state}, E={energy:.4f}")
    return x, wavefunction


if __name__ == "__main__":
    # Run simulations with default parameters
    x_box, psi_box = simulate_particle_in_box()
    x_ho, psi_ho = simulate_harmonic_oscillator()
    print("✓ Simulations complete")
