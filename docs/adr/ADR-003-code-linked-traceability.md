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
links back to its source with commit SHA references (see docs/adr-notes/ADR-002-ADR-003-implementation.md).

## Consequences

### Positive
- Readers can trust paper-to-code correspondence
- Automated testing catches inconsistencies
- Clear path from publication to proof
- Supports reproducibility and verification

### Negative
- Requires discipline to maintain references
- Extra metadata fields
- References go stale if code is refactored without updating them

## Guard

`tests/unit/test_template_metadata.py` checks that recorded code references and lines match the
code they name; `tests/unit/test_code_refs.py` checks that code_ref symbols resolve to their definition.

## Review-by

2027-04-30
