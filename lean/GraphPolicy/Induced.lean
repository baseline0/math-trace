import Mathlib.Combinatorics.SimpleGraph.Basic

/-!
# Induced containment

An induced copy of `H` in `G` is an injective map `f : W → V` that preserves
adjacency and non-adjacency in both directions. The copy's vertex set is
`Set.range f`. Because the biconditional also covers non-edges, the copy is
induced: an edge of `G` between two image vertices must come from an edge of `H`.

The definition is explicit rather than Mathlib's `Subgraph` notation, so a
witness is a plain function and examples are proved by exhibiting it.
-/

namespace GraphPolicy

variable {V W : Type}

/-- `f` embeds `H` into `G` as an induced subgraph: injective, and adjacency
on `W` matches adjacency of the images in `G`. -/
def InducedCopy (G : SimpleGraph V) (H : SimpleGraph W) (f : W → V) : Prop :=
  Function.Injective f ∧ ∀ a b : W, H.Adj a b ↔ G.Adj (f a) (f b)

/-- `G` contains `H` as an induced subgraph, i.e. some `f` is an induced copy. -/
def InducedContains (G : SimpleGraph V) (H : SimpleGraph W) : Prop :=
  ∃ f : W → V, InducedCopy G H f

end GraphPolicy
