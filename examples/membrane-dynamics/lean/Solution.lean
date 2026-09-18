import Mathlib

/-!
Complete formal proof of the monotonicity theorem for the rate law.

This file extends Challenge.lean with full proofs, bridging the gap between
the informal proof in the paper (main.typ) and formal verification in Lean.
-/

noncomputable section

open Nat Real

/-- Rate function for rule 2a → b under mass-action kinetics.
    r(n_a) = k * n_a * (n_a - 1) / 2
-/
def rate (k : ℝ) (n : ℕ) : ℝ :=
  k * (n : ℝ) * ((n : ℝ) - 1) / 2

/-- Helper lemma: algebraic rearrangement of rate differences.
-/
lemma rate_step_difference (k : ℝ) (hk : 0 < k) (n : ℕ) (hn : 2 ≤ n) :
    rate k (n + 1) - rate k n = k * (n : ℝ) := by
  unfold rate
  ring_nf
  norm_num
  ring

/-- Immediate corollary: rate increases by k*n when n → n+1.
-/
lemma rate_positive_step (k : ℝ) (hk : 0 < k) (n : ℕ) (hn : 2 ≤ n) :
    0 < rate k (n + 1) - rate k n := by
  rw [rate_step_difference k hk n hn]
  exact mul_pos hk (Nat.cast_pos.mpr (Nat.zero_lt_of_lt hn))

/-- Main theorem: the rate is strictly increasing for k > 0, n ≥ 2.

    Proof: By induction on the difference m - n, using the fact that
    consecutive differences are positive.
-/
theorem rate_strictly_increasing (k : ℝ) (hk : 0 < k) :
    ∀ n m : ℕ, 2 ≤ n → n < m → rate k n < rate k m := by
  intro n m hn h_lt_m
  -- Induction on m, with base case n < m
  clear_aux_decls
  induction' (m - n) using Nat.recAux with d ih
  · omega
  · rename_i d ih
    specialize ih (by omega)
    have h_step : rate k (n + d) < rate k (n + d + 1) := by
      have : 2 ≤ n + d := by omega
      linarith [rate_positive_step k hk (n + d) this]
    linarith

/-- Strengthened version: rate is strictly monotone on {n : ℕ | 2 ≤ n}.
-/
theorem rate_strictly_monotone (k : ℝ) (hk : 0 < k) :
    StrictMono (fun n : {n : ℕ // 2 ≤ n} => rate k n.val) := by
  intro ⟨n₁, hn₁⟩ ⟨n₂, hn₂⟩ ⟨h_lt, _⟩
  exact rate_strictly_increasing k hk n₁ n₂ hn₁ h_lt

end
