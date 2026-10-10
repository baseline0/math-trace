# Reproducibility Verification Checklist

**For External Reviewers**

This checklist verifies that math-trace is reproducible from a fresh checkout on standard environments.

---

## Environment Requirements

- **Python**: 3.13+ (test with `python --version`)
- **OS**: Linux, macOS (Intel or Apple Silicon), or Windows (WSL2)
- **Tools**: `uv` (package manager), `just` (task runner), `typst` (optional, for PDF generation)
- **Network**: Internet access for initial setup only (uv sync downloads dependencies)

---

## Step 1: Fresh Checkout

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
git checkout <commit-or-tag-under-review>
```

**Acceptance**: Repository clones without errors.

---

## Step 2: Environment Setup

```bash
just setup
```

This installs:
- Python 3.13 (via uv)
- Dependencies (uv sync)
- Typst (for PDF compilation)

**Acceptance**: Setup completes without errors. Verify:
```bash
python --version      # Should show 3.13.x
uv --version          # Should show recent version
typst --version       # Should show 0.10+
```

---

## Step 3: Unit Test Suite

```bash
just test
```

**Acceptance Criteria**:
- [ ] All 144 tests pass
- [ ] No skipped tests (except marked `@pytest.mark.skip`)
- [ ] No warnings or errors in output
- [ ] Test execution time < 5 seconds

**Example output**:
```
======================== 144 passed, 8 skipped in 1.96s ========================
```

---

## Step 4: Verify All 5 Templates

For each template, run:

```bash
cd templates/epidemiology       && just paper && cd ../..
cd templates/quantum-systems    && just paper && cd ../..
cd templates/control-systems    && just paper && cd ../..
cd templates/gnns               && just paper && cd ../..
cd templates/thermodynamics     && just paper && cd ../..
```

### Epidemiology
- [ ] `main.pdf` builds successfully
- [ ] PDF contains 10+ sections (SIR model, scenarios, figures)
- [ ] Formulas render (check for λ, β, γ symbols)
- [ ] Simulation figures appear (trajectory plot)
- [ ] **File size**: ~200-400 KB

### Quantum Systems
- [ ] `main.pdf` builds successfully
- [ ] PDF contains 7+ sections (particle-in-box, harmonic oscillator)
- [ ] Energy eigenvalue equations visible
- [ ] Wavefunction figures appear
- [ ] **File size**: ~150-250 KB

### Control Systems
- [ ] `main.pdf` builds successfully
- [ ] PDF contains 10+ sections (DC motor, PID controller)
- [ ] Transfer function equations visible
- [ ] Control plots appear
- [ ] **File size**: ~200-350 KB

### Graph Neural Networks
- [ ] `main.pdf` builds successfully
- [ ] PDF contains 10+ sections (message passing, attention)
- [ ] Attention weight equations visible
- [ ] Graph structure diagrams appear
- [ ] **File size**: ~200-350 KB

### Thermodynamics
- [ ] `main.pdf` builds successfully
- [ ] PDF contains 10+ sections (ideal gas, Carnot cycle)
- [ ] Thermodynamic equations visible (PV=nRT, η=1-T_c/T_h)
- [ ] Energy diagrams appear
- [ ] **File size**: ~200-350 KB

---

## Step 5: Code Quality Checks

```bash
just check         # Ruff linting
just fmt --check   # Format validation
just typecheck     # Type checking
```

**Acceptance Criteria**:
- [ ] No ruff errors (linting passes)
- [ ] No formatting issues
- [ ] No type errors

---

## Step 6: Formula Consistency Verification

For each template, spot-check 2-3 equations:

```bash
cd templates/epidemiology/src
python model.py  # Should export JSON with equations
```

**Check**:
- [ ] JSON has `latex`, `description`, `source_line` fields for each equation
- [ ] LaTeX is valid (no unmatched braces)
- [ ] Source line references match model.py

---

## Step 7: Documentation Review

- [ ] README.md is present and complete
- [ ] CONTRIBUTING.md explains template structure
- [ ] AGMAI-READY.md defines guarantees clearly
- [ ] docs/adr/ has architecture decisions
- [ ] docs/ has getting-started guide

---

## Step 8: Release Artifacts

Verify these files exist at repository root:

- [ ] `LICENSE` (MIT)
- [ ] `pyproject.toml` (version 0.1.0, Python 3.13+)
- [ ] `CITATION.cff` (bibtex citation metadata)
- [ ] `CHANGELOG.md` (generated from conventional commits)
- [ ] `Justfile` (build recipes for all templates)
- [ ] `.pre-commit-config.yaml` (P0-P3 quality gates)

---

## Sign-Off

**Reviewer**: ________________
**Date**: ________________
**Environment**: macOS / Linux / WSL2 | Python version: ______

### Reproducibility Assessment

- [ ] All 5 templates build without errors
- [ ] PDFs render correctly with equations and figures
- [ ] 144 tests pass
- [ ] Code quality checks pass (lint, format, type)
- [ ] Documentation is complete and accurate

### Known Limitations Acknowledged

- [ ] SymPy constraints: only equations expressible in SymPy
- [ ] Numerical stability: not validated for long-duration runs
- [ ] PDF compilation requires Typst installation
- [ ] This verifies transcription, not scientific validity

### Recommendation

**☐ APPROVED**
Reproducibility verified. Math-trace is ready for release.

**☐ CONDITIONAL** (list issues below)
Reproducibility verified with minor issues:

```
[List any issues found]
```

**☐ NOT APPROVED** (list blockers below)
Reproducibility blocked by:

```
[List blocking issues]
```

---

## Questions or Issues?

Open an issue at https://github.com/baseline0/math-trace/issues or email the maintainer.
