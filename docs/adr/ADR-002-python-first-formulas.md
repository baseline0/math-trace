# ADR-002: Python (SymPy) as Source of Truth for Mathematical Formulas

## Status
Accepted

## Context

Mathematical papers contain symbolic equations that must be:
1. Verified to be correct
2. Used in simulations and code
3. Formalized and proven in theorem provers
4. Rendered in multiple formats (LaTeX, Typst, plain text)

Where should these formulas live?

Options:
- **Typst/LaTeX**: Direct in the paper (hard to reuse, hard to verify)
- **Python/SymPy**: Symbolic mathematics in code (testable, reusable, derivable)
- **Separate formula file** (YAML, JSON): Loses symbolic reasoning

## Decision

Maintain the **source of truth in Python (SymPy)** for all symbolic formulas.

All papers, simulations, and formalizations derive from this Python definition.

## Rationale

### Source of Truth Benefits
1. **Testable**: Write unit tests to verify formula properties
2. **Reusable**: Same formula used in simulation, proof, and paper
3. **Derivable**: Can auto-generate from simpler definitions
4. **Version Controlled**: Formulas are code, tracked in git
5. **Symbolic**: Can manipulate formulas algebraically in Python

### Example: Rate Law

```python
# model.py - SOURCE OF TRUTH
k = sp.Symbol('k', positive=True, real=True)
n_a = sp.Symbol('n_a', positive=True, integer=True)
rate_expr = k * sp.binomial(n_a, 2)
```

Then:
1. **Paper**: `main.typ` imports generated LaTeX
2. **Simulation**: `simulate.py` evaluates `rate` numerically
3. **Proof**: `lean/Challenge.lean` formalizes the definition
4. **Traceability**: All reference `model.py:line`

## Consequences

### Positive
- Single source eliminates inconsistency
- Formulas can be tested and verified
- Easy to update formula globally
- Clear dependency chain: Python → Typst → PDF

### Negative
- Requires Python/SymPy infrastructure
- Developers must be comfortable with symbolic math syntax
- Extra build step (SymPy → LaTeX → Typst)

## Alternatives Considered

### Formulas in LaTeX/Typst
❌ Hard to verify and test
❌ Duplication if used in code
❌ Manual sync required

### Separate formula database (YAML/JSON)
❌ Loses symbolic reasoning
❌ Harder to derive related formulas
❌ Requires custom parsing

## Implementation

1. Write all mathematical formulas in Python/SymPy in `model.py`
2. Add `.to_latex()` method to each formula for export
3. Build pipeline: SymPy → LaTeX → Typst (automatic)
4. Write tests in `tests/test_model_export.py` to verify
5. Document formula source line in metadata (traceability)

## Code Pattern

```python
# model.py
from dataclasses import dataclass
import sympy as sp

@dataclass
class Formula:
    name: str
    expr: sp.Expr
    description: str
    source_line: int
    
    def to_latex(self) -> str:
        return sp.latex(self.expr)

FORMULAS = {
    'rate': Formula(
        name='rate',
        expr=k * sp.binomial(n_a, 2),
        description='Rate law for 2a → b',
        source_line=25
    )
}
```

## Verification

- Unit tests verify formula properties (monotonicity, bounds, etc.)
- Integration tests verify export pipeline
- Manual review: compare generated LaTeX with paper
- Formal verification: Lean proof must match formula

## References

- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy LaTeX Printing](https://docs.sympy.org/latest/modules/printing/latex.html)
- [Code-as-Docs Philosophy](../../README.md#code-as-docs)
