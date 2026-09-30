# Phase 4 Revision Notes (Consultant Feedback Integration)

**Date**: 2026-09-30  
**Source**: Consultant feedback on Phase 4 sequencing, scientific contracts, and release processes  
**Status**: To be integrated into TODO.md

## Key Changes from Feedback

### 1. Reconciliation Discovery First

**REMOVED**: "Write papers immediately"  
**ADDED**: Discovery lane (`MATH-TRACE-PHASE4-BASELINE-RECONCILIATION-001`) as critical first step

- Read-only inventory of current state after epidemiology hardening merge
- Maps stashed work to backlog items
- Identifies scientific contract gaps per template
- Recommends exactly 3 next bounded lanes

### 2. Correct Sequencing

**OLD ORDER**:
```
papers → tests → scenarios → release
```

**NEW ORDER**:
```
reference contract + baseline build
    ↓
focused scientific tests (model invariants)
    ↓
one scenario/reference artifact
    ↓
paper/reference narrative
    ↓
repeat by template
    ↓
cross-template index
    ↓
release readiness (local validation only)
    ↓
[EXPLICIT HUMAN APPROVAL]
    ↓
release execution (GitHub + Zenodo)
```

**Rationale**:
- Paper credibility depends on model contract + tests, not narrative first
- Scenarios need explicit assumptions + tests, not bolted on post-hoc
- Release/publishing are irreversible; require separate explicit approval

### 3. Scientific Contracts Replace Coverage Targets

**REMOVED**: "90% line coverage" as acceptance criterion  
**ADDED**: Eight-area acceptance checklist per template

| Area | Required evidence |
|---|---|
| Model contract | Governing equations, symbols, units, parameter meaning, assumptions explicit |
| Mathematical invariants | Conservation, bounds, normalization, stability, limiting behavior, analytic test cases |
| Scenario contract | Inputs, parameter source/provenance, expected behavior, limitations |
| Artifact contract | Build produces declared equations, plots, output, narrative; reproducible |
| Reproducibility | Repeated runs yield semantically consistent output; nondeterminism bounded |
| Narrative integrity | Paper makes no claim stronger than model/scenario/validation evidence supports |
| Provenance | Direct references support parameters, equations, datasets, limitations |
| Test quality | Tests exercise behavior/invariants, not source-text tautologies |

**Example: Epidemiology** (Captures what recent merge already partially satisfied):
- Population conservation: S(t) + I(t) + R(t) = N, within numerical tolerance ✓ (in tests)
- Non-negativity: S, I, R ≥ 0 ✓ (in tests)
- Frequency-dependent transmission: β SI / N ✓ (in model)
- R₀ = β / γ under baseline assumptions ✓ (in tests)
- Initial growth consistent with sign(β - γ) ✓
- Scenario metadata declares source, assumptions, interpretation ✓ (in tests)

### 4. Smaller Lanes per Template

**REMOVED**: "Write 5 papers in parallel" as one combined task  
**ADDED**: Each template gets its own bounded lane through full cycle

Example lane structure:
- `MATH-TRACE-EPIDEMIOLOGY-REFERENCE-COMPLETION-001` (if incomplete after reconciliation)
- `MATH-TRACE-QUANTUM-REFERENCE-CONTRACT-001`
- `MATH-TRACE-CONTROL-REFERENCE-CONTRACT-001`
- (etc., one per template)

### 5. Scenario Expansion: Risk Assessment First

**REMOVED**: "Measles, Ebola, Cora, Bode—quick wins" mindset  
**ADDED**: Explicit risk/complexity assessment for each

| Scenario | Risk | Better approach |
|----------|------|-----------------|
| Measles SEIR | New model scope beyond SIR | Document SEIR extension boundaries first |
| Ebola stochastic | Stochastic execution + determinism complexity | Start deterministic or seeded stochastic |
| Cora GNN | Dataset licensing + non-deterministic training | Provenance + deterministic preprocessing first |
| Attention viz | Interpretability can exceed evidence | Cautious wording; no causal claims |
| Double-slit/tunneling | Distinct solvers + boundary conditions | One scenario + one convergence check |
| Bode/mass-spring | Units/convention ambiguity | Do mass-spring first; Bode when conventions clear |
| Phase diagrams | May need external equation-of-state data | Start illustrative, clearly labeled |

### 6. Release Work: Two Separate Lanes

**REMOVED**: "Release v1.0.0" as single engineering task  
**ADDED**: Two lanes with explicit human gate between them

**Lane 1: Release Readiness** (read-only)
- Verify clean main
- Confirm scope explicit
- Run focused checks
- Validate changelog + CITATION.cff
- Draft release notes (no tag/push/GitHub/Zenodo actions)
- Deliverable: Readiness checklist + release notes draft

**Human Approval Gate**: "Ready to publish?"

**Lane 2: Release Execution** (only after approval)
- Update version/metadata
- Commit + tag
- Push to GitHub
- Create GitHub release
- Enable/verify Zenodo archival
- Confirm DOI metadata

**Rationale**: GitHub + Zenodo archival is irreversible external publishing. Separate from normal engineering.

### 7. Six-Question Manifest Template

Before dispatching ANY implementation lane:

1. **What user-visible artifact changes?** (Specific files, outputs, sections)
2. **What exact paths may change?** (Include generated artifacts, figures)
3. **What claims will artifact make—what evidence supports them?** (Link to contracts/tests)
4. **What one or two scientific invariants would catch an important mistake?** (Not coverage %)
5. **What reproducibility standard applies?** (Byte, semantic, seeded statistical, visual?)
6. **What must not change?** (Hard boundaries for scientific integrity)

If manifest cannot answer these → it's planning work, not an implementation lane yet.

### 8. Stashed Work: Evidence, Not Baseline

**REMOVED**: Treating stash 278e97a as implementation baseline  
**ADDED**: Explicit classification step in reconciliation

- Do NOT restore casually
- Treat as evidence/candidate material
- Classify in discovery (maps to which 4c-6 through 4c-10 items?)
- If coherent cross-template: one lane
- If scattered: decompose by template domain

## Post-Reconciliation: Suggested Lane Order

Based on consultant feedback + epidemiology hardening evidence:

| Lane | Purpose | Start condition | Effort |
|------|---------|-----------------|--------|
| `RECONCILIATION-001` | Accurate inventory + recommend 3 next lanes | **START NOW** | 2-3 hrs |
| `EPI-REFERENCE-COMPLETION-001` | Complete epidemiology if 4c-1 genuinely incomplete | If reconciliation shows gaps | 2-4 hrs |
| `QUANTUM-REFERENCE-CONTRACT-001` | One quantum reference + model contract | After epidemiology workflow proven | 6-8 hrs |
| `CONTROL-REFERENCE-CONTRACT-001` | One control reference + model contract | After quantum or by strategic value | 6-8 hrs |
| `SCENARIO-TRIAGE-001` | Classify stash; recommend scenario decomposition | After reconciliation | 2-3 hrs |
| `RELEASE-READINESS-001` | Local v1 readiness checklist (read-only, no publishing) | After all references complete | 1-2 hrs |
| [HUMAN APPROVAL GATE] | Explicit decision: "Publish v1.0?" | After readiness passes | — |
| `RELEASE-EXECUTION-001` | Version bump + tag + GitHub + Zenodo | Only after approval | 1 hr |

## Files to Update in TODO.md

1. **Section 4c**: Replace old paper-writing section with reconciliation discovery details
2. **Section 4c-AFTER**: Replace old "write 5 papers" with corrected sequencing + per-template lanes
3. **Section 4d**: Replace "90% coverage" test section with scientific contract checklist
4. **Section 4e-4f**: Replace old "GitHub Release" + "Documentation" sections with:
   - Release Readiness Lane (read-only)
   - [EXPLICIT HUMAN GATE]
   - Release Execution Lane (GitHub + Zenodo only after approval)
5. **Remove**: Scenario expansion as "quick wins"; replace with risk assessment
6. **Add**: Six-question manifest template as requirement before any lane dispatch

## Recommended Action

1. **This session**: Integrate this revision into TODO.md systematically (sections 1-6 above)
2. **Next step**: Execute RECONCILIATION-001 to inventory actual state
3. **After reconciliation**: Re-prioritize remaining Phase 4 lanes based on what's actually incomplete vs. what's already met by epidemiology hardening merge

## WorkItem vs. TODO.md Trade-off

**This feedback is complex enough that it might benefit from WorkItem format if you have CLI tools.**

Questions for WorkItem approach:
- Can you read + comment on WorkItems from command line?
- Would versioned WorkItem structure help capture evolving requirements better than a single TODO.md file?

**For now**: Recommend integrating this into TODO.md with clear section markers, so it's reviewable in one place. Can be decomposed into formal WorkItems later if needed.
