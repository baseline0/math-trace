#set page(paper: "a4", margin: 2.5cm)
#set text(font: "New Computer Modern", size: 11pt)
#set heading(numbering: "1.")

// Load generated formulas
#let formulas = include "generated/formulas.typ"

= A minimal stochastic P-system

We consider a one-membrane P system with a single rewriting rule over a
homogeneous population of objects. This minimal model illustrates the
connection between formal theory, numerical simulation, and mathematical
formalization.

== The model

The rewriting rule is:

#align(center, text(size: 14pt, weight: "bold", `2a → b`))

Under a stochastic mass-action approximation, the expected transition rate
depends on the combinatorial count of unordered pairs of `a` objects at any time $t$.

Let $n_a(t)$ be the number of `a` objects at time $t$. The rate of the
reaction $2a → b$ is given by:

#figure(
  align(center, text(size: 12pt, formulas)),
  caption: [Rate law for rule $2a → b$ derived from mass-action kinetics (see model.py:25)],
) <eq-rate>

This formula is computed symbolically from the Python model using SymPy and
verified in formal logic via Lean.

== The monotonicity theorem

We establish a key property of the rate function:

*Theorem 1 (Monotonicity).* _Let $k > 0$. For integers $n_a ≥ 2$, the function_
$ r(n_a) = (k n_a (n_a - 1)) / 2 $
_is strictly increasing in $n_a$._

*Proof sketch.* For consecutive values, write:
$ r(n_a + 1) - r(n_a) = (k(n_a + 1)n_a) / 2 - (k n_a(n_a - 1)) / 2 = k n_a $

Since $k > 0$ and $n_a ≥ 2$, we have $r(n_a + 1) - r(n_a) > 0$, so the rate
is strictly increasing. □

This theorem is formalized in Lean (see Section 5) and registered in the
Palomar formalization registry.

== Stochastic simulation

We simulate the system under stochastic mass-action kinetics using the
Gillespie algorithm with fixed time steps. Figure 1 shows a representative
trajectory for $k = 0.01$, $n_a(0) = 50$.

#figure(
  image("generated/figures/simulation.png", width: 85%),
  caption: [
    Stochastic trajectory of $n_a(t)$ for rule $2a → b$ with
    rate constant $k = 0.01$, initial count $n_a(0) = 50$, over 200 time steps
    of $Δ t = 0.1$. The monotonicity property is evident in the decreasing trend
    of the reaction rate as the population of `a` objects shrinks. Source: simulate.py.
  ],
) <fig-sim>

== Code traceability

Every formula, theorem statement, and simulation parameter is linked to its
source in the codebase:

- *model.py:25* — SymPy definition of the rate law (source of truth)
- *simulate.py* — Stochastic realization using numpy
- *build_paper.py* — Automated pipeline (formulas → figures → PDF)
- *lean\/* — Formal development and Palomar registration

Users can inspect `model.py` to verify the rate formula, modify simulation
parameters in `simulate.py`, or extend the Lean proof in `lean/Solution.lean`.

== Formalization and verification

Theorem 1 is formalized in Lean 4 using the Mathlib standard library.
The formal proof verifies that for any positive real $k$ and positive integers
$n_a$, the rate function is strictly increasing.

The formal development follows the paper structure:

```
lean/Challenge.lean      — Theorem statement (matches paper exactly)
lean/Solution.lean       — Full formal proof
lean/comparator.json     — Verification against paper statement
lean/formalization.yaml  — Metadata and Palomar registration
```

The registered entry in the Palomar formalization registry provides a persistent,
verifiable link between this published paper and its formal proof.

For the code and proofs, visit:
#align(center, text(size: 10pt, `https://github.com/baseline0/math-trace/tree/main/examples/membrane-dynamics`))

== References

- Păun, Gh. (2000). _Computing with membranes_. Journal of Computer and System Sciences 61(1):108–143.
- Gillespie, D. T. (1977). _Exact stochastic simulation of coupled chemical reactions_. J. Phys. Chem. 81(25):2340–2361.
- Avigad, J., et al. (2015). _Logic and Proof_. CMU Open Learning Initiative.
