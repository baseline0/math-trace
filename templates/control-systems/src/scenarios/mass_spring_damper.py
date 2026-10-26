"""
Scenario: Mass-Spring-Damper (Beginner)

Second-order mechanical system: m·ẍ + c·ẋ + k·x = F(t).
The damping ratio ζ = c / (2·√(k·m)) sets the response: underdamped (ζ < 1) rings and overshoots,
critically damped (ζ = 1) settles fastest without overshoot, overdamped (ζ > 1) is slow and sluggish.
"""

import numpy as np
from scipy.integrate import odeint

from ..model import LinearSystem


def natural_frequency(m: float, k: float) -> float:
    """Undamped natural frequency ω_n = √(k/m) in rad/s."""
    return float(np.sqrt(k / m))


def damping_ratio(m: float, c: float, k: float) -> float:
    """Damping ratio ζ = c / (2·√(k·m)), dimensionless."""
    return float(c / (2.0 * np.sqrt(k * m)))


def classify_damping(zeta: float, tolerance: float = 1e-9) -> str:
    """Name the response regime from the damping ratio."""
    if zeta < 1.0 - tolerance:
        return "underdamped"
    if zeta > 1.0 + tolerance:
        return "overdamped"
    return "critically_damped"


def percent_overshoot(zeta: float) -> float:
    """Peak overshoot of the unit step response, in percent. Zero unless underdamped."""
    if zeta >= 1.0:
        return 0.0
    return float(100.0 * np.exp(-np.pi * zeta / np.sqrt(1.0 - zeta**2)))


def state_space(m: float, c: float, k: float) -> LinearSystem:
    """
    State-space form with state [x, ẋ], input F, output position x.

    A = [[0, 1], [-k/m, -c/m]], B = [[0], [1/m]], C = [[1, 0]]
    """
    A = np.array([[0.0, 1.0], [-k / m, -c / m]])
    B = np.array([[0.0], [1.0 / m]])
    C = np.array([[1.0, 0.0]])
    return LinearSystem(A, B, C)


def step_response(m: float, c: float, k: float, force: float = 1.0, t_end: float = 10.0, dt: float = 0.001) -> tuple:
    """
    Position response to a constant force applied at t = 0 from rest.

    Returns:
        t: Time points
        x: Position over time
    """

    def dynamics(state, _t):
        x, v = state
        return [v, (force - c * v - k * x) / m]

    t = np.arange(0.0, t_end + dt / 2, dt)
    solution = odeint(dynamics, [0.0, 0.0], t)
    return t, solution[:, 0]


def simulate_scenario(m: float = 1.0, c: float = 0.4, k: float = 4.0, force: float = 1.0) -> dict:
    """
    Run the step response and summarise it against the analytic results.

    Returns a dict with the parameters, the regime, the analytic overshoot, the measured overshoot,
    and the final value (which should approach F/k).
    """
    zeta = damping_ratio(m, c, k)
    t, x = step_response(m, c, k, force=force)
    static_position = force / k
    measured_overshoot = 100.0 * max(0.0, (np.max(x) - static_position) / static_position)

    return {
        "t": t,
        "position": x,
        "m": m,
        "c": c,
        "k": k,
        "force": force,
        "omega_n": natural_frequency(m, k),
        "zeta": zeta,
        "regime": classify_damping(zeta),
        "analytic_overshoot_percent": percent_overshoot(zeta),
        "measured_overshoot_percent": measured_overshoot,
        "final_position": x[-1],
        "static_position": static_position,
    }


if __name__ == "__main__":
    result = simulate_scenario()

    print("=" * 70)
    print("Mass-Spring-Damper Step Response")
    print("=" * 70)
    print(f"  ω_n = {result['omega_n']:.3f} rad/s, ζ = {result['zeta']:.3f} ({result['regime']})")
    print(
        f"  Overshoot: analytic {result['analytic_overshoot_percent']:.2f}%, measured {result['measured_overshoot_percent']:.2f}%"
    )
    print(f"  Final position {result['final_position']:.4f} vs F/k = {result['static_position']:.4f}")
    print("\n✅ Mass-spring-damper scenario complete")
