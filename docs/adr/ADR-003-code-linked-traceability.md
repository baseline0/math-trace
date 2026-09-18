# ADR-003: Code-Linked Traceability Between Paper, Code, and Formal Proofs

## Status
Accepted

## Context

When publishing mathematical research, readers should be able to:
1. Verify that equations in the paper match the implementation
2. Inspect the code behind a theorem
3. Read the formal proof (Lean, Coq, etc.)
4. Understand how the paper relates to formalization

Current practice: These are often disconnected or scattered across repos.

## Decision

Implement **code-linked traceability**: Every formula, theorem, and proof
links back to its source with line numbers and git references.

## Rationale

### Trust and Reproducibility
Mathematical papers must be reproducible and verifiable. Code-linked traceability:
- Enables readers to inspect implementations
- Allows automated verification (tests, type checking)
- Prevents drift between paper and code
- Supports formal verification workflows

### Example: The Rate Law

In this repository:

1. **Source of truth** (model.py:25):
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

## Benefits

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

## Implementation

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

## Verification Workflow

1. **Tests verify traceability**:
   ```python
   # tests/examples/test_membrane_end_to_end.py
   def test_formula_metadata():
       rate = FORMULAS['rate']
       assert rate.source_line == 25  # Points to model.py:25
   ```

2. **Build pipeline checks consistency**:
   - Extract formulas from model.py
   - Compare with LaTeX in paper
   - Verify Lean definition matches

3. **Manual review**:
   - Reviewer checks references point to correct lines
   - Verifies formula properties match paper claims

## Consequences

### Positive
- Readers can trust paper-to-code correspondence
- Automated testing catches inconsistencies
- Clear path from publication to proof
- Supports reproducibility and verification

### Negative
- Requires discipline to maintain references
- Extra metadata fields
- Line numbers can break if code is refactored

## Mitigation

- Use semantic versioning: formula name never changes, only implementation
- Write tests that verify traceability metadata
- Use git refs (commit hash) for permanent links when needed
- Automate reference updates in CI/CD

## References

- [Palomar Formalization Registry](https://palomar-registry.org)
- [Literate Programming](https://en.wikipedia.org/wiki/Literate_programming)
- [Code-as-Documentation](../../README.md#code-as-docs)
