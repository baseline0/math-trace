"""
Stochastic simulation of P-system rule 2a → b.

Based on mass-action kinetics with rate r = k * n_a * (n_a - 1) / 2.
"""

import numpy as np
from typing import Tuple


def simulate(
    k_val: float = 0.01,
    na0: int = 50,
    nb0: int = 0,
    steps: int = 200,
    dt: float = 0.1,
    seed: int | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate rule 2a → b under stochastic mass-action kinetics.

    Args:
        k_val: Rate constant (k > 0)
        na0: Initial count of a objects
        nb0: Initial count of b objects (not tracked in output)
        steps: Number of simulation steps
        dt: Time step
        seed: Random seed for reproducibility

    Returns:
        (times, na_trajectory) arrays of shape (steps+1,)
    """
    if seed is not None:
        np.random.seed(seed)

    na = na0
    nb = nb0

    times = [0.0]
    na_traj = [na]

    for i in range(steps):
        t = times[-1]

        # Compute rate: r = k * C(n_a, 2)
        if na < 2:
            rate = 0.0
        else:
            rate = k_val * na * (na - 1) / 2

        # Probability of reaction in dt (Euler method)
        prob_reaction = rate * dt

        if np.random.random() < prob_reaction and na >= 2:
            na -= 2  # Consume 2a
            nb += 1  # Produce b (not tracked)

        times.append(t + dt)
        na_traj.append(na)

    return np.array(times), np.array(na_traj)


if __name__ == '__main__':
    ts, na = simulate(steps=200, seed=42)
    print(f"✅ Simulation complete: {len(ts)} time steps")
    print(f"   Initial n_a: {na[0]}")
    print(f"   Final n_a: {na[-1]}")
    print(f"   Time range: [{ts[0]:.1f}, {ts[-1]:.1f}]")
