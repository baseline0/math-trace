# Getting Started with math-trace

This guide is for researchers and mathematicians who want to **use math-trace** to write papers with formula-to-code traceability.

For **contributing** a domain example, see [CONTRIBUTING.md](../CONTRIBUTING.md).

**Time to first paper: 5 minutes** ⏱️

## What You Get

After following this guide, you'll have:

- A PDF paper with equations, theorems, and simulation figures
- Python formulas (SymPy) that directly feed into your paper
- Tests verifying your equations match your code
- Optional Lean proofs for formal verification

**Key insight**: One edit to `model.py` updates your entire paper automatically.

## Prerequisites

- Python 3.11 or later
- `pip` or `uv` package manager
- (Optional) Typst compiler for PDF generation: `cargo install typst-cli`
- (Optional) Lean 4 for formal proofs

## Installation

### Option A: From PyPI (Recommended)

```bash
pip install math-trace
```

### Option B: From Source

```bash
git clone https://github.com/baseline0/math-trace.git
cd math-trace
uv sync  # or: pip install -e .
```

## 30-Second Quick Start

```bash
# Clone the example
git clone https://github.com/baseline0/math-trace.git
cd math-trace/examples/membrane-dynamics

# Build the paper (requires Typst)
just paper

# View the result
open main.pdf
```

You should see a PDF with:
- Mathematical formula: "Rate law" equation
- Simulation figure: stochastic trajectories
- All traced back to `model.py`

## Adapt to Your Domain (5 minutes)

### Step 1: Copy the Template

```bash
cd math-trace/examples
cp -r membrane-dynamics my-domain
cd my-domain
```

### Step 2: Edit model.py

This is your **source of truth**. All formulas live here.

```python
# model.py
import sympy as sp
from dataclasses import dataclass

@dataclass
class Formula:
    name: str
    expr: sp.Expr
    description: str
    source_line: int

# Your symbols
k = sp.Symbol('k', positive=True, real=True)
n = sp.Symbol('n', positive=True, integer=True)

# Your formula
rate_law = k * sp.binomial(n, 2)

# Export for paper
FORMULAS = {
    'rate': Formula(
        name='rate_law',
        expr=rate_law,
        description='Reaction rate',
        source_line=15  # Where this formula is defined
    )
}
```

### Step 3: Update main.typ

Edit the Typst paper to use your formulas:

```typst
// main.typ
#import "generated/formulas.typ": *

#align(center, [
  = My Domain

  The rate follows:
  
  $ #rate_formula $  // From model.py
])
```

### Step 4: Edit simulate.py

Write code that uses your model:

```python
# simulate.py
from model import FORMULAS
import numpy as np

def compute(k_val, n_val, num_steps=1000):
    """Simulate using formula from model.py."""
    rate = k_val * n_val * (n_val - 1) / 2  # MUST match model.py
    
    # Your simulation logic
    results = []
    for step in range(num_steps):
        # Use rate_law
        pass
    
    return results
```

**Important**: The formula in `simulate.py` **must exactly match** `model.py`. Use tests to verify this.

### Step 5: Add Tests

Verify your formulas are correct:

```python
# tests/examples/test_my_domain.py
import pytest
from examples.my_domain.model import FORMULAS, rate_law
import sympy as sp

def test_rate_formula_defined():
    """Check that formula is exported."""
    assert 'rate' in FORMULAS
    assert FORMULAS['rate'].expr is not None

def test_rate_increases_with_n():
    """Check mathematical properties."""
    k_val = 2.0
    formula = FORMULAS['rate'].expr
    k, n = sp.symbols('k n', positive=True, integer=True)
    
    # At n=3: rate = 2 * C(3,2) = 2 * 3 = 6
    rate_at_3 = formula.subs([(k, k_val), (n, 3)])
    assert rate_at_3 == 6
    
    # At n=4: rate = 2 * C(4,2) = 2 * 6 = 12
    rate_at_4 = formula.subs([(k, k_val), (n, 4)])
    assert rate_at_4 == 12
    
    assert rate_at_4 > rate_at_3
```

### Step 6: Build Your Paper

```bash
# Generate formulas (SymPy → Typst)
just model

# Generate figures (simulation → matplotlib)
just simulate

# Compile to PDF
just pdf

# Or do all at once
just paper
```

View your paper:

```bash
open main.pdf
```

## Optional: Add Formal Proofs

If you want to prove your theorem formally:

### Step 1: Write the Theorem in Lean

`lean/Challenge.lean`:

```lean
import Mathlib

-- Derived from model.py:15
def rate_formula (k : ℝ) (n : ℕ) : ℝ :=
  k * (n * (n - 1) / 2)

theorem rate_is_increasing (k : ℝ) (hk : k > 0) :
    ∀ n m : ℕ, n < m → rate_formula k n < rate_formula k m := by
  sorry  -- Your proof here
```

### Step 2: Prove It

Implement the proof or leave `sorry` for later.

### Step 3: Register (Optional)

Create `lean/formalization.yaml`:

```yaml
theorem: rate_is_increasing
source: model.py:15
palomar_url: https://palomar-registry.org/...
```

Then submit to [Palomar Registry](https://palomar-registry.org) to make your formalization discoverable.

## Publishing Your Paper

Once your paper is ready:

### 1. Generate PDF

```bash
just paper
```

### 2. Export to arXiv or Journal

Use the generated `main.pdf` for submission.

### 3. Cite math-trace

In your acknowledgments or references:

```bibtex
@software{mathTrace2026,
  author = {Alexiuk, Mark},
  title = {math-trace: Formula-to-code traceability for research papers},
  year = {2026},
  url = {https://github.com/baseline0/math-trace}
}
```

### 4. Share Your Example (Optional)

If you'd like to contribute your domain example to math-trace:

1. Follow [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Open a PR
3. Your example helps other researchers in your field

## Common Tasks

### Change a Formula

Edit `model.py`:

```python
# OLD
rate_law = k * sp.binomial(n, 2)

# NEW
rate_law = k * sp.binomial(n, 2) + c  # Add constant term
```

Rebuild:

```bash
just paper  # Everything updates automatically
```

### Add Another Formula

```python
# model.py
FORMULAS = {
    'rate': Formula(...),
    'equilibrium': Formula(  # New formula
        name='equilibrium',
        expr=your_expression,
        description='Equilibrium concentration',
        source_line=30
    )
}
```

Update `main.typ` to display it, rebuild.

### Debug a Formula

Check what SymPy is generating:

```bash
python model.py  # If you add __main__ section
```

Or in Python:

```python
from examples.my_domain.model import FORMULAS
import sympy as sp

formula = FORMULAS['rate']
print(f"Expression: {formula.expr}")
print(f"LaTeX: {sp.latex(formula.expr)}")
```

### Verify Formula ↔ Code Correspondence

Always match your simulation code to your model:

```python
# model.py
rate = k * sp.binomial(n, 2)

# simulate.py
# This MUST be mathematically equivalent
rate = k_val * n_val * (n_val - 1) / 2  # C(n,2) = n*(n-1)/2
```

Write tests to verify:

```python
def test_simulation_matches_model():
    """Formula in code matches model.py."""
    k_val, n_val = 2.0, 5
    
    # From model.py
    from model import FORMULAS
    formula_result = FORMULAS['rate'].expr.subs(
        [(sp.Symbol('k'), k_val), (sp.Symbol('n'), n_val)]
    )
    
    # From simulate.py
    simulation_result = k_val * n_val * (n_val - 1) / 2
    
    assert formula_result == simulation_result
```

## Troubleshooting

### "just paper" fails

Check prerequisites:

```bash
# Python version
python --version  # Should be 3.11+

# Typst installed?
typst --version

# Dependencies?
pip install -e .
```

### "Formula not found in generated/formulas.typ"

Check that:

1. You defined formula in `model.py`
2. You exported it in `FORMULAS` dict
3. You ran `just model` (generates the .typ file)

### "Simulation doesn't match formula"

Verify mathematical equivalence:

```python
from examples.my_domain.model import FORMULAS
import sympy as sp

# Check derivative, integrals, etc.
formula = FORMULAS['rate'].expr
print(sp.latex(formula))

# Your code should implement this exactly
```

## Next Steps

- **Explore examples**: Study `examples/membrane-dynamics/` end-to-end
- **Read code**: Type hints and docstrings in `src/math_trace/` show all APIs
- **Formalize**: Add Lean proofs (optional, but encouraged)
- **Contribute**: Share your domain example ([CONTRIBUTING.md](../CONTRIBUTING.md))
- **Ask questions**: Open a [GitHub Discussion](https://github.com/baseline0/math-trace/discussions)

## File Organization

```
your-paper/
├── model.py              # SymPy formulas (EDIT THIS)
├── simulate.py           # Your simulation (EDIT THIS)
├── build_paper.py        # Build orchestration (usually don't touch)
├── main.typ              # Typst paper (EDIT THIS)
├── Justfile              # Build recipes
├── generated/            # Auto-generated (DON'T EDIT)
│   ├── formulas.typ
│   └── figures/
├── lean/                 # Optional: proofs
│   ├── Challenge.lean
│   ├── Solution.lean
│   └── formalization.yaml
└── tests/                # Your tests
    └── test_model.py
```

## Key Principles

1. **model.py is source of truth** — All formulas live there
2. **One edit, everything updates** — Change a formula, rebuild paper
3. **Code matches formulas** — Tests verify correspondence
4. **Formalization is optional** — Add Lean proofs if you want rigor
5. **Traceability is automatic** — Formulas automatically link to source lines

---

**Ready to write your paper?** Start with the 30-second quick start above, then adapt the example to your domain. Questions? Open a discussion on GitHub or read the [CONTRIBUTING guide](../CONTRIBUTING.md).

Happy researching! 🎓
