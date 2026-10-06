# PHASE 4C BASELINE RECONCILIATION REPORT

**Date**: 2026-10-06
**Scope**: 5 core templates, test coverage, release readiness
**Effort**: Read-only audit (2-3 hours)

---

## ACCEPTANCE CRITERIA STATUS

| Criterion | Status | Notes |
| --- | --- | --- |
| 5 core templates complete (models) | ✅ PASS | epidemiology, quantum-systems, control-systems, gnns, thermodynamics |
| All templates have papers (main.typ) | ✅ PASS | All 5 have Typst papers (55-127 lines, 7-11 sections) |
| All templates have scenarios | ✅ PASS | Each has ≥1 scenario (covid_sir, harmonic_oscillator, dc_motor, karate_club, ideal_gas) |
| Test coverage ≥90% (arbitrary target) | ❌ CONDITIONAL | See "Test Gap Analysis" below |
| Tests for all templates | ⚠️ PARTIAL | epidemiology, quantum-systems, control-systems: ✓ (26+23+40 tests) |
| Tests for gnns, thermodynamics | ❌ BLOCKING | 0 test files—required for acceptance |
| Release artifacts (CHANGELOG, CITATION.cff) | ❌ MISSING | Needed before v0.9.0-rc1 |

---

## TEST GAP ANALYSIS

**Current state** (by template):
- **epidemiology**: 26 tests ✅ (SIR model contract tests + dynamics)
- **quantum-systems**: 23 tests ✅ (particle-in-box, harmonic oscillator)
- **control-systems**: 40 tests ✅ (DC motor, PID controller)
- **gnns**: 0 test files ❌ (code exists; tests deferred)
- **thermodynamics**: 0 test files ❌ (code exists; tests deferred)

**Coverage philosophy** (per user clarification):
- Measure with `pytest-cov`, not arbitrary % targets
- Pyramid shape (unit → integration → e2e) matters more than absolute coverage
- Already have pytest-cov in dev deps; ready to measure

**Action**: Write test files for gnns and thermodynamics (BLOCKING for acceptance)

---

## SCENARIO MATURITY ASSESSMENT

| Template | Scenario | Scientific Complexity | Reproducibility | Test Coverage |
| --- | --- | --- | --- | --- |
| epidemiology | covid_sir | Medium (SIR parameters, R₀) | High (fixed params) | ✓ Tested |
| quantum-systems | harmonic_oscillator | High (Schrödinger, eigenvalues) | Medium (numerical approximation) | ✓ Tested |
| control-systems | dc_motor | High (PID, dynamics) | High (deterministic) | ✓ Tested |
| gnns | karate_club | Medium (graph-based) | High (fixed graph) | ✗ No tests |
| thermodynamics | ideal_gas | Medium (thermodynamics law) | High (physics-based) | ✗ No tests |

**Recommendation**: All scenarios are scientifically reasonable. gnns + thermodynamics need test validation.

---

## RELEASE READINESS

| Item | Status | Blocking? | Notes |
| --- | --- | --- | --- |
| Code complete (5 templates) | ✅ | No | Models, scenarios, papers all present |
| Tests for all templates | ⚠️ Partial | **YES** | gnns, thermodynamics missing tests |
| CHANGELOG.md | ❌ | Yes | Document changes for v0.9.0-rc1 |
| CITATION.cff | ❌ | Yes | Bibtex citation format (standard for PyPI) |
| External review | ⏳ Pending | **YES** | Blocker for v0.9.0-rc1 tag |
| Zenodo DOI | ⏳ Deferred | No | Post-v1.0.0 (user marked "unapproved") |

**Local readiness**: ~80% (code + tests almost done)
**Publishing readiness**: ~50% (missing release metadata + external review)

---

## COMMIT 278e97a ANALYSIS

**What**: LANE-CANDIDATE: template scenario enhancements
**Contents**: README updates + config tweaks across all 5 templates
**Status**: Merged on main
**Action**: Already integrated; no backlog items deferred

---

## RANKED NEXT 3 PRIORITIES (LANES)

**Lane 1: BLOCKING — Add tests for gnns + thermodynamics** ⛔
- **Scope**: Write test files + validate scenarios
- **Templates affected**: gnns, thermodynamics
- **Effort**: 2-3 hours (mimic epidemiology/quantum-systems structure)
- **Acceptance**: All 5 templates pass full test suite
- **Blocks**: v0.9.0-rc1 release gate

**Lane 2: CRITICAL — Write CHANGELOG + CITATION.cff** 📋
- **Scope**: Document v0.9.0-rc1 changes; add bibtex citation
- **Effort**: 45 min
- **Acceptance**: Files present + pass linting
- **Blocks**: v0.9.0-rc1 release gate

**Lane 3: VALIDATION — External reproducibility review** 👥
- **Scope**: External reviewer runs `just paper` on all 5 templates
- **Effort**: 1-2 hours (external, not your time)
- **Acceptance**: Reviewer confirms all PDFs build + match expected structure
- **Blocks**: v0.9.0-rc1 release tag

---

## DECISION TREE FOR v0.9.0-rc1

```
Lane 1: gnns + thermodynamics tests ✓
    ↓
Lane 2: CHANGELOG + CITATION.cff ✓
    ↓
Lane 3: External review sign-off ✓
    ↓
→ v0.9.0-rc1 TAG READY
```

---

## SUMMARY

**What's ready**: 3/5 templates fully tested, all papers complete, all scenarios work
**What's blocking**: gnns + thermodynamics tests, release metadata, external review
**What's post-v1.0**: Lean formalization (3+ templates), Zenodo DOI

**Effort to release**: 3-4 hours of your time (2-3 for tests, 45 min for metadata)
**Timeline**: 1-2 days if external review is fast

---

**Next**: Start Lane 1 (gnns + thermodynamics tests)
