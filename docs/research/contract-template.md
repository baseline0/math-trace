# math-trace: Partnership Contract Template

**Target Audience**: Academic researchers, AI companies, institutions auditing mathematical claims
**Version**: 1.0 (Sep 22, 2026)
**Purpose**: Template for partnership & evaluation contracts; customize with partner name and terms

---

## What math-trace Is

A framework for tracing equations from source code through symbolic representation, verification, and publication.

**Workflow**: Python (SymPy) → LaTeX → Typst → PDF + JSON provenance

### Core Capability

One edit to `model.py` updates your entire paper automatically. Every equation links back to code.

---

## What math-trace Guarantees

### Guaranteed Features (v0.9.0+)

Every formula in your paper is:

- ✅ **Equation extraction from SymPy** — Equations defined in source code export to LaTeX automatically
- ✅ **Typst paper generation** — Equations render in publication-quality Typst documents
- ✅ **Source-line traceability** — Every equation tagged with filename and line number
- ✅ **Metadata schema** — Consistent equation records (name, LaTeX, description, assumptions, units, verification status)
- ✅ **One-command build** — `just paper` generates complete paper from fresh checkout
- ✅ **Test coverage** — All templates pass unit tests (see `tests/unit/test_guarantees.py`)
- ✅ **Reproducibility** — Same equation → same LaTeX every time
- ✅ **Clean installation** — Works in fresh Python 3.11–3.13 environment with `uv sync`

**Proof**: Each guarantee is validated by executable tests. See `tests/unit/test_guarantees.py` for verification.

### Experimental Features (Optional, May Change)

- 🔬 **Lean formalization** — Optional per template; theorems may remain incomplete
- 🔬 **Palomar registry integration** — Optional; metadata format may evolve
- 🔬 **Interactive visualizations** — Streamlit/Jupyter; UI may redesign

---

## What math-trace Does NOT Verify

**Explicitly out of scope**:

- ❌ **Empirical adequacy** — An equation matching experimental data
- ❌ **Parameter estimation** — Fitting constants to real-world measurements
- ❌ **Implementation correctness** — That external libraries (SymPy, NumPy) behave as documented
- ❌ **Numerical stability** — That floating-point arithmetic remains stable over long simulations
- ❌ **Physical realism** — That a model captures relevant phenomena (e.g., SIR ignores age structure)
- ❌ **Scientific validity** — That a theory is correct, only that it was transcribed faithfully
- ❌ **Domain expertise** — That users understand the assumptions and limitations

**Critical implication**: A green "verified" checkmark means "this equation was transcribed correctly from source and passes unit tests," NOT "this equation correctly models reality."

---

## Verification Vocabulary (Six Distinct Categories)

Do NOT collapse these into one "verified" badge:

| Status | Meaning | Example |
|--------|---------|---------|
| `source_verified` | Cited source was inspected by human | "Kermack-McKendrick 1927 paper reviewed" |
| `transcription_verified` | Equation faithfully transcribed from source | "test_sir.py: equation matches Kermack form exactly" |
| `symbolic_verified` | Symbolic identities or transformations passed | "test_algebra.py: SIR + SEIR identity proven" |
| `numerically_verified` | Numerical checks passed over defined test cases | "test_sir_numerics.py: SIR equilibrium within 1e-6" |
| `formally_verified` | Theorem prover established stated property | "Lean: conservation law proven under assumptions" |
| `historical_interpretation` | Human-curated historical claim (not mathematical proof) | "This formulation became standard after 1970" |

Each status is **independent** — an equation can have `source_verified=true` but `transcription_verified=false`.

---

## Supported Use Cases

### Primary (v0.9.0+)

- 🟢 **Academic research papers** — Publish equations with traceability to code
- 🟢 **Educational materials** — Teach formula derivation with source code
- 🟢 **Reproducible research** — Readers can regenerate figures from code
- 🟢 **Audit trails** — Mathematicians verify equation transcription
- 🟢 **Code documentation** — Auto-generate papers from model.py

### Secondary (v0.9.0–1.0.0)

- 🟡 **AI company auditing** — Review assumptions and verification statuses
- 🟡 **Formal verification** — Subset of equations proven in Lean

### Not Supported

- 🔴 **Live code-to-paper synchronization** — Papers are snapshots, not live docs
- 🔴 **Automatic parameter fitting** — math-trace provides structure, not estimation
- 🔴 **Numerical simulation** — math-trace generates derivations; execution is user's responsibility
- 🔴 **Real-time data ingestion** — Static papers only

---

## Supported Environments

### Required

- **Python**: 3.11, 3.12, 3.13 (3.10 or earlier not supported)
- **SymPy**: ≥1.12
- **Operating System**: macOS (Intel or Apple Silicon), Linux (Ubuntu 20.04+), Windows (WSL2)

### Optional

- **Typst**: ≥0.10 (required for PDF generation; installable via `cargo install typst-cli`)
- **Lean**: 4.0+ (required only for Lean formalization optional components)

### Not Supported

- Python 3.10 or earlier
- Windows native cmd.exe (use WSL2 or PowerShell)
- SymPy 1.11 or earlier (compatibility breakage)

---

## Template Ecosystem

### Five Core Templates (v0.9.0)

Each template follows identical contract:

| Template | Equations | Test Coverage | Paper Structure | Status |
|----------|-----------|----------------|-----------------|--------|
| Epidemiology (SIR/SEIR) | 6 | 90%+ | 10-section golden path | ✅ Core |
| Quantum Systems | 5 | 90%+ | 10-section (replicating Epi) | ✅ Core |
| Control Systems | 5 | 90%+ | 10-section | ✅ Core |
| Graph Neural Networks | 5 | 90%+ | 10-section | ✅ Core |
| Thermodynamics | 5 | 90%+ | 10-section | ✅ Core |

### Adding New Templates

To contribute a template:

1. Create `templates/{domain}/model.py` with equations in SymPy
2. Each equation must have: name, LaTeX, description, assumptions, units, source_line
3. Write `templates/{domain}/tests/` with 90%+ coverage
4. Write `templates/{domain}/paper.typ` (10 sections, modeled on Epidemiology)
5. Verify assumptions and units match schema
6. **External reviewer** confirms reproducibility
7. Tag in changelog as "new template added"

---

## Release Roadmap

### v0.9.0-rc1 (Release Candidate)

- ✅ All 5 templates complete (code + tests)
- ✅ Epidemiology paper = golden path (10 sections, 100% claims verified)
- ✅ Other 4 papers replicate Epi structure
- ✅ Test coverage 90%+ on all templates
- ✅ CHANGELOG.md, CITATION.cff, LICENSE, clean install verified
- ✅ External reviewer confirmed reproducibility
- ⚠️ API not yet frozen (may have breaking changes before v1.0.0)

### v0.9.0 (Release)

- Same as rc1, feedback incorporated

### v1.0.0 (When Ready)

- ✅ All from v0.9.0
- ✅ API declared stable (no breaking changes without major version bump)
- ✅ Lean formalization on ≥3 templates (optional but included)
- ✅ Zenodo DOI minted
- ✅ Downstream citations demonstrating adoption

---

## Known Limitations (Honest Assessment)

1. **SymPy constraints** — Only equations expressible in SymPy are supported; complex piecewise functions, special functions may need manual workarounds
2. **Unit tracking** — Units are metadata only; no automatic dimensional analysis or conversion
3. **Symbolic verification** — Limited to polynomial and rational function identities; transcendental proofs require Lean
4. **Scalability** — Papers with 100+ equations may have slow compile times
5. **Peer review NOT replaced** — math-trace supplements but does not replace scientific review
6. **Historical accuracy** — We cite sources but cannot verify archival historical claims beyond academic databases
7. **Implementation fidelity** — Test coverage is local; does not guarantee correctness when equations are embedded in larger systems

---

## How to Evaluate math-trace

1. **Read the guarantees** (above) — Focus on "What math-trace Does NOT Verify"
2. **Review test suite** — `tests/unit/test_guarantees.py` validates each claim
3. **Try the example** — Clone repo, run `just paper` for membrane-dynamics example
4. **Examine templates** — Review Epidemiology golden path for structure and rigor
5. **Check limitations** — Verify they don't block your use case

---

## Contact & Questions

**For integration inquiries**: Review the code and tests first. Limitations are intentional, not bugs.

**For formal verification**: Lean support is optional and evolving; contact for roadmap.

**For feedback**: This contract is version 1.0 (Sep 22, 2026). Your use case helps shape v0.9.0→v1.0.0.

---

**Contract finalized**: Sep 22, 2026
**Author**: Mark Alexiuk
**Version**: 1.0
