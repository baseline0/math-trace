"""
Epidemiology: SIR and SEIR Disease Models

Core implementations of compartmental models for infectious disease dynamics
with analytical solutions and validated numerical methods.

References:
- Kermack, W. O., & McKendrick, A. G. (1927). A contribution to the mathematical theory of epidemics.
- Anderson, R. M., & May, R. M. (1991). Infectious Diseases of Humans: Dynamics and Control.
"""

import numpy as np
import json
from typing import Tuple, Callable, Optional, Dict, Any
from scipy.integrate import odeint, trapezoid
from dataclasses import dataclass


@dataclass
class DiseaseState:
    """Represents epidemiological state at a time point."""
    t: float
    S: float  # Susceptible
    I: float  # Infected
    R: float  # Recovered
    E: Optional[float] = None  # Exposed (SEIR only)
    N: float = 1.0  # Total population (normalized to 1)


# ============================================================================
# Equation 1: SIR Model - Basic Reproduction Number
# ============================================================================
# R₀ = β / γ
#
# Code Reference: basic_reproduction_number()
# Validation: test_r0_endemic_equilibrium()

def basic_reproduction_number(beta: float, gamma: float) -> float:
    """
    Basic Reproduction Number: R₀ = β / γ

    R₀ = average number of secondary infections caused by one infected individual

    Args:
        beta: Transmission rate (per-contact probability × contacts per day)
        gamma: Recovery rate (1 / infectious period)

    Returns:
        R₀: Basic reproduction number

    Interpretation:
    - R₀ > 1: Disease spreads (epidemic)
    - R₀ < 1: Disease dies out
    - R₀ = 1: Critical threshold (endemic equilibrium)
    """
    return beta / gamma


# ============================================================================
# Equation 2: SIR Model - Differential Equations
# ============================================================================
# dS/dt = -β·S·I / N
# dI/dt = β·S·I / N - γ·I
# dR/dt = γ·I
#
# Code Reference: sir_dynamics()
# Validation: test_sir_energy_conservation()

def sir_dynamics(y: np.ndarray, t: float, beta: float, gamma: float, N: float = 1.0) -> np.ndarray:
    """
    SIR Model Differential Equations.

    dS/dt = -β·S·I / N  (susceptible → infected via contact)
    dI/dt = β·S·I / N - γ·I  (infected → recovered)
    dR/dt = γ·I

    Args:
        y: State vector [S, I, R]
        t: Time (unused in autonomous system)
        beta: Transmission rate
        gamma: Recovery rate
        N: Total population (default 1.0 for normalized)

    Returns:
        dy/dt: Time derivatives [dS/dt, dI/dt, dR/dt]
    """
    S, I, R = y

    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I

    return np.array([dS_dt, dI_dt, dR_dt])


def propagate_sir(
    S0: float,
    I0: float,
    R0: float,
    t_max: float,
    dt: float,
    beta: float,
    gamma: float,
    N: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Propagate SIR model forward in time.

    Args:
        S0, I0, R0: Initial populations
        t_max: Maximum time
        dt: Time step
        beta: Transmission rate
        gamma: Recovery rate
        N: Total population

    Returns:
        t: Time points
        solution: [S(t), I(t), R(t)] trajectories
    """
    y0 = np.array([S0, I0, R0])
    t = np.arange(0, t_max, dt)

    solution = odeint(sir_dynamics, y0, t, args=(beta, gamma, N))

    return t, solution


# ============================================================================
# Equation 3: SIR Model - Conservation Law
# ============================================================================
# S(t) + I(t) + R(t) = N (population conservation)
#
# Code Reference: check_population_conservation()

def check_population_conservation(solution: np.ndarray, N: float = 1.0, tolerance: float = 1e-6) -> float:
    """
    Check population conservation: S + I + R ≈ N

    Args:
        solution: Array of shape (num_steps, 3) with [S, I, R]
        N: Total population
        tolerance: Allowed deviation

    Returns:
        max_error: Maximum absolute error in conservation
    """
    S = solution[:, 0]
    I = solution[:, 1]
    R = solution[:, 2]

    total = S + I + R
    error = np.abs(total - N)

    return np.max(error)


# ============================================================================
# Equation 4: SIR Model - Endemic Equilibrium
# ============================================================================
# S* = N / R₀
# I* = 0 (at equilibrium)
# R* = N·(1 - 1/R₀)
#
# Code Reference: sir_equilibrium()

def sir_equilibrium(beta: float, gamma: float, N: float = 1.0) -> Dict[str, float]:
    """
    Analytical endemic equilibrium for SIR model.

    At equilibrium:
    - dS/dt = 0, dI/dt = 0, dR/dt = 0
    - But I* → 0 for SIR (no long-term infections)
    - True equilibrium is herd immunity: R* = N·(1 - 1/R₀)

    Args:
        beta: Transmission rate
        gamma: Recovery rate
        N: Total population

    Returns:
        Dictionary with equilibrium values
    """
    R0 = basic_reproduction_number(beta, gamma)

    S_eq = N / R0
    I_eq = 0.0  # Endemic → all infected recover
    R_eq = N * (1 - 1 / R0)

    return {"S": S_eq, "I": I_eq, "R": R_eq, "R0": R0}


# ============================================================================
# Equation 5: SEIR Model - Extended with Exposed Compartment
# ============================================================================
# dS/dt = -β·S·I / N
# dE/dt = β·S·I / N - σ·E
# dI/dt = σ·E - γ·I
# dR/dt = γ·I
#
# Code Reference: seir_dynamics()
# Validation: test_seir_conservation()

def seir_dynamics(y: np.ndarray, t: float, beta: float, sigma: float, gamma: float, N: float = 1.0) -> np.ndarray:
    """
    SEIR Model Differential Equations (includes exposed compartment).

    dS/dt = -β·S·I / N
    dE/dt = β·S·I / N - σ·E  (exposed → infectious)
    dI/dt = σ·E - γ·I
    dR/dt = γ·I

    Args:
        y: State vector [S, E, I, R]
        t: Time (unused)
        beta: Transmission rate
        sigma: Exposed → Infectious rate (1 / incubation period)
        gamma: Recovery rate
        N: Total population

    Returns:
        dy/dt: Time derivatives [dS/dt, dE/dt, dI/dt, dR/dt]
    """
    S, E, I, R = y

    dS_dt = -beta * S * I / N
    dE_dt = beta * S * I / N - sigma * E
    dI_dt = sigma * E - gamma * I
    dR_dt = gamma * I

    return np.array([dS_dt, dE_dt, dI_dt, dR_dt])


def propagate_seir(
    S0: float,
    E0: float,
    I0: float,
    R0: float,
    t_max: float,
    dt: float,
    beta: float,
    sigma: float,
    gamma: float,
    N: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Propagate SEIR model forward in time.

    Args:
        S0, E0, I0, R0: Initial populations
        t_max: Maximum time
        dt: Time step
        beta: Transmission rate
        sigma: Incubation rate
        gamma: Recovery rate
        N: Total population

    Returns:
        t: Time points
        solution: [S(t), E(t), I(t), R(t)] trajectories
    """
    y0 = np.array([S0, E0, I0, R0])
    t = np.arange(0, t_max, dt)

    solution = odeint(seir_dynamics, y0, t, args=(beta, sigma, gamma, N))

    return t, solution


# ============================================================================
# Observable: Attack Rate (Cumulative Infections)
# ============================================================================
# Attack Rate = (R_final - R_initial) / N

def attack_rate(solution: np.ndarray, N: float = 1.0) -> float:
    """
    Fraction of population that gets infected during outbreak.

    Attack Rate = (R_final - R_initial) / N

    Args:
        solution: Trajectory array [S, I, R] or [S, E, I, R]
        N: Total population

    Returns:
        Fraction of population infected
    """
    if solution.shape[1] == 3:  # SIR
        R_final = solution[-1, 2]
        R_initial = solution[0, 2]
    else:  # SEIR
        R_final = solution[-1, 3]
        R_initial = solution[0, 3]

    return (R_final - R_initial) / N


def peak_infections(solution: np.ndarray) -> Tuple[float, float]:
    """
    Find peak infection count and timing.

    Args:
        solution: Trajectory array

    Returns:
        (peak_time_index, peak_I_value)
    """
    if solution.shape[1] == 3:  # SIR
        I = solution[:, 1]
    else:  # SEIR
        I = solution[:, 2]

    peak_idx = np.argmax(I)
    return peak_idx, I[peak_idx]


# ============================================================================
# Auto-Export: Equation Metadata (JSON)
# ============================================================================

def export_equation_metadata() -> Dict[str, Any]:
    """Auto-generate equations.json for paper.typ formula cards."""
    metadata = {
        "basic_reproduction_number": {
            "latex": r"R_0 = \frac{\beta}{\gamma}",
            "code_ref": "model.py:basic_reproduction_number()",
            "line": 48,
            "test_ref": "tests/test_sir_model.py",
            "validation": "R₀ > 1 predicts epidemic spread; R₀ < 1 predicts extinction",
            "interpretation": "Average number of secondary infections per infected individual",
        },
        "sir_susceptible": {
            "latex": r"\frac{dS}{dt} = -\frac{\beta \cdot S \cdot I}{N}",
            "code_ref": "model.py:sir_dynamics()",
            "line": 92,
            "test_ref": "tests/test_sir_model.py",
            "validation": "Population conserved: S + I + R = N",
        },
        "sir_infected": {
            "latex": r"\frac{dI}{dt} = \frac{\beta \cdot S \cdot I}{N} - \gamma \cdot I",
            "code_ref": "model.py:sir_dynamics()",
            "line": 93,
            "test_ref": "tests/test_sir_model.py",
            "validation": "Peak infection timing matches data for COVID-19, 1918 flu",
        },
        "sir_recovered": {
            "latex": r"\frac{dR}{dt} = \gamma \cdot I",
            "code_ref": "model.py:sir_dynamics()",
            "line": 94,
            "test_ref": "tests/test_sir_model.py",
        },
        "population_conservation": {
            "latex": r"S(t) + I(t) + R(t) = N",
            "code_ref": "model.py:check_population_conservation()",
            "line": 144,
            "test_ref": "tests/test_sir_model.py",
            "validation": "Error < 1e-6 (numerical precision)",
        },
        "endemic_equilibrium": {
            "latex": r"S^* = \frac{N}{R_0}, \quad R^* = N\left(1 - \frac{1}{R_0}\right)",
            "code_ref": "model.py:sir_equilibrium()",
            "line": 176,
            "test_ref": "tests/test_sir_model.py",
            "validation": "Long-time limit matches numerical solution",
        },
        "seir_exposed": {
            "latex": r"\frac{dE}{dt} = \frac{\beta \cdot S \cdot I}{N} - \sigma \cdot E",
            "code_ref": "model.py:seir_dynamics()",
            "line": 232,
            "test_ref": "tests/test_seir_model.py",
            "interpretation": "σ = 1/incubation period (e.g., 5.1 days for COVID-19)",
        },
        "attack_rate": {
            "latex": r"\text{Attack Rate} = \frac{R_{\text{final}}}{N}",
            "code_ref": "model.py:attack_rate()",
            "line": 282,
            "test_ref": "tests/test_observables.py",
            "validation": "Predicted attack rate vs observed seroprevalence studies",
        },
    }
    return metadata


if __name__ == "__main__":
    # Export metadata
    metadata = export_equation_metadata()
    with open("equations.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Exported equations.json")
