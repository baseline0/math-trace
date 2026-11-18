import GraphPolicy.Basic

namespace GraphPolicy.Lifecycle

/-- Operational states of a governed SDLC workflow artifact. -/
inductive State
  | draft
  | ready_for_review
  | accepted_pending_integration
  | integration_authorized
  | verified
  | closed
  deriving DecidableEq, Repr

/-- Monotonic phase rank used for structural reachability invariants. -/
def State.rank : State → Nat
  | .draft => 0
  | .ready_for_review => 1
  | .accepted_pending_integration => 2
  | .integration_authorized => 3
  | .verified => 4
  | .closed => 5

/-- Evidence tokens required to authorize state transitions. -/
inductive Evidence
  | none
  | review_submitted
  | human_approval
  | verification_pass
  deriving DecidableEq, Repr

/-- Small-step transition relation enforcing evidence gates. -/
inductive Step : State → Evidence → State → Prop
  | submit :
      Step .draft .review_submitted .ready_for_review
  | accept :
      Step .ready_for_review .none .accepted_pending_integration
  | authorize :
      Step .accepted_pending_integration .human_approval .integration_authorized
  | verify :
      Step .integration_authorized .none .verified
  | close :
      Step .verified .verification_pass .closed

/-- Multi-step execution trace accumulating emitted evidence tokens. -/
inductive Reachable : State → State → List Evidence → Prop
  | refl (s : State) :
      Reachable s s []
  | step {s₁ s₂ s₃ : State} {e : Evidence} {es : List Evidence} :
      Step s₁ e s₂ → Reachable s₂ s₃ es → Reachable s₁ s₃ (e :: es)

/-- Predicate characterizing an unmediated trace carrying no authorization or test evidence. -/
def NoEvidence (es : List Evidence) : Prop :=
  ∀ e ∈ es, e = Evidence.none

/-- Any trace crossing from rank ≤ 2 to rank ≥ 3 must contain `human_approval`. -/
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
          exact List.mem_cons_self
      | verify =>
          simp [State.rank] at h₁
      | close =>
          simp [State.rank] at h₁

/-- Any trace crossing from rank ≤ 4 to rank ≥ 5 must contain `verification_pass`. -/
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
          exact List.mem_cons_self

/-- Positive necessity theorem: reaching `closed` from `draft` requires both gates. -/
theorem closed_requires_evidence {es : List Evidence}
    (h : Reachable State.draft State.closed es) :
    Evidence.human_approval ∈ es ∧ Evidence.verification_pass ∈ es := by
  refine ⟨?_, ?_⟩
  · exact reach_requires_human_approval State.draft State.closed es h (by simp [State.rank]) (by simp [State.rank])
  · exact reach_requires_verification_pass State.draft State.closed es h (by simp [State.rank]) (by simp [State.rank])

/-- Non-bypassability theorem: an unmediated trace can never reach `closed` from `draft`. -/
theorem unmediated_cannot_reach_closed (es : List Evidence)
    (h_no : NoEvidence es) :
    ¬ Reachable State.draft State.closed es := by
  intro h_reach
  have h_app := (closed_requires_evidence h_reach).1
  have h_eq := h_no _ h_app
  cases h_eq

end GraphPolicy.Lifecycle