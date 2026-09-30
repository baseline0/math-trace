"""
SIR Model Simulation

Implements numerical integration of the SIR differential equations and
generates example outputs for the epidemiology paper.

Scenario: COVID-like baseline
  - R₀ = 2.0 (two secondary infections per primary case)
  - γ = 0.1 [1/days] (10-day infectious period)
  - β = R₀ × γ = 0.2 [1/days]
  - Population: N = 1,000,000
  - Initial: S₀ = 999,900, I₀ = 100, R₀ = 0
"""

import numpy as np
from scipy.integrate import odeint
from pathlib import Path
from typing import Tuple, Dict
import json


# === PARAMETERS ===

class Parameters:
    """SIR model parameters with units and domains."""

    def __init__(self, beta: float, gamma: float, N: int):
        """
        Args:
            beta: Transmission rate [1/days]
            gamma: Recovery rate [1/days]
            N: Population size [persons]
        """
        assert beta > 0, "beta must be positive"
        assert gamma > 0, "gamma must be positive"
        assert N > 0, "N must be positive"

        self.beta = beta
        self.gamma = gamma
        self.N = N
        self.R0 = beta / gamma  # Basic reproduction number

    def __repr__(self):
        return f"Parameters(β={self.beta}, γ={self.gamma}, R₀={self.R0:.2f}, N={self.N})"


# === SIR DIFFERENTIAL EQUATIONS ===

def sir_model(y: np.ndarray, t: float, params: Parameters) -> np.ndarray:
    """
    SIR model differential equations.

    Args:
        y: State vector [S, I, R]
        t: Time [days]
        params: Model parameters

    Returns:
        Derivatives [dS/dt, dI/dt, dR/dt]

    Equations (from model.py):
        dS/dt = -β S I / N
        dI/dt = β S I / N - γ I
        dR/dt = γ I

    Assumptions:
        - Homogeneous mixing (any S equally likely to contact any I)
        - No vital dynamics (births, deaths)
        - No behavior change (β constant)
        - Exponential recovery (1/γ = infectious period)
        - Permanent immunity (no reinfection)
    """
    S, I, R = y
    N = params.N
    beta = params.beta
    gamma = params.gamma

    # Rate equations
    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I

    # Verify conservation law: S + I + R should stay constant
    total = S + I + R
    if not np.isclose(total, N, rtol=1e-6):
        print(f"⚠️  Warning: Conservation violated. S+I+R={total}, expected N={N}")

    return np.array([dS_dt, dI_dt, dR_dt])


# === SCENARIOS ===

def covid_baseline() -> Tuple[np.ndarray, Parameters]:
    """
    COVID-like scenario with R₀ ≈ 2.

    Returns:
        (times, S, I, R), parameters
    """
    # Parameters
    R0_target = 2.0  # Basic reproduction number
    gamma = 0.1  # 10-day infectious period
    beta = R0_target * gamma  # Derive transmission rate
    N = 1_000_000  # Population

    params = Parameters(beta=beta, gamma=gamma, N=N)

    # Initial conditions
    I0 = 100  # Start with 100 infected
    R0 = 0    # No recovered yet
    S0 = N - I0 - R0  # Susceptible
    y0 = np.array([S0, I0, R0])

    # Time span: 100 days
    t = np.linspace(0, 100, 1001)  # Daily resolution

    # Integrate ODE
    solution = odeint(sir_model, y0, t, args=(params,))
    S, I, R = solution.T

    return t, S, I, R, params


def measles_scenario() -> Tuple[np.ndarray, Parameters]:
    """
    Measles scenario with R₀ ≈ 15 (highly contagious).

    Returns:
        (times, S, I, R), parameters
    """
    R0_target = 15.0  # Measles is very contagious
    gamma = 1/7  # 7-day infectious period (approximate)
    beta = R0_target * gamma
    N = 1_000_000

    params = Parameters(beta=beta, gamma=gamma, N=N)

    I0 = 10
    R0 = 0
    S0 = N - I0 - R0
    y0 = np.array([S0, I0, R0])

    t = np.linspace(0, 50, 501)  # Faster dynamics
    solution = odeint(sir_model, y0, t, args=(params,))
    S, I, R = solution.T

    return t, S, I, R, params


# === ANALYSIS FUNCTIONS ===

def compute_peak_infection(I: np.ndarray, t: np.ndarray) -> Tuple[float, float]:
    """Find time and magnitude of peak infections."""
    peak_idx = np.argmax(I)
    peak_time = t[peak_idx]
    peak_count = I[peak_idx]
    return peak_time, peak_count


def compute_attack_rate(R: np.ndarray) -> float:
    """Final attack rate (fraction of population infected)."""
    return R[-1] / R[-1] + 1e-10  # Avoid division by zero


def generate_report(t: np.ndarray, S: np.ndarray, I: np.ndarray,
                   R: np.ndarray, params: Parameters) -> Dict:
    """Generate quantitative report for scenario."""
    N = params.N
    peak_time, peak_count = compute_peak_infection(I, t)

    return {
        'parameters': {
            'R0': params.R0,
            'beta': params.beta,
            'gamma': params.gamma,
            'N': N,
            'infectious_period': 1 / params.gamma,
        },
        'initial_conditions': {
            'S0': S[0],
            'I0': I[0],
            'R0': R[0],
        },
        'key_outcomes': {
            'peak_infection_day': peak_time,
            'peak_infection_count': int(peak_count),
            'peak_infection_percentage': 100 * peak_count / N,
            'final_attack_rate': int(R[-1]),
            'final_attack_rate_percentage': 100 * R[-1] / N,
        },
    }


if __name__ == '__main__':
    # Run COVID scenario
    print("=== COVID-like Scenario (R₀=2) ===")
    t, S, I, R, params = covid_baseline()
    print(params)

    report = generate_report(t, S, I, R, params)
    print("\nKey outcomes:")
    for key, val in report['key_outcomes'].items():
        if isinstance(val, float):
            print(f"  {key}: {val:.1f}")
        else:
            print(f"  {key}: {val}")

    # Save report
    output_path = Path(__file__).parent / 'generated' / 'covid_scenario.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Report saved to {output_path}")
