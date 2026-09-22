"""
Scenario 1: COVID-19 SIR Model (Beginner)

Reproduce key COVID-19 dynamics using SIR model with realistic parameters.

Parameters from:
- He et al. (2020): SARS-CoV-2 generation interval ~5.1 days
- CDC: R₀ ≈ 2-2.5 (original Wuhan strain)
- Hospitalization: ~5% of infected
"""

import numpy as np
from typing import Dict, Tuple
from ..model import (
    basic_reproduction_number,
    propagate_sir,
    check_population_conservation,
    sir_equilibrium,
    attack_rate,
    peak_infections,
)


def covid_parameters() -> Dict[str, float]:
    """
    COVID-19 epidemiological parameters (per day).

    Returns:
        Dictionary with beta, gamma, generation_interval, R0
    """
    generation_interval = 5.1  # days (He et al. 2020)
    R0 = 2.5  # Basic reproduction number (Wuhan strain)

    # γ = 1 / infectious period ≈ 1 / 10 days
    gamma = 1.0 / 10.0  # People infectious for ~10 days

    # β = R₀ × γ
    beta = R0 * gamma

    return {
        "beta": beta,
        "gamma": gamma,
        "R0": R0,
        "generation_interval": generation_interval,
        "infectious_period": 1.0 / gamma,
    }


def simulate_covid_wave(
    population: float = 1e7,  # 10 million population
    initial_infected: float = 100,  # 100 infected at t=0
    days_to_simulate: float = 365,
) -> Dict:
    """
    Simulate first COVID-19 wave using SIR model.

    Args:
        population: Total population
        initial_infected: Number of infected at t=0
        days_to_simulate: Simulation duration

    Returns:
        Dictionary with trajectories, metrics, and analytical solutions
    """
    params = covid_parameters()
    beta = params["beta"]
    gamma = params["gamma"]
    R0 = params["R0"]

    # Initial conditions (normalized)
    N = population
    S0 = (population - initial_infected) / population
    I0 = initial_infected / population
    R0_init = 0.0

    # Propagate
    t, solution = propagate_sir(
        S0, I0, R0_init,
        t_max=days_to_simulate,
        dt=0.1,
        beta=beta,
        gamma=gamma,
        N=1.0
    )

    # Denormalize to actual population
    S = solution[:, 0] * population
    I = solution[:, 1] * population
    R = solution[:, 2] * population

    # Compute observables
    conservation_error = check_population_conservation(solution, N=1.0)
    eq = sir_equilibrium(beta, gamma, N=1.0)
    ar = attack_rate(solution, N=1.0)
    peak_idx, peak_I = peak_infections(solution)
    peak_I *= population
    peak_time = t[peak_idx]

    return {
        "t": t,
        "S": S,
        "I": I,
        "R": R,
        "R0": R0,
        "beta": beta,
        "gamma": gamma,
        "conservation_error": conservation_error,
        "equilibrium": eq,
        "attack_rate": ar,
        "peak_time_days": peak_time,
        "peak_I_count": peak_I,
        "hospitalized_peak": peak_I * 0.05,  # ~5% hospitalization rate
        "population": population,
    }


def compute_intervention_effect(
    beta_baseline: float,
    gamma: float,
    intervention_reductions: list,  # [30%, 50%, 70%] etc.
    days_to_simulate: float = 365,
) -> Dict:
    """
    Simulate effect of social distancing/vaccination.

    Args:
        beta_baseline: Transmission rate without intervention
        gamma: Recovery rate
        intervention_reductions: List of transmission reductions (e.g., [0.3, 0.5, 0.7])
        days_to_simulate: Simulation duration

    Returns:
        Dictionary with baseline and intervention scenarios
    """
    S0, I0, R0 = 0.999, 0.001, 0.0  # 0.1% infected initially

    results = {
        "baseline": {},
        "interventions": {}
    }

    # Baseline (no intervention)
    t, sol = propagate_sir(S0, I0, R0, days_to_simulate, 0.1, beta_baseline, gamma)
    results["baseline"]["t"] = t
    results["baseline"]["I"] = sol[:, 1]
    results["baseline"]["peak_I"] = np.max(sol[:, 1])
    results["baseline"]["attack_rate"] = np.max(sol[:, 2])

    # With interventions
    for reduction in intervention_reductions:
        beta_reduced = beta_baseline * (1 - reduction)
        t, sol = propagate_sir(S0, I0, R0, days_to_simulate, 0.1, beta_reduced, gamma)

        results["interventions"][f"{int(reduction*100)}%_reduction"] = {
            "t": t,
            "I": sol[:, 1],
            "peak_I": np.max(sol[:, 1]),
            "attack_rate": np.max(sol[:, 2]),
            "peak_reduction": 1 - (np.max(sol[:, 1]) / results["baseline"]["peak_I"]),
        }

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("COVID-19 Wave Simulation")
    print("=" * 70)

    result = simulate_covid_wave()

    print(f"\nBasic Reproduction Number R₀: {result['R0']:.2f}")
    print(f"  (Each infected person infects ~{result['R0']:.1f} others on average)")
    print()
    print(f"Peak Infections: {result['peak_I_count']:,.0f} people")
    print(f"  Occurs at day {result['peak_time_days']:.1f}")
    print(f"  Peak hospitalizations: {result['hospitalized_peak']:,.0f}")
    print()
    print(f"Attack Rate: {result['attack_rate']*100:.1f}% of population")
    print(f"  = {result['attack_rate'] * result['population']:,.0f} total infected")
    print()
    print(f"Population Conservation Error: {result['conservation_error']:.2e}")
    print(f"  ✓ SIR model preserves population ({result['population']:,.0f})")

    print("\n" + "=" * 70)
    print("Intervention Analysis: Effect of Transmission Reduction")
    print("=" * 70)

    interventions = compute_intervention_effect(
        beta_baseline=result["beta"],
        gamma=result["gamma"],
        intervention_reductions=[0.30, 0.50, 0.70],  # 30%, 50%, 70% reduction
    )

    print(f"\nBaseline (no intervention):")
    print(f"  Peak infections: {interventions['baseline']['peak_I']*100:.1f}% of population")

    for key, val in interventions["interventions"].items():
        print(f"\n{key} transmission reduction:")
        print(f"  Peak infections: {val['peak_I']*100:.1f}% of population")
        print(f"  Peak reduction: {val['peak_reduction']*100:.0f}%")
        print(f"  Attack rate: {val['attack_rate']*100:.1f}%")

    print("\n✅ COVID-19 scenario complete")
