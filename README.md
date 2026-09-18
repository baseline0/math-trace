# math-trace

**Write publication-quality papers where every equation links back to code.**

Formula-to-code traceability for researchers who want reproducible mathematics. SymPy → Typst → PDF, with optional Lean formalization and Palomar registry integration.

## Quick Install & Try

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

## What Is math-trace?

Every formula in your paper should link to the code that uses it. Every theorem should have a proof. Every proof should be verified.

math-trace connects:
- **SymPy formulas** (Python) → source of truth
- **Typst paper** (typesetting) → equations in your PDF
- **Simulations** (matplotlib/numpy) → figures validated against formulas
- **Lean proofs** (optional) → formal verification
- **Palomar registry** (optional) → publication registration

One edit to `model.py` updates your paper automatically.

### Requirements

- Python 3.11+
- `pip install math-trace`
- Optional: Typst compiler (`just install-typst` for PDF generation)
- Optional: Lean 4 (for formal proofs)

## Example: Stochastic P Systems

The included example demonstrates end-to-end formula traceability:

### Step 1: Define Formulas in Python

`examples/membrane-dynamics/model.py` (source of truth):

```python
import sympy as sp

k = sp.Symbol('k', positive=True, real=True)
n_a = sp.Symbol('n_a', positive=True, integer=True)
rate_expr = k * sp.binomial(n_a, 2)  # Rate law: r = k * n_a * (n_a - 1) / 2
```

### Step 2: Use Formulas in Paper

`main.typ` imports and displays:

```typst
#figure(
  align(center, $k binomial(n_a, 2)$),
  caption: [Rate law (from model.py:25)]
)
```

### Step 3: Validate with Simulation

`simulate.py` uses the same formula:

```python
# This MUST match model.py:25 exactly
rate = k_val * na * (na - 1) / 2
```

Tests verify code ↔ formula equivalence.

### Step 4: Formalize (Optional)

`lean/Challenge.lean` states the theorem:

```lean
def rate (k : ℝ) (n : ℕ) : ℝ := k * (n : ℝ) * ((n : ℝ) - 1) / 2
```

### The Traceability Chain

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

## Getting Started (5 Minutes)

### For Users: Just Use It

See [Getting Started Guide](docs/getting-started-external.md) for:
- Installation (1 minute)
- Running the example (2 minutes)
- Adapting to your domain (2 minutes)

### For Contributors: Fork a Template

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

### For Contributors: Add Your Domain

See [Contributing Guide](CONTRIBUTING.md) to:
- Fork and clone
- Create your domain example
- Submit a PR

### Full Workflow

**1. Clone template** (or use `pip install math-trace` + example from GitHub)

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace/examples/membrane-dynamics
```

**2. Edit `model.py`** with your formulas

```python
import sympy as sp

# Your symbols
k, n = sp.symbols('k n', positive=True)

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

## Project Structure

```
math-trace/
├── README.md                    # This file
├── CLAUDE.md                    # Fleet integration
├── Justfile                     # Build recipes
├── pyproject.toml              # Python dependencies
│
├── src/math_trace/             # Reusable library
│   ├── __init__.py
│   ├── generators.py           # SymPy → Typst converters
│   └── templates/              # Typst/Lean templates
│
├── examples/
│   └── membrane-dynamics/      # Complete working example
│       ├── model.py            # SymPy formulas (SOURCE OF TRUTH)
│       ├── simulate.py         # Stochastic simulation
│       ├── build_paper.py      # Build orchestration
│       ├── main.typ            # Typst paper
│       ├── generated/          # Auto-generated (ignored in git)
│       │   ├── formulas.typ
│       │   └── figures/
│       └── lean/               # Lean formalization
│           ├── Challenge.lean
│           ├── Solution.lean
│           ├── comparator.json
│           └── formalization.yaml
│
├── templates/                  # Fork-friendly templates by domain
│   ├── TEMPLATE-USAGE.md       # Master guide for customizing templates
│   ├── simple-physics/         # Template: Classical mechanics
│   │   ├── model.py, simulate.py, build_paper.py, main.typ, README.md
│   └── biochemistry/           # Template: Enzyme kinetics
│       ├── model.py, simulate.py, build_paper.py, main.typ, README.md
│
├── tests/                      # Test suite
│   ├── test_model_export.py    # Formula generation tests
│   └── examples/
│       └── test_membrane_end_to_end.py
│
├── docs/
│   └── adr/                    # Architecture Decision Records
│       ├── ADR-001-typst-over-latex.md
│       ├── ADR-002-python-first-formulas.md
│       └── ADR-003-code-linked-traceability.md
│
└── scripts/                    # Utilities (optional)
```

## Standards & Philosophy

### Code-as-Docs

This project follows the fleet-base code-as-docs philosophy:

- **Formulas are code** (SymPy objects in Python)
- **Tests are documentation** (examples of how to use the system)
- **Type hints communicate intent** (don't write comments if the code is clear)
- **ADRs for decisions** (why Typst? why Python-first?)

See [docs/adr/](docs/adr/) for architecture decisions.

### Traceability

Every formula, theorem, and proof links to its source:

```python
# model.py
rate_formula = Formula(
    expr=k * sp.binomial(n_a, 2),
    source_line=25  # Always document where this comes from
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

## Building & Testing

### Build Commands

```bash
just model       # Export formulas from SymPy
just formulas    # Convert LaTeX → Typst
just simulate    # Run stochastic simulation
just figures     # Generate matplotlib figures
just pdf         # Compile Typst to PDF
just paper       # Full pipeline (model → figures → pdf)
```

### Testing

```bash
just test              # Run full test suite
just test-formulas     # Test formula generation
just test-model        # Test model definitions
just typecheck         # Type check Python code
```

### Cleanup

```bash
just clean             # Remove generated files
```

## How to Use

### I just want to write a paper

1. Follow [Getting Started Guide](docs/getting-started-external.md)
2. Clone the example, edit `model.py`, run `just paper`
3. Cite math-trace in your paper (see citation below)

### I want to contribute a domain example

1. Follow [Contributing Guide](CONTRIBUTING.md)
2. Add your example to `examples/`
3. Include tests and Lean formalization (optional but encouraged)
4. Open a PR

### I want to use math-trace as a library

```python
from math_trace import SymPyToTypst
import sympy as sp

converter = SymPyToTypst()
expr = sp.Symbol('x')**2 + 1
typst_code = converter.convert(expr)
print(typst_code)
```

See API docs in docstrings and examples in `tests/`.

### I want to formalize my theorem

See `examples/membrane-dynamics/lean/` for the pattern. Optional: register with [Palomar](https://palomar-registry.org).

## Citation

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

## For Fleet Members

This repository is part of the mathematical research fleet. For fleet-specific commands and infrastructure integration, see [CLAUDE.md](CLAUDE.md).

## References

### SymPy & Mathematics
- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy Printing (LaTeX)](https://docs.sympy.org/latest/modules/printing/latex.html)

### Typst
- [Typst Documentation](https://typst.app/docs/)
- [Typst Packages](https://typst.app/packages/)
- [Why Typst](docs/adr/ADR-001-typst-over-latex.md)

### Lean & Formal Verification
- [Lean 4 Manual](https://lean-lang.org/lean4/doc/)
- [Mathlib Documentation](https://mathlib4.github.io/)

### Registry & Publication
- [Palomar Formalization Registry](https://palomar-registry.org)
- [Traceability Design](docs/adr/ADR-003-code-linked-traceability.md)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to add your domain example
- Code standards
- PR process
- Where to get help

## License

MIT — See [LICENSE](LICENSE) for details.

## Support

- **Questions?** Open a [GitHub Discussion](https://github.com/baseline0/math-trace/discussions)
- **Bug reports?** File an [issue](https://github.com/baseline0/math-trace/issues)
- **Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Why math-trace?**

Rigorous mathematics deserves rigorous traceability. Every equation should link to its proof, every theorem to its formalization, every formula to the code that uses it. With math-trace, one edit to `model.py` updates your entire paper—formulas, figures, proofs, and all.
