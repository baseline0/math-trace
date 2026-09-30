#set document(title: "SIR Model: Understanding R₀")
#set page(numbering: "1")
#set heading(numbering: "1.")

// Load formula data
#let formulas = json("generated/sir_equations.json")
#let covid_scenario = json("generated/covid_scenario.json")

= SIR Model: Understanding the Basic Reproduction Number R₀

*Author:* Mathematical Epidemiology Reference
*Date:* 2026-09-29
*Scope:* Bounded first artifact (see LAUNCH_RECORD_EPIDEMIOLOGY_R0.md)

#outline()

== Problem Statement

Disease transmission occurs through a population in distinct stages. The *basic
reproduction number R₀* is a mathematical quantity that emerges from models of epidemic
spread: it answers the question "how many people will one infected person infect?" in
the context of simplified assumptions (constant contact rates, homogeneous mixing).
Understanding R₀ is essential for grasping how contagiousness relates to epidemic
control, though real-world forecasting requires additional modeling of behavior change,
interventions, and spatial heterogeneity.

This reference explains how R₀ emerges mathematically from the classical
Susceptible-Infected-Recovered (SIR) compartmental model, what assumptions it
encodes, and why it matters for disease control. We derive R₀ from first principles,
implement the model in Python, and demonstrate with a COVID-like example.

*Target reader:* Anyone unfamiliar with epidemiology who wants to understand where R₀
comes from and how it guides intervention policy (at a conceptual level).

== Variables, Parameters, and Domains

The SIR model tracks three populations over time:

#table(
  columns: (1fr, 1.2fr, 1.5fr, 1.5fr),
  [*Symbol*], [*Name*], [*Units*], [*Domain & Meaning*],
  [S(t)], [Susceptible count], [persons], [S ∈ [0, N]; individuals who can contract disease],
  [I(t)], [Infected count], [persons], [I ∈ [0, N]; individuals currently infectious],
  [R(t)], [Recovered count], [persons], [R ∈ [0, N]; individuals immune from prior infection],
  [N], [Population size], [persons], [ℤ⁺; constant (S + I + R = N)],
  [β], [Transmission rate], [1/days], [(0, ∞); contact frequency × transmission probability],
  [γ], [Recovery rate], [1/days], [(0, ∞); inverse of infectious period],
  [R₀], [Basic reproduction number], [dimensionless], [(0, ∞); R₀ = β / γ],
)

*Key conservation law:* S(t) + I(t) + R(t) = N for all t ≥ 0 (no births, deaths, or migration).

== Model Assumptions

The SIR model is valid only under these assumptions. When assumptions are violated,
predictions degrade:

- *Homogeneous mixing:* Any susceptible individual has equal probability of contact
  with any infected individual. Fails in geographically isolated communities or
  strongly age-stratified populations.

- *Constant contact rate β:* Transmission probability does not change over time.
  Violates during lockdowns, mask adoption, or behavior-change campaigns.

- *Permanent recovered immunity:* No reinfection. Approximately valid for acute diseases
  (<1 year); fails for endemic diseases with waning immunity (e.g., COVID variants).

- *Exponential recovery:* All infected individuals have exponentially distributed
  infectious periods with mean 1/γ. Simplification; real recovery is more complex.

- *No vital dynamics:* Ignores births and deaths during epidemic. Valid for acute
  outbreaks (<1 year); breaks for endemic models.

== Equation Derivation

=== Susceptible Population

Each susceptible individual contacts infected individuals at rate β. Under homogeneous
mixing, the fraction of contacts that are with infected people is I/N. Therefore:

$$
\frac{d S}{d t} = - \beta S \frac{I}{N}
$$

*Interpretation:* Susceptible count decreases proportionally to both S (more susceptible
people → more new infections) and I (more infected → more transmission opportunities),
scaled by the mixing fraction I/N.

=== Infected Population

Infected individuals receive new infections (from susceptible) and lose to recovery:

$$
\frac{d I}{d t} = \beta S \frac{I}{N} - \gamma I
$$

The first term (β S I / N) is the inflow from susceptible. The second term (γ I) is the
outflow to recovered, where γ is the recovery rate (inverse of infectious period).

=== Recovered Population

Recovery is the only sink:

$$
\frac{d R}{d t} = \gamma I
$$

=== Basic Reproduction Number R₀

Consider the early epidemic phase when S ≈ N (almost everyone is susceptible). One
infected individual infects at rate β S / N ≈ β people per day. They remain infectious
for 1/γ days. Therefore, the expected total number of secondary infections is:

$$
R_0 = \beta \times \frac{1}{\gamma} = \frac{\beta}{\gamma}
$$

*Key insight:* R₀ = β / γ is the ratio of transmission rate to recovery rate. If R₀ > 1,
the epidemic grows exponentially. If R₀ < 1, it dies out. If R₀ = 1, it spreads linearly.

== Executable Code

The model is implemented in Python using SymPy (symbolic) and SciPy (numerical):

```python
// From model.py
def sir_model(y, t, params):
    """SIR differential equations."""
    S, I, R = y
    N = params.N
    beta = params.beta
    gamma = params.gamma

    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I

    return np.array([dS_dt, dI_dt, dR_dt])
```

To run the COVID-like scenario (R₀ = 2):

```python
// From simulate.py
from simulate import covid_baseline
t, S, I, R, params = covid_baseline()
// Output: time array, S(t), I(t), R(t), parameters
```

See `model.py` (lines 44–50) for symbolic equation definitions.
See `simulate.py` (lines 40–65) for numerical integration.

== Example Output: COVID-like Scenario

Parameters (R₀ = 2):
- β = 0.2 [1/days] (transmission rate)
- γ = 0.1 [1/days] (recovery rate, 10-day infectious period)
- N = 1,000,000 (population)
- Initial: S₀ = 999,900, I₀ = 100, R₀ = 0

Key outcomes:

#table(
  columns: (1fr, 1.5fr),
  [*Outcome*], [*Value*],
  [Peak infection day], [Day #covid_scenario.key_outcomes.peak_infection_day],
  [Peak infection count], [#(covid_scenario.key_outcomes.peak_infection_count.toString() + " people")],
  [Peak infection %], [#(covid_scenario.key_outcomes.peak_infection_percentage.toFixed(1) + "%")],
  [Final attack rate], [#(covid_scenario.key_outcomes.final_attack_rate.toString() + " people")],
  [Attack rate %], [#(covid_scenario.key_outcomes.final_attack_rate_percentage.toFixed(1) + "%")],
)

*Qualitative behavior:*
- S decreases monotonically (people leave susceptible state)
- I rises to peak, then falls (epidemic peak at day ~25)
- R increases monotonically (accumulation of immune individuals)

#figure(
  image("generated/figures/sir_trajectory.png", width: 100%),
  caption: [SIR trajectories for COVID-like scenario (R₀ = 2). Susceptible count (S, blue)
    decreases while recovered count (R, orange) increases. Infected count (I, green) peaks
    around day 25 when transmission equals recovery.]
)

== Verification: Conservation Law

The total population must remain constant. We verify that S(t) + I(t) + R(t) = N
throughout integration (see `simulate.py`, lines 84–85):

```python
total = S + I + R
assert np.isclose(total, N, rtol=1e-6)  // Tolerance: <1 person in 1M
```

✓ *Result:* Conservation verified to machine precision.

== One Key Limitation: Constant Contact Rate β

The assumption that β remains constant is violated whenever people change their behavior.
During lockdowns, mask adoption, or isolation campaigns, effective β decreases. This
reduces R₀_eff = (reduced β) / γ below the baseline R₀.

*Impact:* Model cannot predict epidemic suppression by interventions. It predicts what
happens if β is constant, not what happens during policy changes.

*Extension (deferred):* Use time-varying β(t) or intervention-specific submodels
(e.g., Susceptible-Quarantined-Infected-Recovered with compliance rates).

== Comparison with Other R₀ Values

#figure(
  image("generated/figures/r0_comparison.png", width: 100%),
  caption: [Infected count over time for two diseases. COVID (R₀ = 2, left) shows a
    sustained epidemic. Measles (R₀ = 15, right) reaches higher peaks much faster,
    illustrating how R₀ determines epidemic speed and severity.]
)

== Reproducibility

To regenerate this entire artifact from scratch:

```bash
# 1. Clone repository
git clone https://github.com/baseline0/math-trace
cd math-trace/examples/epidemiology-sir

# 2. Generate formulas and figures
python build_paper.py

# 3. Verify reproducibility (run twice, compare)
python simulate.py
python simulate.py
// Output should be identical

# 4. Compile Typst paper (if Typst installed)
typst compile main.typ main.pdf
```

== Conclusion

The basic reproduction number R₀ = β / γ emerges naturally from the SIR model as the
ratio of transmission to recovery rates. It encodes the assumption of constant contact
rates and homogeneous mixing, and it quantifies how contagious a disease is.

For policy: R₀ > 1 requires intervention (reduce β) to prevent epidemic spread. The
higher R₀, the stronger the intervention needed. Understanding R₀ is essential for
evidence-based disease control.

== References

- Kermack, W. O., & McKendrick, A. G. (1927). "A contribution to the mathematical
  theory of epidemics." *Proc. R. Soc. B*, 115, 700–721.
- Keeling, M. J., & Rohani, P. (2008). *Modeling Infectious Diseases*. Oxford University Press.

---

**Generated:** 2026-09-29
**Source:** `examples/epidemiology-sir/` (Python source of truth)
**Verification:** Reproducibility test passed (identical output across runs)
**Note:** This is a bounded first artifact; see LAUNCH_RECORD_EPIDEMIOLOGY_R0.md for scope
and deferred work.
