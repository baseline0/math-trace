# math-trace

[![Tests](https://github.com/baseline0/math-trace/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/baseline0/math-trace/actions)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

**math-trace makes mathematical references reproducible: each reference connects its equations, assumptions, implementation, tests, and generated results in one inspectable workflow.**

Its flagship reference, `sidorenko-turan`, reproduces one result: a Turán-density bound for r-uniform hypergraphs with r ≥ 3. The paper proves that bound. It is not a proof of Sidorenko's conjecture. The reviewer command `just reference-check` rebuilds the reference from a clone, checks it, and writes a JSON report.

**Status: pre-release.** The version is 0.1.0. v1.0.0 is not tagged, and the external reproducibility review has not started.

## Quickstart

You need `git`, [`uv`](https://docs.astral.sh/uv/), and [`just`](https://just.systems). `uv` fetches Python 3.13 from `.python-version` and installs the locked dependencies.

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
uv sync --frozen        # Python 3.13 and the dependencies pinned in uv.lock
just reference-check    # rebuilds sidorenko-turan twice, then runs its contract tests
echo $?                 # 0 = pass, 1 = fail
```

On success the last line is `sidorenko-turan: pass (report: .../examples/sidorenko-turan/generated/reference-report.json)`. On failure the command prints one line per failed check, for example `contract tests exited 1`, and exits 1. The report is written in both cases, so the failure can be read there.

To check the other registered reference, `epidemiology-sir` (a secondary example), run `just reference-check epidemiology-sir`. An unknown name exits 2 and lists the known names.

## Worked example: the flagship reference

`sidorenko-turan` lives in `examples/sidorenko-turan/`. It states, for every r-uniform forbidden hypergraph F with r ≥ 3 and m ≥ 1 edges:

> turanDensity F ≤ 1 − c_r / m^((r−1)/r),

with c_r given explicitly. The constant is `paperConstant` and the gap is `paperGap` in `lean_statement.lean`, copied verbatim from the upstream Lean project `xliu2022/improved-sidorenko-lean` at commit `ba6f109`.

What the reference contains:

- `build_table.py` evaluates the displayed constant and gap exactly (with sympy) for r in {3, 4, 5} and m in 1..10, and writes `generated/gap_table.json`. For example, at r = 3, m = 1 the gap is (1/81)·3^(1/3) ≈ 0.0178055502507, so the bound is about 0.9821944497.
- `formalization.json` records the status of each check, with its evidence.

What is checked, and by what:

| Claim | Status | Evidence |
| --- | --- | --- |
| The upstream Lean project builds and its three main theorems depend only on the standard axioms | Passed, recorded | `formalization.json` (`build`, `axioms`) |
| The Lean statement matches the target statement (`statement_match`) | Passed, recorded, with a caveat | The author's Comparator judge printed "Your solution is okay!" on `ba6f109`. It ran **with network access**, so it is not offline (Phase B) evidence. |
| The displayed constant and gap are computed correctly | Checked by `just reference-check` | `build_table.py` plus `tests/integration/test_sidorenko_turan_contract.py`, which compares each row with an independent float evaluation to 1e-12 and checks that the gap is positive and decreases in m |

`just reference-check` does not rebuild the Lean project and does not re-run the Comparator. Those results are recorded, not reproduced by this command.

## What "reproducible" means operationally

For a registered reference, `just reference-check` establishes the following, all from one checkout:

1. The required files exist (the list is in the registry).
2. The build runs, then runs again. After each run, every output file is hashed with SHA-256. The two runs must produce identical hashes, and the outputs must not be empty.
3. The reference's contract tests pass (`uv run pytest`).
4. Provenance is written to the report: the source revision (HEAD), the exact tag if HEAD has one, whether the tree has uncommitted changes, the Python version, and the SHA-256 of each required input.

The check passes only if all of these hold. A dirty tree is recorded in the report but does not cause a failure, so review a clean checkout (`git status` empty) when you need the report as evidence.

The check does **not** establish:

- that another checkout, machine, or platform produces the same hashes. Expected hashes are not recorded yet; deciding how to pin the Python and library versions is an open item.
- that the Lean build or the Comparator result holds today. Those are recorded in `formalization.json` (see the table above).
- anything about the scientific content of the paper. The check confirms the transcription and arithmetic, not the mathematics.

## Add or review a reference

**To review a reference:** run `just reference-check <name>`, then read `examples/<name>/generated/reference-report.json`. Its `result` field is `pass` or `fail`, and `failures` lists each reason. The reasons are: missing required files, a build step that exited non-zero, failing contract tests, no outputs, and outputs that differ between two builds.

**To add a reference:**

1. Add a `Reference` entry to `REFERENCES` in `src/math_trace/reference_check.py`. It names the directory, the build commands (run inside that directory), the required files, the output glob patterns, and the contract test files (relative to the repo root).
2. Write the contract tests. Put them under `tests/integration/` or `tests/unit/`, and list them in the entry.
3. Run `just reference-check <name>` until it passes. Add a test to `tests/unit/test_reference_check.py` that the new entry is registered, following `test_the_epidemiology_reference_is_registered_with_its_contract_tests`.

The registry is code, so a new reference is a reviewed change, not a configuration file.

## Limitations

- **Not released.** The version is 0.1.0. v1.0.0 is not tagged, and the external reproducibility review has not started. - **Two registered references.** `sidorenko-turan` is the flagship. `epidemiology-sir` is a secondary example.
- **Lean is recorded, not rebuilt here.** This repository holds two verbatim Lean definitions and the recorded evidence, not the full Lean project. Its build and axiom checks come from the upstream commit.
- **The Comparator run used network access.** The offline (Phase B) configuration has not been shown to reproduce it.
- **The companion table checks arithmetic only.** Matching the Lean statement to the paper is the Comparator's job, not `build_table.py`'s.
- **Determinism is checked within one checkout.** Cross-checkout and cross-platform hashes are not recorded.
- **Deferred, not in v1:** Lean formalization of the other templates, PDF export, multi-paper comparison, LaTeX-to-SymPy conversion, interactive visualisations, and Palomar registry integration.

---

## For contributors

The sections below cover the architecture, the membrane-dynamics example, and the developer workflow. They are kept for contributors and are not part of the reviewer path.

Formula-to-code traceability for researchers who want reproducible mathematics. SymPy → Typst → PDF, with Lean formalization as a path for theorem-style references. Palomar registry integration is deferred.

### Quick Install & Try

```bash
# Install from PyPI
pip install math-trace

# Or clone to use examples
git clone https://github.com/baseline0/math-trace.git
cd math-trace/examples/membrane-dynamics

# Build the paper (30 seconds)
just paper
open main.pdf
```

**What you get**: A publication-ready PDF with equations, theorems, and simulation figures—all traced back to `model.py`.

### What math-trace Guarantees

Every formula in your paper is:
- **Traced to source code** — Equations in your SymPy model automatically appear in the paper
- **Marked with source location** — Every equation tagged with filename:line for easy reference
- **Tested** — Core conversion pipeline validated (see `tests/unit/test_guarantees.py`)
- **Reproducible** — Same equation produces same LaTeX output every time
- **Publication-ready** — Generates Typst PDF from a fresh Python 3.13 environment in seconds

⚠️ **What this does NOT mean**: math-trace verifies your equations are **transcribed correctly from code**. It does NOT verify scientific validity, empirical adequacy, or physical realism—that's peer review's job.

### What math-trace Does NOT Verify

math-trace is **NOT** responsible for:
- **Scientific validity** — Whether your theory is correct (peer review's job)
- **Empirical adequacy** — Whether equations match real-world data
- **Domain expertise** — Whether you understand your model's assumptions
- **Numerical stability** — Behavior of external libraries (SymPy, NumPy)
- **Parameter estimation** — Fitting constants to measurements

**Bottom line**: A ✅ "verified" badge means "equation transcribed correctly," NOT "equation is scientifically sound."

### What Is math-trace?

Every formula in your paper should link to the code that uses it. Every theorem should have a proof. Every proof should be verified.

math-trace connects:
- **SymPy formulas** (Python) → source of truth
- **Typst paper** (typesetting) → equations in your PDF
- **Simulations** (matplotlib/numpy) → figures validated against formulas
- **Lean proofs** (optional) → formal verification
- **Palomar registry** (optional) → publication registration

One edit to `model.py` updates your paper automatically.

### Requirements

**Core**:
- Python 3.13 (`requires-python` is `>=3.13` in `pyproject.toml`)
- `pip install math-trace` (or `just setup` for one-command installation)

**Optional**:
- Typst ≥0.10 (required for PDF generation; `just install-typst` to set up)
- Lean 4 (required only for optional formal proofs)

**Supported Platforms**:
- **macOS** (Intel and Apple Silicon)
- **Linux** (Ubuntu 20.04+, other distributions)
- **Windows** (via WSL2; native cmd.exe not supported)

### Example: Stochastic P Systems

The included example demonstrates end-to-end formula traceability:

#### Step 1: Define Formulas in Python

`examples/membrane-dynamics/model.py` (source of truth):

```python
import sympy as sp

k = sp.Symbol("k", positive=True, real=True)
n_a = sp.Symbol("n_a", positive=True, integer=True)
rate_expr = k * sp.binomial(n_a, 2)  # Rate law: r = k * n_a * (n_a - 1) / 2
```

#### Step 2: Use Formulas in Paper

`main.typ` imports and displays:

```typst
#figure(
  align(center, $k binomial(n_a, 2)$),
  caption: [Rate law (from model.py:25)]
)
```

#### Step 3: Validate with Simulation

`simulate.py` uses the same formula:

```python
# This MUST match model.py:25 exactly
rate = k_val * na * (na - 1) / 2
```

Tests verify code ↔ formula equivalence.

#### Step 4: Formalize (Optional)

`lean/Challenge.lean` states the theorem:

```lean
def rate (k : ℝ) (n : ℕ) : ℝ := k * (n : ℝ) * ((n : ℝ) - 1) / 2
```

#### The Traceability Chain

```
model.py (SymPy: source of truth)
    ↓
generated/formulas.typ (automatic LaTeX → Typst)
    ↓
main.typ (your paper)
    ↓
main.pdf (compiled PDF)
    ↓
simulate.py (validation: formulas match code)
    ↓
tests/ (proof: simulations match equations)
    ↓
lean/ (optional: formal proof)
    ↓
Palomar Registry (optional: publish formalization)
```

**Key principle**: Edit formulas once in `model.py`. Everything updates automatically.

### Getting Started (5 Minutes)

#### For Users: Just Use It

See [Getting Started Guide](docs/getting-started-external.md) for:
- Installation (1 minute)
- Running the example (2 minutes)
- Adapting to your domain (2 minutes)

#### For Contributors: Fork a Template

Want to start your own paper? Pick a template and customize it:

- **[simple-physics](templates/simple-physics/)** — Harmonic oscillator (classical mechanics)
- **[biochemistry](templates/biochemistry/)** — Enzyme kinetics (Michaelis-Menten)
- See [TEMPLATE-USAGE.md](templates/TEMPLATE-USAGE.md) for full guide

Each template includes a complete working example you can fork:

```bash
cp -r templates/simple-physics ../my-physics-paper
cd ../my-physics-paper
# Edit model.py, simulate.py, main.typ with your research
python build_paper.py
```

See [templates/TEMPLATE-USAGE.md](templates/TEMPLATE-USAGE.md) for:
- Step-by-step adaptation guide
- Multi-domain examples (optics, pharmacokinetics, gene regulation)
- Publishing workflows (GitHub, arXiv, journals)

#### For Contributors: Add Your Domain

See [Contributing Guide](CONTRIBUTING.md) to:
- Fork and clone
- Create your domain example
- Submit a PR

#### Full Workflow

**1. Clone template** (or use `pip install math-trace` + example from GitHub)

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace/examples/membrane-dynamics
```

**2. Edit `model.py`** with your formulas

```python
import sympy as sp

# Your symbols
k, n = sp.symbols("k n", positive=True)

# Your formula (source of truth)
your_formula = k * sp.binomial(n, 2)
```

**3. Update `main.typ`** to use your formulas

**4. Adapt `simulate.py`** to compute your results

**5. Build and view**

```bash
just paper     # Generates main.pdf
```

**Optional: Formalize with Lean**

```bash
# Edit lean/Challenge.lean with your theorem
# (See examples/membrane-dynamics/lean/ for structure)
just lean      # Compile Lean proofs
```

### Project Structure

```
math-trace/
├── Justfile                    # Build recipes (just paper, just test, just help)
├── pyproject.toml              # Dependencies and package config
├── README.md                   # This file
│
├── src/math_trace/             # Reusable library for formula conversion
│   ├── generators.py           # SymPy → LaTeX/Typst converters
│   └── services.py             # High-level API
│
├── examples/
│   ├── membrane-dynamics/      # Complete end-to-end example (clone & just paper)
│   └── epidemiology/           # (Stub) Reference config for SIR/SEIR models
│
├── templates/                  # Fork-friendly domain templates
│   ├── simple-physics/         # Classical mechanics template
│   └── biochemistry/           # Enzyme kinetics template
│
├── tests/                      # Test suite (pytest)
│   ├── test_model_export.py    # Formula generation tests
│   └── examples/               # End-to-end workflow examples
│
├── docs/
│   ├── adr/                    # Architecture decisions
│   └── ARCHITECTURE.md         # System design and flexibility
│
└── LICENSE                     # MIT license
```

### Standards & Philosophy

#### Code-as-Docs

This project follows the fleet-base code-as-docs philosophy:

- **Formulas are code** (SymPy objects in Python)
- **Tests are documentation** (examples of how to use the system)
- **Type hints communicate intent** (don't write comments if the code is clear)
- **ADRs for decisions** (why Typst? why Python-first?)

See [docs/adr/](docs/adr/) for architecture decisions.

#### Traceability

Every formula, theorem, and proof links to its source:

```python
# model.py
rate_formula = Formula(
    expr=k * sp.binomial(n_a, 2),
    source_line=25,  # Always document where this comes from
)
```

```typst
// main.typ
#figure(align(center, rate), caption: [Rate law (from model.py:25)])
```

```lean
-- Challenge.lean
/-- Derived from model.py:25 -/
def rate (k : ℝ) (n : ℕ) : ℝ := ...
```

### Building & Testing

#### Build Commands

```bash
just model       # Export formulas from SymPy
just formulas    # Convert LaTeX → Typst
just simulate    # Run stochastic simulation
just figures     # Generate matplotlib figures
just pdf         # Compile Typst to PDF
just paper       # Full pipeline (model → figures → pdf)
```

#### Testing

```bash
just test              # Run full test suite
just test-formulas     # Test formula generation
just test-model        # Test model definitions
just typecheck         # Type check Python code
```

#### Pre-commit Hooks

This repository uses [pre-commit](https://pre-commit.com) to enforce code quality before commits and tests before pushes.

**Install hooks** (one-time setup):
```bash
uv run pre-commit install --install-hooks
```

**Hook stages**:
- **Pre-commit** (runs on `git commit`): Fast checks (~3 seconds)
  - Whitespace and formatting (ruff, trailing whitespace, etc.)
  - Python syntax validation
  - YAML/TOML validation
  - Secret detection
  - Autogenerated file regeneration

- **Pre-push** (runs on `git push`): Slow checks (~5 seconds)
  - Unit tests (tests/unit + tests/e2e)

**Manual control**:
```bash
just regenerate        # Manually regenerate autogenerated files
uv run pre-commit run --all-files  # Run all hooks on all files
uv run pre-commit run --hook-stage commit   # Run only commit-stage hooks
uv run pre-commit run --hook-stage push     # Run only push-stage hooks
```

**Bypass hooks** (use carefully):
```bash
git commit --no-verify   # Skip pre-commit hooks (not recommended)
git push --no-verify     # Skip pre-push hooks (not recommended)
```

See `.pre-commit-config.yaml` for the full hook configuration.

#### Cleanup

```bash
just clean-generated   # Remove generated files
```

### How to Use

#### I just want to write a paper

1. Follow [Getting Started Guide](docs/getting-started-external.md)
2. Clone the example, edit `model.py`, run `just paper`
3. Cite math-trace in your paper (see citation below)

#### I want to contribute a domain example

1. Follow [Contributing Guide](CONTRIBUTING.md)
2. Add your example to `examples/`
3. Include tests and Lean formalization (optional but encouraged)
4. Open a PR

#### I want to use math-trace as a library

```python
from math_trace import SymPyToTypst
import sympy as sp

converter = SymPyToTypst()
expr = sp.Symbol("x") ** 2 + 1
typst_code = converter.convert(expr)
print(typst_code)
```

See API docs in docstrings and examples in `tests/`.

#### I want to formalize my theorem

See `examples/membrane-dynamics/lean/` for the pattern. Optional: register with [Palomar](https://palomar-registry.org).

### Citation

If you use math-trace in your research, please cite:

```bibtex
@software{mathTrace2026,
  author = {Alexiuk, Mark},
  title = {math-trace: Formula-to-code traceability for research papers},
  year = {2026},
  url = {https://github.com/baseline0/math-trace},
  howpublished = {\url{https://pypi.org/project/math-trace/}}
}
```

### For Fleet Members

This repository is part of the mathematical research fleet. For fleet-specific commands and infrastructure integration, see [CLAUDE.md](CLAUDE.md).

### References

#### SymPy & Mathematics
- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy Printing (LaTeX)](https://docs.sympy.org/latest/modules/printing/latex.html)

#### Typst
- [Typst Documentation](https://typst.app/docs/)
- [Typst Packages](https://typst.app/packages/)
- [Why Typst](docs/adr/ADR-001-typst-over-latex.md)

#### Lean & Formal Verification
- [Lean 4 Manual](https://lean-lang.org/lean4/doc/)
- [Mathlib Documentation](https://mathlib4.github.io/)

#### Registry & Publication
- [Palomar Formalization Registry](https://palomar-registry.org)
- [Traceability Design](docs/adr/ADR-003-code-linked-traceability.md)

### Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to add your domain example
- Code standards
- PR process
- Where to get help

### License

MIT — See [LICENSE](LICENSE) for details.

### Support

- **Questions?** Open a [GitHub Discussion](https://github.com/baseline0/math-trace/discussions)
- **Bug reports?** File an [issue](https://github.com/baseline0/math-trace/issues)
- **Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Why math-trace?**

Rigorous mathematics deserves rigorous traceability. Every equation should link to its proof, every theorem to its formalization, every formula to the code that uses it. With math-trace, one edit to `model.py` updates your entire paper—formulas, figures, proofs, and all.
