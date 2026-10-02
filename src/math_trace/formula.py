"""Standardized formula representation and abstraction layer.

## Architecture: Pluggable Formula Backends

The Formula abstraction is designed to survive dependency maintenance risks by
decoupling formula definition from export and publishing. This module defines
the contract that all formula representations must implement.

## Design Principle: Swap-friendly Abstractions

Currently math-trace uses SymPy for symbolic mathematics. However, if SymPy
becomes unmaintained, we can swap it for an alternative (e.g., MathBox) without
rewriting the entire codebase.

**The Pipeline:**
    Source Formula → Export to LaTeX → Typst Conversion → PDF Publishing → Lean (optional)

Each stage is independent. If any library becomes problematic, we can swap its
implementation while keeping the rest of the pipeline unchanged.

## Currently Implemented

- **Formula Definition Layer:** SymPy (Python symbolic math)
  - All formulas are SymPy expressions
  - Exported as LaTeX via sp.latex()

- **Export Layer:** Regex-based LaTeX→Typst conversion (see exporters.py)
  - Converts LaTeX syntax to Typst syntax
  - Plugin-based for future alternatives

- **Publishing Layer:** Typst compiler (see publishers.py)
  - Currently uses Typst for PDF generation
  - Fallback to pdflatex available

## To Swap Libraries (e.g., SymPy → MathBox)

1. Implement a new Formula subclass that matches this interface
2. Update examples/*/model.py to use the new class
3. Rest of pipeline unchanged (still exports LaTeX)

Example:
    class MathBoxFormula(Formula):
        def __init__(self, expr):
            self.expr = expr
            self.latex = expr.to_latex()  # Provide LaTeX for downstream

See Also:
    - exporters.py: LatexToTypstConverter (swap if Typst syntax changes)
    - publishers.py: Publisher interface (swap if Typst becomes unmaintained)
    - examples/*/build_paper.py: Orchestration (unchanged when swapping)
"""

from dataclasses import asdict, dataclass


@dataclass
class Formula:
    """Standardized representation of a mathematical formula.

    All templates should export formulas using this dataclass.
    This ensures consistent structure, verification metadata, and test coverage.

    The Formula dataclass is a simple contract: it holds the formula's
    LaTeX representation and metadata. The actual computation engine
    (SymPy, MathBox, etc.) is abstracted away—downstream code only
    cares that to_dict() returns valid LaTeX.

    This design enables swapping formula sources without touching the
    export/publish pipeline (see module docstring for examples).
    """

    name: str
    """Unique identifier (e.g., 'schrodinger', 'michaelis_menten')"""

    latex: str
    """LaTeX representation (from sp.latex() or manual LaTeX string)"""

    description: str
    """Human-readable description of the formula"""

    source_line: int
    """Line number in model.py where this formula is defined"""

    assumptions: str = ""
    """Mathematical assumptions (e.g., 'assumes n ≥ 0')"""

    units: str = ""
    """Physical units (e.g., 'm/s', 'dimensionless')"""

    verified: bool = False
    """Whether formula has been manually reviewed and tested"""

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)


def formula_to_json_dict(formula: Formula) -> dict:
    """Convert Formula to JSON-compatible dictionary.

    Filters out verification metadata (kept for validation, not distribution).

    Returns:
        Dict with name, latex, description, source_line, assumptions, units
    """
    return {
        "latex": formula.latex,
        "description": formula.description,
        "source_line": formula.source_line,
        "assumptions": formula.assumptions,
        "units": formula.units,
    }
