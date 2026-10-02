# Documentation

This directory contains all documentation for math-trace, organized by purpose.

## Directories

### **adr/** — Architecture Decision Records
Long-term design decisions that justify why the project is structured as it is.

- **CONTEXT-architecture-overview.md** — System design overview
- **ADR-001-typst-over-latex.md** — Why Typst instead of LaTeX
- **ADR-002-python-first-formulas.md** — Why SymPy is source of truth
- **ADR-003-code-linked-traceability.md** — How traceability works

Read these to understand *why* math-trace works the way it does.

### **guides/** — How-To Guides
Step-by-step instructions for common tasks.

- **getting-started-external.md** — First-time user guide (5 min)
- **typst-troubleshooting.md** — Debug guide for Typst compilation
- **typst-linting.md** — Code quality checklist for .typ files

Read these when you need to *do* something.

### **research/** — Research & Market Analysis
Strategic documents for positioning, planning, and future work.

- **competitive-positioning.md** — Market positioning & competitors
- **FORMULA_SLIDES_MARKET_ASSESSMENT.md** — Target market analysis
- **arxiv-publication-plan.md** — arXiv publication roadmap
- **equation-traceability-semantic-minimum.md** — Formal verification requirements

Read these for context on business strategy and long-term planning.

### **archived/** — Historical Status Documents
Old status reports, implementation notes, and launch records (kept for reference).

Read these only if investigating historical decisions or release notes.

---

---

## research/contract-template.md

Generic partnership contract template. Customize with partner organization name and specific terms before use.

---

## Organization Principles

- **ADRs** are permanent — they document decisions that won't change
- **Guides** are living — they should update as the project evolves
- **Research** is reference material — it informs decisions but can become stale
- **Archived** docs are read-only — they explain historical context

If you're adding documentation:
1. Is it a decision that affects architecture? → `adr/`
2. Is it instructions on how to do something? → `guides/`
3. Is it analysis, market data, or planning? → `research/`
4. Is it a historical status document? → `archived/`

---

**Last updated**: Oct 2, 2026
