import Mathlib.Tactic.FinCases
import Mathlib.Data.Fin.VecNotation
import GraphPolicy.Induced
import GraphPolicy.Guarded

/-!
# Concrete examples

- `chain` is the forbidden pattern `H`: a path on three vertices, edges 0–1 and 1–2.
- `chainPlusApproval` is `H` plus vertex 3 adjacent to the middle vertex 1. The
  extra vertex lies outside the copy and stands in for an approval-like context.
  It contains `chain` induced, with witness `![0, 1, 2]`.
- `emptyThree` has no edges on three vertices, so it contains no induced copy of
  `chain` and the pure policy accepts it.

No `decide` is used on graphs. Adjacency is reasoned about by `simp` after
`fin_cases`, and injectivity by `decide` on the explicit three-element witness.
-/

namespace GraphPolicy.Examples

open GraphPolicy

/-- Forbidden pattern: the path 0–1–2 on three vertices. -/
def chain : SimpleGraph (Fin 3) :=
  SimpleGraph.fromRel (fun a b : Fin 3 => a.val + 1 = b.val)

/-- The path 0–1–2 plus vertex 3 adjacent to vertex 1. -/
def chainPlusApproval : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel
    (fun a b : Fin 4 => (a = 0 ∧ b = 1) ∨ (a = 1 ∧ b = 2) ∨ (a = 1 ∧ b = 3))

/-- No edges on three vertices. -/
def emptyThree : SimpleGraph (Fin 3) := ⊥

/-- The pattern contains itself, with the identity as witness. -/
theorem chain_induces_chain : InducedContains chain chain :=
  ⟨id, Function.injective_id, fun _ _ => Iff.rfl⟩

/-- The witness `![0, 1, 2]` embeds `chain` into `chainPlusApproval`; the
extra vertex 3 is outside the image and does not disturb the copy. -/
theorem approval_induces_chain : InducedContains chainPlusApproval chain := by
  refine ⟨![0, 1, 2], ?_, ?_⟩
  · decide
  · intro a b
    fin_cases a <;> fin_cases b <;>
      simp [chain, chainPlusApproval, SimpleGraph.fromRel_adj]

/-- The empty graph on three vertices does not contain the path, since the
path has the edge 0–1 and the empty graph has none. The pure policy accepts it. -/
theorem emptyThree_pure_accepts : PurePolicyAccepts emptyThree chain := by
  unfold PurePolicyAccepts
  rintro ⟨f, -, hf⟩
  have h01 : chain.Adj 0 1 := by simp [chain, SimpleGraph.fromRel_adj]
  have h := (hf 0 1).mp h01
  simp [emptyThree] at h

/-- The pure policy rejects `chainPlusApproval` (it contains the pattern). -/
theorem approval_pure_rejects : ¬ PurePolicyAccepts chainPlusApproval chain := by
  unfold PurePolicyAccepts
  exact fun h => h approval_induces_chain

/-- Guarded policy with no approval still rejects a forbidden graph. -/
theorem chain_guarded_rejects_unapproved :
    ¬ GuardedPolicyAccepts chain chain (fun _ => False) := by
  unfold GuardedPolicyAccepts
  rintro (h | h)
  · exact h chain_induces_chain
  · exact h

/-- Guarded policy accepts `chainPlusApproval` when its approval holds. -/
theorem approval_guarded_accepts :
    GuardedPolicyAccepts chainPlusApproval chain (fun G => G = chainPlusApproval) :=
  Or.inr rfl

end GraphPolicy.Examples
