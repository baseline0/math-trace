"""
Scenario 3: Ebola, Stochastic SEIR Ensemble (Intermediate)

A small outbreak in a population of 10,000 modelled with Poisson transitions, so chance matters:
some runs die out early, others grow. The ensemble spread shows that variability.

Parameters (per day), chosen for illustration:
- R₀ = β/γ = 1.8
- Infectious period 10 days (γ = 0.1)
- Incubation period about 9 days (σ = 1/9)
- Case fatality ratio 50%

The fatality ratio is applied when reporting deaths among removed cases. It does not change the dynamics,
because the SEIR model has one removed compartment.
"""

import numpy as np

from ..model import attack_rate, propagate_seir, propagate_seir_stochastic


def ebola_parameters() -> dict[str, float]:
    """Ebola transmission parameters per day, with R₀ = β/γ and the fatality ratio."""
    gamma = 0.1  # infectious period 10 days
    R0 = 1.8
    return {
        "R0": R0,
        "beta": R0 * gamma,
        "gamma": gamma,
        "sigma": 1.0 / 9.0,  # incubation period 9 days
        "case_fatality_ratio": 0.5,
    }


def run_ensemble(
    population: int = 10000,
    initial_exposed: int = 0,
    initial_infected: int = 5,
    t_max: float = 365.0,
    dt: float = 1.0,
    num_runs: int = 10,
    seed: int = 2026,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    """
    Run the stochastic SEIR ensemble with the Ebola parameters.

    Returns:
        t: Time points in days
        ensemble: Shape (num_runs, steps, 4) of integer [S, E, I, R] counts
        params: The parameter dictionary used
    """
    params = ebola_parameters()
    S0 = population - initial_exposed - initial_infected
    t, ensemble = propagate_seir_stochastic(
        S0,
        initial_exposed,
        initial_infected,
        0,
        t_max=t_max,
        dt=dt,
        beta=params["beta"],
        sigma=params["sigma"],
        gamma=params["gamma"],
        N=population,
        num_runs=num_runs,
        seed=seed,
    )
    return t, ensemble, params


def summarise(ensemble: np.ndarray, population: int, case_fatality_ratio: float) -> dict:
    """
    Per-run and ensemble outcomes.

    A run counts as a fade-out when its outbreak ends with fewer than 5% of the population ever infected.
    Deaths are estimated as the case fatality ratio times the removed count at the end of each run.
    """
    final = ensemble[:, -1, :]
    final_attack = final[:, 3] / population
    fade_out = final_attack < 0.05
    peak_infected = ensemble[:, :, 2].max(axis=1)
    deaths = case_fatality_ratio * final[:, 3]

    return {
        "final_attack_rate": final_attack,
        "mean_final_attack_rate": float(np.mean(final_attack)),
        "fade_out": fade_out,
        "fade_out_count": int(np.sum(fade_out)),
        "peak_infected": peak_infected,
        "mean_peak_infected": float(np.mean(peak_infected)),
        "estimated_deaths": deaths,
        "mean_estimated_deaths": float(np.mean(deaths)),
    }


def deterministic_final_size(
    population: int = 10000, initial_exposed: int = 0, initial_infected: int = 5, t_max: float = 365.0, dt: float = 1.0
) -> float:
    """Final attack rate of the deterministic SEIR model with the same parameters, as a fraction of the population."""
    params = ebola_parameters()
    S0 = (population - initial_exposed - initial_infected) / population
    _t, solution = propagate_seir(
        S0,
        initial_exposed / population,
        initial_infected / population,
        0.0,
        t_max=t_max,
        dt=dt,
        beta=params["beta"],
        sigma=params["sigma"],
        gamma=params["gamma"],
    )
    return attack_rate(solution)


def simulate_scenario() -> dict:
    """Run the ensemble and summarise it, alongside the deterministic final size for comparison."""
    population = 10000
    t, ensemble, params = run_ensemble(population=population)
    summary = summarise(ensemble, population, params["case_fatality_ratio"])
    return {
        "t": t,
        "ensemble": ensemble,
        "params": params,
        "deterministic_final_size": deterministic_final_size(population=population),
        **summary,
    }


if __name__ == "__main__":
    result = simulate_scenario()
    params = result["params"]

    print("=" * 70)
    print("Ebola: stochastic SEIR ensemble, N = 10,000, 10 runs")
    print("=" * 70)
    print(
        f"\n  R₀ = {params['R0']}, β = {params['beta']:.3f}/day, γ = {params['gamma']}/day, σ = {params['sigma']:.3f}/day"
    )
    print(f"  Fade-outs (under 5% infected): {result['fade_out_count']} of {len(result['final_attack_rate'])}")
    print(f"  Mean final attack rate: {result['mean_final_attack_rate']:.3f}")
    print(f"  Deterministic final size (for comparison): {result['deterministic_final_size']:.3f}")
    print(f"  Mean estimated deaths (CFR {params['case_fatality_ratio']:.0%}): {result['mean_estimated_deaths']:.0f}")

    print("\n✅ Ebola stochastic scenario complete")
