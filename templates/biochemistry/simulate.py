"""
Simulate Michaelis-Menten enzyme kinetics.

Run: python simulate.py
"""

import numpy as np


def michaelis_menten(S: np.ndarray, Vmax: float, Km: float) -> np.ndarray:
    """
    Michaelis-Menten equation: v = (Vmax * S) / (Km + S)

    Args:
        S: Substrate concentration array
        Vmax: Maximum velocity (μmol/min)
        Km: Michaelis constant (mM)

    Returns:
        Reaction velocity array (v)
    """
    return (Vmax * S) / (Km + S)


def simulate_enzyme_kinetics(
    Vmax: float = 100.0,
    Km: float = 5.0,
    steps: int = 100,
    S_max: float = 50.0,
    seed: int = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate enzyme kinetics across substrate concentration range.

    Args:
        Vmax: Maximum velocity (μmol/min)
        Km: Michaelis constant (mM)
        steps: Number of substrate concentrations to sample
        S_max: Maximum substrate concentration (mM)
        seed: Random seed (for reproducibility)

    Returns:
        Tuple of (S_array, v_array)
    """
    if seed is not None:
        np.random.seed(seed)

    # Substrate concentration range: 0 to S_max
    S = np.linspace(0.01, S_max, steps)

    # Ideal Michaelis-Menten kinetics
    v_ideal = michaelis_menten(S, Vmax, Km)

    # Add measurement noise (±5%)
    noise = np.random.normal(1.0, 0.05, steps)
    v_measured = v_ideal * noise

    return S, v_measured


if __name__ == '__main__':
    # Run default simulation
    S, v = simulate_enzyme_kinetics(Vmax=100.0, Km=5.0, steps=100, S_max=50.0, seed=42)

    print(f"✅ Simulated Michaelis-Menten kinetics")
    print(f"   Substrate range: [{S[0]:.2f}, {S[-1]:.2f}] mM")
    print(f"   Velocity range: [{v.min():.2f}, {v.max():.2f}] μmol/min")
    print(f"   Data points: {len(S)}")
