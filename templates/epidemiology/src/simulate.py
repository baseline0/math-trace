"""
Epidemiology simulations: SIR and SEIR disease dynamics.

Runs realistic pandemic scenarios and generates data for visualization.
"""

import numpy as np
from model import (
    propagate_sir,
    propagate_seir,
    attack_rate,
    peak_infections,
    basic_reproduction_number,
)


def covid_baseline(
    beta: float = 0.5,
    gamma: float = 1 / 10,  # 10-day infectious period
    days: int = 200,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate COVID-19 baseline scenario (SIR model).

    Args:
        beta: Transmission rate (contacts × probability per day)
        gamma: Recovery rate (1 / infectious period)
        days: Simulation duration (days)

    Returns:
        Tuple of (time, susceptible, infected)
    """
    # Initial conditions: 1 infected in population of 1M
    S0 = 0.999999
    I0 = 0.000001
    R0 = 0.0

    # Run SIR model
    t, S, I, R = propagate_sir(
        beta=beta,
        gamma=gamma,
        S0=S0,
        I0=I0,
        R0=R0,
        days=days,
    )

    return t, S, I


def measles_scenario(
    beta: float = 0.9,  # Measles is highly contagious
    sigma: float = 1 / 8,  # 8-day incubation
    gamma: float = 1 / 8,  # 8-day infectious period
    days: int = 200,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate measles outbreak (SEIR model with exposed period).

    Args:
        beta: Transmission rate
        sigma: Rate of progression from exposed to infected (1 / latency period)
        gamma: Recovery rate
        days: Simulation duration

    Returns:
        Tuple of (time, susceptible, exposed, infected)
    """
    S0 = 0.95
    E0 = 0.05  # 5% exposed (unvaccinated)
    I0 = 0.0
    R0 = 0.0

    t, S, E, I, R = propagate_seir(
        beta=beta,
        sigma=sigma,
        gamma=gamma,
        S0=S0,
        E0=E0,
        I0=I0,
        R0=R0,
        days=days,
    )

    return t, S, E, I


def intervention_scenario(
    beta_baseline: float = 0.5,
    beta_intervention: float = 0.15,  # 70% reduction via lockdown
    intervention_day: int = 50,
    gamma: float = 1 / 10,
    days: int = 200,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate intervention impact (e.g., lockdown, vaccination).

    Runs SIR with transmission rate drop at intervention_day.

    Args:
        beta_baseline: Pre-intervention transmission rate
        beta_intervention: Post-intervention transmission rate
        intervention_day: Day intervention begins
        gamma: Recovery rate
        days: Total simulation days

    Returns:
        Tuple of (time, susceptible, infected)
    """
    # Phase 1: Before intervention
    t1, S1, I1, R1 = propagate_sir(
        beta=beta_baseline,
        gamma=gamma,
        S0=0.999,
        I0=0.001,
        R0=0.0,
        days=intervention_day,
    )

    # Phase 2: After intervention (use state at intervention_day as initial)
    S_at_intervention = S1[-1]
    I_at_intervention = I1[-1]
    R_at_intervention = R1[-1]

    t2, S2, I2, R2 = propagate_sir(
        beta=beta_intervention,
        gamma=gamma,
        S0=S_at_intervention,
        I0=I_at_intervention,
        R0=R_at_intervention,
        days=(days - intervention_day),
    )

    # Combine phases
    t = np.concatenate([t1, intervention_day + t2[1:]])
    S = np.concatenate([S1, S2[1:]])
    I = np.concatenate([I1, I2[1:]])

    return t, S, I


def generate_report(t: np.ndarray, S: np.ndarray, I: np.ndarray) -> dict:
    """
    Generate epidemiological metrics from simulation.

    Args:
        t: Time vector
        S: Susceptible population
        I: Infected population

    Returns:
        Dict with key metrics
    """
    # Reconstruct R (population conservation)
    R = 1.0 - S - I

    # Calculate metrics
    total_infected = 1.0 - S[-1]  # Everyone not susceptible at end
    attack_rate_val = total_infected * 100

    # Peak infections
    peak_time = t[np.argmax(I)]
    peak_infected = np.max(I) * 100

    return {
        "attack_rate_pct": attack_rate_val,
        "peak_infections_pct": peak_infected,
        "peak_time_days": peak_time,
        "final_susceptible_pct": S[-1] * 100,
        "final_recovered_pct": R[-1] * 100,
        "duration_days": t[-1],
    }


if __name__ == "__main__":
    # Run baseline scenario
    t, S, I = covid_baseline()
    metrics = generate_report(t, S, I)

    print("COVID-19 Baseline (SIR)")
    print(f"  Attack rate: {metrics['attack_rate_pct']:.1f}%")
    print(f"  Peak infections: {metrics['peak_infections_pct']:.2f}% at day {metrics['peak_time_days']:.0f}")
    print(f"  Final recovered: {metrics['final_recovered_pct']:.1f}%")
    print()

    # Run measles scenario
    t_m, S_m, E_m, I_m = measles_scenario()
    metrics_m = generate_report(t_m, S_m, I_m)

    print("Measles Outbreak (SEIR)")
    print(f"  Attack rate: {metrics_m['attack_rate_pct']:.1f}%")
    print(f"  Peak infections: {metrics_m['peak_infections_pct']:.2f}% at day {metrics_m['peak_time_days']:.0f}")
    print()

    # Run intervention scenario
    t_int, S_int, I_int = intervention_scenario()
    metrics_int = generate_report(t_int, S_int, I_int)

    print("Intervention (Lockdown at day 50)")
    print(f"  Attack rate: {metrics_int['attack_rate_pct']:.1f}%")
    print(f"  Peak infections: {metrics_int['peak_infections_pct']:.2f}%")
