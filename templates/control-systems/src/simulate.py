"""Control systems simulations: feedback control and PID tuning."""

import numpy as np
from scipy.integrate import odeint
from model import PIDController, LinearSystem, simulate_feedback_system

def step_response_first_order(tau: float = 1.0, K: float = 1.0, t_end: float = 5.0):
    """First-order system step response: tau*dx/dt + x = K*u."""
    def system(x, t):
        return (K - x) / tau
    
    t = np.linspace(0, t_end, 100)
    x = odeint(system, 0, t)
    return t, x.flatten()

def pid_control_demo(Kp: float = 2.0, Ki: float = 0.5, Kd: float = 0.1):
    """PID control of first-order system."""
    A = np.array([[-1.0]])
    B = np.array([[1.0]])
    C = np.array([[1.0]])
    system = LinearSystem(A, B, C)
    
    pid = PIDController(Kp, Ki, Kd, dt=0.01)
    
    t = np.linspace(0, 10, 1000)
    y_list, u_list = [], []
    x = np.array([0.0])
    
    for ti in t:
        error = 1.0 - x[0]
        u = pid.compute(error)
        dx = A @ x + B * u
        x = x + dx * 0.01
        y_list.append(x[0])
        u_list.append(u)
    
    return t, np.array(y_list), np.array(u_list)

if __name__ == "__main__":
    t, y = step_response_first_order()
    print(f"First-order step response: steady-state = {y[-1]:.3f}")
    
    t, y, u = pid_control_demo()
    print(f"PID control: final error = {1.0 - y[-1]:.4f}")
