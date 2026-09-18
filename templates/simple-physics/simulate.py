"""
Simulate a harmonic oscillator and export trajectory data.

Run: python simulate.py
"""

import numpy as np


def simulate_harmonic_oscillator(
    amplitude: float = 1.0,
    omega: float = 1.0,
    steps: int = 200,
    dt: float = 0.01,
    seed: int = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate a harmonic oscillator: x(t) = A * cos(ωt)

    Args:
        amplitude: Initial amplitude A
        omega: Angular frequency ω (rad/s)
        steps: Number of time steps
        dt: Time step (seconds)
        seed: Random seed (for reproducibility)

    Returns:
        Tuple of (time_array, position_array)
    """
    if seed is not None:
        np.random.seed(seed)

    # Time array: 0 to T
    t = np.linspace(0, steps * dt, steps)

    # Ideal trajectory: x(t) = A * cos(ωt)
    x_ideal = amplitude * np.cos(omega * t)

    # Add small Gaussian noise for realism
    noise = np.random.normal(0, amplitude * 0.05, steps)
    x = x_ideal + noise

    return t, x


if __name__ == '__main__':
    # Run default simulation
    t, x = simulate_harmonic_oscillator(amplitude=2.0, omega=0.5, steps=200, dt=0.1, seed=42)

    print(f"✅ Simulated harmonic oscillator")
    print(f"   Time steps: {len(t)}")
    print(f"   Initial x: {x[0]:.3f}")
    print(f"   Final x: {x[-1]:.3f}")
    print(f"   Time range: [{t[0]:.1f}, {t[-1]:.1f}]")
