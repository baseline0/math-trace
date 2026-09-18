# math-trace

**Formula-to-code traceability for publication-quality mathematical documents.**

Typst + Python for rigorous research papers where every equation links back to its implementation and formal proofs.

## Quick Start

```bash
cd examples/membrane-dynamics
just paper
```

This generates `main.pdf` with equations, theorems, and simulation figures—all derived from `model.py`.

Requirements:
- Python 3.11+
- uv package manager
- Typst compiler (`cargo install typst-cli`)

## The Demo: Stochastic P Systems

We demonstrate complete end-to-end traceability using a minimal membrane computing example:

### The Model

Rule `2a → b` with stochastic mass-action kinetics.

**Source of truth**: `examples/membrane-dynamics/model.py:25`

```python
import sympy as sp
k = sp.Symbol('k', positive=True, real=True)
n_a = sp.Symbol('n_a', positive=True, integer=True)
rate_expr = k * sp.binomial(n_a, 2)  # Rate law: r = k * n_a * (n_a - 1) / 2
```

### The Paper

Typst document that imports formulas from the model:

```typst
#figure(
  align(center, rate_formula),
  caption: [Rate law (from model.py:25)]
)
```

### The Simulation

Stochastic realization evaluates the rate law:

```python
# simulate.py
rate = k_val * na * (na - 1) / 2  # Matches model.py:25
```

### The Formalization

Lean proof of monotonicity:

```lean
-- Challenge.lean: Derived from model.py:25
def rate (k : ℝ) (n : ℕ) : ℝ := k * (n : ℝ) * ((n : ℝ) - 1) / 2

theorem rate_strictly_increasing (k : ℝ) (hk : 0 < k) :
    ∀ n m : ℕ, 2 ≤ n → n < m → rate k n < rate k m := by ...
```

### Traceability Chain

```
model.py (SymPy formulas - SOURCE OF TRUTH)
    ↓
formulas.typ (LaTeX → Typst conversion)
    ↓
main.typ (Typst paper with equations, theorem, figure)
    ↓
main.pdf (compiled document)
    ↓
lean/Challenge.lean (formal theorem statement)
    ↓
lean/Solution.lean (formal proof)
    ↓
lean/comparator.json (verification of correspondence)
    ↓
Palomar Registry (formalization registration)
```

## Workflow

### 1. Build the Paper

```bash
just paper
```

This runs:
1. `model.py` → exports formulas to JSON
2. JSON → `generated/formulas.typ` (LaTeX → Typst conversion)
3. `simulate.py` → stochastic trajectories
4. Matplotlib → `generated/figures/simulation.png`
5. Typst compiler → `main.pdf`

### 2. Adapt to Your Domain

Replace `examples/membrane-dynamics/model.py` with your formulas:

```python
# model.py
import sympy as sp

# Define your symbols and equations
x = sp.Symbol('x', real=True)
y = sp.Symbol('y', positive=True)

# Your formula
my_formula = sp.exp(-x**2) * sp.sqrt(y)

# Wrap in Formula class
FORMULAS = {
    'my_formula': Formula(
        name='my_formula',
        expr=my_formula,
        description='My important equation',
        source_line=15
    )
}
```

Then:
1. Run `just model` to export formulas
2. Edit `main.typ` to import and use your formulas
3. Run `just paper` to build

### 3. Add Your Simulation

Replace `simulate.py` with your own numerical computations:

```python
# simulate.py
def compute(param1, param2):
    # Your simulation logic
    return results
```

Update `build_paper.py` to generate your figures.

### 4. Formalize Your Theorem

Add Lean proof in `lean/Challenge.lean`:

```lean
theorem my_theorem : ... := by
  sorry  -- Your proof here
```

Register in Palomar with `lean/formalization.yaml`.

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

## For New Users

1. **Understand the demo**: Read `examples/membrane-dynamics/` end-to-end
   - Start with `model.py` (formulas in SymPy)
   - Read `simulate.py` (how formulas are used)
   - Read `main.typ` (how equations appear in paper)
   - Read `lean/Challenge.lean` (how theorems are formalized)

2. **Run the build**: `just paper` → generates `main.pdf`

3. **Adapt the example**: Replace formulas in `model.py` with your own

4. **Add your simulation**: Modify `simulate.py` to compute your results

5. **Formalize your theorem**: Extend `lean/Challenge.lean` with your proof

6. **Register in Palomar**: Fill out `lean/formalization.yaml` and submit

## Integration with Fleet

This repository is part of the mathematical research fleet. For fleet-specific setup and commands, see [CLAUDE.md](CLAUDE.md).

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

## License

MIT

## Authors

- Mark Alexiuk (@baseline0)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Add your mathematical example to `examples/`
3. Include tests in `tests/examples/`
4. Document design decisions in `docs/adr/`
5. Run `just test` and `just typecheck` before submitting
6. Open a PR with reference to Palomar entry (if formalizing)

---

**Why math-trace?** Because rigorous mathematics deserves rigorous traceability. Every equation should link to its proof, every theorem to its formalization, every formula to the code that uses it.
