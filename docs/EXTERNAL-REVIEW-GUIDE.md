# External Review Guide for v0.9.0-rc1

**What We're Asking You To Do**

Verify that math-trace v0.9.0-rc1 can be built and tested reproducibly from a fresh checkout on your local machine. This is the final gate before releasing to PyPI.

---

## What Is math-trace?

math-trace is a Python framework for tracing equations from source code through publication:

```
Python (SymPy) → LaTeX → Typst → PDF + JSON provenance
```

**Example workflow**:
1. Define formulas in `templates/epidemiology/src/model.py` (SymPy)
2. Run `just paper` → generates PDF with equations, figures, and source traceability
3. Every equation tagged with filename:line for verification

---

## What You'll Verify

**Scope**: 5 production templates, 144 unit tests, publication pipeline

| Component | What to check |
| --- | --- |
| **Model definitions** | 5 templates export SymPy formulas cleanly |
| **Test suite** | 144 unit tests pass (happy-path coverage) |
| **Paper generation** | All 5 PDFs build without errors |
| **Documentation** | README, CONTRIBUTING, AGMAI-READY, ADRs complete |
| **Release artifacts** | LICENSE, CITATION.cff, CHANGELOG, Justfile present |
| **Code quality** | Lint, format, type checks pass |

---

## How Long Will This Take?

**Estimate**: 1-2 hours

- Setup: 10 min (uv sync, install Typst)
- Tests: 2 min (144 tests)
- Template builds: 20 min (5 × `just paper`)
- Code checks: 5 min (lint, format, type)
- Documentation review: 20 min
- Sign-off: 5 min

---

## Step-by-Step Instructions

### 1. Clone and Setup

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
git checkout v0.9.0-rc1

# One-command setup
just setup
```

Expected time: ~10 minutes (first time only; installs uv, Python 3.13, Typst)

### 2. Run Unit Tests

```bash
just test
```

Expected result:
```
======================== 144 passed, 8 skipped in 1.96s ========================
```

Expected time: ~2 minutes

### 3. Build All 5 Templates

```bash
# Option A: Build all (takes ~20 min)
for t in epidemiology quantum-systems control-systems gnns thermodynamics; do
  cd templates/$t && just paper && cd ../..
done

# Option B: Build one at a time (spot-check)
cd templates/epidemiology && just paper
```

Expected result: All templates generate `main.pdf` without errors.

### 4. Code Quality Checks

```bash
just check         # Linting (should pass)
just fmt --check   # Format check (should pass)
just typecheck     # Type check (should pass)
```

Expected result: No errors.

### 5. Review Documentation

Open in your editor or browser:
- `README.md` — Overview and quick start
- `CONTRIBUTING.md` — How to add new templates
- `AGMAI-READY.md` — Public contract and guarantees
- `docs/adr/` — Architecture decisions
- `CITATION.cff` — How to cite

### 6. Sign Off

Complete the checklist in `docs/REPRODUCIBILITY-CHECKLIST.md` and return it with your recommendation.

---

## What Could Go Wrong? Troubleshooting

### Setup fails

**Problem**: `just setup` fails on Typst installation
**Solution**: Typst is optional. You can skip PDF generation and just verify formulas export cleanly.

**Problem**: Python 3.13 not available
**Solution**: The repo requires Python 3.13+. Upgrade your Python or ask us to backport to 3.11.

### Tests fail

**Problem**: Some tests fail on your system
**Solution**: Report which tests failed. We'll investigate (may be environment-specific).

### PDF doesn't build

**Problem**: `just paper` fails with Typst error
**Solution**:
- Verify Typst installed: `typst --version`
- PDF build is optional; formulas export is the critical path
- Skip PDF and verify `generated/formulas.typ` contains valid Typst

### Missing dependencies

**Problem**: Import errors when running `just paper`
**Solution**: Run `uv sync` again to refresh dependencies.

---

## What We're NOT Asking You To Do

❌ Verify scientific validity (that's peer review's job)
❌ Verify empirical adequacy (that equations match real-world data)
❌ Run performance benchmarks
❌ Test on every Python version (3.13+ is our support scope)
❌ Modify code or commit changes

---

## What Reproducibility Means Here

**Reproducibility = "I can build this from a fresh checkout and get the same outputs"**

Not:
- Scientific reproducibility (whether results match reality)
- Numerical reproducibility (exact bit-for-bit matches)
- Implementation reproducibility (whether the approach is optimal)

We're asking: "Does the code work as intended on your machine?"

---

## Success Criteria

✅ All 5 templates generate PDFs
✅ 144 tests pass
✅ Documentation is complete
✅ Code quality checks pass
✅ You can cite math-trace using CITATION.cff

---

## When You're Done

1. Complete `docs/REPRODUCIBILITY-CHECKLIST.md`
2. Email or PR with your sign-off
3. We'll cut the v0.9.0-rc1 tag and release to PyPI

---

## Questions?

- **Technical**: Open an issue at https://github.com/baseline0/math-trace/issues
- **Scope**: Email the maintainer (Mark Alexiuk, malexiuk@gmail.com)
- **Logistics**: Tag in a PR or discussion

---

**Thank you for verifying math-trace!** 🙏

Your sign-off helps us confidently release to the community.
