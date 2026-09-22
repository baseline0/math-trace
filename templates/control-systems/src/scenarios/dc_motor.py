"""
Scenario: DC Motor Speed Control (Intermediate)

Speed control of a DC motor using PID controller.
Realistic parameters: J, b, K (inertia, damping, motor constant).
"""

import numpy as np
from typing import Dict, Tuple
from ..model import LinearSystem, PIDController, simulate_feedback_system, second_order_response


def dc_motor_system() -> LinearSystem:
    """
    DC motor state-space model.

    State: [ω] (angular velocity)
    Input: V (applied voltage)
    Output: ω (measured speed)

    J·ω̇ + b·ω = K·i (motor equation)
    L·i̇ + R·i = V - K·ω (electrical equation)
    Combined: ω̇ = (K/(J·L))·(V - K·ω) - b·ω/J

    Simplified (fast electrical response, L ≈ 0):
    ω̇ = -b/J·ω + K/(J·R)·V

    Parameters (realistic DC motor):
    - J = 0.01 kg·m² (inertia)
    - b = 0.1 N·m·s/rad (friction)
    - K = 0.01 N·m/A (motor constant)
    - R = 1.0 Ω (resistance)
    """
    J = 0.01   # inertia
    b = 0.1    # friction
    K = 0.01   # motor constant
    R = 1.0    # resistance

    # State-space: ẋ = A·x + B·u, y = C·x
    A = np.array([[-b/J]])
    B = np.array([[K / (J * R)]])
    C = np.array([[1.0]])  # Measure speed

    return LinearSystem(A, B, C)


def simulate_speed_control(
    target_speed: float = 100.0,  # rad/s
    K_p: float = 1.0,
    K_i: float = 0.5,
    K_d: float = 0.1,
    t_sim: float = 10.0,
) -> Dict:
    """
    Simulate DC motor speed control with PID.

    Args:
        target_speed: Desired angular velocity
        K_p, K_i, K_d: PID gains
        t_sim: Simulation time

    Returns:
        Dictionary with time, speed, error, control voltage
    """
    system = dc_motor_system()
    controller = PIDController(K_p, K_i, K_d, setpoint=target_speed)

    t, x, y, u = simulate_feedback_system(system, controller, t_sim, dt=0.01)

    error = target_speed - y
    peak_overshoot = np.max(y) - target_speed if np.max(y) > target_speed else 0
    steady_state_error = np.abs(error[-1])

    return {
        "t": t,
        "speed": y,
        "voltage": u,
        "error": error,
        "target_speed": target_speed,
        "K_p": K_p,
        "K_i": K_i,
        "K_d": K_d,
        "peak_overshoot": peak_overshoot,
        "steady_state_error": steady_state_error,
        "settling_time": estimate_settling_time(t, y, target_speed),
    }


def estimate_settling_time(t: np.ndarray, y: np.ndarray, setpoint: float, tolerance: float = 0.02) -> float:
    """Estimate 2% settling time."""
    error = np.abs(y - setpoint)
    threshold = tolerance * setpoint

    settled_idx = np.where(error <= threshold)[0]
    if len(settled_idx) > 0:
        return t[settled_idx[0]]
    else:
        return t[-1]


if __name__ == "__main__":
    print("=" * 70)
    print("DC Motor Speed Control")
    print("=" * 70)

    result = simulate_speed_control(target_speed=100.0)

    print(f"\nControl Performance:")
    print(f"  Target speed: {result['target_speed']:.1f} rad/s")
    print(f"  Peak overshoot: {result['peak_overshoot']:.2f} rad/s ({result['peak_overshoot']/result['target_speed']*100:.1f}%)")
    print(f"  Steady-state error: {result['steady_state_error']:.3f} rad/s")
    print(f"  Settling time (2%): {result['settling_time']:.2f} sec")

    print(f"\nPID Gains:")
    print(f"  K_p = {result['K_p']:.2f}")
    print(f"  K_i = {result['K_i']:.2f}")
    print(f"  K_d = {result['K_d']:.2f}")

    print("\n✅ DC motor scenario complete")
