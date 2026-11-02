import GraphPolicy.Induced

/-!
# Pure and guarded policies

A pure policy rejects any graph that contains the forbidden pattern `H` as an
induced subgraph. `PurePolicyAccepts` is the negation of `InducedContains`.

A guarded policy adds an approval context `Approved : SimpleGraph V → Prop`.
It rejects a graph only when the graph is forbidden and not approved:
`GuardedPolicyAccepts G H Approved` is `¬ InducedContains G H ∨ Approved G`.

This is the corrected logic. The approval is a predicate on the whole graph,
not on the copy, so it can only add acceptance: it never removes a pure
acceptance, and a graph with no induced copy of `H` is accepted whatever
`Approved` says. The guard is a relaxation of the pure policy, and every
graph that the pure policy accepts is accepted by the guarded one.
-/

namespace GraphPolicy

variable {V W : Type}

/-- A pure policy accepts `G` exactly when `G` does not contain `H` induced. -/
def PurePolicyAccepts (G : SimpleGraph V) (H : SimpleGraph W) : Prop :=
  ¬ InducedContains G H

/-- A guarded policy accepts `G` when `G` does not contain `H` induced, or when
the approval context `Approved` holds for `G`. It rejects iff `G` contains `H`
and `G` is not approved. -/
def GuardedPolicyAccepts (G : SimpleGraph V) (H : SimpleGraph W)
    (Approved : SimpleGraph V → Prop) : Prop :=
  ¬ InducedContains G H ∨ Approved G

end GraphPolicy
