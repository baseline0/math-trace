import Mathlib

/-!
Stochastic P-system: Formal model of the monotonicity theorem.

This file contains the theorem statement exactly as it appears in the paper
(see main.typ, Theorem 1).

The formal challenge: Prove that the rate law r(n_a) = k * n_a * (n_a - 1) / 2
is strictly increasing for k > 0 and n_a ≥ 2.

Source of truth: examples/membrane-dynamics/model.py:25
-/

noncomputable section

open Nat Real

/-- Rate function for rule 2a → b under mass-action kinetics.
    Corresponds to model.py:25: r = k * n_a * (n_a - 1) / 2

    This is the rate of the transition 2a → b as a function of the
    count of `a` objects and the rate constant k.
-/
def rate (k : ℝ) (n : ℕ) : ℝ :=
  k * (n : ℝ) * ((n : ℝ) - 1) / 2

/-- For k > 0, the rate function is strictly increasing for n ≥ 2.

    Theorem statement from paper (main.typ): "Let k > 0. For integers n_a ≥ 2,
    the function r(n_a) = (k n_a (n_a - 1)) / 2 is strictly increasing in n_a."

    Proof strategy:
    1. Show that rate is defined and positive for all k > 0, n ≥ 2
    2. Show that ∀ n ≥ 2, rate(k)(n+1) - rate(k)(n) = k * n > 0
    3. Conclude strict monotonicity
-/
theorem rate_strictly_increasing (k : ℝ) (hk : 0 < k) :
    ∀ n m : ℕ, 2 ≤ n → n < m → rate k n < rate k m := by
  sorry

/-- Helper lemma: consecutive differences.
    For any k > 0 and n ≥ 2, the rate increases by exactly k*n
    when n advances by 1.
-/
lemma rate_step_difference (k : ℝ) (hk : 0 < k) (n : ℕ) (hn : 2 ≤ n) :
    rate k (n + 1) - rate k n = k * (n : ℝ) := by
  sorry

/-- Immediate corollary: rate is positive on increasing integers.
-/
lemma rate_positive_step (k : ℝ) (hk : 0 < k) (n : ℕ) (hn : 2 ≤ n) :
    0 < rate k (n + 1) - rate k n := by
  rw [rate_step_difference k hk n hn]
  positivity

end
