# math-trace Configuration

**Formula-to-code traceability for publication-quality mathematical documents.**

For universal rules, see `~/.claude/CLAUDE.md`.

## Quick Commands

All git and build commands go through `just`:

```bash
just paper             # Build complete PDF (model → formulas → figures → pdf)
just test              # Run test suite
just clean             # Remove generated files
just help              # Show all recipes
```

**NEVER run raw `git commit`, `git push`, or `uv run pytest` directly.**
Always use `just` recipes.

## Project Context

**Purpose**: Demonstrate complete end-to-end traceability for published mathematics:
- Python (SymPy) formulas → Typst paper → Lean formalization → Palomar registry

**Key Modules**:
- `src/math_trace/generators.py` — SymPy → LaTeX/Typst converters
- `examples/membrane-dynamics/model.py` — Source of truth for formulas
- `examples/membrane-dynamics/simulate.py` — Stochastic simulation (uses formulas)
- `examples/membrane-dynamics/main.typ` — Typst paper (imports formulas)
- `examples/membrane-dynamics/lean/` — Lean formalization + Palomar metadata

**Design Philosophy**:
- **Code-as-docs**: Formulas in Python (SymPy) are source of truth, not equations in paper
- **Tests as documentation**: See `tests/examples/test_membrane_end_to_end.py` for full workflow
- **Traceability**: Every formula tagged with source line (e.g., `model.py:25`)

## Dependencies

### Python
- `sympy>=1.12` — Symbolic mathematics
- `numpy>=1.24` — Numerical computing
- `matplotlib>=3.8` — Figure generation
- `pytest>=7.4` — Testing (dev only)

### System
- `typst` — Typst compiler for PDFs (install: `cargo install typst-cli`)
- `python>=3.11` — Python runtime

## Building the Paper

Complete workflow (formula → simulation → figures → PDF):

```bash
just paper
```

Individual steps:
```bash
just model       # SymPy → JSON (source of truth export)
just formulas    # JSON → formulas.typ (LaTeX → Typst)
just simulate    # Run simulation (uses rate formula from model.py)
just figures     # Generate PNG figures
just pdf         # Compile Typst to PDF
```

## Testing & Verification

```bash
just test              # Full test suite (unit + integration)
just test-formulas     # Test formula generation pipeline
just test-model        # Test model.py definitions
just typecheck         # Type check Python code
```

Tests verify:
- Formulas export correctly from SymPy
- LaTeX → Typst conversion works
- Simulation runs deterministically
- All generated artifacts exist

## Adapting the Example

To use this template for your own mathematics:

1. **Edit `model.py`**: Replace formulas with yours
   ```python
   # model.py
   my_formula = sp.exp(-x**2) + sp.sqrt(y)
   FORMULAS = {'my_formula': Formula(...)}
   ```

2. **Update `simulate.py`**: Replace simulation logic
   ```python
   # simulate.py
   def simulate(...):
       # Your numerical code here
   ```

3. **Edit `main.typ`**: Update paper text and figures

4. **Extend `lean/Challenge.lean`**: Formalize your theorem

5. **Run `just paper`**: Build your document

6. **Register in Palomar**: Fill `lean/formalization.yaml`

## Code Standards

**Python**:
- Type hints on all functions (PEP 484)
- Docstrings for public classes/functions (Google style)
- Tests for formula properties (monotonicity, bounds, etc.)
- No bare `except:` clauses

**Typst**:
- Comments explain mathematical intent (not what the code does)
- Consistent spacing and indentation
- Links to source code (e.g., "from model.py:25")

**Lean**:
- Document source of truth (e.g., `/-- Derived from model.py:25 --/`)
- Use Mathlib conventions
- Include informal proof sketches in comments

## Traceability Standards

Every formula must have:

```python
# model.py
FORMULAS = {
    'rate': Formula(
        name='rate',
        expr=k * sp.binomial(n_a, 2),
        description='Rate law for 2a → b',
        source_line=25  # Always document this
    )
}
```

Then reference in paper and proof:
```typst
// main.typ
#figure(..., caption: [Rate law (from model.py:25)])
```

```lean
-- Challenge.lean
/-- Derived from model.py:25 -/
def rate (k : ℝ) (n : ℕ) : ℝ := ...
```

## Git Workflow

Use `just commit` for all commits:

```bash
git status                    # Check what changed
git add path/to/file          # Stage specific files
just commit                   # Use `just` to commit (not raw git)
```

Commit messages should:
- Reference source of truth when adding formulas
- Link to ADR when making design decisions
- Note if this is a paper update or code update

Example:
```
refactor: Simplify rate formula in model.py:25

The binomial coefficient is now computed directly as n*(n-1)/2
for clarity in simulations. Typst paper regenerated automatically.

Related: ADR-002-python-first-formulas.md
```

## Extending the Framework

### Add a New Example

1. Create `examples/my-domain/` with `model.py`, `simulate.py`, `main.typ`
2. Add integration test in `tests/examples/test_my_domain.py`
3. Document in `examples/my-domain/README.md`

### Add a New Formula Converter

1. Extend `src/math_trace/generators.py` with new converter
2. Add tests in `tests/test_generators.py`
3. Update build pipeline in `examples/*/build_paper.py`

### Add a New Output Format

1. If not LaTeX/Typst, create adapter in `src/math_trace/converters/`
2. Wire into `build_paper.py` pipeline
3. Test in end-to-end test

## Troubleshooting

### `typst` not found
```bash
cargo install typst-cli
```

### Formulas not generating
```bash
cd examples/membrane-dynamics
uv run python model.py          # Check export
uv run python build_paper.py    # Run full pipeline
```

### Tests fail
```bash
just test -v                    # Verbose output
cd examples/membrane-dynamics && uv run python simulate.py  # Test simulation
```

## References

- **ADR-001**: [Why Typst](docs/adr/ADR-001-typst-over-latex.md)
- **ADR-002**: [Python-first formulas](docs/adr/ADR-002-python-first-formulas.md)
- **ADR-003**: [Code-linked traceability](docs/adr/ADR-003-code-linked-traceability.md)
- [SymPy Docs](https://docs.sympy.org/)
- [Typst Docs](https://typst.app/docs/)
- [Palomar Registry](https://palomar-registry.org)

## Questions?

See `README.md` for high-level overview or `examples/membrane-dynamics/` for working example.
