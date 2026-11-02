import GraphPolicy.Induced
import GraphPolicy.Guarded
import GraphPolicy.Preservation
import GraphPolicy.Examples

/-!
# Separation of pure and guarded policies

A forbidden family is an indexed family of patterns `Hf i : SimpleGraph (Wt i)`.
A pure family policy rejects a graph as soon as some pattern of the family occurs
in it as an induced subgraph. A guarded family policy adds an approval predicate
`Approved` on whole graphs and rejects a graph only when some pattern occurs in it
and the graph is not approved.

The main theorem `forbidden_induced_cannot_express_conditional_approval` shows that
no pure family can express this conditional approval. Suppose `G₁` contains the
forbidden pattern `Hf i₀` along `f`, and `G₂` agrees with `G₁` on the vertices of
that copy, while `G₂` is approved and `G₁` is not. Then the copy survives in `G₂`
by `induced_contains_preserved`, so every pure policy over the family rejects `G₂`
as well as `G₁`. Approval of `G₂` lies outside the copy and cannot help a pure
policy. Only the guarded policy accepts `G₂` and rejects `G₁`.

The theorem holds for an arbitrary index type `ι` and arbitrary pattern sizes
`Wt i`. The only property of `Hf i₀` used is that it occurs in `G₁`.
-/

namespace GraphPolicy

variable {ι : Type} {Wt : ι → Type} (Hf : (i : ι) → SimpleGraph (Wt i))

variable {V : Type}

/-- A pure family policy accepts `G` when no pattern of the family occurs in `G`
as an induced subgraph. -/
def PureFamilyAccepts (G : SimpleGraph V) : Prop :=
  ∀ i, ¬ InducedContains G (Hf i)

/-- A guarded family policy accepts `G` when the pure family accepts it, or when
the approval predicate `Approved` holds for `G`. It rejects `G` iff some pattern
occurs in `G` and `G` is not approved. -/
def GuardedFamilyAccepts (G : SimpleGraph V) (Approved : SimpleGraph V → Prop) : Prop :=
  PureFamilyAccepts Hf G ∨ Approved G

/-- Separation: if `G₁` contains the forbidden pattern `Hf i₀` along `f`, and `G₂`
agrees with `G₁` on the copy vertices, then `G₂` is rejected by every pure family
policy as well. With `G₂` approved and `G₁` unapproved, the guarded policy accepts
`G₂` and rejects `G₁`. So no pure family accepts `G₂` while rejecting `G₁`. -/
theorem forbidden_induced_cannot_express_conditional_approval
    (G₁ G₂ : SimpleGraph V) (Approved : SimpleGraph V → Prop) (i₀ : ι) (f : Wt i₀ → V)
    (hf : InducedCopy G₁ (Hf i₀) f)
    (h_agree : ∀ x y : V, x ∈ Set.range f → y ∈ Set.range f → (G₁.Adj x y ↔ G₂.Adj x y))
    (h_approved : Approved G₂)
    (h_unapproved : ¬ Approved G₁) :
    ¬ PureFamilyAccepts Hf G₁ ∧ ¬ PureFamilyAccepts Hf G₂ ∧
      (GuardedFamilyAccepts Hf G₂ Approved ∧ ¬ GuardedFamilyAccepts Hf G₁ Approved) :=
  have hc₁ : InducedContains G₁ (Hf i₀) := ⟨f, hf⟩
  have hc₂ : InducedContains G₂ (Hf i₀) := induced_contains_preserved G₁ G₂ (Hf i₀) f hf h_agree
  ⟨fun h => h i₀ hc₁, fun h => h i₀ hc₂, Or.inr h_approved,
    fun h => Or.elim h (fun hp => hp i₀ hc₁) h_unapproved⟩

/-- Corollary: under the same hypotheses, no pure family accepts `G₂` while
rejecting `G₁`. The pure family rejects `G₂` by the main theorem, so it cannot
accept `G₂` at all. -/
theorem no_pure_family_separates
    (G₁ G₂ : SimpleGraph V) (Approved : SimpleGraph V → Prop) (i₀ : ι) (f : Wt i₀ → V)
    (hf : InducedCopy G₁ (Hf i₀) f)
    (h_agree : ∀ x y : V, x ∈ Set.range f → y ∈ Set.range f → (G₁.Adj x y ↔ G₂.Adj x y))
    (h_approved : Approved G₂)
    (h_unapproved : ¬ Approved G₁) :
    ¬ (PureFamilyAccepts Hf G₂ ∧ ¬ PureFamilyAccepts Hf G₁) :=
  fun h =>
    (forbidden_induced_cannot_express_conditional_approval Hf G₁ G₂ Approved i₀ f hf h_agree
      h_approved h_unapproved).2.1 h.1

namespace Examples

open GraphPolicy.Examples

/-- `chainPlusApproval` with the extra edge 2–3, which lies outside the copy
`![0, 1, 2]`. It contains `chain` induced and is not equal to `chainPlusApproval`. -/
def chainPlusExtraEdge : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel
    (fun a b : Fin 4 => (a = 0 ∧ b = 1) ∨ (a = 1 ∧ b = 2) ∨ (a = 1 ∧ b = 3) ∨ (a = 2 ∧ b = 3))

/-- The chain pattern as a one-element family, applied to the pair
`chainPlusExtraEdge` (unapproved) and `chainPlusApproval` (approved). The copy
`![0, 1, 2]` is the same in both graphs, since they differ only on the pair 2–3. -/
theorem chain_family_separation :
    ¬ PureFamilyAccepts (Wt := fun _ : Unit => Fin 3) (fun _ => chain) chainPlusExtraEdge ∧
      ¬ PureFamilyAccepts (Wt := fun _ : Unit => Fin 3) (fun _ => chain) chainPlusApproval ∧
      (GuardedFamilyAccepts (Wt := fun _ : Unit => Fin 3) (fun _ => chain) chainPlusApproval
          (fun G => G = chainPlusApproval) ∧
        ¬ GuardedFamilyAccepts (Wt := fun _ : Unit => Fin 3) (fun _ => chain) chainPlusExtraEdge
          (fun G => G = chainPlusApproval)) :=
  forbidden_induced_cannot_express_conditional_approval (fun _ => chain) chainPlusExtraEdge
    chainPlusApproval (fun G => G = chainPlusApproval) () ![0, 1, 2]
    ⟨by decide, by
      intro a b
      fin_cases a <;> fin_cases b <;>
        simp [chain, chainPlusExtraEdge, SimpleGraph.fromRel_adj]⟩
    (by
      intro x y hx hy
      obtain ⟨a, rfl⟩ := hx
      obtain ⟨b, rfl⟩ := hy
      fin_cases a <;> fin_cases b <;>
        simp [chainPlusExtraEdge, chainPlusApproval, SimpleGraph.fromRel_adj])
    rfl
    (by
      intro h
      have h23 := congrArg (fun G : SimpleGraph (Fin 4) => G.Adj 2 3) h
      simp [chainPlusExtraEdge, chainPlusApproval, SimpleGraph.fromRel_adj] at h23)

end Examples

end GraphPolicy
