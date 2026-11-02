import GraphPolicy.Induced

/-!
# Preservation of induced copies

If `G₁` has an induced copy of `H` along `f`, and `G₂` agrees with `G₁` on every
pair of copy vertices, then `G₂` has the same induced copy. Approval structure
outside the copy cannot erase the forbidden induced pattern.

The hypothesis `h_agree` ranges only over pairs in `Set.range f`. It therefore
covers edges changed between copy vertices, which are the only edges that can
affect the copy, and it places no constraint on edges changed outside the copy.
Only copy-internal adjacency matters for the copy.
-/

namespace GraphPolicy

variable {V W : Type}

/-- Preservation: an induced copy of `H` along `f` in `G₁` remains an induced
copy along `f` in `G₂`, provided `G₁` and `G₂` agree on every pair of vertices
in the copy `Set.range f`. Injectivity does not depend on the graph, and each
adjacency `H.Adj a b ↔ G.Adj (f a) (f b)` is transported across the agreement
on the pair `(f a, f b)`, which lies in `Set.range f`. -/
theorem induced_copy_preserved {V W : Type} (G₁ G₂ : SimpleGraph V) (H : SimpleGraph W) (f : W → V)
    (hf : InducedCopy G₁ H f)
    (h_agree : ∀ x y : V, x ∈ Set.range f → y ∈ Set.range f → (G₁.Adj x y ↔ G₂.Adj x y)) :
    InducedCopy G₂ H f :=
  ⟨hf.1, fun a b => (hf.2 a b).trans (h_agree _ _ ⟨a, rfl⟩ ⟨b, rfl⟩)⟩

/-- Corollary: if `G₁` contains `H` induced and `G₂` agrees with `G₁` on the
vertices of that copy, then `G₂` contains `H` induced. Approval structure outside
the copy cannot erase the forbidden induced pattern. -/
theorem induced_contains_preserved {V W : Type} (G₁ G₂ : SimpleGraph V) (H : SimpleGraph W) (f : W → V)
    (hf : InducedCopy G₁ H f)
    (h_agree : ∀ x y : V, x ∈ Set.range f → y ∈ Set.range f → (G₁.Adj x y ↔ G₂.Adj x y)) :
    InducedContains G₂ H :=
  ⟨f, induced_copy_preserved G₁ G₂ H f hf h_agree⟩

end GraphPolicy
