"""
Control Systems: Linear Systems & PID Controllers

State-space representation, stability analysis, and PID control design.

References:
- Ogata, K. (2010). Modern Control Engineering (5th ed.).
- Franklin, G. F., et al. (2010). Feedback Control of Dynamic Systems.
"""

import numpy as np
import json
from typing import Tuple, Dict, Any, Optional, Callable
from scipy.integrate import odeint
from scipy.linalg import eig


# ============================================================================
# Equation 1: State-Space Representation
# ============================================================================
# ẋ = A·x + B·u
# y = C·x + D·u
#
# Code Reference: state_space_dynamics()

class LinearSystem:
    """Linear time-invariant system in state-space form."""

    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray = None):
        """
        Initialize SISO or MIMO linear system.

        ẋ = A·x + B·u (state equation)
        y = C·x + D·u (output equation)

        Args:
            A: State matrix (n × n)
            B: Input matrix (n × m)
            C: Output matrix (p × n)
            D: Feedthrough matrix (p × m), default 0
        """
        self.A = A
        self.B = B
        self.C = C
        self.D = D if D is not None else np.zeros((C.shape[0], B.shape[1]))

        self.n = A.shape[0]  # Number of states
        self.m = B.shape[1]  # Number of inputs
        self.p = C.shape[0]  # Number of outputs

    def dynamics(self, x: np.ndarray, t: float, u: Callable) -> np.ndarray:
        """ẋ = A·x + B·u(t)"""
        return self.A @ x + self.B @ u(t)

    def output(self, x: np.ndarray, u_val: float) -> np.ndarray:
        """y = C·x + D·u"""
        return self.C @ x + self.D * u_val

    def poles(self) -> np.ndarray:
        """Eigenvalues of A (system poles)."""
        eigenvalues, _ = eig(self.A)
        return np.sort_complex(eigenvalues)

    def is_stable(self) -> bool:
        """Stable iff all poles have negative real part."""
        poles = self.poles()
        return np.all(np.real(poles) < 0)


def state_space_dynamics(x: np.ndarray, t: float, A: np.ndarray, B: np.ndarray, u: Callable) -> np.ndarray:
    """
    State-space dynamics: ẋ = A·x + B·u

    Args:
        x: State vector
        t: Time
        A: State matrix
        B: Input matrix
        u: Input signal function u(t)

    Returns:
        dx/dt: State derivative
    """
    return A @ x + B @ u(t)


# ============================================================================
# Equation 2: PID Controller
# ============================================================================
# u(t) = K_p·e(t) + K_i·∫e(τ)dτ + K_d·de/dt
#
# Code Reference: PIDController class

class PIDController:
    """PID (Proportional-Integral-Derivative) controller."""

    def __init__(self, K_p: float, K_i: float, K_d: float, setpoint: float = 0.0):
        """
        Initialize PID controller.

        u = K_p·e + K_i·∫e + K_d·ė

        Args:
            K_p: Proportional gain
            K_i: Integral gain
            K_d: Derivative gain
            setpoint: Desired setpoint (reference)
        """
        self.K_p = K_p
        self.K_i = K_i
        self.K_d = K_d
        self.setpoint = setpoint

        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, measurement: float, dt: float) -> float:
        """
        Update controller and compute control signal.

        Args:
            measurement: Current measured output
            dt: Time step

        Returns:
            u: Control signal
        """
        error = self.setpoint - measurement

        # Proportional term
        P = self.K_p * error

        # Integral term (accumulate error)
        self.integral += error * dt
        I = self.K_i * self.integral

        # Derivative term
        if dt > 0:
            D = self.K_d * (error - self.prev_error) / dt
        else:
            D = 0.0

        self.prev_error = error

        return P + I + D


# ============================================================================
# Equation 3: Steady-State Error
# ============================================================================
# e_ss = 1 / (1 + K_p) for unit step, constant K_p
#
# Code Reference: steady_state_error()

def steady_state_error(K_p: float, step_magnitude: float = 1.0) -> float:
    """
    Steady-state error for proportional controller with step input.

    e_ss = step_magnitude / (1 + K_p)

    Args:
        K_p: Proportional gain
        step_magnitude: Magnitude of step input

    Returns:
        Steady-state error
    """
    return step_magnitude / (1 + K_p)


# ============================================================================
# Equation 4: Settling Time & Overshoot (2nd Order System)
# ============================================================================
# ω_n² = natural frequency squared
# ζ = damping ratio
# t_s ≈ 4/(ζ·ω_n) (2% criterion)
# M_p = exp(-ζ·π/√(1-ζ²))·100% (peak overshoot)
#
# Code Reference: second_order_response()

def second_order_response(omega_n: float, zeta: float) -> Dict[str, float]:
    """
    Transient response metrics for 2nd order system.

    Args:
        omega_n: Natural frequency (rad/s)
        zeta: Damping ratio (0 = undamped, 1 = critical, >1 = overdamped)

    Returns:
        Dictionary with rise_time, peak_time, overshoot, settling_time
    """
    if zeta <= 0:
        raise ValueError("Damping ratio must be positive")

    if zeta < 1:  # Underdamped
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        rise_time = (np.pi - np.arccos(zeta)) / omega_d
        peak_time = np.pi / omega_d
        overshoot = 100 * np.exp(-zeta * np.pi / np.sqrt(1 - zeta**2))
        settling_time = 4 / (zeta * omega_n)
    else:  # Overdamped or critically damped
        rise_time = (1 / omega_n) * np.log(2 / (2 * zeta - 1))
        peak_time = float('inf')
        overshoot = 0.0
        settling_time = 4 / (zeta * omega_n)

    return {
        "omega_n": omega_n,
        "zeta": zeta,
        "rise_time": rise_time,
        "peak_time": peak_time,
        "overshoot_percent": overshoot,
        "settling_time": settling_time,
    }


# ============================================================================
# Equation 5: Stability Criterion (Pole Locations)
# ============================================================================
# Stable iff all poles have Re(λ) < 0
#
# Code Reference: LinearSystem.is_stable()

def simulate_feedback_system(
    system: LinearSystem,
    controller: PIDController,
    t_sim: float,
    dt: float,
    x0: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate closed-loop system with feedback controller.

    Args:
        system: LinearSystem instance
        controller: PIDController instance
        t_sim: Simulation time
        dt: Time step
        x0: Initial state (default: zero)

    Returns:
        t, x, y, u: Time, states, outputs, control signals
    """
    if x0 is None:
        x0 = np.zeros(system.n)

    t = np.arange(0, t_sim, dt)
    num_steps = len(t)

    x = np.zeros((num_steps, system.n))
    y = np.zeros(num_steps)
    u = np.zeros(num_steps)

    x[0] = x0

    for i in range(1, num_steps):
        # Measure output
        y[i-1] = float(system.output(x[i-1], u[i-1]))

        # Compute control signal
        u[i] = controller.update(y[i-1], dt)

        # Update state
        x[i] = x[i-1] + dt * (system.A @ x[i-1] + system.B * u[i])

    y[-1] = float(system.output(x[-1], u[-1]))

    return t, x, y, u


def export_equation_metadata() -> Dict[str, Any]:
    """Auto-generate equations.json for paper.typ."""
    return {
        "state_space": {
            "latex": r"\dot{x} = A \mathbf{x} + B \mathbf{u}, \quad \mathbf{y} = C \mathbf{x} + D \mathbf{u}",
            "code_ref": "model.py:LinearSystem",
            "line": 24,
            "description": "LTI system representation: compact form for analysis & control design",
        },
        "pid_control": {
            "latex": r"u(t) = K_p e(t) + K_i \int e(\tau) d\tau + K_d \frac{de}{dt}",
            "code_ref": "model.py:PIDController",
            "line": 95,
            "description": "PID controller: proportional, integral, derivative terms",
        },
        "steady_state_error": {
            "latex": r"e_{ss} = \frac{1}{1 + K_p}",
            "code_ref": "model.py:steady_state_error()",
            "line": 159,
            "validation": "↓ K_p → ↓ e_ss (higher gain → lower error)",
        },
        "settling_time": {
            "latex": r"t_s \approx \frac{4}{\zeta \omega_n}",
            "code_ref": "model.py:second_order_response()",
            "line": 187,
            "validation": "2% settling time criterion",
        },
        "stability": {
            "latex": r"\text{Stable} \iff \text{Re}(\lambda_i) < 0 \text{ for all poles}",
            "code_ref": "model.py:LinearSystem.is_stable()",
            "line": 59,
            "validation": "All eigenvalues of A in left half-plane",
        },
    }


if __name__ == "__main__":
    metadata = export_equation_metadata()
    with open("equations.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Exported equations.json")
