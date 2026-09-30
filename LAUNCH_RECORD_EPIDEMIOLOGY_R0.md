# EPIDEMIOLOGY-R0-REFERENCE: Delivery Lane Launch Record

**WorkItem:** MATH-TRACE-EPIDEMIOLOGY-DELIVERY-001  
**Lane:** End-user delivery (Step 8)  
**Date:** 2026-09-29  
**Owner:** Claude Haiku 4.5  
**Repository:** math-trace  

---

## Isolation & Identity

**Repository Path:** `/home/mark/projects/math-trace`  
**Worktree Path:** `/tmp/epi-delivery-worktree`  
**Branch:** `epidemiology-r0-reference`  
**Base SHA:** `3cdddde` (docs: Add Week 1 contract freeze for AGMAI engagement)  
**Scope Authority:** MATH-TRACE-EPIDEMIOLOGY-DELIVERY-001 + EPIDEMIOLOGY-GOLDEN-PATH.md  

---

## User Question & Scope

**User Question (Core):**
> How does the basic reproduction number R₀ arise in a simple SIR model, what assumptions does it encode, and how does it relate to the model equations?

**Scope: Bounded First Artifact**

This is NOT the full epidemiology golden path (10 sections, 3500–4000 words, weeks of work). This is a **focused, end-user-consumable reference artifact** that demonstrates:

1. ✅ Problem statement: Why R₀ matters for disease control
2. ✅ Assumptions: Explicit list (homogeneous mixing, no behavior change, constant contact rate)
3. ✅ Variable definitions: Table with units and domains (S, I, R, N, β, γ, R₀)
4. ✅ Equation derivation: How R₀ arises from β/γ
5. ✅ Executable code: Working SIR model that students can run
6. ✅ Example output: COVID-like scenario with R₀=2
7. ✅ One key limitation: Assumes constant contact rate (breaks during lockdowns)

**Deferred (Not in this artifact):**
- Historical provenance (Kermack 1927)
- Full dimensional analysis
- Comprehensive test suite
- Known limitations table (limiting to one key case)
- Lean formalization
- Multiple scenarios

---

## Mutable Resources

- `examples/epidemiology-sir/` — New example directory
  - `model.py` — SIR equations (SymPy)
  - `simulate.py` — Integration and scenario
  - `main.typ` — Typst paper
  - `build_paper.py` — Build pipeline

- `examples/epidemiology-sir/generated/` — Auto-generated (not committed)
  - `sir_equations.json`
  - `figures/sir_trajectory.png`
  - `main.pdf`

---

## Output & Deliverable

**Final artifact:** `examples/epidemiology-sir/main.pdf`

**Approval gate (Human decision):**
- Is the paper technically accurate? (Equations match code?)
- Is it understandable to a reader unfamiliar with epidemiology?
- Does the code run without errors?
- Is the example output sensible (COVID-like scenario)?

**Acceptance:** Human review → explicit approve/defer/reject decision

---

## Source/Citation Plan

**Code sources:**
- SymPy formulas in `model.py` (owned, first principles)
- Differential equation solver: scipy.integrate.odeint (standard library)

**Citation sources (for paper):**
- Kermack & McKendrick 1927 (original SIR)
- Keeling & Rohani 2008 (modern reference)
- Basic epidemiology textbook notation

**Traceability:**
- Every equation in paper cites line number in `model.py`
- Formula JSON export for reproducibility

---

## Validation & Approval

**Technical validation (before human review):**
1. ✅ `model.py` runs without error
2. ✅ `simulate.py` produces sensible output
3. ✅ `build_paper.py` generates `main.pdf`
4. ✅ `main.pdf` compiles from Typst template
5. ✅ Equations in paper match code (visual inspection)

**Human approval gate:**
- Reviewer must confirm: technical accuracy, clarity, code reproducibility
- No external peer review required for this bounded artifact
- Decision: Accept → merge to main | Defer → preserve branch | Reject → document rationale

---

## Next Steps (If Accepted)

1. Merge `epidemiology-r0-reference` → `main`
2. Tag branch with completion record
3. Archive launch/completion records outside worktree
4. Remove temporary worktree
5. Record as Step 8 completion in three-lane proof

---

**Status:** LAUNCHED  
**Expected Duration:** 3–4 hours  
**Target Completion:** 2026-09-29 evening UTC
