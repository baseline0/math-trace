import GraphPolicy.Basic

/-!
# Lifecycle Module

Defines a simple state machine for graph‑policy lifecycle with evidence‑gated transitions.
-/

open List

namespace GraphPolicy.Lifecycle

/-- Inductive states of the policy lifecycle. -/
inductive State where
  | draft
  | ready_for_review
  | accepted_pending_integration
  | integration_authorized
  | verified
  | closed
  deriving DecidableEq, Repr

/-- Evidence items that gate transitions. -/
inductive Evidence where
  | none
  | review_submitted
  | human_approval
  | verification_pass
  deriving DecidableEq, Repr

/-- Transition relation between states, guarded by evidence. -/
inductive Step : State → Evidence → State → Prop where
  | submit : Step .draft .review_submitted .ready_for_review
  | accept : Step .ready_for_review .none .accepted_pending_integration
  | authorize : Step .accepted_pending_integration .human_approval .integration_authorized
  | verify : Step .integration_authorized .none .verified
  | close : Step .verified .verification_pass .closed

/-- Reachability of a target state from a source state via a list of evidence items. -/
inductive Reachable : State → State → List Evidence → Prop where
  | refl (s : State) : Reachable s s []
  | step {s₁ s₂ s₃ : State} {e : Evidence} {es : List Evidence} :
      Step s₁ e s₂ → Reachable s₂ s₃ es → Reachable s₁ s₃ (e :: es)

/-
  Monotonic phase rank used for structural reachability invariants.
-/
def State.rank : State → Nat
  | .draft => 0
  | .ready_for_review => 1
  | .accepted_pending_integration => 2
  | .integration_authorized => 3
  | .verified => 4
  | .closed => 5

/-
  Predicate characterizing an unmediated trace carrying no authorization or test evidence.
-/
def NoEvidence (es : List Evidence) : Prop :=
  ∀ e ∈ es, e = Evidence.none

/-
  Any trace crossing from rank ≤ 2 to rank ≥ 3 must contain `human_approval`.
-/
theorem reach_requires_human_approval (s₁ s₂ : State) (es : List Evidence)
    (h : Reachable s₁ s₂ es) (h₁ : s₁.rank ≤ 2) (h₂ : 3 ≤ s₂.rank) :
    Evidence.human_approval ∈ es := by
  induction h with
  | refl s =>
      cases s <;> simp [State.rank] at h₁ h₂
  | @step a b c e rest hstep hrest ih =>
      cases hstep with
      | submit =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | accept =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | authorize =>
          exact List.mem_cons_self _ _
      | verify =>
          simp [State.rank] at h₁
      | close =>
          simp [State.rank] at h₁

/-
  Any trace crossing from rank ≤ 4 to rank ≥ 5 must contain `verification_pass`.
-/
theorem reach_requires_verification_pass (s₁ s₂ : State) (es : List Evidence)
    (h : Reachable s₁ s₂ es) (h₁ : s₁.rank ≤ 4) (h₂ : 5 ≤ s₂.rank) :
    Evidence.verification_pass ∈ es := by
  induction h with
  | refl s =>
      cases s <;> simp [State.rank] at h₁ h₂
  | @step a b c e rest hstep hrest ih =>
      cases hstep with
      | submit =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | accept =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | authorize =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | verify =>
          exact List.mem_cons_of_mem _ (ih (by simp [State.rank]) h₂)
      | close =>
          exact List.mem_cons_self _ _

/-
  Positive necessity theorem: reaching `closed` from `draft` requires both gates.
-/
theorem closed_requires_evidence {es : List Evidence}
    (h : Reachable State.draft State.closed es) :
    Evidence.human_approval ∈ es ∧ Evidence.verification_pass ∈ es := by
  refine ⟨?_, ?_⟩
  · exact reach_requires_human_approval State.draft State.closed es h (by simp [State.rank]) (by simp [State.rank])
  · exact reach_requires_verification_pass State.draft State.closed es h (by simp [State.rank]) (by simp [State.rank])

/-
  Non-bypassability theorem: an unmediated trace can never reach `closed` from `draft`.
-/
theorem unmediated_cannot_reach_closed (es : List Evidence)
    (h_no : NoEvidence es) :
    ¬ Reachable State.draft State.closed es := by
  intro h_reach
  have h_app := (closed_requires_evidence h_reach).1
  have h_eq := h_no .human_approval h_app
  cases h_eq

end GraphPolicy.Lifecycle

/--
  Theorem: any trace that reaches `closed` from `draft` must contain both
  `human_approval` and `verification_pass` evidence items.
-/
theorem unmediated_cannot_reach_closed (es : List Evidence)
    (h : Reachable .draft .closed es) :
    Evidence.human_approval ∈ es ∧ Evidence.verification_pass ∈ es := by
  induction h with
  | refl _ =>
      -- impossible: `draft` ≠ `closed`
      cases rfl
  | step step_h ih =>
      cases step_h with
      | submit =>
          -- transition uses `review_submitted`, does not affect the needed evidence
          exact ih
      | accept =>
          exact ih
      | authorize =>
          -- this step adds `human_approval`
          have hp : Evidence.human_approval ∈ (Evidence.human_approval :: _) := by
            simp
          have vp := ih.right
          exact And.intro hp vp
      | verify =>
          -- this step adds no new evidence for `human_approval`
          exact ih
      | close =>
          -- this step adds `verification_pass`
          have vp : Evidence.verification_pass ∈ (Evidence.verification_pass :: _) := by
            simp
          have hp := ih.left
          exact And.intro hp vp

end GraphPolicy.Lifecycle