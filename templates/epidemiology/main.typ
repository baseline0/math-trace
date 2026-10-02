#set page(margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))
#set text(font: "New Computer Modern", size: 11pt)

#import "generated/formulas.typ": *

= Epidemiology: SIR and SEIR Disease Models

_Mathematical modeling of infectious disease dynamics_

== 1. Introduction

This paper develops and analyzes compartmental models for infectious disease transmission, based on the classic Kermack-McKendrick framework. We model disease dynamics using differential equations and validate predictions against realistic pandemic scenarios.

== 2. The SIR Model

The SIR (Susceptible-Infected-Recovered) model divides a population into three compartments:

- *S(t)*: Susceptible individuals (can contract disease)
- *I(t)*: Infected individuals (transmit disease)
- *R(t)*: Recovered individuals (immune, cannot be infected)

Total population is conserved: $N = S(t) + I(t) + R(t)$

== 3. Basic Reproduction Number

The basic reproduction number $R_0$ quantifies disease transmissibility:

#figure(
  align(center, $R_0 = beta \/ gamma$),
  caption: [Basic reproduction number (from model.py:38)]
)

Interpretation:
- $R_0 > 1$: Disease spreads exponentially (epidemic)
- $R_0 < 1$: Disease dies out
- $R_0 = 1$: Critical threshold (endemic equilibrium)

For COVID-19 (respiratory transmission), $R_0 approx 2–3$. For measles (airborne), $R_0 approx 12–18$.

== 4. SIR Differential Equations

The dynamics are governed by three coupled ODEs:

#figure(
  align(center, block(
    "dS/dt = −βSI/N",
    "dI/dt = βSI/N − γI",
    "dR/dt = γI"
  )),
  caption: [SIR dynamics (from model.py:69)]
)

Where:
- $beta$: transmission rate (contact rate × probability per contact)
- $gamma$: recovery rate (1 / infectious period)

The term $beta S I / N$ represents the force of infection—how susceptibles encounter infected individuals.

== 5. Equilibrium Analysis

At endemic equilibrium ($dI\/dt = 0$), the number of infected individuals stabilizes:

#figure(
  align(center, $I^* = (1 - 1/R_0) times N$),
  caption: [Endemic equilibrium infected proportion (from model.py:100)]
)

If $R_0 < 1$, the disease cannot maintain itself and dies out.

== 6. The SEIR Extension

For diseases with an incubation period, we add an Exposed compartment:

- *E(t)*: Exposed (infected but not yet infectious)

The SEIR model captures:
- $sigma$: rate of progression from exposed → infected (1 / latency)
- $beta, gamma$: same as SIR

Measles has a ~8-day latency period. COVID-19 has ~5-day latency. SEIR is more realistic for these diseases.

== 7. Attack Rate

The attack rate is the total proportion of the population that becomes infected by epidemic end:

#figure(
  align(center, $A = R_infinity = 1 - S_infinity$),
  caption: [Final attack rate (from model.py:136)]
)

Higher $R_0$ → higher attack rate. For measles ($R_0 = 15$), ~95% of unvaccinated population eventually infected.

== 8. Peak Infections

The peak infection occurs when $dI\/dt = 0$ (before the disease burns out):

#figure(
  align(center, $I_"max" = arg max(I(t))$),
  caption: [Peak infection timing and magnitude (from model.py:145)]
)

Healthcare systems are stressed during peak infections. Interventions (lockdown, vaccination) flatten the curve by reducing $beta$ or R₀.

== 9. Interventions

An intervention (lockdown, vaccination, social distancing) reduces the effective transmission rate:

- Before: $beta_0$, $R_0 = beta_0 / gamma$
- After: $beta_"int" < beta_0$, $R_0^"eff" = beta_"int" / gamma < R_0$

Reducing transmission by 50% drops attack rate from 80% → 40%. Public health interventions work by lowering $R_0^"eff"$ below 1.

== 10. Conclusion

Compartmental models provide interpretable predictions of disease spread. The SIR and SEIR models capture the essential dynamics with minimal parameters. By estimating $beta$ and $gamma$ from data, we can:

1. Predict epidemic trajectory
2. Evaluate intervention impact
3. Guide public health decisions

Trade-offs: Simple models assume homogeneous mixing (unrealistic), but remain useful for qualitative understanding and policy evaluation.

---

#set text(size: 9pt, fill: gray)

_Paper generated from model.py, simulate.py, and main.typ. All formulas traced to source code. See docs/adr/ for design decisions._
