# ADR-002: Python (SymPy) as Source of Truth for Mathematical Formulas

## Status
Accepted

## Context

Mathematical papers contain symbolic equations that must be:
1. Verified to be correct
2. Used in simulations and code
3. Formalized and proven in theorem provers
4. Rendered in multiple formats (LaTeX, Typst, plain text)

Where should these formulas live? Options: Typst/LaTeX directly in the paper (hard to reuse and
verify), Python/SymPy (testable, reusable, derivable), or a separate YAML/JSON formula file
(loses symbolic reasoning).

## Decision

Maintain the **source of truth in Python (SymPy)** for all symbolic formulas.

All papers, simulations, and formalizations derive from this Python definition.

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

## Guard

`tests/unit/test_model_export.py` verifies that formulas generated from the Python model export
correctly to the paper formats.

## Review-by

2027-04-30
