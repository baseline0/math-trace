# ADR-002 and ADR-003: Implementation Notes

Detail removed from docs/adr/ADR-002-python-first-formulas.md and docs/adr/ADR-003-code-linked-traceability.md.
The decisions are in those ADRs; this file holds the rationale, examples, paths and commands.
Line numbers from the original text are kept here as history, each tied to commit 925e5a4 (the commit that
introduced the examples), so the references stay resolvable.

## ADR-002: Rationale

### Source of Truth Benefits
1. **Testable**: Write unit tests to verify formula properties
2. **Reusable**: Same formula used in simulation, proof, and paper
3. **Derivable**: Can auto-generate from simpler definitions
4. **Version Controlled**: Formulas are code, tracked in git
5. **Symbolic**: Can manipulate formulas algebraically in Python

### Example: Rate Law

```python
# model.py - SOURCE OF TRUTH
k = sp.Symbol("k", positive=True, real=True)
n_a = sp.Symbol("n_a", positive=True, integer=True)
rate_expr = k * sp.binomial(n_a, 2)
```

Then:
1. **Paper**: `main.typ` imports generated LaTeX
2. **Simulation**: `simulate.py` evaluates `rate` numerically
3. **Proof**: `lean/Challenge.lean` formalizes the definition
4. **Traceability**: All reference `model.py:line`

## ADR-002: Alternatives Considered

### Formulas in LaTeX/Typst
- Hard to verify and test
- Duplication if used in code
- Manual sync required

### Separate formula database (YAML/JSON)
- Loses symbolic reasoning
- Harder to derive related formulas
- Requires custom parsing

## ADR-002: Implementation

1. Write all mathematical formulas in Python/SymPy in `model.py`
2. Add `.to_latex()` method to each formula for export
3. Build pipeline: SymPy → LaTeX → Typst (automatic)
4. Write tests in `tests/test_model_export.py` to verify
5. Document formula source line in metadata (traceability)

### Code Pattern

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
    "rate": Formula(name="rate", expr=k * sp.binomial(n_a, 2), description="Rate law for 2a → b", source_line=25)
}
```

## ADR-002: Verification

- Unit tests verify formula properties (monotonicity, bounds, etc.)
- Integration tests verify export pipeline
- Manual review: compare generated LaTeX with paper
- Formal verification: Lean proof must match formula

## ADR-002: References

- [SymPy Documentation](https://docs.sympy.org/)
- [SymPy LaTeX Printing](https://docs.sympy.org/latest/modules/printing/latex.html)
- [Code-as-Docs Philosophy](../../README.md#code-as-docs)

## ADR-003: Example: The Rate Law (was model.py:25 at 925e5a4)

1. **Source of truth** (model.py, 925e5a4):
   ```python
   rate_expr = k * sp.binomial(n_a, 2)  # Source: model.py:25
   ```

2. **Paper** (main.typ):
   ```typst
   #figure(
     align(center, rate),
     caption: [Rate law (from model.py:25)]
   )
   ```

3. **Simulation** (simulate.py:45):
   ```python
   rate = k_val * na * (na - 1) / 2  # Matches model.py:25
   ```

4. **Formalization** (lean/Challenge.lean:14):
   ```lean
   -- Derived from model.py:25
   def rate (k : ℝ) (n : ℕ) : ℝ := k * (n : ℝ) * ((n : ℝ) - 1) / 2
   ```

5. **Metadata** (lean/comparator.json):
   ```json
   {
     "source_of_truth": "examples/membrane-dynamics/model.py:25",
     "paper_reference": "examples/membrane-dynamics/main.typ (Theorem 1, Section 2)",
     "lean_formalization": "examples/membrane-dynamics/lean/Challenge.lean"
   }
   ```

## ADR-003: Benefits

### For Authors
- Auto-detect inconsistencies: formula in paper vs. code
- Regression testing: theorem statement must match formalization
- Easy updates: change formula once, update everywhere

### For Readers
- Click through from paper to code
- Inspect implementations behind claims
- Verify proofs are correct
- Reproduce results

### For Forking
- New users can adapt `model.py` without breaking paper/proof links
- Traceability aids understanding of what changed

## ADR-003: Rationale

Mathematical papers must be reproducible and verifiable. Code-linked traceability:
- Enables readers to inspect implementations
- Allows automated verification (tests, type checking)
- Prevents drift between paper and code
- Supports formal verification workflows

## ADR-003: Implementation

### 1. Metadata in Source Code
```python
# model.py
@dataclass
class Formula:
    name: str
    expr: sp.Expr
    description: str
    source_line: int  # Where this formula is defined
```

### 2. Reference in Papers
```typst
// main.typ
#figure(
  align(center, rate),
  caption: [Rate law (from model.py:25)]
)
```

### 3. Reference in Proofs
```lean
-- lean/Challenge.lean
/-- Rate function for rule 2a → b under mass-action kinetics.
    This definition is derived from model.py:25.
-/
def rate (k : ℝ) (n : ℕ) : ℝ := ...
```

### 4. Verification Metadata
```json
// lean/comparator.json
{
  "source_of_truth": "examples/membrane-dynamics/model.py:25",
  "paper_reference": "examples/membrane-dynamics/main.typ (Theorem 1, Section 2)",
  "lean_formalization": "examples/membrane-dynamics/lean/Challenge.lean"
}
```

### 5. Registry Entry
```yaml
# lean/formalization.yaml
code_of_truth:
  system: "Python + SymPy"
  file: "examples/membrane-dynamics/model.py"
  line: 25
  formula: "rate = k * n_a * (n_a - 1) / 2"
```

## ADR-003: Verification Workflow

1. **Tests verify traceability**:
   ```python
   # tests/examples/test_membrane_end_to_end.py
   def test_formula_metadata():
       rate = FORMULAS["rate"]
       assert rate.source_line == 25  # Points to model.py:25
   ```

2. **Build pipeline checks consistency**:
   - Extract formulas from model.py
   - Compare with LaTeX in paper
   - Verify Lean definition matches

3. **Manual review**:
   - Reviewer checks references point to correct lines
   - Verifies formula properties match paper claims

## ADR-003: Negative consequences and mitigation

- Line numbers break if code is refactored. Mitigation: use semantic versioning (formula name never changes,
  only implementation); write tests that verify traceability metadata; use git refs (commit hash) for
  permanent links; automate reference updates in CI/CD.

## ADR-003: References

- [Palomar Formalization Registry](https://palomar-registry.org)
- [Literate Programming](https://en.wikipedia.org/wiki/Literate_programming)
- [Code-as-Documentation](../../README.md#code-as-docs)
