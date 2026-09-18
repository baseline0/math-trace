# Contributing to math-trace

## Welcome!

We'd love to have you contribute to math-trace. Whether you're adding a new domain example, fixing a bug, or improving documentation—contributions make the project better for everyone.

This is an **open project** for researchers, mathematicians, and scientists. We want your domain examples, your ideas, and your feedback.

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/math-trace.git
cd math-trace
```

### 2. Set Up Your Environment

```bash
# Install dependencies
uv sync

# Run tests to verify setup
uv run pytest tests/
```

### 3. Add Your Domain Example

The easiest way to contribute is to add a new domain example. We include a template:

```bash
cp -r examples/membrane-dynamics examples/your-domain
cd examples/your-domain
```

#### Structure

Each domain example has:

```
examples/your-domain/
├── model.py              # SymPy formulas (SOURCE OF TRUTH)
├── simulate.py           # Simulation logic (uses model.py)
├── build_paper.py        # Build orchestration
├── main.typ              # Typst paper template
├── generated/            # Auto-generated (ignore in git)
│   ├── formulas.typ
│   └── figures/
└── lean/                 # Optional: Lean formalization
    ├── Challenge.lean
    ├── Solution.lean
    └── formalization.yaml
```

### 4. Write Your Model

`model.py` contains **all formulas** (source of truth):

```python
import sympy as sp
from dataclasses import dataclass

@dataclass
class Formula:
    name: str
    expr: sp.Expr
    description: str
    source_line: int

# Define your domain
# Example: Quantum mechanics
hbar = sp.Symbol('hbar', positive=True, real=True)
m = sp.Symbol('m', positive=True, real=True)
x = sp.Symbol('x', real=True)

# Schrödinger equation (simplified form)
kinetic_energy = -hbar**2 / (2 * m) * sp.Symbol('d2psi_dx2')

# Export formulas for paper
FORMULAS = {
    'kinetic': Formula(
        name='kinetic_energy',
        expr=kinetic_energy,
        description='Kinetic energy term',
        source_line=20
    )
}
```

### 5. Write Your Simulation

`simulate.py` **must use the exact formulas from model.py**:

```python
# simulate.py
from model import FORMULAS
import numpy as np

# Extract formula
kinetic_formula = FORMULAS['kinetic'].expr

# Evaluate or use in computation
# Your simulation code here
```

### 6. Write Your Paper

`main.typ` imports and displays formulas:

```typst
#import "generated/formulas.typ": *

#align(center, [
  = My Domain Example

  The kinetic energy is:
  
  $ #kinetic_energy_formula $
])
```

### 7. Add Tests

Create `tests/examples/test_your_domain.py`:

```python
def test_model_export():
    """Verify model formulas export correctly."""
    from examples.your_domain.model import FORMULAS
    
    assert 'kinetic' in FORMULAS
    assert FORMULAS['kinetic'].expr is not None

def test_simulation_uses_model():
    """Verify simulation uses model formulas."""
    # Your test verifying formulas ↔ code correspondence
    pass
```

### 8. Run Tests

```bash
uv run pytest tests/examples/test_your_domain.py -v
```

### 9. Optional: Formalize Your Theorem

Add Lean proofs to `lean/Challenge.lean`:

```lean
import Mathlib

-- Derived from model.py:20
def kinetic_energy (hbar m x : ℝ) : ℝ :=
  -(hbar ^ 2 / (2 * m))

theorem kinetic_is_bounded (hbar m : ℝ) :
    hbar > 0 → m > 0 → True := by
  sorry  -- Your proof here
```

See `examples/membrane-dynamics/lean/` for a complete example.

## Code Standards

### Python

- **Type hints required** for all functions (PEP 484)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Keep functions under ~50 lines
- Document WHY, not WHAT (code-as-docs philosophy)
- Write docstrings for public functions

Example:

```python
def convert_formula(expr: sp.Expr) -> str:
    """
    Convert SymPy expression to Typst notation.
    
    Args:
        expr: SymPy expression
        
    Returns:
        Typst-formatted string
    """
    latex = sp.latex(expr)
    return latex_to_typst(latex)
```

### Tests

- Use `pytest`
- Test both happy path and edge cases
- Name tests clearly: `test_<feature>_<scenario>`
- Run full suite before submitting: `uv run pytest tests/`

### Typst

- Use descriptive variable names
- Keep templates simple
- Document assumptions (e.g., "assumes formulas.typ exists")

## Git Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-domain
# or
git checkout -b fix/issue-name
```

### 2. Make Changes

```bash
# Edit model.py, simulate.py, tests, etc.
# Commit frequently with clear messages
git add examples/your-domain/
git commit -m "Add your-domain example with model and simulation"
```

### 3. Push & Create PR

```bash
git push origin feature/your-domain
```

Then open a PR on GitHub with:

- **Title**: "Add your-domain example" or "Fix: brief description"
- **Description**:
  - What domain does this example demonstrate?
  - Any optional: link to Palomar formalization (if applicable)
  - Any blockers or questions?

### 4. Code Review

- Respond to feedback promptly
- Re-run tests: `uv run pytest tests/`
- Make sure linting passes: `uv run ruff check .`

### 5. Merge

Once approved, a maintainer will merge your PR.

## Checklist Before Submitting

- [ ] Code follows PEP 8 and includes type hints
- [ ] All tests pass: `uv run pytest tests/`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Docstrings written (code-as-docs)
- [ ] Example runs: `cd examples/your-domain && just paper`
- [ ] Commit messages are clear
- [ ] PR description explains what's being added

## Questions & Help

### Getting Help

- **Usage questions?** Open a [GitHub Discussion](https://github.com/baseline0/math-trace/discussions/new?category=q-a)
- **Found a bug?** File an [issue](https://github.com/baseline0/math-trace/issues/new)
- **Need guidance?** Comment on a PR or discussion—maintainers are here to help

### Where to Learn

- [README.md](README.md) — Overview and quick start
- [docs/getting-started-external.md](docs/getting-started-external.md) — User guide
- [examples/membrane-dynamics/](examples/membrane-dynamics/) — Complete working example
- [docs/adr/](docs/adr/) — Architecture decisions
- Tests in `tests/` — Usage patterns

## What We're Looking For

### ✅ Great Contributions

- New domain examples (physics, biology, ML, topology, etc.)
- Bug fixes with tests
- Documentation improvements
- Performance improvements (with benchmarks)
- Better error messages
- Template improvements

### ❌ Out of Scope

- Changes to core architecture (open discussion first)
- New dependencies (discuss in issue first)
- Removing examples (they stay for reference)

## Code of Conduct

- Be respectful and collaborative
- Assume good intent
- Welcome diverse perspectives
- Help others learn

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to math-trace!** Your domain examples, fixes, and ideas make this project better for every researcher using it. 🎓
